# Story Slicing — ordering and cutting the work

Load this when slicing a selected epic into stories, or refining a story to
Ready. It carries the slicing model (capability epics, vertical stories), the
risk toolkit (spike / walking skeleton / lane), how to write acceptance an
agent can verify, and the Ready/Done gates.

## The model — capability epics, vertical stories

**An epic is a capability someone can use; a story is the smallest usable
step toward it.** Epics are dependency-ordered in `backlog.md`, and each epic
row carries a **"Usable means"** entry — the observable surface (a UI screen,
a CLI, an endpoint) a person touches to exercise the capability. The epic is
done when that surface works end-to-end, not when its code exists.

Who is that person? Whoever operates the product. For an internal or solo
tool, the builder-operator IS the user — "no external users" never means "no
human consumer." If a human will ever click, run, or read it, there is a
consumer to slice for.

A **story is a vertical slice by default**: it crosses whatever layers it
needs (data, logic, surface) and ends demoable on the product's real surface,
phrased from the consumer's seat:

```
As <the operator/user>, I want <goal>, so that <benefit>.
e.g. "As the operator, I paste a novel URL and see the novel in my library
with its chapters" — ingest + storage + list UI, one story.
```

**Stage-shaped stories are the exception, gated by one predicate: the
consumer is code, not a person.** A library, a pipeline stage another story
calls, an internal contract — "build the segmenter" is legitimate there,
verified by tests/output instead of a demo. Name that consumer in the packet
(`Consumer: <the story/code that calls this>`). No nameable code consumer
means the consumer is a person, and the story is a vertical slice.

**Reserve a seam, never a bypass.** When a predecessor genuinely must wait,
build the story against the predecessor's **interface with a stub/fake behind
the real seam** — ideally a fake that doubles as a permanent test double. A
shortcut that routes *around* the seam is the debt a later story tears out.

## The risk toolkit — de-risk inside the plan, not by reshaping it

Risk never reorders the epic structure. It is handled by three bounded tools;
match the tool to the risk's shape:

| Tool | Answers | Shape | Ends in |
|------|---------|-------|---------|
| **Spike** | A research question that could invalidate the plan — "is X good enough?", "does Y scale?" | Time-boxed throwaway code: the cheapest experiment that yields the answer | An ADR in `docs/adr/`; the code is discarded |
| **Walking-skeleton story** | Will these seams hold? — 2+ capabilities integrating over contracts the spec has NOT pinned | ONE thin story crossing those seams end-to-end; production habits; kept | Proven contracts to widen from |
| **Lane `high-risk`** | A risky capability that must be built for real | A normal story, pulled as early as its dependencies allow | The capability, early |

- A **quality or feasibility question is a spike, never a build.** "Is the
  output good enough?" is answered by producing three real samples with a
  disposable driver and judging them — not by building the pipeline that
  would use them. A spike **jumps the queue**: run it as soon as its inputs
  exist, whatever epic is in progress.
- An **integration question gets the skeleton — one story, never an epic.**
  When epics build sequentially on real predecessors, integration is
  continuous and no skeleton is needed at all.
- An **external lead-time item** (API audit, account review, approval) is a
  scheduling fact: start it early, run it in parallel, note it in the build
  order. It is not a story and never reshapes the structure.

## INVEST — the slice quality check

| Letter | Means | Fails when |
|---|---|---|
| Independent | Buildable/shippable without waiting on a sibling | a strict prerequisite chain |
| Negotiable | Captures intent, not a frozen task list | reads like a spec dump |
| Valuable | Observable value to its consumer | no demoable outcome and no named code consumer |
| Estimable | You can assign a lane | too vague/unknown → spike first |
| Small | Ships in one go | "almost there" for a long stretch |
| Testable | Has agent-verifiable acceptance | "works well" with no check |

## Splitting patterns — when a slice is too big

| Pattern | Split by |
|---|---|
| Workflow steps | the user's path; ship the first usable step first |
| Business-rule variation | one rule now, variants later |
| Happy / error path | success now, failure handling next |
| Data variation | one data shape now, more later |
| Operations (CRUD) | one operation per story |
| Interface / platform | one surface now |
| Spike | a time-boxed research story that ends in an answer |

## Acceptance criteria — agent-verifiable, Gherkin

Write each as Given/When/Then, checkable without subjective judgment:

```
- [ ] Given <context>, When <action>, Then <observable outcome>.
```

Prefer an observable artifact (a file exists, an endpoint returns 200, a test
passes) over a quality adjective. "Reads nicely" is not acceptance. For a
vertical story, at least one criterion runs on the product's real surface
(the UI shows X, the CLI prints Y) — an increment verified only by unit tests
is not usable yet.

## Definition of Ready — gate into In Progress

- [ ] Dependencies are built, or stand behind a real seam (stub/fake, not a bypass).
- [ ] Acceptance criteria are written and agent-verifiable.
- [ ] In/Out scope is explicit.
- [ ] Research questions this story rests on are answered (spike run, decision
      recorded) — building the story is not how you find out.
- [ ] Build-vs-buy decided; durable picks recorded as ADRs in `docs/adr/`.
- [ ] It is a vertical slice — or the packet names its code consumer.

## Definition of Done — story

- [ ] All acceptance criteria pass (a test passes / an output exists / a flow completes).
- [ ] A vertical story was exercised once on the product's real surface, not
      only through tests.
- [ ] Tests per the repo's standard.
- [ ] `docs/architecture.md` updated if the structure changed.
- [ ] Durable notes promoted from the packet to `docs/adr/`.
- [ ] Status flipped to `done` in `docs/backlog.md`; packet marked Done.

## Definition of Done — epic

- [ ] All its stories are done.
- [ ] Its "Usable means" holds: a person exercises the capability end-to-end
      on the real surface.

## Lazy slicing — do not pre-cut the whole backlog

Create a story packet when the story is selected for work, or when a product
decision needs a durable home — not up front. An epic stays `unsliced` until
you pick it; a story stays a `candidate` row until you slice it. Pre-writing
every packet plans against assumptions early work will overturn.
