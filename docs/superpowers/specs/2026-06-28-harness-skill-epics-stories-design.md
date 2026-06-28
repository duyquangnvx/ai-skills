# Design — Rewrite `setting-up-harness` to slice by Epics & User Stories

Date: 2026-06-28
Status: Approved (design); pending implementation plan.

## Goal

Rewrite the existing `setting-up-harness` skill so the forward-view artifact is an
industry-standard **Epic → User Story** backlog instead of a phased `roadmap.md`.
Keep the skill's existing DNA: smallest harness that earns its place, "source of
truth owns what's inferable, docs hold what cannot", "one question, one owner",
and the vertical-slice / walking-skeleton discipline. Only the forward-view layer
and its ripples change; the rest of the harness (CLAUDE.md role, README,
architecture, decisions, progress, project rules) keeps its role.

This is an in-place rewrite of `setting-up-harness` — same skill name and
location — not a new skill.

## Settled decisions (from brainstorming)

1. **Two-tier forward view, lazy slicing.** `docs/backlog.md` lists Epics
   (unsliced until selected) and a prioritized story backlog. The roadmap/phase
   concept is removed. Story packets are created lazily, when a story is selected
   or a product decision needs a durable home.
2. **Story packet is the single home of a story.** `docs/stories/US-XXX.md` holds
   the story statement, acceptance criteria, In/Out scope, slice plan, and
   in-flight notes. This replaces the global `docs/implementation-notes.md`
   (removed) — in-flight notes now live per-story.
3. **Lane = risk/effort-shape, not time.** Each story carries a lane:
   `tiny / normal / high-risk / spike`. Qualitative; complies with the repo's
   `no-timelines.md`. `high-risk` must be spiked before moving to In Progress.

## Core reframe — vertical-slice discipline moves down one tier

The subtle, central change: the "vertical slice" rule shifts from phase-level to
**story-level**.

