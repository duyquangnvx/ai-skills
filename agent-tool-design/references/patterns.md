# Deep-dive: tool design patterns

This reference expands on the five pillars, schema design patterns, system-prompt/schema boundaries, and tool-set architecture from the main SKILL.md. Read the sections relevant to your current task — no need to read top-to-bottom.

## Contents

1. The five pillars in depth
2. Schema design patterns
3. System prompt vs tool schema — detailed
4. Tool set design — detailed

---

## 1. The five pillars in depth

### Pillar 1 — Choose the right tools

**Don't mirror your internal API.** Shipping one tool per backend endpoint optimizes for API coverage, not for agent effectiveness. Agents have limited context; chaining five low-level calls for every workflow wastes tokens on intermediate state the agent doesn't need to see.

The question is: **what workflows does the agent actually run?** Build tools that subdivide *those workflows* the way a thoughtful human would, given access to the same underlying resources.

Concrete examples:

- Instead of `list_users` + `list_events` + `create_event`, ship `schedule_event` that finds availability and creates the event in one call.
- Instead of `read_logs` that returns everything, ship `search_logs` that returns relevant lines plus context.
- Instead of `get_customer_by_id` + `list_transactions` + `list_notes`, ship `get_customer_context` that compiles recent, relevant customer info in one response.

The principle: **consolidate what agents chain frequently; subdivide what they need to control finely.**

**Fewer tools is usually better.** Too many tools or overlapping tools distract the agent from efficient strategies. Curating a minimal viable set — tools that match the workflows your evals cover — reliably outperforms bloated tool sets. Add tools only when you've seen a real workflow that needs one, not speculatively.

**The human engineer test.** If a human engineer can't definitively say which tool to use in a given situation, an agent can't either. Overlap is the biggest failure mode; every new tool should have a crisp one-sentence "use this when…" that doesn't apply to any existing tool.

### Pillar 2 — Namespace for clarity

As tool sets grow (especially with MCP, where an agent may load dozens of servers at once), name collisions and purpose ambiguity become a leading cause of wrong-tool calls.

**Namespacing patterns:**

- By service: `asana_search`, `jira_search`, `github_search`.
- By service and resource: `asana_projects_search`, `asana_users_search`.
- By domain: `billing_get_invoice`, `billing_refund_payment`.

Prefix vs suffix style can affect tool-use accuracy, and the effect varies by model and runtime. Pick a consistent convention, then test if naming order matters for your use case.

Consistency matters more than any specific style: pick a convention and apply it everywhere. Agents will learn the boundary if it's clearly drawn; they'll stumble if some tools follow the convention and others don't.

### Pillar 3 — Return meaningful context

Tool responses are another form of context the agent has to reason over. Returning raw technical identifiers is a common failure:

```json
// Low-signal — agent must chain more calls to interpret
{ "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "thread_ts": "1234567890.123" }

// High-signal — agent can act on this directly
{ "name": "Jane Chen", "channel": "#product-launch", "last_message_at": "2h ago" }
```

Resolving arbitrary UUIDs to natural-language names — or even a simple numbered scheme — often reduces hallucinations in retrieval tasks. Agents reason better over semantic identifiers than cryptic ones.

**The `response_format` pattern.** Sometimes the agent needs IDs (to chain into a next tool call), sometimes it just needs the content. Expose a `response_format` parameter with a small enum:

```typescript
enum ResponseFormat {
  CONCISE  = "concise",   // name, content, timestamp — for reasoning
  DETAILED = "detailed"   // adds IDs, URIs, metadata — for follow-up tool calls
}
```

In tools where the response can be either a compact summary or a full object, concise responses can save substantial tokens. The agent chooses per call which it needs.

**Response shape matters.** XML vs JSON vs Markdown — no universal winner. LLMs are trained on next-token prediction and tend to perform better with the format they've seen most for a given kind of content. Test format on your own evals. When in doubt, match what the content would naturally look like on the open web.

### Pillar 4 — Optimize for token efficiency

The context window is a finite attention budget. Every unnecessary token in a tool response dilutes the agent's attention on what matters.

**Bake limits into the tool:**

- Pagination with sensible page sizes. Provider/client caps are backstops, not a substitute for bounded tool design.
- Filtering parameters so the agent can ask for only what it needs.
- Range selection for time-series or ordered data.
- Truncation with a clear indicator that more data exists, plus instructions on how to page further.

