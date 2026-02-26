# FPL Design Patterns

Reusable patterns for common agent scenarios. Copy and adapt these into your flows.

## Authentication Pattern

Use when: Agent must verify user identity before granting access to sensitive operations.

```
#### AUTHENTICATION ROUTINE
1. Request Identifier
  - Reply "May I have your {{identifier_type}}?"

2. Verify Identifier
  - call verify_identity(id={{user_input}}, type={{identifier_type}})
  - If **verified**, then set state.authenticated = true
  - If **not_found**, then reply "I couldn't find that {{identifier_type}}" and **End**
  - If **locked**, then reply "Account locked. Please contact support." and **End**

3. Secondary Verification (if required)
  - Ask security question or OTP
  - call verify_secondary(answer={{user_input}})
  - If **failed**, then call end_session("AUTH_FAILED") and **End**
```

## Retry with Backoff Pattern

Use when: An operation might fail temporarily (API calls, user input validation).

```
#### RETRY ROUTINE
**DO:**
  - Attempt operation
  - call {{operation}}({{params}})
**LOOP UNTIL:**
  - Operation succeeds
  - Failed **3 times** → reply "Unable to complete after multiple attempts" and **Proceed** FALLBACK_FLOW
```

## Escalation Pattern

Use when: Agent reaches limits of its capability or user explicitly requests human assistance.

```
## TRIGGER FLOW: ESCALATION_FLOW
*Trigger*: user says matching "manager|supervisor|human|real person|speak to someone"

1. Confirm Escalation
  - Reply "I'll connect you with a team member. Before I do, can I get a brief summary of your issue?"

2. Prepare Handoff
  - call create_ticket(summary={{conversation_summary}}, priority={{calculated_priority}})
  - call transfer_to_agent(ticket_id={{ticket_id}}, department={{department}})
  - Reply "I've created ticket #{{ticket_id}} and you'll be connected shortly."
  - **End**
```

## Conditional Escalation (non-trigger):
```
- If **sentiment_negative** AND **failed_resolution_attempts >= 2**, then **Proceed** ESCALATION_FLOW
- If **query_complexity == "high"** AND **confidence < 0.6**, then **Proceed** ESCALATION_FLOW
```

## Data Collection Pattern

Use when: Agent needs to collect multiple pieces of information from user in sequence.

```
#### COLLECT_INFO ROUTINE
1. Ask Field A
  - Reply "What is your {{field_a_label}}?"
  - Validate: {{field_a_validation}}
  - If **invalid**, then reply "Please provide a valid {{field_a_label}}" and retry (max 2)

2. Ask Field B
  - Reply "And your {{field_b_label}}?"
  - Validate: {{field_b_validation}}
  - If **invalid**, then retry (max 2)

3. Confirm Collected Data
  - Reply "Let me confirm: {{field_a}} = {{value_a}}, {{field_b}} = {{value_b}}. Is this correct?"
  - If **user_confirms**, then proceed to next step
  - If **user_corrects**, then go back to the corrected field
```

## Try-Catch Pattern

Use when: Tool calls or external operations may fail unpredictably.

```
3. Execute Operation
  - call {{operation}}({{params}})
  - If **success**, then proceed to step 4
  - If **timeout**, then reply "System is taking longer than expected. Let me try again." and retry (max 1)
  - If **error_recoverable**, then call log_error({{error}}) and **Proceed** ALTERNATIVE_FLOW
  - If **error_fatal**, then reply "I encountered an issue. Let me connect you with support." and **Proceed** ESCALATION_FLOW
```

## Confirmation Before Action Pattern

Use when: Irreversible or high-impact operations require explicit user consent.

```
4. Confirm Before Execute
  - Reply "I'm about to {{action_description}}. This will {{impact_description}}. Shall I proceed?"
  - If **user_confirms**, then call {{action}}({{params}})
  - If **user_declines**, then reply "No problem. What would you like to do instead?" and **Proceed** MAIN FLOW
```

## Saga Pattern (Multi-step Transaction)

Use when: Multiple operations must succeed together, with rollback if any fails.

```
#### BOOKING_SAGA ROUTINE
1. Reserve Slot
  - call reserve_slot(date={{date}}, duration={{duration}})
  - If **failed**, then reply "Slot unavailable" and **End**

2. Process Payment
  - call charge_payment(amount={{amount}}, method={{payment_method}})
  - If **failed**, then call release_slot(reservation_id={{res_id}}) and reply "Payment failed" and **End**

3. Send Confirmation
  - call send_confirmation(booking_id={{booking_id}}, email={{user_email}})
  - If **failed**, then call log_warning("confirmation_send_failed") (do NOT rollback — booking is valid)

4. Complete
  - Reply "Booking confirmed! Reference: {{booking_id}}"
  - **End**
```

Each step includes rollback for previous steps if it fails. Step 3 shows a deliberate decision NOT to rollback — not all failures require undo.

## State Machine Pattern

Use when: Agent behavior depends on which "state" the conversation is in.

```
## GLOBAL RULES
Agent tracks current state. Valid states: GREETING, COLLECTING, PROCESSING, CONFIRMING, DONE.
State transitions only happen through explicit **set state** actions.

## MAIN FLOW: STATE_MACHINE
1. Check State
  - If **state == GREETING**, then **Proceed** GREETING_SUB_FLOW
  - If **state == COLLECTING**, then **Proceed** DATA_COLLECTION_SUB_FLOW
  - If **state == PROCESSING**, then **Proceed** PROCESSING_SUB_FLOW
  - If **state == CONFIRMING**, then **Proceed** CONFIRMATION_SUB_FLOW
```

## Progressive Disclosure Pattern

Use when: Agent needs to present complex information without overwhelming the user.

```
5. Present Results
  - Reply with top 3 results summary
  - Reply "Would you like more details on any of these?"
  - If **user_selects_item**, then call get_details(item_id={{selected}}) and present full details
  - If **user_wants_more**, then present next 3 results
  - Otherwise, proceed to next step
```