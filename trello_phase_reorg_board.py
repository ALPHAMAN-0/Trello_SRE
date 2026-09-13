#!/usr/bin/env python3
"""
Create a NEW Trello board that mirrors every card on the Shasroy Bazaar board
(mlRtG8ED) but organized into the 8 classic SDLC phases instead of the
workflow-state lists:

    Planning -> Requirements -> Design -> Development -> Testing -> UAT
    -> Go-Live -> Support & Maintenance

The source board is read-only here - nothing on it is changed or removed.
Card text, due/start dates, labels and checklists (including checked state)
are copied across.

    python3 trello_phase_reorg_board.py --dry-run
    python3 trello_phase_reorg_board.py
    python3 trello_phase_reorg_board.py --name "My Board Name"
"""

import argparse
import re
import time

from trello_gantt_board import api, iso

SOURCE_BOARD_ID = "mlRtG8ED"
BOARD_NAME = "Shasroy Bazaar - Project Phases"
BOARD_DESC = ("Same tasks as the Shasroy Bazaar board, reorganized into the "
              "8-stage SDLC view (Planning -> Requirements -> Design -> "
              "Development -> Testing -> UAT -> Go-Live -> Support & Maintenance).")

PHASES = ["Planning", "Requirements", "Design", "Development", "Testing",
          "UAT", "Go-Live", "Support & Maintenance"]

KEY_RE = re.compile(r"^([A-Za-z]+-\d+)")

# Explicit calls for cards a simple label/keyword rule would get wrong.
PHASE_OVERRIDES = {
    # ---- SRE course project ----
    "SRE-01": "Planning", "SRE-05": "Planning", "SRE-06": "Planning",
    "SRE-07": "Planning", "SRE-08": "Planning", "SRE-12": "Planning",
    "SRE-13": "Planning", "SRE-19": "Planning", "SRE-21": "Planning",
    "SRE-22": "Planning", "SRE-23": "Planning",
    "SRE-18": "Design",
    "SRE-24": "Testing",
    "SRE-25": "Go-Live", "SRE-26": "Go-Live", "SRE-27": "Go-Live",
    "SRE-28": "Go-Live", "SRE-29": "Go-Live",
    # (remaining SRE-02/03/04/09/10/11/14/15/16/17/20 fall through to Requirements)

    # ---- Dev roadmap: architecture / domain-design decisions ----
    "DEV-01": "Design", "DEV-12": "Design", "DEV-17": "Design",
    "DEV-22": "Design", "DEV-24": "Design", "DEV-31": "Design",
    "DEV-32": "Design", "DEV-33": "Design", "DEV-36": "Design",

    # ---- Dev roadmap: ongoing ops / post-launch ----
    "DEV-61": "Support & Maintenance", "DEV-62": "Support & Maintenance",
    "DEV-63": "Support & Maintenance", "DEV-64": "Support & Maintenance",

    "DEV-65": "UAT",
}


def split_key(card_name):
    m = KEY_RE.match(card_name.strip())
    return m.group(1) if m else None


def classify_phase(key, title, label_names):
    if key in PHASE_OVERRIDES:
        return PHASE_OVERRIDES[key]
    if key.startswith("BL-"):
        return "Support & Maintenance"
    if key.startswith("SRE-"):
        return "Requirements"
    if "MILESTONE" in title.upper():
        return "Go-Live"
    if "Testing" in label_names:
        return "Testing"
    return "Development"


def fetch_source_cards():
    return api("GET", f"/boards/{SOURCE_BOARD_ID}/cards",
               fields="name,desc,due,start,labels",
               checklists="all", checklist_fields="name", limit=1000)


def build_plan(cards):
    plan = {phase: [] for phase in PHASES}
    for c in cards:
        key = split_key(c["name"])
        if not key:
            print(f"  ! skipping card with no recognizable key: {c['name']!r}")
            continue
        title = c["name"].split(" - ", 1)[-1]
        label_names = [l["name"] for l in c["labels"] if l["name"]]
        phase = classify_phase(key, title, label_names)
        plan[phase].append((key, c))
    return plan


def dry_run():
    cards = fetch_source_cards()
    print(f"Source board: https://trello.com/b/{SOURCE_BOARD_ID}  ({len(cards)} cards)")
    print(f"New board name: {BOARD_NAME}\n")

    plan = build_plan(cards)
    for phase in PHASES:
        items = plan[phase]
        print(f"--- {phase} ({len(items)} cards) ---")
        for key, c in items:
            title = c["name"].split(" - ", 1)[-1]
            labels = ",".join(l["name"] for l in c["labels"] if l["name"])
            print(f"  {key} - {title}  [{labels}]")
    total = sum(len(v) for v in plan.values())
    print(f"\n{total} cards would be created across {len(PHASES)} lists on a brand-new board.")
    print("The source board (Shasroy Bazaar) is not modified.")


def main():
    ap = argparse.ArgumentParser(description="Clone Shasroy Bazaar into a phase-based board.")
    ap.add_argument("--name", default=BOARD_NAME)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        dry_run()
        return

    cards = fetch_source_cards()
    plan = build_plan(cards)

    print(f"Creating board: {args.name}")
    board = api("POST", "/boards/", name=args.name, desc=BOARD_DESC,
                defaultLists="false", prefs_permissionLevel="private")
    board_id = board["id"]
    print(f"  -> {board['shortUrl']}")

    print("Creating lists...")
    list_ids = {}
    for pos, phase in enumerate(PHASES, start=1):
        list_ids[phase] = api("POST", "/lists", name=phase, idBoard=board_id,
                              pos=pos * 1000)["id"]
        print(f"  + {phase}")

    print("Creating labels...")
    label_id_by_name = {}
    seen = {}
    for c in cards:
        for l in c["labels"]:
            if l["name"] and l["name"] not in seen:
                seen[l["name"]] = l["color"]
    for name, color in seen.items():
        label_id_by_name[name] = api("POST", "/labels", name=name,
                                     color=color or None, idBoard=board_id)["id"]
        print(f"  + {name} ({color})")

    print("Creating cards...")
    created = 0
    for phase in PHASES:
        for key, c in plan[phase]:
            label_ids = [label_id_by_name[l["name"]] for l in c["labels"]
                         if l["name"] in label_id_by_name]
            new_card = api("POST", "/cards",
                           idList=list_ids[phase],
                           name=c["name"],
                           desc=c["desc"],
                           due=c["due"],
                           start=c["start"],
                           idLabels=",".join(label_ids) or None,
                           pos="bottom")
            for checklist in c["checklists"]:
                chk = api("POST", "/checklists", idCard=new_card["id"], name=checklist["name"])
                for item in checklist["checkItems"]:
                    api("POST", f"/checklists/{chk['id']}/checkItems",
                       name=item["name"], checked=str(item["state"] == "complete").lower())
                    time.sleep(0.1)
            print(f"  + [{phase:<20}] {key}")
            created += 1
            time.sleep(0.15)

    print(f"\nDone. {created} cards created on {board['shortUrl']}")
    print("The source board (Shasroy Bazaar) was not modified.")


if __name__ == "__main__":
    main()
