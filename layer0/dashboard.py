"""Renders dashboard.html: the Trainer Card. A mascot whose mood is derived
from streak state, stat tiles, a calendar heatmap, and a day-over-day
time-spent chart. Data is inlined as a <script> literal (not fetched) so the
file opens directly from disk without hitting the `file://` CORS wall.
"""
from __future__ import annotations

import html
import json
from datetime import date, datetime, timedelta
from typing import Any, Literal

from layer0.state_machine import (
    StreakState,
    completed_dates_from_entries,
    compute_longest_streak,
    compute_streak_state,
    current_streak_length,
)

HEATMAP_WEEKS = 12
CHART_DAYS = 14
MASCOT_DIR = "assets/mascot"

Mood = Literal["thriving", "neutral", "worried", "battered"]


def mood_for(streak_state: StreakState, today_logged: bool) -> Mood:
    if today_logged:
        return "thriving"
    if streak_state == "active":
        return "neutral"
    if streak_state == "grace":
        return "worried"
    return "battered"


def _minutes(entry: dict[str, Any]) -> float | None:
    started, completed = entry.get("started_at"), entry.get("completed_at")
    if not started or not completed:
        return None
    delta = datetime.fromisoformat(completed) - datetime.fromisoformat(started)
    return max(delta.total_seconds() / 60, 0)


