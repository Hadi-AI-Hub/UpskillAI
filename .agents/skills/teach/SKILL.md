---
name: teach
description: Teach the user a new skill or concept, within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Workspace

Treat the current directory as a teaching workspace, shared across every mission the user is upskilling on. Each mission gets its own folder under `./missions/<mission-slug>/`, holding everything specific to that goal:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. This should be used to ground all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference materials. These are the compressed learnings from the lessons - cheat sheets, reference algorithms, syntax, yoga poses, glossaries. They are the raw units of learning. They should be beautiful documents which print out well, and are designed for quick reference.
- `RESOURCES.md`: A list of resources which can be explored to ground your teaching in contextual knowledge, or to acquire knowledge and wisdom. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records, which capture what the user has learned. These are loosely equivalent to architectural decision records in software development - they capture non-obvious lessons and key insights that may need to be revised later, or drive future sessions. These should be used to calculate the zone of proximal development. They are titled `0001-<dash-case-name>.md`, where the number increments each time. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html`: A directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching in this workspace.
- `./notes/*.html`: A read-only mirror of the user's own in-lesson notes, one file per lesson. See [NOTES-PANEL-FORMAT.md](./NOTES-PANEL-FORMAT.md).
- `NOTES.md`: A scratchpad for you to jot down user preferences, or working notes, specific to this mission.

One thing lives outside every mission folder, shared by all of them:

- `./assets/*` (repo root, **not** per-mission): Reusable **components** shared across lessons in every mission. See [Assets](#assets).

### Which mission is active

- If `./missions/` contains exactly one folder, that's the active mission — use it without asking.
- If it contains several, infer which one this session is for from what the user says (they'll usually name the topic or continue a conversation that makes it obvious). If it's genuinely unstated and ambiguous, default to whichever mission's `learning-records/` was most recently touched, and only ask the user directly if that still doesn't resolve it.
- Every path below (`MISSION.md`, `./lessons/`, `./notes/`, `./reference/`, `./learning-records/`, `NOTES.md`, `RESOURCES.md`) is relative to the active mission's folder, `./missions/<active-mission-slug>/`, unless stated otherwise.

### Starting a new mission

Distinguish two cases:

- **The mission shifted** (same underlying goal, sharpened or corrected in light of what the user has learned): edit the active mission's `MISSION.md` in place and add a learning record — see [The Mission](#the-mission). Stays in the same folder.
- **A genuinely new, unrelated goal**: create a new `./missions/<new-slug>/` folder with the full skeleton (`MISSION.md` via [MISSION-FORMAT.md](./MISSION-FORMAT.md), empty `RESOURCES.md` and `NOTES.md`, empty `lessons/`, `notes/`, `reference/`, `learning-records/` dirs) and make that the active mission going forward. Never overwrite or repurpose an existing mission's folder for a different goal — missions accumulate side by side.

## Daily Streak (Layer 0)

This workspace's daily practice is tracked by Layer 0, a separate plain-code engine at `bin/upskill` in this repo's root that owns the log and the streak — this skill only reports outcomes to it, never edits its data files directly. Run `./bin/upskill --help` for the exact flags; the completion model is locked in `docs/adr/0002-content-based-completion-not-quiz-gated.md`, and the full log schema (including the `exercise` JSON shape) in `.scratch/upskill-streak-system/issues/03-lock-schema-and-completion.md`.

- **Start of today's first `/teach` run**: ask the user's target minutes for today if not already clear (30 is the Use Loop default), then run `start-day --target-minutes <N>`.
- **Chunks stay internal.** Break today's material into chunks (typically one or more lessons), but don't persist chunk-level progress anywhere — Layer 0 only wants the final outcome.
- **Detect "done with this lesson" primarily from what the user tells you in chat.** Every lesson also carries an explicit "Mark this lesson complete" button (see [LESSON-COMPLETE-FORMAT.md](./LESSON-COMPLETE-FORMAT.md)). If the lesson was published as a Claude Artifact, you can additionally read that flag back with `action: "read_db"`. If it's a local-only lesson (no Artifact, or a non-Claude harness), the button is a personal per-browser reminder only — chat confirmation is the only signal there is, and always works regardless.
- **Once today's material is fully worked through** — the session has reached its defined endpoint, not before — run `log-day --mission "<one-line summary of today's material>"`, adding `--exercise '<json>'` only when the session actually included a quiz, recall check, or hands-on exercise.
- Calling `log-day` *is* the completion signal — there is no partial credit and no discretion to withhold it once the material is exhausted. Never call it early, more than once per day, or with fabricated exercise results.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Lessons

A lesson is the main thing you produce: the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to the active mission's `./lessons/` (i.e. `./missions/<active-mission-slug>/lessons/`) and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful**, with clean, readable typography and layout, since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

Author every lesson as a single, self-contained local HTML file first — it must work completely on its own, opened directly in any browser, with no AI vendor's runtime required. This workspace gets handed off to teammates on a mix of AI coding tools (Cursor, Copilot, others), so nothing can be Claude-required.

**If this session can publish Claude Artifacts** (the `Artifact` tool is available — i.e., this is Claude Code), also publish the exact same lesson file as an Artifact, in addition to keeping the local copy. The lesson's own JS feature-detects `window.claude` at load time and lights up richer, live functionality automatically when present, with no separate version to maintain — see [LIVE-FEEDBACK-FORMAT.md](./LIVE-FEEDBACK-FORMAT.md) for the mechanics and the local-vs-published asset path rewrite. Open the published URL for the user in that case (mentioning the local file exists too); otherwise open the local file.

Each lesson should link via HTML anchors to other lessons and reference documents.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

Every lesson also carries the notes panel — see [NOTES-PANEL-FORMAT.md](./NOTES-PANEL-FORMAT.md) — so the user can jot something without leaving the page. Sync the notes mirror at the natural end of a session, right before `log-day`.

## Assets

Lessons are built from reusable **components**, stored in `./assets/` at the repo root — shared across every mission, not duplicated per-folder — stylesheets, quiz widgets, simulators, diagram helpers, and anything else a second lesson could reuse. From a lesson at `./missions/<slug>/lessons/0001-....html`, that's `../../../assets/...`.

Reuse is the default, not the exception. Before authoring a lesson, read `./assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it; never inline code a future lesson would duplicate.

A shared stylesheet is the first component the workspace earns: every lesson across every mission links it, so the lessons look like one consistent course rather than a pile of one-offs. As the workspace grows, so should the component library.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or the `MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal - make sure to update the `MISSION.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their `learning-records`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically. For an open-ended exercise (code, a written answer, anything without one fixed right string) where a personalized nudge would beat a static reveal, use the tutor widget — see [LIVE-FEEDBACK-FORMAT.md](./LIVE-FEEDBACK-FORMAT.md). It gives live, in-page AI feedback automatically when the lesson is opened as a published Claude Artifact, and a one-click copy-to-clipboard prompt (for whatever AI assistant the user has open) everywhere else — same markup, same file, no lesson-author decision required.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents - they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later - reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Glossaries, in particular, are an essential reference. Once one is created, it should be adhered to in every lesson.

## `NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.
