# Verification Checklist (PM Layer)

Run after phase 3 (generation), before phase 5 (recommendations). These are quality gates — fix in place if any fail. Don't surface failures to the user as questions.

The exception: if a fact genuinely isn't recoverable from spec or conversation, convert to a `> TBD:` marker and add to the final summary.

## Layer purity

The single most important set of checks. Layer leakage is the biggest failure mode for this skill.

- [ ] No file mentions a specific programming language, framework, database, queue, or library — unless the user explicitly confirmed those as product-level locks.
- [ ] No file describes paths in the source tree, file layouts, or module organization. Repository structure is not a PM concern.
- [ ] No file lists code-level concepts — classes, services, controllers, components, hooks, or methods.
- [ ] No file prescribes commands. Build/test/deploy commands belong to dev-layer config.
- [ ] `architecture.md` describes the **product**, not the system. Items inside the boundary are feature groups, not modules.

If any check above fails, the skill drifted into implementation territory. Fix by removing or relocating; do not soften the rule.

## Roadmap integrity

- [ ] Every phase has both `In scope` and `Out of scope` explicit. Listing only what's in is half the story; what's deliberately out is what prevents scope creep.
- [ ] Every phase has observable Acceptance criteria — what an outside observer can verify, not internal completeness.
- [ ] Phases are vertical slices. Bad: "Phase 1: build all data models. Phase 2: build all surfaces." Good: each phase ships something demoable end-to-end.
- [ ] The `Why` for each phase explains why it's THIS phase, not the next or previous one. Reasoning, not restatement.
- [ ] Definition of Done v1 has only observable criteria. Aspirational phrases like "high quality" don't qualify.
- [ ] Phasing covers the full v1 scope. Every must-have feature lands in some phase, or is in `architecture.md` non-goals.

## Decisions log integrity

- [ ] Every row has a real Source pointer — section number, doc name, dated chat, link. Never blank, never "TBD".
- [ ] No invented decisions. Each row traces to either the spec or to explicit user confirmation in this conversation. Anything else: delete or mark `> TBD:`.
- [ ] IDs are sequential and unique. No gaps, no duplicates.
- [ ] No decisions about pure implementation. Only product-level commitments and process commitments belong here.
- [ ] One-line text per decision. Long context goes in linked docs.

## Progression integrity

- [ ] `Current phase` matches a phase that actually exists in `roadmap.md`.
- [ ] The phases table mirrors `roadmap.md` exactly — same numbers, same names. They drift apart fast otherwise.
- [ ] `Current focus` section is present with all four bullets (Active work, Recent changes, Immediate next steps, Open questions). At bootstrap, "not yet begun" is acceptable for Active work — but the structure must be there.
- [ ] Initial state is honest: all phases `⏳`, no fake "in progress" entries, log has exactly one entry (the bootstrap event).
- [ ] Update rules are present and cover Phase start, Phase done, Session end, Blocker, Decision made, Architecture changed, Roadmap scope changed.

## Architecture (product) integrity

- [ ] Under one page in any reasonable rendering. If longer, it's drifted into systems-engineering territory.
- [ ] "What's inside the boundary" lists feature groups, not modules.
- [ ] "What's outside" lists genuine externalities — things the project depends on but does not own. Not internal libraries.
- [ ] Constraints are observable rules, not aspirations. Anything that can't be verified is not a constraint.

## Cross-reference integrity

- [ ] `README.md` lists all four sibling files with one-line role descriptions.
- [ ] `README.md` has a "Protocol for agents" section with at-session-start, during-session, and at-session-end rules.
- [ ] `README.md` has a "What happens after planning" section delineating the boundary with feature-level work.
- [ ] `progression.md` links to `roadmap.md` and `decisions.md`.
- [ ] `roadmap.md` links to `decisions.md` and `progression.md` in its "How this evolves" section.
- [ ] `decisions.md` links to `progression.md` in its "How to add" section.
- [ ] `architecture.md` links to `decisions.md` in its "How this file evolves" section.
- [ ] Each phase in `roadmap.md` references the spec section(s) it implements (or has refs marked `—` if none apply).

## Honesty

- [ ] All `> TBD:` markers are listed in a single summary at the end of the skill's response.
- [ ] Every concrete claim across all four files traces to spec or to user confirmation. Anything else: replace with `> TBD:`.
- [ ] No file uses confident language for uncertain things. "The product targets X" only if a source confirms it; otherwise the line should explicitly say it's TBD.

## Anti-patterns to scan for and remove

- Implementation tasks anywhere in any file
- Aspirational platitudes about quality or maintainability
- Vague time estimates ("a few weeks", "soon") — use phase numbers or actual dates
- Reorganized restatements of the spec rather than analysis
- Generic boilerplate not specific to this product
