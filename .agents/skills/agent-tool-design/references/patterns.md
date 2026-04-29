# Tool Design Patterns

Use this reference when the main checklist is too compressed. These are design heuristics, not universal laws; verify important tradeoffs with evals in the target runtime.

## 1. Choose Tools by Workflow

Agents do better with tools that match the work they need to perform, not tools copied one-for-one from backend endpoints.

Useful consolidation:

```text
Weak: list_users + list_events + create_event
Better: schedule_event(attendees, time_window, topic)

Weak: read_logs(limit=10000)
Better: search_logs(query, time_range, context_lines)

Weak: get_customer + list_transactions + list_notes
Better: get_customer_context(customer_ref, include_recent_activity=true)
```

Split tools when variants have different semantics, preconditions, side effects, or safety requirements:

```text
Good split:
- update_scene(scene_id, updates)
- delete_scene(scene_id, dry_run=true)

Risky merge:
- mutate_scene(scene_id, operation, payload)
```

The human-engineer test: if a developer cannot quickly explain which tool to call, the model probably cannot either.

## 2. Name and Namespace for Selection

Names are part of the prompt. Prefer intent and domain over implementation:

```text
Good: github_search_issues, billing_refund_payment, scene_update
Weak: get_data, update, parseAndInsertNodes
```

Use consistent service/domain prefixes when many tools are loaded. Prefix vs suffix order can matter by model and runtime, so pick a convention and test it rather than treating one style as universal.

## 3. Make Responses Easy for the Agent to Use

Tool responses are model context. Prefer high-signal fields that directly support the next decision.

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

Do not add this parameter to tiny tools where it only expands the schema.

Response format has no universal winner. JSON, XML, Markdown, and plain text can all work. Choose the simplest shape that preserves structure, avoids awkward escaping/counting, and performs well in evals.

## 4. Bound Context Before the Runtime Does

Provider or client output caps are backstops, not design. Add controls where responses can grow:

- Pagination with sensible defaults.
- Filters for query, type, date, owner, status, or range.
- Truncation that clearly says what was omitted.
- Narrow follow-up instructions in truncation messages.

Example:

```json
{
  "results": [/* 50 items */],
  "truncated": true,
  "next": { "cursor": "abc123" },
  "hint": "Narrow with status or created_after, or pass cursor to continue."
}
```

## 5. Make Errors Actionable

Opaque errors waste turns. Validation errors should tell the agent exactly what to fix.

```json
{
  "error": "Unknown scene_id 'scene_99'.",
  "valid_scene_ids": ["opening", "arrival", "choice_a"],
  "hint": "Call list_scenes() if you need the current scene list."
}
```

Only include valid values when safe; for permissions or sensitive resources, return a non-enumerating error.

## 6. Keep Schema and Prompt Separate

The tool schema should own:

- Field names and types.
- Required vs optional.
- Enums and structured output shape.
- Per-field descriptions.
- Tool-level description: what the tool does, when to call it, side effects, sibling-tool disambiguation. This is a model-facing prompt, not human documentation — drop file paths, change history, implementation notes, and "how it works" details.

The developer/system prompt should own:

- Cross-tool workflow order.
- Disambiguation between overlapping tools.
- Destructive-action confirmation policy.
- Domain concepts that are not field definitions.
- Tone and user-facing behavior.

Duplicating field schemas in the prompt costs tokens and creates drift.

## 7. Prefer Partial Updates

For editing structured state:

```text
Better: update_scene(scene_id, updates: Partial<Scene>)
Riskier: update_scene(scene_id, scene: Scene)
```

Partial updates reduce the amount the agent must reconstruct and let the server preserve omitted fields. For deeply nested objects, a constrained patch format may be useful, but JSON Pointer-style paths add another thing the model can get wrong.

## 8. Validate References Server-Side

Any deterministic check belongs in software:

- Does this ID exist?
- Is this enum valid for the current object?
- Is this transition allowed from current state?
- Does the user have permission?

Dynamic per-request enums can prevent invalid references in strict runtimes, but they may reduce prompt-cache reuse. Use them when the reliability gain beats the cache cost; otherwise rely on server validation plus actionable errors.

## 9. Add Orient and Validate Tools When They Pay Off

Many editing domains benefit from:

- `overview` / `orient`: cheap counts, top-level refs, schema version, warnings.
- `list_*`: shallow labels and refs.
- `get_*`: full detail by ref.
- `search_*`: keyword or semantic lookup.
- `validate`: read-only structural and reference checks after edits.

Document the usual call pattern as guidance, not as a rigid mandate.
