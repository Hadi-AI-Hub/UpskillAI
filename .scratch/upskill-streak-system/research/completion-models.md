# Research: how daily-learning systems define "done for today"

Research for ticket `01-completion-models-research.md`. Question: across existing daily-learning,
habit-streak, and mastery-based systems, is "completion" typically time-based, content-based,
assessment-based, or hybrid — and what does that imply for UpskillAI's schema-locking ticket (03)?

## Summary of findings by system

### Duolingo — content-based trigger (lesson finished), with an internal error-tolerance gate, decoupled from an XP goal

- **What actually extends the streak**: completing *one lesson* before local midnight. This is
  content-based completion (did you finish a discrete unit), not a quiz-style score threshold and
  not raw time-on-app.
  [Streak | Duolingo Wiki](https://duolingo.fandom.com/wiki/Streak),
  [Duolingo — Streak System Breakdown (Medium)](https://medium.com/@salamprem49/duolingo-streak-system-detailed-breakdown-design-flow-886f591c953f)

- **They used to require the full daily XP goal**, not just one lesson, to extend a streak — and
  reversed this. Duolingo's own product blog explains why: data showed learners with more
  ambitious daily-XP goals were *less* likely to sustain a streak, because "almost 40% of learners
  active two days in a row with no streak had the 'intense' daily goal." The high bar caused people
  to disengage entirely rather than risk falling short. Decoupling streak-continuation from the
  goal (one lesson is enough) produced a 3.3% lift in Day-14 retention and a >40% increase in
  learners sustaining a 7+ day streak within a year.
  [Improving the Streak — Duolingo blog](https://blog.duolingo.com/improving-the-streak)

- **Within a lesson**, Duolingo does gate on correctness via the "Hearts" system: users start with
  5 hearts, lose one per mistake, and lose access to the lesson (on mobile) at zero, needing to
  wait, practice, or pay to continue. This is a soft assessment layer *inside* a lesson, not a
  quiz-with-pass-threshold at the end — there's no "you got 6/10 questions right, lesson failed."
  Notably, the desktop version imposes no mistake limit at all, i.e. Duolingo doesn't treat error-
  tolerance as essential to what "done" means, only as monetization/pacing friction on mobile.
  [Hearts | Duolingo Wiki](https://duolingo.fandom.com/wiki/Hearts)

- **Design rationale (from Duolingo's own blog)**: early-streak days are given outsized positive
  reinforcement (a 2→3-day jump is a 50% relative increase; 200→201 is 0.5%), and later the design
  leans on loss aversion to keep long streaks alive. They explicitly built in "slack" (Streak
  Freeze) because "offering people a little slack as they pursue their goals can actually be more
  motivating than having a rigid set of rules" — a deliberate hedge against all-or-nothing
  streak collapse.
  [How Duolingo's Streak Builds Habit — Duolingo blog](https://blog.duolingo.com/how-duolingo-streak-builds-habit)

- **Known failure mode — streak gaming / performative learning**: secondary sources (UX analysis,
  and a cited *Journal of Consumer Research* finding) describe users treating streak-preservation
  as the goal itself, doing the minimum viable lesson just to not lose the number, decoupled from
  actual learning value. This is described as a signal that "the streak-maintaining action isn't
  valuable enough" — i.e. content-based completion with a low bar is easy to satisfy without
  learning happening.
  [Streak Creep — The Decision Lab](https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification)
- **Known failure mode — streak anxiety / all-or-nothing brittleness**: multiple secondary sources
  describe the all-or-nothing nature (one missed day = "failure") producing anxiety and burnout,
  cited as a driver of the Streak Freeze feature above.
  [Duolingo Streaks and the 'Loss Aversion' Trap](https://screenwiseapp.com/guides/duolingo-streaks-and-anxiety-in-kids)

### Anki — content/engagement-based, explicitly *not* pass/fail

- Anki's spaced-repetition scheduling (SM-2, and the newer FSRS algorithm) is driven entirely by a
  **self-rated 4-choice recall scale**: Again / Hard / Good / Easy. The official FAQ is explicit
  that this is not a pass/fail model: *"Anki uses 4 choices for answering review cards, not 6.
  There is only one fail choice, not 3."* There is no external correctness check, no quiz score,
  and no "pass threshold" — the learner is the sole judge of whether they knew the answer.
  [What spaced repetition algorithm does Anki use? — Anki FAQs (official)](https://faqs.ankiweb.net/what-spaced-repetition-algorithm)
- There is no daily "done" threshold baked into the algorithm itself — a day's session ends when
  the learner has reviewed all cards currently due, which is a card-queue-emptied (content-based)
  definition, not a score-based one. "Again" doesn't block progress; it just requeues the card
  sooner.
- **Implication**: the most mature, decades-old spaced-repetition tool in the space deliberately
  avoids graded assessment as its completion signal, on the theory that self-assessed recall
  difficulty is a *better* engineering signal for the algorithm's purpose (interval scheduling)
  than right/wrong scoring — and that grading would distort self-report incentives.

### Corporate microlearning / LMS quiz-gated modules — assessment-based is common, with a fairly standardized parameter (80% threshold)

- Where corporate/compliance microlearning modules use quizzes to gate completion, **80% is the
  overwhelmingly common default pass threshold** in shipped LMS tooling (Articulate/Storyline,
  SCORM packages, TalentLMS, etc.), frequently paired with a small number of allowed retries (a
  commonly cited practitioner configuration is "80% pass score, 2 retries").
  [Retry Quiz — Score Reset discussion, Articulate community](https://community.articulate.com/discussions/articulate-storyline/retry-quiz-score-reset-and-completion-status-reset-issue)
- This 80% figure is not arbitrary trivia — it traces back to **Bloom's mastery learning model**
  (Bloom, "Learning for Mastery", 1968), which is the academic origin of quiz-gated completion in
  education generally. The literature consensus is a mastery bar of 80–90% on formative
  assessment, with those scoring below it required to review correctives and **retake** the
  assessment (not simply fail forward) before advancing; the 80–90% band is explicitly justified
  as "no lower than a B, no higher than 90% unless the task is safety-critical."
  [A Practical Review of Mastery Learning — American Journal of Pharmaceutical Education](https://www.ajpe.org/article/S0002-9459(23)00738-6/fulltext),
  [Mastery Learning: Definition, Examples and Evidence — Structural Learning](https://www.structural-learning.com/post/mastery-learning)
- **Retry policy in practice is "review-then-retake," not "pass on any attempt"**: the mastery
  model's whole mechanism is that a fail redirects the learner to targeted remediation before the
  next attempt, rather than just re-rolling the same quiz. Real-world SCORM/LMS implementations
  are inconsistent about enforcing this faithfully — practitioner threads describe retry-limit
  settings frequently *not* being honored correctly by the LMS, and attempt-counting getting muddled
  between "quiz attempts" and "module attempts."
  [LMS not recognizing quiz retries limit — Articulate community](https://community.articulate.com/discussions/discuss/lms-not-recognizing-quiz-retries-limit/1056073)
- **Typical question counts**: no authoritative industry standard was found; practitioner
  convention for a short microlearning unit clusters around ~5 questions per module-end quiz, but
  this is a norm, not a documented spec, and search results explicitly note there is no universally
  agreed count.
  [Completion in Microlearnings? — Articulate community](https://community.articulate.com/discussions/discuss/completion-in-microlearnings/826830)

### Habit trackers (Quranly) — content/time-based, no assessment layer at all

- Quranly's streak/completion model is purely content- or time-based: users choose to track either
  **minutes spent reading** or **pages completed**, and the day is marked complete once that
  self-reported target is hit. There is no comprehension check of any kind.
  [Build a Daily Quran Reading Habit — Greentech Apps Foundation (Quranly's publisher)](https://gtaf.org/blog/build-a-daily-quran-reading-habit/)
- Recovery mechanics exist independent of completion definition: a weekly automatic streak restore
  and the ability to "regain" a streak for up to 3 missed days via simple make-up actions — directly
  analogous to UpskillAI's deferred "Redemption" concept.
  [Track Your Quran Streak — Greentech Apps Foundation](https://gtaf.org/blog/read-quran-daily-with-quran-streak/)
- This is the weakest-signal completion model surveyed (self-report, no verification), but it's
  also the one built for a devotional/reflective practice where comprehension-checking would be
  inappropriate to the domain — worth noting as a boundary case, not a template.

## Direct answers to the ticket's three questions

**1. Time-based, content-based, assessment-based, or hybrid?**
All four exist, mapped to different products for different reasons — there is no single dominant
pattern:
- **Duolingo (the closest comparable to a daily streak product)**: content-based (lesson finished),
  explicitly *decoupled* from a stricter time/XP-based bar after they found the stricter bar hurt
  retention. It has an internal, non-blocking-by-default correctness signal (Hearts) but that is
  not what the streak keys on.
- **Anki (the closest comparable to a learning-retention product)**: content-based (queue emptied)
  with self-rated recall as the *scheduling* signal, deliberately not pass/fail.
- **Corporate microlearning/mastery learning**: assessment-based (quiz + pass threshold), rooted in
  Bloom's mastery-learning research, when the goal is verified competency rather than habit
  formation.
- **Quranly / devotional habit trackers**: pure content/time-based self-report, no assessment.

The pattern that emerges: **products optimizing for habit formation and long-run retention
(Duolingo, Anki, Quranly) lean content-based or self-rated; products optimizing for verified
competency (corporate/compliance training) lean assessment-based.** The two goals pull in opposite
directions, and every system surveyed picked one lane rather than trying to satisfy both with a
single hard gate.

**2. Assessment-based specifics (question counts, thresholds, retries)**
- Pass threshold: **80%** is the de facto standard (Bloom's mastery-learning literature recommends
  an 80–90% band; corporate LMS tooling defaults to 80% almost universally in practice).
- Question count: no authoritative standard; ~5 questions is a common informal convention for a
  short module, not a documented spec.
- Retry policy: the theoretically correct mastery-learning retry policy is **review corrective
  material, then retake** (not infinite blind retries) — but real LMS implementations are notably
  bad at enforcing this correctly (attempt-limit bugs are a recurring practitioner complaint).

**3. Known failure modes, by approach**
- **Time-based**: trivially gameable (leave the tab open, minimal engagement); UpskillAI's own
  CONTEXT.md already treats "time spent" as a Build/Use Loop *target*, not a completion signal —
  consistent with this research.
- **Content-based (view/complete)**: gameable via minimal-effort pass-through — Duolingo's own
  streak-gaming criticism is a direct real-world instance of this ("users view extending their
  streak as more important than the underlying activity" — Journal of Consumer Research finding,
  via The Decision Lab). Low ceremony, low friction, but weak signal that learning actually
  happened.
- **Assessment-based (quiz/pass threshold)**: strongest signal of engagement, but (a) quiz fatigue
  is a real, documented effect — high-frequency assessment increases cognitive/emotional fatigue
  and can *reduce* measured retention past an optimal point, per quiz-frequency research on
  secondary students; (b) single-attempt, all-or-nothing dichotomous scoring produces **false
  negatives on partial understanding** — the partial-credit literature finds that without partial
  credit, meaningfully-informed-but-imperfect learners fail assessments they shouldn't, and this
  effect is largest for weaker students (i.e. exactly the population a learning tool should be
  most protective of, not most punitive toward).
- **Hybrid / self-rated (Anki's model)**: avoids gaming pressure from a right/wrong score, and
  avoids the false-negative problem, at the cost of relying on the learner's honesty/self-
  awareness — a plausible failure mode being self-rating drift (always clicking "Good" out of
  habit, not real recall). This wasn't found addressed directly in Anki's own docs but is a
  structural risk of any self-report system.

## Recommendation for UpskillAI (ticket 03: schema-locking)

**Adopt a hybrid model: content-based completion as the required floor, with an assessment signal
recorded as a quality/confidence dimension rather than a hard pass/fail gate on the streak itself.**

Concretely, for schema-locking purposes:

- The **completion boolean that drives the streak state machine** should be satisfied by
  Layer 1 reporting that a day's material was worked through end-to-end (mission attempted,
  material engaged) — this is the Duolingo lesson-finished pattern and the Anki queue-emptied
  pattern, both from products explicitly optimized for daily habit retention over decades of
  iteration, which is UpskillAI's stated goal (CONTEXT.md: "a daily learning-streak habit").
  A hard quiz-pass-threshold gate on the streak itself replicates the failure mode Duolingo
  measured and reversed: raising the bar to extend a streak reduced streak retention, because a
  missed threshold on a bad day breaks the *habit* signal, not just the *mastery* signal.
- **Do gate real information into the log**, but as a *recorded outcome*, not a binary
  streak-blocker: Layer 1 should still generate end-of-material questions and report a score
  (e.g. correct/total) on the daily log line. This preserves the assessment-based diagnostic value
  (is the learner actually retaining anything, is Layer 1's material calibrated correctly) without
  making the streak fragile to quiz fatigue or false negatives on partial understanding — both of
  which are documented risks of a hard pass/fail gate, and both of which are more damaging to a
  *solo, self-directed, daily* system (no instructor to intervene on a false fail) than to a
  classroom mastery-learning context where Bloom's model assumes an instructor-mediated
  review-and-retake loop.
- This mirrors Anki's core insight more than Duolingo's: correctness/recall data is valuable as a
  **scheduling and calibration signal** (what Layer 1 should reteach, review, or escalate
  tomorrow), not as a **gate** on whether today counts. Score-as-metadata also sidesteps the
  retry-policy mess that real LMS implementations struggle with (attempt-limit enforcement bugs
  were a recurring theme in the SCORM/LMS sources above) — there's no retry state machine to build
  if a low score doesn't block completion.

**Open questions this research does not resolve** (flag for ticket 03 rather than guessing):
- Whether Layer 1 should have *any* mechanism to refuse to mark a day complete (e.g., learner
  visibly disengaged) — no surveyed system gives an AI-generated-content system this discretion;
  this is closer to a novel design question than a "how do others do it" question.
- If a quiz score is recorded, whether a specific pass threshold (e.g. 80%) should be used even as
  a non-blocking signal, or whether raw score/total is sufficient without a threshold at all — the
  numbers this research turned up (question count, threshold) are informal industry convention,
  not a settled standard, and adopting 80% here would be borrowing a number designed for an
  instructor-mediated mastery-learning context, not a solo AI-generated one.
- How self-rating (Anki-style, learner says "I got this") vs. AI-graded quiz answers (Duolingo/LMS-
  style, system checks correctness) should be weighted if UpskillAI ever wants both — this research
  surveyed each in isolation; no source combines them in one product.

## Sources

- [Streak | Duolingo Wiki](https://duolingo.fandom.com/wiki/Streak)
- [Duolingo — Streak System Detailed Breakdown & Design (Medium, Sr. Duolingo Game Designer)](https://medium.com/@salamprem49/duolingo-streak-system-detailed-breakdown-design-flow-886f591c953f)
- [Improving the Streak — Duolingo official blog](https://blog.duolingo.com/improving-the-streak)
- [How Duolingo's Streak Builds Habit — Duolingo official blog](https://blog.duolingo.com/how-duolingo-streak-builds-habit)
- [Hearts | Duolingo Wiki](https://duolingo.fandom.com/wiki/Hearts)
- [Streak Creep: When Gamified Engagement Mechanics Backfire — The Decision Lab](https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification)
- [Duolingo Streaks and the 'Loss Aversion' Trap — Screenwise](https://screenwiseapp.com/guides/duolingo-streaks-and-anxiety-in-kids)
- [What spaced repetition algorithm does Anki use? — Anki FAQs (official)](https://faqs.ankiweb.net/what-spaced-repetition-algorithm)
- [A Practical Review of Mastery Learning — American Journal of Pharmaceutical Education](https://www.ajpe.org/article/S0002-9459(23)00738-6/fulltext)
- [Mastery Learning: Definition, Examples and Evidence — Structural Learning](https://www.structural-learning.com/post/mastery-learning)
- [Completion in Microlearnings? — Articulate/E-Learning Heroes community](https://community.articulate.com/discussions/discuss/completion-in-microlearnings/826830)
- [Retry Quiz — Score Reset and Completion Status Reset Issue — Articulate community](https://community.articulate.com/discussions/articulate-storyline/retry-quiz-score-reset-and-completion-status-reset-issue)
- [LMS not recognizing quiz retries limit — Articulate community](https://community.articulate.com/discussions/discuss/lms-not-recognizing-quiz-retries-limit/1056073)
- [Build a Daily Quran Reading Habit — Greentech Apps Foundation (Quranly's publisher)](https://gtaf.org/blog/build-a-daily-quran-reading-habit/)
- [Track Your Quran Streak — Greentech Apps Foundation](https://gtaf.org/blog/read-quran-daily-with-quran-streak/)
- [Beyond right or wrong: How partial credit scoring on multiple-choice questions improves student performance and assessment perceptions — British Journal of Clinical Pharmacology / PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13420885/)
- Quiz-frequency/fatigue finding cited via web search from ScienceDirect: "Impact of quiz frequency on knowledge retention among high school students in Shenyang" (https://www.sciencedirect.com/science/article/pii/S0001691826011133) — noted as secondary/aggregated finding, not independently fetched and read in full; treat the specific "medium-frequency optimum" claim as indicative rather than verified in full text.