def _fmt_duration(minutes: float) -> str:
    whole = int(round(minutes))
    hours, mins = divmod(whole, 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def render_dashboard(entries: list[dict[str, Any]], today: date) -> str:
    completed_dates = completed_dates_from_entries(entries)
    streak_state = compute_streak_state(completed_dates, today)
    streak_count = current_streak_length(completed_dates, today)
    longest_streak = compute_longest_streak(completed_dates)

    today_entry = next((e for e in entries if e["date"] == today.isoformat()), None)
    today_logged = today_entry is not None
    today_minutes = _minutes(today_entry) if today_entry else None
    total_minutes = sum(m for m in (_minutes(e) for e in entries) if m is not None)
    mood = mood_for(streak_state, today_logged)

    voice = _voice_lines(mood, streak_count, longest_streak, today_minutes)
    chip = _chip(mood, today_minutes)

    return f"""<title>UpskillAI Trainer Card</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@600;700&family=Karla:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Press+Start+2P&display=swap">
<style>{_CSS}</style>

<div class="app">
  <header class="topbar">
    <div class="brand"><span class="eyebrow">UPSKILLAI</span><h1>Trainer Card</h1></div>
    <div class="streak-chip" title="Current streak">
      <svg class="flame" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2c1 4-3 5-3 9a3 3 0 0 0 6 0c0-1-.5-2-.5-2s2.5 1.5 2.5 5a5 5 0 0 1-10 0c0-3 2-5 2-5s-.5 3 1.5 3c1.5 0 1.5-2 1.5-2s2 1 2 3.5C14 9 12 6 12 2z"/></svg>
      <span class="n num">{streak_count}</span>
      <span class="state-word">{streak_state}</span>
    </div>
  </header>

  <section class="buddy-card">
    <div class="screen mood-{mood}" id="buddyScreen" title="Click me">
      <div class="tick-bl"></div><div class="tick-br"></div>
      <picture class="buddy-pic">
        <source id="buddyImgWebp" type="image/webp" srcset="{MASCOT_DIR}/{mood}.webp">
        <img id="buddyImg" src="{MASCOT_DIR}/{mood}.png" alt="Buddy, {mood}" width="226" height="226" draggable="false">
      </picture>
      <div class="buddy-placeholder" id="buddyPlaceholder" hidden>
        <span class="ph-word">{_MOOD_WORD[mood]}</span>
        <span class="ph-hint">drop art in {MASCOT_DIR}/</span>
      </div>
    </div>
    <div class="buddy-meta">
      <h2><span id="buddyName" class="name-editable" title="Click to rename">Sparky</span></h2>
      <p class="stage">Day {len(entries)} &middot; longest streak {longest_streak}</p>
      <p class="voice-line" id="voiceLine">{html.escape(voice[0])}</p>
      <div class="hp-row"><span class="pixel hp-tag">HEALTH</span><span class="hp-word" id="hpWord">{_MOOD_WORD[mood]}</span></div>
      <div class="hp-track"><div class="hp-fill" id="hpFill" style="width:{_MOOD_PCT[mood]}%"></div></div>
      <div class="today-chip" id="todayChip"><span class="dot"></span><span id="chipText">{html.escape(chip)}</span></div>
    </div>
  </section>

  <section class="stat-row">
    <div class="stat-tile"><span class="v num">{streak_count}</span><span class="l">Current streak</span></div>
    <div class="stat-tile"><span class="v num">{longest_streak}</span><span class="l">Longest streak</span></div>
    <div class="stat-tile"><span class="v num">{len(entries)}</span><span class="l">Days trained</span></div>
    <div class="stat-tile"><span class="v num">{_fmt_duration(total_minutes)}</span><span class="l">Total time</span></div>
  </section>

  <section class="log-grid">
    <div class="log-card">
      <h3>Calendar</h3>
      {_render_heatmap(completed_dates, today)}
      <div class="heatmap-legend"><span class="sw sw-off"></span> missed <span class="sw sw-on"></span> logged <span class="sw sw-today"></span> today</div>
    </div>
    <div class="log-card">
      <h3>Time spent</h3>
      {_render_time_bars(entries)}
    </div>
  </section>
</div>

<script>
const upskillData = {json.dumps(entries, indent=2)};
const upskillMeta = {json.dumps({"mood": mood, "todayLogged": today_logged,
                                 "completedAt": today_entry.get("completed_at") if today_entry else None,
                                 "voice": voice, "mascotDir": MASCOT_DIR})};
{_JS}
</script>
"""


_MOOD_WORD = {"thriving": "Thriving", "neutral": "Ready", "worried": "Worried", "battered": "Knocked out"}
_MOOD_PCT = {"thriving": 100, "neutral": 80, "worried": 45, "battered": 0}


def _chip(mood: Mood, today_minutes: float | None) -> str:
    if mood == "thriving":
        return f"Today logged · {_fmt_duration(today_minutes or 0)}"
    if mood == "neutral":
        return "Not logged yet today — let's train"
    if mood == "worried":
        return "Missed yesterday — log today to keep the streak"
    return "Streak broken — log today to start a new one"


def _voice_lines(mood: Mood, streak: int, longest: int, today_minutes: float | None) -> list[str]:
    if mood == "thriving":
        lines = [f"Day {streak} in the books. Full charge!"]
        if streak and streak >= longest:
            lines.append(f"{streak}-day streak — the most consistent we have ever been.")
        if today_minutes:
            lines.append(f"{_fmt_duration(today_minutes)} today. Same time tomorrow?")
        return lines
    if mood == "neutral":
        return ["Streak is safe until midnight. What are we learning today?",
                "I am warmed up whenever you are."]
    if mood == "worried":
        return ["One day missed. Today still saves the streak.",
                "A little shaky, not lost. Come back today."]
    return ["Two days without training. Nothing learned was undone, though.",
            "Log today and I am back on my feet."]


def _render_heatmap(completed_dates: set[date], today: date) -> str:
    days_back = HEATMAP_WEEKS * 7 - 1
    start = today - timedelta(days=days_back)
    start -= timedelta(days=start.weekday())  # align to Monday

    cell, gap, pad = 12, 3, 1
    stride = cell + gap
    weeks = (today - start).days // 7 + 1
    width = weeks * stride - gap + 2 * pad
    height = 7 * stride - gap + 2 * pad

    rects = []
    day = start
    week = 0
    while day <= today:
        weekday = day.weekday()
        cls = "cell filled" if day in completed_dates else "cell"
        if day == today:
            cls += " today"
        rects.append(
            f'<rect class="{cls}" x="{pad + week * stride}" y="{pad + weekday * stride}" width="{cell}" height="{cell}" rx="2">'
            f"<title>{day.isoformat()}</title></rect>"
        )
        if weekday == 6:
            week += 1
        day += timedelta(days=1)

    return (
        f'<svg class="heatmap" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(rects)}</svg>'
    )


def _render_time_bars(entries: list[dict[str, Any]]) -> str:
    points = [(e["date"], m, e.get("target_minutes")) for e in entries if (m := _minutes(e)) is not None]
    points = points[-CHART_DAYS:]
    if not points:
        return '<p class="empty">No sessions logged yet.</p>'

    max_minutes = max(max(m for _, m, _ in points), max((t or 0) for _, _, t in points), 1)
    targets = [t for _, _, t in points if t]
    target_html = ""
    if targets:
        target = targets[-1]
        target_html = (
            f'<div class="target-line" style="bottom:{target / max_minutes * 100:.1f}%">'
            f"<span>target {target}m</span></div>"
        )

    cols = "".join(
        f'<div class="bar-col"><span class="bar-val">{m:.0f}</span>'
        f'<div class="bar-shape" style="height:{m / max_minutes * 100:.1f}%"></div>'
        f'<span class="bar-date">{iso[5:]}</span></div>'
        for iso, m, _ in points
    )
    return f'<div class="bars">{target_html}{cols}</div>'


_CSS = """
  :root{
    --paper:#e9e4d3; --paper-deep:#ded4b8; --card:#f7f3e6; --card-2:#fdfbf3; --line:#c9bfa0;
    --ink:#241f15; --ink-dim:#6b6250; --ember:#d1480f; --ember-2:#b23d0c; --spark:#e0a000;
    --hp-good:#3f8f5f; --hp-good-bg:#dcead9; --hp-warn:#b8860b; --hp-warn-bg:#f4e6c6; --hp-bad:#a13a3a; --hp-bad-bg:#f2dcdc;
    --font-display:'Zilla Slab', ui-serif, Georgia, serif;
    --font-body:'Karla', ui-sans-serif, system-ui, sans-serif;
    --font-mono:'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    --font-pixel:'Press Start 2P', monospace;
  }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --paper:#17150f; --paper-deep:#1f1b12; --card:#201c14; --card-2:#262217; --line:#3a3323;
      --ink:#ece6d4; --ink-dim:#a89f8a; --ember:#ff7a2e; --ember-2:#e8590c; --spark:#ffcc33;
      --hp-good:#59c98a; --hp-good-bg:#17301f; --hp-warn:#e0a83c; --hp-warn-bg:#3a2f14; --hp-bad:#e0615f; --hp-bad-bg:#3a1f1f;
    }
  }
  :root[data-theme="dark"]{
    --paper:#17150f; --paper-deep:#1f1b12; --card:#201c14; --card-2:#262217; --line:#3a3323;
    --ink:#ece6d4; --ink-dim:#a89f8a; --ember:#ff7a2e; --ember-2:#e8590c; --spark:#ffcc33;
    --hp-good:#59c98a; --hp-good-bg:#17301f; --hp-warn:#e0a83c; --hp-warn-bg:#3a2f14; --hp-bad:#e0615f; --hp-bad-bg:#3a1f1f;
  }
  *{ box-sizing:border-box; }
  [hidden]{ display:none !important; }
  html,body{ margin:0; }
  body{ background:var(--paper); color:var(--ink); font-family:var(--font-body); -webkit-font-smoothing:antialiased; }
  .pixel{ font-family:var(--font-pixel); font-size:0.52rem; letter-spacing:0.03em; }
  .eyebrow{ font-family:var(--font-pixel); font-size:0.5rem; color:var(--ember); letter-spacing:0.04em; }
  h1,h2,h3{ font-family:var(--font-display); font-weight:700; margin:0; }
  .num{ font-family:var(--font-mono); font-variant-numeric:tabular-nums; }
  .app{ max-width:1080px; margin:0 auto; padding:0 1.5rem 1.5rem; display:flex; flex-direction:column; gap:0.8rem; }
  .topbar{ display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:0.85rem 0 0.4rem; }
  .brand{ display:flex; align-items:baseline; gap:0.55rem; }
  .brand h1{ font-size:1.15rem; }
  .streak-chip{ display:flex; align-items:center; gap:0.4rem; }
  .streak-chip .flame{ width:19px; height:19px; fill:var(--ember); }
  .streak-chip .n{ font-family:var(--font-display); font-weight:700; font-size:1.15rem; }
  .streak-chip .state-word{ font-family:var(--font-mono); font-size:0.66rem; color:var(--ink-dim); text-transform:uppercase; letter-spacing:0.05em; }

  .buddy-card{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1rem 1.4rem; display:flex; align-items:center; gap:1.5rem; }
  .screen{
    position:relative; background:radial-gradient(circle at 45% 35%, var(--card-2), var(--paper-deep));
    border-radius:10px; border:1px solid var(--line); width:250px; height:250px; flex:none;
    display:flex; align-items:flex-end; justify-content:center; cursor:pointer; overflow:hidden;
    transition:background 0.4s ease;
  }
  .screen::before, .screen::after, .screen .tick-br, .screen .tick-bl{ content:""; position:absolute; width:9px; height:9px; z-index:2; opacity:0.5; }
  .screen::before{ top:5px; left:5px; border-top:2px solid var(--ember); border-left:2px solid var(--ember); }
  .screen::after{ top:5px; right:5px; border-top:2px solid var(--ember); border-right:2px solid var(--ember); }
  .screen .tick-bl{ bottom:5px; left:5px; border-bottom:2px solid var(--ember); border-left:2px solid var(--ember); }
  .screen .tick-br{ bottom:5px; right:5px; border-bottom:2px solid var(--ember); border-right:2px solid var(--ember); }
  .buddy-pic{ display:block; width:226px; height:226px; margin-bottom:12px; position:relative; z-index:1; }
  #buddyImg{
    display:block; width:226px; height:226px; object-fit:contain; object-position:center bottom;
    transform-origin:50% 100%; user-select:none; -webkit-user-drag:none;
    filter:drop-shadow(0 6px 6px rgba(36,31,21,0.22));
  }
  .buddy-placeholder{
    position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0.4rem;
    text-align:center; padding:1rem;
  }
  .buddy-placeholder .ph-word{ font-family:var(--font-pixel); font-size:0.7rem; color:var(--mood-color, var(--ink-dim)); }
  .buddy-placeholder .ph-hint{ font-family:var(--font-mono); font-size:0.62rem; color:var(--ink-dim); opacity:0.75; }
  .screen.is-scene .buddy-pic{ width:250px; height:250px; margin:0; }
  .screen.is-scene #buddyImg{ width:250px; height:250px; object-fit:cover; filter:none; border-radius:9px; }
  #buddyImg[data-anim="breathe"]{ animation:breathe 3.2s ease-in-out infinite; }
  #buddyImg[data-anim="bounce"]{ animation:bounce 0.9s cubic-bezier(.3,.9,.4,1) infinite; }
  #buddyImg[data-anim="tremble"]{ animation:tremble 1.6s ease-in-out infinite; }
  #buddyImg[data-anim="none"]{ animation:none; filter:none; }
  #buddyImg.pop{ animation:pop 0.42s cubic-bezier(.34,1.56,.64,1) 1, var(--idle, none); }
  #buddyImg.pop[data-anim="breathe"]{ --idle: breathe 3.2s ease-in-out 0.42s infinite; }
  #buddyImg.pop[data-anim="bounce"]{ --idle: bounce 0.9s cubic-bezier(.3,.9,.4,1) 0.42s infinite; }
  #buddyImg.pop[data-anim="tremble"]{ --idle: tremble 1.6s ease-in-out 0.42s infinite; }
  @keyframes breathe{ 0%,100%{ transform:scale(1,1); } 50%{ transform:scale(1.015,1.035); } }
  @keyframes bounce{ 0%,100%{ transform:translateY(0) scale(1.02,0.98); } 40%,60%{ transform:translateY(-14px) scale(0.98,1.03); } }
  @keyframes tremble{ 0%,100%{ transform:rotate(0deg); } 25%{ transform:rotate(-1.6deg); } 75%{ transform:rotate(1.6deg); } }
  @keyframes pop{ 0%{ transform:scale(0.86,1.1); } 55%{ transform:scale(1.08,0.94); } 100%{ transform:scale(1,1); } }
  .screen.mood-celebrating{ background:radial-gradient(circle at 50% 40%, #fff6c4, var(--paper-deep)); }
  .screen.mood-worried{ background:radial-gradient(circle at 45% 35%, var(--card-2), var(--hp-warn-bg)); }
  .screen.mood-battered{ background:radial-gradient(circle at 45% 35%, #eee9df, #d9d2c2); }
  @media (prefers-reduced-motion: reduce){ #buddyImg{ animation:none !important; } }

  .buddy-meta{ flex:1; min-width:0; display:flex; flex-direction:column; gap:0.42rem; }
  .buddy-meta h2{ font-size:1.3rem; }
  .name-editable{ cursor:pointer; border-bottom:1px dashed var(--line); display:inline-block; }
  .name-editable:hover{ border-bottom-color:var(--ember); }
  #nameInput{ font-family:var(--font-display); font-weight:700; font-size:1.3rem; width:9ch; background:var(--card-2); border:1px solid var(--ember); border-radius:4px; color:var(--ink); padding:0 0.2rem; }
  .buddy-meta .stage{ font-size:0.76rem; color:var(--ink-dim); margin:-0.3rem 0 0; }
  .voice-line{ font-style:italic; font-size:0.78rem; color:var(--ink-dim); min-height:2.1em; line-height:1.4; display:flex; align-items:center; margin:0; }
  .hp-row{ display:flex; align-items:center; gap:0.5rem; }
  .hp-tag{ color:var(--mood-color, var(--hp-good)); }
  .hp-word{ font-family:var(--font-mono); font-size:0.7rem; color:var(--mood-color, var(--hp-good)); text-transform:uppercase; letter-spacing:0.05em; margin-left:auto; }
  .hp-track{ height:8px; border-radius:999px; background:var(--paper-deep); border:1px solid var(--line); overflow:hidden; }
  .hp-fill{ height:100%; background:var(--mood-color, var(--hp-good)); transition:width 0.4s ease, background 0.3s ease; }
  .today-chip{
    display:flex; align-items:center; gap:0.5rem; font-size:0.8rem; color:var(--ink);
    background:var(--mood-bg, var(--hp-good-bg)); border:1px solid var(--mood-color, var(--hp-good)); border-radius:999px;
    padding:0.35rem 0.8rem; width:fit-content;
  }
  .today-chip .dot{ width:6px; height:6px; border-radius:50%; background:var(--mood-color, var(--hp-good)); flex:none; }
  .buddy-card.mood-neutral{ --mood-color:var(--ink-dim); --mood-bg:var(--card-2); }
  .buddy-card.mood-worried{ --mood-color:var(--hp-warn); --mood-bg:var(--hp-warn-bg); }
  .buddy-card.mood-battered{ --mood-color:var(--hp-bad); --mood-bg:var(--hp-bad-bg); }

  .stat-row{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.7rem; }
  .stat-tile{ display:flex; flex-direction:column; align-items:center; justify-content:center; padding:0.9rem 0; background:var(--card); border:1px solid var(--line); border-radius:12px; }
  .stat-tile .v{ font-family:var(--font-display); font-weight:700; font-size:1.35rem; }
  .stat-tile .l{ font-size:0.62rem; color:var(--ink-dim); text-transform:uppercase; letter-spacing:0.05em; margin-top:0.15rem; }

  .log-grid{ display:grid; grid-template-columns:1.1fr 0.9fr; gap:1rem; }
  .log-card{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1rem 1.3rem; display:flex; flex-direction:column; min-height:260px; }
  .log-card h3{ font-size:0.95rem; }
  .heatmap{ display:block; width:100%; max-width:440px; height:auto; margin:0.8rem 0; }
  .heatmap .cell{ fill:var(--line); opacity:0.55; }
  .heatmap .cell.filled, .heatmap .cell.today{ opacity:1; }
  .heatmap .cell.filled{ fill:var(--ember); }
  .heatmap .cell.today{ stroke:var(--spark); stroke-width:1.5; }
  .heatmap-legend{ display:flex; align-items:center; gap:0.4rem; font-size:0.72rem; color:var(--ink-dim); margin-top:auto; }
  .heatmap-legend .sw{ width:10px; height:10px; border-radius:2px; }
  .sw-off{ background:var(--paper-deep); } .sw-on{ background:var(--ember); } .sw-today{ background:var(--paper-deep); outline:1.5px solid var(--spark); }
  .empty{ font-size:0.8rem; color:var(--ink-dim); }
  .bars{ height:200px; display:flex; align-items:flex-end; gap:0.8rem; position:relative; padding-top:1.6rem; margin-top:0.4rem; }
  .target-line{ position:absolute; left:0; right:0; border-top:1.5px dashed var(--ink-dim); opacity:0.6; }
  .target-line span{ position:absolute; right:0; top:-1.15rem; font-family:var(--font-mono); font-size:0.66rem; color:var(--ink-dim); }
  .bar-col{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; min-width:0; }
  .bar-val{ font-family:var(--font-mono); font-size:0.72rem; color:var(--ink); margin-bottom:0.3rem; }
  .bar-shape{ width:58%; background:linear-gradient(180deg, var(--spark), var(--ember-2)); border-radius:4px 4px 0 0; }
  .bar-date{ font-family:var(--font-mono); font-size:0.66rem; color:var(--ink-dim); margin-top:0.4rem; }
  @media (max-width:760px){
    .stat-row{ grid-template-columns:repeat(2,1fr); }
    .log-grid{ grid-template-columns:1fr; }
    .buddy-card{ flex-direction:column; align-items:stretch; }
    .screen{ margin:0 auto; }
  }
"""

_JS = """
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var screenEl = document.getElementById('buddyScreen');
  var cardEl = screenEl.parentNode;
  var imgEl = document.getElementById('buddyImg');
  var srcEl = document.getElementById('buddyImgWebp');
  var phEl = document.getElementById('buddyPlaceholder');
  var voiceEl = document.getElementById('voiceLine');

  // No art ships with the repo, so a missing file is the default state, not an error.
  // The image can fail before this script runs, so check the already-failed case too.
  var picEl = imgEl.parentNode;
  function markMissing() { picEl.hidden = true; phEl.hidden = false; }
  function markPresent() { picEl.hidden = false; phEl.hidden = true; }
  imgEl.addEventListener('error', markMissing);
  imgEl.addEventListener('load', markPresent);
  if (imgEl.complete && imgEl.naturalWidth === 0) markMissing();
  var ANIM = { celebrating: 'bounce', thriving: 'breathe', neutral: 'breathe', worried: 'tremble', battered: 'none' };
  var SCENE = { celebrating: true, battered: true };
  var voice = upskillMeta.voice, voiceIndex = 0;

  function pop() {
    if (reduceMotion) return;
    imgEl.classList.remove('pop');
    void imgEl.offsetWidth;
    imgEl.classList.add('pop');
  }
  function show(mood) {
    Object.keys(ANIM).forEach(function (k) { screenEl.classList.remove('mood-' + k); });
    screenEl.classList.add('mood-' + mood);
    screenEl.classList.toggle('is-scene', !!SCENE[mood]);
    imgEl.dataset.anim = reduceMotion ? 'none' : ANIM[mood];
    srcEl.srcset = upskillMeta.mascotDir + '/' + mood + '.webp';
    imgEl.src = upskillMeta.mascotDir + '/' + mood + '.png';
    phEl.querySelector('.ph-word').textContent = mood;
    pop();
  }
  cardEl.classList.add('mood-' + upskillMeta.mood);
  imgEl.dataset.anim = reduceMotion ? 'none' : ANIM[upskillMeta.mood];

  // Celebrate once per log write: the dashboard is regenerated right after
  // log-day runs, so the first open after that is the moment to cheer.
  var celebrated = false;
  if (upskillMeta.todayLogged && upskillMeta.completedAt) {
    try { celebrated = localStorage.getItem('upskill_celebrated') === upskillMeta.completedAt; } catch (e) {}
    if (!celebrated) {
      var pre = new Image(); pre.src = upskillMeta.mascotDir + '/celebrating.png';
      show('celebrating');
      try { localStorage.setItem('upskill_celebrated', upskillMeta.completedAt); } catch (e) {}
      setTimeout(function () { show(upskillMeta.mood); }, 3200);
    }
  }

  screenEl.addEventListener('click', function () {
    if (voice.length > 1) { voiceIndex = (voiceIndex + 1) % voice.length; voiceEl.textContent = voice[voiceIndex]; }
    pop();
  });

  var nameEl = document.getElementById('buddyName');
  function attachNameHandler(el) {
    el.addEventListener('click', function () {
      var current = el.textContent;
      var input = document.createElement('input');
      input.id = 'nameInput'; input.value = current; input.maxLength = 14;
      el.replaceWith(input); input.focus(); input.select();
      function commit() {
        var val = (input.value || '').trim() || current;
        var span = document.createElement('span');
        span.id = 'buddyName'; span.className = 'name-editable'; span.title = 'Click to rename'; span.textContent = val;
        input.replaceWith(span);
        try { localStorage.setItem('upskill_buddy_name', val); } catch (e) {}
        attachNameHandler(span);
      }
      input.addEventListener('blur', commit);
      input.addEventListener('keydown', function (e) { if (e.key === 'Enter') input.blur(); });
    });
  }
  attachNameHandler(nameEl);
  try { var saved = localStorage.getItem('upskill_buddy_name'); if (saved) nameEl.textContent = saved; } catch (e) {}
})();
"""
