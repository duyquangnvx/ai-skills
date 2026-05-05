---
name: project-bootstrap
description: Bootstrap a project's PM-level planning artifacts — roadmap, decisions log, progression tracker, and product architecture sketch — from an existing top-level spec, PRD, vision doc, or design brief. Use this skill at day-zero of a project to produce the planning surface that anchors a product across many sessions and many contributors. The output is "what ships, why, in what order, and where we are right now" — distinct from the spec above (which says what the product is) and from feature-level planning below (which says how a feature gets built). Trigger on requests like "bootstrap planning docs from this spec", "set up roadmap and decisions log", "scaffold the planning files from this PRD", "turn this vision doc into a phased plan". Use this skill even when the user does not explicitly mention "roadmap" or "decisions log" — the trigger is the day-zero PM-bootstrap intent itself. Do NOT use for feature-level planning. Do NOT use to produce code-level architecture, component diagrams, file structures, or task breakdowns — those are dev concerns. Do NOT use when the project already has planning artifacts — propose gap-filling instead of overwriting.
---

# Project Bootstrap (PM Planning Layer)

Takes an existing spec and produces the **PM-level planning artifacts** a project needs from day one. These are the "what / why / when / where-we-are" docs.

## Layer this skill operates at

Three layers exist in a typical product project. This skill produces only the middle one:

| Layer | Concern | Owner |
|---|---|---|
| Product / vision | Why does this exist, for whom, what is it | The spec — input to this skill |
| **PM planning** | **What ships, in what order, key decisions, where we are now** | **This skill** |
| Feature / implementation | How a feature is built; code structure, classes, components | Dev — out of scope for this skill |

The skill must NOT generate implementation tasks, code structure, file paths, framework choices, or anything code-shaped. Code thế nào là việc của dev.

## Outputs

Five files in `docs/plans/`. Four of them map to different time orientations, which is why each exists separately. The fifth is the folder index.

| File | Role | What it answers |
|---|---|---|
| `README.md` | Folder entry point + agent protocol | What's in this folder, in what order to read it, how agents should maintain it across sessions, what happens after planning ends |
| `architecture.md` | Present (invariant) | What kind of product is this? What does it touch? What are its hard constraints? |
| `roadmap.md` | Future (plan) | What ships, in what order, with what acceptance bar? |
| `decisions.md` | Past (locked) | What has been decided and why, append-only? |
| `progression.md` | Now (live) | Where are we right now (phase + session-level focus), what's blocking, what's next? |

The five cross-reference each other. `README.md` is the folder entry point; `progression.md` is the live status.

This skill does NOT create or modify any agent-facing file at the repo root (e.g., `AGENTS.md`, `CLAUDE.md`, repo `README.md`). Those belong to the dev layer and may already exist with content this skill must not touch. Linking from a repo-root entry point to `docs/plans/README.md` is recommended in phase 5 but is the user's action, not the skill's.

## Layout

One pattern: `docs/plans/` at the repo root. No alternatives in the default skill — projects that need a different layout can rename after the fact, the cross-references are sibling-relative.

```
project/
└── docs/
    └── plans/
        ├── README.md
        ├── architecture.md
        ├── decisions.md
        ├── progression.md
        └── roadmap.md
```

## Core workflow — five phases

### Phase 1: Read and analyze the spec

Read the full spec end-to-end. Then extract structured info using `references/spec-analysis.md`. The output is a 5–10 bullet analysis summary, shown to the user before any file is written.

The analysis stays at the PM layer. If the spec contains tech-stack details, framework choices, or code patterns, note that they exist (the dev layer will care) but do NOT carry them into the analysis or the generated artifacts. The PM layer should be re-implementable in any tech stack without changing.

### Phase 2: Clarify gaps and confirm scope

For each `[GAP]` in the analysis that blocks bootstrap, ASK the user. Common PM-side gaps:

- Phasing horizon — is v1 the only horizon, or is there v2/v3 thinking?
- Success threshold — what's the qualitative or quantitative bar for "we shipped"?
- Hard deadlines — anything from outside the team forcing a date?
- External dependencies — other teams, vendors, approvals
- Reversibility appetite — willing to rip and replace later, or is v1 commitment heavy?

