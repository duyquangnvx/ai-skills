# Story Slicing — ordering and cutting the work

Load this when slicing a selected epic into stories, or refining a story to
Ready. It carries two ordering models, how to cut a story under each, how to
write acceptance an agent can verify, and the Ready/Done gates.

## Pick the ordering model first

One predicate decides it: **is early external feedback a goal?** (shipping an
MVP, validating with users/stakeholders, requirements still uncertain). Present
this call to the user as a recommendation with its reasoning and confirm before
slicing — it shapes the whole backlog; recommend the default unless the spec or
context signals MVP or user validation.

- **No → dependency order (default).** The common case for this skill: a solo
  tool, or a build from a settled spec. Shipping is not the driver, so a thin
  demoable slice buys little; dependency order avoids stub-debt and dependency
  inversions.
- **Yes → vertical slices (variant).** Early feedback outweighs the friction of
  stubs and re-traversal.

The universal gates (acceptance, Ready, Done, lazy slicing) apply to both.

## Default model — dependency order, risk front-loaded

Order stories so each is built on **real, finished predecessors**. Within what
the dependency graph allows, do the **hardest / most-uncertain core first** — if
that core is wrong, everything built on the plan is wasted. The spec's own
dependency DAG is usually the backbone; the lane (`high-risk`/`spike`) tells you
what to pull early.

A story here is a **capability built real and independently verifiable** — a test
passes, an output exists. It does **not** have to be demoable end-to-end to a
user, and a **stage-shaped story is fine** (in a pipeline, "build the segmenter"
is a legitimate story when it is built real and verifiable). This is the opposite
of the variant below — do not force a thin vertical path here.

**Reserve a seam, never a bypass.** When a predecessor genuinely must wait, build
the story against the predecessor's **interface with a stub/fake behind the real
seam** — ideally a fake that doubles as a permanent test double. A shortcut that
routes *around* the seam is the debt a later story tears out. This keeps "build on
real predecessors" honest when one isn't ready yet.

**Integration smoke (optional).** If many components are built independently and
the spec has NOT fixed the contracts between them, run one thin end-to-end path
early as a one-time integration check. When the spec pins those contracts, that
risk is pre-paid — skip it; it is not the organizing principle here.

Anti-patterns this order prevents:

- **Deferring the hard core** — saving the riskiest capability for late.
- **Bypassing a seam** — routing around an unbuilt dependency instead of stubbing
  behind its real interface.
- **A story you cannot verify** — a half-built capability with no test/output.
  Even a stage-story must pass acceptance on its own.

## Variant model — vertical slices (only when early feedback is the goal)

Here a story is a **vertical slice**: demoable end-to-end, narrow in feature
scope but routed through the real seams — not a lone stage or layer. The actor is
a person, never the system:

```
WRONG (a pipeline stage, nothing demoable):
  As the system, I want to fetch the page HTML, so that it can be processed.
RIGHT (one thin path a user observes):
  As a reader, I want to save a URL and read its extracted text in the reader.
```

Build a **spine slice first** — one thin path crossing the dependency chain
end-to-end (a walking skeleton), every seam real at one-feature depth, breadth
stubbed — then widen. A stub behind a real seam is scope; a bypass around it is
debt.

### INVEST — the slice quality check (variant)

| Letter | Means | Fails when |
|---|---|---|
| Independent | Buildable/shippable without waiting on a sibling | a strict prerequisite chain |
| Negotiable | Captures intent, not a frozen task list | reads like a spec dump |
| Valuable | Observable value to a user | "As the system…"; no demoable outcome |
| Estimable | You can assign a lane | too vague/unknown → spike first |
| Small | Ships in one go | "almost there" for a long stretch |
| Testable | Has agent-verifiable acceptance | "works well" with no check |

### Splitting patterns (variant) — when a slice is too big

| Pattern | Split by |
|---|---|
| Workflow steps | the user's path; ship the spine step first |
| Business-rule variation | one rule now, variants later |
| Happy / error path | success now, failure handling next |
| Data variation | one data shape now, more later |
| Operations (CRUD) | one operation per story |
| Interface / platform | one surface now |
| Spike | a time-boxed research story that ends in an answer |

## Acceptance criteria — agent-verifiable, Gherkin (both models)

Write each as Given/When/Then, checkable without subjective judgment:

```
- [ ] Given <context>, When <action>, Then <observable outcome>.
```

Prefer an observable artifact (a file exists, an endpoint returns 200, a test
passes) over a quality adjective. "Reads nicely" is not acceptance.

## Definition of Ready — gate into In Progress (both models)

- [ ] Dependencies are built, or stand behind a real seam (stub/fake, not a bypass).
- [ ] Acceptance criteria are written and agent-verifiable.
- [ ] In/Out scope is explicit.
- [ ] High-risk unknowns are spiked (lane `high-risk` resolved, or a `spike` story created).
- [ ] Build-vs-buy decided; durable picks recorded in `docs/decisions.md`.
- [ ] (variant) It is a vertical slice, not a lone stage/layer.

## Definition of Done — story (both models)

- [ ] All acceptance criteria pass (a test passes / an output exists / a flow completes).
- [ ] Tests per the repo's standard.
- [ ] `docs/architecture.md` updated if the structure changed.
- [ ] Durable notes promoted from the packet to `docs/decisions.md`.
- [ ] Status flipped to `done` in `docs/backlog.md`; packet marked Done.

## Lazy slicing — do not pre-cut the whole backlog (both models)

Create a story packet when the story is selected for work, or when a product
decision needs a durable home — not up front. An epic stays `unsliced` until you
pick it; a story stays a `candidate` row until you slice it. Pre-writing every
packet plans against assumptions early work will overturn.
