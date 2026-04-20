# Sources

Primary sources the guidance in this skill is drawn from. Read these directly for the full original context.

## Anthropic Engineering Blog (primary)

**Writing effective tools for agents — with agents** (Sep 2025)
<https://www.anthropic.com/engineering/writing-tools-for-agents>

The canonical source for the five pillars. Covers the full prototype → eval → iterate methodology, with concrete data from optimizing Slack and Asana MCP servers. The `response_format` concise/detailed pattern, the 25,000-token tool-response cap in Claude Code, and the "web search appending 2025" example all come from here. Read this in full if you're going to build an agent tool system seriously.

**Effective context engineering for AI agents**
<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

Source for the "human engineer test" ("if a human engineer can't definitively say which tool should be used, an AI agent can't be expected to do better"), just-in-time retrieval patterns, the Claude Code `head`/`tail` database example, and the principle of a minimum viable tool set. Also discusses the broader attention-budget framing. Background for `conversation-state.md` — the "message history is part of context state" framing comes from here, though the specific stateful-tool-responses pattern is a synthesis.

**Building effective agents** (Dec 2024)
<https://www.anthropic.com/research/building-effective-agents>

Source for the "agent-computer interface (ACI)" framing and format-choice guidance for tool I/O ("keep the format close to what the model has seen naturally occurring in text on the internet"). Also includes the workflow patterns (prompt chaining, routing, orchestrator-workers, evaluator-optimizer) that are useful background when thinking about how tools compose into systems.

**Effective harnesses for long-running agents** (2026)
<https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>

Useful adjunct if the agent you're designing tools for spans many context windows. Covers compaction, cross-session state, and why testing tools (e.g., browser automation) are essential for feature verification.

## OpenAI

**Function calling guide**
<https://developers.openai.com/api/docs/guides/function-calling>

Source for strict mode and structured outputs. The guide is explicit: `strict: true` requires `additionalProperties: false` and all fields required (use nullable for optional). Also introduces `tool_search` for large tool sets (gpt-5.4+).

**o3/o4-mini Function Calling Guide**
<https://cookbook.openai.com/examples/o-series/o3o4-mini_prompting_guide>

Source for the "developer prompt as centralized, durable contract" framing and the overlap-disambiguation pattern ("Use python for X. Use calculate_shipping_cost for Y. Prefer Y when both could apply. Fall back to python only if Y fails"). Especially relevant for reasoning models.

## Model Context Protocol

**Specification**
<https://modelcontextprotocol.io/specification>

Authoritative source for the tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), dynamic tool-list notifications, and the overall protocol shape. MCP is the de facto standard for tool interop across Anthropic, OpenAI, and Google Cloud as of 2026.

**Tool Annotations as Risk Vocabulary** (MCP blog, Mar 2026)
<https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/>

Source for the "annotations are hints, not guarantees" stance, the lethal-trifecta discussion in context of MCP, and the ongoing proposals for annotations like `reads_private_data`, `sees_untrusted_content`, `can_exfiltrate`.

## Related reading

**Simon Willison on the lethal trifecta**

Willison's blog coined this framing. Search his site for "lethal trifecta" — he has multiple posts with concrete prompt-injection examples and mitigations. The short version: private data + untrusted content + external communication = exfiltration risk. This is the most practical threat model for agent tool systems.

**Anthropic prompt caching docs**
<https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>

Official reference for how prefix caching works, cache breakpoints, and TTL behavior. Background for `conversation-state.md` — the three-places-to-inject analysis and the "msg_N is free" insight are consequences of the caching mechanics documented here.

**On the stateful-tool-responses pattern**

The specific pattern (mutation tools returning current-state summaries so the agent's history becomes its memory) is a synthesis, not drawn verbatim from any single source. It emerges from combining (a) Anthropic's context engineering guidance about treating history as part of context state, (b) prompt caching mechanics, and (c) observations from production agent systems where re-querying state every turn is the dominant token cost. The framing in `conversation-state.md` is distilled from practice; the underlying concepts are well-supported by the Anthropic sources above.

**MCP tool annotation SEPs (Standards Enhancement Proposals)**

If you want to see where the annotation story is headed, follow the MCP GitHub for open SEPs. Several active proposals cover trust, sensitivity, and preflight checks. Worth tracking if you're shipping MCP servers in production.
