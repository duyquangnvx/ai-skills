# The Tool Layer: The Standard

Applies to tool scoping, names, schemas, descriptions, responses, and errors. These are strong defaults, not universal laws; verify important tradeoffs in the target runtime.

## Contents

- Where to cut the catalog
- Make tool contracts self-explanatory
- Design responses for the agent reader
- Bound context before the runtime does
- Answer with the new state
- Make errors actionable
- Schema vs prompt ownership
- Partial updates
- Server-side validation
- A cost ladder over the same data
- Agents as tools
- Descriptions rot

## Where to cut the catalog

Tools are shaped around workflows the agent repeatedly performs, not around backend endpoints. The hard question is where to cut, and one rule answers it: **consolidate along axes the model chooses well — which entity, which field. Split along axes where a wrong choice is unrecoverable or unbudgeted.**

Safety class is the clearest unrecoverable case, and hiding a delete behind `mutate_scene(operation, payload)` is the canonical error: the merged tool inherits the scariest gate any of its actions needs, and a read-only annotation becomes impossible. But the criterion reaches past safety. A ten-minute backfill does not belong behind the same name as a cheap query, and neither do operations under different authorization scopes.

The mechanism behind all of it: **permission, cost expectation, and annotation attach to the tool name, not to its arguments.** Allow-listing a merged tool because its cheap read is harmless silently allow-lists everything else the mode parameter can reach, and no description text narrows that grant. The practical question is therefore not "are these the same kind of operation" but **"would I grant them together"**.

Two corrections to the instinct that fewer is better. Tool count is not the thing to minimize — ambiguity per tool is; keep the active set small (cross-vendor guidance suggests under ~20 per turn) and namespace beyond that. And over-consolidation has its own failure: when one tool serves unrelated use cases, the failure moves from tool *selection* to tool *parameterization*, and the model can no longer tell which combination of parameters is valid. Reach for defaults, format presets, and an `options` object for the rarely-used tail before splitting.

Two things consolidation is *not*. It is not a claim about how long the result may be held — a bundled response routinely mixes stable identity with volatile state, so stamp per field rather than per response and decide holding time separately, by volatility. And it is not purely an efficiency argument: a sequence of writes that must be coherent should be one call, because a rejection partway through a sequence leaves the earlier writes applied.

When the data layer is legible and the model strong, a few primitive tools can beat many specialized ones — see `architecture.md`.

## Make tool contracts self-explanatory

**The description is the highest-leverage surface in the contract** — evals rank it the single largest factor in tool performance, above naming and schema. Lead with what the tool does, then when to call it and when not, input conventions and defaults, side effects, and how it differs from its siblings. Where state has a lifetime, put that lifetime in the description, so it enters context alongside the handle the model is carrying. Add schema-validated input examples for format-sensitive tools, and use strict schemas where the runtime supports them.

Two naming facts that are runtime behavior rather than style. Prefix versus suffix order can measurably matter by model and runtime, so pick a convention and test it instead of treating one as universal. And in prompts, reference tools by fully qualified name (`ServerName:tool_name`) — with multiple servers loaded, unqualified names can collide or fail to resolve, so audit for collisions when adding a server.

## Design responses for the agent reader

Responses become context, so they are read by something that reasons rather than renders. Lead with human-readable, task-relevant fields — labels, slugs, short refs — and include raw IDs only where follow-up calls need them. `{ "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479" }` as the main reasoning surface measurably increases hallucinated references; `{ "label": "Jane Chen in #product-launch", "ref": "thread_7" }` does not.

Where a value can change under the agent, say when the response was true. An undated value reads as present tense forever, and a stamp is the only lever the agent has for reasoning about its own staleness.

Use `response_format` only where verbosity meaningfully varies — concise for confirmations, detailed for decisions needing the full record — and document in the description when to use each. Do not add it to tiny tools, where it only expands the schema. The serialization itself has no universal winner: choose the simplest shape that preserves structure and avoids awkward escaping.

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
    "safe_to_retry_verbatim": false,
    "replan_required": true,
    "resolution": "Re-derive your change from the state included here. If what landed touches the field you meant to write, surface it instead of reapplying."
  }
}
```

Four properties do the work:

- **Say what was applied.** A conflict from a multi-entity write may arrive after part of it committed. "Retry" against a partially applied write re-fires whatever already succeeded — a second notification, a second charge. State `applied` explicitly rather than leaving the agent to infer that a conflict means nothing happened.
- **Split retryability into two questions, and answer both server-side.** *May the identical payload be resent?* and *is the decision behind it still valid?* A single `retryable: true` conflates them, and on a conflict it answers the wrong one: the mechanism will accept a retry, which is precisely why the agent must not send one. Resubmitting the same value against a fresh version launders a stale decision through the precondition that existed to catch it. Transient failures — a timeout, a lock, a rate limit — are retryable verbatim; conflicts and precondition failures never are.
- **Carry the current state.** Recovery then costs no extra round trip, and the correction arrives at the one moment with guaranteed attention: an announcement can be ignored, a refused write cannot.
- **Distinguish "retry this" from "stop".** A conflict caused by someone else's change is an escalation signal — see `context-lifecycle.md`. Authorization failures are terminal and must not read as solvable; `trust-and-safety.md` covers why.

Common cases: validation errors state received versus expected plus a fix; rate limits state the wait; not-found suggests a verification step. Only include valid values when safe — for permissions or sensitive resources, return a non-enumerating error.

## Schema vs prompt ownership

The tool schema owns field names and types, required versus optional, enums and return shape, and defaults that reflect the common case so the agent can safely omit parameters. Per-field descriptions carry a concrete format example wherever the format is non-obvious (`"CUST-######, e.g. CUST-000001"`, `"YYYY-MM-DD"`) — the schema is where the model looks when constructing an argument, and prose elsewhere will not reach it in time.

Every parameter is a decision delegated to the model. A value the model cannot reliably know — the current user, tenant, project scope — is not a parameter: resolve it in the handler from session or runtime context and keep it out of the schema, even when the backend API requires it. The model can no longer hallucinate an identifier software already knows, the schema stays small and cache-stable, and a manipulated call cannot reach another tenant's scope.

These rules apply to any schema the model writes against. Structured-output response schemas are the same surface: per-field descriptions steer generation exactly as parameter descriptions steer calls, and a vague field name yields a vague field value.

The tool description is a model-facing prompt, not human documentation — drop file paths, change history, implementation notes, and how-it-works detail. The developer or system prompt owns cross-tool workflow order, disambiguation between overlapping tools, approval choreography, domain concepts that are not field definitions, and tone. Neither restates the schema.

## Partial updates

The agent-specific argument for partial updates is not convenience: a whole-object update makes the agent reconstruct fields it never read, so any field that changed under it gets silently reverted by its own write. Partials let the server preserve what the agent did not touch. For deeply nested objects a constrained patch format may help, but pointer-style paths add another thing the model can get wrong.

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

A stale description misroutes the agent more quietly than a broken schema does — the call is well-formed and simply wrong, so nothing errors. Version descriptions with the tool, review them in the change that touches the API, and re-run tool evals after meaningful edits.

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
