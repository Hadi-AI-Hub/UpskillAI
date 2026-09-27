# Notes Panel

Every lesson gets a slide-out notes drawer on its right edge, so the user can jot something without leaving the page for a separate notebook. The note stays with that lesson, and — when possible — is mirrored into a standalone local file the user (or a future session) can read without opening the lesson at all.

## Markup

Add this once per lesson, anywhere in the body (it renders its own fixed-position button and drawer, so placement doesn't matter):

```html
<div data-notes-panel data-lesson-id="0001-some-lesson"></div>
```

`data-lesson-id` must match the lesson's filename stem exactly (`0001-pyspark-groupby-fundamentals`, no extension) — it's also the notes file's stem in `./notes/`. Add the script tag near the other asset scripts:

```html
<script src="../../../assets/notes-panel.js"></script>
```

(published-Artifact copies use `assets/notes-panel.js`, same as the other asset scripts — see [LIVE-FEEDBACK-FORMAT.md](./LIVE-FEEDBACK-FORMAT.md) for the local-vs-published path rewrite.)

## Persistence

**Opened inside a published Claude Artifact** declaring the `db` capability: notes save to `db.doc("notes/<lessonId>")`, debounced as the user types — durable across reloads and republishes, no consent prompt (unlike `sample`, `db` doesn't spend the viewer's Claude usage). **Opened as a plain local file** — any browser, any AI coding tool, or Claude before the lesson is published — falls back to `localStorage` and says so in its status line: real, but stuck in that one browser, never mirrored anywhere.

Declaring `capabilities` on an Artifact is a full-set replace, not additive — a lesson using both the tutor widget and the notes panel must declare `capabilities: {sample: {}, db: {}}` together on every publish.

## Mirroring notes to a local file

The published copy (when one exists) is the one place notes are actually written server-side; `./notes/<lessonId>.html` is a read-only mirror for browsing without opening the lesson. Refresh it:
- whenever the user asks to see or sync their notes,
- and as a matter of habit at the natural end of a `/teach` session, right before `log-day` — so the mirror never drifts far from what's actually in the drawer.

To refresh from a published Artifact: `Artifact` tool, `action: "read_db"`, the lesson's published `url`, `collection: "notes"`, `doc_id: "<lessonId>"`. If the doc doesn't exist yet (`exists: false` / not found), the user hasn't written anything for this lesson — leave `./notes/<lessonId>.html` as a short placeholder rather than fabricating content. Otherwise write the `text` field into `./notes/<lessonId>.html`, wrapped in the shared stylesheet like any other reference doc — plain, readable, printable, linking back to the lesson.

**When there's no published Artifact** (any local-only lesson, any non-Claude harness), there's nothing to read back — if the user wants their `localStorage`-only notes mirrored, they paste the text to you directly in chat.
