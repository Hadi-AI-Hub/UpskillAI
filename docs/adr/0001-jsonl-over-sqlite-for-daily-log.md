# JSONL, not SQLite, for the daily log

Layer 0's daily log is a JSONL file (`layer0/data/log.jsonl`), append-only, one line per day. SQLite was the obvious alternative for a "local-first source of truth" and was deliberately rejected: at this system's actual scale (one append/day, single writer, ~3,650 lines over 10 years) SQLite's advantages — transactional multi-writer integrity, indexed queries — solve problems this workload doesn't have, while JSONL keeps the log trivially readable/appendable from any future Layer 2 harness adapter's language of choice (no SQLite driver/binding required), diffable, and hand-repairable if corrupted. Revisit only if the access pattern changes materially: concurrent writers, large-scale queries, or multi-user.

## Considered options

- **SQLite**: rejected — its own documentation frames it as competing with ad hoc binary formats, not line-delimited text logs; its strengths target a workload UpskillAI doesn't have.
- **JSONL** (chosen): matches JSON Lines' stated use case (logs, streaming, inter-process messages) and the map's stated goal of cross-harness legibility.

See `.scratch/upskill-streak-system/research/architecture-patterns.md` §1 for the full analysis and sources.
