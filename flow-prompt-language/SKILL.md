---
name: flow-prompt-language
description: Use when creating, refactoring, or reviewing agent instructions for deterministic multi-step workflows, especially business processes with branching, tool calls, verification, escalation, booking, sales, customer service, or complaints about agents skipping steps or calling tools incorrectly.
---

# Flow Prompt Language (FPL)

FPL writes agent instructions as executable workflow specifications. The core rule: separate decisions from actions so the agent can follow a predictable path instead of inferring intent from prose.

## When to use this skill

- Creating or refactoring agent instructions for a business workflow
- Designing agents that must follow sequences, branch on conditions, or call tools at precise points
- Debugging prompts where agents skip steps, call wrong tools, loop indefinitely, or behave inconsistently
- Reviewing workflow prompts before handing them to another agent or production system

Use normal prose instead when the agent only needs style guidance, domain background, or a one-shot task with no branching workflow.

## Authoring workflow

1. Map the business process in plain language. Each independent process becomes a Flow or Trigger Flow.
2. Find decision points. Each branch with its own sequence becomes a Sub-Flow.
3. Extract repeated logic into a Routine, then call it explicitly from a Flow step.
4. Number every step inside each Flow, Sub-Flow, and Routine.
5. Put tool calls, replies, state changes, **Proceed**, and **End** only as Actions under a step.
6. Add guards: every decision chain has a fallback, every loop has a max retry exit, and every tool call names parameter sources.
7. Review the final prompt with the checklist below.

## FPL building blocks

### Flow types

Markdown heading levels define execution scope:

```markdown
## MAIN FLOW: <NAME>
### SUB_FLOW: <NAME>
## TRIGGER FLOW: <NAME>
*Trigger*: <natural language pattern or regex>
#### <ROUTINE_NAME> ROUTINE
```

- `MAIN FLOW` is the primary process.
- `SUB_FLOW` is entered only through a `Proceed` action.
- `TRIGGER FLOW` can interrupt other flows when its trigger matches.
- `ROUTINE` is reusable logic. It does not run unless an action calls it.

### Steps and actions

A Step decides what state the workflow is in. An Action does exactly one thing.

```markdown
1. Step Title
  - Reply "..."
  - call tool_name(param={{source_variable}})
  - If **condition_a**, then **Proceed** TARGET_SUB_FLOW
  - If **condition_b**, then set state.flag = true and **End**
  - Otherwise, reply "..." and **End**
```

Keep decision logic in `If` lines. Do not hide decisions inside vague actions like "handle issue", "route appropriately", or "retry if needed".

### Conditions

Write conditions as top-to-bottom chains. The first matching branch runs, then evaluation stops.

```markdown
- If **verification_failed**, then call end_call(reason="VERIFY_FAIL") and **End**
- If **user_is_vip**, then **Proceed** VIP_HANDLING_SUB_FLOW
- Otherwise, **Proceed** STANDARD_FLOW
```

Use `Otherwise` whenever the chain could fall through. A single guard may omit `Otherwise` only when the next action in the same step intentionally continues.

### Loops

Every loop needs the repeated work, success exit, and failure exit.

```markdown
**DO:**
  - Reply "What date works for you?"
  - call validate_date(date={{user_input}})
**LOOP UNTIL:**
  - If **valid_date**, then set state.preferred_date = {{user_input}} and exit loop
  - If **attempts >= 3**, then reply "I could not confirm a valid date." and **End**
```

Do not write open-ended loops such as "keep asking until valid".

### Routines

Define repeated logic once, then call it by name from a step.

```markdown
1. Verify Customer
  - Run AUTHENTICATION ROUTINE
  - If **state.authenticated == true**, then proceed to step 2
  - Otherwise, **End**

#### AUTHENTICATION ROUTINE
1. Request Identifier
  - Reply "May I have your account number?"
```

### Tool calls

Tools appear only as Actions. Every parameter must identify its source.

```markdown
- call get_slots(date={{state.preferred_date}}, location={{state.branch_id}})
- If **no_slots**, then reply "No availability for that date." and **Proceed** RESCHEDULE_SUB_FLOW
- Otherwise, present {{slots}} and proceed to step 4
```

## Output template

```markdown
# <Agent Name> Instructions

## ROLE
<Who the agent is and what domain it operates in.>

## GLOBAL RULES
<Constraints that apply across all flows: tone, language, safety boundaries, forbidden actions.>

## MAIN FLOW: <PRIMARY_PROCESS>
1. <First Step>
  - <Action>

2. <Decision Step>
  - If <condition>, then **Proceed** <SUB_FLOW>
  - Otherwise, <action> and **End**

### SUB_FLOW: <BRANCH_NAME>
1. <Step>
  - <Action>
  - **End**

#### <ROUTINE_NAME> ROUTINE
1. <Step>
  - <Action>

## TRIGGER FLOW: <INTERRUPT_NAME>
*Trigger*: <pattern>
1. <Step>
  - <Action> and **End**
```

## Common mistakes

### Vague prose instead of executable steps

```markdown
Bad: Verify the user's identity before proceeding.

Good:
1. Ask For Policy Number
  - Reply "May I have your policy number?"
2. Verify Policy
  - call verify_policy(number={{user_input}})
  - If **not_found**, then call end_call(reason="POLICY_NOT_FOUND") and **End**
  - Otherwise, set state.policy_id = {{policy_id}} and proceed to step 3
```

### Hidden tool timing

```markdown
Bad: Use search when relevant.

Good:
2. Search Knowledge Base
  - call search_kb(query={{user_question}})
  - If **no_results**, then reply "I could not find that information." and **Proceed** ESCALATION_SUB_FLOW
  - Otherwise, reply with {{search_result.summary}} and **End**
```

### Missing loop exit

```markdown
Bad: Keep asking until the user provides valid input.

Good:
**DO:**
  - Reply "Please provide the 6-digit code."
  - call validate_code(code={{user_input}})
**LOOP UNTIL:**
  - If **valid_code**, then exit loop
  - If **attempts >= 3**, then call end_session(reason="CODE_FAILED") and **End**
```

## Review checklist

Before finalizing, verify:

- [ ] Every Flow and Trigger Flow has at least one reachable **End** point.
- [ ] Every Sub-Flow is reachable through a `Proceed` action.
- [ ] Every Trigger Flow has a `*Trigger*` pattern.
- [ ] Every Routine is called from a Flow/Sub-Flow or explicitly marked as optional reference.
- [ ] Every loop has success and failure exits, including max retries.
- [ ] Every tool call has explicit parameters with sources.
- [ ] Every decision chain that can fall through has an `Otherwise`.
- [ ] Steps are numbered sequentially inside each Flow, Sub-Flow, and Routine.
- [ ] No operational instructions live outside `ROLE`, `GLOBAL RULES`, Flow, Sub-Flow, Trigger Flow, or Routine sections.
- [ ] Heading hierarchy is consistent: `##` Flow/Trigger, `###` Sub-Flow, `####` Routine.
- [ ] Placeholders use consistent format: `{{variable_name}}`.

## For complex domains

Read `references/patterns.md` for reusable design patterns: authentication, retry, escalation, data collection, try-catch, confirmation, saga, state machine, and progressive disclosure.

Read `references/examples.md` for complete examples across customer service, booking, and sales qualification.
