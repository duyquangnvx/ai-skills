# The Tool Layer: The Standard

Applies to tool scoping, names, schemas, descriptions, responses, and errors. These are strong defaults, not universal laws; verify important tradeoffs in the target runtime.

## Contents

- Shape tools around workflows
- Make tool contracts self-explanatory
- Design responses for the agent reader
- Bound context before the runtime does
- Answer with the new state
- Make errors actionable
- Schema vs prompt ownership
- Partial updates
- Keep handlers thin
- Server-side validation
- A cost ladder over the same data
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

Consolidation is a claim about **call shape**, never about how long the result may be held. A bundled response routinely mixes a stable identity with volatile state, so stamp per field rather than per response, and decide separately — by volatility, in `context-lifecycle.md` — which of those fields may sit in context and which must be re-fetched at the point of use.

Grouping near-identical sibling actions behind one tool with an `action` parameter is a good default — `pr_manage(action: "create" | "review", ...)` beats three tools differing only in verb, because fewer, more capable tools reduce selection ambiguity. Consolidation also has a correctness argument beyond efficiency: a sequence of writes that must be coherent should be one call, because a rejection partway through a sequence leaves the earlier writes applied.

**Consolidate along axes the model chooses well — which entity, which field. Split along axes where a wrong choice is unrecoverable or unbudgeted.**

```text
Good split (wrong choice is unrecoverable):
- update_scene(scene_id, updates)
- delete_scene(scene_id, dry_run=true)

Risky merge (destructive hidden behind a mode):
- mutate_scene(scene_id, operation, payload)   # "operation" includes delete
```

Safety class is the clearest case of unrecoverable, and a merged tool inherits the scariest gate any of its actions needs while making a read-only annotation impossible. But the criterion reaches further than safety: a ten-minute expensive backfill does not belong behind the same name as a cheap query, and neither do operations with different authorization scopes.

The mechanism behind all of these is that **permission, cost expectation, and annotation attach to the tool name, not to its arguments.** Allow-listing a merged tool because its cheap read is harmless silently allow-lists everything else the mode parameter can reach, and no amount of description text narrows that grant. So the practical question is not "are these the same kind of operation" but "would I grant them together" — and tool count is the wrong thing to minimize anyway. Minimize ambiguity per tool.

Overlap test: if a human engineer cannot say which tool to use in one sentence, the agent cannot either. Keep the active set small — cross-vendor guidance suggests under ~20 tools per turn — and namespace beyond that.

Over-consolidation is the opposite failure. When one tool serves unrelated use cases, the failure moves from tool *selection* to tool *parameterization*: the model can no longer tell which combination of parameters is valid. Remedies before splitting: sensible defaults, format presets that group related options, an `options` object for the rarely-used tail.

When the data layer is legible and the model strong, a few primitive tools can beat many specialized ones — see `architecture.md`.

## Make tool contracts self-explanatory

Names read clearly in a trace. Prefer intent and domain over implementation:

```text
Good: github_search_issues, billing_refund_payment, scene_update
Weak: get_data, update, parseAndInsertNodes
```

Use consistent service or domain prefixes when many tools are loaded. Prefix versus suffix order can matter by model and runtime, so pick a convention and test it rather than treating one style as universal.

Consistency extends across the whole catalog: one name per concept (`customer_id` everywhere, never `id` in one tool and `identifier` in another); one pattern for boolean options (`include_history`, `include_metadata`, `exclude_archived`); the same verbosity enum everywhere.

When referencing tools in prompts, use fully qualified names (`ServerName:tool_name`). With multiple servers loaded, unqualified names can collide or fail to resolve; audit for collisions when adding a server.

The description is the highest-leverage surface in the contract — evals rank it the single largest factor in tool performance, above naming and schema. Lead with what the tool does, then when to call it and when not, input conventions and defaults, side effects, and how it differs from its siblings. Where state has a lifetime, put that lifetime in the description so it enters context alongside the handle the model is carrying. Add schema-validated input examples for format-sensitive tools, and use strict schemas, where the runtime supports them.

## Design responses for the agent reader

Responses become context. Lead with human-readable, task-relevant fields — labels, slugs, short refs — and include raw IDs only where follow-up calls need them:

```json
// Low signal
{ "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "thread_ts": "1234567890.123" }

// Higher signal
{ "label": "Jane Chen in #product-launch", "last_message_at": "2h ago", "ref": "thread_7" }
```

