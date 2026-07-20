# The Tool Layer: The Standard

Applies to tool scoping, names, schemas, descriptions, responses, and errors. These are design rules with strong defaults, not universal laws; verify important tradeoffs with evals in the target runtime (see `evals-and-safety.md`).

## Contents

- Shape tools around workflows
- Make tool contracts self-explanatory
- Design responses for the agent reader
- Bound context before the runtime does
- Make errors actionable
- Schema vs prompt ownership
- Partial updates
- Keep handlers thin
- Server-side validation
- Orient and validate tools
- Agents as tools
- Descriptions rot

## Shape tools around workflows

Do not mirror backend endpoints. Consolidate chains the agent repeatedly performs:

```text
Weak: list_users + list_events + create_event
Better: schedule_event(attendees, time_window, topic)

Weak: read_logs(limit=10000)
Better: search_logs(query, time_range, context_lines)

Weak: get_customer + list_transactions + list_notes
Better: get_customer_context(customer_ref, include_recent_activity=true)
```

Grouping near-identical sibling actions behind one tool with an `action` parameter is a vendor-endorsed default — `pr_manage(action: "create" | "review", ...)` beats three tools that differ only in verb, because fewer, more capable tools reduce selection ambiguity. Draw the line at safety class:

```text
Good split (different safety class):
- update_scene(scene_id, updates)
- delete_scene(scene_id, dry_run=true)

Risky merge (destructive hidden behind a mode):
- mutate_scene(scene_id, operation, payload)   # "operation" includes delete
```

A merged tool inherits the scariest confirmation gate any of its actions needs, and a read-only annotation becomes impossible. Keep reads, reversible writes, and destructive operations separate even when consolidating everything else.

Overlap test: if a human engineer cannot say which tool to use in one sentence, the agent cannot either. Keep the active set small — cross-vendor guidance suggests under ~20 tools per turn; namespace beyond that.

Over-consolidation is the opposite failure. When a tool drifts toward 8–10+ parameters serving unrelated use cases, the failure moves from tool *selection* to tool *parameterization*. Remedies before splitting: sensible defaults, format presets that group related options, an `options` object for the rarely-used tail.

When the data layer is legible and the model strong, a few primitive tools can beat many specialized ones: see `architectural-reduction.md`.

## Make tool contracts self-explanatory

Names read clearly in a trace. Prefer intent and domain over implementation:

```text
Good: github_search_issues, billing_refund_payment, scene_update
Weak: get_data, update, parseAndInsertNodes
```

Use consistent service/domain prefixes when many tools are loaded. Prefix vs suffix order can matter by model and runtime, so pick a convention and test it rather than treating one style as universal.

Consistency extends to parameters and enums across the whole catalog:

- One name per concept: always `customer_id`, never `id` in one tool and `identifier` in another.
- Boolean options follow one pattern: `include_history`, `include_metadata`, `exclude_archived`.
- Verbosity enums match everywhere: `"concise" | "detailed"`, not `"short" | "long"` in some tools.

When referencing MCP tools in prompts, use fully qualified names (`ServerName:tool_name`, e.g. `GitHub:create_issue`). With multiple servers loaded, unqualified names can collide or fail to resolve; audit for collisions when adding a new server.

The description is the highest-leverage surface in the contract — vendor evals rank it the single most important factor in tool performance. Aim for at least 3–4 sentences leading with what the tool does, when to call it (and when not), input conventions and defaults, side effects, and how it differs from sibling tools. Add schema-validated input examples for format-sensitive tools where the runtime supports them, and use strict schemas where the runtime supports them.

## Design responses for the agent reader

Responses become context. Lead with human-readable, task-relevant fields — labels, slugs, short refs — and include raw IDs only where follow-up calls need them:

```json
// Low signal
{ "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "thread_ts": "1234567890.123" }

// Higher signal
{ "label": "Jane Chen in #product-launch", "last_message_at": "2h ago", "ref": "thread_7" }
```

Cryptic identifiers as the main reasoning surface increase hallucinated references.

Use `response_format` only when response verbosity meaningfully varies:

```typescript
type ResponseFormat = "concise" | "detailed";
```

Concise suits confirmations and follow-up calls after an initial retrieval; detailed suits decisions that need the full record. Document in the description when to use each. Do not add this parameter to tiny tools where it only expands the schema.

Response format has no universal winner. JSON, XML, Markdown, and plain text can all work. Choose the simplest shape that preserves structure, avoids awkward escaping/counting, and performs well in evals.

## Bound context before the runtime does

Provider or client output caps are backstops, not design. Add controls where responses can grow:

- Pagination with sensible defaults.
- Filters for query, type, date, owner, status, or range.
- Truncation that clearly says what was omitted.
- Narrow follow-up instructions in truncation messages.
- For very large payloads, a file-reference mode: write the content to a file and return the path instead of the body.

Example:

```json
{
  "results": [/* 50 items */],
  "truncated": true,
  "next": { "cursor": "abc123" },
  "hint": "Narrow with status or created_after, or pass cursor to continue."
}
```

## Make errors actionable

Errors serve two audiences — developers debugging and agents recovering — and the agent is the primary one: every error must say what went wrong and what to change before retrying.

```json
{
  "error": "Unknown scene_id 'scene_99'.",
  "valid_scene_ids": ["opening", "arrival", "choice_a"],
  "hint": "Call list_scenes() if you need the current scene list."
}
```

