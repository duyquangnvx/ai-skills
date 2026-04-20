---
name: agent-tool-design
description: Design tools, tool sets, tool descriptions, tool responses, and multi-turn state patterns for LLM agents — whether exposed as function calls, MCP servers, or a custom ACI. Use whenever the user is drafting or refactoring an agent's tool layer, debating tool granularity ("one big tool or many small ones"), fighting schema duplication between tool definitions and system prompts, dealing with agents that hallucinate IDs or call the wrong tool, trying to fit many tools into limited context, shaping tool responses for token efficiency, handling state across conversation turns, dealing with prefix-cache issues in long agent sessions, adding safety annotations, or writing tool descriptions that steer agent behavior. Distilled from Anthropic's "Writing Effective Tools for Agents", "Effective Context Engineering", and "Building Effective Agents", plus the MCP specification and OpenAI's function-calling guidance. Trigger on phrases like "design tools for my agent", "tool schema", "MCP server design", "agent keeps calling wrong tool", "agent hallucinates IDs", "reduce agent token usage", "one tool or many tools", "partial update vs full object", "tool description", "tool response format", "agent re-queries state every turn", "prompt cache breaking", "stateful tool responses", "agent memory across turns", "thiết kế tool cho agent", "tool schema của agent", "cách viết tool cho LLM", "agent bị miss cache", even when the user doesn't explicitly say "skill" or "best practice".
---

# Agent Tool Design

How to design the tool layer for an LLM agent — the names, schemas, responses, descriptions, and boundaries that together form the **agent-computer interface (ACI)**. The tool layer is the contract between a deterministic system (your backend) and a non-deterministic system (the agent). When that contract is wrong, no amount of system-prompt tuning will save the agent.

This skill synthesizes guidance from authoritative sources — primarily Anthropic's engineering blog, the MCP specification, and OpenAI's function-calling documentation.

## How to use this skill

Start by reading this file end-to-end. It gives you the mental model, the five pillars, decision heuristics, and a review checklist — enough to critique or draft most tool sets.

Load deeper material as needed:

- **`references/patterns.md`** — detailed explanations of each pillar, schema design patterns, tool-set architecture, system-prompt/schema boundaries. Read when a specific section here is too compressed for the task.
- **`references/conversation-state.md`** — how tool responses carry state across turns, prefix-cache mechanics, the stateful-tool-responses pattern, when to fall back to message-level injection. Read when designing multi-turn agents over mutating state, or when an agent is burning tokens re-querying state every turn.
- **`references/process.md`** — the evaluation-driven improvement loop, safety annotations, the "lethal trifecta" threat model. Read when the user wants to set up testing, iterate on tools with measurement, or is dealing with destructive/sensitive actions.
- **`references/case-study.md`** — a concrete walkthrough applying all the principles to a visual-novel editor. Read when the user is working on something structurally similar (domain editor, CMS, story builder) and wants to see the full intervention plan.
- **`references/sources.md`** — annotated links to the original articles. Point the user here when they want primary sources.

---

## Why tools for agents are different

Traditional functions are contracts between deterministic systems: `getWeather("NYC")` returns the same shape every call, called by a programmer who read the docs. Tools for agents are contracts between a deterministic system and a **non-deterministic** caller that may call the wrong tool, pass wrong parameters, hallucinate IDs, ignore description hints, or process responses incorrectly.

Anthropic frames this as treating the **agent-computer interface** with the same care engineers give to human-computer interfaces. Designing for agents means the "user" reads via next-token prediction, has a finite attention budget, and doesn't read docs outside its context.

The practical implication: **wrapping your existing REST API one endpoint per tool is almost never right.** The right tool shape for an agent is usually different from the right endpoint shape for a programmer.

---

## Five pillars

Anthropic distilled five principles from optimizing internal tool servers on Slack and Asana MCP. When something feels off about a tool design, map the symptom to one of these — the fix almost always lives there.

### 1. Choose the right tools

Build tools that match real workflows, not one-per-backend-endpoint. Consolidate chains the agent runs frequently (e.g., `schedule_event` instead of `list_users` + `list_events` + `create_event`). Subdivide what needs fine control. Test: if a human engineer can't definitively say which tool to use in a given situation, neither can the agent.

### 2. Namespace for clarity

Group related tools with consistent prefixes (`asana_search`, `jira_search`) or service+resource pairs (`asana_projects_search`). With dozens of MCP servers loaded, namespacing is often the difference between the right tool and a guess.

### 3. Return meaningful context

Lead with human-readable fields. UUIDs cause hallucinations when the agent has to reference them in follow-up calls. Expose a `response_format: concise | detailed` enum so the agent chooses — Anthropic's Slack example used ⅓ the tokens on "concise."

### 4. Optimize for token efficiency

Pagination, filtering, range selection, truncation — all with sensible defaults. Claude Code caps tool responses at 25,000 tokens by default. Steer behavior through error messages: every validation failure should tell the agent exactly what was wrong and how to retry.

