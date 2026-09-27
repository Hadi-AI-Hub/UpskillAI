# Exercise Tutor Widget — Progressive Enhancement

Every hands-on exercise gets a three-way tutor: **hint**, **feedback on an attempt**, and an **explained full solution**. One shared codebase (`assets/tutor-feedback.js`) serves two audiences with the exact same markup:

- **Opened inside a published Claude Artifact** — `window.claude`'s `sample` capability is live. The three buttons call it in-page and stream a real, personalized answer into `.tutor-feedback`.
- **Opened as a plain local file** — any browser, any AI coding tool (Cursor, Copilot, whatever), or Claude before the lesson is published — there's no `window.claude` at all. The same three buttons instead build the exact same prompt and copy it to the clipboard, so the learner pastes it into whatever AI assistant they have open.

Never author two versions of a lesson. The feature-detection lives entirely in `tutor-feedback.js`; the HTML is identical either way.

## Why this split, and not one or the other

An in-page live AI call only exists at all inside a published Claude Artifact — no other AI coding tool exposes an equivalent for a plain HTML page to call into its chat. So a purely "live AI" design would break for every teammate not on Claude, and a purely "copy to clipboard" design would throw away real, working functionality for the user whenever they *are* on Claude. Feature detection gets both: automatic and seamless where Claude's runtime is present, fully functional (just one paste-step further) everywhere else.

## When to publish as an Artifact

If the session generating a lesson has the `Artifact` tool available (i.e., it's Claude Code), publish the same lesson file as an Artifact **in addition to** keeping the local copy in `./lessons/` — see the main `SKILL.md` for when. If the session doesn't have that tool (a different harness), just author the local file; it already works completely on its own, live-AI buttons simply never appear.

When publishing, declare `capabilities: {sample: {}, db: {}}` (the `db` piece backs the notes panel and lesson-complete button — see their format docs) and bundle `assets/style.css`, `assets/quiz.js`, `assets/tutor-feedback.js`, `assets/notes-panel.js`, `assets/lesson-complete.js` via the Artifact tool's `files`/`root`. **Rewrite asset paths for the published copy**: the local file sits in `./missions/<slug>/lessons/` and links `../../../assets/...`; the published Artifact's document sits at its own root, so the published copy must reference `assets/...` (no `../`). Don't hand-maintain two files for this — publish a rewritten copy (e.g. via a scratch `sed` pass) built from the same source, and keep the local file's `../../../assets/...` paths untouched. Open the published URL for the user, and mention the local file also exists as an offline copy.

**Also bundle and fix the reference cheat sheet, or its link 404s in the published copy.** The local lesson links `../reference/000N-*.html`; rewrite that to `reference/000N-*.html` in the published copy (same `sed` pass as the asset rewrite), and add `reference/000N-*.html` to `files`, pointing at the reference doc — it needs no internal rewriting itself (its own `../../../assets/style.css` resolves correctly at that nesting depth once bundled at `reference/...`), **except** its own back-link to the lesson: locally `../lessons/000N-*.html`, which must become `../index.html` in the bundled copy (the published lesson is served as the bare root document, not nested under `lessons/`). This is exactly the bug that shipped on lessons 1–3 before being caught and fixed — verify both directions (lesson → reference, reference → lesson) work after every publish, not just the forward link.

**Known, accepted limitation — don't try to fix this one:** links between *different* lessons or reference docs (lesson 2 → lesson 1, reference 3 → reference 2, the `../MISSION.md` link) stay broken inside a published Artifact, because each lesson is published as its own separate, thin Artifact — bundling every other lesson into each one to make sibling links resolve would defeat the point. Those links work correctly in the local file copy, which is the reason to keep maintaining that copy as the source of truth rather than treating the Artifact as canonical.

## Markup contract

```html
<div class="exercise">
<div class="label">Exercise N — short description</div>
<p class="task">The exercise prompt.</p>

<details class="reveal" data-hint>
<summary>Need a nudge? Hint</summary>
<p>Concrete enough to unstick them — name the specific method/concept to look up — but never the working code or the full solution.</p>
</details>

<details class="reveal" data-solution>
<summary>Or reveal the reference answer</summary>
<pre><code>... the correct code ...</code></pre>
<p>Optional: one line on why, or the one gotcha this exercise is testing.</p>
</details>

<div class="tutor" data-tutor>
  <textarea class="tutor-input" rows="4" placeholder="Write your attempt here… (optional for a hint, needed for feedback)"></textarea>
  <div class="tutor-actions"></div>
  <div class="tutor-feedback"></div>
</div>
</div>
```

`.tutor-actions` is populated by `tutor-feedback.js` at load time (three buttons, labeled for whichever mode is active) — leave it empty in the HTML. The script reads the task from `.task`, and the reference solution from inside `[data-solution]`, so write those once and both the hint/reveal blocks and the tutor prompts stay in sync automatically — never duplicate the solution text into a separate attribute.

The two `<details>` blocks work with zero JS and zero dependency, in every browsing context — they're the always-available fallback under the tutor widget, not a decoration.

## Writing a good hint

State what to look up or the shape of the fix concretely enough to unstick a stuck learner, without writing the solution for them — one sentence you'd say out loud before they get back to typing.

## The three tutor actions

- **Hint** — works even with an empty attempt. Names a concept/method, never working code.
- **Feedback** — needs a written attempt (both modes refuse politely if the textarea is empty). Points at the one biggest issue and ends on a nudging question; never hands back the full solution outright.
- **Explain solution** — grounded in the exercise's own `[data-solution]` content, so it can't invent a wrong answer; walks through why it's correct and what mistakes it avoids, optionally relating it to the learner's own attempt if they wrote one.
