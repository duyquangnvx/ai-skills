---
paths:
  - "docs/adr/**"
---
# Writing an ADR

You're here because you're adding or editing an ADR in `docs/adr/` — this repo's
decision log (numbered `NNNN-<slug>.md`, one file per decision).

## A choice earns an ADR only if all three hold
1. **Hard to reverse** — changing your mind later costs something real.
2. **Surprising without context** — a future reader will wonder "why this way?"
3. **A real trade-off** — genuine alternatives existed; you picked one for reasons.

Easy to reverse, unsurprising, or no real alternative → no ADR. One exception: a
*stopgap* ("X until Y") earns an ADR with an `Expires`, to stop a later session
building the deferred thing early.

## Append-only — supersede, never overwrite or delete
A wrong ADR is never edited into a different decision and never deleted. Write a
**new** ADR and mark the old one `superseded by ADR-NNNN` (status frontmatter, or
a one-line note at its top). Git keeps the history; the marker keeps the trail
readable.

## Keep it to the decision — not the notes
An ADR is Decision / Why / Tradeoff. Reference detail — selector/probe tables,
enumerated rejected-alternatives, long derivations — bloats the ADR and
duplicates what code, fixtures, or the spec already own. Put it where it is owned
(the code/fixtures, or a sibling `NNNN-<slug>-notes.md`) behind a one-line
pointer. A spike's output is a decision, not its probe log. No nameable
`Tradeoff` → not an ADR.

Fields: `status` frontmatter (omit while simple), an H1 title, then `Decision` /
`Why` / `Tradeoff`; add `Expires` for a stopgap and `Supersedes: ADR-NNNN` when it
replaces one. Match the existing ADRs; a trivial one can be a sentence or two.
