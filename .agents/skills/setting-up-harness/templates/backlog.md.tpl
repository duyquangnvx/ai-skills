# Backlog

> Provisional, not a contract — re-order as implementation reveals what you
> couldn't know up front. Epics are coarse capability containers, dependency-
> ordered; each is done when its "Usable means" holds. Stories are vertical
> slices — the work-units you build. Risk is handled by spikes, at most one
> walking-skeleton story, and the high-risk lane — never by reshaping this
> structure. Slicing model & gates: .claude/rules/project/backlog.md.

## Epics (unsliced until selected)

| Epic | Capability | Usable means | Depends on | Status |
|------|-----------|--------------|-----------|--------|
| E01 | <capability a person gets> | <surface they touch to exercise it> | — | unsliced |
| E02 | <…> | <…> | E01 | unsliced |

## Build order

<Dependency order of the capabilities. List spikes that can jump the queue as
soon as their inputs exist, and external lead-time items (audits, approvals)
to start early in parallel.>

## Story backlog (prioritized; sliced into a packet when selected)

| Story | Epic | Lane | Status | Builds (one line) |
|-------|------|------|--------|-------------------|
| US-001 | E01 | normal | ready | As <the operator>, <goal> — <slice, surface included> |
| SP-001 | E0X | spike | ready | <research question> → ADR in docs/adr/; code discarded |

## Definition of Done — v1

1. <observable product-level criterion — the floor, not stretch goals>

## How this file evolves

- Select an epic to slice → break it into stories per the slicing rule
  (.claude/rules/project/backlog.md), add candidate rows.
- Select a story → create its packet and refine to Ready: confirm deps are built
  (or stubbed behind a real seam), write acceptance, set In/Out, spike high-risk
  unknowns, decide build-vs-buy, record durable picks as ADRs in docs/adr/. The
  manifest stays the source of truth for what's used.
- A story is done → flip its Status to `done`; in one pass over docs/adr/, add
  ADRs for durable packet notes and sweep stale ones (mark newly-superseded ADRs,
  retire expired stopgaps — supersede, never delete) — appending without sweeping
  is how the log rots; update architecture.md if structure changed; then re-read this file
  before the next story — what you built usually reveals something the plan didn't
  know, so re-order if needed.
- An epic is `done` when all its stories are done.
- Scope changes mid-story → update In/Out in the packet, record the why as an
  ADR in docs/adr/.
- A story too big to finish in one agent session → split it. Two small stories
  beat one long "almost there."
