---
tags: [component, Trello_SRE]
---
- Path: `trello_gantt_chart.py` (templates in `trello_gantt_chart_template.py` and `trello_gantt_chart_a4_template.py`)
- Role: Read-only. Fetches the Shasroy Bazaar phase board (`K4uuWzx5`) live from the Trello API and renders it as a self-contained interactive Gantt chart (`trello_gantt_chart.html`), or with `--a4` as a paginated A4-landscape print version (`trello_gantt_chart_a4.html`). Never creates/updates/deletes anything on Trello - safe to re-run any time to refresh.
- Talks to: [[GanttBoardScript]], [[EnvConfig]]
- Back: [[ARCHITECTURE]]
