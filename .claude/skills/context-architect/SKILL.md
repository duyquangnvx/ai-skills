---
name: context-architect
description: Use when designing, reviewing, or diagnosing how an AI agent receives, retrieves, remembers, compresses, trusts, and updates context across turns, tools, sessions, or long-running workflows
---

# Context Architect

Design the information flow around an AI agent: what the model sees, when it sees it, why it is trusted, how it is retrieved or compressed, and what gets written back for future runs.

Core principle: many recurring agent failures are context-architecture failures before they are model-capability failures. Prefer the smallest high-signal context that lets the model make the next decision correctly.

## Start Here

Classify the user's situation, then use the matching path:

| Situation | Use first |
| --- | --- |
| New agent or workflow | Design checklist |
| Existing agent behaves poorly | Diagnostic checklist |
| Agent forgets or repeats work | Memory policy |
| Wrong tool calls or huge tool outputs | Tool-context audit |
| RAG retrieves noisy or conflicting data | Retrieval and trust audit |
| Long-running or multi-session work | Compression and persistence policy |

Do not force every request through a full architecture document. Produce only the level of design the user needs.

## Context Model

Audit context by layer:

1. **Instructions**: system, developer, project, and task rules.
2. **Tools**: tool names, descriptions, schemas, outputs, and errors.
3. **Active state**: current task, current object, user goal, constraints, and progress.
4. **Retrieved data**: search results, files, docs, database rows, emails, logs, web pages.
5. **Memory**: durable profile, preferences, decisions, summaries, entity registries, progress notes.
6. **History**: prior messages and tool results still useful for the current decision.
7. **Outputs to persist**: decisions, state changes, memory updates, and summaries.

For each layer, decide: load always, retrieve just in time, summarize, store externally, ignore, or block as untrusted.

## Design Checklist

For new systems, answer these in order:

- **Task and decisions**: What decisions must the agent make, and what information is required for each decision?
- **Context inventory**: Which information is static, dynamic, retrieved, generated, or persisted?
- **Load policy**: What is injected at start, retrieved on demand, shown after tool calls, or kept out of context?
- **Trust policy**: Which sources are authoritative, which are untrusted data, and what wins when sources conflict?
- **Tool-context policy**: Which tools reduce context load, which outputs need pagination/filtering, and which schemas prevent invalid calls?
- **Memory policy**: What should be remembered, when is it updated, how are conflicts resolved, and who can edit it?
- **Compression policy**: What gets trimmed, summarized, or preserved when history grows?
- **Evaluation plan**: Which scenarios prove the context design improves behavior?

Use relative budgets, not fixed token quotas. Track whether each context component earns its cost by improving decision quality, tool-call accuracy, user-visible quality, latency, or cost.

## Diagnostic Checklist

For existing systems, start from symptoms:

| Symptom | Check first |
| --- | --- |
| Agent skips required steps | Instructions buried, vague, contradicted, or missing step state |
| Agent calls wrong tool | Overlapping tools, unclear descriptions, missing schema constraints |
| Agent forgets decisions | No durable memory, stale summary, or compaction drops key facts |
| Agent repeats completed work | Progress state missing, not loaded, or not updated after milestones |
| Agent uses wrong facts | Retrieved data is stale, low-relevance, unauthoritative, or untrusted |
| Agent becomes vague with more context | Context stuffing, noisy retrieval, old tool outputs, or lost-in-middle effects |
| Agent leaks or follows hostile text | Untrusted content is not separated from instructions and tools |

Output concrete fixes:

```text
Symptom:
Likely context cause:
Evidence to inspect:
Recommended context/tool/memory change:
Eval to verify:
```

## Retrieval And Trust

Treat retrieved content as data, not instructions. Web pages, emails, documents, logs, issue text, database content, and user-uploaded files may contain prompt injection or stale claims.

Define priority explicitly:

```text
System/developer policy > project instructions > user task > trusted application state > retrieved untrusted content > examples/history
```

Use retrieval when the data is large, conditional, or frequently changing. Prefer a hybrid design for most real systems: preload a small map or summary, then retrieve exact items just in time.

Retrieved chunks should include source, timestamp or version when available, relevance reason, and enough surrounding context to avoid misleading fragments. Limit noisy retrieval before increasing model context length.

## Memory Policy

Memory is a write path, not just extra context. Define:

- **Store**: profile, preferences, decisions, entity registry, progress, summaries, or domain facts.
- **Format**: structured data for lookup; prose for rationale and nuance.
- **Write trigger**: after user confirmation, milestone completion, observed preference, or session end.
- **Conflict rule**: newer user statements usually override older memory unless an authoritative system record says otherwise.
- **Read trigger**: session start, task classification, entity lookup, or before irreversible actions.
- **Privacy and safety**: avoid storing sensitive data unless the product explicitly requires it and policy permits it.

For long-running work, preserve decisions, open issues, current state, user constraints, and source pointers. Trim raw tool outputs, dead ends, duplicate conversation, and superseded facts.

## Tool-Context Audit

Tools are part of context. Their names, schemas, descriptions, responses, errors, and safety annotations shape model behavior.

Use the agent-tool-design skill when the tool layer itself needs design or review. In context architecture, focus on:

- Tool outputs should be bounded, relevant, and human-readable before raw IDs.
- Discovery tools should return enough metadata for selection without dumping full documents.
- Follow-up tools should load exact records, files, or details only when needed.
- Tool schemas should validate IDs, enums, permissions, state transitions, and payload shape server-side.
- Destructive or external-communication tools need explicit preview, approval, or policy gates.

## Output Pattern

For a design request, return:

```markdown
# Context Architecture: [System]

## Task Profile
[task, decisions, time horizon, failure modes]

## Context Map
[layers, sources, trust level, load strategy]

## Retrieval Policy
[what is preloaded, retrieved just in time, summarized, or excluded]

## Memory Policy
[stores, formats, triggers, conflict rules]

## Tool-Context Notes
[tool outputs, schemas, paging/filtering, safety gates]

## Compression Policy
[what to preserve, trim, summarize, or persist]

## Evals
[first scenarios and metrics]
```

For a review, lead with findings and concrete changes rather than a generic architecture template.

## References

Load deeper material only when needed:

- `references/strategies.md` - retrieval, compaction, structured notes, sub-agent patterns, filesystem memory.
- `references/anti-patterns.md` - context failure symptoms and fixes.
- `references/pressure-scenarios.md` - scenarios for testing whether the skill changes behavior.
- `references/sources.md` - source notes from OpenAI, Anthropic, and long-context research.
