# Lock the Layer 0 daily-log schema and completion model

Type: grilling
Status: resolved

Blocked by: 01

## Question

Given the findings from "Research: how daily-learning systems define 'done for today'" (ticket 01), lock:

- The exact JSONL schema for a daily log line (field names, types, required vs optional).
- How the completion signal is derived and stored (quiz-based, time-based, hybrid, or whatever the research recommends) — including whatever minimal mechanics that requires (e.g. pass threshold, question count) without over-specifying what can't be known before real dogfood data exists.
- What Layer 1 is responsible for computing/passing vs what Layer 0 derives itself, consistent with Layer 0 staying a plain-code engine with no AI dependency.

## Answer

**Completion model**: content-based, not quiz-gated. `/teach` breaks a day's material into chunks; clicking through all of them = the session reached its defined endpoint = `completed: true`. This drives the streak. Layer 1 has no discretion to refuse completion once the session reaches its endpoint (no judgment-based veto in v1). A quiz/exercise score is captured separately as non-blocking diagnostic metadata for Layer 1 to read back and adjust future material — never a gate.

**Daily log line (JSONL)**:
```json
{
  "date": "2026-09-11",
  "mission": "Intro to attention mechanisms",
  "target_minutes": 30,
  "started_at": "2026-09-11T08:02:11-07:00",
  "completed_at": "2026-09-11T08:34:50-07:00",
  "completed": true,
  "exercise": {
    "type": "quiz",
    "items": [
      { "topic": "scaled dot-product attention", "correct": true },
      { "topic": "multi-head attention", "correct": false }
    ]
  },
  "streak_state": "active"
}
```
- `exercise` is `null` on days with no exercise (nullable — not every day's material fits one).
- `exercise.type` is `"quiz"`, `"recall"` (Anki-style flashcards), or `"hands-on"`.
- `exercise.items: [{topic, correct}]` is present for `quiz`/`recall` — topic-tagged, not just an aggregate score, so Layer 1 can see *what* was missed, not just *how much*. No pass/fail threshold is stored (the 80% industry convention is borrowed from an instructor-mediated context with no evidence it transfers here — raw numbers only).
- `exercise.attempted: true/false` replaces `items` for `hands-on` (forcing a fake correct/total on a build exercise would be meaningless).
- `actual_minutes` is not a stored field — always derived from `completed_at - started_at`, including by the dashboard's day-over-day time-spent line chart (carried forward to ticket 04, alongside streak count / longest streak / calendar heatmap).
- `chunks_total`/`chunks_completed` are deliberately *not* persisted — chunk progress stays internal to the Layer 1 session; only the final outcome is logged. Revisit only if 30 days of dogfooding shows a real need.

**Layer 0 / Layer 1 responsibility split**: Layer 0's CLI exposes two calls — `start-day` (Layer 0 stamps `date` and `started_at` itself from the system clock) and `log-day` (Layer 0 stamps `completed_at` itself at call time and computes `streak_state` itself from log history; accepts `mission`, `target_minutes`, `completed`, and `exercise` as arguments from Layer 1). Layer 0 never trusts Layer 1 for anything it can verify itself (time, streak state) — only content-judgment fields arrive as external data. Exact CLI argument/flag names are ticket 04's job; this locks the shape of the split.
