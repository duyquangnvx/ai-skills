# Spec-Driven Agent Development — Template Pack

A ready-to-use set of artifacts for **spec-driven development (SDD)**: you write an
intent-level spec, refine it into a technical plan, break the plan into discrete
tasks, and only then let an agent implement. The spec — not the code — is the source
of truth. Code becomes a *projection* of the spec, regenerable and reviewable.

Synthesized from GitHub **Spec Kit** (`specify → plan → tasks → implement`) and AWS
**Kiro** (`requirements → design → tasks`), trimmed to the essentials and aligned with
this repo's standards (feature-first layout, explicit acceptance criteria, 80% test
floor, no calendar estimates).

---

## When to use this

| Use SDD when… | Skip it when… |
|---|---|
| The feature is non-trivial and spans multiple files | A one-line fix or rename |
| Requirements are fuzzy or stakeholders disagree | The change is fully specified already |
| You want the agent to build *exactly* one thing, not improvise | You're exploring/prototyping throwaway code |
| You'll want to regenerate or re-implement against the same intent | Intent lives entirely in your head and won't change |

The payoff: assumptions surface while changing them costs keystrokes, not sprints.

---

## The workflow

```
constitution.md   (once per project — the non-negotiable principles)
        │
   ┌────▼─────┐   PHASE 0 — capture intent. WHAT & WHY, no tech.
   │ spec.md  │   Gate: zero [NEEDS CLARIFICATION] left unresolved.
   └────┬─────┘
        │
   ┌────▼─────┐   PHASE 1 — design. HOW. Stack, structure, contracts, data model.
   │ plan.md  │   Gate: passes the constitution check.
   └────┬─────┘
        │
   ┌────▼─────┐   PHASE 2 — decompose. Ordered, independently-testable tasks.
   │ tasks.md │   Gate: every requirement maps to ≥1 task.
   └────┬─────┘
        │
   ┌────▼─────┐   PHASE 3 — implement. Agent executes tasks in order.
   │   code   │   Gate: acceptance scenarios + success criteria pass.
   └──────────┘
```

**Hard rule between phases:** each phase produces *one artifact and stops*. The plan
phase does not write code; the tasks phase does not implement. A human (or a review
gate) approves each artifact before the next phase begins. This is the single most
common thing agents get wrong — they run past the gate into implementation.

---

## Directory layout

One folder per feature, numbered for ordering:

```
specs/
└── 001-<feature-slug>/
    ├── spec.md          # Phase 0 — the WHAT
    ├── plan.md          # Phase 1 — the HOW
    ├── tasks.md         # Phase 2 — the STEPS
    ├── research.md      # Phase 1 side-output — decisions & alternatives (optional)
    ├── data-model.md    # Phase 1 side-output — entities (if data-heavy)
    └── contracts/       # Phase 1 side-output — API/interface contracts (if any)
constitution.md          # repo root — project-wide principles (once)
```

---

## Artifact 0 — `constitution.md` *(once per project)*

The fixed principles every spec and plan is checked against. Keep it short; these are
hard constraints, not aspirations.

```markdown
# Project Constitution

## Principles
- **P1 — <name>**: <one-sentence non-negotiable rule>. Rationale: <why>.
- **P2 — <name>**: <rule>. Rationale: <why>.
- **P3 — Test floor**: every feature ships with tests; coverage ≥ 80%.
- **P4 — Simplicity**: no abstraction without a second concrete caller (YAGNI).

## Constraints
- Language/runtime: <e.g. TypeScript 5.x, Node 20>
- Architecture: <e.g. feature-first modules, no cross-feature imports>
- Forbidden: <e.g. no global mutable state, no hardcoded secrets>

## Review gates
A plan that violates a principle must justify it in plan.md → "Complexity Tracking",
or be rejected.
```

---

## Artifact 1 — `spec.md` (the WHAT) — Phase 0

> Describes behavior and value. **No tech choices, no file names, no APIs.** A
> non-technical stakeholder must be able to read and approve it. Mark every unknown
> with `[NEEDS CLARIFICATION: <question>]` — the gate is zero of these remaining.