**Make errors actionable.** Don't return opaque `500 Internal Server Error` or `Invalid input`. Tell the agent exactly what went wrong and how to recover:

```
# Unhelpful
{"error": "Invalid request"}

# Helpful
{
  "error": "Unknown scene_id 'scene_99'.",
  "valid_scene_ids": ["scene_1", "scene_2", "scene_3"],
  "hint": "Call list_scenes() to get the current scene IDs."
}
```

The agent reads this, self-corrects, and retries without human intervention. Every reference error becomes a self-healing loop instead of a failed task.

**Steer via truncation messages.** When you truncate, use the truncation message to steer behavior: "Results truncated at 50 items. Narrow the search with a more specific `query` or use `created_after` to filter by date." The agent will follow the hint on the retry.

### Pillar 5 — Prompt-engineer tool descriptions

Tool names, descriptions, and parameter names are loaded into the agent's context on every turn. They **are** prompts. Treat them with the care of prompt engineering.

**Write for a new hire.** Imagine describing the tool to a smart engineer joining your team who has zero domain context. Spell out the implicit:

- What the tool does, and what it does NOT do (especially vs. sibling tools).
- When to call it — preconditions, typical triggers.
- Expected input format — not just types but conventions (ISO dates, tz handling).
- What to expect back — shape and meaning.
- Any edge cases worth knowing — rate limits, pagination defaults, side effects.

Small description refinements can produce large gains on tool-use evals. One common pattern: when a model repeatedly adds an unwanted default or uses the wrong sibling tool, a sharper tool description often fixes the behavior without changing the model.

**Self-documenting parameter names:**

- `user_id` beats `user` or `id`.
- `start_date` beats `start` or `date`.
- `after_node_id` beats `after`.
- `include_archived` beats `flag1`.

A parameter name should read correctly in a tool-call trace with no surrounding context.

**Use strict schemas.** Where your tool protocol supports it, use strict schemas / structured outputs so the runtime can enforce that the agent's call matches your contract. Exact requirements vary by provider and protocol; verify current docs for details such as additional properties and nullable optional fields.

---

## 2. Schema design patterns

### Tool schema is the single source of truth

The most common waste in agent systems: defining a field schema twice, once in the system prompt as documentation and once in the tool's `parameters`. Three things go wrong:

- **Token waste.** A moderately complex schema duplicated in the prompt easily costs 3-5k tokens per request.
- **Drift.** The two copies diverge silently. Required lists, enums, defaults get updated on one side and not the other.
- **Contradiction.** The agent receives two contracts. Which wins? Unpredictable.

**Fix:** delete field-shape documentation from the system prompt. Keep in the prompt only what the schema can't express — policy, workflow order, semantic constraints between tools, disambiguation rules. Let the tool schema speak for itself.

### Partial updates over full-object replacement

For any edit tool on a structured object:

```
# Brittle — forces the agent to reconstruct the whole object
update_scene(scene_id, scene: Scene)

# Robust — agent sends only what changes
update_scene(scene_id, updates: Partial<Scene>)
```

With a partial-update shape, the agent's mental model shrinks from "the whole object" to "the delta." Fields it didn't name are preserved server-side. For deeply nested edits, JSON Patch (`[{op: "replace", path: "/title", value: "..."}]`) is also viable, but partial-object is more LLM-friendly in practice — JSON Pointer syntax adds a second thing to get right.

### One tool vs many — a judgment call

**Split into narrow tools when:**

- Variants have different semantics, preconditions, or side effects.
- Variants have very different required fields and the `oneOf` has become unwieldy.
- You want distinct descriptions to steer tool selection.
- You want different error messages per variant.

**Keep a merged tool when:**

- Variants share most fields and semantics.
- The agent frequently emits mixed batches of variants together (one atomic call is better than many sequential ones).
- The variants differ cosmetically, not in validation logic.

When torn, err toward splitting. Wide `oneOf` unions are harder for models to handle than lists of narrow tools — especially non-frontier models.

### Reference integrity belongs in the tool layer

Any rule that can be checked deterministically — "does this ID exist", "is this enum valid given current state", "is this edit allowed" — should be validated server-side. Two reasons:

1. The agent might ignore the rule even if it's in the prompt.
2. The tool has fresh state; the prompt is static.

Return actionable errors (see Pillar 4 above) and the agent's self-correction loop handles the rest.

### Dynamic enums (where cache economics allow)

