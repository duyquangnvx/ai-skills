---
name: agent-tool-design
description: Use when designing, reviewing, or refactoring an LLM agent's tool layer: function calls, MCP servers, tool schemas, tool descriptions, response formats, safety annotations, prompt/schema boundaries, wrong tool calls, hallucinated IDs, oversized responses, partial updates, or one-tool-vs-many-tool decisions.
---

# Agent Tool Design

Design the agent-computer interface (ACI): the tool names, schemas, descriptions, responses, validation, and safety boundaries that sit between deterministic software and a non-deterministic model.

Core principle: tools are not just backend endpoints. They are context and action surfaces for an agent with limited attention, imperfect tool choice, and imperfect argument construction.

## Start Here

Classify the user's problem, then use the matching checks:

| Symptom | Check first |
| --- | --- |
| Wrong tool call | Tool overlap, namespacing, description boundaries |
| Bad arguments | Schema strictness, parameter names, examples, validation errors |
| Hallucinated IDs | Human-readable identifiers, reference validation, current-state enums |
| Huge responses | Filtering, pagination, truncation, concise/detail modes |
| Prompt drift | Schema as source of truth; remove duplicated field docs |
| Risky action | Destructive naming, confirmation gates, trust boundaries |
| Unclear design tradeoff | Write eval tasks and compare alternatives |

## Design Rules

### 1. Shape tools around workflows

Do not mirror every REST/API endpoint by default. Consolidate chains the agent repeatedly performs, such as `schedule_event` instead of `list_users` + `list_events` + `create_event`. Split tools when variants have different semantics, preconditions, side effects, or validation needs.

Test for overlap: if a human engineer cannot say which tool to use in one sentence, the agent will likely struggle too.

### 2. Make tool contracts self-explanatory

Use names and parameters that read clearly in a trace: `billing_refund_payment`, `scene_id`, `include_archived`. Tool descriptions should state what the tool does, when to call it, important input conventions, side effects, and how it differs from sibling tools.

Keep cross-tool workflow and disambiguation in the developer/system prompt. Keep field names, required fields, enums, and return shape in the tool schema.

### 3. Design responses for the agent reader

Tool results become model context. Lead with human-readable, task-relevant fields; avoid making raw UUIDs the primary thing the agent must reason over. Use stable slugs, names, labels, or numbered IDs where possible, and include technical IDs only when follow-up calls need them.

For variable-size responses, provide bounded defaults and a small verbosity option only when useful, such as `response_format: "concise" | "detailed"`. Errors should be actionable: name the invalid field, show valid values when safe, and tell the agent how to retry.

### 4. Enforce what software can enforce

Do not rely on prompt rules for deterministic constraints. Validate IDs, enum membership, permissions, state transitions, destructive preconditions, and payload shape server-side. Return clear errors. Use strict schemas or structured outputs where the runtime supports them.

Prefer partial updates for structured edits: `update_scene(scene_id, updates)` or a narrow patch operation beats asking the agent to resend the whole object.

### 5. Treat tool safety as a session property

Name destructive tools plainly: `delete_scene`, `send_email`, `make_payment`. Add dry-run or preview modes for high-stakes actions.

Annotations such as read-only/destructive/idempotent/open-world are useful hints in runtimes that support them, but they are not security guarantees. Treat annotations from untrusted servers as untrusted. Watch for sessions combining private data, untrusted content, and external communication; require explicit user approval or runtime policy before exfiltration-capable actions after untrusted reads.

## Review Checklist

- [ ] Each tool maps to a real workflow or measured need.
- [ ] Overlapping tools have a one-sentence disambiguation rule.
- [ ] Namespacing is consistent across services or domains.
- [ ] Tool schema is the source of truth for fields, required values, enums, and return shape.
- [ ] Descriptions put key usage criteria and argument conventions up front.
- [ ] Edit tools use partial updates where practical.
- [ ] Reference fields are validated server-side with actionable errors.
- [ ] Responses are bounded, high-signal, and human-readable first.
- [ ] Truncation tells the agent how to narrow or page.
- [ ] Safety gates cover destructive actions and lethal-trifecta combinations.
- [ ] Evals track accuracy, tool calls, tokens, latency, invalid calls, and final outcome.

## Output Pattern

For reviews, be concrete:

```text
Symptom:
Likely cause:
Recommended tool/schema/response change:
Example signature or error:
Eval to verify:
```

For new designs, propose the smallest viable tool set, explain boundaries between tools, and list the first eval tasks that would prove the design works.

## References

Load deeper material only when needed:

- `references/patterns.md` - expanded design patterns and examples.
- `references/process.md` - eval loop, metrics, and safety/trust boundaries.
- `references/testing.md` - pressure scenarios for this skill.
- `references/sources.md` - verified source notes and links.
