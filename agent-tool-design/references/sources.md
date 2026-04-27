# Verified Source Notes

Use these as background, not as a substitute for checking the target runtime's current documentation.

## Strongly Supported Claims

### Tools are an ACI, not just backend endpoints

Sources:

- Anthropic, "Writing effective tools for agents - with agents" (Sep 11, 2025): https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, "Building effective agents" (Dec 2024, now under Engineering): https://www.anthropic.com/engineering/building-effective-agents

Supported guidance:

- Tool design is a contract with a non-deterministic caller.
- Existing API endpoints are often not the right agent tool shape.
- Tool names, descriptions, parameters, and response formats deserve prompt-engineering attention.
- Invest in ACI design similarly to HCI: make the action obvious from the interface.

### Five recurring tool-design levers

Source:

- Anthropic, "Writing effective tools for agents - with agents": https://www.anthropic.com/engineering/writing-tools-for-agents

Supported guidance:

- Choose the right tools.
- Namespace tools for clearer boundaries.
- Return meaningful context.
- Optimize responses for token efficiency.
- Prompt-engineer tool descriptions/specs.

Notes:

- The exact performance impact of naming schemes, response formats, and descriptions is model/runtime dependent. Treat these as eval targets, not universal constants.

### Responses should be high-signal and bounded

Source:

- Anthropic, "Writing effective tools for agents - with agents": https://www.anthropic.com/engineering/writing-tools-for-agents

Supported guidance:

- Prefer contextual, human-readable fields over low-level technical identifiers as the primary response surface.
- Cryptic identifiers such as arbitrary UUIDs can increase hallucinated references.
- `response_format: concise | detailed` is useful when the model sometimes needs compact content and sometimes needs technical IDs for follow-up calls.
- Pagination, filtering, range selection, and truncation help control context use.
- Error and truncation messages can steer the next call.

Notes:

- Do not add `response_format` to every tool by default; use it only when response verbosity meaningfully varies.

### Format choice should minimize model burden

Sources:

- Anthropic, "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents
- OpenAI, "o3/o4-mini Function Calling Guide" (May 26, 2025): https://developers.openai.com/cookbook/examples/o-series/o3o4-mini_prompting_guide

Supported guidance:

- Some formats are harder for models to produce or consume than others.
- Avoid unnecessary escaping, line-counting, or awkward nested formats.
- Put key usage and argument rules early in tool descriptions.
- Use strict schemas where the runtime supports them.

Notes:

- OpenAI's guide is model-family specific. Use the durable parts (clarity, strict schemas, disambiguation) and verify behavior for the deployed model.

### Prompt/schema boundary

Sources:

- OpenAI, "o3/o4-mini Function Calling Guide": https://developers.openai.com/cookbook/examples/o-series/o3o4-mini_prompting_guide
- OpenAI, "Function calling": https://developers.openai.com/api/docs/guides/function-calling

Supported guidance:

- Function/tool descriptions explain when and how to invoke a tool.
- Developer/system instructions are better for cross-tool workflow, disambiguation, and policy.
- Strict schemas can constrain argument shape in supported runtimes.

Notes:

- Exact JSON Schema support, strict-mode limitations, and tool-call message formats change over time. Check current docs.

### Evals should measure tool behavior, not just final answers

Sources:

- Anthropic, "Writing effective tools for agents - with agents": https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, "Effective harnesses for long-running agents": https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Supported guidance:

- Use realistic multi-step tasks.
- Collect tool-call count, errors, token use, latency, transcripts, and final accuracy.
- Use held-out tasks to avoid overfitting.
- End-to-end verification catches failures that unit-style checks miss.

Important adjustment:

- Some provider content discusses reasoning/CoT for eval analysis. In this skill, prefer observable diagnostics and provider-exposed reasoning summaries. Do not ask models to reveal hidden chain-of-thought.

### Tool annotations are hints, not guarantees

Sources:

- MCP specification: https://modelcontextprotocol.io/specification
- MCP blog, "Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do" (Mar 16, 2026): https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/

Supported guidance:

- MCP-style annotations include read-only, destructive, idempotent, open-world, and title hints.
- Annotations from untrusted servers must be treated as untrusted.
- Annotations can inform UX and policy, but enforcement belongs in authorization, sandboxing, runtime policy, or network controls.

### Lethal trifecta risk is session-level

Sources:

- Simon Willison, "The lethal trifecta for AI agents" (Jun 16, 2025): https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- MCP blog, "Tool Annotations as Risk Vocabulary": https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/

Supported guidance:

- High exfiltration risk appears when one session combines private data, untrusted content, and external communication.
- The risk often comes from the combination of tools, not one tool alone.
- Prompt instructions alone are not a reliable security boundary.

## Claims Removed or Softened

- "The fix almost always lives in the five pillars" became a diagnostic heuristic.
- Provider/client token caps were removed as durable recommendations because defaults change.
- Chain-of-thought logging was replaced with observable diagnostics.
- Fictional case-study claims are not treated as evidence.
- Dynamic enums are framed as a cache/reliability tradeoff, not a default recommendation.
