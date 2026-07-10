# <Project name>

<One line: what this project is.>

## Commands

| Task | Command |
|------|---------|
| Test | <cmd> |
| Type check | <cmd> |
| Build | <cmd> |
| Lint/format | <cmd> |

## Session protocol

1. Read `docs/progress.md` — current story and working state.
2. Working a story? Read its packet `docs/stories/US-XXX.md` (and its epic row
   in `docs/backlog.md`).
3. At session end: refresh `docs/progress.md`; accumulate off-spec notes in the
   current story packet; if a choice could be undone by mistake later, record an
   ADR in `docs/adr/`.

## Conventions

- <Only project-specific, non-inferable rules and gotchas. Leave empty if none yet.>

## Workflow (optional — omit if you use the defaults)

- <Only deviations from the default plan/implement workflow.>

## Docs

- Architecture (current state): docs/architecture.md
- Decisions (why; ADRs): docs/adr/
- Backlog (epics + stories + status): docs/backlog.md
- Stories (per-story packets): docs/stories/
- Current state: docs/progress.md

This list is the full set. Before adding a new doc, check whether an
existing file already owns the question — extend or link it instead of
creating a parallel file.