For richer catalogs, a structured error shape pays off:

```json
{
  "error": {
    "code": "INVALID_CUSTOMER_ID",
    "message": "Customer ID 'CUST-123' does not match required format",
    "expected_format": { "pattern": "CUST-######", "example": "CUST-000001" },
    "resolution": "Provide a customer ID matching pattern CUST-######",
    "retryable": true
  }
}
```

Common cases: validation errors state received vs expected plus a fix; rate limits state wait time; not-found suggests a verification step. Only include valid values when safe; for permissions or sensitive resources, return a non-enumerating error.

## Schema vs prompt ownership

The tool schema should own:

- Field names and types.
- Required vs optional.
- Enums and structured output shape.
- Per-field descriptions, with concrete format examples where the format is non-obvious (`"CUST-######, e.g. CUST-000001"`, `"YYYY-MM-DD"`).
- Sensible defaults that reflect the common case, so the agent can omit parameters safely.

Every parameter is a decision delegated to the model. A value the model cannot reliably know — the current user, tenant, project scope — is not a parameter: resolve it in the handler from session or runtime context (injected arguments) and keep it out of the schema, even when the backend API requires it. The model can no longer hallucinate an ID software already knows, the schema stays small and cache-stable, and a manipulated call cannot reach another tenant's scope.

These rules apply to any schema the model writes against, not just tool inputs. Structured-output schemas (`generateObject`-style response formats) are the same surface: per-field descriptions steer generation exactly as parameter descriptions steer calls, and a vague field name yields a vague field value.

The tool description is a model-facing prompt, not human documentation — drop file paths, change history, implementation notes, and "how it works" details. Return shape belongs in the schema, not restated as prose or long code examples.

The developer/system prompt should own:

- Cross-tool workflow order.
- Disambiguation between overlapping tools.
- Destructive-action approval choreography — the gate itself belongs in the runtime when one exists (see `evals-and-safety.md`, One Approval Gate).
- Domain concepts that are not field definitions.
- Tone and user-facing behavior.

Duplicating field schemas in the prompt costs tokens and creates drift.

## Partial updates

For editing structured state:

```text
Better: update_scene(scene_id, updates: Partial<Scene>)
Riskier: update_scene(scene_id, scene: Scene)
```

Partial updates reduce the amount the agent must reconstruct and let the server preserve omitted fields. For deeply nested objects, a constrained patch format may be useful, but JSON Pointer-style paths add another thing the model can get wrong.

## Keep handlers thin

A tool parses and validates input, delegates to existing domain code, and shapes the result for the agent. Business rules do not live in the handler: thin handlers keep logic testable outside the agent and let you rename, split, or merge tools freely. (Workflow shaping decides what each tool exposes; this rule keeps logic out of the plumbing.)

## Server-side validation

Any deterministic check belongs in software: ID existence, enum validity for the current object, allowed state transitions, permissions. Prompts are for judgment, never for enforcing what software can enforce.

For permissions, prose is neither the gate nor the map. The handler enforces regardless of what the prompt says — a prompt is not a security boundary. And instead of describing who may do what, filter tool exposure per session: a role that cannot use a tool should not see it in the tool list. Fine-grained denials the toolset cannot express (per-resource, per-row) surface as actionable, non-enumerating errors. Decide the toolset at session start — swapping it mid-session invalidates the prompt cache.

Dynamic per-request enums can prevent invalid references in strict runtimes, but they may reduce prompt-cache reuse. Use them when the reliability gain beats the cache cost; otherwise rely on server validation plus actionable errors.

## Orient and validate tools

Many editing domains benefit from:

- `overview` / `orient`: cheap counts, top-level refs, schema version, warnings.
- `list_*`: shallow labels and refs.
- `get_*`: full detail by ref.
- `search_*`: keyword or semantic lookup.
- `validate`: read-only structural and reference checks after edits.

Document the usual call pattern as guidance, not as a rigid mandate.

## Agents as tools

Multi-agent runtimes expose sub-agents as callable tools, and the description standard above applies unchanged. Two specifics:

- Describe what the sub-agent returns — shape and level of detail — so the caller can plan around it without a verification call.
- The task argument is the sub-agent's entire briefing: it starts without the caller's conversation, so the call itself must carry the deliverable, the constraints, and any refs it needs. A one-line task produces a sub-agent that rediscovers context the caller already had.

## Descriptions rot

Descriptions rot: parameters get added, return formats change, error codes shift, and the prose stops matching behavior. Version descriptions with the tool, review them in the same change that touches the API, and re-run tool evals after meaningful edits. A stale description misroutes the agent more quietly than a broken schema.

## Review checklist

- [ ] Each tool maps to a real workflow; overlapping tools have a one-sentence disambiguation.
- [ ] Destructive operations are separate tools, never modes of a merged tool.
- [ ] Naming, parameters, and enums are consistent across the catalog; namespaced when large.
- [ ] Every description carries when-to-call, conventions, side effects, sibling boundaries — and nothing meant for humans.
- [ ] The schema is the source of truth for fields, enums, and return shape.
- [ ] Responses are bounded and human-readable first; truncation says how to narrow.
- [ ] Every error says what to change before retrying.
- [ ] References are validated server-side.
- [ ] No parameter asks the model for what the handler can resolve from session context.
- [ ] Handlers are thin: validate, delegate, shape.
- [ ] Sub-agent tools state what they return, and their task argument carries the full briefing.
