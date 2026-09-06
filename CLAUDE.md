# Trello_SRE

## Commands
- Dry run (no API calls): `python3 trello_phase_board.py --dry-run` (README.md:66)
- Create the board: `python3 trello_phase_board.py` (README.md:72)
- Override board name: `python3 trello_phase_board.py --name "My Board Name"` (README.md:78)
- No test or lint command found in the repo.

## Rules
- Stdlib only — no `pip install` (README.md:5). Don't add third-party dependencies without checking this.
- Scripts are **create-only**: re-running builds a *second* Trello board, not an update (README.md:81-82). Always `--dry-run` first.
- Never commit `.env` (git-ignored; holds `TRELLO_KEY`/`TRELLO_SECRET`/`TRELLO_TOKEN`) (README.md:37).
- Editing the task table in a script does **not** regenerate `sre_tasks_trello.csv` — it's a hand-maintained parallel copy (README.md:40-41).

## Read first
- `README.md` — full project description, setup, and known gaps
- `trello_phase_board.py` — main script
- `trello_gantt_board.py` — shared API helpers + `.env` loader

Architecture: see ARCHITECTURE.md — read before structural changes
