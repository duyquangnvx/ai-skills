# FPL Design Patterns

Reusable patterns for common agent workflows. Copy only the relevant block, then rename states, tools, and placeholders to match the target system.

## Authentication Pattern

Use when an agent must verify identity before sensitive operations.

```markdown
#### AUTHENTICATION ROUTINE
1. Request Identifier
  - Reply "May I have your {{identifier_label}}?"

2. Verify Identifier
  - call verify_identity(id={{user_input}}, type={{identifier_type}})
  - If **verified**, then set state.authenticated = true and proceed to step 3
  - If **locked**, then reply "This account is locked. Please contact support." and **End**
  - If **attempts >= 3**, then call end_session(reason="AUTH_FAILED") and **End**
  - Otherwise, reply "I could not verify that. Please try again." and repeat step 1

3. Complete Authentication
  - Return to calling flow
```

## Retry With Backoff Pattern

Use when a tool call may fail temporarily.

```markdown
#### RETRY_OPERATION ROUTINE
1. Attempt Operation
  - call {{operation_name}}({{operation_params}})
  - If **success**, then set state.operation_result = {{result}} and return to calling flow
  - If **attempts >= 3**, then reply "I am unable to complete that right now." and **Proceed** FALLBACK_SUB_FLOW
  - Otherwise, wait {{backoff_seconds}} seconds and repeat step 1
```

## Escalation Pattern

Use when the user requests human help or the agent reaches a capability boundary.

```markdown
## TRIGGER FLOW: ESCALATION_FLOW
*Trigger*: user asks for "manager", "supervisor", "human", "real person", or "speak to someone"

1. Confirm Escalation
  - Reply "I can connect you with a team member. Please give me a brief summary of the issue."

2. Prepare Handoff
  - call create_ticket(summary={{user_input}}, priority={{state.calculated_priority}})
  - call transfer_to_agent(ticket_id={{ticket_id}}, department={{state.department}})
  - Reply "I created ticket #{{ticket_id}} and will connect you now."
  - **End**
```

Conditional escalation inside another flow:

```markdown
- If **sentiment_negative** AND **failed_resolution_attempts >= 2**, then **Proceed** ESCALATION_FLOW
- If **confidence < 0.6**, then **Proceed** ESCALATION_FLOW
- Otherwise, proceed to step 4
```

## Data Collection Pattern

Use when the agent must collect multiple fields in sequence.

```markdown
#### COLLECT_INFO ROUTINE
1. Collect Field A
  - Reply "What is your {{field_a_label}}?"
  - call validate_field_a(value={{user_input}})
  - If **valid**, then set state.field_a = {{user_input}} and proceed to step 2
  - If **attempts >= 3**, then reply "I could not confirm a valid {{field_a_label}}." and **End**
  - Otherwise, reply "Please provide a valid {{field_a_label}}." and repeat step 1

2. Collect Field B
  - Reply "What is your {{field_b_label}}?"
  - call validate_field_b(value={{user_input}})
  - If **valid**, then set state.field_b = {{user_input}} and proceed to step 3
  - If **attempts >= 3**, then reply "I could not confirm a valid {{field_b_label}}." and **End**
  - Otherwise, reply "Please provide a valid {{field_b_label}}." and repeat step 2

3. Confirm Collected Data
  - Reply "I have {{state.field_a}} and {{state.field_b}}. Is that correct?"
  - If **user_confirms**, then return to calling flow
  - If **user_corrects_field_a**, then repeat step 1
  - If **user_corrects_field_b**, then repeat step 2
  - Otherwise, reply "Please tell me what needs to change." and repeat step 3
```

## Try-Catch Pattern

Use when tool calls or external operations may fail unpredictably.

```markdown
3. Execute Operation
  - call {{operation_name}}({{operation_params}})
  - If **success**, then set state.operation_result = {{result}} and proceed to step 4
  - If **timeout** AND **attempts < 2**, then reply "The system is taking longer than expected. I will try once more." and repeat step 3
  - If **error_recoverable**, then call log_error(error={{error}}) and **Proceed** ALTERNATIVE_SUB_FLOW
  - If **error_fatal**, then reply "I encountered an issue and will connect you with support." and **Proceed** ESCALATION_FLOW
  - Otherwise, call log_error(error={{error}}) and **Proceed** ESCALATION_FLOW
```

## Confirmation Before Action Pattern

Use when irreversible or high-impact operations require explicit consent.

```markdown
4. Confirm Before Execute
  - Reply "I am about to {{action_description}}. This will {{impact_description}}. Shall I proceed?"
  - If **user_confirms**, then call {{action_name}}({{action_params}}) and proceed to step 5
  - If **user_declines**, then reply "No problem. What would you like to do instead?" and **Proceed** MAIN FLOW
  - Otherwise, reply "Please answer yes or no." and repeat step 4
```

## Saga Pattern

Use when multiple operations must succeed together, with rollback on failure.

```markdown
#### BOOKING_SAGA ROUTINE
1. Reserve Slot
  - call reserve_slot(date={{state.date}}, duration={{state.duration}})
  - If **reserved**, then set state.reservation_id = {{reservation_id}} and proceed to step 2
  - Otherwise, reply "That slot is unavailable." and **End**

2. Process Payment
  - call charge_payment(amount={{state.amount}}, method={{state.payment_method}})
  - If **paid**, then set state.payment_id = {{payment_id}} and proceed to step 3
  - Otherwise, call release_slot(reservation_id={{state.reservation_id}}), reply "Payment failed.", and **End**

3. Send Confirmation
  - call send_confirmation(booking_id={{booking_id}}, email={{state.user_email}})
  - If **sent**, then proceed to step 4
  - Otherwise, call log_warning(code="confirmation_send_failed") and proceed to step 4

4. Complete
  - Reply "Booking confirmed. Reference: {{booking_id}}"
  - **End**
```

## State Machine Pattern

Use when behavior depends on conversation state.

```markdown
## GLOBAL RULES
Valid states: GREETING, COLLECTING, PROCESSING, CONFIRMING, DONE.
State transitions happen only through explicit `set state.current = ...` actions.

## MAIN FLOW: STATE_MACHINE
1. Check State
  - If **state.current == "GREETING"**, then **Proceed** GREETING_SUB_FLOW
  - If **state.current == "COLLECTING"**, then **Proceed** DATA_COLLECTION_SUB_FLOW
  - If **state.current == "PROCESSING"**, then **Proceed** PROCESSING_SUB_FLOW
  - If **state.current == "CONFIRMING"**, then **Proceed** CONFIRMATION_SUB_FLOW
  - Otherwise, set state.current = "GREETING" and **Proceed** GREETING_SUB_FLOW
```

## Progressive Disclosure Pattern

Use when the agent must present complex information without overwhelming the user.

```markdown
5. Present Results
  - Reply with the top 3 results from {{state.results}}
  - Reply "Would you like details on any of these, or should I show more?"
  - If **user_selects_item**, then call get_details(item_id={{selected_item_id}}) and proceed to step 6
  - If **user_wants_more**, then set state.result_page = {{state.result_page + 1}} and repeat step 5
  - Otherwise, proceed to step 7
```