### 5. Prompt-engineer tool descriptions

Tool names, descriptions, and parameter names are prompts loaded on every turn. Write them for a new hire with no domain context: state what the tool does and does NOT do, when to call it, input conventions (ISO dates, tz), what to expect back, edge cases. Parameter names should read correctly without context (`user_id` beats `user`).

See `references/patterns.md` for in-depth examples and sub-patterns under each pillar.

---

## Core schema patterns

Beyond the pillars, these concrete decisions recur:

- **Tool schema is the single source of truth.** Do not duplicate field shapes in the system prompt. Drift between the two copies causes contradiction and wastes thousands of tokens per request. Keep in the prompt only what the schema can't express: policy, workflow order, disambiguation between overlapping tools.

- **Partial updates over full-object replacement.** `update_scene(id, updates: Partial<Scene>)` beats `update_scene(id, scene: Scene)`. The agent mental model shrinks from "the whole object" to "the delta"; unnamed fields are preserved server-side.

- **Reference integrity in the tool layer.** Every rule that can be checked deterministically ("does this ID exist", "is this enum valid given current state") belongs in server-side validation, not in prompt rules. Return actionable errors listing valid values; the agent's self-correction loop handles the rest.

- **Dynamic enums** (when cache economics allow). Generate schemas per-request with current-state enums for reference fields: `character_id: enum["nobita", "shizuka"]`. In strict mode the agent physically cannot emit an invalid reference. Tradeoff: per-request schemas break prompt caching.

- **One tool vs many — judgment call.** Split when variants have different semantics, preconditions, or side effects, or when `oneOf` has become unwieldy. Keep merged when variants share semantics and the agent frequently emits mixed batches. When torn, err toward splitting — wide unions are harder for models than lists of narrow tools.

For worked-through examples of each pattern, see `references/patterns.md` § "Schema design patterns".

---

## System prompt vs tool schema: what goes where

| Put in the tool schema | Put in the system prompt |
|------------------------|--------------------------|
| Field names, types, enums | When to call which tool (especially overlapping cases) |
| Required vs optional | Workflow / call order patterns |
| Parameter descriptions | Semantic constraints that span tools |
| Per-tool "what this does" | Persona, tone, domain context |
| Per-tool return shape | Policy (confirmation for destructive actions) |

The OpenAI o3/o4-mini guide frames the developer prompt as a **"centralized, durable contract"** — the place to spell out decision boundaries when tools overlap. Example: "Use `python` for general math. Use `calculate_shipping_cost` for shipping — it applies business rules. When both could apply, prefer `calculate_shipping_cost`. Fall back to `python` only if the custom tool fails."

Rules like this don't fit in individual tool descriptions. Put them in the prompt, once, clearly.

---

## Tool set design (system view)

Individual tools can be perfect and the set can still fail. Think about the collection:

- **Read/orient layer.** Provide an `orient` tool (cheap overview), `list_*` (shallow IDs + labels), `get_*` (full detail by ID), `search_*` (keyword lookup). Document expected call order in the system prompt as workflow, not mandate.

- **Just-in-time context.** Don't pre-load everything. Claude Code's example: instead of reading full database contents, Claude writes a query, stores results, uses `head`/`tail` to inspect. Lightweight identifiers + dereferencing tools scale to arbitrary data.

- **Progressive tool discovery** (past 20-30 tools): namespace aggressively first; then `tool_search` as a meta-tool; then subagent delegation. Don't reach for these prematurely — 10-15 well-named tools beat a clever discovery layer for small domains.

Deeper discussion in `references/patterns.md` § "Tool set design".

---

## State across turns

Multi-turn agents need to carry state across turns — the roster of characters, the list of scenes, the open tickets — without re-querying every turn. Two interlocking patterns solve this:

- **Stateful tool responses.** Mutation tools return a compact current-state summary of the slice they touched, not just an ID. After `createCharacter` returns `"Characters now: Nobita, Shizuka, Suneo"`, the agent knows the roster on every subsequent turn because the summary is in conversation history. Apply to every mutation tool; apply to actionable errors as well so the agent self-corrects with full information.

- **Cache-stable by default.** Prefix caching hashes from the start of the request. Anything that changes in the system prompt or earlier messages destroys the cache; tool responses that enter history normally don't, because history bytes stay stable forever after. This is why injecting state into the system prompt is expensive and stateful responses are free.

When state can change outside the chat (users editing directly in the UI), either add a workflow rule telling the agent to re-orient on uncertainty, or inject a state-change notice into the latest user message — both are cache-safe escape hatches.

See `references/conversation-state.md` for mechanics, the three injection points and their cache cost, cumulative-growth mitigation, and a decision recipe.

---

## Evaluation and safety

Two operational concerns that apply to every tool system:

