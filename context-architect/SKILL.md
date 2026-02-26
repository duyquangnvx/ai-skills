---
name: context-architect
description: Design context architectures for AI agent systems. Use when user needs to plan what information an agent receives, when, and in what structure — including memory design, tool set design, context retrieval strategy, and long-horizon handling. Triggers on phrases like "design context for agent", "agent keeps forgetting", "agent skips steps", "context architecture", "context engineering", "agent memory design", "what context should my agent have", or any situation where the user is building an agent system and needs to decide how information flows to and from the model. Also use when user has an existing agent with poor performance that may be caused by context issues (too much noise, lost information, inconsistent behavior across sessions).
---

# Context Architect

Design context architectures for AI agent systems. This skill produces a **Context Architecture Document** — a blueprint of what information the agent receives, when it receives it, how it's structured, and how it evolves over time.

## Core principle

Most agent failures are context failures, not model failures. An agent that skips steps, calls wrong tools, or forgets previous decisions almost always has a context problem: either too much noise, missing information, or wrong information at the wrong time.

Context engineering means finding the smallest set of high-signal tokens that maximize the likelihood of the desired outcome. More context is not better — focused context is better.

## When to use this skill

- Designing a new agent system from scratch
- Diagnosing an existing agent that behaves inconsistently
- Planning memory/state management for multi-session agents
- Deciding between RAG, just-in-time retrieval, or hybrid approaches
- Designing tool sets that agents can use effectively
- Building systems that run over long horizons (hours, days, recurring)

## Design workflow

Follow these phases sequentially. Each phase produces a section of the Context Architecture Document.

---

### Phase 1: Task analysis

Understand what the agent needs to do before deciding what context it needs.

Interview the user (or extract from conversation):

1. **What does the agent do?** — Describe the core task in one paragraph.
2. **What decisions does the agent make?** — List the branching points where the agent must choose between actions.
3. **What information does each decision require?** — For each decision, what data must be present in context?
4. **What's the time horizon?** — Single turn? Multi-turn session? Multi-session over days/weeks?
5. **What changes between runs?** — What's static (instructions, rules) vs dynamic (user data, state, accumulated knowledge)?
6. **What are the failure modes?** — What goes wrong when the agent fails? Skips steps? Wrong tool? Hallucinated data?

Output a **Task Profile**:
```
Task: [one-line description]
Decision points: [count]
Time horizon: single-turn | multi-turn | multi-session | long-horizon
Static context: [list]
Dynamic context: [list]
Primary failure modes: [list]
```

---

### Phase 2: Context budget planning

Context is finite. Plan how to spend the attention budget.

Estimate token allocation across components. These compete for the same limited window — every token added to one component is attention taken from another.

| Component | Priority | Estimated tokens | Notes |
|-----------|----------|-----------------|-------|
| System prompt | High | 500-2000 | Core identity, rules, constraints |
| Tool definitions | High | 200-500 per tool | Keep tool set minimal |
| Active context (current task data) | High | Varies | The data being worked on now |
| Retrieved context (RAG/memory) | Medium | 1000-3000 | Just-in-time, not exhaustive |
| Message history | Medium | Varies, manage actively | Compact when growing |
| Examples/few-shot | Low-Medium | 500-1500 | Diverse and canonical, not exhaustive |
| Metadata/state | Low | 100-500 | Progress tracking, flags |

Guiding principles for budget planning:

- **Information at the beginning and end of context gets more attention** (U-shaped attention curve). Place critical instructions at the start, current task data at the end.
- **Doubling context length does not double useful capacity.** It increases noise and dilutes attention. A focused 2K-token context often outperforms a bloated 100K-token context.
- **Every component must justify its presence.** If removing it doesn't degrade output quality, remove it.

Output a **Context Budget Table** with estimated allocations for the specific system.

---

### Phase 3: Context structure design

Decide what lives where, in what format, and when it gets loaded.

#### 3.1 — Static context (loaded once, rarely changes)

This is the system prompt, tool definitions, and global rules. Design it at the "right altitude" — specific enough to guide behavior, flexible enough for the model to apply judgment.

Two failure modes to avoid:
- **Too prescriptive**: hardcoded if-else logic in the prompt. Brittle, high-maintenance, breaks on edge cases.
- **Too vague**: "handle customer issues professionally." No actionable signal.

For complex instructions, use the FPL methodology (see `references/strategies.md` for details): structure instructions as workflow specifications with explicit flows, steps, conditions, and actions rather than free-form descriptions.

#### 3.2 — Dynamic context (changes per session/turn)

Classify each piece of dynamic information:

| Information | Retrieval strategy | When to load | Format |
|------------|-------------------|-------------|--------|
| [item] | pre-loaded / just-in-time / on-demand | [trigger] | [format] |

Three retrieval strategies — pick the right one per information type:

**Pre-loaded** (loaded into context at session start):
- Use for: small, always-needed data (user profile, project config, rules)
- Example: CLAUDE.md files, glossary, style guides
- Trade-off: fast access, but consumes budget even when not needed

**Just-in-time** (agent retrieves via tools when needed):
- Use for: large or conditional data (documentation, databases, file contents)
- Example: agent uses grep/glob to find relevant files, then reads only what's needed
- Trade-off: slower, requires good tool design, but preserves budget

**Hybrid** (some pre-loaded, more available on demand):
- Use for: most real systems. Pre-load lightweight summaries/indexes, retrieve full data when needed.
- Example: novel-processor loads glossary (small, always needed) but reads chapter files just-in-time

