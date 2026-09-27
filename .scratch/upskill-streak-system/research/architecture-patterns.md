# Research: Architecture Patterns for UpskillAI Layer 0/1/2

Status: complete
Ticket: [../issues/02-architecture-patterns-research.md](../issues/02-architecture-patterns-research.md)

## Question

Sanity-check the proposed 3-layer split (Layer 0: plain-code engine with a JSONL daily
log + streak state machine + dashboard; Layer 1: AI-driven teaching protocol; Layer 2:
per-harness adapters) against prior art in three areas:

1. Local-first, single-file-source-of-truth formats for personal logging tools (JSONL vs
   SQLite vs alternatives).
2. Plugin/extension architectures for AI coding assistants — how they separate
   deterministic logic from AI-driven logic.
3. Lightweight dashboard/visualization patterns for streak + calendar-heatmap data.

---

## 1. JSONL vs SQLite for a single-user daily log

### What the primary sources say

SQLite's own documentation is unambiguous that it generally wants to replace ad hoc
flat-file formats, not the other way around:

> "SQLite does not compete with client/server databases. SQLite competes with fopen()."
> "Many programs use fopen(), fread(), and fwrite() to create and manage files of data in
> home-grown formats. SQLite works particularly well as a replacement for these ad hoc
> data files... SQLite can be faster than the filesystem for reading and writing content
> to disk." — [sqlite.org, "Appropriate Uses For SQLite" / "When To Use SQLite"](https://www.sqlite.org/whentouse.html)

And on device-local, single-writer scenarios specifically: "For device-local storage
with low writer concurrency and less than a terabyte of content, SQLite is almost always
a better solution [than a client/server DB or hand-rolled file format]."

Taken at face value this reads as an argument *for* SQLite over JSONL. But the SQLite
page is arguing SQLite vs. a *binary or ad hoc* file format (its own worked examples are
things like custom binary formats, or many small files on disk) — not vs. a
line-delimited, human- and tool-readable text format used as an interchange/log format.
JSON Lines occupies a different niche than "home-grown fopen() format":

> "JSON Lines is a text format... each line is a valid JSON value... UTF-8 encoded, one
> JSON value per line, line separator is '\n'." Its stated use cases are "log files,"
> "streaming," and "flexible format for passing messages between cooperating processes."
> — [jsonlines.org](https://jsonlines.org/)

That description — log files, streaming, inter-process messages — is close to an exact
match for UpskillAI's daily log: one append per day, written by Layer 0's CLI, read by
both Layer 0 (dashboard render, state machine) and potentially Layer 1/2 (agents/scripts
across different harnesses, possibly in different languages).

### Applying this to UpskillAI's actual scale and access pattern

The map's own numbers matter here: one line per day, single user, years of data. Even at
10 years that's ~3,650 lines — kilobytes of text, not a dataset SQLite's performance
guidance is aimed at. The deciding factors are therefore not throughput or query
complexity but:

- **Write pattern**: exactly one append per day, from one process. SQLite's main
  advantages (atomic multi-statement transactions, concurrent-writer safety, complex
  queries, indexing) are solving problems this workload doesn't have.
- **Read pattern**: whole-file scans to rebuild streak state and render a dashboard —
  something `jq`/a few lines of any language's JSON parser does trivially over a file
  this small, no query planner needed.
- **Cross-process, cross-harness legibility**: Layer 1 is explicitly meant to run inside
  multiple future harnesses (Claude Code today, Cursor/ChatGPT/Codex CLI later per
  CONTEXT.md), and Layer 2 adapters are thin per-harness glue. A line-delimited text file
  is trivially readable/appendable from any language or shell without a driver/binding;
  a SQLite file requires a SQLite library be available and correctly linked in every
  harness environment that wants to touch it directly.
- **Human/AI legibility and diffability**: JSONL is directly `cat`/`tail`/`grep`-able,
  diffs cleanly line-by-line (useful if this ever sits under version control, and useful
  for an AI agent to reason about via a text read rather than a query), and is trivial to
  hand-edit or repair. A SQLite file is an opaque binary blob to all of that.
- **Corruption risk is low and bounded**: with one append per day via a single writer
  (Layer 0's CLI), POSIX append semantics make a single `write()` of one line
  effectively atomic in practice; the worst case (a torn last line from a mid-write crash)
  is easy to detect and repair by hand, unlike partial corruption of a binary DB file.
  SQLite's crash-safety guarantees are solving for a harder problem (multi-writer,
  multi-statement transactions) than this workload has.

### Verdict

JSONL is the right choice at this scale and for this access pattern — not because SQLite
is a bad tool, but because SQLite's advantages (transactional multi-writer integrity,
indexed query performance over larger datasets) are unneeded here, while JSONL's
advantages (zero-dependency read/write from any harness/language, human legibility,
diff-friendliness, trivial repair) directly serve the stated constraints: single user,
one write/day, and a system that must stay legible and portable across several future AI
harnesses. This should be revisited only if the log's access pattern changes materially
(e.g., concurrent writers, need for indexed queries over large history, or multi-user).

