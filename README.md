# SRE Trello Board Generator

Python scripts that build the Trello boards for the **Software Requirement
Engineering Project** (19 Aug – 14 Sep 2026) straight from the project Gantt
chart. Stdlib only — no `pip install` needed.

The point of this repo: the course requires the schedule to live in a real
project management tool, not only in Word or Excel. These scripts push the Gantt
chart into Trello and keep the two in sync by hand-editing one task table.

**Tags:** `trello` · `trello-api` · `project-management` · `gantt-chart` ·
`software-requirements-engineering` · `automation` · `python` · `stdlib-only` ·
`university-project`

---

## Boards

| Board | Structure | Cards | Link |
|---|---|---|---|
| Gantt mirror | 3 lists by status | 28 | https://trello.com/b/3njEcNan |
| Phase board | 6 workflow lists, labels, checklists | 29 | https://trello.com/b/mlRtG8ED |
| Shasroy Bazaar *(current)* | 8 SDLC-phase lists (Planning → Support & Maintenance) | 100 | https://trello.com/b/K4uuWzx5 |

The Gantt mirror and the 6-list phase board are **private**; teammates see
nothing until invited from the board's Share menu. **Shasroy Bazaar is
public.** It carries every task from both the SRE coursework (19 Aug – 14
Sep 2026) and the solo-developer build roadmap that follows it (15 Sep – 19
Dec 2026, `trello_phase_reorg_board.py`'s output), reorganized into SDLC
phases. It supersedes the other two — consider closing them so nobody opens
the wrong board.

---

## Files

| File | What it is |
|---|---|
| `trello_phase_board.py` | **Main script.** Builds the 6-list phase board with category labels, per-card checklists and Gantt due dates. |
| `trello_gantt_board.py` | First-generation script: 3 lists (Planned / In Progress / Done), one label per person. Also holds the shared API helpers and `.env` loader that every other script imports. |
| `trello_sync_cards.py` | Adds `sre_tasks_trello.csv` rows to an existing board as new cards, skipping any key already present. Never duplicates a card. |
| `trello_phase_reorg_board.py` | Clones every card on the phase board into a **new** board organized by the 8 SDLC phases (Planning → Support & Maintenance) — this is how the Shasroy Bazaar board was built. Read-only against its source board. |
| `trello_gantt_chart.py` | **Read-only.** Fetches the Shasroy Bazaar board live and renders it as an interactive Gantt chart (`trello_gantt_chart.html`). Safe to re-run any time — see [Visualize the roadmap](#visualize-the-roadmap). |
| `sre_tasks_trello.csv` | The same 28 tasks flattened for Trello's built-in CSV import. A manual fallback if the API route fails. |
| `.env` | Trello credentials. **Git-ignored — never commit.** |
| `.gitignore` | Keeps `.env`, `__pycache__/` and editor noise out of version control. |

> **Note:** the CSV is a hand-maintained parallel copy. Editing the task table in
> a script does **not** regenerate it.

---

## Setup

1. Get an API key at https://trello.com/power-ups/admin (create a Power-Up → API key).
2. On the same page, click **Token** to generate a token.
3. Put both in `.env` at the repo root:

   ```
   TRELLO_KEY    = your_key_here
   TRELLO_SECRET = your_secret_here
   TRELLO_TOKEN  = your_token_here
   ```

`load_env()` in `trello_gantt_board.py` parses this file directly and tolerates
the spaces around `=`. Real environment variables take precedence, so
`export TRELLO_KEY=...` still overrides the file.

## Usage

Always dry-run first — it prints the full plan and makes zero API calls:

```bash
python3 trello_phase_board.py --dry-run
```

Then create the board:

```bash
python3 trello_phase_board.py
```

Override the board name:

```bash
python3 trello_phase_board.py --name "My Board Name"
```

> ⚠️ **The scripts are create-only.** Re-running builds a *second* board rather
> than updating the existing one. There is no idempotency check and no update mode.

---

## Visualize the roadmap

`trello_gantt_chart.py` is the exception to the create-only rule above — it
never writes to Trello at all, only reads. Run it any time to pull the
Shasroy Bazaar board's current state and render it as a self-contained Gantt
chart:

```bash
python3 trello_gantt_chart.py
```

This writes `trello_gantt_chart.html` — open it directly in a browser. It
shows the SRE coursework sprint and the DEV build roadmap as two panels on a
shared day-scale, groups rows by phase/sprint, colors bars by category
(Backend, Frontend, Architecture, Documentation, Security, DevOps, Testing,
with everything else folded into Other), marks the 11 milestones and 15
high-risk cards, and includes a table view for accessibility. Nothing is
cached — re-run the script whenever the board changes to get a fresh file.

```bash
python3 trello_gantt_chart.py --out somewhere/else.html   # custom output path
python3 trello_gantt_chart.py --board-id XXXXXXXX         # point at a different board
python3 trello_gantt_chart.py --dry-run                   # print a summary, write nothing
```

---

## Board structure

### Lists — where a card sits

Lists are workflow states. Moving cards left to right as work progresses is what
demonstrates active tool use to the PM.

| List | Meaning |
|---|---|
| **Backlog** | Scheduled but not started; nothing due within the week. |
| **To Do** | Next up — due in the coming few days. |
| **In Progress** | Actively being worked on right now. |
| **PM Review** | Waiting on PM Md. Shajahan Islam Sani — drafts submitted, consultations pending. |
| **QA / Validation** | With QA for completeness, consistency and testability checks. |
| **Done** | Finished and accepted. |

### Labels — what kind of work a card is

Colour-coded tags, independent of which list a card sits in. A card can carry
more than one.

| Label | Colour | Covers |
|---|---|---|
| **Research** | sky | Background investigation, market and technology scans. |
| **Requirements** | blue | Elicitation, scope, FR/NFR specification, revisions. |
| **Design / UML** | purple | Diagrams and system design artefacts. |
| **PM Review** | orange | Anything that goes to or comes from the PM. |
| **QA** | lime | Validation, defect logging, quality checks. |
| **Business** | pink | Revenue, cost, marketing, social and community impact. |
| **Documentation** | yellow | Report writing, formatting, slides, the Gantt chart itself. |
| **Milestone** | red | Fixed, unmissable dates — consultations and final submission. |

### Card anatomy

Every card follows the same shape:

```
SRE-12 - Plan community outreach

**Owner:** Mishal
**Planned:** 28 Aug 2026 -> 29 Aug 2026

**What needs to be done**
<one-line statement of the task>

**Expected output**
<the concrete deliverable that closes the card>
```

Plus a **Steps** checklist (120 items across the board). Most cards use the
generic Research → Draft → Review → Finalize. Three types are tailored:

- **Consultations** — Prepare agenda → Attend → Record minutes → Share action items
- **QA review** — Check completeness → consistency → testability → Log defects → Confirm fixes
- **Plan community outreach** — the exact 7-point action item from Consultation #1

---

## Team

| Person | Role | Owns |
|---|---|---|
| Mishal | Product Owner | Scope, problem analysis, community outreach, social impact, development plan, Gantt chart |
| Siam Hossain | Developer | Existing-solution research, ads and payment gateway research, UML diagrams, cost/profit analysis |
| Israt Jahan Surovy | QA | Project name, eKYC research, QA review, requirements validation |
| Team | — | Requirements elicitation, SRS writing, PM consultations, marketing plan, final report, presentation |
| Md. Shajahan Islam Sani | Project Manager | Reviews and consultations |

---

## Known gaps

- **No members are assigned.** `USERNAMES` in both scripts is empty, so the
  member lookup step does nothing. Owners appear in card descriptions only. Fill
  in real Trello usernames to enable auto-assignment.
- **No attachments.** The report template and meeting minutes are not in this
  repo, so no files are attached to cards.
- **One date to confirm.** `SRE-15 First SRS draft` is set to **30 Aug** per the
  latest instruction; the Gantt chart and CSV both say **31 Aug**.
- **No update or delete path.** Fixing a card after creation means editing it in
  Trello by hand, or writing a one-off `PUT /cards/{id}` call.

## Timeline

19 Aug 2026 → 14 Sep 2026. Fixed dates: Consultation #1 on 27 Aug (done),
Consultation #2 on 4 Sep (tentative), Consultation #3 on 10 Sep (tentative),
final submission and presentation on 14 Sep.