Cryptic identifiers as the main reasoning surface increase hallucinated references.

Where a value can change under the agent, say when the response was true. An undated value reads as present tense forever, and a stamp is the only lever the agent has for reasoning about its own staleness.

Use `response_format` only where verbosity meaningfully varies — concise for confirmations and follow-ups, detailed for decisions needing the full record — and document in the description when to use each. Do not add it to tiny tools where it only expands the schema.

Response format has no universal winner. JSON, XML, Markdown, and plain text can all work. Choose the simplest shape that preserves structure and avoids awkward escaping.

## Bound context before the runtime does

Provider or client output caps are backstops, not design. **Any dimension that can grow needs an agent-visible control, and any bounded response must describe its own incompleteness** — the second half is what makes truncation safe, because a response that silently omits looks identical to one that had nothing more to give.

Growth dimensions worth controlling: result count, nesting depth, per-item fan-out, history length, and expansion of linked records.

```json
{
  "results": [/* 50 items */],
  "truncated": true,
  "next": { "cursor": "abc123" },
  "hint": "Narrow with status or created_after, or pass cursor to continue."
}
```

For very large payloads, write the content to a file and return the path instead of the body.

## Answer with the new state

A write that returns `{ "ok": true }` leaves the agent's belief behind its own action, and the agent's next move is either to re-read what it just did or to reason from the pre-write copy still in its context. Return the post-write state instead — it costs one response body and removes a whole class of failure:

```json
// Weak
{ "ok": true }

// Better
{ "scene": { "id": "arrival", "title": "...", "beats": [...] }, "version": 47 }
```

For writes that others can race, take the version the agent read as a required argument and refuse the write before applying it when the version no longer matches. Required rather than optional: an optional precondition protects only the callers that remember it, and the model is exactly the caller that will not. Where the runtime carries no transport-level mechanism for this, the token rides in the tool arguments, which means it passes through the model — so keep it short, opaque, and adjacent to the value it validates.

## Make errors actionable

Errors serve two audiences — developers debugging and agents recovering — and the agent is the primary one. Every error says what went wrong and what to change before retrying.

```json
{
  "error": "Unknown scene_id 'scene_99'.",
  "valid_scene_ids": ["opening", "arrival", "choice_a"],
  "hint": "Call list_scenes() if you need the current scene list."
}
```

For richer catalogs, a structured shape pays off:

```json
{
  "error": {
    "code": "STALE_WRITE",
    "message": "Scene 'arrival' changed since the version you read (41 → 47).",
    "current": { "title": "...", "beats": [...] },
    "applied": "none",
    "resolution": "Reapply your change against the state included here.",
    "retryable": true
  }
}
```

Four properties do the work:

- **Say what was applied.** A conflict from a multi-entity write may arrive after part of it committed. "Retry" against a partially applied write re-fires whatever already succeeded — a second notification, a second charge. State `applied` explicitly rather than leaving the agent to infer that a conflict means nothing happened.
- **Set retryability server-side.** It is a fact about the failure, not something the agent should derive from the word "conflict" or from a retry count it keeps itself.
- **Carry the current state.** Recovery then costs no extra round trip, and the correction arrives at the one moment with guaranteed attention: an announcement can be ignored, a refused write cannot.
- **Distinguish "retry this" from "stop".** A conflict caused by someone else's change is an escalation signal — see `context-lifecycle.md`. Authorization failures are terminal and must not read as solvable; `trust-and-safety.md` covers why.

Common cases: validation errors state received versus expected plus a fix; rate limits state the wait; not-found suggests a verification step. Only include valid values when safe — for permissions or sensitive resources, return a non-enumerating error.

## Schema vs prompt ownership

The tool schema owns field names and types, required versus optional, enums and structured output shape, per-field descriptions with concrete format examples where the format is non-obvious (`"CUST-######, e.g. CUST-000001"`, `"YYYY-MM-DD"`), and defaults that reflect the common case so the agent can safely omit parameters.

Every parameter is a decision delegated to the model. A value the model cannot reliably know — the current user, tenant, project scope — is not a parameter: resolve it in the handler from session or runtime context and keep it out of the schema, even when the backend API requires it. The model can no longer hallucinate an identifier software already knows, the schema stays small and cache-stable, and a manipulated call cannot reach another tenant's scope.

