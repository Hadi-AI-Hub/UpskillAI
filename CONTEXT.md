# UpskillAI

An AI-driven upskilling system built around a daily learning-streak habit, rather than one-off courses or certifications. Dogfooded solo for 30 days before being presented to leadership as a mindset shift in how upskilling should work.

## Language

### The two loops

**Build Loop**:
The daily practice of improving the system itself (target 30-60 min/day).
_Avoid_: Dev loop, engineering time

**Use Loop**:
The daily practice of using whatever version of the system exists that day to learn something real (target 30-60 min/day).
_Avoid_: Learning loop, study time

### Architecture

**Layer 0**:
The engine: plain code with no AI dependency. Owns the daily log as the single source of truth, implements the streak state machine, and renders the dashboard.
_Avoid_: The backend, the core

**Layer 1**:
The teaching protocol: the AI-driven side that generates a day's lesson and reports the outcome to Layer 0 via its CLI. Currently built on Matt Pocock's `/teach` skill.
_Avoid_: The AI layer, the frontend

**Layer 2**:
Harness adapters: the thin, per-tool glue that lets Layer 1 run inside a given AI coding assistant (a Claude Code skill + hook today; Cursor, ChatGPT, Codex CLI later). Out of scope for the current effort beyond Claude Code.
_Avoid_: Integrations, plugins (the system as a whole is "the plugin"; Layer 2 is what makes it work per-harness)

### Streak mechanics

**Daily log**:
The JSONL file that is the single source of truth for the system: one line per day, written by Layer 0's CLI at the end of a day's session.
_Avoid_: The log file, history

**Mission**:
The free-text field on a daily log line describing what was studied that day. Also names the workspace folder holding everything specific to that goal (`missions/<mission-slug>/`: `MISSION.md`, `NOTES.md`, `RESOURCES.md`, lessons, notes, reference docs, learning records) — see the `/teach` skill's `SKILL.md`.
_Avoid_: Topic, subject

**Completion**:
The boolean on a daily log line that drives the streak: true once a `/teach` session reaches its defined endpoint (all of the day's material chunks worked through). Content-based, not gated by exercise performance — Layer 1 has no discretion to withhold it once the session ends.
_Avoid_: Done, success (too generic outside the log's context); pass/fail (completion isn't graded)

**Exercise**:
The optional, nullable diagnostic activity attached to a day's log line (`quiz`, `recall`, or `hands-on`), scored and read back by Layer 1 to decide what to reteach. Never gates completion or the streak.
_Avoid_: Quiz (too narrow — only one of the three exercise types), assessment (implies grading/gating)

**Streak state**:
The daily log's derived position in the state machine: `active` (today or yesterday logged), `grace` (one day missed, still recoverable), or `broken` (two consecutive days missed).
_Avoid_: Status

**Redemption**:
A future, not-yet-specified mechanism for restoring a `broken` streak via make-up work within some window. Deliberately deferred — no mechanics are decided.
_Avoid_: Recovery, streak freeze

### Presentation

**Dashboard**:
The static HTML view, regenerated on every log write, showing streak count, longest streak, a calendar heatmap, and a day-over-day time-spent line chart.
_Avoid_: The UI, the report
