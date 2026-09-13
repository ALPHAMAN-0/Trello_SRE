#!/usr/bin/env python3
"""
Sync sre_tasks_trello.csv onto an EXISTING Trello board, adding cards only for
rows whose key (e.g. "DEV-01") isn't already on the board. Never touches or
duplicates a card that's already there.

Reuses the API helpers and .env loading from trello_gantt_board.py.

    python3 trello_sync_cards.py --dry-run
    python3 trello_sync_cards.py
"""

import argparse
import csv
import re
import time

from trello_gantt_board import api, iso

BOARD_ID = "mlRtG8ED"  # Shasroy Bazaar board (see README.md)
CSV_PATH = "sre_tasks_trello.csv"

# CSV "List" value -> real list name on the phase board. Everything not yet
# started lands in Backlog regardless of which Gantt-style status it carries.
STATUS_TO_LIST = {
    "Planned": "Backlog",
    "Tentative": "Backlog",
    "Milestone": "Backlog",
    "In Progress": "In Progress",
    "Done": "Done",
}

# Colour to use for a label the board doesn't already have. Repeats are fine.
NEW_LABEL_COLORS = ["black", "green", "sky", "lime", "orange", "purple",
                     "red", "blue", "yellow", "pink"]

KEY_RE = re.compile(r"^([A-Za-z]+-\d+)")


def split_key(card_name):
    m = KEY_RE.match(card_name.strip())
    return m.group(1) if m else None


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


LABELLED_SEGMENT_RE = re.compile(r"^([A-Za-z][A-Za-z ]{0,20}):\s*(.*)$")


def format_description(raw):
    """Turn "Assignee: X | Sprint: Y | Goal: Z || AC: W || Owner: V" into Trello markdown."""
    main, *rest = raw.split(" || ")
    lines = []
    for part in main.split(" | "):
        label, _, value = part.partition(":")
        lines.append(f"**{label.strip()}:** {value.strip()}")
    for segment in rest:
        segment = segment.strip()
        m = LABELLED_SEGMENT_RE.match(segment)
        if m:
            lines += ["", f"**{m.group(1).strip()}:** {m.group(2).strip()}"]
        else:
            lines += ["", segment]
    return "\n".join(lines)


def fetch_existing(board_id):
    real_id = api("GET", f"/boards/{board_id}", fields="id")["id"]
    lists = api("GET", f"/boards/{board_id}/lists", fields="name,closed")
    list_id_by_name = {l["name"]: l["id"] for l in lists if not l["closed"]}

    labels = api("GET", f"/boards/{board_id}/labels", fields="name,color", limit=200)
    label_id_by_name = {l["name"]: l["id"] for l in labels if l["name"]}

    cards = api("GET", f"/boards/{board_id}/cards", fields="name", limit=1000)
    existing_keys = {split_key(c["name"]) for c in cards if split_key(c["name"])}

    return real_id, list_id_by_name, label_id_by_name, existing_keys


def plan(rows, existing_keys):
    new_rows = []
    for row in rows:
        key = split_key(row["Card Name"])
        if key and key not in existing_keys:
            new_rows.append((key, row))
    return new_rows


def labels_needed(new_rows):
    needed = set()
    for _key, row in new_rows:
        for name in row["Labels"].split(","):
            name = name.strip()
            if name:
                needed.add(name)
    return needed


def dry_run():
    rows = read_csv_rows(CSV_PATH)
    _real_id, list_id_by_name, label_id_by_name, existing_keys = fetch_existing(BOARD_ID)

    print(f"BOARD: {BOARD_ID} (https://trello.com/b/{BOARD_ID})")
    print(f"Existing cards on board: {len(existing_keys)}")
    print(f"Rows in {CSV_PATH}: {len(rows)}\n")

    new_rows = plan(rows, existing_keys)
    if not new_rows:
        print("Nothing to do - every CSV row already has a matching card.")
        return

    missing_lists = {STATUS_TO_LIST.get(r["List"], "Backlog") for _k, r in new_rows} - set(list_id_by_name)
    if missing_lists:
        print(f"WARNING: board is missing expected list(s): {sorted(missing_lists)}")

    needed = labels_needed(new_rows)
    new_labels = sorted(needed - set(label_id_by_name))
    reused_labels = sorted(needed & set(label_id_by_name))
    print(f"Labels already on board that will be reused: {reused_labels}")
    print(f"New labels that will be created: {new_labels}\n")

    by_list = {}
    for key, row in new_rows:
        target = STATUS_TO_LIST.get(row["List"], "Backlog")
        by_list.setdefault(target, []).append((key, row))

    for lst, items in by_list.items():
        print(f"--- {lst} ({len(items)} new cards) ---")
        for key, row in items:
            title = row["Card Name"].split(" · ", 1)[-1]
            print(f"  {key} - {title}")
            print(f"        due={row['Due Date'] or '-':<12} labels={row['Labels']}")

    print(f"\n{len(new_rows)} new cards would be created. "
          f"{len(rows) - len(new_rows)} rows already match an existing card and will be skipped.")


def main():
    ap = argparse.ArgumentParser(description="Add CSV rows that aren't on the board yet as new cards.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        dry_run()
        return

    rows = read_csv_rows(CSV_PATH)
    real_id, list_id_by_name, label_id_by_name, existing_keys = fetch_existing(BOARD_ID)
    new_rows = plan(rows, existing_keys)

    if not new_rows:
        print("Nothing to do - every CSV row already has a matching card.")
        return

    needed = labels_needed(new_rows)
    colors = iter(NEW_LABEL_COLORS * 3)
    for name in sorted(needed - set(label_id_by_name)):
        label = api("POST", "/labels", name=name, color=next(colors), idBoard=real_id)
        label_id_by_name[name] = label["id"]
        print(f"  + label {name} ({label['color']})")

    created = 0
    for key, row in new_rows:
        target = STATUS_TO_LIST.get(row["List"], "Backlog")
        if target not in list_id_by_name:
            print(f"  ! skipping {key}: no '{target}' list on the board")
            continue
        title = row["Card Name"].split(" · ", 1)[-1]
        label_ids = [label_id_by_name[n.strip()] for n in row["Labels"].split(",")
                     if n.strip() in label_id_by_name]
        new_card = api("POST", "/cards",
                       idList=list_id_by_name[target],
                       name=f"{key} - {title}",
                       desc=format_description(row["Description"]),
                       due=iso(row["Due Date"] or None, "17:00:00"),
                       start=iso(row["Start Date"] or None, "09:00:00"),
                       idLabels=",".join(label_ids) or None,
                       pos="bottom")
        print(f"  + [{target:<12}] {key} {title}")
        created += 1
        time.sleep(0.15)

    print(f"\nDone. {created} cards created, {len(new_rows) - created} skipped.")


if __name__ == "__main__":
    main()