These rules apply to any schema the model writes against. Structured-output response schemas are the same surface: per-field descriptions steer generation exactly as parameter descriptions steer calls, and a vague field name yields a vague field value.

The tool description is a model-facing prompt, not human documentation — drop file paths, change history, implementation notes, and how-it-works detail. Return shape belongs in the schema, not restated as prose.

The developer or system prompt owns cross-tool workflow order, disambiguation between overlapping tools, approval choreography, domain concepts that are not field definitions, and tone. Duplicating field schemas in the prompt costs tokens and creates drift.

## Partial updates

```text
Better: update_scene(scene_id, updates: Partial<Scene>)
Riskier: update_scene(scene_id, scene: Scene)
```

Partial updates reduce what the agent must reconstruct and let the server preserve omitted fields — which also means the agent cannot silently revert a field it never read. For deeply nested objects a constrained patch format may help, but pointer-style paths add another thing the model can get wrong.

## Keep handlers thin

A tool parses and validates input, delegates to existing domain code, and shapes the result for the agent. Business rules do not live in the handler: thin handlers keep logic testable outside the agent and let you rename, split, or merge tools freely.

## Server-side validation

Any deterministic check belongs in software: identifier existence, enum validity for the current object, allowed state transitions, permissions, freshness preconditions. Each of these has an unambiguous answer at call time, and a rule in prose asking the model to respect one is a rule it will occasionally decide around.

For permissions, prose is neither the gate nor the map. The handler enforces regardless of what the prompt says. And rather than describing who may do what, filter tool exposure per session: a role that cannot use a tool should not see it in the tool list. Fine-grained denials the toolset cannot express surface as actionable, non-enumerating errors.

Dynamic per-request enums can prevent invalid references in strict runtimes at some cost to prompt-cache reuse. Use them where the reliability gain beats the cost; otherwise rely on server validation plus good errors.

## A cost ladder over the same data

Give the agent several ways into the same data at different costs, cheap and broad to expensive and narrow, so it can spend proportionally to what it needs:

- `overview` / `orient`: counts, top-level refs, schema version, warnings.
- `list_*`: shallow labels and refs.
- `search_*`: keyword or semantic lookup.
- `get_*`: full detail by ref.
- `diff` / `history`: what changed, and when.
- `validate`: read-only structural and reference checks after edits.

Not every domain needs every rung, and domains with expensive reads earn others — a dry-run preview, a cost estimate before a large fetch. Document the usual call pattern as guidance, not as a mandate.

## Agents as tools

Where sub-agents are exposed as callable tools, the description standard above applies unchanged. Two specifics: describe what the sub-agent returns, in shape and level of detail, so the caller can plan around it without a verification call; and treat the task argument as the entire briefing, since the sub-agent starts without the caller's conversation. A one-line task produces a sub-agent that rediscovers context the caller already had.

Where the spawn is ad-hoc and there is no registered description to hold it, the return contract moves into the brief and becomes one of its required parts. An unspecified return shape is not an omission the sub-agent will fill in consistently — a capable model picks a reasonable shape and a different one each time, and a caller with no declared shape cannot even detect the mismatch. State the required parts in order, including what to return when the result is empty or the work was blocked, since those are where shapes diverge most and where a guessing caller does the most damage.

## Descriptions rot

Parameters get added, return formats change, error codes shift, and the prose stops matching behavior. Version descriptions with the tool, review them in the same change that touches the API, and re-run tool evals after meaningful edits. A stale description misroutes the agent more quietly than a broken schema.

## Review checklist

- [ ] Each tool maps to a real workflow; overlapping tools have a one-sentence disambiguation.
- [ ] Splits fall where a wrong choice is unrecoverable or unbudgeted, never behind a mode parameter.
- [ ] Naming, parameters, and enums are consistent across the catalog; namespaced when large.
- [ ] Every description carries when-to-call, conventions, side effects, sibling boundaries — and nothing meant for humans.
- [ ] The schema is the source of truth for fields, enums, and return shape.
- [ ] Responses are bounded, human-readable first, and state their own incompleteness.
- [ ] Mutations return the post-write state; racy writes require the version the agent read.
- [ ] Every error says what was applied, whether to retry, and what to change.
- [ ] No parameter asks the model for what the handler can resolve from session context.
- [ ] Handlers are thin: validate, delegate, shape.
