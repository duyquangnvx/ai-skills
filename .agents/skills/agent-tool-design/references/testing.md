# Pressure Scenarios

Use these with `superpowers:writing-skills` when changing this skill. Baseline agents should commonly miss at least one expected behavior without the skill; agents with the skill should comply.

## 1. Provider-Neutral Tool Review

Prompt:

```text
We are designing a provider-neutral tool layer for an LLM agent. It must not prioritize Anthropic, OpenAI, Claude Code, MCP, or any provider-specific model. Give guidance on schemas, tool descriptions, evals, and tool discovery. Keep it concise and avoid provider-specific defaults unless clearly marked as examples.
```

Baseline failures to watch for:

- Treats MCP or one provider as the default architecture.
- Repeats generic "write clear descriptions" advice without concrete schema/response guidance.
- Makes version-specific claims without telling the user to verify current docs.

Expected with skill:

- Frames provider features as optional runtime details.
- Gives concrete schema, response, description, eval, and discovery guidance.
- Says to verify exact strict-schema/annotation/tool-search behavior in the target runtime.

## 2. Eval Diagnostics Without Hidden Reasoning

Prompt:

```text
I need to build an eval harness for our agent tools. I want useful transcripts for debugging tool choice and parameter mistakes. Should I instruct the evaluation agent to output its chain-of-thought or reasoning before each tool call? Give me the exact instruction text you would put in the eval harness.
```

Baseline failures to watch for:

- Requests hidden chain-of-thought.
- Logs only final answers, not tool calls and raw tool results.
- Omits metrics.

Expected with skill:

- Does not request hidden chain-of-thought or private reasoning.
- Asks for concise observable diagnostics: goal, selected tool, one-sentence selection reason, parameters, expected result, uncertainty, observed issue, next action.
- Logs raw tool calls, tool results, validation errors, token count, latency, retry count, and final verdict separately.

## 3. Five-Minute Review

Prompt:

```text
I have only five minutes to review a 12-tool agent API. Do I need to read the whole skill/reference package first? Also should I add a response_format enum to every tool by default? Give a fast review plan and top checks.
```

Baseline failures to watch for:

- Tells the user to read all references first.
- Adds `response_format` everywhere by default.
- Misses prompt/schema duplication or bounded responses.

Expected with skill:

- Starts with symptoms and checklist, not the full reference package.
- Adds `response_format` only where response verbosity meaningfully varies.
- Prioritizes workflow/tool overlap, names/descriptions, schema clarity, reference validation, bounded responses, safety, and prompt/schema split.

## 4. Concrete Redesign

Prompt:

```text
Our agent has list_users, list_events, create_event, delete, update, and get_data. It often picks the wrong tool, passes bad IDs, and dumps huge responses. Propose a better tool set and two example error messages.
```

Baseline failures to watch for:

- Renames tools cosmetically without changing workflow shape.
- Leaves `delete` ambiguous.
- Keeps unbounded list/get responses.
- Relies on prompt instructions to prevent bad IDs.

Expected with skill:

- Proposes intent-based names and separates destructive tools clearly.
- Consolidates common workflows where appropriate.
- Adds bounded list/search responses and human-readable identifiers.
- Moves ID validation server-side.
- Gives concrete signatures and actionable error messages.

## 5. Prompt Injection and Tool Safety

Prompt:

```text
Our agent can read private CRM data, scrape arbitrary webpages, and send emails. The email tool is annotated as non-destructive. Is that enough? What should the tool layer or runtime do?
```

Baseline failures to watch for:

- Treats annotation metadata as a security guarantee.
- Focuses only on the email tool in isolation.
- Suggests "tell the model not to leak data" as the main defense.

Expected with skill:

- Identifies the lethal-trifecta combination at session level.
- Treats annotations as hints, especially if server trust is unknown.
- Recommends least-authority sessions, tainting after untrusted reads, explicit approval before external communication, and hard runtime controls where possible.
