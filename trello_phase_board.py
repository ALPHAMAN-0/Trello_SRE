#!/usr/bin/env python3
"""
Build the phase-based Trello board for the SRE project.

Six workflow lists (Backlog -> To Do -> In Progress -> PM Review -> QA / Validation
-> Done), category labels, per-card checklists and Gantt due dates.

Reuses the API helpers and .env loading from trello_gantt_board.py.

    python3 trello_phase_board.py --dry-run
    python3 trello_phase_board.py
"""

import argparse
import time

from trello_gantt_board import api, iso, pretty

BOARD_NAME = "Software Requirement Engineering Project - Anew"
BOARD_DESC = ("SRE project day-to-day tracking. Timeline mirrors the project Gantt "
              "chart (19 Aug - 14 Sep 2026). PM: Md. Shajahan Islam Sani.")

LISTS = ["Backlog", "To Do", "In Progress", "PM Review", "QA / Validation", "Done"]

LABELS = {
    "Research":      "sky",
    "Requirements":  "blue",
    "Design / UML":  "purple",
    "PM Review":     "orange",
    "QA":            "lime",
    "Business":      "pink",
    "Documentation": "yellow",
    "Milestone":     "red",
}

# Fill these in to auto-assign cards; blank means "skip".
USERNAMES = {
    "Mishal": "",
    "Siam Hossain": "",
    "Israt Jahan Surovy": "",
    "Team": "",
}

DEFAULT_CHECKLIST = ["Research", "Draft", "Review", "Finalize"]
CONSULTATION = ["Prepare agenda and questions", "Attend consultation",
                "Record meeting minutes", "Share action items with team"]
QA_CHECKLIST = ["Check completeness", "Check consistency", "Check testability",
                "Log defects", "Confirm fixes"]
FINAL_CHECKLIST = ["Final proofread", "Submit report", "Deliver presentation",
                   "Archive final files"]
OUTREACH = ["Identify NGO-based approach", "Add volunteer support",
            "Add SMS/phone support", "Add community pickup points",
            "Add offline awareness", "Add privacy and verification",
            "Finalize PM-ready answer"]


def card(key, title, owner, lst, start, due, labels, what, output, checklist=None):
    return dict(key=key, title=title, owner=owner, lst=lst, start=start, due=due,
                labels=labels, what=what, output=output,
                checklist=checklist or DEFAULT_CHECKLIST)


