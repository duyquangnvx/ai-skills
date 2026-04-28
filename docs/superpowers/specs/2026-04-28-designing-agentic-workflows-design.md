# Designing Agentic Workflows Skill Design

## Purpose

Create a Codex skill named `designing-agentic-workflows` for designing agentic AI workflows from scratch. The skill should guide an agent through deep discovery with the user and produce an `Agentic Workflow Spec` that is ready for prompt, tool, or implementation handoff if the user later requests it.

The skill is not primarily for reviewing or debugging an existing agent. It may mention those as non-goals or handoff cases, but the core behavior is new workflow design.

## Scope

The skill applies when a user wants to design an AI agent, agentic workflow, business automation flow, tool-using assistant, multi-step AI process, or AI workflow spec from an initial idea.

The skill should not be used for:

- General prompt polish without workflow design.
- Reviewing an existing broken agent workflow.
- Implementing code before the workflow spec is approved.
- Open-ended brainstorming that is not about an agentic workflow.

## Source Skills Combined

- `guided-consultation`: phased discovery, one decision at a time, recommendation plus choices when useful.
- `instructions-best-practices`: observable behavior contracts, instruction priority, untrusted-content boundaries, testable output.
- `agent-tool-design`: tool contracts, schemas, response shapes, validation, safety gates, bounded responses.
- `flow-prompt-language`: mandatory FPL-style workflow section with main flow, branches, triggers, routines, state, loop guards, tool gates, and terminal outcomes.
- `superpowers:writing-skills`: test-first skill creation using baseline pressure scenarios before writing `SKILL.md`.

## Consultation Model

The skill uses deep discovery before drafting. The agent should move through these phases in order:

1. Domain
2. Users and success criteria
3. Flow
4. Tools and data
5. Safety
6. Evals
7. Draft

The consultation style is assumption-forward:

- Ask one major decision per message.
- Recommend a default when there is a defensible trade-off.
- If the user gives incomplete detail, propose a labeled assumption.
- Confirm assumptions that affect flow, tools, safety, evals, or user outcomes.
- Do not draft the full spec before reaching the Draft phase unless the user explicitly asks to stop discovery and draft from current assumptions.

## Default Deliverable

The default artifact is an `Agentic Workflow Spec`, not an implementation plan and not a final production prompt.

The spec uses a fixed template:

```markdown
# Agentic Workflow Spec: <Name>

## Goal and Scope
## Operating Context
## Users and Success Criteria
## Assumptions
## State and Memory
## Tool Contracts
## Safety and Trust Boundaries
## FPL Workflow
## Failure Handling
## Evals
## Open Questions
```

Every section must appear. If a section does not apply, the section should say so explicitly, for example `No external tools required` or `No persistent memory required`.

## Workflow Requirements

The `FPL Workflow` section is mandatory. It must use Flow Prompt Language conventions:

- `## MAIN FLOW: <NAME>` for the default path.
- `### SUB_FLOW: <NAME>` for explicit branches.
- `## TRIGGER FLOW: <NAME>` for anytime interrupts.
- `#### ROUTINE: <NAME>` for reusable ordered logic.
- State variables defined before use.
- Branches ordered first-match with fallback behavior.
- Retry loops with exit conditions, limits, and terminal outcomes.
- Tool calls only inside valid steps with prerequisites and result handling.
- Every path ends, resumes, hands off, or records a terminal outcome.

## Tool Design Requirements

Tool contracts are conditionally required:

- If the workflow only advises, reasons, or writes text without external data or side effects, the section must state `No external tools required`.
- If the workflow reads external data, calls APIs, writes files, sends messages, performs bookings, updates records, handles payments, or causes side effects, the spec must define tool contracts.

Each tool contract should include:

- Tool name and one-sentence purpose.
- Inputs with types and source.
- Outputs with important fields.
- Error cases and retry or fallback behavior.
- Side effects.
- Reference or ID validation.
- Response bounds, pagination, or concise/detail behavior where relevant.
- Confirmation gate for destructive, external, financial, private-data, or high-stakes actions.

## Safety Requirements

Every spec must include `Safety and Trust Boundaries`.

The section must address:

- Trusted instructions versus user input, retrieved content, documents, web pages, tool results, and logs.
- The rule that untrusted content is data, not instructions.
- Private-data handling and exfiltration risk.
- Confirmation gates for destructive, external, financial, or high-stakes actions.
- Escalation or handoff conditions.
- Audit trail or terminal outcome needs when compliance, money, account changes, or user-impacting actions are involved.

## Eval Requirements

Every spec must include `Evals`.

The evals should cover process-relevant and workflow-relevant cases:

- Happy path.
- Ambiguous or missing input.
- Tool failure when tools exist.
- Trigger interruption.
- Retry exhaustion.
- Prompt injection or untrusted-content attempt.
- Safety confirmation or handoff case when relevant.

## Optional Handoff

The skill stops at the spec by default. It may offer optional handoff artifacts only after the spec is produced or if the user explicitly asks.

Possible handoff artifacts:

- FPL prompt.
- Tool schema draft.
- Eval suite.
- Implementation tickets.
- MCP or API boundary notes.

The skill should not automatically generate these artifacts during the default flow.

## Proposed Skill File

Path:

```text
.agents/skills/designing-agentic-workflows/SKILL.md
```

Potential frontmatter:

```yaml
---
name: designing-agentic-workflows
description: Use when designing an AI agent, tool-using assistant, business automation flow, or agentic workflow from scratch before writing prompts, tool schemas, evals, or implementation plans.
---
```

The description is trigger-only and does not summarize the process, matching `writing-skills` guidance.

## Pressure Test Strategy

Per `superpowers:writing-skills`, create baseline pressure scenarios before writing `SKILL.md`.

Primary test focus: process compliance.

Baseline scenarios should test whether an agent without the skill:

- Drafts the full spec too early before deep discovery.
- Asks many unrelated questions in one turn.
- Skips the safety phase.
- Skips evals.
- Fails to confirm a major assumption.
- Produces a non-fixed template.
- Jumps into prompt or implementation plan even though the requested deliverable is a spec.

After writing the skill, rerun the same scenarios and verify the agent:

- Moves through the required phases.
- Asks one major decision at a time.
- Uses labeled assumptions.
- Keeps safety and evals mandatory.
- Produces the fixed template only at the Draft phase.
- Stops at the spec unless handoff is requested.

## Open Implementation Notes

The next step is to create the pressure scenarios and run baseline tests before writing the skill. This design intentionally does not include a completed `SKILL.md` because the skill-writing workflow requires observed baseline failures first.
