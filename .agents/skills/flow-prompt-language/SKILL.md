---
name: flow-prompt-language
description: Use when creating, refactoring, or reviewing agent instructions for deterministic multi-step workflows, especially business processes with branching, tool calls, verification, escalation, booking, sales, customer service, or complaints about agents skipping steps or calling tools incorrectly.
---

# Flow Prompt Language (FPL)

FPL turns agent instructions into explicit workflow specs. Use it when behavior depends on sequence, branching, state, tools, retries, confirmation, or escalation.

Core rule: separate decisions from actions. A step decides what state the workflow is in; each action does one observable thing.

Use normal prose instead when the agent only needs style guidance, domain background, or a one-shot task with no branching.

## Authoring Workflow

1. Map the process in plain language.
2. Split each independent process into a `MAIN FLOW`, callable `SUB_FLOW`, interrupt-only `TRIGGER FLOW`, or reusable `ROUTINE`.
3. Write numbered steps for every flow and routine.
4. Put replies, tool calls, state changes, flow transitions, routine calls, waits, and endings only as actions under steps.
5. Add guards: every decision chain has a fallback, every loop has max retries, every tool call names parameter sources, and every high-impact action has confirmation.
6. Run the review checklist.

## Structure

```markdown
# <Agent Name> Instructions

## ROLE
<Agent role and domain.>

## GLOBAL RULES
<Priority rules, tone, safety boundaries, and cross-flow policies.>

## MAIN FLOW: <PRIMARY_PROCESS>

### SUB_FLOW: <CALLABLE_BRANCH>

## TRIGGER FLOW: <INTERRUPT_NAME>
*Trigger*: <natural language pattern or regex>

#### <ROUTINE_NAME> ROUTINE
```

- `MAIN FLOW`: primary entry point.
- `SUB_FLOW`: callable only with `Proceed <SUB_FLOW_NAME>`.
- `TRIGGER FLOW`: starts only when its trigger matches. Do not `Proceed` directly to a trigger flow; put shared handling in a `SUB_FLOW`.
- `ROUTINE`: reusable logic called with `Run <ROUTINE_NAME> ROUTINE`.

## Action Vocabulary

Use these action forms consistently:

```markdown
- Reply "<user-facing text>"
- Present {{value_or_list}}
- call tool_name(param={{source_variable}})
- set state.field = {{value}}
- If **condition**, then <action>
- Otherwise, <action>
- Proceed <SUB_FLOW_NAME>
- go to step <number>
- repeat step <number>
- Run <ROUTINE_NAME> ROUTINE
- return to calling flow
- wait <duration>
- **End**
```

Rules:

- Use `Proceed` only for `SUB_FLOW` targets.
- Use `go to step` for forward movement inside the same flow.
- Use `repeat step` only when the step has a max-attempt or timeout exit.
- Use `return to calling flow` only inside routines.
- Use `**End**` when the workflow is complete or intentionally stops.
- If a branch calls a tool, include all required parameters and their sources.

## Decisions

Write condition chains top-to-bottom. The first matching branch runs, then evaluation stops.

```markdown
1. Route Request
  - If **verification_failed**, then call end_session(reason="VERIFY_FAIL") and **End**
  - If **user_is_vip**, then Proceed VIP_HANDLING_SUB_FLOW
  - Otherwise, Proceed STANDARD_HANDLING_SUB_FLOW
```

Use `Otherwise` whenever a chain can fall through. Do not hide decisions inside vague actions such as "handle appropriately" or "retry if needed".

## Loops

Every loop needs repeated work, success exit, and failure exit.

```markdown
1. Collect Code
  - Reply "Please provide the 6-digit code."
  - call validate_code(code={{user_input}})
  - If **valid_code**, then set state.verified = true and go to step 2
  - If **attempts >= 3**, then call end_session(reason="CODE_FAILED") and **End**
  - Otherwise, repeat step 1
```

## Tool Calls

Tools appear only as actions. Tool timing must be explicit.

```markdown
2. Search Knowledge Base
  - call search_kb(query={{user_question}})
  - If **no_results**, then Proceed ESCALATION_SUB_FLOW
  - Otherwise, Reply "{{search_result.summary}}" and **End**
```

## Review Checklist

- [ ] Every `MAIN FLOW` and `TRIGGER FLOW` has at least one reachable `**End**`.
- [ ] Every `SUB_FLOW` is reachable through `Proceed <SUB_FLOW_NAME>`.
- [ ] No `Proceed` action targets a `TRIGGER FLOW`.
- [ ] Every `TRIGGER FLOW` has a `*Trigger*`.
- [ ] Shared trigger handling lives in a `SUB_FLOW`, not duplicated trigger bodies.
- [ ] Every `ROUTINE` is called or explicitly marked as optional reference.
- [ ] Every routine path returns to the calling flow or ends intentionally.
- [ ] Every loop has success and failure exits, including max retries or timeout.
- [ ] Every tool call has explicit parameters with sources.
- [ ] Every decision chain that can fall through has an `Otherwise`.
- [ ] Step numbers are sequential integers inside each flow/routine.
- [ ] Operational instructions live only in `ROLE`, `GLOBAL RULES`, flows, sub-flows, trigger flows, or routines.
- [ ] Heading hierarchy is consistent: `##` main/trigger, `###` sub-flow, `####` routine.
- [ ] Placeholders use `{{variable_name}}` consistently.

## References

- `references/patterns.md` - reusable patterns for authentication, retry, escalation, data collection, confirmation, saga, state machine, and progressive disclosure.
- `references/examples.md` - complete examples across customer service, booking, and sales qualification.
- `references/testing.md` - pressure scenarios for validating this skill.
