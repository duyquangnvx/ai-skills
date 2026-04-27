# Pressure Scenarios

Use these with `superpowers:writing-skills` when changing this skill. Baseline agents should commonly miss at least one expected behavior without the skill; agents with the skill should comply.

## 1. Prose to Workflow

Prompt:

```text
Rewrite this support prompt into deterministic workflow instructions:
"Verify the customer, check the order, handle refunds when needed, and escalate if something goes wrong."
```

Baseline failures to watch for:

- Leaves vague actions such as "handle refunds" or "something goes wrong".
- Does not specify tool timing.
- Omits max retry or fallback paths.

Expected with skill:

- Produces `MAIN FLOW`, `SUB_FLOW`, and optional `ROUTINE` sections.
- Separates verification, order lookup, refund eligibility, refund confirmation, and escalation into numbered steps.
- Names tool parameters and parameter sources.
- Adds `Otherwise` fallbacks and reachable `**End**` points.

## 2. Trigger Versus Sub-Flow

Prompt:

```text
Review this FPL snippet:
## TRIGGER FLOW: ESCALATION_FLOW
*Trigger*: user asks for a manager
1. Escalate
  - call transfer_to_agent(summary={{summary}})
  - **End**

### SUB_FLOW: ORDER_FLOW
1. Lookup
  - call get_order(order_id={{order_id}})
  - If **not_found**, then Proceed ESCALATION_FLOW
```

Baseline failures to watch for:

- Accepts `Proceed ESCALATION_FLOW` even though it targets a trigger flow.
- Does not suggest a shared callable sub-flow.

Expected with skill:

- Flags that `Proceed` should target a `SUB_FLOW`, not a `TRIGGER FLOW`.
- Recommends `ESCALATION_SUB_FLOW` plus `ESCALATION_TRIGGER` that proceeds to it.

## 3. Missing Loop Exit

Prompt:

```text
Review this step:
1. Collect Code
  - Reply "What is the code?"
  - call validate_code(code={{user_input}})
  - If **invalid**, then repeat step 1
  - If **valid**, then go to step 2
```

Baseline failures to watch for:

- Says the loop is fine.
- Adds prose like "do not loop forever" without a concrete max-attempt branch.

Expected with skill:

- Requires a failure exit such as `If **attempts >= 3**, then ... and **End**`.
- Keeps validation as a tool action with explicit parameter source.

## 4. Hidden Tool Timing

Prompt:

```text
Convert this into FPL:
"Answer from the knowledge base when relevant. If confidence is low, escalate."
```

Baseline failures to watch for:

- Keeps "when relevant" as prose.
- Does not show where `search_kb` or confidence check happens.

Expected with skill:

- Adds a numbered search step with `call search_kb(query={{user_question}})`.
- Branches on `no_results`, `confidence < threshold`, and successful answer.
- Uses `Proceed ESCALATION_SUB_FLOW` for escalation.

## 5. Unsafe High-Impact Action

Prompt:

```text
Create FPL for cancelling a paid booking. The agent has tools cancel_booking and refund_payment.
```

Baseline failures to watch for:

- Calls cancellation/refund tools without explicit user confirmation.
- Does not define rollback/failure handling.

Expected with skill:

- Adds a confirmation step before cancellation/refund.
- Names payment and booking IDs from state or previous tool results.
- Adds failure branches and escalation.
- Ends intentionally after success or user decline.
