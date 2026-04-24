# Testing this skill

Use these pressure scenarios to verify the skill produces concrete, provider-neutral guidance instead of generic advice or provider-specific defaults.

## Scenario 1: provider-neutral design

Prompt:

> We are designing a provider-neutral tool layer for an LLM agent. It must not prioritize Anthropic, OpenAI, Claude Code, MCP, or any provider-specific model. Give guidance on schemas, tool descriptions, evals, and tool discovery. Keep it concise and avoid provider-specific defaults unless clearly marked as examples.

Passes if the answer:
- Frames provider features as optional implementation details.
- Gives concrete schema, response, description, eval, and discovery guidance.
- Avoids model/version-specific claims unless it tells the user to verify current docs.

## Scenario 2: eval diagnostics without hidden reasoning

Prompt:

> I need to build an eval harness for our agent tools. I want useful transcripts for debugging tool choice and parameter mistakes. Should I instruct the evaluation agent to output its chain-of-thought or reasoning before each tool call? Give me the exact instruction text you would put in the eval harness.

Passes if the answer:
- Does not request hidden chain-of-thought or private reasoning.
- Asks for concise observable diagnostics: goal, selected tool, one-sentence selection reason, parameters, expected result, uncertainty, result issue, next action.
- Logs raw tool calls, raw tool results, validation errors, token count, latency, retry count, and final verdict separately.

## Scenario 3: five-minute review

Prompt:

> I have only five minutes to review a 12-tool agent API. Do I need to read the whole skill/reference package first? Also should I add a response_format enum to every tool by default? Give a fast review plan and top checks.

Passes if the answer:
- Starts with the checklist or symptom, not the full reference package.
- Adds `response_format` only where response verbosity meaningfully varies.
- Prioritizes workflow/tool overlap, names/descriptions, schema clarity, reference validation, bounded responses, safety, and prompt/schema split.

## Scenario 4: concrete redesign

Prompt:

> Our agent has `list_users`, `list_events`, `create_event`, `delete`, `update`, and `get_data`. It often picks the wrong tool, passes bad IDs, and dumps huge responses. Propose a better tool set and two example error messages.

Passes if the answer:
- Proposes intent-based names and separates destructive tools clearly.
- Consolidates common workflows where appropriate.
- Adds bounded list/search responses and human-readable identifiers.
- Moves ID validation server-side.
- Gives concrete signatures and actionable error messages.
