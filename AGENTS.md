## Agent skills

`/teach` (`.agents/skills/teach/`) is the only skill this repo ships. It is Layer 1:
it runs a day's lesson and reports the outcome to Layer 0 through `bin/upskill`.
Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), then
rewritten to be mission-generic.

The skill lives in `.agents/skills/`, which Cursor and GitHub Copilot read directly;
`.claude/skills/teach` is a symlink into it for Claude Code. Cloning the repo is the
install — there is no per-harness setup step.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

`.scratch/upskill-streak-system/` holds the original design effort (map, research,
resolved tickets) that the ADRs cite. It is a historical record, not live process.
