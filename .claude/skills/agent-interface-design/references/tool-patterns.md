# Tool Design Patterns: Worked Examples

The rules live in SKILL.md (Designing the Tool Layer). This file shows them applied. These are design heuristics, not universal laws; verify important tradeoffs with evals in the target runtime.

## Contents

- Consolidation and splitting
- Naming and namespacing
- Response shaping
- Bounding context
- Actionable errors
- Schema vs prompt ownership
- Partial updates
- Server-side validation
- Orient and validate tools
- Descriptions rot

## Consolidation and splitting

Consolidate around the work, not the endpoints:

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

When a tool drifts toward 8–10+ parameters serving unrelated use cases, the failure moves from tool *selection* to tool *parameterization*. Remedies before splitting: sensible defaults, format presets that group related options, an `options` object for the rarely-used tail.

## Naming and namespacing

Names are part of the prompt. Prefer intent and domain over implementation:

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

## Response shaping

```json
// Low signal
{ "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "thread_ts": "1234567890.123" }

// Higher signal
{ "label": "Jane Chen in #product-launch", "last_message_at": "2h ago", "ref": "thread_7" }
```

Use natural-language labels, stable slugs, or short references where possible. Include raw IDs when the next tool requires them, but avoid making cryptic IDs the main thing the agent must reason over.

Use `response_format` only when response verbosity meaningfully varies:

```typescript
type ResponseFormat = "concise" | "detailed";
```

Concise suits confirmations and follow-up calls after an initial retrieval; detailed suits decisions that need the full record. Document in the description when to use each. Do not add this parameter to tiny tools where it only expands the schema.

Response format has no universal winner. JSON, XML, Markdown, and plain text can all work. Choose the simplest shape that preserves structure, avoids awkward escaping/counting, and performs well in evals.

## Bounding context

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

## Actionable errors

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

The tool description is a model-facing prompt, not human documentation — drop file paths, change history, implementation notes, and "how it works" details. Return shape belongs in the schema, not restated as prose or long code examples.

The developer/system prompt should own:

- Cross-tool workflow order.
- Disambiguation between overlapping tools.
- Destructive-action confirmation policy.
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

## Server-side validation

Any deterministic check belongs in software: ID existence, enum validity for the current object, allowed state transitions, permissions.

Dynamic per-request enums can prevent invalid references in strict runtimes, but they may reduce prompt-cache reuse. Use them when the reliability gain beats the cache cost; otherwise rely on server validation plus actionable errors.

## Orient and validate tools

Many editing domains benefit from:

- `overview` / `orient`: cheap counts, top-level refs, schema version, warnings.
- `list_*`: shallow labels and refs.
- `get_*`: full detail by ref.
- `search_*`: keyword or semantic lookup.
- `validate`: read-only structural and reference checks after edits.

Document the usual call pattern as guidance, not as a rigid mandate.

## Descriptions rot

Descriptions rot: parameters get added, return formats change, error codes shift, and the prose stops matching behavior. Version descriptions with the tool, review them in the same change that touches the API, and re-run tool evals after meaningful edits. A stale description misroutes the agent more quietly than a broken schema.
