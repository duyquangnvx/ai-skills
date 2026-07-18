---
name: issue-log
description: Per-project issue log — one file per issue under docs/issues/, with an ambient index imported into CLAUDE.md. Set up a project, migrate an old backlog, or audit on request.
disable-model-invocation: true
---

A lightweight per-project system for work that arises mid-task and must not be lost: stray fixes, deliberate deferrals, decisions parked behind a reopen condition. The user's request carries the verb — set up, migrate a file, audit, capture, close — apply it so the project ends in the shape below.

## The shape of a set-up project

1. `docs/issues/` — one Markdown file per issue, kebab-case filename.
2. `docs/issues/index.md` — the canonical header below, then one table row per **open** issue.
3. The project's `CLAUDE.md` contains the line `@docs/issues/index.md`.

The import is the load-bearing piece: it makes the index ambient, so every open trigger sits in view of every session and can fire in the middle of unrelated work. Without it the system degrades to a file nobody re-reads.

## Canonical index header

Install verbatim at the top of `index.md`. It is the single source of the daily rules — agents in the project follow it with no skill loaded:

```markdown
# Issues

Deferred work. One issue per file in this directory; this index owns status:
open = a row below, closed = row removed (the file stays as the record).

- Capture: write `<slug>.md` beside this index, add a row to the table
  `| [title](<slug>.md) | <condition> |`. A trigger is an observable
  condition ("when services/tts lands"); use `—` for tasks waiting to be
  picked by hand.
- When a trigger below has just come true, read its file and surface it to
  the user.
- Close: remove the row, keep the file. A settled durable decision may be
  worth promoting to an ADR where the project keeps them.

| Issue | Trigger |
| --- | --- |
```

## Writing entries

- **Triggers** are the system's payoff, so hold each one to a single test: could an agent that just finished some work look at the row and *know* whether it fired? "when the TTS service lands" passes; "when needed" fails.
- **Issue files** are freeform and sized to their content — two lines for a stray fix, a full argument with sources for a rejected-twice decision. Open with why the work is deferred or worth doing; end with `_Source: <what was in flight when it arose, date>_`. Write content in the user's language, whatever the project.

## Boundaries

- One row per open issue in the index, ever — the index is paid for in every turn of every session. Detail belongs in the issue file.
- Migrate only files the user points at. A `backlog.md` found in a repo may belong to a different system (epic/story planning); never assume it is an issue log.