---

## 2. Plugin/extension architecture: does the 3-layer split hold up?

### Claude's own Agent Skills architecture

Anthropic's official docs describe Skills as filesystem-based packages with three kinds
of content, each loaded at a different time and for a different purpose:

> "Instructions: Additional markdown files... containing specialized guidance and
> workflows. Code: Executable scripts (fill_form.py, validate.py) that Claude runs using
> bash, providing deterministic operations without loading their code into context.
> Resources: Reference materials such as database schemas, API documentation, templates."
> — [Agent Skills overview, platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

The key architectural point: **scripts are deterministic and run via bash; the model
never has to "be careful" about logic that can just be code.** This is exactly
UpskillAI's Layer 0/Layer 1 boundary — Layer 0's CLI (`log-day`, state derivation,
dashboard render) is the "script," deterministic, called by bash from within the
`/teach` skill session; Layer 1 is the SKILL.md-level "instructions" content deciding
*when* and *what* to call it. This is not just an analogy: UpskillAI's Layer 1 literally
*is* a Claude Code skill (`/teach`), so its own AI-vs-deterministic seam should — and
does — mirror the seam Anthropic designed Skills around.

### The broader industry pattern this matches

Anthropic's "Building Effective Agents" engineering post frames this same seam at a
level above Skills specifically:

> "Workflows are systems where LLMs and tools are orchestrated through predefined code
> paths... In workflows control flow is predefined in code, not produced by the LLM...
> Agents [are systems where] the model dynamically directs its own processes and tool
> usage, maintaining control over how it accomplishes tasks." — [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)

Layer 0 is a workflow component (fixed control flow, no model in the loop at all —
plain code). Layer 1 is closer to the "agent" end (the model decides how to teach, what
to ask, when to call `log-day`) but is deliberately bounded: it reports outcomes to
Layer 0 through a narrow CLI rather than being given write access to the log or state
machine itself. That bounding — model-directed logic calling into a small, fixed,
code-owned interface, rather than being trusted to reimplement the deterministic parts —
is exactly the guidance Anthropic gives ("use the simplest pattern," "add complexity only
when it demonstrably improves outcomes," keep the LLM's blast radius small).

This same split has a much older name in general software architecture — **Ports and
Adapters** (a.k.a. Hexagonal Architecture), coined by Alistair Cockburn:

> "[The pattern] allows an application to equally be driven by users, programs, automated
> test or batch scripts, and to be developed and tested in isolation from its eventual
> run-time devices and databases... As events arrive from the outside world at a port, a
> technology-specific adapter converts it into a usable procedure call or message and
> passes it to the application." — [Alistair Cockburn, "Hexagonal Architecture"](https://alistair.cockburn.us/hexagonal-architecture)

Mapped onto UpskillAI: Layer 0 is the core application (the hexagon); its CLI is the
port; Layer 2's per-harness glue (Claude Code skill + hook today, Cursor/ChatGPT/Codex
CLI later) are the adapters that let different "driving" technologies reach that port.
This is a clean fit and gives Layer 2 a well-known justification for staying "thin": in
Ports and Adapters, adapters are supposed to contain translation only, no business logic
— which matches CONTEXT.md's framing of Layer 2 as "thin... glue."

The related **Functional Core, Imperative Shell** pattern reinforces the same shape at
the level of Layer 0 internally:

> "The Functional Core, Imperative Shell pattern... changes the call order: the shell
> obtains values, the Functional Core evaluates the rules, and the shell performs the
> effects. The Functional Core can then be tested without a database or test double."
> — [Kenneth Lange, "The Functional Core, Imperative Shell Pattern"](https://kennethlange.com/functional-core-imperative-shell/)

This suggests a refinement *inside* Layer 0 rather than a change to the 3-layer split:
the streak state-machine (pure: log lines in, state out) should be written and testable
as pure functions, with reading the JSONL file and writing the rendered dashboard kept as
a thin imperative shell around it. That keeps the state machine trivially unit-testable
without touching the filesystem, and keeps Layer 0 honest about "plain code, no AI
dependency" by making the core logic have no I/O dependency either.

### Verdict

The 3-layer split holds up and is not a novel or risky shape — it's a recognizable
composite of two well-established patterns applied at two different scopes:

- **Ports and Adapters** (Cockburn) at the macro scope: Layer 0 = core + port (the CLI),
  Layer 2 = adapters per harness.
- **Workflow vs. agent** (Anthropic) plus the **Skills deterministic-script vs.
  AI-instruction split** at the Layer 0/Layer 1 seam specifically — which is doubly
  validated here because Layer 1 literally *is* implemented as a Claude Code skill, so it
  should follow the same internal discipline Anthropic designed Skills around.

One refinement worth adopting, not because the layering is wrong but because it makes
Layer 0 easier to trust and test: apply **Functional Core, Imperative Shell** inside
Layer 0 itself — keep the state-machine transitions as pure functions over log data, and
push file I/O and dashboard rendering to a thin shell around them.

---

## 3. Dashboard/visualization patterns for streak + calendar-heatmap data

### Calendar heatmap prior art

GitHub's own contribution graph is the reference implementation everyone benchmarks
against, and the open-source ecosystem has converged on a small, well-known set of
minimal implementations that reproduce it:

- **[cal-heatmap](https://github.com/wa0x6e/cal-heatmap)** — the most widely used
  standalone JS library purpose-built for "a time-series calendar heatmap, like the
  GitHub contribution calendar," with plugins for zoom/legend/tooltip.
- **[calendar-heatmap (DKirwan)](https://github.com/DKirwan/calendar-heatmap)** — "a d3
  heatmap for representing time series data similar to GitHub's contribution chart,"
  itself built on Mike Bostock's original D3 Calendar View example — useful as a minimal
  reference for hand-rolling the same SVG grid without pulling in a library.
- **[calendarheatmap (nikolaydubina)](https://github.com/nikolaydubina/calendarheatmap)**
  — a small Go implementation that renders a GitHub-style heatmap as a static SVG/PNG
  with no browser/JS runtime at all — relevant precedent for "generate the visual at
  write time as a static artifact" rather than rendering it client-side.

For UpskillAI's scale (one cell per day, a handful of years at most), any of these is
overkill as a dependency; the useful thing to borrow is the *layout algorithm* (a
week-column × day-row SVG grid, one `<rect>` per day, colored by a small bucket function)
rather than the library itself. A single self-contained SVG or a small hand-rolled grid
of `<div>`s is well within "30–60 min/day" build-loop budget and avoids a JS dependency
entirely.

### Static file vs. local dev server

The concrete, primary-source reason a naive "static HTML that `fetch()`es a sibling JSON
file" approach breaks when opened directly from disk: browsers treat `file://` pages as
an opaque/null origin, and `fetch()`/XHR against another local file from that origin is
blocked by the same-origin/CORS model that assumes HTTP(S) origins. This is a
well-documented, common failure mode for exactly this kind of "just open the HTML file"
tooling (see e.g. the CORS-in-local-files writeups on
[dev.to](https://dev.to/idioms/how-to-fix-blocked-by-cors-policy-error-in-javascript-step-by-step-guide-48h6)
and [codestudy.net](https://www.codestudy.net/blog/cors-request-blocked-in-locally-opened-html-file/)).
A local dev server sidesteps this because it serves everything from a real `http://`
origin, so `fetch()` works normally — but standing up a server is unnecessary machinery
for a single-user, single-file dashboard.

The standard workaround used throughout the CLI-report tooling ecosystem (coverage
report generators, test-runner HTML reporters, notebook-to-HTML exporters, and the
`file://`-CORS writeups above all converge on this) is simpler than either "run a
server" or "deal with fetch": **inline the data directly into the HTML at generation
time**, as a `<script>const days = [...]</script>` literal or equivalent, rather than
having the page fetch a sibling file at load time. This produces a single self-contained
`.html` file with zero runtime dependencies, no server, and no CORS restriction — because
there is no cross-file request to make. It also matches CONTEXT.md's existing framing
("static HTML view, regenerated on every log write") almost exactly; it just resolves the
one open question ("delivery/rendering approach pending research") in favor of *embedding*
over *fetching*.

A local dev server would only start to earn its cost if the dashboard needed live
auto-refresh while being watched (e.g., during a long study session), cross-device access
over a LAN, or dynamic server-side computation the static render can't precompute — none
of which apply to a solo, single-machine, write-once-per-day tool per the map's
scalability posture.

### Verdict

- Borrow the calendar-heatmap *layout algorithm* (week-column grid, per-day color
  bucket) from prior art like cal-heatmap / GitHub's own graph; no need to pull in the
  library itself at this scale.
- Confirm the "static HTML regenerated on every log write" approach, with one concrete
  refinement: **inline the day/streak data into the HTML file at generation time**
  (a small `<script>` data literal Layer 0's CLI writes alongside the markup) rather than
  having the page `fetch()` a separate JSON file — this avoids the well-documented
  `file://` CORS failure mode and keeps the dashboard a true single-file, double-click-to-
  open artifact with no local server required.
- A local dev server is not warranted for the current solo/single-machine posture; revisit
  only if live-refresh-while-watching or multi-device/LAN access become real
  requirements.

---

## Overall recommendation

**Validate the 3-layer architecture as proposed**, with one internal refinement: inside
Layer 0, separate the streak state machine (pure functions over log data — Functional
Core) from file I/O and dashboard rendering (Imperative Shell), so the state machine is
trivially unit-testable and the "plain code, no AI dependency" promise extends to "no I/O
dependency either" for the core logic. This isn't a change to the layer boundaries, just
a recommended internal shape for Layer 0.

**Keep JSONL as the daily log's format.** SQLite is the right call for local-first apps
with larger, more complex, or multi-writer local data, but UpskillAI's actual profile —
one append/day, single writer, single user, years-scale row counts, and a stated need to
stay legible/portable across multiple future AI harnesses — is squarely the profile JSON
Lines was designed for (log files, streaming, inter-process messages), and it keeps the
log human-readable, diffable, and dependency-free to read/write from any future Layer 2
adapter's language of choice.

**Confirm "static HTML regenerated on every log write, opened locally," revised to
embed rather than fetch its data.** Layer 0's CLI should write the day/streak data as an
inlined `<script>` literal directly into the generated `dashboard.html` (not as a
separate JSON file loaded via `fetch()`), which sidesteps the standard `file://` CORS
failure mode, needs no local server, and keeps the dashboard a genuine single-file,
double-click artifact — consistent with the map's solo-first, not-yet-multi-tenant
posture. For the calendar heatmap itself, hand-roll a small SVG/grid using the same
week-column layout popularized by GitHub's contribution graph and libraries like
cal-heatmap, rather than adding a JS dependency for a few hundred cells of data.

## Sources

- [sqlite.org — "Appropriate Uses For SQLite" / When To Use SQLite](https://www.sqlite.org/whentouse.html)
- [jsonlines.org — JSON Lines format](https://jsonlines.org/)
- [platform.claude.com — Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [anthropic.com/engineering — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [alistair.cockburn.us — Hexagonal Architecture (Ports and Adapters)](https://alistair.cockburn.us/hexagonal-architecture)
- [Wikipedia — Hexagonal architecture (software)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [Kenneth Lange — The Functional Core, Imperative Shell Pattern](https://kennethlange.com/functional-core-imperative-shell/)
- [cal-heatmap (GitHub)](https://github.com/wa0x6e/cal-heatmap)
- [DKirwan/calendar-heatmap (GitHub)](https://github.com/DKirwan/calendar-heatmap)
- [nikolaydubina/calendarheatmap (GitHub)](https://github.com/nikolaydubina/calendarheatmap)
- [dev.to — How to Fix "Blocked by CORS Policy" Error in JavaScript](https://dev.to/idioms/how-to-fix-blocked-by-cors-policy-error-in-javascript-step-by-step-guide-48h6)
- [codestudy.net — Fix CORS Request Blocked in Locally Opened HTML File](https://www.codestudy.net/blog/cors-request-blocked-in-locally-opened-html-file/)
- Local-first framing (background context, not directly cited for a specific claim above): [Ink & Switch — Local-first software: you own your data, in spite of the cloud](https://www.inkandswitch.com/local-first-software/)
