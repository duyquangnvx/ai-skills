---
paths:
  - "docs/backlog.md"
  - "docs/stories/**"
---
# Backlog & story rules

You're here because you're editing the backlog or a story packet — slicing an
epic, refining a story to Ready, or closing one out.

## The model

- An **epic** is a capability someone can use, done when its "Usable means"
  surface works end-to-end — not when its code exists.
- A **story** is a vertical slice by default: it crosses whatever layers it
  needs (data, logic, surface) and ends demoable on the product's real
  surface. Exception — a stage-shaped story is legitimate only when its
  consumer is code, not a person; name that consumer in the packet.
- **Size a story to one agent session**: build it and run its acceptance to
  pass/fail within a single session, before context degrades. Too big →
  split (by workflow step, rule variation, happy/error path, data variation,
  operation, or surface). Two small stories beat one long "almost there."
- **Reserve a seam, never a bypass**: a not-ready dependency is a stub/fake
  behind the real interface, never a shortcut around it.
- **Lazy slicing**: epics stay `unsliced` until selected; a story packet is
  created only when its story is selected for work. Never pre-cut the backlog.

## Risk toolkit — never reshape the epic structure

| Tool | Use for | Ends in |
|------|---------|---------|
| Spike | A research question that could invalidate the plan; jumps the queue as soon as its inputs exist | An ADR in docs/adr/; code discarded |
| Walking-skeleton story | Unpinned integration contracts — ONE thin story, never an epic | Proven seams to widen from |
| Lane `high-risk` | A risky capability that must be built for real | The capability, early |

A quality or feasibility question is a spike, never a build.

Lane values are exactly `tiny / normal / high-risk / spike` — a walking
skeleton is a story *shape*, not a lane (give it a normal/high-risk lane).

**Status lives in two places with one owner each.** The packet's frontmatter
owns the live status (`draft → ready → in progress → done`); the backlog row
carries only `candidate → sliced → done`, flipped on story events (packet
created; story closed). Never track ready/in-progress in the backlog table —
concurrent sessions editing one table is how status races start.

## Definition of Ready — gate into In Progress

- [ ] Dependencies built, or stubbed behind a real seam (never a bypass).
- [ ] Acceptance written as Given/When/Then, agent-verifiable; for a vertical
      story at least one criterion runs on the product's real surface.
- [ ] In/Out scope explicit.
- [ ] Research questions answered first (spike run, decision recorded) —
      building the story is not how you find out.
- [ ] Build-vs-buy decided; durable picks recorded as ADRs in docs/adr/.
- [ ] Vertical slice — or the packet names its code consumer.

## Definition of Done

- [ ] Story: acceptance passes; a vertical story exercised once on the real
      surface, not only through tests; tests per repo standard;
      architecture.md updated if structure changed; durable notes promoted
      to docs/adr/; backlog row flipped to `done`; packet status `done`;
      progress.md regenerated.
- [ ] Epic: all its stories done AND its "Usable means" holds end-to-end.
