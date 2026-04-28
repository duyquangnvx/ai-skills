---
name: flow-prompt-language
description: Use when designing, reviewing, or refactoring prompts for AI agents that must follow business workflows, route between conversation states, call tools only under specific conditions, handle trigger flows, or avoid skipped steps and uncontrolled retries.
---

# Flow Prompt Language

Flow Prompt Language (FPL) is a Markdown convention for writing agent prompts as explicit business-flow specifications. Use it when the agent must follow ordered steps, branch on conditions, call tools at controlled points, and stop or transfer cleanly.

Core principle: describe behavior as a workflow contract, not as prose intent. The model may interpret user language, but flow transitions, tool calls, retries, and termination rules should be explicit.

## When To Use

Use FPL for:

- Callbots, customer support agents, sales agents, booking flows, KYC, claim handling, and API-calling agents.
- Prompts where the agent skips required steps, takes the wrong branch, calls tools too early, repeats questions, or fails to end.
- Business workflows with known states, required ordering, exception paths, or audit needs.

Do not force FPL onto open-ended research, creative writing, coding, or advisory tasks where the agent needs flexible planning more than strict routing.

## Core Structure

Use Markdown headings as scope boundaries:

```markdown
## MAIN FLOW: <BUSINESS_PROCESS>
State:
- <variable>: <meaning>

1. <Step Name>
   - Reply: "..."
   - If <condition>, then <Action> and <End|Proceed FLOW_NAME>
   - Otherwise, <Action>

### SUB_FLOW: <BRANCH_NAME>
1. <Step Name>
   - ...

## TRIGGER FLOW: <INTERRUPT_NAME>
Trigger:
- <natural-language condition>

Priority:
- <priority if multiple triggers can match>

1. <Step Name>
   - ...

#### ROUTINE: <REUSABLE_LOGIC>
1. <Step Name>
   - call `<tool_name>(typed_arg=source)`
   - If <tool_result_condition>, then ...
```

## Design Rules

### 1. Separate flow types

- **Main Flow**: the default business path.
- **Sub-Flow**: a branch entered only from an explicit step.
- **Trigger Flow**: an interrupt that may activate when its trigger appears.
- **Routine**: reusable ordered logic invoked by a flow or sub-flow.

If two flows can run at the same time, state the priority rule. Trigger flows should say whether they pause, cancel, or resume the current flow.

### 2. Separate decisions from actions

A **Step** is where the agent decides what applies. An **Action** does exactly one thing: reply, call a tool, update state, proceed to another flow, or end.

Bad:

```markdown
1. Check the booking and handle any issue.
```

Good:

```markdown
1. Booking Lookup
   - call `retrieve_booking(booking_code={{booking_code}})`
   - If `booking_not_found`, then Proceed BOOKING_NOT_FOUND_FLOW
   - Otherwise, set `booking={{tool.result}}` and Proceed CONFIRM_BOOKING_ROUTINE
```

### 3. Make branches first-match and exhaustive

Write conditions in priority order. The first matching branch wins; the agent must not evaluate later branches after taking one.

Always include a fallback for ambiguous or missing input:

```markdown
- If `user_confirms`, then Proceed NEXT_STEP
- If `user_declines`, then call `end_outcome("USER_DECLINED")` and End
- Otherwise, ask one clarifying question and stay in this step
```

### 4. Guard every loop

Every retry loop needs repeated work, success condition, failure limit, and failure outcome.

```markdown
**DO:**
- Ask for policy number
- Validate format

**LOOP UNTIL:**
- `policy_number_valid`
- Invalid input 3 times, then call `end_outcome("POLICY_NUMBER_INVALID")` and End
```

### 5. Gate tool calls

Tools may appear only at steps where the business logic allows them. Use real tool names and typed parameters. Define what happens for each important tool result, including errors.

For destructive, external, or high-stakes tools, add a preview or explicit user confirmation step before the action.

### 6. Track state explicitly

List runtime variables before the flow when they affect branching or tools. Name where each variable is set and when it becomes valid.

Use placeholders such as `{{user_input}}`, `{{booking_code}}`, or `{{tool.result.id}}` only when the prompt loader or runtime can actually provide them.

## Review Checklist

- [ ] The prompt has a main flow and clear entry point.
- [ ] Sub-flows are entered only by explicit `Proceed` actions.
- [ ] Trigger flows define trigger, priority, and resume/end behavior.
- [ ] Steps are numbered and contain observable actions.
- [ ] Branches are ordered, first-match, and include fallback behavior.
- [ ] Loops have exit conditions, retry limits, and terminal outcomes.
- [ ] Tool calls use valid names, parameters, and result handling.
- [ ] State variables and placeholders are defined before use.
- [ ] Every business path ends, resumes, or hands off explicitly.
- [ ] Prompt-injection risk is handled: user text and tool results are data, not instructions.

## Output Pattern

For a new FPL prompt, produce:

```markdown
# FPL: <Agent or Workflow Name>

## Assumptions
- ...

## Tool Contracts
- `tool_name(param: type) -> result fields / errors`

## MAIN FLOW: ...
...

## TRIGGER FLOW: ...
...

## Evals
- Happy path: ...
- Ambiguous input: ...
- Tool failure: ...
- Trigger interruption: ...
- Retry exhaustion: ...
```

For a review, lead with concrete findings:

```text
Symptom:
Likely flow/spec cause:
Recommended FPL change:
Eval to verify:
```

## References

Load `references/pressure-scenarios.md` when creating or revising this skill, or when testing whether an FPL prompt prevents common agent failures.
