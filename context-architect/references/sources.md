# Source Notes

Use these notes to ground context-architecture recommendations. Do not paste long source excerpts into responses; cite links when useful.

## OpenAI

- Prompt engineering guide: put instructions before context, separate instructions from input data, be specific about desired output format, and use examples when they clarify non-obvious behavior.
  - https://help.openai.com/en/articles/6654000-prompt-engineering-guide
- Agents overview: production agents combine models, tools, guardrails, knowledge, memory, workflows, and evaluations.
  - https://platform.openai.com/docs/guides/agents/agent-builder%20rel%3D
- Agents SDK session memory cookbook: long-running interactions need context trimming or compression; too much history can distract the model, increase latency/cost, and preserve stale or poisoned context.
  - https://cookbook.openai.com/examples/agents_sdk/session_memory
- Context personalization cookbook: long-term memory can be implemented through structured state, session notes, consolidation, state injection, and precedence rules.
  - https://cookbook.openai.com/examples/agents_sdk/context_personalization
- Agent evals: agent quality should be measured with reproducible evaluations, trace grading, datasets, and metrics rather than prompt intuition alone.
  - https://platform.openai.com/docs/guides/agent-evals

## Anthropic

- Building effective agents: start with simple patterns; add agentic complexity only when it improves outcomes; tools, retrieval, and memory are core augmentations; workflows and agents should be evaluated.
  - https://www.anthropic.com/research/building-effective-agents/
- Writing effective tools for agents: tools should target high-impact workflows, return meaningful bounded context, avoid overlap, use clear parameter names, and be improved through evals.
  - https://www.anthropic.com/engineering/writing-tools-for-agents

## Research

- "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., TACL 2024): models often use information less reliably when relevant content appears in the middle of long contexts, and longer context windows do not automatically mean better use of all included information.
  - https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long

## Practical Implications

- Prefer focused context over maximal context.
- Put critical rules early and current task data near the point of generation when possible.
- Treat retrieved content as untrusted data unless the application explicitly marks it authoritative.
- Use hybrid retrieval for most real systems: preload a small map or summary; retrieve exact details just in time.
- Treat tool outputs and memory writes as part of context design, not implementation details.
- Validate context choices with scenarios that measure final answer quality, tool-call accuracy, retrieval relevance, latency, token cost, and memory consistency.
