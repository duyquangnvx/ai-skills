---
paths:
  - "docs/backlog.md"
  - "docs/stories/**"
  - "docs/progress.md"
---
# Parallel sessions — lanes, claiming, merging

You're here because this project runs several agent sessions at once and
you're touching the coordination surface: the backlog, a story packet, or the
progress rollup.

## The lane model

- The unit of parallel work is the **epic**: one session owns one claimed
  epic and works its stories one at a time. Two sessions never share an epic.
- One session = one isolated checkout (git worktree or clone). Never two
  sessions in one working tree.
- Spikes and other read-only work (research, audits) are always safe to run
  in parallel, alongside any lane.
- **Hotspot files** — shared surfaces every lane touches — are edited
  serially: never touch one while another lane has an unmerged edit to it,
  and keep the diff minimal. This project's hotspots:
  - <config / route table / registry / schema files — from the interview>

## Claiming an epic

- Claims live in `docs/progress.md` (the Assignee column). Claim **before
  fan-out**, on the main checkout, then start the session in its own
  worktree — the single main checkout is what serializes claims.
- A session picking up work itself: commit *only* the claim row and push
  immediately; a rejected push means someone claimed first — pull and pick
  another epic. No remote → only the operator assigns; never self-claim.
- An epic is claimable when its `Depends on` epics are done and it is
  unassigned. Respect an existing assignee even if the lane looks stale —
  flag it, don't take it.

## Before fanning out — all three must hold

1. **The spine is real**: the epics every lane builds on are merged and run
   end-to-end on main.
2. **Cross-lane contracts are pinned in code** — shared types, interfaces,
   schemas, contract tests. If two lanes meet at a seam, the seam compiles
   before either lane starts. Prose is not a contract.
3. **Shared conventions are recorded** (CLAUDE.md conventions, ADRs): naming,
   error shape, data model.

A lane executes decisions; it does not make cross-lane ones. A cross-lane
decision surfacing mid-story stops the lane: surface it to the operator,
record the outcome as an ADR, then continue.

## Merging back — the only time shared docs change

- Mid-story, write only inside your lane: your epic's code and your story
  packet. ADRs are date-named, so recording one from a worktree is safe.
- Merge lanes one at a time. At merge, on main: rebase onto latest main,
  re-run the story's acceptance after the rebase, pass the repo's checks —
  then flip the backlog row, promote packet notes to ADRs, update
  architecture.md if structure changed, regenerate `docs/progress.md`.

## Width

Open 2–3 lanes before widening; the ceiling is how much merged work gets
reviewed, not how many sessions can run.
