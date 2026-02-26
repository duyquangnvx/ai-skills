---
name: flow-prompt-language
description: Write structured agent instructions using Flow Prompt Language (FPL). Triggers when user wants to create, refactor, or improve prompts/instructions for AI agents — especially agents handling business workflows, customer service, sales, booking, verification, or any multi-step process. Also use when user mentions "agent instructions", "agent prompt", "workflow prompt", "FPL", or complains about agents skipping steps, calling tools wrong, or behaving unpredictably. If the user is designing any kind of agent that needs deterministic behavior, this skill applies.
---

# Flow Prompt Language (FPL)

FPL is a method for writing agent instructions as workflow specifications instead of free-form text. The core insight: agents need execution blueprints, not intent descriptions.

When a prompt says "handle customer complaints professionally and escalate when needed", the agent must guess what "professionally" means, when exactly to escalate, and what steps to follow. When an FPL prompt defines the exact flow with steps, conditions, and actions, the agent executes reliably.

## When to use this skill

- Creating new agent instructions for any business workflow
- Refactoring existing prompts that produce inconsistent agent behavior
- Designing agents that must follow specific sequences, handle branching logic, or call tools at precise moments
- Any situation where the user says their agent "skips steps", "calls wrong tools", or "doesn't follow instructions"

## Authoring workflow

Follow these steps when creating FPL instructions:

1. **Map the business process** — Ask the user to describe the workflow in plain language. Identify each distinct process as a Flow or Trigger Flow.
2. **Identify branches** — Find decision points. Each branch with its own sequence becomes a Sub-Flow.
3. **Extract reusable blocks** — Logic that repeats (identity verification, confirmation sequences) becomes a Routine.
4. **Number every step** — Each step gets explicit numbering. Place Actions (tool calls, replies, state changes) directly under the step that triggers them.
5. **Add conditions and guards** — Write If-Then-Otherwise for every decision. Add exit conditions for every loop.
6. **Review with checklist** — see Review Checklist section below.

## FPL building blocks

### Flow types — defined by Markdown heading level

```
## MAIN FLOW: <NAME>           — Primary business process. Agent starts here.
### SUB_FLOW: <NAME>           — Branch entered only when a condition is met.
## TRIGGER FLOW: <NAME>        — Can interrupt any flow when trigger matches.
  *Trigger*: <natural language pattern or regex>
#### <ROUTINE_NAME> ROUTINE    — Reusable logic block, called by name from any flow.
```

Why heading levels matter: the agent uses Markdown hierarchy to understand scope and nesting. A Sub-Flow (###) is scoped under its parent Flow (##). This is not formatting — it is structural logic.

### Steps and Actions

A **Step** is where the agent makes a decision. An **Action** is what happens as a result — it does exactly one thing.

```
1. Step Title
  - Action: reply "..." / call tool(...) / set state / **End** / **Proceed** <FLOW>
  - If <condition>, then <action> and **Proceed** <FLOW>
  - Otherwise, <action> and **End**
```

Actions never contain logic. Steps never execute without Actions. Keep them separated — this is what prevents the agent from confusing "deciding" with "doing."

### Conditions

Write conditions as **If – Then – Otherwise** chains. The agent reads top-to-bottom and takes the first matching branch, then stops evaluating.

```
- If **verification_failed**, then call end_call("VERIFY_FAIL") and **End**
- If **user_is_vip**, then **Proceed** VIP_HANDLING_SUB_FLOW
- Otherwise, **Proceed** STANDARD_FLOW
```

### Loops

Every loop requires: what to repeat, exit condition, and max retries.

```
**DO:**
  - Ask user for date
  - Validate format
**LOOP UNTIL:**
  - Input is valid
  - Invalid input **3 times** → call end_call("INPUT_FAIL") and **End**
```

Never write loops without exit conditions — the agent will retry indefinitely.

### Tool calls

Tools appear only at designed points, as Actions within Steps. Include parameter sources explicitly.

```
- call get_slots(date={{preferred_date}}, location={{branch_id}})
- If **no_slots**, then reply "No availability" and **Proceed** RESCHEDULE_SUB_FLOW
```

This prevents hallucinated tool calls — the agent doesn't decide when to call tools, the flow does.

## Output template

When generating FPL instructions, use this structure:

```markdown
# <Agent Name> Instructions

## ROLE
<One paragraph: who the agent is, what domain it operates in>

## GLOBAL RULES
<Constraints that apply across ALL flows — tone, language, forbidden actions>

## MAIN FLOW: <PRIMARY_PROCESS>
1. <First Step>
  - <Action>

2. <Second Step>
  - If <condition>, then <action> and **Proceed** <SUB_FLOW>
  - Otherwise, <action>

### SUB_FLOW: <BRANCH_NAME>
1. <Step>
  - <Action>

#### <ROUTINE_NAME> ROUTINE
1. <Step>
  - <Action>
2. <Step>
  - If <condition>, then <action> and **End**

## TRIGGER FLOW: <INTERRUPT_NAME>
*Trigger*: <pattern>
1. <Step>
  - <Action> and **End**
```

## Anti-patterns — what NOT to do

**Vague instructions instead of steps:**
```
❌ "Verify the user's identity before proceeding"
✅ 1. Ask for policy number
     - Reply "May I have your policy number?"
   2. Verify policy
     - call verify_policy(number={{user_input}})
     - If **not_found**, then call end_call("POLICY_NOT_FOUND") and **End**
```

**Tool calls without conditions:**
```
❌ "Use the search API to find relevant information"
✅ - call search_kb(query={{user_question}})
   - If **no_results**, then reply "I couldn't find that info" and **Proceed** ESCALATION
```

**Loops without exit:**
```
❌ "Keep asking until the user provides valid input"
✅ **DO:** Ask for input / Validate
   **LOOP UNTIL:** Valid input OR **3 attempts** → End
```

**Mixing decision and execution:**
```
❌ "If the user seems frustrated, consider escalating to a supervisor"
✅ - If **sentiment_negative** AND **retry_count >= 2**, then **Proceed** ESCALATION_FLOW
```

## Review checklist

Before finalizing, verify:

- [ ] Every Flow has at least one **End** point
- [ ] Every Sub-Flow is reachable (some condition leads to it)
- [ ] Every Trigger Flow has a *Trigger* pattern defined
- [ ] Every loop has an exit condition with max retries
- [ ] Every tool call has explicit parameters with sources
- [ ] Every If-Then chain ends with an Otherwise
- [ ] Steps are numbered sequentially within each flow
- [ ] No "floating" instructions outside of a flow structure
- [ ] Heading hierarchy is consistent (## Flow, ### Sub-Flow, #### Routine)
- [ ] Placeholders use consistent format: {{variable_name}}

## For complex domains

Read `references/patterns.md` for reusable design patterns (retry, escalation, authentication, saga transactions).

Read `references/examples.md` for complete FPL examples across domains (customer service, sales, booking, verification, API integration).