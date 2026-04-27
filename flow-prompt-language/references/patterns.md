# FPL Design Patterns

Copy only the relevant pattern, then rename states, tools, flow names, and placeholders for the target system.

## Authentication Routine

Use when sensitive operations require identity verification.

```markdown
#### AUTHENTICATION ROUTINE
1. Request Identifier
  - Reply "May I have your {{identifier_label}}?"

2. Verify Identifier
  - call verify_identity(id={{user_input}}, type={{identifier_type}})
  - If **verified**, then set state.authenticated = true and return to calling flow
  - If **locked**, then Reply "This account is locked. Please contact support." and **End**
  - If **attempts >= 3**, then call end_session(reason="AUTH_FAILED") and **End**
  - Otherwise, Reply "I could not verify that. Please try again." and repeat step 1
```

## Retry Routine

Use when a tool can fail temporarily.

```markdown
#### RETRY_OPERATION ROUTINE
1. Attempt Operation
  - call {{operation_name}}({{operation_params}})
  - If **success**, then set state.operation_result = {{result}} and return to calling flow
  - If **attempts >= 3**, then Proceed FALLBACK_SUB_FLOW
  - Otherwise, wait {{backoff_seconds}} and repeat step 1
```

## Escalation

Use a callable sub-flow for shared escalation handling. Use a trigger flow only to enter that sub-flow.

```markdown
### SUB_FLOW: ESCALATION_SUB_FLOW
1. Prepare Handoff
  - Reply "I can connect you with a team member. Please give me a brief summary of the issue."
  - call create_ticket(summary={{user_input}}, priority={{state.calculated_priority}})
  - call transfer_to_agent(ticket_id={{ticket_id}}, department={{state.department}})
  - Reply "I created ticket #{{ticket_id}} and will connect you now."
  - **End**

## TRIGGER FLOW: ESCALATION_TRIGGER
*Trigger*: user asks for "manager", "supervisor", "human", "real person", or "speak to someone"
1. Start Escalation
  - Proceed ESCALATION_SUB_FLOW
```

Conditional escalation inside another flow:

```markdown
- If **sentiment_negative AND failed_resolution_attempts >= 2**, then Proceed ESCALATION_SUB_FLOW
- If **confidence < 0.6**, then Proceed ESCALATION_SUB_FLOW
- Otherwise, go to step 4
```

## Data Collection Routine

Use when the agent must collect multiple fields in sequence.

```markdown
#### COLLECT_INFO ROUTINE
1. Collect Field A
  - Reply "What is your {{field_a_label}}?"
  - call validate_field_a(value={{user_input}})
  - If **valid**, then set state.field_a = {{user_input}} and go to step 2
  - If **attempts >= 3**, then Reply "I could not confirm a valid {{field_a_label}}." and **End**
  - Otherwise, Reply "Please provide a valid {{field_a_label}}." and repeat step 1

2. Collect Field B
  - Reply "What is your {{field_b_label}}?"
  - call validate_field_b(value={{user_input}})
  - If **valid**, then set state.field_b = {{user_input}} and go to step 3
  - If **attempts >= 3**, then Reply "I could not confirm a valid {{field_b_label}}." and **End**
  - Otherwise, Reply "Please provide a valid {{field_b_label}}." and repeat step 2

3. Confirm Collected Data
  - Reply "I have {{state.field_a}} and {{state.field_b}}. Is that correct?"
  - If **user_confirms**, then return to calling flow
  - If **user_corrects_field_a**, then repeat step 1
  - If **user_corrects_field_b**, then repeat step 2
  - Otherwise, Reply "Please tell me what needs to change." and repeat step 3
```

## Tool Failure Handling

Use when external operations may timeout or fail.

```markdown
3. Execute Operation
  - call {{operation_name}}({{operation_params}})
  - If **success**, then set state.operation_result = {{result}} and go to step 4
  - If **timeout AND attempts < 2**, then Reply "The system is taking longer than expected. I will try once more." and repeat step 3
  - If **error_recoverable**, then call log_error(error={{error}}) and Proceed ALTERNATIVE_SUB_FLOW
  - Otherwise, call log_error(error={{error}}) and Proceed ESCALATION_SUB_FLOW
```

## Confirmation Before Action

Use before irreversible, external, or high-impact actions.

```markdown
4. Confirm Before Execute
  - Reply "I am about to {{action_description}}. This will {{impact_description}}. Shall I proceed?"
  - If **user_confirms**, then call {{action_name}}({{action_params}}) and go to step 5
  - If **user_declines**, then Reply "No problem. What would you like to do instead?" and go to step 1
  - Otherwise, Reply "Please answer yes or no." and repeat step 4
```

## Saga

Use when multiple operations should succeed together and require compensation on failure.

```markdown
#### BOOKING_SAGA ROUTINE
1. Reserve Slot
  - call reserve_slot(date={{state.date}}, duration={{state.duration}})
  - If **reserved**, then set state.reservation_id = {{reservation_id}} and go to step 2
  - Otherwise, Reply "That slot is unavailable." and **End**

2. Process Payment
  - call charge_payment(amount={{state.amount}}, method={{state.payment_method}})
  - If **paid**, then set state.payment_id = {{payment_id}} and go to step 3
  - Otherwise, call release_slot(reservation_id={{state.reservation_id}}), Reply "Payment failed.", and **End**

3. Send Confirmation
  - call send_confirmation(booking_id={{booking_id}}, email={{state.user_email}})
  - If **sent**, then go to step 4
  - Otherwise, call log_warning(code="confirmation_send_failed") and go to step 4

4. Complete
  - Reply "Booking confirmed. Reference: {{booking_id}}"
  - return to calling flow
```

## State Machine

Use when behavior depends on conversation state.

```markdown
## GLOBAL RULES
Valid states: GREETING, COLLECTING, PROCESSING, CONFIRMING, DONE.
State transitions happen only through explicit `set state.current = ...` actions.

## MAIN FLOW: STATE_MACHINE
1. Check State
  - If **state.current == "GREETING"**, then Proceed GREETING_SUB_FLOW
  - If **state.current == "COLLECTING"**, then Proceed DATA_COLLECTION_SUB_FLOW
  - If **state.current == "PROCESSING"**, then Proceed PROCESSING_SUB_FLOW
  - If **state.current == "CONFIRMING"**, then Proceed CONFIRMATION_SUB_FLOW
  - Otherwise, set state.current = "GREETING" and Proceed GREETING_SUB_FLOW
```

## Progressive Disclosure

Use when the agent must present complex information without overwhelming the user.

```markdown
5. Present Results
  - Present {{state.results.top_3}}
  - Reply "Would you like details on any of these, or should I show more?"
  - If **user_selects_item**, then call get_details(item_id={{selected_item_id}}) and go to step 6
  - If **user_wants_more AND state.result_page < 3**, then set state.result_page = {{state.result_page + 1}} and repeat step 5
  - Otherwise, go to step 7
```