CARDS = [
    # ---- Done -------------------------------------------------------------
    card("SRE-01", "Project kickoff and topic selection", "Team", "Done",
         "2026-08-19", "2026-08-20", ["Documentation"],
         "Agree the project domain, confirm the team, and lock the topic for the SRE project.",
         "Confirmed topic statement and team list."),
    card("SRE-02", "Problem background and root-cause research", "Mishal", "Done",
         "2026-08-20", "2026-08-22", ["Research"],
         "Research the real-world problem, its underlying causes and who it affects.",
         "Problem background section with cited root causes."),
    card("SRE-03", "Existing solutions and related research", "Siam Hossain", "Done",
         "2026-08-21", "2026-08-23", ["Research"],
         "Survey products and services that already solve a similar problem and note their gaps.",
         "Comparison of existing solutions with the gaps our project fills."),
    card("SRE-04", "Define scope, actors and proposed solution", "Mishal", "Done",
         "2026-08-23", "2026-08-24", ["Requirements"],
         "Set the scope boundaries, list every system actor, and describe the proposed solution.",
         "Scope statement, actor list and solution overview."),
    card("SRE-05", "Prepare Consultation #1 brief", "Team", "Done",
         "2026-08-25", "2026-08-26", ["PM Review", "Documentation"],
         "Prepare the progress summary and question list to bring to the first PM consultation.",
         "Consultation #1 brief ready to present."),
    card("SRE-06", "Consultation #1", "Team", "Done",
         None, "2026-08-27", ["PM Review", "Milestone"],
         "Hold the first consultation with PM Md. Shajahan Islam Sani and capture the feedback.",
         "Meeting minutes and an agreed action-item list.", CONSULTATION),
    card("SRE-07", "Finalize team roles", "Israt Jahan Surovy", "Done",
         "2026-08-28", "2026-08-28", ["Documentation"],
         "Assign Product Owner, Developer and QA responsibilities across the team.",
         "Role table: Mishal (PO), Siam Hossain (Developer), Israt Jahan Surovy (QA)."),

    # ---- In Progress ------------------------------------------------------
    card("SRE-08", "Finalize project name", "Israt Jahan Surovy", "In Progress",
         "2026-08-28", "2026-08-29", ["Documentation", "QA"],
         "Replace the working title with a clearer, more descriptive project name.",
         "Final project name agreed by the team and approved by the PM."),
    card("SRE-09", "Research eKYC process", "Israt Jahan Surovy", "In Progress",
         "2026-08-28", "2026-08-29", ["Research", "Requirements"],
         "Research how eKYC verification works and what it requires from our users.",
         "eKYC summary listing the verification steps and the data the system must handle."),
    card("SRE-10", "Research ads as revenue source", "Siam Hossain", "In Progress",
         "2026-08-28", "2026-08-29", ["Research", "Business"],
         "Investigate ad networks and placement options as a revenue stream.",
         "Ad revenue options with expected earnings and integration effort."),
    card("SRE-11", "Research payment gateway options", "Siam Hossain", "In Progress",
         "2026-08-28", "2026-08-29", ["Research", "Business"],
         "Compare the available payment gateways on fees, coverage and integration effort.",
         "Gateway comparison table with a recommended option."),
    card("SRE-12", "Plan community outreach", "Mishal", "In Progress",
         "2026-08-28", "2026-08-29", ["Research", "Business"],
         "Answer the PM's Consultation #1 action item on how the platform reaches the community.",
         "PM-ready outreach plan covering NGO, volunteer, SMS, pickup, offline and privacy angles.",
         OUTREACH),
    card("SRE-13", "Prepare project Gantt chart", "Mishal", "In Progress",
         "2026-08-28", "2026-08-29", ["Documentation"],
         "Build the project schedule from 19 Aug to 14 Sep 2026 with owners and dependencies.",
         "Gantt chart exported and mirrored on this Trello board."),
    card("SRE-14", "Requirements elicitation and prioritization", "Team", "In Progress",
         "2026-08-28", "2026-08-30", ["Requirements"],
         "Gather requirements from the stakeholders and rank them by priority.",
         "Prioritized requirements list ready to feed the SRS."),

    # ---- PM Review --------------------------------------------------------
    card("SRE-15", "First SRS draft", "Team", "PM Review",
         "2026-08-29", "2026-08-30", ["Documentation", "PM Review"],
         "Write the first full SRS draft using the report template and submit it for PM review.",
         "First SRS draft submitted to the PM."),
    card("SRE-19", "Consultation #2", "Team", "PM Review",
         None, "2026-09-04", ["PM Review", "Milestone"],
         "Second PM consultation. Date is tentative - confirm with the PM before the week starts.",
         "Meeting minutes and an updated action-item list.", CONSULTATION),
    card("SRE-25", "Consultation #3", "Team", "PM Review",
         None, "2026-09-10", ["PM Review", "Milestone"],
         "Final PM consultation before submission. Date is tentative - confirm with the PM.",
         "Final approval, or the last correction list from the PM.", CONSULTATION),

    # ---- QA / Validation --------------------------------------------------
    card("SRE-24", "Requirements validation and QA review", "Israt Jahan Surovy",
         "QA / Validation", "2026-09-09", "2026-09-10", ["QA", "Requirements"],
         "Check every requirement for completeness, consistency and testability.",
         "QA review report with defects logged and confirmed fixed.", QA_CHECKLIST),

    # ---- To Do ------------------------------------------------------------
    card("SRE-16", "Revise requirements after PM feedback", "Team", "To Do",
         "2026-08-31", "2026-09-02", ["Requirements", "PM Review"],
         "Apply the PM's corrections from the SRS review to the requirement set.",
         "Updated requirements with a short change log."),
    card("SRE-17", "System features and FR/NFR specification", "Team", "To Do",
         "2026-08-31", "2026-09-03", ["Requirements"],
         "Write the system feature list plus the functional and non-functional requirements.",
         "Numbered FR/NFR specification."),
    card("SRE-18", "Create three UML diagrams", "Siam Hossain", "To Do",
         "2026-09-01", "2026-09-04", ["Design / UML"],
         "Produce the three required UML diagrams and explain each one.",
         "Three exported diagrams with short written explanations."),
    card("SRE-20", "Social impact analysis", "Mishal", "To Do",
         "2026-09-02", "2026-09-04", ["Research", "Business"],
         "Analyse the social, economic and ethical impact of the proposed system.",
         "Social impact section for the report."),

    # ---- Backlog ----------------------------------------------------------
    card("SRE-21", "Development plan and SDLC description", "Mishal", "Backlog",
         "2026-09-05", "2026-09-08", ["Documentation"],
         "Describe the chosen SDLC model and lay out the development plan.",
         "Development plan section with justification for the SDLC choice."),
    card("SRE-22", "Marketing plan", "Team", "Backlog",
         "2026-09-05", "2026-09-08", ["Business"],
         "Define the target users, the positioning and the launch channels.",
         "Marketing plan section."),
    card("SRE-23", "Cost and profit analysis", "Siam Hossain", "Backlog",
         "2026-09-06", "2026-09-08", ["Business"],
         "Estimate development and running costs against the projected revenue.",
         "Cost and profit table with a break-even estimate."),
    card("SRE-26", "Integrate report and references", "Team", "Backlog",
         "2026-09-08", "2026-09-10", ["Documentation"],
         "Merge every section into the report template and complete the reference list.",
         "Single integrated report draft with correctly formatted references."),
    card("SRE-27", "Final revisions and formatting", "Team", "Backlog",
         "2026-09-10", "2026-09-12", ["Documentation", "QA"],
         "Apply the last corrections and format the report to the template rules.",
         "Submission-ready report."),
    card("SRE-28", "Prepare presentation", "Team", "Backlog",
         "2026-09-12", "2026-09-13", ["Documentation"],
         "Build the slide deck and rehearse the delivery with the speaking split agreed.",
         "Rehearsed slide deck."),
    card("SRE-29", "Final submission and presentation", "Team", "Backlog",
         None, "2026-09-14", ["Milestone", "Documentation"],
         "Submit the final report and deliver the presentation.",
         "Report submitted and presentation delivered.", FINAL_CHECKLIST),
]


