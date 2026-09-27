# Lock Layer 0 architecture: state machine, CLI contract, and dashboard delivery

Type: grilling
Status: resolved

Blocked by: 02, 03

## Question

Given the findings from "Research: architecture patterns for local-first, layered learning tools" (ticket 02) and the schema locked in "Lock the Layer 0 daily-log schema and completion model" (ticket 03), lock:

- The state machine implementation shape (pure functions deriving `active`/`grace`/`broken` from the log; the transition rules themselves are already fixed: grace after 1 missed day, broken after 2 consecutive).
- The Layer 1 → Layer 0 CLI contract: ticket 03 already locked the shape (`start-day` stamps `date`/`started_at`; `log-day` stamps `completed_at`, computes `streak_state`, and accepts `mission`, `target_minutes`, `completed`, `exercise` from Layer 1) — this ticket nails exact argument/flag names and invocation details.
- The dashboard rendering and delivery approach (static HTML regenerated on write, data inlined as a `<script>` literal per the architecture research), and its minimum viable content: streak count, longest streak, calendar heatmap, **and a day-over-day time-spent line chart** (derived from `started_at`/`completed_at`, per ticket 03's resolution).

This ticket's resolution is the spec the user hands to their local Claude Code session to actually build Layer 0.

## Answer

**Runtime**: Python 3, stdlib only (`json`, `pathlib`, `datetime`) — no `requirements.txt` for v1.

**File layout**:
```
layer0/
  state_machine.py   # pure functions: log entries + today → streak_state, longest_streak (Functional Core)
  store.py            # JSONL read/append, marker-file read/write/delete (Imperative Shell)
  dashboard.py         # renders dashboard.html: inlined <script> data literal, hand-rolled SVG heatmap + time-spent line chart
  cli.py               # argument parsing, wires subcommands
  data/log.jsonl        # the log
  data/.in-progress.json  # transient marker, not part of the log
bin/upskill            # #!/usr/bin/env bash → exec python3 layer0/cli.py "$@"
dashboard.html          # repo root, regenerated on every log-day
```

**CLI contract**:
- `./bin/upskill start-day --target-minutes 30` — stamps `date`/`started_at` from the system clock; writes the marker file `layer0/data/.in-progress.json` = `{date, started_at, target_minutes}`.
- `./bin/upskill log-day --mission "..." [--exercise '{"type":"quiz","items":[...]}']` — no `--completed` flag: calling `log-day` at all *is* the completion signal (matches ticket 03's "no discretion" rule). Reads the marker for `started_at`/`target_minutes` (falls back to `now`/`null` if missing or stale, then deletes it regardless); stamps `completed_at` = now; computes `streak_state` and `longest_streak` by scanning full log history (no running-state field — negligible cost at this scale); appends the full JSONL line; regenerates `dashboard.html`; prints a one-line confirmation.

**State machine rules** (evaluated as of "today," walking backward from the most recent completed date):
- Today already completed → `active`.
- Today not yet logged, yesterday completed → `active` (today isn't over yet).
- Yesterday missing, day before completed → `grace` (one day missed).
- Both yesterday and the day before missing → `broken`.
- No prior log at all → `active`.

**Architecture**: 3-layer split confirmed as-is (Ports & Adapters at the macro scope; Layer 0/1 seam mirrors Anthropic's own Agent Skills deterministic-script/AI-instruction split). Inside Layer 0, Functional Core (state_machine.py, pure) / Imperative Shell (store.py, dashboard.py, cli.py) for testability. Dashboard: static HTML, data inlined as a `<script>` literal (not fetched — avoids the `file://` CORS wall), calendar heatmap hand-rolled as an SVG week-column grid (GitHub contribution-graph style, no JS dependency), plus a day-over-day time-spent line chart derived from `started_at`/`completed_at`.

**Two ADRs recorded** from this map's decisions: [0001](../../../docs/adr/0001-jsonl-over-sqlite-for-daily-log.md) (JSONL over SQLite) and [0002](../../../docs/adr/0002-content-based-completion-not-quiz-gated.md) (content-based completion, not quiz-gated).

**Note for the build session**: wiring `/teach`'s `SKILL.md` to actually call `start-day`/`log-day` at the right moments (deciding chunk pacing, generating the `mission` text, invoking the CLI) is implementation work directly derivable from this contract — no open decision remains, so it doesn't need its own ticket. One naming note: `/teach`'s own `MISSION.md` (the persistent *why*) and this schema's per-day `mission` field (the daily *what*) are different concepts sharing a word — not a conflict requiring a rename, just worth being aware of when writing that integration.
