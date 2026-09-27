# Lesson-Complete Button

Every lesson carries an explicit "Mark this lesson complete" button — a checkable, on-page signal, same progressive-enhancement pattern as the [tutor widget](./LIVE-FEEDBACK-FORMAT.md) and [notes panel](./NOTES-PANEL-FORMAT.md).

## Markup

Add once per lesson, typically as the last thing before `<div class="lesson-nav">`:

```html
<div class="lesson-complete" data-lesson-complete data-lesson-id="0001-pyspark-groupby-fundamentals"></div>
```

Script tag alongside the other asset scripts: `<script src="../../../assets/lesson-complete.js"></script>` (published copies: `assets/lesson-complete.js`, same local-vs-published path rewrite as every other asset — see [LIVE-FEEDBACK-FORMAT.md](./LIVE-FEEDBACK-FORMAT.md)). `data-lesson-id` matches the lesson's filename stem, same convention as the notes panel.

## Persistence

**Opened inside a published Claude Artifact** with `db` granted: writes/reads `db.doc("completion/<lessonId>")` — the agent can read this back (`action: "read_db"`) to know a lesson is done without asking in chat. **Opened as a plain local file** — any browser, any AI coding tool, or Claude before the lesson is published — falls back to `localStorage`: the button still works fully, it's just a personal, per-browser reminder nothing outside the page can read.

## What flipping it means

The button does not gate anything and does not by itself call `log-day` — it only marks *this lesson* done. React to it the same way you'd react to the user telling you in chat "I finished that lesson": decide, using the usual pacing judgment (elapsed time vs. today's `--target-minutes`, how much of today's planned material remains), whether to

- generate and open the next chunk/lesson for today, or
- treat today's material as exhausted and proceed to the end-of-session steps (sync the notes mirror per [NOTES-PANEL-FORMAT.md](./NOTES-PANEL-FORMAT.md), then `log-day`).

## Checking the flag

Only possible when the lesson was published as an Artifact: `Artifact` tool, `action: "read_db"`, the lesson's published `url`, `collection: "completion"`, `doc_id: "<lessonId>"`. Not found or `completed: false` means still in progress. This is a poll, not a push — nothing notifies a session automatically when the flag flips.

**Default: check it, don't watch it.** Read the flag when the user tells you in chat they're done, or at the start of the next `/teach` run — never spin up a recurring background poll (`loop`/`CronCreate`) on your own initiative to "watch" for the click. A tight poll with no backoff will fire identically for hours against a human-paced event and burn turns for nothing.

**When there's no published Artifact to check** (any local-only lesson, any non-Claude harness) — chat confirmation is the only signal there is, and it always works regardless of which button state the page happens to be in.