See `references/strategies.md` for detailed guidance on choosing strategies.

#### 3.3 — External memory (persisted outside context window)

For any system that runs across multiple sessions or accumulates knowledge, design external memory files.

For each memory file, define:
- **Name and purpose**: what it stores
- **Format**: structured (table/JSON) or prose? Why?
- **Update trigger**: when does it get updated?
- **Update method**: append-only? Overwrite? Merge?
- **Source of truth**: is this file authoritative, or can the agent override it?

Structured formats (tables, JSON, YAML) are better for data the agent needs to look up precisely — names, mappings, settings. Prose is better for nuanced information — style decisions, design rationale, summaries.

Example from novel-processor skill:
```
context/
├── glossary.md      (table format, append after translation step, authoritative)
├── characters.md    (structured + prose, append after translation, user can edit)
└── style.md         (prose + decision log table, set during init, evolves)
```

#### 3.4 — Tool set design

Tools are context too — their definitions consume tokens and their outputs flow back into the context window.

Design principles:
- **Minimal set**: if a human engineer can't clearly say which tool to use in a situation, the agent can't either. Remove ambiguity by having fewer, clearer tools.
- **Self-contained**: each tool does one thing well. No overlap between tools.
- **Token-efficient returns**: tools should return the minimum useful information, not raw data dumps. Offer a `format` parameter (summary vs full) when possible.
- **Contextual errors**: when a tool fails, the error message should help the agent recover, not just say "error."
- **Clear parameter names**: `user_id` not `id`, `search_query` not `q`.

For each tool, document:
```
Tool: [name]
Purpose: [one line]
When used: [which step/condition triggers it]
Input: [parameters with types]
Output: [what it returns, how many tokens approximately]
Error handling: [what happens on failure]
```

---

### Phase 4: Long-horizon strategy

Skip this phase if the system is single-turn or short multi-turn.

For systems that run over extended periods, context will eventually exceed the window. Choose one or more strategies:

**Compaction** — Summarize old context, reinitialize with summary.
- Best for: extended back-and-forth conversations
- Implement: preserve decisions, unresolved issues, key facts. Discard old tool outputs, redundant messages.
- Tune by: first maximize recall (capture everything relevant), then improve precision (cut noise)
- Lowest-effort version: clear old tool call results — once used, the raw output is rarely needed again

**Structured note-taking** — Agent writes notes to external files, reads them back when needed.
- Best for: iterative tasks with clear milestones (coding projects, multi-chapter processing)
- Implement: agent maintains a progress file (TODO.md, NOTES.md, project.md) and updates it at defined checkpoints
- The novel-processor skill uses this: `project.md` tracks which chapters are done, `context/` files accumulate knowledge

**Sub-agent architecture** — Split work across specialized agents with isolated context windows.
- Best for: complex research, parallel exploration, tasks with separable concerns
- Implement: lead agent coordinates plan, sub-agents execute focused tasks with clean context, return condensed summaries (1-2K tokens from potentially 50K+ of exploration)
- Key benefit: detailed search context stays isolated within sub-agents

**Decision framework:**

| Scenario | Strategy |
|----------|----------|
| Long conversations, extensive back-and-forth | Compaction |
| Iterative development with milestones | Structured note-taking |
| Complex research, parallelizable tasks | Sub-agent |
| Multi-session, accumulating knowledge | Note-taking + external memory files |
| All of the above | Combine strategies by layer |

See `references/strategies.md` for implementation details.

---

### Phase 5: Assemble the Context Architecture Document

Combine outputs from all phases into a single document. Use this template:

```markdown
# Context Architecture: [System Name]

## Task Profile
[from Phase 1]

## Context Budget
[table from Phase 2]

## Context Structure

### Static Context
- System prompt: [summary of what it contains]
- Tool set: [list of tools with one-line purposes]
- Pre-loaded data: [list]

### Dynamic Context
[table from Phase 3.2]

### External Memory
[file list with format/update rules from Phase 3.3]

### Tool Specifications
[tool docs from Phase 3.4]

## Long-Horizon Strategy
[chosen strategies and implementation plan from Phase 4]

## File Structure
[directory tree showing where everything lives]

## Context Flow Diagram
[describe or draw how context flows through the system:
 what's loaded at start → what's retrieved during execution →
 what's updated after each step → what's persisted between sessions]
```

Save the document to the project directory. This becomes the reference for implementing the system.

---

## Diagnosing existing systems

When the user has an agent that's already built but performing poorly, skip Phase 1-5 and instead:

1. **Identify symptoms**: What specifically goes wrong? (skips steps, wrong tool, forgets info, inconsistent outputs)
2. **Map to context causes**:
   - Skips steps → instructions too vague or buried in noise. Check system prompt altitude.
   - Wrong tool → tool set has overlapping purposes or ambiguous descriptions. Audit tool definitions.
   - Forgets info → no memory persistence, or context window exceeded without compaction. Check if critical info is being pushed out.
   - Inconsistent outputs → dynamic context is noisy or irrelevant data is polluting the window. Audit what's being loaded and whether it's all necessary.
   - Lost-in-middle → critical info is in the middle of a long context. Move it to beginning or end.
3. **Prescribe fix**: recommend specific changes to context structure, not model changes.

See `references/anti-patterns.md` for common context failures and their fixes.

---

## References

- `references/strategies.md` — Detailed guidance on retrieval strategies, compaction implementation, note-taking patterns, sub-agent design, and FPL integration
- `references/anti-patterns.md` — Common context failures, symptoms, causes, and fixes