# The Context Runtime: The Standard

Applies to what enters the model's context window and when: load policy, retrieval, message history, memory, compaction, and cache-aware request layout. The static surfaces (instructions, tool contracts) have their own standards; this one governs how they and everything else are assembled at runtime.

## Contents

- Load policy
- Cache-aware request layout
- Compaction
- Memory outside the window
- Sub-agent context isolation
- Review checklist

## Load policy

More context does not mean better answers: attention is a finite budget, and answer quality degrades as the window fills — context rot. Prefer the smallest high-signal set that lets the model make the next decision.

Three loading strategies, by data shape:

- **Preload** what is small, needed nearly every turn, and rarely changes: core rules, user profile, glossary, a project index. Audit each preloaded item — if removing it doesn't degrade output, remove it.
- **Just-in-time** for large or conditional data: the agent holds lightweight identifiers (file paths, stored queries, links) and loads content through tools when a need arises. Discovery tools return names, snippets, and metadata — not full content; follow-up tools load exact items. File names, folder structure, and timestamps are navigation signal the agent uses without loading anything.
- **Hybrid** is the default for real systems: preload a small map or summary, retrieve details just in time.

Retrieved chunks carry source, timestamp or version, and enough surrounding context to avoid misleading fragments. Semantic similarity is not task relevance — limit chunk count (a few focused chunks beat many noisy ones) and filter for whether a chunk helps the current question before injecting it.

## Cache-aware request layout

Prompt caching (prefix caching in inference engines, context caching in some provider APIs) reuses computation for a stable request prefix. The request is a hierarchy — tools, then system, then messages — and a change at any level invalidates that level and everything after it. Layout rules:

- Static content first: tool definitions, system instructions, reference context, examples. Per-request content after it.
- Keep the prefix byte-stable. A timestamp, request ID, or per-user counter in the system prompt breaks the cache on every request; put volatile data in the latest user message instead.
- Append, don't rewrite. Message history edits invalidate everything after the edit point; summaries and state updates go in new messages.
- Where the API takes explicit cache breakpoints, place one on the last block that is identical across the requests that should share the cache.
- Swapping the active tool set mid-session invalidates the whole cache. Change it only when the gain beats the cache cost — the same tradeoff as dynamic per-request enums in schemas.

When instructions are functions of runtime state (per-request context, per-step overrides), keep the stable core static and cacheable, and inject per-run data as a clearly delimited data block near the end of the prompt rather than woven into instruction prose. Injected data that originates outside the system is untrusted content, not instructions. Prefer appending step state as messages over rewriting the system prompt each step.

Within the window, attention is strongest at the beginning and end: critical rules go early, current task data near the generation point, and for very long contexts the one or two critical rules bear repeating near the end.

## Compaction

When history grows, summarize and reinitialize. Keep decisions and their rationale, unresolved issues, current state, key discovered facts, and user constraints. Drop raw tool outputs, redundant back-and-forth, superseded facts, and exploratory dead ends. Tune for recall first — a compaction that loses a design decision causes the agent to revert it later — then trim for precision.

The lightest-touch form is tool result clearing: once the agent has acted on a tool result, replace the raw output with a one-line summary. Gradual degradation over a long session usually comes from accumulated debris rather than any single item, so clear on a schedule instead of waiting for the window limit.

## Memory outside the window

Structured note-taking — agentic memory — survives compaction and sessions; the context window does not. Define memory as a write path, not just extra context:

- **Store**: decisions with rationale, progress state, entity registry, user preferences, open issues.
- **Write triggers**: after a milestone, a design decision, a discovered entity, or session end — explicit triggers, not agent judgment.
- **Read triggers**: session start, and before decisions that depend on history.
- **Conflict rule**: newer user statements override older memory unless an authoritative system record says otherwise.
- **Privacy**: store sensitive data only when the product requires it and policy permits it.

The filesystem is a natural memory substrate: one interface for store, retrieve, and update; hierarchy and file metadata give navigation cues; standard tools give targeted discovery. Useful patterns:

- Scratchpad files for oversized results: write the full payload to a file, keep only a one-line pointer in context, re-read selectively later — observation masking.
- Cross-session state: a current-status file overwritten each session, an append-only decision log, a session log. Read status at session start; update at session end.

## Sub-agent context isolation

Split work across sub-agents when deep exploration would flood one window. Each sub-agent explores in its own context and returns a condensed summary; the coordinator sees summaries, never raw exploration. Where the runtime supports it, communicate through files: the coordinator writes task specs, sub-agents write findings, and the coordinator synthesizes.

## Review checklist

- [ ] Every preloaded item earns its place; large or conditional data loads just in time via discovery-then-load.
- [ ] Retrieved chunks are few, relevant, and carry source and version.
- [ ] The request prefix is byte-stable; volatile data sits after the last stable block; history is append-only.
- [ ] Compaction preserves decisions, open issues, and state; acted-on tool results are cleared or summarized.
- [ ] Memory has explicit write and read triggers and a conflict rule.
- [ ] Sub-agents return summaries, not raw exploration.
