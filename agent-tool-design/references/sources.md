# Sources

Primary sources the guidance in this skill is drawn from. Read these directly for the full original context.

## Provider and protocol references

**Writing effective tools for agents — with agents** (Sep 2025)
<https://www.anthropic.com/engineering/writing-tools-for-agents>

Source for the five-pillar framing and prototype → eval → iterate methodology, with concrete examples from optimizing Slack and Asana tool servers. Treat product-specific limits and examples as historical context; verify current limits in your target runtime.

**Effective context engineering for AI agents**
<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

Source for the "human engineer test" ("if a human engineer can't definitively say which tool should be used, an AI agent can't be expected to do better"), just-in-time retrieval patterns, and the principle of a minimum viable tool set. Also discusses the broader attention-budget framing.

**Building effective agents** (Dec 2024)
<https://www.anthropic.com/research/building-effective-agents>

Source for the "agent-computer interface (ACI)" framing and format-choice guidance for tool I/O ("keep the format close to what the model has seen naturally occurring in text on the internet"). Also includes the workflow patterns (prompt chaining, routing, orchestrator-workers, evaluator-optimizer) that are useful background when thinking about how tools compose into systems.

**Effective harnesses for long-running agents** (2026)
<https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>

Useful adjunct if the agent you're designing tools for spans many context windows. Covers compaction, cross-session state, and why testing tools (e.g., browser automation) are essential for feature verification.

**Function calling guide**
<https://developers.openai.com/api/docs/guides/function-calling>

Source for strict mode and structured outputs. Provider requirements change; verify current schema restrictions before relying on exact behavior.

**o3/o4-mini Function Calling Guide**
<https://cookbook.openai.com/examples/o-series/o3o4-mini_prompting_guide>

Source for the overlap-disambiguation pattern ("Use python for X. Use calculate_shipping_cost for Y. Prefer Y when both could apply. Fall back to python only if Y fails"). Useful as a concrete example, not a provider requirement.

**Specification**
<https://modelcontextprotocol.io/specification>

Source for one protocol's tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), dynamic tool-list notifications, and overall protocol shape. Use when building MCP servers or clients; otherwise translate the concepts to your runtime.

**Tool Annotations as Risk Vocabulary** (MCP blog, Mar 2026)
<https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/>

Source for the "annotations are hints, not guarantees" stance, the lethal-trifecta discussion in context of MCP, and the ongoing proposals for annotations like `reads_private_data`, `sees_untrusted_content`, `can_exfiltrate`.

## Related reading

**Simon Willison on the lethal trifecta**

Willison's blog coined this framing. Search his site for "lethal trifecta" — he has multiple posts with concrete prompt-injection examples and mitigations. The short version: private data + untrusted content + external communication = exfiltration risk. This is the most practical threat model for agent tool systems.

**MCP tool annotation SEPs (Standards Enhancement Proposals)**

If you want to see where the annotation story is headed, follow the MCP GitHub for open SEPs. Several active proposals cover trust, sensitivity, and preflight checks. Worth tracking if you're shipping MCP servers in production.
