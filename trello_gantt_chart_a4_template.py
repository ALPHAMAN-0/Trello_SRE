"""
A4 print layout for trello_gantt_chart.py --a4.

The screen chart (trello_gantt_chart_template.py) is one long scrolling
page - far too wide and tall for paper. This layout paginates the same
payload into A4-landscape sheets instead:

  1. Overview - totals, a one-bar-per-phase/sprint summary Gantt, milestones
  2+. Course Sprint detail, grouped by phase, on one shared date window
  3+. Build Roadmap detail, grouped by sprint; each page starts at its own
      sprints but spans the same number of days, so a day is one width
  Last: the unscheduled post-v1 backlog

Every sheet is exactly 297 x 210 mm with its own date axis, so pages can be
printed, saved as PDF, or screenshotted one at a time (append #sheet-N to
the URL to show only sheet N). Pagination measures real rendered row
heights in the browser, so long titles that wrap never push rows off a page.
"""

import json

TITLE = "Shasroy Bazaar Schedule (A4)"

_HTML = r"""<title>%%TITLE%%</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+Bengali:wght@500;600&display=swap" rel="stylesheet">
<style>
  @page { size: A4 landscape; margin: 0; }
  :root {
    color-scheme: light;
    --ink: #0b0b0b;
    --ink-2: #4a4945;
    --muted: #77756e;
    --grid: #e4e3dd;
    --grid-2: #cfcdc4;
    --band: #f2f2ef;
    --paper: #ffffff;
    --desk: #d6d6d2;
    --brand: #2f2a63;
    --brand-fill: #453d8c;
    --brand-soft: #e4e2f0;
    --critical: #d03b3b;
    --cat-other: #a6a49b;
    --cat-1: #2a78d6;
    --cat-2: #eb6834;
    --cat-3: #1baf7a;
    --cat-4: #eda100;
    --cat-5: #e87ba4;
    --cat-6: #008300;
    --cat-7: #4a3aa7;
  }
  * { box-sizing: border-box; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body {
    margin: 0; background: var(--desk); color: var(--ink);
    font-family: "IBM Plex Sans", "Noto Sans Bengali", system-ui, -apple-system, "Segoe UI", sans-serif;
    font-size: 10.5px; line-height: 1.3;
  }
  .mono { font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; }
  .bn { font-family: "Noto Sans Bengali", "Kohinoor Bangla", "Bangla Sangam MN", sans-serif; }

  /* ---------- Screen-only toolbar ---------- */
  .toolbar {
    display: flex; justify-content: center; align-items: center; gap: 14px; padding: 12px;
    font-size: 12px; color: var(--ink-2);
  }
  .toolbar button {
    font: 600 12px "IBM Plex Sans", sans-serif; color: #fff; background: var(--brand-fill);
    border: 0; border-radius: 5px; padding: 7px 14px; cursor: pointer;
  }
  .toolbar button:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }

  /* ---------- Sheet ---------- */
  .sheet {
    /* 0.5mm under A4: Chrome's A4 page is a hair short of 210mm, and a full-
       height sheet would spill a blank page onto the end of the PDF. */
    width: 297mm; height: 209.5mm; margin: 0 auto 8mm; background: var(--paper);
    padding: 9mm 12mm 8mm; display: flex; flex-direction: column; gap: 6px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.18), 0 8px 24px rgba(0,0,0,0.08);
    break-after: page; page-break-after: always;
  }
  .sheet:last-child { break-after: auto; page-break-after: auto; }
  @media print {
    body { background: var(--paper); }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; }
  }
  body.solo { background: var(--paper); }
  body.solo .toolbar, body.solo .sheet { display: none; }
  body.solo .sheet.on { display: flex; margin: 0; box-shadow: none; }

  .run {
    display: flex; justify-content: space-between; align-items: baseline; gap: 16px;
    font-size: 9px; color: var(--muted); padding-bottom: 4px; border-bottom: 1.5px solid var(--brand);
  }
  .run b { color: var(--ink); font-weight: 600; }
  .run .pg { margin-left: 12px; color: var(--ink); font-weight: 600; }
  .sheet-body { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 7px; }
  .foot {
    display: flex; justify-content: space-between; gap: 16px; font-size: 8.5px; color: var(--muted);
    border-top: 1px solid var(--grid); padding-top: 4px;
  }

  /* ---------- Section heading + legend ---------- */
  .sec-head { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
  .sec-head h2 { margin: 0; font-size: 14px; font-weight: 700; }
  .sec-head .range { font-family: "IBM Plex Mono", monospace; font-size: 9.5px; color: var(--ink-2); }
  .sec-head .sub { font-size: 9.5px; color: var(--muted); }
  .legend { display: flex; flex-wrap: wrap; align-items: center; gap: 3px 12px; font-size: 8.8px; color: var(--ink-2); }
  .legend .it { display: inline-flex; align-items: center; gap: 4px; }
  .legend .sw { width: 10px; height: 7px; border-radius: 2px; }
  .legend .sep { width: 1px; height: 10px; background: var(--grid-2); }
  .legend .gl { font-weight: 700; width: 9px; text-align: center; }
  .legend .dash { width: 0; height: 10px; border-left: 1.5px dashed var(--ink); }

  /* ---------- Timeline box ---------- */
  .tl {
    flex: 1; min-height: 0; display: flex; flex-direction: column;
    border: 1px solid var(--grid-2); border-radius: 4px; overflow: hidden;
  }
  .tl.ov { flex: none; }
  .axis { display: grid; grid-template-columns: var(--lw) 1fr; border-bottom: 1px solid var(--grid-2); flex: none; }
  .axis-lab {
    display: grid; grid-template-columns: 44px 1fr 78px 12px; gap: 0 5px; align-items: end;
    padding: 0 8px 4px; font-size: 7.8px; text-transform: uppercase; letter-spacing: 0.07em;
    color: var(--muted); border-right: 1px solid var(--grid-2);
  }
  .axis-lab.ov { grid-template-columns: 1fr 40px 48px; }
  .axis-lab.ov span:nth-child(n+2) { text-align: right; }
  .axis-trk { position: relative; height: 32px; overflow: hidden; }
  .mband {
    position: absolute; top: 0; height: 16px; padding: 2px 0 0 4px; white-space: nowrap; overflow: hidden;
    font-family: "IBM Plex Mono", monospace; font-size: 8.5px; color: var(--ink-2);
    border-left: 1px solid var(--grid-2);
  }
  .dnum {
    position: absolute; top: 16px; height: 16px; line-height: 16px; text-align: center; white-space: nowrap;
    font-family: "IBM Plex Mono", monospace; font-size: 7.8px; color: var(--muted);
  }
  .dnum.wide { text-align: left; padding-left: 3px; }
  .dnum.mon { color: var(--ink); font-weight: 600; }
  .today-flag {
    position: absolute; top: 1px; transform: translateX(-50%); z-index: 3; white-space: nowrap;
    background: var(--ink); color: var(--paper); border-radius: 2px; padding: 1px 4px;
    font-family: "IBM Plex Mono", monospace; font-size: 7.5px; font-weight: 700; letter-spacing: 0.03em;
  }

  .rows { flex: 1; min-height: 0; overflow: hidden; position: relative; }
  .tl.ov .rows { flex: none; overflow: visible; }
  .grp { display: grid; grid-template-columns: var(--lw) 1fr; background: var(--band); border-bottom: 1px solid var(--grid); }
  .grp .gl {
    display: flex; justify-content: space-between; gap: 8px; padding: 2px 8px;
    font-size: 10px; font-weight: 600; border-right: 1px solid var(--grid-2);
  }
  .grp .gc { font-family: "IBM Plex Mono", monospace; font-size: 8.5px; font-weight: 400; color: var(--muted); }
  .row { display: grid; grid-template-columns: var(--lw) 1fr; min-height: 17px; border-bottom: 1px solid var(--grid); }
  .lab {
    display: grid; grid-template-columns: 44px 1fr 78px 12px; gap: 0 5px; align-items: center;
    padding: 1px 8px; border-right: 1px solid var(--grid-2);
  }
  .lab.ov { grid-template-columns: 1fr 40px 48px; }
  .lab.ov .n, .lab.ov .p { text-align: right; font-family: "IBM Plex Mono", monospace; font-size: 9px; font-variant-numeric: tabular-nums; }
  .lab .k { font-family: "IBM Plex Mono", monospace; font-size: 8.5px; color: var(--muted); }
  .lab .t { font-size: 10.5px; }
  .lab .d { font-family: "IBM Plex Mono", monospace; font-size: 8.8px; color: var(--ink-2); font-variant-numeric: tabular-nums; white-space: nowrap; }
  .lab .s { font-size: 9.5px; font-weight: 700; text-align: center; }
  .s.done { color: var(--ink); }
  .s.overdue { color: var(--critical); }
  .s.active { color: var(--brand-fill); }
  .trk { position: relative; }

  .bar { position: absolute; top: 50%; height: 9px; margin-top: -4.5px; border-radius: 3px; }
  .bar.done { opacity: 0.45; }
  .risk { position: absolute; top: 50%; margin-top: -6px; line-height: 12px; font-size: 7.5px; color: var(--critical); }
  .ms {
    position: absolute; top: 50%; width: 8px; height: 8px; margin: -4px 0 0 -4px;
    transform: rotate(45deg); background: var(--ink);
  }
  .msl { position: absolute; top: 50%; transform: translateY(-50%); white-space: nowrap; font-size: 9px; font-weight: 600; z-index: 3; background: var(--paper); padding: 0 3px; }
  .sbar { position: absolute; top: 50%; height: 10px; margin-top: -5px; border-radius: 3px; background: var(--brand-soft); overflow: hidden; }
  .sfill { height: 100%; background: var(--brand-fill); }
  .unsched { position: absolute; left: 6px; top: 50%; transform: translateY(-50%); font-size: 9px; font-style: italic; color: var(--muted); white-space: nowrap; z-index: 3; background: var(--paper); padding: 0 3px; }

  .gridlayer { position: absolute; top: 0; left: var(--lw); right: 0; z-index: 0; pointer-events: none; }
  .gline { position: absolute; top: 0; bottom: 0; width: 1px; background: var(--grid); }
  .today { position: absolute; top: 0; width: 0; border-left: 1.5px dashed var(--ink); z-index: 2; pointer-events: none; }

  /* ---------- Backlog block ---------- */
  .bl { border-top: 1px solid var(--grid-2); padding: 6px 8px 4px; background: var(--paper); position: relative; z-index: 3; }
  .bl-h { font-size: 10px; font-weight: 600; margin-bottom: 4px; }
  .bl-h span { font-weight: 400; color: var(--muted); }
  .bl-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 3px 24px; }
  .bl-it { display: grid; grid-template-columns: 10px 40px 1fr auto; gap: 6px; align-items: center; }
  .bl-it .sw { width: 8px; height: 8px; border-radius: 2px; }
  .bl-it .k { font-family: "IBM Plex Mono", monospace; font-size: 8.5px; color: var(--muted); }
  .bl-it .cat { font-size: 8.8px; color: var(--muted); }

  /* ---------- Overview ---------- */
  .ov-top { display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; }
  .ov-id { display: flex; align-items: center; gap: 8px; }
  .badge {
    width: 22px; height: 22px; border-radius: 3px; background: var(--brand-fill); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-family: "IBM Plex Mono", monospace; font-size: 10px; font-weight: 700;
  }
  .eyebrow { font-family: "IBM Plex Mono", monospace; font-size: 9px; letter-spacing: 0.09em; text-transform: uppercase; color: var(--muted); }
  h1 { margin: 4px 0 3px; font-size: 24px; font-weight: 700; letter-spacing: -0.01em; }
  h1 .bn { font-size: 16px; font-weight: 500; color: var(--ink-2); }
  .lede { margin: 0; font-size: 10.5px; color: var(--ink-2); max-width: 70ch; }
  .ov-meta { text-align: right; font-family: "IBM Plex Mono", monospace; font-size: 9px; color: var(--ink-2); line-height: 1.6; }
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid var(--grid-2); border-radius: 4px; }
  .stat { padding: 6px 10px; border-right: 1px solid var(--grid); }
  .stat:last-child { border-right: 0; }
  .stat .l { font-size: 7.8px; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); }
  .stat .v { font-size: 18px; font-weight: 600; margin: 1px 0; }
  .stat .x { font-size: 9px; color: var(--ink-2); }
  .mlist { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px 18px; }
  .mi { display: grid; grid-template-columns: 8px 40px 42px 1fr 10px; gap: 5px; align-items: center; font-size: 9.5px; }
  .mi .dm { width: 6px; height: 6px; transform: rotate(45deg); background: var(--ink); margin-left: 1px; }
  .mi .dt { font-family: "IBM Plex Mono", monospace; font-size: 8.8px; font-variant-numeric: tabular-nums; }
  .mi .k { font-family: "IBM Plex Mono", monospace; font-size: 8.5px; color: var(--muted); }
  .mi .s { font-weight: 700; text-align: center; }
</style>

<div class="toolbar" id="toolbar">
  <span id="toolbar-info">A4 landscape</span>
  <button type="button" onclick="window.print()">Print</button>
</div>
<main id="doc"></main>

<script>
const DATA = %%DATA_JSON%%;

(function () {
  const LABEL_W = 420;
  const OV_LABEL_W = 300;
  document.documentElement.style.setProperty('--lw', LABEL_W + 'px');

  const DAY = 86400000;
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December'];
  const toUTC = s => new Date(s + 'T00:00:00Z');
  const isoOf = d => d.toISOString().slice(0, 10);
  const addDays = (s, n) => isoOf(new Date(toUTC(s).getTime() + n * DAY));
  const diff = (a, b) => Math.round((toUTC(a) - toUTC(b)) / DAY);
  const mondayOf = s => addDays(s, -((toUTC(s).getUTCDay() + 6) % 7));
  const fmt = s => { const d = toUTC(s); return d.getUTCDate() + ' ' + MONTHS[d.getUTCMonth()]; };
  const fmtY = s => fmt(s) + ' ' + toUTC(s).getUTCFullYear();
  function fmtRange(c) {
    if (!c.start || c.start === c.due) return fmt(c.due);
    const a = toUTC(c.start), b = toUTC(c.due);
    return a.getUTCMonth() === b.getUTCMonth()
      ? a.getUTCDate() + '–' + fmt(c.due)
      : fmt(c.start) + ' – ' + fmt(c.due);
  }
  function statusOf(c) {
    if (c.done) return ['done', '✓'];
    if (c.due && c.due < DATA.today) return ['overdue', '!'];
    if (c.start && c.start <= DATA.today && c.due >= DATA.today) return ['active', '•'];
    return ['scheduled', ''];
  }
  const CAT = {};
  DATA.categories.forEach(c => { CAT[c.name] = c.slot === 'other' ? 'var(--cat-other)' : `var(--cat-${c.slot})`; });
  const colorOf = b => CAT[b] || 'var(--cat-other)';
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  const byKey = new Map();
  DATA.sre.cards.concat(DATA.dev.cards).forEach(c => byKey.set(c.key, c));
  const doc = document.getElementById('doc');
  const sheets = [];
  // Leave a few pixels spare: font rendering differs slightly between screen
  // and print, and a page filled to the last pixel can repaginate when printed.
  const SAFETY_PX = 8;
  // Compare where the last row actually ends; scrollHeight can't be used
  // here because it never reports less than the box's own height.
  const overflows = box => {
    const last = box.lastElementChild;
    return !!last && last.offsetTop + last.offsetHeight > box.clientHeight - SAFETY_PX;
  };

  // ---------------- Sheet chrome ----------------
  function newSheet() {
    const s = el('section', 'sheet');
    const run = el('header', 'run');
    const left = el('div');
    left.append(el('b', null, DATA.board.name), document.createTextNode(' '),
                el('span', 'bn', 'সাশ্রয় বাজার'),
                document.createTextNode(' · Project schedule'));
    const right = el('div', 'mono', 'Synced ' + DATA.generatedAt);
    const pg = el('span', 'pg');
    right.append(pg);
    run.append(left, right);
    const body = el('div', 'sheet-body');
    const foot = el('footer', 'foot');
    foot.append(
      el('span', null, 'Source: Trello board “' + DATA.board.name + '” · ' + DATA.board.url.replace(/^https?:\/\//, '')),
      el('span', 'mono', 'generated by trello_gantt_chart.py --a4'));
    s.append(run, body, foot);
    doc.append(s);
    const rec = { el: s, body, pg };
    sheets.push(rec);
    return rec;
  }

  function legend() {
    const lg = el('div', 'legend');
    DATA.categories.forEach(c => {
      const it = el('span', 'it');
      const sw = el('span', 'sw'); sw.style.background = colorOf(c.name);
      it.append(sw, document.createTextNode(c.name));
      lg.append(it);
    });
    lg.append(el('span', 'sep'));
    [['✓', 'done (bar faded)', 'var(--ink)'], ['!', 'overdue', 'var(--critical)'],
     ['•', 'in progress', 'var(--brand-fill)'], ['◆', 'milestone', 'var(--ink)'],
     ['▲', 'high-risk', 'var(--critical)']].forEach(([g, label, color]) => {
      const it = el('span', 'it');
      const gl = el('span', 'gl', g); gl.style.color = color;
      it.append(gl, document.createTextNode(label));
      lg.append(it);
    });
    const t = el('span', 'it');
    t.append(el('span', 'dash'), document.createTextNode('today (' + fmt(DATA.today) + ')'));
    lg.append(t);
    return lg;
  }

  // ---------------- Date axis (shared) ----------------
  function buildAxis(axt, ws, days, ppd) {
    const we = addDays(ws, days - 1);
    const x = d => diff(d, ws) * ppd;
    let cur = ws;
    while (diff(we, cur) >= 0) {
      const d = toUTC(cur);
      const next = isoOf(new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1)));
      const end = diff(next, we) > 0 ? addDays(we, 1) : next;
      const width = diff(end, cur) * ppd;
      const full = MONTHS_LONG[d.getUTCMonth()] + ' ' + d.getUTCFullYear();
      const short = MONTHS[d.getUTCMonth()];
      const b = el('div', 'mband');
      b.dataset.full = full; b.dataset.short = short;
      b.append(el('span', null, width > 96 ? full : width > 26 ? short : ''));
      b.style.left = x(cur) + 'px'; b.style.width = width + 'px';
      axt.append(b);
      cur = end;
    }
    const daily = ppd >= 15;
    const everyOtherWeek = !daily && ppd * 7 < 48;
    let mondays = 0;
    for (let i = 0; i < days; i++) {
      const di = addDays(ws, i);
      const isMon = toUTC(di).getUTCDay() === 1;
      if (daily) {
        const n = el('div', 'dnum' + (isMon ? ' mon' : ''), String(toUTC(di).getUTCDate()));
        n.style.left = x(di) + 'px'; n.style.width = ppd + 'px';
        axt.append(n);
      } else if (isMon) {
        if (!everyOtherWeek || mondays % 2 === 0) {
          const n = el('div', 'dnum wide mon', fmt(di));
          n.style.left = x(di) + 'px';
          axt.append(n);
        }
        mondays++;
      }
    }
  }

  function gridAndToday(rowsBox, axt, ws, days, ppd, contentH) {
    const x = d => diff(d, ws) * ppd;
    const layer = el('div', 'gridlayer');
    layer.style.height = contentH + 'px';
    for (let i = 0; i < days; i++) {
      const di = addDays(ws, i);
      if (toUTC(di).getUTCDay() === 1) {
        const g = el('div', 'gline'); g.style.left = x(di) + 'px'; layer.append(g);
      }
    }
    rowsBox.prepend(layer);
    const we = addDays(ws, days - 1);
    if (DATA.today >= ws && DATA.today <= we) {
      const tx = x(DATA.today) + ppd / 2;
      const labW = parseFloat(getComputedStyle(rowsBox).getPropertyValue('--lw')) || LABEL_W;
      const t = el('div', 'today');
      t.style.left = (labW + tx) + 'px'; t.style.height = contentH + 'px';
      rowsBox.append(t);
      const f = el('div', 'today-flag', 'TODAY ' + fmt(DATA.today).toUpperCase());
      f.style.left = tx + 'px';
      axt.append(f);
      // Keep month names readable: move or shorten any label the flag would cover.
      const fl = tx - f.offsetWidth / 2 - 4, fr = tx + f.offsetWidth / 2 + 4;
      axt.querySelectorAll('.mband').forEach(b => {
        const span = b.firstChild, bl = parseFloat(b.style.left), bw = parseFloat(b.style.width);
        if (!span || bl + 4 + span.offsetWidth <= fl || bl + 4 >= fr) return;
        const fit = room => [b.dataset.full, b.dataset.short].some(t => { span.textContent = t; return span.offsetWidth <= room; });
        if (fit(fl - bl - 4)) return;
        b.style.paddingLeft = (fr - bl) + 'px';
        if (!fit(bw - (fr - bl))) span.textContent = '';
      });
    }
  }

  // ---------------- Detail timeline sheets ----------------
  function timelineSheet(title) {
    const s = newSheet();
    const head = el('div', 'sec-head');
    const range = el('span', 'range');
    const sub = el('span', 'sub');
    head.append(el('h2', null, title), range, sub);
    const tl = el('div', 'tl');
    const axis = el('div', 'axis');
    const axl = el('div', 'axis-lab');
    ['Key', 'Task', 'Dates', ''].forEach(t => axl.append(el('span', null, t)));
    const axt = el('div', 'axis-trk');
    axis.append(axl, axt);
    const rows = el('div', 'rows');
    tl.append(axis, rows);
    s.body.append(head, legend(), tl);
    return Object.assign(s, { range, sub, axt, rows });
  }

  function groupRow(name, count, cont) {
    const g = el('div', 'grp');
    g.dataset.group = name;
    const gl = el('div', 'gl');
    gl.append(el('span', null, name + (cont ? ' (continued)' : '')),
              el('span', 'gc', count + (count === 1 ? ' task' : ' tasks')));
    g.append(gl, el('div'));
    return g;
  }

  function cardRow(c) {
    const r = el('div', 'row');
    r.dataset.key = c.key;
    const lab = el('div', 'lab');
    const [sk, sg] = statusOf(c);
    lab.append(el('span', 'k', c.key), el('span', 't', c.title), el('span', 'd', fmtRange(c)), el('span', 's ' + sk, sg));
    r.append(lab, el('div', 'trk'));
    return r;
  }

  // Fill sheets group by group. A group that fits whole stays whole; one
  // that can't fit even on a fresh sheet is split row by row, with a
  // "(continued)" header on the next sheet.
  function paginate(title, groups, cards, groupOf) {
    const byGroup = new Map(groups.map(g => [g, []]));
    cards.forEach(c => { const g = groupOf(c); if (byGroup.has(g)) byGroup.get(g).push(c); });
    let s = timelineSheet(title);
    const made = [s];
    const fresh = () => { s = timelineSheet(title); made.push(s); };
    groups.forEach(g => {
      const list = byGroup.get(g);
      if (!list.length) return;
      const nodes = [groupRow(g, list.length, false)].concat(list.map(cardRow));
      nodes.forEach(n => s.rows.append(n));
      if (!overflows(s.rows)) return;
      nodes.forEach(n => n.remove());
      if (s.rows.children.length) fresh();
      nodes.forEach(n => s.rows.append(n));
      if (!overflows(s.rows)) return;
      nodes.forEach(n => n.remove());
      s.rows.append(groupRow(g, list.length, false));
      list.forEach(c => {
        const r = cardRow(c);
        s.rows.append(r);
        if (overflows(s.rows)) { r.remove(); fresh(); s.rows.append(groupRow(g, list.length, true), r); }
      });
    });
    return made;
  }

  // Monday before the sheet's first task through the day after its last.
  function naturalWindow(s) {
    const cards = [...s.rows.querySelectorAll('.row')].map(r => byKey.get(r.dataset.key));
    return [mondayOf(cards.map(c => c.start || c.due).sort()[0]),
            addDays(cards.map(c => c.due).sort().slice(-1)[0], 1)];
  }

  // Draw axis, bars and markers once a sheet's rows are final. fixedWin
  // [start, endInclusive] keeps every sheet of a panel on one scale;
  // without it the sheet zooms to the rows it holds.
  function fillTimeline(s, fixedWin) {
    const rowEls = [...s.rows.querySelectorAll('.row')];
    if (!rowEls.length) return;
    const cards = rowEls.map(r => byKey.get(r.dataset.key));
    const [ws, we] = fixedWin || naturalWindow(s);
    const days = diff(we, ws) + 1;
    const trackW = s.axt.clientWidth;
    const ppd = trackW / days;
    const x = d => diff(d, ws) * ppd;

    s.range.textContent = fmt(ws) + ' → ' + fmtY(we) + ' · ' + days + ' days shown';
    const groupNames = [...new Set([...s.rows.querySelectorAll('.grp')].map(g => g.dataset.group))];
    s.sub.textContent = groupNames.join('  /  ');
    buildAxis(s.axt, ws, days, ppd);

    rowEls.forEach((r, i) => {
      const c = cards[i];
      const trk = r.querySelector('.trk');
      if (c.milestone) {
        const cx = x(c.due) + ppd / 2;
        const m = el('div', 'ms'); m.style.left = cx + 'px';
        const lbl = el('div', 'msl', c.title.replace(/^MILESTONE:\s*/i, ''));
        trk.append(m, lbl);
        const w = lbl.offsetWidth;
        lbl.style.left = (cx + 9 + w <= trackW - 4 ? cx + 9 : Math.max(2, cx - 9 - w)) + 'px';
      } else {
        const bx = x(c.start);
        const bw = Math.max(4, (diff(c.due, c.start) + 1) * ppd - 2);
        const b = el('div', 'bar' + (c.done ? ' done' : ''));
        b.style.left = (bx + 1) + 'px'; b.style.width = bw + 'px'; b.style.background = colorOf(c.bucket);
        trk.append(b);
        if (c.highRisk) {
          const k = el('span', 'risk', '▲');
          k.style.left = (bx + bw + 4) + 'px';
          trk.append(k);
        }
      }
    });

    const tlEls = s.rows.querySelectorAll('.row, .grp');
    const last = tlEls[tlEls.length - 1];
    gridAndToday(s.rows, s.axt, ws, days, ppd, last.offsetTop + last.offsetHeight);
  }

  function backlogBlock() {
    const list = DATA.dev.cards.filter(c => c.track === 'BL');
    if (!list.length) return null;
    const b = el('div', 'bl');
    const h = el('div', 'bl-h', 'Post-v1 backlog ');
    h.append(el('span', null, '— ' + list.length + ' cards, not scheduled. Held until DEV-66 ships.'));
    const grid = el('div', 'bl-grid');
    list.forEach(c => {
      const it = el('div', 'bl-it');
      const sw = el('span', 'sw'); sw.style.background = colorOf(c.bucket);
      it.append(sw, el('span', 'k', c.key), el('span', null, c.title), el('span', 'cat', c.bucket));
      grid.append(it);
    });
    b.append(h, grid);
    return b;
  }

  // ---------------- Overview sheet ----------------
  function groupStats(cards) {
    const starts = cards.map(c => c.start || c.due).filter(Boolean).sort();
    const dues = cards.map(c => c.due).filter(Boolean).sort();
    return {
      n: cards.length,
      done: cards.filter(c => c.done).length,
      start: starts[0], end: dues[dues.length - 1],
      milestones: cards.filter(c => c.milestone && c.due),
    };
  }

  function statTile(label, value, sub) {
    const t = el('div', 'stat');
    t.append(el('div', 'l', label), el('div', 'v', value), el('div', 'x', sub));
    return t;
  }

  function overview() {
    const s = newSheet();
    const top = el('div', 'ov-top');
    const left = el('div');
    const id = el('div', 'ov-id');
    id.append(el('span', 'badge', 'SB'), el('span', 'eyebrow', 'Project ledger · খতিয়ান'));
    const h1 = el('h1');
    h1.append(document.createTextNode(DATA.board.name + ' '),
              el('span', 'bn', 'সাশ্রয় বাজার'));
    left.append(id, h1, el('p', 'lede',
      `Software Requirement Engineering coursework (${fmt(DATA.sre.start)} – ${fmtY(DATA.sre.end)}), `
      + `followed by the solo build roadmap to v1.0 (${fmt(DATA.dev.start)} – ${fmtY(DATA.dev.end)}).`));
    const meta = el('div', 'ov-meta');
    meta.append(el('div', null, 'Status as of ' + fmtY(DATA.today)),
                el('div', null, 'Synced ' + DATA.generatedAt),
                el('div', null, DATA.board.url.replace(/^https?:\/\//, '')));
    top.append(left, meta);

    const t = DATA.totals;
    const stats = el('div', 'stats');
    stats.append(statTile('Tasks', String(t.cards), `${t.sre} course · ${t.dev} build · ${t.backlog} backlog`));
    stats.append(statTile('Checked off', `${t.done}/${t.cards}`, Math.round(100 * t.done / t.cards) + '% complete'));
    if (DATA.today <= DATA.sre.end) {
      const d = diff(DATA.sre.end, DATA.today);
      stats.append(statTile('To final submission', d <= 0 ? 'Today' : d + (d === 1 ? ' day' : ' days'), 'Course sprint ends ' + fmtY(DATA.sre.end)));
    } else if (DATA.today <= DATA.dev.end) {
      stats.append(statTile('Into the build roadmap', 'Day ' + (diff(DATA.today, DATA.dev.start) + 1),
        'of ' + (diff(DATA.dev.end, DATA.dev.start) + 1) + ' · v1.0 targeted ' + fmtY(DATA.dev.end)));
    } else {
      stats.append(statTile('Build roadmap', 'Complete', 'v1.0 targeted ' + fmtY(DATA.dev.end)));
    }
    stats.append(statTile('Milestones', String(t.milestones), t.highRisk + ' tasks flagged high-risk'));

    // Summary Gantt: one bar per phase / sprint.
    const head = el('div', 'sec-head');
    head.append(el('h2', null, 'Schedule at a glance'),
                el('span', 'sub', 'Each bar spans a phase or sprint · dark fill = share of its tasks checked off · ◆ milestone · dashed line = today'));
    const tl = el('div', 'tl ov');
    tl.style.setProperty('--lw', OV_LABEL_W + 'px');
    const axis = el('div', 'axis');
    const axl = el('div', 'axis-lab ov');
    ['Phase / sprint', 'Tasks', 'Done'].forEach(x => axl.append(el('span', null, x)));
    const axt = el('div', 'axis-trk');
    axis.append(axl, axt);
    const rows = el('div', 'rows');
    tl.append(axis, rows);

    const sumRows = [];
    function band(name, sub) {
      const g = el('div', 'grp');
      const gl = el('div', 'gl');
      gl.append(el('span', null, name), el('span', 'gc', sub));
      g.append(gl, el('div'));
      rows.append(g);
    }
    function sumRow(name, cards) {
      const st = groupStats(cards);
      const r = el('div', 'row');
      const lab = el('div', 'lab ov');
      lab.append(el('span', 't', name), el('span', 'n', String(st.n)),
                 el('span', 'p', Math.round(100 * st.done / st.n) + '%'));
      const trk = el('div', 'trk');
      r.append(lab, trk);
      rows.append(r);
      sumRows.push({ trk, st });
    }
    band('Course Sprint', `${fmt(DATA.sre.start)} – ${fmtY(DATA.sre.end)}`);
    DATA.sre.groups.forEach(g => sumRow(g, DATA.sre.cards.filter(c => c.phase === g)));
    band('Build Roadmap', `${fmt(DATA.dev.start)} – ${fmtY(DATA.dev.end)}`);
    DATA.dev.groups.filter(g => !/^Backlog/.test(g)).forEach(g =>
      sumRow(g, DATA.dev.cards.filter(c => c.track === 'DEV' && c.sprint === g)));
    const blCards = DATA.dev.cards.filter(c => c.track === 'BL');
    let blTrk = null;
    if (blCards.length) {
      const r = el('div', 'row');
      const lab = el('div', 'lab ov');
      lab.append(el('span', 't', 'Post-v1 backlog'), el('span', 'n', String(blCards.length)), el('span', 'p', '–'));
      blTrk = el('div', 'trk');
      r.append(lab, blTrk);
      rows.append(r);
    }

    // Milestone list.
    const msHead = el('div', 'sec-head');
    const allMs = DATA.sre.cards.concat(DATA.dev.cards).filter(c => c.milestone && c.due)
      .sort((a, b) => a.due.localeCompare(b.due));
    msHead.append(el('h2', null, 'Milestones'), el('span', 'sub', allMs.length + ' fixed dates, in order'));
    const ml = el('div', 'mlist');
    allMs.forEach(c => {
      const it = el('div', 'mi');
      const [sk, sg] = statusOf(c);
      const st = el('span', 's ' + sk, sg);
      st.style.color = sk === 'overdue' ? 'var(--critical)' : sk === 'active' ? 'var(--brand-fill)' : 'var(--ink)';
      it.append(el('span', 'dm'), el('span', 'dt', fmt(c.due)), el('span', 'k', c.key),
                el('span', null, c.title.replace(/^MILESTONE:\s*/i, '')), st);
      ml.append(it);
    });

    s.body.append(top, stats, head, tl, msHead, ml);

    // Now that it's laid out, draw the summary bars on a whole-project scale.
    const ws = mondayOf(DATA.sre.start);
    const we = addDays(DATA.dev.end, 1);
    const days = diff(we, ws) + 1;
    const trackW = axt.clientWidth;
    const ppd = trackW / days;
    const x = d => diff(d, ws) * ppd;
    buildAxis(axt, ws, days, ppd);
    sumRows.forEach(({ trk, st }) => {
      const bar = el('div', 'sbar');
      bar.style.left = x(st.start) + 'px';
      bar.style.width = Math.max(4, (diff(st.end, st.start) + 1) * ppd) + 'px';
      const fill = el('div', 'sfill'); fill.style.width = (100 * st.done / st.n) + '%';
      bar.append(fill);
      trk.append(bar);
      st.milestones.forEach(m => {
        const d = el('div', 'ms'); d.style.left = (x(m.due) + ppd / 2) + 'px'; trk.append(d);
      });
    });
    if (blTrk) blTrk.append(el('span', 'unsched', 'Not scheduled — held until DEV-66 ships'));
    const tlEls = rows.querySelectorAll('.row, .grp');
    const last = tlEls[tlEls.length - 1];
    gridAndToday(rows, axt, ws, days, ppd, last.offsetTop + last.offsetHeight);
    if (s.body.scrollHeight > s.body.clientHeight + 0.5) console.warn('Overview sheet content is taller than the page.');
  }

  // ---------------- Build ----------------
  function build() {
    overview();

    const sreSheets = paginate('Course Sprint', DATA.sre.groups,
      DATA.sre.cards.filter(c => c.start || c.due), c => c.phase);
    const devSheets = paginate('Build Roadmap', DATA.dev.groups.filter(g => !/^Backlog/.test(g)),
      DATA.dev.cards.filter(c => c.track === 'DEV' && (c.start || c.due)), c => c.sprint);

    const blk = backlogBlock();
    if (blk) {
      const last = devSheets[devSheets.length - 1];
      last.rows.append(blk);
      if (overflows(last.rows)) {
        blk.remove();
        const s = newSheet();
        const h = el('div', 'sec-head');
        h.append(el('h2', null, 'Post-v1 Backlog'));
        s.body.append(h, blk);
      }
    }

    const sreWin = [mondayOf(DATA.sre.start), addDays(DATA.sre.end, 1)];
    sreSheets.forEach(s => fillTimeline(s, sreWin));
    // Every Build Roadmap page spans the same number of days, so a day is
    // the same width on each page. A window that would run past the end of
    // the project is slid back to finish on the project's last day instead.
    const devWins = devSheets.map(naturalWindow);
    const devDays = Math.max(...devWins.map(([a, b]) => diff(b, a) + 1));
    const devEnd = addDays(DATA.dev.end, 1);
    devSheets.forEach((s, i) => {
      let ws = devWins[i][0];
      if (diff(devEnd, ws) + 1 < devDays) ws = addDays(devEnd, -(devDays - 1));
      fillTimeline(s, [ws, addDays(ws, devDays - 1)]);
    });

    sheets.forEach((s, i) => { s.pg.textContent = `Page ${i + 1} of ${sheets.length}`; });
    document.getElementById('toolbar-info').textContent =
      `A4 landscape · ${sheets.length} pages · set margins to "Default" and keep "Background graphics" on if your browser asks`;

    const m = location.hash.match(/^#sheet-(\d+)$/);
    if (m) {
      const want = +m[1] - 1;
      document.body.classList.add('solo');
      sheets.forEach((s, i) => s.el.classList.toggle('on', i === want));
    }
    document.body.dataset.pages = String(sheets.length);
  }

  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(build);
})();
</script>
"""


def render_a4(payload):
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return _HTML.replace("%%TITLE%%", TITLE).replace("%%DATA_JSON%%", data)
