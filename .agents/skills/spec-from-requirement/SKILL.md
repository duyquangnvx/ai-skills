---
name: spec-from-requirement
description: Use when the user wants a detailed specification (CLI surface, API contract, schema, integration spec) produced from a requirement or design document while applying a standard — a skill, best-practices doc, or convention set — especially when delegating the writing to a subagent, or when a previous spec attempt came back shallow, generic, or duplicated the design doc instead of specifying the interface.
---

# Spec from Requirement

Turn a requirement/design doc + a standard into a detailed, reviewable specification by dispatching ONE subagent with a structured prompt. Spec depth is determined by the prompt's structure, not the model: an unstructured "write a spec" prompt yields a spec at whatever depth the agent picks — usually shallow, and often a re-narration of the design doc.

## The five elements the dispatch prompt MUST contain

A naturally-written dispatch prompt already gets the basics right (read inputs first, list sections, write to one file). These five are what it reliably misses — each maps to a failure observed without them:

1. **Two sources, two roles, explicit precedence.** Standard = quality authority; requirement doc = product truth that must NOT be redesigned. State both directions: "follow the standard where the requirement is silent or conflicting" AND "do not redesign the product / re-document its internals." Without the second guard, the spec duplicates the design doc's data model and pipeline instead of specifying the interface.
2. **Enumerated deliverables, each with a completeness definition.** Letter every section (a, b, c...) and define what "complete" means inside it ("every command — flags short+long, defaults, examples for both human and `--json`/script usage"). The agent fills the frame you give; no frame → agent picks its own depth.
3. **A dedicated Tensions section, seeded with one example.** Require a section listing every conflict between standard and requirement, each with: the conflict, the reconciliation chosen, and what to ask the product owner. Seed it with ONE real conflict you already spotted ("example to examine: X says A, standard forbids A"). The seed calibrates sophistication — agents given a seed find the remaining tensions at that depth; agents without one find fewer and shallower.
4. **Traceability.** Require an "Inputs used" section: which files were read, plus a table of major decision → driving section of the standard. This forces the agent to actually open the references and blocks unverifiable claims — without it, agents invent plausible-sounding repo/standard details.
5. **Operational locks.** Read all sources BEFORE writing; output to exactly ONE named file; do NOT create other files; no side effects (no installs/builds); final message is a 5-8 line summary of decisions and tensions, not the content.

## Dispatch prompt template

```
You are applying <STANDARD> to a real product requirement.

Standard to follow (read ALL of it first): <paths — entry file + which references to read>
Requirement document (read fully): <path> — <2-3 sentence orientation: what the product is,
which section sketches the surface to specify>. The requirement doc is product truth — do
not redesign its <pipeline/data model/...>. But where it conflicts with or underspecifies
what the standard mandates, follow the standard and FLAG each such point in a dedicated
"Tensions" section (example to examine: <one conflict you already spotted>).

Deliverables, all in ONE markdown file:
a) "Inputs used" — files read; table of major decisions → driving standard section
b..n) <every spec section, each with its completeness definition and required examples>
z) "Tensions" — every conflict found, your reconciliation, what you'd ask the product owner

Write the COMPLETE deliverable to: <output path>
Do NOT create any other files. Do not run <npm/build/network>.
Final message: 5-8 line summary of key decisions and the tensions you found.
```

## After the subagent returns

Verify the output file exists and skim its heading outline before reporting. Relay the Tensions to the user — they are decisions only the product owner can make; the resolved ones should be promoted to the project's ADR/decisions doc.

## Common mistakes

| Mistake | Consequence |
|---|---|
| "Apply the standard" without the do-not-redesign guard | Spec re-documents the design doc's internals; reviewer reads everything twice |
| Tensions required but not seeded | Agent reports 1-2 obvious conflicts, misses the subtle ones |
| Deliverables described, not enumerated | Agent picks its own (shallow) depth per section |
| No traceability requirement | Decisions cite nothing; agent fabricates details about the standard or repo |
| Letting the agent choose the output location | Files scattered; some content only in the final message, lost |