def description(c):
    when = (f"**Planned:** {pretty(c['start'])} -> {pretty(c['due'])}"
            if c["start"] else f"**Date:** {pretty(c['due'])}")
    return "\n".join([
        f"**Owner:** {c['owner']}",
        when,
        "",
        "**What needs to be done**",
        c["what"],
        "",
        "**Expected output**",
        c["output"],
        "",
        "_SRE project - schedule mirrored from the Gantt chart (19 Aug - 14 Sep 2026)._",
    ])


def dry_run(name):
    print(f"BOARD : {name}")
    print(f"LISTS : {' | '.join(LISTS)}")
    print(f"LABELS: {', '.join(LABELS)}\n")
    for lst in LISTS:
        in_list = [c for c in CARDS if c["lst"] == lst]
        print(f"--- {lst}  ({len(in_list)} cards) ---")
        for c in in_list:
            print(f"  {c['key']} {c['title']}")
            print(f"        owner={c['owner']:<20} due={pretty(c['due']):<13} "
                  f"labels={c['labels']}")
            print(f"        checklist={len(c['checklist'])} items")
    print(f"\n{len(CARDS)} cards would be created.")


def main():
    ap = argparse.ArgumentParser(description="Create the phase-based SRE Trello board.")
    ap.add_argument("--name", default=BOARD_NAME)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        dry_run(args.name)
        return

    print(f"Creating board: {args.name}")
    board = api("POST", "/boards/", name=args.name, desc=BOARD_DESC,
                defaultLists="false", prefs_permissionLevel="private")
    board_id = board["id"]
    print(f"  -> {board['shortUrl']}")

    print("Creating lists...")
    list_ids = {}
    for pos, name in enumerate(LISTS, start=1):
        list_ids[name] = api("POST", "/lists", name=name, idBoard=board_id,
                             pos=pos * 1000)["id"]
        print(f"  + {name}")

    print("Creating labels...")
    label_ids = {}
    for name, colour in LABELS.items():
        label_ids[name] = api("POST", "/labels", name=name, color=colour,
                              idBoard=board_id)["id"]
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
    if not member_ids:
        print("  (no usernames configured - owners are named in each card description)")

    print("Creating cards...")
    for c in CARDS:
        tags = [label_ids[n] for n in c["labels"] if n in label_ids]
        new = api("POST", "/cards",
                  idList=list_ids[c["lst"]],
                  name=f"{c['key']} - {c['title']}",
                  desc=description(c),
                  due=iso(c["due"], "17:00:00"),
                  start=iso(c["start"], "09:00:00"),
                  idLabels=",".join(tags) or None,
                  pos="bottom")
        chk = api("POST", "/checklists", idCard=new["id"], name="Steps")
        for item in c["checklist"]:
            api("POST", f"/checklists/{chk['id']}/checkItems", name=item, checked="false")
            time.sleep(0.1)
        if c["owner"] in member_ids:
            api("POST", f"/cards/{new['id']}/idMembers", value=member_ids[c["owner"]])
        print(f"  + [{c['lst']:<15}] {c['key']} {c['title']}")
        time.sleep(0.15)

    print(f"\nDone. {len(CARDS)} cards created.")
    print(f"Open your board: {board['shortUrl']}")


if __name__ == "__main__":
    main()