End phase 2 with explicit confirmation: "I'll generate 4 files in `docs/plans/`. Proceed?"

### Phase 3: Generate the planning set

Generate in this order — each later file references earlier ones, and the README is generated last because it indexes the others:

1. **`architecture.md`** — Use `assets/architecture.md.template`. Product shape only: kind of product, major external dependencies, product-level constraints. One page max. Mark unknowns as `> TBD:`.

2. **`roadmap.md`** — Use `assets/roadmap.md.template`. Phases that match the spec's natural shape, each with Why / In / Out / Acceptance. Phases must be vertical slices — each phase ships something demoable end-to-end, not "build the data layer first, then the UI." Order by dependency. Include a Definition of Done for v1.

3. **`decisions.md`** — Use `assets/decisions.md.template`. Append-only table. Pre-populate only with decisions explicitly stated in the spec — give each one a sequential ID, a one-line statement, and a Source pointer. Do NOT invent decisions the spec didn't make.

4. **`progression.md`** — Use `assets/progression.md.template`. Initial state: phase 1 not started, no blockers, "Next" pointing to phase 1 kickoff. Current focus section filled with "Active work: not yet begun" and "Immediate next steps: kick off Phase 1." The Log section starts with one entry: "<date> — planning artifacts initialized."

5. **`README.md`** — Use `assets/README.md.template`. Folder index, agent protocol, and post-planning workflow notes. Generated last because it points to the other four. The Protocol for agents and What happens after planning sections are core — keep them as-is from the template; per-project customization is rarely needed for those.

After each file is written, tell the user where it lives and what placeholders need filling.

### Phase 4: Self-verify

Run `references/verification-checklist.md`. Fix in place — don't punt verification failures to the user. The exception is when a fact genuinely isn't recoverable from spec or conversation — convert to a `> TBD:` marker and add to the summary.

### Phase 5: Recommend next steps

Short actionable list (max 5 items). Generic recommendations:

1. Read through each file and fill remaining `> TBD:` markers
2. Commit `docs/plans/` to version control before any code lands — this anchors the spec
3. If the repo has an agent-facing entry point at the root (e.g., `AGENTS.md`, `CLAUDE.md`, or a top-level `README.md`), add a one-line pointer to `docs/plans/README.md` from there, so agents opening the repo find the planning surface. Don't create a root entry point file as part of this skill — that's the dev's call.
4. When ready to start phase 1, flip its status in `progression.md` to in-progress
5. Re-read the roadmap after the first phase ships — phasing assumptions decay fast

Do NOT offer to start implementation work. The skill ends with planning artifacts.

## Language

Match the user's conversational language. Generated docs should match the spec's language. Do not translate universal terms (roadmap, milestone, blocker, supersede).

## Anti-patterns to avoid

The failure modes that turn this skill into an implementation skill — refuse them even if asked:

- **Don't generate file structures.** No `src/`, no module layouts, no "create a Service named X". The dev decides this.
- **Don't pick tech stacks unless the spec did.** Picking a framework is not a PM decision unless the spec or user said so.
- **Don't write tasks at the action level.** "Implement feature X" is a dev task. PM-level granularity is "Phase N is shippable when <observable acceptance>."
- **Don't break phases into sub-tasks in the roadmap.** Acceptance criteria are the right granularity for a roadmap. Sub-tasks belong to the dev layer.
- **Don't invent decisions.** A decisions log is valuable because each entry was actually decided. Inventing entries to look complete is worse than being sparse.
- **Don't write the roadmap as a calendar.** Phase order with dependency reasoning beats calendar dates with fake confidence. Add dates only if the spec demands them.
- **Don't pad with platitudes.** No "follow best practices", no "prioritize quality", no "ensure testability". Either the spec said it (then quote and source it) or skip it.

## Reference files

- `references/spec-analysis.md` — Checklist for extracting PM-relevant info from any spec
- `references/verification-checklist.md` — PM-layer quality gates

## Asset templates

In `assets/`. Copy, fill, write to the project's `docs/plans/`:

- `assets/architecture.md.template`
- `assets/roadmap.md.template`
- `assets/decisions.md.template`
- `assets/progression.md.template`
- `assets/README.md.template`
