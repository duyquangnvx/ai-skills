# Story Slicing — cutting epics into vertical-slice user stories

Load this when slicing a selected epic into stories, or refining a story to
Ready. It holds the craft the backlog/story templates assume: how to cut a slice
that is vertical, how to write acceptance an agent can verify, and the
Ready/Done gates.

## The one test that matters

A user story is a **vertical slice**: it delivers something observable
end-to-end — a demo that runs, an output that exists, a flow that completes —
narrow in feature scope but routed through the real architectural seams.

It is **not** a technical stage, a layer, or a task. The reliable tell of a bad
slice is an actor that is the system or a tier, not a person:

```
WRONG (horizontal — a pipeline stage, nothing demoable):
  As the system, I want to fetch the page HTML, so that it can be processed.
  As the system, I want to store the extracted article.

RIGHT (vertical — one thin path a user can observe):
  As a reader, I want to save a URL and see its extracted text in the reader,
  so that I can read it later.   (touches save → fetch → extract → store → render,
                                  each seam real but thin: one happy path, one site)
```

If you catch yourself writing one story per stage (fetch / extract / store), you
are slicing horizontally. Collapse them into one thin vertical story, then split
*that* by the patterns below when it is too big.

## INVEST — the slice quality check

| Letter | Means | Fails when |
|---|---|---|
| **I**ndependent | Can be built/shipped without waiting on a sibling | Ordered chain where each needs the previous tier |
| **N**egotiable | Captures intent, not a frozen task list | Reads like a spec dump |
| **V**aluable | Observable value to a user or the running product | "As the system…"; no demoable outcome |
| **E**stimable | You can assign a lane (tiny/normal/high-risk) | Too vague or too unknown → needs a `spike` first |
| **S**mall | Ships in one go | "Almost there" for a long stretch → split it |
| **T**estable | Has acceptance an agent can verify alone | "works well", "is fast" with no observable check |

## Splitting patterns — when a story is too big

Split *along* the value, never *across* the layers. Pick the first pattern that
fits:

| Pattern | Split by | Example |
|---|---|---|
| Workflow steps | The user's path; ship the spine step first | Save+read first; tag/search later stories |
| Business-rule variation | One rule now, variants later | Extract standard articles now; paywalled/PDF later |
| Happy / error path | Success now, failure handling next | Save a good URL; failed-fetch retry as its own story |
| Data variation | One data shape now, more later | English articles now; RTL/CJK typography later |
| Operations (CRUD) | One operation per story | Create+read now; delete/edit later |
| Interface / platform | One surface now | API + minimal UI now; mobile polish later |
| Spike | A time-boxed research story that ends in an **answer**, not an artifact | "Decide extraction lib" → records the pick in decisions.md |

A `spike` is the right move for a `high-risk` lane: resolve the unknown, record
the decision, then the real story becomes `normal`.

## The spine slice (walking skeleton) — build first

Before widening any epic, build one thin slice that crosses the dependency chain
end-to-end with fakes/stubs — proving the architecture's seams connect. It may
span several epics. Its acceptance is "the spine runs end-to-end; an output
exists", not feature completeness. Everything after it thickens a seam that
already works.

The discipline that separates a walking skeleton from throwaway scaffolding:
every seam the spine runs through is built **real** even at one-feature depth —
only feature *breadth* is stubbed. A stub behind a real seam is scope; a bypass
*around* a seam is the debt a later story tears out.

## Acceptance criteria — agent-verifiable, Gherkin

Write each as Given/When/Then, checkable without subjective judgment:

```
- [ ] Given a saved URL with a readable article,
      When extraction runs,
      Then the reader view shows the title and body with no nav/ads.
```

Prefer an observable artifact (a file exists, an endpoint returns 200, a flow
completes) over a quality adjective. "Reads nicely" is not acceptance; "renders
title + body, no boilerplate nodes in output" is.

## Definition of Ready — gate into In Progress

A story may start only when:

- [ ] It is a vertical slice (INVEST-checked), not a task or a layer.
- [ ] Acceptance criteria are written and agent-verifiable.
- [ ] In/Out scope is explicit.
- [ ] Dependencies are done, or stand behind a real seam (stub, not bypass).
- [ ] High-risk unknowns are spiked (lane `high-risk` resolved, or a `spike`
      story created).
- [ ] Build-vs-buy and real-vs-stub are decided; durable picks recorded in
      `docs/decisions.md`.

## Definition of Done — story

- [ ] All acceptance criteria pass (demo runs / output exists / flow completes).
- [ ] Tests per the repo's standard.
- [ ] `docs/architecture.md` updated if the structure changed.
- [ ] Durable notes promoted from the packet to `docs/decisions.md`.
- [ ] Status flipped to `done` in `docs/backlog.md`; packet marked Done.

## Lazy slicing — do not pre-cut the whole backlog

Create a story packet when the story is selected for work, or when a product
decision needs a durable home — not up front. An epic stays `unsliced` until you
pick it; a story stays a `candidate` row until you slice it. Pre-writing every
packet plans against assumptions that shipping the spine will overturn.