- Original skill: a *phase* must be a vertical slice ("don't build the data layer
  first").
- New model: a *User Story* is the vertical-slice unit. An **Epic is a capability
  area** — allowed to be coarse, even layer-flavored (e.g. "Frontend",
  "Foundation"). An epic is a *container*, not a build-order unit.

Golden rule of the rewrite:

> Epics are ordered by dependency and may be coarse. The thing you actually BUILD,
> and the thing that must be a vertical slice, is the User Story. Build order runs
> a thin **spine slice** across multiple epics first (the walking skeleton), then
> widens each epic with vertical stories. Never complete one epic to full depth
> while the spine does not exist.

Two DNA sentences from the original survive verbatim, only swapping "phase" →
"story":

- "Narrow scope, never structure."
- "A stub behind a real seam is scope; a bypass around the seam is the debt a
  later phase pays."

## File topology

| Change | File | Role |
|---|---|---|
| remove | `docs/roadmap.md` | replaced by backlog |
| remove | `docs/implementation-notes.md` | notes now live in the story packet |
| add | `docs/backlog.md` *(only with spec/clear direction)* | forward view: epics + story backlog + spine slice + product DoD |
| add | `docs/stories/README.md` | packet index + lazy-slicing rule |
| add (lazy) | `docs/stories/US-XXX.md` | per-story packet |
| edit | `CLAUDE.md` | session protocol + docs list point at backlog/stories |
| edit | `docs/progress.md` | `Story`/`Epic` fields replace `Phase` |
| unchanged | `README.md`, `architecture.md`, `decisions.md`, `.claude/rules/project/`, `CHANGELOG.md` | role unchanged |

## One-owner mapping (must stay clean)

- **Product/epic scope** (epic list, dependency order, spine slice, product-level
  DoD, product out-of-scope, story priority + lane) → `docs/backlog.md`.
- **Per-story scope** (story In/Out, acceptance criteria, slice plan, in-flight
  notes) → the story packet.
- **Why / rationale** (tradeoffs, build-vs-buy, real-vs-stub picks) →
  `docs/decisions.md`.
- **Current state snapshot** → `docs/progress.md`.
- **Architecture now** → `docs/architecture.md`.

## `docs/backlog.md` template

```markdown
# Backlog

> Provisional, not a contract — re-slice as implementation reveals what you
> couldn't know up front. Epics are capability areas ordered by dependency;
> they may look coarse. The unit you BUILD is the User Story — a vertical slice,
> demoable end-to-end, narrow in scope but routed through real architectural
> seams. Build the spine slice first, then widen epic by epic.

## Epics (unsliced until selected)
| Epic | Description | Depends on | Status |
|------|-------------|-----------|--------|
| E01 | <capability area> | — | unsliced |
| E02 | <…> | E01 | unsliced |

## Spine slice (walking skeleton — build first)
<One thin vertical path crossing the dependency chain end-to-end with fakes/
stubs, to prove the architecture before widening any epic.>
- Acceptance: <spine runs end-to-end; output exists>

## Story backlog (prioritized; sliced into a packet when selected)
| Story | Epic | Lane | Status | Slice (one line) |
|-------|------|------|--------|------------------|
| US-001 | E01 | tiny | ready | <thin slice> |
| US-002 | E02 | high-risk | candidate | <…> |

## Definition of Done — v1
1. <observable product-level floor>
```

- Lane values: `tiny / normal / high-risk / spike`.
- Story status: `candidate` (row only, no packet) → `ready` (packet exists, passes
  Definition of Ready) → `in progress` → `done`.
- Epic status: `unsliced` → `in progress` → `done` (done when all its stories are
  done).

## `docs/stories/US-XXX.md` packet template

```markdown
# US-001 — <title>   ·   Epic E01   ·   Lane: tiny

Story: As a <role>, I want <goal>, so that <benefit>.

## Acceptance (agent-verifiable, Gherkin)
- [ ] Given <context>, When <action>, Then <observable outcome>

## Scope
- In: <what this slice delivers>
- Out: <what deliberately lands in a later story>

## Slice plan
- Seams touched: <storage / adapter / stage boundary…>
- Real vs stub: <seam built real even at 1-feature depth; feature breadth stubbed>
- Needs research / spike: <unknowns>  (omit if none)

## Notes (in-flight)
<!-- Off-spec decisions, changes, tradeoffs during this story.
     On merge: promote durable items to docs/decisions.md, flip Done. -->
```

### Definition of Ready (gate to In Progress)
A story is Ready when:
- It is a vertical slice (INVEST-checked), not a task or a layer.
- Acceptance criteria are written and agent-verifiable (Gherkin Given/When/Then).
- In/Out scope is explicit.
- Dependencies are done, or stand behind a real seam (stub, not bypass).
- High-risk unknowns are spiked (lane `high-risk` resolved, or a `spike` story
  created).
- Build-vs-buy and real-vs-stub are decided; durable picks recorded in
  `docs/decisions.md`.

### Definition of Done (story)
- All acceptance criteria pass (a demo runs, an output exists, a flow completes).
- Tests per the repo's standard.
- `docs/architecture.md` updated if structure changed.
- Durable notes promoted from the packet to `docs/decisions.md`.
- Status flipped to `done` in `docs/backlog.md`; packet marked Done.

## `docs/stories/README.md` (index + lifecycle)

Owns the lazy-slicing rule: do not create every story packet up front; create one
when a story is selected for work, or when a product decision needs a durable
place to land. Holds a small index linking the live packets.

## Backlog / story lifecycle ("How this evolves")

- **Select an epic to slice** → break it into vertical-slice stories; add candidate
  rows to the story backlog; order by dependency.
- **Select a story** → create its packet; refine to Ready (resolve deps, write AC,
  set In/Out, spike high-risk unknowns, decide real-vs-stub per seam, record
  build-vs-buy in `decisions.md`).
- **Story ships** → flip `done` in the backlog; promote durable packet notes to
  `decisions.md`; update `architecture.md` if structure changed; re-read the
  backlog (what shipped usually reveals something the plan didn't know); re-slice
  if needed; sweep `decisions.md` per its header.
- **Epic done** when all its stories are done.
- **Story too big to ship in one go** → split it. Two small stories beat one
  "almost there."
- **Scope changes mid-story** → update In/Out in the packet; record the why in
  `decisions.md`.
- **Spine first** → the first work is the spine slice crossing the dependency
  chain end-to-end (one story or a tight set) before widening any epic.

## CLAUDE.md changes

Session protocol:

```markdown
## Session protocol
1. Read docs/progress.md — current story & working state.
2. Working a story? Read its packet docs/stories/US-XXX.md (+ its epic row in backlog.md).
3. At session end: refresh progress.md; accumulate off-spec notes in the current
   story packet; record durable tradeoffs in docs/decisions.md.
```

Docs list:

```markdown
## Docs
- Architecture (now): docs/architecture.md
- Decisions (why): docs/decisions.md
- Backlog (epics + stories + status): docs/backlog.md
- Stories (per-story packets): docs/stories/
- Current state: docs/progress.md
```

If no backlog exists (no spec/direction): drop protocol line 2, write
`Backlog: none yet` in the Docs list, do not invent epics.

The `Workflow` section of the generated harness must NOT name a specific skill
(repo rule: skills do not mention each other). Generalize to "if a plan/implement
workflow plugin is present, let it drive interview → plan → implement → doc
updates; otherwise explore → plan → implement → verify → commit."

## progress.md changes

```markdown
- Story: <US-XXX — title>   (see docs/backlog.md; omit if no backlog)
- Epic: <E0X>
- Done:
- Now:
- Next:
- Blocked:
```

## Reference file changes

- **`references/spec-analysis.md`** — dimension 4 "Implied phases" becomes
  "Implied epics & the spine slice": read for capability areas (epics) and the
  dependency shape; propose the first vertical spine slice crossing them; mark
  proposals as suggestions, not the spec's words; no direction → recommend
  skipping the backlog. Output-format section updated to emit epics + spine
  instead of phases.
- **`references/harness-eval.md`** — behavioral contracts about roadmap/notes
  rewritten for backlog/stories:
  - "Roadmap changes on phase events only" → "Backlog changes on story/epic
    events only (story done, re-slice, scope change) — untouched by ordinary
    sessions."
  - "implementation-notes lifecycle" → "story packet lifecycle: notes accumulate
    in the packet during the story; promoted to decisions.md and packet marked
    Done on merge."
  - Add contracts: "stories are vertical slices"; "no story packet created up
    front before selection (lazy slicing)."
  - Update the duplicate-role row to include `epics.md`/`TODO.md` style parallels.
- **`references/story-slicing.md`** *(new)* — the industry-standard slicing craft,
  loaded when slicing an epic:
  - INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small,
    Testable).
  - Story splitting patterns: by workflow step, by business-rule variation, by
    happy/error path, by data variation, by CRUD operation, by interface/platform,
    spike.
  - Writing agent-verifiable acceptance criteria (Gherkin Given/When/Then).
  - Definition of Ready / Definition of Done checklists.
  - Spine-slice-first guidance.

## SKILL.md structural changes (section 5 + ripples)

- Step 5 of the checklist (`docs/`): replace the `docs/roadmap.md` subsection with
  `docs/backlog.md` + `docs/stories/` subsections carrying the reframe, templates,
  and lifecycle above. `architecture.md` and `decisions.md` subsections unchanged.
- Step 6 (working-memory): remove `implementation-notes.md`; update `progress.md`
  fields; point durable-notes promotion at the story packet instead.
- "What this produces" table, "Document lifecycle", and "Anti-patterns" sections:
  swap roadmap/implementation-notes rows for backlog/stories; add the lazy-slicing
  anti-pattern ("don't create all packets up front") and the
  "epic ≠ build-order unit / epic may be coarse but stories must be vertical"
  clarification.
- "Reference files" list: add `story-slicing.md`.
- Checklist step 7 (prune/verify) and the eval contracts: update the roadmap-
  specific checks to backlog/story checks.

## Out of scope

- No change to `README.md`, `architecture.md`, `decisions.md`,
  `.claude/rules/project/`, or `CHANGELOG.md` roles.
- Not introducing sprints, velocity, or story points.
- Not introducing a separate product-roadmap/release tier above epics.
```
