# Research: how daily-learning systems define "done for today"

Type: research
Status: resolved

## Question

Survey how existing daily-learning, habit-streak, and mastery-based systems (e.g. Duolingo, Anki/spaced-repetition tools, corporate microlearning platforms, habit trackers like Quranly) define completion for a single day's session — specifically:

- Is completion typically time-based, content-based (did you view/complete the material), assessment-based (quiz/question pass threshold), or some hybrid?
- For assessment-based models: typical question counts per session, pass thresholds, retry policies (same-day retry allowed? does a fail block the day or give partial credit?).
- Any known failure modes of each approach (e.g. gaming a time-based streak, quiz fatigue, false negatives on partial understanding).

This directly informs the leading candidate for UpskillAI's completion model: Layer 1 generates end-of-material quiz questions, and a pass threshold on correct answers determines "done for the day." The goal is a recommended completion model (with rationale) that the schema-locking ticket can be built around — not to lock exact numbers, but to ground the decision in how similar systems actually do this instead of guessing.

Capture findings as a markdown file under `.scratch/upskill-streak-system/research/` and link it from this ticket's Answer.

## Answer

Across the systems surveyed, habit-retention products (Duolingo, Anki, Quranly) lean content-based
or self-rated completion, while verified-competency products (corporate/compliance microlearning,
rooted in Bloom's mastery learning) lean assessment-based with an ~80% pass threshold — the two
goals pull in opposite directions, and Duolingo's own data shows raising the completion bar (full
daily goal vs. one lesson) *reduced* streak retention. Recommendation: ticket 03 should schema-lock
a **hybrid model** — content-based completion (material engaged end-to-end) as the boolean that
drives the streak state machine, with Layer 1's end-of-material quiz score recorded on the daily
log line as a *diagnostic/calibration signal*, not a hard pass/fail gate on the streak itself. This
avoids both Duolingo's measured streak-fragility failure mode and the quiz-fatigue/false-negative
failure modes documented for hard assessment gates, which matter more in a solo, instructor-less
daily system than in a classroom mastery-learning context. Full findings, sources, and open
questions (whether a pass threshold like 80% is even meaningful as non-blocking metadata; whether
Layer 1 should ever have discretion to refuse completion) are in
[`research/completion-models.md`](../research/completion-models.md).