When you can generate tool schemas per-request, inject current state as enums:

```json
{
  "character_id": { "type": "string", "enum": ["nobita", "shizuka", "doraemon"] },
  "target_scene": { "type": "string", "enum": ["scene_1", "scene_2"] }
}
```

In strict mode, the model physically cannot emit an invalid reference. This eliminates a whole class of hallucination bug. Tradeoff: per-request schemas break prompt caching. If your traffic pattern relies on cache hits, lean on server-side validation instead.

---

## 3. System prompt vs tool schema — detailed

The short answer is in the main SKILL.md table. The longer answer covers the reasoning and some harder cases:

**Workflow guidance** belongs in the prompt because it spans tools. A sentence like "Call `list_scenes` before creating a `choice` so targets resolve to real IDs" doesn't fit in either tool's description — it's relational.

**Disambiguation between overlapping tools.** Use the developer/system prompt as the durable contract for cross-tool decision boundaries. A concrete pattern:

> "Use `python` for general math or data parsing that needs no external lookup. Use `calculate_shipping_cost` for shipping estimates — it applies business rules and live rate tables. When both could apply, prefer `calculate_shipping_cost` for policy compliance. Fall back to `python` only if the custom tool fails."

Rules like this span tools. Put them in the prompt, once, clearly.

**Destructive-action policy.** "Confirm before calling `delete_scene` or `send_email`" — prompt-level policy, applied across tools.

**Persona, tone, style.** Always prompt-level.

**What does NOT belong in the prompt:**

- Field names, types, enum values (tool schema handles this).
- Required vs optional (tool schema).
- Per-tool "what this is" (tool description).
- Cases enforceable by server-side validation (move to the tool layer).

**Grey area: semantic domain glossary.** If your domain has specific vocabulary — "a 'beat' is one dialogue exchange", "a 'scene' in our system always has a single background" — this is prompt-level. It's conceptual context, not schema.

---

## 4. Tool set design — detailed

### Read/orient/search layer

For any agent that inspects and edits a domain, provide multiple tiers of read access:

- **Orient** — one cheap call that returns a whole-project summary: counts, top-level IDs, flags, schema version. Good first call in any conversation.
- **List** — shallow enumerations returning IDs and short labels. Used to discover what exists. Cheap.
- **Get** — full detail on a specific entity by ID. Used right before acting.
- **Search** — full-text or semantic lookup when the agent has a keyword but not an ID.

Document the expected call pattern in the system prompt as a workflow, not a mandate:

```
Typical workflow:
- First call: get_project_overview()
- Before editing a scene: list_scenes() → get_scene(id)
- Before creating a reference: list the referenced entity type first
- After significant edits: validate_project()
```

This gives the agent a "default path" to follow, while leaving room to deviate when the situation warrants.

### Just-in-time context retrieval

Don't pre-load everything. Let the agent load context when it needs it. Instead of reading entire datasets, provide query/search/list tools plus a way to inspect slices of the result. The full data never needs to enter context.

This pattern — lightweight identifiers + tools that dereference them — scales to arbitrary data sizes and keeps attention focused on the current task.

### Progressive tool discovery

Past 20-30 tools, the tool list itself starts costing meaningful tokens. Options, in order of increasing complexity:

1. **Namespace aggressively** and rely on namespacing to make the list scannable.
2. **Tool search** — expose a `tool_search(keywords)` meta-tool that returns relevant tool schemas on demand. The agent loads tools just-in-time. Some providers and clients ship built-in versions of this pattern; verify availability in your target runtime.
3. **Subagent delegation** — a coordinator agent with a small tool set delegates to specialized sub-agents, each with their own focused tool set and a clean context window.

Don't reach for these prematurely. A flat list of 10-15 well-named tools usually outperforms a clever discovery layer for small domains.

### When to add an `overview` or `validate` tool

Two tool types that recur across domains and are easy to forget:

- **`overview` / `orient`** — a single cheap read that surfaces things the UI might hide: counts, flags, schema versions, dangling references. Useful as the first call in any conversation; reduces the agent's need to chain several `list_*` calls just to get oriented.
- **`validate`** — a read-only check that returns all structural/referential issues at once. After significant edits, a single `validate` call catches broken references faster than the agent could notice them via tool errors. Pairs well with actionable error messages.

Both are "lightweight read tools" that pay for themselves many times over in reduced round-trips.
