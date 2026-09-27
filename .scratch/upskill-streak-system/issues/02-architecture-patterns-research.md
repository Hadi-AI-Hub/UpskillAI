# Research: architecture patterns for local-first, layered learning tools

Type: research
Status: resolved

## Question

Sanity-check UpskillAI's proposed 3-layer split (Layer 0: plain-code engine owning a JSONL log + state machine + dashboard; Layer 1: AI-driven teaching protocol; Layer 2: per-harness adapters) against how similar tools are actually built:

- Local-first, single-file-source-of-truth patterns for personal logging/habit-tracking tools (JSONL vs SQLite vs other formats, and why one is typically preferred for this scale of data).
- Plugin/extension architecture patterns for AI coding assistants (e.g. how Claude Code skills, or comparable tools, cleanly separate deterministic logic from AI-driven logic) — does the 3-layer split hold up, or is there a better-known shape?
- Lightweight dashboard/visualization patterns for streak and calendar-heatmap style personal data (static HTML generation approaches, when a local server beats a plain file, existing minimal calendar-heatmap implementations worth borrowing from).

Goal: either validate the 3-layer architecture and a "static HTML regenerated on write" dashboard approach, or recommend a specific revision — grounded in prior art, not guesswork, consistent with the map's scalability posture (solo-first, clean interfaces, not designing for multi-tenancy yet).

Capture findings as a markdown file under `.scratch/upskill-streak-system/research/` and link it from this ticket's Answer.

## Answer

The 3-layer split is validated as-is: it's a recognizable composite of Ports and Adapters
(Layer 0 core + CLI port, Layer 2 adapters) and the deterministic-script/AI-instruction
seam Anthropic's own Agent Skills architecture uses (matching doubly here since Layer 1
literally is a Claude Code skill). One internal refinement is recommended: inside Layer 0,
split the state machine (pure functions) from file I/O/rendering (Functional Core,
Imperative Shell), so the core logic is trivially testable. JSONL is confirmed as the
daily log format at this scale (single writer, one append/day, years-scale row counts,
multi-harness legibility) over SQLite. The dashboard approach is confirmed as static HTML
regenerated on every log write, opened locally, with one revision: inline the day/streak
data as a `<script>` literal in the generated HTML rather than `fetch()`-ing a sibling
JSON file, which avoids the standard `file://` CORS failure and needs no local server;
borrow the week-column grid layout from GitHub's contribution graph / cal-heatmap rather
than adding a JS dependency.

Full findings and sources: [../research/architecture-patterns.md](../research/architecture-patterns.md)
