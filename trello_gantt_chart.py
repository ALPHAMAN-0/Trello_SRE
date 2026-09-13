#!/usr/bin/env python3
"""
Build a self-contained, interactive Gantt-chart HTML page from the live
"Shasroy Bazaar" phase board (K4uuWzx5) on Trello.

Read-only. This script never creates, updates, or deletes anything on
Trello - it only calls GET endpoints. Re-run it any time to refresh the
chart against the board's current state; nothing about it is create-only
the way trello_phase_board.py and trello_gantt_board.py are.

Reuses the shared API helper and .env loader from trello_gantt_board.py.

    python3 trello_gantt_chart.py                # fetch + write trello_gantt_chart.html
    python3 trello_gantt_chart.py --dry-run       # fetch + print a summary, write nothing
    python3 trello_gantt_chart.py --out path.html
    python3 trello_gantt_chart.py --board-id XXXX # point at a different board

No third-party packages needed (stdlib only).
"""

import argparse
import datetime
import json
import re
import sys

from trello_gantt_board import api

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

SOURCE_BOARD_ID = "K4uuWzx5"          # Shasroy Bazaar - Project Phases (public)
OUT_DEFAULT = "trello_gantt_chart.html"
OUT_A4_DEFAULT = "trello_gantt_chart_a4.html"

KEY_RE = re.compile(r"^([A-Za-z]+-\d+)")
SPRINT_RE = re.compile(r"\*\*Sprint:\*\*\s*(.+)")

# Track a card belongs to, by key prefix.
TRACK_META = {
    "SRE": {"label": "Course Sprint", "sub": "Software Requirement Engineering coursework"},
    "DEV": {"label": "Build Roadmap", "sub": "Solo-developer implementation plan"},
    "BL": {"label": "Post-v1 Backlog", "sub": "Deferred - not scheduled"},
}

# Which Trello label wins the single "category" color for a card, checked in
# this order (most specific first). Anything left over buckets into "Other" -
# folding a long tail into one neutral bucket, never a 9th/10th generated hue.
# "Milestone" and "High-Risk" are flags, not categories - handled separately.
CATEGORY_RULES = [
    ("Architecture", {"Architecture"}),
    ("Security", {"Security"}),
    ("DevOps", {"DevOps"}),
    ("Testing", {"Testing", "QA"}),
    ("Frontend", {"Frontend"}),
    ("Documentation", {"Documentation", "Docs"}),
    ("Backend", {"Backend", "Database"}),
]


def classify_bucket(labels):
    names = {l["name"] for l in labels if l.get("name")}
    for bucket, aliases in CATEGORY_RULES:
        if names & aliases:
            return bucket
    return "Other"


def parse_sprint(desc):
    m = SPRINT_RE.search(desc or "")
    return m.group(1).strip() if m else None


def day(iso_str):
    """'2026-08-19T09:00:00.000Z' -> '2026-08-19'."""
    return iso_str[:10] if iso_str else None


def pretty(date_str):
    if not date_str:
        return "-"
    d = datetime.date.fromisoformat(date_str)
    return d.strftime("%-d %b %Y") if sys.platform != "win32" else d.strftime("%d %b %Y").lstrip("0")


# ---------------------------------------------------------------------------
# Fetch + shape
# ---------------------------------------------------------------------------

def fetch_board(board_id):
    board = api("GET", f"/boards/{board_id}", fields="name,desc,shortUrl,dateLastActivity")
    lists = api("GET", f"/boards/{board_id}/lists", fields="name,pos,closed")
    cards = api(
        "GET", f"/boards/{board_id}/cards",
        fields="name,desc,due,start,dueComplete,idList,labels,shortUrl",
        limit=1000,
    )
    return board, lists, cards


def build_cards(lists, cards):
    list_name = {l["id"]: l["name"] for l in lists}
    out = []
    skipped = []
    for c in cards:
        m = KEY_RE.match(c["name"].strip())
        if not m:
            skipped.append(c["name"])
            continue
        key = m.group(1)
        track = key.split("-")[0]
        title = c["name"].split(" - ", 1)[-1].strip()
        labels = c["labels"]
        label_names = sorted({l["name"] for l in labels if l.get("name")})
        milestone = "Milestone" in label_names or "MILESTONE" in title.upper()
        sprint = parse_sprint(c["desc"]) or ("Backlog (Post-v1)" if track == "BL" else None)
        out.append({
            "key": key,
            "title": title,
            "url": c["shortUrl"],
            "track": track,
            "phase": list_name.get(c["idList"], "?"),
            "sprint": sprint,
            "start": day(c["start"]),
            "due": day(c["due"]),
            "done": bool(c["dueComplete"]),
            "milestone": milestone,
            "highRisk": "High-Risk" in label_names,
            "bucket": classify_bucket(labels),
            "labels": [n for n in label_names if n not in ("Milestone", "High-Risk")],
        })
    # Stable sort: by start date (falling back to due, then key) within
    # whatever grouping the page applies later.
    out.sort(key=lambda r: (r["start"] or r["due"] or "", r["key"]))
    return out, skipped


