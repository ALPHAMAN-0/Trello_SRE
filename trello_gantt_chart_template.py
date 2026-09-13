"""
HTML/CSS/JS template for trello_gantt_chart.py.

Kept in its own module because the generated page is a full design, not a
one-liner - splitting it out mirrors how trello_gantt_board.py already ships
as a shared module the other scripts import from.

render(payload) takes the JSON-shaped dict built by trello_gantt_chart.py
and returns a complete HTML string. The output deliberately has no
<!DOCTYPE>/<html>/<head>/<body> wrapper - browsers render a bare
title+style+body-content file fine when opened directly, and the same file
can be handed unmodified to something that supplies its own document shell.
"""

import json

TITLE = "Shasroy Bazaar Ledger"

_HTML = r"""<title>%%TITLE%%</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: light;
    --page-bg:      #f5f1e5;
    --page-plane:   #efe9d8;
    --surface-1:    #fcfcfb;
    --surface-2:    #f3f0e8;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --text-muted:   #898781;
    --gridline:     #e1e0d9;
    --baseline:     #c3c2b7;
    --border:       rgba(11,11,11,0.10);
    --brand:        #2f2a63;
    --brand-fill:   #453d8c;
    --brand-soft:   rgba(47,42,99,0.09);
    --status-critical: #d03b3b;
    --cat-other:    #a6a49b;
    --cat-1: #2a78d6; /* Backend */
    --cat-2: #eb6834; /* Frontend */
    --cat-3: #1baf7a; /* Architecture */
    --cat-4: #eda100; /* Documentation */
    --cat-5: #e87ba4; /* Security */
    --cat-6: #008300; /* DevOps */
    --cat-7: #4a3aa7; /* Testing */
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --page-bg:      #100e0a;
      --page-plane:   #17150f;
      --surface-1:    #1a1a19;
      --surface-2:    #201f1a;
      --text-primary: #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted:   #898781;
      --gridline:     #2c2c2a;
      --baseline:     #383835;
      --border:       rgba(255,255,255,0.10);
      --brand:        #9b93e8;
      --brand-fill:   #453d8c;
      --brand-soft:   rgba(155,147,232,0.14);
      --status-critical: #d03b3b;
      --cat-other:    #6b6a63;
      --cat-1: #3987e5;
      --cat-2: #d95926;
      --cat-3: #199e70;
      --cat-4: #c98500;
      --cat-5: #d55181;
      --cat-6: #008300;
      --cat-7: #9085e9;
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --page-bg:      #100e0a;
    --page-plane:   #17150f;
    --surface-1:    #1a1a19;
    --surface-2:    #201f1a;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:   #898781;
    --gridline:     #2c2c2a;
    --baseline:     #383835;
    --border:       rgba(255,255,255,0.10);
    --brand:        #9b93e8;
    --brand-fill:   #453d8c;
    --brand-soft:   rgba(155,147,232,0.14);
    --status-critical: #d03b3b;
    --cat-other:    #6b6a63;
    --cat-1: #3987e5;
    --cat-2: #d95926;
    --cat-3: #199e70;
    --cat-4: #c98500;
    --cat-5: #d55181;
    --cat-6: #008300;
    --cat-7: #9085e9;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body {
    background: var(--page-bg);
    color: var(--text-primary);
    font-family: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.5;
  }
  .mono { font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace; }
  .ledger { max-width: 1180px; margin: 0 auto; padding: 28px 24px 64px; }

  a { color: var(--brand); }
  a:focus-visible, button:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
  }

  /* ---------- Masthead ---------- */
  .masthead {
    display: flex; flex-wrap: wrap; gap: 16px 32px; justify-content: space-between; align-items: flex-end;
    padding-bottom: 18px; margin-bottom: 22px;
    border-bottom: 3px solid var(--brand);
  }
  .masthead-id { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .monogram {
    width: 26px; height: 26px; border-radius: 3px; background: var(--brand-fill); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-family: "IBM Plex Mono", monospace; font-weight: 700; font-size: 12px; flex: none;
  }
  .eyebrow {
    margin: 0; font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--text-muted);
  }
  h1 { margin: 4px 0 6px; font-size: 30px; font-weight: 700; letter-spacing: -0.01em; text-wrap: balance; }
  h1 .bn { font-weight: 500; color: var(--text-secondary); font-size: 20px; }
  .subtitle { margin: 0; color: var(--text-secondary); max-width: 46ch; }
  .masthead-right { text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
  .sync-badge {
    display: inline-flex; align-items: center; gap: 7px; font-family: "IBM Plex Mono", monospace;
    font-size: 12px; color: var(--text-secondary);
  }
  .sync-dot { width: 7px; height: 7px; border-radius: 50%; background: #0ca30c; flex: none; }
  .board-link { font-size: 13px; font-weight: 500; text-decoration: none; }
  .board-link:hover { text-decoration: underline; }

  /* ---------- Stat strip ---------- */
  .stats {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 8px;
    overflow: hidden; margin-bottom: 22px;
  }
  .stat { background: var(--surface-1); padding: 14px 16px; }
  .stat-label { margin: 0 0 6px; font-size: 11.5px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }
  .stat-value { font-size: 26px; font-weight: 600; }
  .stat-sub { margin: 3px 0 0; font-size: 12px; color: var(--text-secondary); }

  /* ---------- Controls ---------- */
  .controls {
    display: flex; flex-wrap: wrap; gap: 14px 24px; align-items: center; justify-content: space-between;
    margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid var(--gridline);
  }
  .tabs { display: flex; gap: 6px; flex-wrap: wrap; }
  .tab {
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px; border: 1px solid var(--border);
    background: var(--surface-1); color: var(--text-secondary); border-radius: 6px; padding: 6px 11px;
    cursor: pointer;
  }
  .tab[aria-pressed="true"] { background: var(--brand-fill); border-color: var(--brand-fill); color: #fff; }
  .tab .n { opacity: 0.7; margin-left: 4px; }

  .legend { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; }
  .legend-group { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; }
  .swatch-btn {
    display: inline-flex; align-items: center; gap: 6px; border: 1px solid transparent; background: none;
    font-size: 12.5px; color: var(--text-secondary); cursor: pointer; padding: 3px 6px; border-radius: 5px;
    font-family: "IBM Plex Sans", sans-serif;
  }
  .swatch-btn:hover { background: var(--surface-2); }
  .swatch-btn.is-off { opacity: 0.4; }
  .swatch { width: 10px; height: 10px; border-radius: 2px; flex: none; }
  .legend-sep { width: 1px; height: 16px; background: var(--gridline); }
  .glyph-key { display: flex; gap: 12px; align-items: center; font-size: 12px; color: var(--text-muted); }
  .glyph-key span { display: inline-flex; align-items: center; gap: 5px; }

  .view-toggle {
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px; border: 1px solid var(--border);
    background: var(--surface-1); color: var(--text-primary); border-radius: 6px; padding: 6px 11px; cursor: pointer;
  }
  .view-toggle:hover { background: var(--surface-2); }

  /* ---------- Timeline panels ---------- */
  .panel { margin-bottom: 26px; }
  .panel-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
  .panel-head h2 { margin: 0; font-size: 16px; font-weight: 600; }
  .panel-head .range { font-size: 12.5px; color: var(--text-muted); font-family: "IBM Plex Mono", monospace; }
  .panel-head .sub { font-size: 12.5px; color: var(--text-secondary); }

  .scrollbox {
    border: 1px solid var(--border); border-radius: 8px; background: var(--surface-1);
    max-height: 560px; overflow: auto; position: relative;
  }
  .grid-wrap { position: relative; }

  .header-row { display: flex; position: sticky; top: 0; z-index: 3; background: var(--surface-1); }
  .header-label {
    flex: none; width: var(--label-w); position: sticky; left: 0; z-index: 4; background: var(--surface-1);
    border-bottom: 1px solid var(--gridline); border-right: 1px solid var(--border);
  }
  .header-track { position: relative; border-bottom: 1px solid var(--gridline); }
  .month-band { position: relative; height: 20px; }
  .month-lbl {
    position: absolute; top: 0; height: 20px; display: flex; align-items: center; padding-left: 6px;
    font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--text-muted);
    border-left: 1px solid var(--gridline); box-sizing: border-box;
  }
  .week-band { position: relative; height: 22px; }
  .week-lbl {
    position: absolute; top: 0; height: 22px; display: flex; align-items: center; padding-left: 5px;
    font-family: "IBM Plex Mono", monospace; font-size: 10.5px; color: var(--text-muted);
  }

  .group-row { display: flex; background: var(--page-plane); position: sticky; left: 0; }
  .group-row .group-label {
    width: var(--label-w); flex: none; position: sticky; left: 0; z-index: 2; background: var(--page-plane);
    padding: 6px 12px; font-weight: 600; font-size: 12.5px; border-right: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
  }
  .group-row .group-fill { flex: 1 1 auto; background: var(--page-plane); }
  .group-count { font-weight: 400; color: var(--text-muted); font-family: "IBM Plex Mono", monospace; font-size: 11px; }

  .card-row { display: flex; border-bottom: 1px solid var(--gridline); min-height: 36px; }
  .card-row:hover { background: var(--surface-2); }
  .card-row.dimmed { opacity: 0.28; }
  .row-label {
    width: var(--label-w); flex: none; position: sticky; left: 0; z-index: 1; background: inherit;
    background-color: var(--surface-1); padding: 6px 12px; border-right: 1px solid var(--border);
    display: flex; align-items: center; gap: 8px; min-width: 0;
  }
  .card-row:hover .row-label { background-color: var(--surface-2); }
  .row-key { font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--text-muted); flex: none; }
  .row-title { font-size: 12.5px; overflow-wrap: break-word; }
  .row-track { position: relative; flex: 1 1 auto; }

  .bar {
    position: absolute; top: 50%; transform: translateY(-50%); height: 16px; border-radius: 4px;
    cursor: pointer; min-width: 6px;
  }
  .bar.is-done { opacity: 0.55; }
  .bar-stamp {
    position: absolute; right: 2px; top: 50%; transform: translateY(-50%); font-size: 10px; line-height: 1;
    color: rgba(255,255,255,0.9);
  }
  .risk-flag {
    position: absolute; left: -3px; top: -7px; font-size: 9px; color: var(--status-critical);
  }
  .milestone {
    position: absolute; top: 50%; width: 13px; height: 13px; transform: translate(-50%,-50%) rotate(45deg);
    background: var(--text-primary); border: 2px solid var(--surface-1); cursor: pointer;
  }
  .milestone-label {
    position: absolute; top: 50%; transform: translateY(-50%); white-space: nowrap; font-size: 11px;
    font-weight: 600; color: var(--text-primary); pointer-events: none;
  }
  .gridlines { position: absolute; inset: 0; pointer-events: none; }
  .gridline { position: absolute; top: 0; bottom: 0; width: 1px; background: var(--gridline); }
  .todayline { position: absolute; top: 0; bottom: 0; width: 0; border-left: 2px dashed var(--text-primary); z-index: 2; }
  .todayline .flag {
    position: sticky; top: 24px; display: inline-block; transform: translateX(-50%);
    background: var(--text-primary); color: var(--surface-1); font-family: "IBM Plex Mono", monospace;
    font-size: 10px; font-weight: 700; letter-spacing: 0.04em; padding: 2px 5px; border-radius: 3px; white-space: nowrap;
  }

  /* ---------- Handoff divider ---------- */
  .handoff {
    display: flex; align-items: center; gap: 14px; margin: 4px 0 26px; padding: 10px 16px;
    background: var(--brand-soft); border: 1px dashed var(--brand); border-radius: 8px;
    font-size: 12.5px; color: var(--text-secondary);
  }
  .handoff strong { color: var(--text-primary); }
  .handoff .arrow { font-family: "IBM Plex Mono", monospace; color: var(--brand); font-size: 15px; flex: none; }

  /* ---------- Backlog rail ---------- */
  .backlog-note { margin: 0 0 10px; font-size: 12.5px; color: var(--text-secondary); }
  .backlog-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip {
    display: flex; align-items: center; gap: 8px; background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 7px; padding: 8px 11px; max-width: 320px; cursor: pointer;
  }
  .chip .swatch { width: 8px; height: 8px; }
  .chip-key { font-family: "IBM Plex Mono", monospace; font-size: 10.5px; color: var(--text-muted); }
  .chip-title { font-size: 12px; }

  /* ---------- Table view ---------- */
  .table-wrap { border: 1px solid var(--border); border-radius: 8px; overflow: auto; background: var(--surface-1); }
  table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
  thead th {
    position: sticky; top: 0; background: var(--surface-1); text-align: left; padding: 8px 10px;
    border-bottom: 1px solid var(--gridline); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--text-muted); white-space: nowrap;
  }
  tbody td { padding: 7px 10px; border-bottom: 1px solid var(--gridline); vertical-align: top; }
  tbody tr:hover { background: var(--surface-2); }
  td.key { font-family: "IBM Plex Mono", monospace; color: var(--text-muted); white-space: nowrap; }
  td.dates { font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .pill { display: inline-block; padding: 1px 7px; border-radius: 999px; font-size: 11px; border: 1px solid var(--border); }
  .pill.done { color: #0ca30c; border-color: currentColor; }
  .pill.overdue { color: var(--status-critical); border-color: currentColor; }
  .pill.active { color: var(--brand); border-color: currentColor; }
  .pill.scheduled { color: var(--text-muted); }

  /* ---------- Tooltip ---------- */
  #tooltip {
    position: fixed; z-index: 50; max-width: 300px; background: var(--text-primary); color: var(--page-bg);
    border-radius: 7px; padding: 10px 12px; font-size: 12.5px; pointer-events: none; box-shadow: 0 8px 24px rgba(0,0,0,0.28);
  }
  #tooltip .tt-key { font-family: "IBM Plex Mono", monospace; font-size: 11px; opacity: 0.7; }
  #tooltip .tt-title { font-weight: 600; margin: 2px 0 6px; }
  #tooltip .tt-row { display: flex; justify-content: space-between; gap: 12px; margin: 2px 0; opacity: 0.9; }
  #tooltip .tt-link { display: inline-block; margin-top: 6px; color: inherit; text-decoration: underline; opacity: 0.85; }
  #tooltip .tt-labels { margin-top: 6px; opacity: 0.8; font-size: 11.5px; }

  footer {
    margin-top: 30px; padding-top: 16px; border-top: 1px solid var(--gridline);
    font-size: 12px; color: var(--text-muted); display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;
  }

  @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
  @media (max-width: 640px) {
    h1 { font-size: 24px; }
    .masthead { align-items: flex-start; }
    .masthead-right { align-items: flex-start; text-align: left; }
  }
</style>

<div class="ledger">
  <header class="masthead">
    <div>
      <div class="masthead-id">
        <span class="monogram">SB</span>
        <p class="eyebrow">Project ledger &middot; খতিয়ান</p>
      </div>
      <h1>Shasroy Bazaar <span class="bn">সাশ্রয় বাজার</span></h1>
      <p class="subtitle">One schedule, two clocks: the coursework sprint that ends this week, and the solo build roadmap that starts the day after.</p>
    </div>
    <div class="masthead-right">
      <span class="sync-badge"><span class="sync-dot"></span>Synced with Trello &middot; <span id="synced-at"></span></span>
      <a class="board-link" id="board-link" href="#" target="_blank" rel="noopener">Open board on Trello &#8599;</a>
    </div>
  </header>

  <section class="stats" id="stats" aria-label="Ledger totals"></section>

  <section class="controls">
    <div class="tabs" id="tabs" role="group" aria-label="Filter by track"></div>
    <div class="legend">
      <div class="legend-group" id="legend"></div>
      <div class="legend-sep"></div>
      <div class="glyph-key">
        <span><svg width="11" height="11" viewBox="0 0 11 11"><rect x="1.5" y="1.5" width="6" height="6" transform="rotate(45 4.5 4.5)" fill="currentColor"/></svg> milestone</span>
        <span style="color:var(--status-critical)">&#9650; high-risk</span>
        <span>&#10003; done</span>
      </div>
    </div>
    <button class="view-toggle" id="view-toggle" type="button">Table view</button>
  </section>

  <div id="timeline-view">
    <section class="panel" id="panel-sre">
      <div class="panel-head">
        <h2>Course Sprint</h2>
        <span class="range" id="sre-range"></span>
        <span class="sub">grouped by phase</span>
      </div>
      <div class="scrollbox"><div class="grid-wrap" id="sre-grid"></div></div>
    </section>

    <div class="handoff" id="handoff">
      <span class="arrow">&#8618;</span>
      <span id="handoff-text"></span>
    </div>

    <section class="panel" id="panel-dev">
      <div class="panel-head">
        <h2>Build Roadmap</h2>
        <span class="range" id="dev-range"></span>
        <span class="sub">grouped by sprint</span>
      </div>
      <div class="scrollbox"><div class="grid-wrap" id="dev-grid"></div></div>
    </section>

    <section class="panel" id="panel-backlog">
      <div class="panel-head"><h2>Post-v1 Backlog</h2></div>
      <p class="backlog-note">Not scheduled &mdash; deliberately out of v1 scope. Held until <strong class="mono">DEV-66</strong> ships.</p>
      <div class="backlog-chips" id="backlog-chips"></div>
    </section>
  </div>

  <section class="table-wrap" id="table-view" hidden>
    <table>
      <thead><tr>
        <th>Key</th><th>Title</th><th>Track</th><th>Group</th><th>Start</th><th>Due</th><th>Status</th><th>Category</th><th>Flags</th>
      </tr></thead>
      <tbody id="table-body"></tbody>
    </table>
  </section>

  <footer>
    <span>Generated by <span class="mono">trello_gantt_chart.py</span> &middot; read-only, re-run any time to refresh.</span>
    <span id="footer-counts"></span>
  </footer>
</div>

<div id="tooltip" role="tooltip" hidden></div>

<script>
const DATA = %%DATA_JSON%%;

(function () {
  const PX_PER_DAY = 30;
  const LABEL_W = 300;
  document.documentElement.style.setProperty('--label-w', LABEL_W + 'px');

  const CAT_COLOR = {};
  DATA.categories.forEach(c => { CAT_COLOR[c.name] = c.slot === 'other' ? 'var(--cat-other)' : `var(--cat-${c.slot})`; });
  function colorFor(bucket) { return CAT_COLOR[bucket] || 'var(--cat-other)'; }

  function toUTC(iso) { return new Date(iso + 'T00:00:00Z'); }
  function dayOffset(iso, startIso) { return Math.round((toUTC(iso) - toUTC(startIso)) / 86400000); }
  function fmtShort(iso) {
    if (!iso) return '–';
    const d = toUTC(iso);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' });
  }
  function fmtFull(iso) {
    if (!iso) return '–';
    const d = toUTC(iso);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
  }

  function cardStatus(c) {
    if (c.done) return { key: 'done', label: 'Done' };
    if (c.due && c.due < DATA.today) return { key: 'overdue', label: 'Overdue' };
    if (c.start && c.start <= DATA.today && (!c.due || c.due >= DATA.today)) return { key: 'active', label: 'In window' };
    return { key: 'scheduled', label: 'Scheduled' };
  }

  // ---------------- Masthead ----------------
  document.getElementById('synced-at').textContent = DATA.generatedAt;
  const boardLink = document.getElementById('board-link');
  boardLink.href = DATA.board.url;
  boardLink.textContent = 'Open ' + DATA.board.name + ' on Trello ↗';

  // ---------------- Stats ----------------
  function statTile(label, value, sub) {
    const el = document.createElement('div');
    el.className = 'stat';
    const l = document.createElement('p'); l.className = 'stat-label'; l.textContent = label;
    const v = document.createElement('p'); v.className = 'stat-value'; v.textContent = value;
    el.append(l, v);
    if (sub) { const s = document.createElement('p'); s.className = 'stat-sub'; s.textContent = sub; el.append(s); }
    return el;
  }
  (function buildStats() {
    const stats = document.getElementById('stats');
    const t = DATA.totals;
    stats.append(statTile('Tasks on the ledger', t.cards, `${t.sre} course · ${t.dev} build · ${t.backlog} backlog`));
    stats.append(statTile('Checked off', `${t.done}/${t.cards}`, Math.round(100 * t.done / t.cards) + '% complete'));

    const today = DATA.today;
    let countLabel, countValue, countSub;
    if (today <= DATA.sre.end) {
      const days = dayOffset(DATA.sre.end, today);
      countLabel = 'To final submission';
      countValue = days <= 0 ? 'Today' : days + 'd';
      countSub = 'Course sprint ends ' + fmtFull(DATA.sre.end);
    } else if (today <= DATA.dev.end) {
      const into = dayOffset(today, DATA.dev.start) + 1;
      const span = dayOffset(DATA.dev.end, DATA.dev.start) + 1;
      countLabel = 'Into the build roadmap';
      countValue = `Day ${into}`;
      countSub = `of ${span} · v1.0 targeted ${fmtFull(DATA.dev.end)}`;
    } else {
      countLabel = 'Build roadmap';
      countValue = 'Complete';
      countSub = 'v1.0 targeted ' + fmtFull(DATA.dev.end);
    }
    stats.append(statTile(countLabel, countValue, countSub));
    stats.append(statTile('Milestones', t.milestones, t.highRisk + ' cards flagged high-risk'));
  })();

  // ---------------- Legend ----------------
  const activeCats = new Set();
  function refreshDimming() {
    document.querySelectorAll('[data-bucket]').forEach(el => {
      el.classList.toggle('dimmed', activeCats.size > 0 && !activeCats.has(el.dataset.bucket));
    });
    document.querySelectorAll('.swatch-btn[data-cat]').forEach(btn => {
      btn.classList.toggle('is-off', activeCats.size > 0 && !activeCats.has(btn.dataset.cat));
    });
  }
  (function buildLegend() {
    const legend = document.getElementById('legend');
    DATA.categories.forEach(c => {
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'swatch-btn'; btn.dataset.cat = c.name;
      const sw = document.createElement('span'); sw.className = 'swatch';
      sw.style.background = c.slot === 'other' ? 'var(--cat-other)' : `var(--cat-${c.slot})`;
      const label = document.createElement('span'); label.textContent = `${c.name} (${c.count})`;
      btn.append(sw, label);
      btn.addEventListener('click', () => {
        if (activeCats.has(c.name)) activeCats.delete(c.name); else activeCats.add(c.name);
        refreshDimming();
      });
      legend.append(btn);
    });
  })();

  // ---------------- Tabs ----------------
  const PANELS = { all: null, sre: 'panel-sre', dev: 'panel-dev', backlog: 'panel-backlog' };
  (function buildTabs() {
    const tabs = document.getElementById('tabs');
    const defs = [
      ['all', 'All', DATA.totals.cards],
      ['sre', 'Course Sprint', DATA.totals.sre],
      ['dev', 'Build Roadmap', DATA.totals.dev],
      ['backlog', 'Backlog', DATA.totals.backlog],
    ];
    let active = 'all';
    defs.forEach(([key, label, n]) => {
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'tab'; btn.setAttribute('aria-pressed', key === 'all');
      btn.innerHTML = ''; // built via textContent below, no injected data here (static labels only)
      const span = document.createElement('span'); span.textContent = label;
      const n_ = document.createElement('span'); n_.className = 'n'; n_.textContent = n;
      btn.append(span, n_);
      btn.addEventListener('click', () => {
        active = key;
        tabs.querySelectorAll('.tab').forEach(t => t.setAttribute('aria-pressed', 'false'));
        btn.setAttribute('aria-pressed', 'true');
        ['panel-sre', 'panel-dev', 'panel-backlog'].forEach(id => {
          const el = document.getElementById(id);
          el.hidden = key !== 'all' && PANELS[key] !== id;
        });
        document.getElementById('handoff').hidden = key !== 'all';
      });
      tabs.append(btn);
    });
  })();

  // ---------------- Tooltip ----------------
  const tooltip = document.getElementById('tooltip');
  function showTooltip(card, x, y) {
    tooltip.innerHTML = '';
    const key = document.createElement('div'); key.className = 'tt-key mono'; key.textContent = card.key;
    const title = document.createElement('div'); title.className = 'tt-title'; title.textContent = card.title;
    tooltip.append(key, title);
    const status = cardStatus(card);
    const rows = [
      [card.track === 'SRE' ? 'Phase' : 'Sprint', card.track === 'SRE' ? card.phase : (card.sprint || '–')],
      ['Dates', card.start ? `${fmtShort(card.start)} → ${fmtShort(card.due)}` : fmtShort(card.due)],
      ['Status', status.label],
      ['Category', card.bucket],
    ];
    rows.forEach(([k, v]) => {
      const row = document.createElement('div'); row.className = 'tt-row';
      const a = document.createElement('span'); a.textContent = k; a.style.opacity = '0.6';
      const b = document.createElement('span'); b.textContent = v;
      row.append(a, b); tooltip.append(row);
    });
    if (card.highRisk) {
      const r = document.createElement('div'); r.className = 'tt-row';
      r.textContent = '⚠ Flagged high-risk';
      tooltip.append(r);
    }
    if (card.labels.length) {
      const l = document.createElement('div'); l.className = 'tt-labels';
      l.textContent = card.labels.join(' · ');
      tooltip.append(l);
    }
    const link = document.createElement('a'); link.className = 'tt-link'; link.href = card.url;
    link.target = '_blank'; link.rel = 'noopener'; link.textContent = 'Open in Trello ↗';
    tooltip.append(link);

    tooltip.hidden = false;
    const vw = window.innerWidth, vh = window.innerHeight;
    const rect = tooltip.getBoundingClientRect();
    let left = x + 14, top = y + 14;
    if (left + rect.width > vw - 8) left = x - rect.width - 14;
    if (top + rect.height > vh - 8) top = y - rect.height - 14;
    tooltip.style.left = Math.max(8, left) + 'px';
    tooltip.style.top = Math.max(8, top) + 'px';
  }
  function hideTooltip() { tooltip.hidden = true; }

  // ---------------- Timeline panel builder ----------------
  function buildTicks(startIso, endIso) {
    const totalDays = dayOffset(endIso, startIso) + 1;
    const width = totalDays * PX_PER_DAY;
    const monthBands = [];
    const weekTicks = [];
    let cursor = toUTC(startIso);
    const end = toUTC(endIso);
    while (cursor <= end) {
      const dayIdx = Math.round((cursor - toUTC(startIso)) / 86400000);
      if (dayIdx === 0 || cursor.getUTCDate() === 1) {
        const monthStart = dayIdx;
        const monthEndDate = new Date(Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1));
        const monthEndIdx = Math.min(totalDays, Math.round((monthEndDate - toUTC(startIso)) / 86400000));
        monthBands.push({
          label: cursor.toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' }),
          left: monthStart * PX_PER_DAY, width: (monthEndIdx - monthStart) * PX_PER_DAY,
        });
      }
      if (dayIdx % 7 === 0) {
        weekTicks.push({ label: fmtShort(cursor.toISOString().slice(0, 10)), left: dayIdx * PX_PER_DAY });
      }
      cursor = new Date(cursor.getTime() + 86400000);
    }
    return { totalDays, width, monthBands, weekTicks };
  }

  function groupCards(cards, groups) {
    const byGroup = new Map(groups.map(g => [g, []]));
    cards.forEach(c => {
      const g = c.track === 'SRE' ? c.phase : c.sprint;
      if (byGroup.has(g)) byGroup.get(g).push(c);
    });
    return byGroup;
  }

  function renderPanel(gridEl, track, section, rangeEl) {
    const { start, end, groups, cards } = section;
    const scheduled = cards.filter(c => c.start || (c.milestone && c.due));
    const { totalDays, width, monthBands, weekTicks } = buildTicks(start, end);
    rangeEl.textContent = `${fmtFull(start)} → ${fmtFull(end)} · ${totalDays} days`;

    const frag = document.createDocumentFragment();

    // header
    const header = document.createElement('div'); header.className = 'header-row';
    const headerLabel = document.createElement('div'); headerLabel.className = 'header-label';
    const headerTrack = document.createElement('div'); headerTrack.className = 'header-track'; headerTrack.style.width = width + 'px';
    const monthRow = document.createElement('div'); monthRow.className = 'month-band';
    monthBands.forEach(b => {
      const el = document.createElement('div'); el.className = 'month-lbl';
      el.style.left = b.left + 'px'; el.style.width = b.width + 'px'; el.textContent = b.label;
      monthRow.append(el);
    });
    const weekRow = document.createElement('div'); weekRow.className = 'week-band';
    weekTicks.forEach(t => {
      const el = document.createElement('div'); el.className = 'week-lbl';
      el.style.left = t.left + 'px'; el.textContent = t.label;
      weekRow.append(el);
    });
    headerTrack.append(monthRow, weekRow);
    header.append(headerLabel, headerTrack);
    frag.append(header);

    const byGroup = groupCards(scheduled, groups);
    groups.forEach(g => {
      const rows = byGroup.get(g) || [];
      if (!rows.length) return;
      const gRow = document.createElement('div'); gRow.className = 'group-row';
      const gLabel = document.createElement('div'); gLabel.className = 'group-label';
      const gName = document.createElement('span'); gName.textContent = g;
      const gCount = document.createElement('span'); gCount.className = 'group-count'; gCount.textContent = rows.length;
      gLabel.append(gName, gCount);
      const gFill = document.createElement('div'); gFill.className = 'group-fill'; gFill.style.width = width + 'px';
      gRow.append(gLabel, gFill);
      frag.append(gRow);

      rows.forEach(c => {
        const row = document.createElement('div'); row.className = 'card-row'; row.dataset.bucket = c.bucket;
        const label = document.createElement('div'); label.className = 'row-label';
        const key = document.createElement('span'); key.className = 'row-key'; key.textContent = c.key;
        const title = document.createElement('span'); title.className = 'row-title'; title.textContent = c.title;
        label.append(key, title);

        const trackEl = document.createElement('div'); trackEl.className = 'row-track'; trackEl.style.width = width + 'px';
        const activate = (e) => {
          const pt = e.touches ? e.touches[0] : e;
          showTooltip(c, pt.clientX, pt.clientY);
        };

        if (c.milestone) {
          const left = dayOffset(c.due, start) * PX_PER_DAY + PX_PER_DAY / 2;
          const dot = document.createElement('div'); dot.className = 'milestone';
          dot.style.left = left + 'px'; dot.tabIndex = 0;
          dot.setAttribute('role', 'button'); dot.setAttribute('aria-label', c.key + ' milestone: ' + c.title);
          const lbl = document.createElement('div'); lbl.className = 'milestone-label';
          lbl.style.left = (left + 12) + 'px'; lbl.textContent = c.title;
          dot.addEventListener('pointerenter', activate);
          dot.addEventListener('pointermove', activate);
          dot.addEventListener('focus', (e) => { const r = dot.getBoundingClientRect(); showTooltip(c, r.left, r.top); });
          dot.addEventListener('pointerleave', hideTooltip);
          dot.addEventListener('blur', hideTooltip);
          trackEl.append(dot, lbl);
        } else {
          const left = dayOffset(c.start, start) * PX_PER_DAY;
          const w = Math.max(PX_PER_DAY - 4, (dayOffset(c.due, start) - dayOffset(c.start, start) + 1) * PX_PER_DAY - 4);
          const bar = document.createElement('div'); bar.className = 'bar' + (c.done ? ' is-done' : '');
          bar.style.left = (left + 2) + 'px'; bar.style.width = w + 'px'; bar.style.background = colorFor(c.bucket);
          bar.tabIndex = 0; bar.setAttribute('role', 'button');
          bar.setAttribute('aria-label', `${c.key} ${c.title}, ${fmtFull(c.start)} to ${fmtFull(c.due)}`);
          if (c.done) { const s = document.createElement('span'); s.className = 'bar-stamp'; s.textContent = '✓'; bar.append(s); }
          if (c.highRisk) { const r = document.createElement('span'); r.className = 'risk-flag'; r.textContent = '▲'; bar.append(r); }
          bar.addEventListener('pointerenter', activate);
          bar.addEventListener('pointermove', activate);
          bar.addEventListener('focus', () => { const r = bar.getBoundingClientRect(); showTooltip(c, r.left, r.top); });
          bar.addEventListener('pointerleave', hideTooltip);
          bar.addEventListener('blur', hideTooltip);
          trackEl.append(bar);
        }
        row.append(label, trackEl);
        frag.append(row);
      });
    });

    // gridlines + today line sit in a full-height absolute layer appended last
    gridEl.appendChild(frag);
    gridEl.style.setProperty('--full-width', width + 'px');

    const gridLayer = document.createElement('div'); gridLayer.className = 'gridlines';
    gridLayer.style.left = LABEL_W + 'px'; gridLayer.style.width = width + 'px';
    weekTicks.forEach(t => {
      const line = document.createElement('div'); line.className = 'gridline'; line.style.left = t.left + 'px';
      gridLayer.append(line);
    });
    if (DATA.today >= start && DATA.today <= end) {
      const line = document.createElement('div'); line.className = 'todayline';
      line.style.left = (dayOffset(DATA.today, start) * PX_PER_DAY) + 'px';
      const flag = document.createElement('span'); flag.className = 'flag'; flag.textContent = 'TODAY · ' + fmtShort(DATA.today);
      line.append(flag);
      gridLayer.append(line);
    }
    gridEl.style.position = 'relative';
    gridEl.appendChild(gridLayer);
  }

  renderPanel(document.getElementById('sre-grid'), 'SRE', DATA.sre, document.getElementById('sre-range'));
  renderPanel(document.getElementById('dev-grid'), 'DEV', DATA.dev, document.getElementById('dev-range'));

  // handoff line
  const lastSre = DATA.sre.cards.slice().sort((a, b) => (b.due || '').localeCompare(a.due || ''))[0];
  const firstDev = DATA.dev.cards.filter(c => c.track === 'DEV').slice().sort((a, b) => (a.start || '').localeCompare(b.start || ''))[0];
  document.getElementById('handoff-text').textContent =
    `${lastSre.key} “${lastSre.title}” closes the course sprint on ${fmtFull(lastSre.due)} — `
    + `${firstDev.key} “${firstDev.title}” opens the build roadmap the next day.`;

  // ---------------- Backlog chips ----------------
  (function buildBacklog() {
    const wrap = document.getElementById('backlog-chips');
    DATA.dev.cards.filter(c => c.track === 'BL').forEach(c => {
      const chip = document.createElement('div'); chip.className = 'chip'; chip.dataset.bucket = c.bucket;
      chip.tabIndex = 0; chip.setAttribute('role', 'button');
      const sw = document.createElement('span'); sw.className = 'swatch'; sw.style.background = colorFor(c.bucket);
      const box = document.createElement('div');
      const key = document.createElement('div'); key.className = 'chip-key'; key.textContent = c.key;
      const title = document.createElement('div'); title.className = 'chip-title'; title.textContent = c.title;
      box.append(key, title);
      chip.append(sw, box);
      const activate = (e) => { const pt = e.touches ? e.touches[0] : e; showTooltip(c, pt.clientX, pt.clientY); };
      chip.addEventListener('pointerenter', activate);
      chip.addEventListener('pointermove', activate);
      chip.addEventListener('focus', () => { const r = chip.getBoundingClientRect(); showTooltip(c, r.left, r.top); });
      chip.addEventListener('pointerleave', hideTooltip);
      chip.addEventListener('blur', hideTooltip);
      wrap.append(chip);
    });
  })();

  // ---------------- Table view ----------------
  (function buildTable() {
    const tbody = document.getElementById('table-body');
    const all = DATA.sre.cards.concat(DATA.dev.cards)
      .slice()
      .sort((a, b) => (a.start || a.due || '9999-99-99').localeCompare(b.start || b.due || '9999-99-99'));
    all.forEach(c => {
      const tr = document.createElement('tr');
      const status = cardStatus(c);
      const cells = [
        ['key', c.key],
        [null, c.title],
        [null, c.track],
        [null, c.track === 'SRE' ? c.phase : (c.sprint || '–')],
        ['dates', fmtShort(c.start)],
        ['dates', fmtShort(c.due)],
      ];
      cells.forEach(([cls, text]) => {
        const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = text;
        tr.append(td);
      });
      const statusTd = document.createElement('td');
      const pill = document.createElement('span'); pill.className = 'pill ' + status.key; pill.textContent = status.label;
      statusTd.append(pill); tr.append(statusTd);
      const catTd = document.createElement('td'); catTd.textContent = c.bucket; tr.append(catTd);
      const flagsTd = document.createElement('td');
      flagsTd.textContent = [c.milestone ? 'milestone' : null, c.highRisk ? 'high-risk' : null].filter(Boolean).join(', ') || '–';
      tr.append(flagsTd);
      tbody.append(tr);
    });
  })();

  // ---------------- View toggle ----------------
  const viewToggle = document.getElementById('view-toggle');
  const timelineView = document.getElementById('timeline-view');
  const tableView = document.getElementById('table-view');
  let showingTable = false;
  viewToggle.addEventListener('click', () => {
    showingTable = !showingTable;
    timelineView.hidden = showingTable;
    tableView.hidden = !showingTable;
    viewToggle.textContent = showingTable ? 'Timeline view' : 'Table view';
  });

  document.getElementById('footer-counts').textContent =
    `${DATA.totals.done}/${DATA.totals.cards} checked off · ${DATA.totals.milestones} milestones · board: ${DATA.board.name}`;
})();
</script>
"""


def render(payload):
    html = _HTML.replace("%%TITLE%%", TITLE)
    html = html.replace("%%DATA_JSON%%", json.dumps(payload, ensure_ascii=False))
    return html