- **Evaluation-driven iteration.** The only reliable way to improve a tool layer is to run realistic multi-step eval tasks, collect metrics (accuracy, tokens, tool errors, duration), read transcripts, and iterate on descriptions. Small description edits often produce large gains. See `references/process.md` for the full loop.

- **Safety annotations and the lethal trifecta.** MCP defines `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. Treat them as hints, not guarantees. Watch for sessions that combine private data + untrusted content + external communication — that's the prompt-injection exfiltration risk surface. See `references/process.md` for detail.

---

## Anti-patterns

1. **Mirroring internal API endpoints one-to-one.** Backend shape ≠ agent shape.
2. **Returning raw UUIDs as the primary identifier.** Agents reason badly over cryptic strings.
3. **Duplicating field schemas in the system prompt.** Token waste, drift, contradiction.
4. **Unbounded responses.** Always paginate, filter, truncate with defaults.
5. **Opaque errors.** Catch, translate, tell the agent how to fix the call.
6. **Relying on prompt rules to prevent hallucinated references.** Server-side validation is the fix.
7. **MUST/NEVER walls in the prompt for things the tool could enforce.** Guarantee > hope.
8. **Tool names describing implementation, not intent.** `parseAndInsertNodes` vs `add_nodes`.
9. **Adding tools speculatively.** Every tool costs attention.
10. **Skipping evaluation.** Small refinements compound only if measured.
11. **Re-querying state every turn** because tool responses only return IDs. Make mutation responses carry a current-state summary; the agent then reads its own history as memory.
12. **Injecting state into the system prompt or earlier messages.** Both destroy prefix caching. Inject into the latest user message if you must, or (better) put state in tool responses.

---

## Review checklist

**Tool selection**
- [ ] Every tool corresponds to an evaluated workflow — no speculative additions.
- [ ] No two tools have overlapping "use this when…" conditions a human couldn't disambiguate in one sentence.
- [ ] Tools consolidate chains the agent runs frequently.
- [ ] Namespacing is consistent across the set.

**Schema**
- [ ] No field shapes duplicated between system prompt and tool schemas.
- [ ] Edit tools accept partial updates.
- [ ] Parameter names are self-documenting (`user_id`, not `user`).
- [ ] Strict mode / structured outputs enabled where supported.
- [ ] Every reference field validated server-side with actionable errors.

**Responses**
- [ ] Responses lead with human-readable fields, not UUIDs.
- [ ] `response_format` enum where the agent might want concise vs detailed.
- [ ] Pagination/truncation defaults keep responses under a reasonable ceiling.
- [ ] Error messages name what went wrong and how to retry.

**Conversation state (multi-turn agents)**
- [ ] Mutation tools return a compact current-state summary, not just an ID.
- [ ] Actionable errors also carry relevant state so the agent self-corrects without re-querying.
- [ ] No state injection into system prompt or earlier messages (cache-hostile).
- [ ] Workflow rule or escape hatch for out-of-band state changes if the UI allows them.

**Descriptions**
- [ ] Each description covers what the tool does, does NOT do, and when to call it.
- [ ] Edge cases the agent needs (timezones, rate limits, side effects) mentioned.
- [ ] Parameter descriptions include format conventions, not just types.

**System prompt**
- [ ] Contains policy, workflow, disambiguation — not duplicated field docs.
- [ ] Destructive tools called out with "confirm before calling."
- [ ] Typical workflow order documented as guidance.

**Safety**
- [ ] Destructive tools distinguishable by name.
- [ ] Human-in-the-loop gates on combinations approaching the lethal trifecta.
- [ ] Annotations set appropriately if in MCP.

**Process**
- [ ] Eval set with realistic, multi-step tasks.
- [ ] Metrics beyond accuracy: tokens, tool-call count, error rate, duration.
- [ ] Held-out test set to avoid overfitting.

---

## How to apply this skill

When the user brings a tool-design problem:

1. **Understand the shape of the problem first.** Is it (a) reviewing an existing tool set, (b) designing a new one, (c) fixing a specific failure mode, or (d) refactoring the prompt/schema split? Each has a slightly different entry point in this skill.

2. **Map symptoms to pillars.** "Agent picks wrong tool" → Pillars 1, 2, 5. "Agent hallucinates IDs" → Pillar 3 + reference integrity. "Responses are huge" → Pillar 4. "Prompt is huge and drifting" → schema-as-source-of-truth.

3. **Run the review checklist** for reviews, or use it as a backwards-design target when building from scratch.

4. **Be concrete.** Propose actual tool signatures, actual error messages, actual description phrasings. This skill's value is in specifics, not in re-stating "design tools well."

5. **Load references/ when depth is needed.** Don't dump the entire knowledge base into the response — point the user to specific files when they'd benefit.

6. **When in doubt, recommend evaluation.** Most tool-design questions have no universal right answer. The reliable path is eval → observe → iterate.