```markdown
# Feature Specification: <FEATURE NAME>

**Feature**: `001-<feature-slug>` · **Status**: Draft · **Created**: <DATE>
**Input**: <the original one-line request>

## User Scenarios & Testing *(mandatory)*

Stories are PRIORITIZED (P1 = most critical) and each must be INDEPENDENTLY TESTABLE —
implementing only P1 still yields a viable MVP.

### User Story 1 — <Brief Title> (Priority: P1)
<The user journey in plain language.>

**Why this priority**: <value + why it ranks here>
**Independent test**: <how to verify this story alone delivers value>
**Acceptance scenarios**:
1. **Given** <state>, **When** <action>, **Then** <outcome>
2. **Given** <state>, **When** <action>, **Then** <outcome>

### User Story 2 — <Brief Title> (Priority: P2)
<journey> · **Why**: <…> · **Independent test**: <…>
1. **Given** <…>, **When** <…>, **Then** <…>

<Add more stories as needed, each with a priority.>

### Edge Cases
- What happens when <boundary condition>?
- How does the system handle <error scenario>?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST <specific capability>.
- **FR-002**: Users MUST be able to <key interaction>.
- **FR-003**: System MUST <data/behavior requirement>.
- **FR-004**: System MUST authenticate via [NEEDS CLARIFICATION: method not specified].

### Key Entities *(if data is involved)*
- **<Entity>**: <what it represents, key attributes — no schema/implementation>.

## Success Criteria *(mandatory)*

Measurable and **technology-agnostic** — no framework names here.
- **SC-001**: <e.g. "User completes signup in under 2 minutes">
- **SC-002**: <e.g. "System handles 1000 concurrent users without degradation">
- **SC-003**: <e.g. "90% of users complete the primary task on first attempt">

## Assumptions
- <assumption the spec depends on>

## Out of Scope
- <explicitly excluded so the agent doesn't gold-plate>
```

---

## Artifact 2 — `plan.md` (the HOW) — Phase 1

> The first place tech appears. Resolve every `NEEDS CLARIFICATION` from the spec or
> push it into `research.md`. Stop after the plan — **do not write code or tasks.**

```markdown
# Implementation Plan: <FEATURE>

**Feature**: `001-<feature-slug>` · **Date**: <DATE> · **Spec**: ./spec.md

## Summary
<Primary requirement (from spec) + the chosen technical approach in 2–3 sentences.>

## Technical Context
- **Language/Version**: <e.g. TypeScript 5.4>
- **Primary Dependencies**: <e.g. Hono, Zod>
- **Storage**: <e.g. Postgres / files / N/A>
- **Testing**: <e.g. Vitest>
- **Target Platform**: <e.g. Node 20 server>
- **Project Type**: <cli / web-service / library / …>
- **Performance Goals**: <e.g. p95 < 200ms> *(or N/A)*
- **Constraints**: <e.g. offline-capable, < 100MB memory> *(or N/A)*

## Constitution Check
*GATE — must pass before design proceeds; re-check after design.*
- [ ] P1 <name> — satisfied? <note>
- [ ] P3 Test floor — plan includes tests for each story
- [ ] P4 Simplicity — no speculative abstraction introduced

## Design

### Project Structure
<Concrete directory tree this feature adds/touches — real paths, not placeholders.>
```
src/<feature>/
├── <module>.ts
└── <module>.test.ts
```
**Structure decision**: <one line on why this layout>.

### Data Model *(if applicable → expand in data-model.md)*
- **<Entity>**: <fields, relationships, invariants>.

### Contracts *(if applicable → files in contracts/)*
- <endpoint / interface> → <input> → <output> → <errors>.

### Approach Notes
- <key decision> — chosen because <…>; rejected <alternative> because <…>.

## Complexity Tracking
*Fill ONLY if the Constitution Check has a justified violation.*

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| <e.g. extra layer> | <current need> | <why the simple option fails> |
```

---

## Artifact 3 — `tasks.md` (the STEPS) — Phase 2