def category_order(cards):
    """Real category buckets ranked by how many cards use them, most first.

    Slot N gets the categorical palette's Nth hue - so the biggest bucket
    lands on the most legible color. 'Other' never gets a generated hue.
    """
    counts = {}
    for c in cards:
        if c["bucket"] != "Other":
            counts[c["bucket"]] = counts.get(c["bucket"], 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    other_count = sum(1 for c in cards if c["bucket"] == "Other")
    return (
        [{"name": name, "count": n, "slot": i + 1} for i, (name, n) in enumerate(ranked)]
        + ([{"name": "Other", "count": other_count, "slot": "other"}] if other_count else [])
    )


def date_range(cards, track):
    dates = [d for c in cards if c["track"] == track for d in (c["start"], c["due"]) if d]
    return (min(dates), max(dates)) if dates else (None, None)


def sprint_groups(cards):
    """Ordered list of distinct sprint labels among DEV/BL cards, in the
    order they naturally appear (S0 < S1 < ... < S6 < Backlog)."""
    seen = []
    for c in cards:
        if c["track"] in ("DEV", "BL") and c["sprint"] and c["sprint"] not in seen:
            seen.append(c["sprint"])
    # "Backlog (Post-v1)" has no S-number; keep it at the end regardless of
    # first-appearance order.
    seen.sort(key=lambda s: (s.startswith("Backlog"), s))
    return seen


def phase_groups(cards, lists):
    """Ordered list of distinct phases among SRE cards, in board-list order."""
    board_order = [l["name"] for l in sorted(lists, key=lambda l: l["pos"])]
    present = {c["phase"] for c in cards if c["track"] == "SRE"}
    return [p for p in board_order if p in present]


def build_payload(board, lists, cards):
    all_cards, skipped = build_cards(lists, cards)
    sre = [c for c in all_cards if c["track"] == "SRE"]
    dev_bl = [c for c in all_cards if c["track"] in ("DEV", "BL")]

    sre_start, sre_end = date_range(all_cards, "SRE")
    dev_start, _ = date_range(all_cards, "DEV")
    _, dev_end = date_range(all_cards, "DEV")

    today = datetime.date.today().isoformat()

    payload = {
        "board": {"name": board["name"], "url": board["shortUrl"]},
        "generatedAt": datetime.datetime.now().strftime("%-d %b %Y, %H:%M") if sys.platform != "win32"
                       else datetime.datetime.now().strftime("%d %b %Y, %H:%M"),
        "today": today,
        "categories": category_order(all_cards),
        "sre": {
            "start": sre_start, "end": sre_end,
            "groups": phase_groups(all_cards, lists),
            "cards": sre,
        },
        "dev": {
            "start": dev_start, "end": dev_end,
            "groups": sprint_groups(all_cards),
            "cards": dev_bl,
        },
        "totals": {
            "cards": len(all_cards),
            "done": sum(1 for c in all_cards if c["done"]),
            "milestones": sum(1 for c in all_cards if c["milestone"]),
            "highRisk": sum(1 for c in all_cards if c["highRisk"]),
            "sre": len(sre),
            "dev": sum(1 for c in dev_bl if c["track"] == "DEV"),
            "backlog": sum(1 for c in dev_bl if c["track"] == "BL"),
        },
    }
    return payload, skipped


# ---------------------------------------------------------------------------
# Summary (used by both --dry-run and the normal run's console output)
# ---------------------------------------------------------------------------

def print_summary(payload, skipped):
    t = payload["totals"]
    print(f"Board: {payload['board']['name']} ({payload['board']['url']})")
    print(f"Cards: {t['cards']}  (SRE {t['sre']} · DEV {t['dev']} · Backlog {t['backlog']})")
    print(f"Done: {t['done']}  · Milestones: {t['milestones']}  · High-Risk: {t['highRisk']}")
    print(f"Course sprint span: {pretty(payload['sre']['start'])} → {pretty(payload['sre']['end'])}")
    print(f"Build roadmap span: {pretty(payload['dev']['start'])} → {pretty(payload['dev']['end'])}")
    print("Categories: " + ", ".join(f"{c['name']} ({c['count']})" for c in payload["categories"]))
    if skipped:
        print(f"Skipped {len(skipped)} card(s) with no recognizable KEY-NN prefix: {skipped}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Render the Shasroy Bazaar phase board as a Gantt chart.")
    ap.add_argument("--board-id", default=SOURCE_BOARD_ID, help="Trello board short ID")
    ap.add_argument("--out", default=None,
                    help=f"Output HTML path (default {OUT_DEFAULT}, or {OUT_A4_DEFAULT} with --a4)")
    ap.add_argument("--a4", action="store_true",
                    help="Write the paginated A4-landscape print version instead of the screen chart")
    ap.add_argument("--dry-run", action="store_true", help="Fetch and summarize only; write nothing")
    args = ap.parse_args()
    out = args.out or (OUT_A4_DEFAULT if args.a4 else OUT_DEFAULT)

    board, lists, cards = fetch_board(args.board_id)
    payload, skipped = build_payload(board, lists, cards)
    print_summary(payload, skipped)

    if args.dry_run:
        print("\n--dry-run: no file written.")
        return

    if args.a4:
        from trello_gantt_chart_a4_template import render_a4 as render
    else:
        from trello_gantt_chart_template import render
    html = render(payload)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"\nWrote {out}")
    if args.a4:
        print("Open it in a browser and print (A4 landscape is preset), or Save as PDF.")
    else:
        print("Open it in a browser, or re-run this script any time to refresh from Trello.")


if __name__ == "__main__":
    main()
