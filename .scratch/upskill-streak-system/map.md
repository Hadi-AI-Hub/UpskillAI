# Map: UpskillAI Foundation

Label: wayfinder:map

## Destination

A locked, research-grounded spec for Layer 0 (JSONL schema, streak state machine, dashboard) and its integration contract with Layer 1 (`/teach`) — enough to start and sustain the 30-day Build Loop / Use Loop dogfood. Redemption mechanics, Layer 2 adapters beyond Claude Code, and the leadership presentation deck are explicitly out of scope for this map.

## Notes

- Domain vocabulary: see [CONTEXT.md](../../CONTEXT.md) — Build Loop, Use Loop, Layer 0/1/2, daily log, mission, completion, streak state, redemption, dashboard.
- Scalability posture: solo-first, clean interfaces. Build for one user now; avoid designs that would force a rewrite if this becomes a multi-user product later. Do not design for multi-tenancy today.
- Timezone: local system midnight, ISO date string (`YYYY-MM-DD`), no time component. (Locked.)
- Streak state machine transitions are locked: `active` → `grace` after 1 missed day → `broken` after 2 consecutive missed days. What's still open is schema/completion and implementation shape, not these transition rules.
- Layer 1 → Layer 0 handoff: a small CLI Layer 0 exposes (e.g. `log-day`), called from within the `/teach` session — this shape is tentative, pending the architecture research ticket.
- Every ticket here should stay small: the user's Build Loop budget is 30-60 min/day, so decisions should be scoped to fit real daily sessions, not sprawling designs.
- When resolving grilling tickets, call the grilling and domain-modeling skills — keep CONTEXT.md current as vocabulary sharpens.
- Tracker: local markdown (see `docs/agents/issue-tracker.md`). This repo is not a git repository, so research findings are saved as plain files (no throwaway branch).

## Decisions so far

- [Research: how daily-learning systems define "done for today"](issues/01-completion-models-research.md): recommend a hybrid completion model — content-based engagement (reported by Layer 1) drives the streak, with the end-of-material quiz score recorded as a diagnostic signal rather than a hard pass/fail gate. Duolingo's own data shows raising the completion bar *reduces* streak retention; hard assessment gates carry known quiz-fatigue/false-negative risk. See [research/completion-models.md](research/completion-models.md).
- [Research: architecture patterns for local-first, layered learning tools](issues/02-architecture-patterns-research.md): 3-layer split confirmed (matches Ports & Adapters + Anthropic's own Agent Skills deterministic/AI seam) — one refinement: split Layer 0's state machine (pure functions) from file I/O and rendering (Functional Core / Imperative Shell) for testability. JSONL confirmed over SQLite at this scale. Dashboard confirmed as static HTML regenerated on write, with data inlined as a `<script>` literal (not fetched) to avoid the `file://` CORS wall; heatmap borrows GitHub's contribution-graph week-column grid. See [research/architecture-patterns.md](research/architecture-patterns.md).
- [Lock the Layer 0 daily-log schema and completion model](issues/03-lock-schema-and-completion.md): completion is content-based (all of a day's chunks worked through), never exercise-gated. JSONL schema locked: `date`, `mission`, `target_minutes`, `started_at`, `completed_at`, `completed`, `exercise` (nullable; `quiz`/`recall`/`hands-on`, topic-tagged `items` or `attempted`, no pass threshold), `streak_state`. Layer 0's CLI splits into `start-day` (stamps date/started_at) and `log-day` (stamps completed_at, computes streak_state, accepts judgment fields from Layer 1). Dashboard also needs a day-over-day time-spent line chart (carried to ticket 04). See [ADR 0002](../../docs/adr/0002-content-based-completion-not-quiz-gated.md).
- [Lock Layer 0 architecture: state machine, CLI contract, and dashboard delivery](issues/04-lock-architecture-cli-dashboard.md): Python 3 (stdlib only), Functional Core/Imperative Shell split (`state_machine.py`/`store.py`/`dashboard.py`/`cli.py` under `layer0/`, invoked via `bin/upskill`). CLI: `start-day --target-minutes N` writes a transient marker; `log-day --mission "..." [--exercise '{...}']` (no `--completed` flag — calling it at all is the signal) reads the marker, appends the full JSONL line, regenerates `dashboard.html` automatically. Streak/`longest_streak` computed by full-history scan, no cached running state. This is the spec ready to hand to a build session. See [ADR 0001](../../docs/adr/0001-jsonl-over-sqlite-for-daily-log.md).

## Not yet specified

- **Claude Code daily-trigger hook**: a `SessionStart`/`UserPromptSubmit` hook that checks the log on session open and nudges if today isn't logged yet. Depends on the Layer 0 CLI existing first. Not required to start the dogfood; revisit once Layer 0 is built.
- **Google Calendar integration**: exploratory idea for scheduling/reminding the daily session. Not yet scoped.

## Out of scope

- **Redemption mechanics**: how a `broken` streak can be repaired via make-up tasks (window length, number of make-up sessions, whether the streak resumes or partially resets). Named out of scope in the Destination from the start — deliberately deferred until after Layer 0 v1 ships and a real break has been lived through; revisit as a fresh effort then.
- **Harness-agnostic teaching prompt** (Cursor / ChatGPT / Codex CLI parity for people without a Claude subscription): the dogfood runs on Claude Code only. Revisit as a fresh effort if/when the system is actually shared with others.
- **Layer 2 adapters beyond Claude Code**: same reasoning — out of scope until there's a reason to support another harness.
- **The leadership presentation deck**: needs 30 days of real dogfood data to be honest; belongs to a later effort once that data exists.

## Status: destination reached

All four tickets are resolved and no further decisions are required — [Lock Layer 0 architecture: state machine, CLI contract, and dashboard delivery](issues/04-lock-architecture-cli-dashboard.md) explicitly confirms the Layer 1 (`/teach`) integration wiring is implementation work directly derivable from the locked contract, not an open decision. The spec (schema, completion model, state machine, CLI contract, dashboard delivery) is ready to hand to a build session. Remaining fog (daily-trigger hook, calendar integration) is optional follow-on work, not required to start the dogfood.
