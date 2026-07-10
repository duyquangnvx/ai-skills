# Story Slicing — applying the model at setup

The slicing model itself — epic/story definitions, session sizing, seams, the
risk toolkit, the Ready/Done gates, lazy slicing — is owned by
`templates/rule-backlog.md.tpl`, generated into each project as
`.claude/rules/project/backlog.md` so later sessions carry it without this
skill. Read that template first; this file is the setup-time application
guide: identifying the consumer, matching risk tools to risk shapes, judging
and splitting slices, and writing acceptance.

## Who is the consumer?

Whoever operates the product. For an internal or solo tool, the
builder-operator IS the user — "no external users" never means "no human
consumer." If a human will ever click, run, or read it, there is a consumer
to slice for, and the story is phrased from that seat:

```
As <the operator/user>, I want <goal>, so that <benefit>.
e.g. "As the operator, I paste a novel URL and see the novel in my library
with its chapters" — ingest + storage + list UI, one story.
```

A stage-shaped story ("build the segmenter") is legitimate only when the
consumer is code — a library, a pipeline stage another story calls, an
internal contract. Verify it by tests/output instead of a demo, and name the
consumer in the packet. No nameable code consumer means the consumer is a
person, and the story is a vertical slice.

## Matching the risk tool to the risk's shape

- A **quality or feasibility question is a spike, never a build.** "Is the
  output good enough?" is answered by producing three real samples with a
  disposable driver and judging them — not by building the pipeline that
  would use them. A spike jumps the queue: run it as soon as its inputs
  exist, whatever epic is in progress.
- An **integration question gets the walking skeleton — one story, never an
  epic.** When epics build sequentially on real predecessors, integration is
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
| Small | Fits one agent session, acceptance run included | "almost there" for a long stretch |
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
(the UI shows X, the CLI prints Y) — an increment verified only by unit
tests is not usable yet.