> Mechanical decomposition of the plan. Tasks are grouped **by user story** so each
> story is an independently shippable increment. `[P]` marks tasks that can run in
> parallel (different files, no shared dependency). Include exact file paths. **No
> time estimates** — order and dependencies, not calendar.

```markdown
# Tasks: <FEATURE NAME>

**Input**: ./plan.md (required), ./spec.md (for stories) · **Feature**: 001-<slug>

## Format: `[ID] [P?] [Story] Description (file path)`
- **[P]** — parallelizable (independent file, no dependency)
- **[US#]** — the user story this serves

## Phase 1 — Setup
- [ ] T001 Create feature structure per plan (src/<feature>/)
- [ ] T002 [P] Add dependencies / configure tooling

## Phase 2 — Foundational *(blocks all stories)*
> No user-story work begins until this phase is done.
- [ ] T003 <shared model/schema all stories depend on>
- [ ] T004 [P] <error handling / base scaffolding>

## Phase 3 — User Story 1 (P1) 🎯 MVP
**Goal**: <what this delivers> · **Independent test**: <verify alone>
- [ ] T005 [P] [US1] Write test for <acceptance scenario> (…/x.test.ts)  ← TDD: fails first
- [ ] T006 [P] [US1] Implement <entity/model> (…/x.ts)
- [ ] T007 [US1] Implement <service/endpoint> (depends on T006)
- [ ] T008 [US1] Validation + error handling
**Checkpoint**: US1 fully functional and testable on its own.

## Phase 4 — User Story 2 (P2)
**Goal**: <…> · **Independent test**: <…>
- [ ] T009 [P] [US2] Write test for <scenario>
- [ ] T010 [US2] Implement <…>
**Checkpoint**: US2 works independently of US1.

## Phase 5 — Polish
- [ ] T0xx [P] Docs / cleanup / coverage to ≥ 80%

## Traceability
Every FR and SC from spec.md maps to at least one task above. Confirm before implementing.

| Requirement | Task(s) |
|---|---|
| FR-001 | T007 |
| SC-001 | T008, T010 |
```

---

## Phase gates — the agent's operating contract

Each gate is a hard stop. The agent presents the artifact and waits for approval.

| Gate | Pass condition |
|---|---|
| **Spec → Plan** | Zero unresolved `[NEEDS CLARIFICATION]`; every story has acceptance scenarios + a measurable success criterion. |
| **Plan → Tasks** | Constitution Check passes (or violations justified in Complexity Tracking); structure + contracts concrete. |
| **Tasks → Implement** | Every FR/SC traces to a task; task order respects dependencies; `[P]` tasks are genuinely independent. |
| **Implement → Done** | All acceptance scenarios pass; success criteria met; tests ≥ 80%; no constitution violation introduced. |

**Behavioral rules for the agent**
1. Produce one artifact per phase, then **stop and ask** — never run past a gate into the next phase.
2. Surface ambiguity as `[NEEDS CLARIFICATION]` rather than guessing.
3. Keep the spec tech-free and the success criteria technology-agnostic.
4. When implementing, follow `tasks.md` order; check off tasks as completed; don't invent work not in the task list.
5. If reality contradicts the plan mid-implementation, stop and amend `plan.md` — don't silently diverge.

---

## Quick start

```
1. Write constitution.md once (project principles).
2. /specify  <one-line intent>   → fills spec.md   → review, resolve clarifications.
3. /plan                         → fills plan.md   → review, pass constitution check.
4. /tasks                        → fills tasks.md  → review traceability.
5. /implement                    → agent executes tasks → verify against success criteria.
```

(The slash commands above mirror Spec Kit's `specify` CLI; you can also just prompt an
agent to "fill spec.md for <intent>, stop after the spec" at each phase.)

## References
- GitHub Spec Kit — https://github.com/github/spec-kit (canonical templates, `specify` CLI)
- Spec-Driven Development overview — https://developer.microsoft.com/blog/spec-driven-development-spec-kit
- AWS Kiro specs (requirements/design/tasks, EARS notation) — https://kiro.dev/docs/specs/
```
