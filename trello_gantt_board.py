#!/usr/bin/env python3
"""
Build a Trello board from the "Software Requirement Engineering Project" Gantt chart
(19 Aug 2026 - 14 Sep 2026).

SETUP
-----
1. Get your API key:   https://trello.com/power-ups/admin  (create a Power-Up -> API key)
   Older/simpler page: https://trello.com/app-key
2. On that same page click "Token" to generate a token (choose "Never" expiry if you like).
3. Export them:
       export TRELLO_KEY=your_key_here
       export TRELLO_TOKEN=your_token_here

USAGE
-----
    python3 trello_gantt_board.py --dry-run     # show what will be created, no API calls
    python3 trello_gantt_board.py               # actually create the board
    python3 trello_gantt_board.py --name "My Board Name"

No third-party packages needed (stdlib only).
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.trello.com/1"

# ---------------------------------------------------------------------------
# CONFIG - edit freely
# ---------------------------------------------------------------------------

BOARD_NAME = "Software Requirement Engineering Project"
BOARD_DESC = "Imported from the project Gantt chart (19 Aug 2026 - 14 Sep 2026)."

# Lists, left to right on the board.
LISTS = ["Planned", "In Progress", "Done"]

# Trello label name -> Trello label colour.
LABELS = {
    "Milestone": "red",
    "Tentative": "orange",
    "Team": "blue",
    "Mishal": "green",
    "Siam Hossain": "yellow",
    "Israt Jahan Surovy": "purple",
}

# OPTIONAL: map an assignee to a real Trello username to auto-assign the card.
# Leave a value empty to skip assigning that person.
USERNAMES = {
    "Mishal": "",
    "Siam Hossain": "",
    "Israt Jahan Surovy": "",
    "Team": "",
}

# Which list each STATUS goes into.
STATUS_TO_LIST = {
    "Done": "Done",
    "In Progress": "In Progress",
    "Planned": "Planned",
    "Tentative": "Planned",
    "Milestone": "Planned",
}

# key, task, assignee, status, start (YYYY-MM-DD), due (YYYY-MM-DD)
# Dates were read off the Gantt bars - adjust any that are slightly off.
TASKS = [
    ("SRE-01", "Project kickoff & topic selection",        "Team",               "Done",        "2026-08-19", "2026-08-20"),
    ("SRE-02", "Problem background & root-cause research", "Mishal",             "Done",        "2026-08-20", "2026-08-22"),
    ("SRE-03", "Existing solutions / related research",    "Siam",               "Done",        "2026-08-21", "2026-08-23"),
    ("SRE-04", "Define scope, actors & proposed solution", "Mishal",             "Done",        "2026-08-23", "2026-08-24"),
    ("SRE-05", "Prepare Consultation #1 brief",            "Team",               "Done",        "2026-08-25", "2026-08-26"),
    ("SRE-06", "Consultation #1",                          "Team",               "Done",        None,         "2026-08-27"),
    ("SRE-07", "Finalize team roles",                      "Israt Jahan Surovy", "Done",        "2026-08-28", "2026-08-28"),
    ("SRE-08", "Finalize clearer project name",            "Israt Jahan Surovy", "In Progress", "2026-08-28", "2026-08-29"),
    ("SRE-09", "Research eKYC process",                    "Israt Jahan Surovy", "In Progress", "2026-08-28", "2026-08-29"),
    ("SRE-10", "Research ads & payment gateway",           "Siam Hossain",       "In Progress", "2026-08-28", "2026-08-29"),
    ("SRE-11", "Plan community outreach",                  "Mishal",             "In Progress", "2026-08-28", "2026-08-29"),
    ("SRE-12", "Prepare project Gantt chart",              "Mishal",             "In Progress", "2026-08-28", "2026-08-29"),
    ("SRE-13", "Requirements elicitation & prioritization","Team",               "In Progress", "2026-08-28", "2026-08-30"),
    ("SRE-14", "First SRS draft / PM review",              "Team",               "Planned",     None,         "2026-08-31"),
    ("SRE-15", "Revise requirements after PM feedback",    "Team",               "Planned",     "2026-08-31", "2026-09-02"),
    ("SRE-16", "System features + FR/NFR specification",   "Team",               "Planned",     "2026-08-31", "2026-09-03"),
    ("SRE-17", "Create 3 UML diagrams",                    "Siam Hossain",       "Planned",     "2026-09-01", "2026-09-04"),
    ("SRE-18", "Social impact analysis",                   "Mishal",             "Planned",     "2026-09-02", "2026-09-04"),
    ("SRE-19", "Consultation #2 (Tentative)",              "Team",               "Tentative",   None,         "2026-09-04"),
    ("SRE-20", "Development plan & SDLC description",      "Mishal",             "Planned",     "2026-09-05", "2026-09-08"),
    ("SRE-21", "Marketing plan",                           "Team",               "Planned",     "2026-09-05", "2026-09-08"),
    ("SRE-22", "Cost & profit analysis",                   "Siam Hossain",       "Planned",     "2026-09-06", "2026-09-08"),
    ("SRE-23", "Integrate report & references",            "Team",               "Planned",     "2026-09-08", "2026-09-10"),
    ("SRE-24", "Requirements validation & QA review",      "Israt Jahan Surovy", "Planned",     "2026-09-09", "2026-09-10"),
    ("SRE-25", "Consultation #3 (Tentative)",              "Team",               "Tentative",   None,         "2026-09-10"),
    ("SRE-26", "Final revisions & formatting",             "Team",               "Planned",     "2026-09-10", "2026-09-12"),
    ("SRE-27", "Prepare presentation & rehearse",          "Team",               "Planned",     "2026-09-12", "2026-09-13"),
    ("SRE-28", "Final submission & presentation",          "Team",               "Milestone",   None,         "2026-09-14"),
]

# ---------------------------------------------------------------------------
# Trello API helpers
# ---------------------------------------------------------------------------

def load_env(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")):
    """Read `NAME = value` lines from a local .env. Real env vars win."""
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            os.environ.setdefault(name.strip(), value.strip().strip("\"'"))


load_env()

KEY = os.environ.get("TRELLO_KEY", "")
TOKEN = os.environ.get("TRELLO_TOKEN", "")


def api(method, path, **params):
    """Call the Trello API. Params go in the query string, which Trello accepts."""
    params = {k: v for k, v in params.items() if v is not None}
    params.update({"key": KEY, "token": TOKEN})
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/json")

    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            return json.loads(body) if body.strip() else {}
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", "replace").strip()
            if err.code == 429:                       # rate limited - back off
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"\nTrello API error {err.code} on {method} {path}\n{detail}\n")
        except urllib.error.URLError as err:
            raise SystemExit(f"\nNetwork error calling Trello: {err.reason}\n")
    raise SystemExit("Trello kept rate-limiting the request. Try again in a minute.")


def iso(date_str, hour="12:00:00"):
    return f"{date_str}T{hour}.000Z" if date_str else None


def pretty(date_str):
    if not date_str:
        return "-"
    y, m, d = date_str.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{int(d)} {months[int(m) - 1]} {y}"


def card_description(assignee, status, start, due):
    lines = [
        f"**Assignee:** {assignee}",
        f"**Status on Gantt chart:** {status}",
        f"**Planned:** {pretty(start)} -> {pretty(due)}" if start else f"**Date:** {pretty(due)}",
        "",
        "_Imported from the SRE project Gantt chart (19 Aug - 14 Sep 2026)._",
    ]
    return "\n".join(lines)


def labels_for(assignee, status):
    names = []
    if status in ("Milestone", "Tentative"):
        names.append(status)
    if assignee in LABELS:
        names.append(assignee)
    elif assignee == "Siam":          # chart uses both "Siam" and "Siam Hossain"
        names.append("Siam Hossain")
    return names


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def dry_run(board_name):
    print(f"BOARD: {board_name}")
    print(f"LISTS: {', '.join(LISTS)}")
    print(f"LABELS: {', '.join(LABELS)}\n")
    for key, task, assignee, status, start, due in TASKS:
        lst = STATUS_TO_LIST[status]
        tags = labels_for(assignee, status)
        print(f"  [{lst:<11}] {key}  {task}")
        print(f"                start={pretty(start):<14} due={pretty(due):<14} labels={tags}")
    print(f"\n{len(TASKS)} cards would be created. Re-run without --dry-run to push to Trello.")


def main():
    parser = argparse.ArgumentParser(description="Create a Trello board from the SRE Gantt chart.")
    parser.add_argument("--name", default=BOARD_NAME, help="Board name")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan, call nothing")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.name)
        return

    if not KEY or not TOKEN:
        sys.exit("Set TRELLO_KEY and TRELLO_TOKEN first. See the header of this file.")

    print(f"Creating board: {args.name}")
    board = api("POST", "/boards/", name=args.name, desc=BOARD_DESC,
                defaultLists="false", prefs_permissionLevel="private")
    board_id = board["id"]
    print(f"  -> {board['shortUrl']}")

    print("Creating lists...")
    list_ids = {}
    for pos, name in enumerate(LISTS, start=1):
        lst = api("POST", "/lists", name=name, idBoard=board_id, pos=pos * 1000)
        list_ids[name] = lst["id"]
        print(f"  + {name}")

    print("Creating labels...")
    label_ids = {}
    for name, colour in LABELS.items():
        lbl = api("POST", "/labels", name=name, color=colour, idBoard=board_id)
        label_ids[name] = lbl["id"]
        print(f"  + {name} ({colour})")

    print("Looking up members...")
    member_ids = {}
    for person, username in USERNAMES.items():
        if not username:
            continue
        try:
            member_ids[person] = api("GET", f"/members/{username}")["id"]
            print(f"  + {person} -> @{username}")
        except SystemExit:
            print(f"  ! could not find @{username}, skipping {person}")

    print("Creating cards...")
    for key, task, assignee, status, start, due in TASKS:
        target = list_ids[STATUS_TO_LIST[status]]
        tag_ids = [label_ids[n] for n in labels_for(assignee, status) if n in label_ids]
        card = api(
            "POST", "/cards",
            idList=target,
            name=f"{key} · {task}",
            desc=card_description(assignee, status, start, due),
            due=iso(due, "17:00:00"),
            start=iso(start, "09:00:00"),
            idLabels=",".join(tag_ids) or None,
            pos="bottom",
        )
        if assignee in member_ids:
            api("POST", f"/cards/{card['id']}/idMembers", value=member_ids[assignee])
        print(f"  + {key} {task}")
        time.sleep(0.15)          # stay under Trello's rate limit

    print(f"\nDone. {len(TASKS)} cards created.")
    print(f"Open your board: {board['shortUrl']}")


if __name__ == "__main__":
    main()
