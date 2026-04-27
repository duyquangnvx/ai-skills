# Context Strategies — Detailed Implementation

## Table of contents
1. Retrieval strategies (pre-loaded, just-in-time, hybrid)
2. Compaction
3. Structured note-taking
4. Sub-agent architecture
5. FPL integration for system prompts
6. Filesystem-as-memory pattern

---

## 1. Retrieval strategies

### Pre-loaded context

Load into context at session start. Best for small, always-relevant data.

When to use:
- Data is under ~1000 tokens
- Agent needs it on almost every turn
- Data changes rarely (per session or less)

Examples: system rules, user profile, project config, glossary of terms

Implementation:
```
# At session start, inject into system prompt or first message:
<project_context>
  <user_profile>{{user_profile}}</user_profile>
  <glossary>{{glossary}}</glossary>
  <style_guide>{{style_guide}}</style_guide>
</project_context>
```

Risk: if too much is pre-loaded, it consumes budget even when irrelevant. Regularly audit — does removing this item degrade output?

### Just-in-time context

Agent retrieves data dynamically using tools when a specific need arises.

When to use:
- Data is large (documents, databases, file trees)
- Only a subset is needed per turn
- Data structure provides navigation cues (file names, folders, timestamps)

Examples: codebase navigation, document search, API calls, database queries

Implementation pattern:
```
Step 1: Agent receives task
Step 2: Agent uses lightweight discovery tool (ls, glob, grep, search)
  → Returns file names, snippets, metadata — NOT full content
Step 3: Agent identifies relevant items from discovery results
Step 4: Agent loads specific items (read_file, fetch_document)
  → Only the items needed for the current decision
Step 5: Agent acts on loaded content
```

This mirrors how humans work: we don't memorize the whole codebase, we navigate to the right file and read it.

Key enabler: **metadata as context signal**. File names, folder structure, timestamps, and file sizes all give the agent navigation cues without loading content. A file named `test_utils.py` in `tests/` tells the agent something different than the same name in `src/core/`.

### Hybrid context

Pre-load lightweight summaries/indexes. Enable just-in-time retrieval for details.

When to use: most real systems. This is the default recommendation.

Implementation pattern:
```
Pre-loaded at session start:
  - Project summary (what this project is, key decisions made)
  - File index or table of contents (names + one-line descriptions)
  - Key entity list (names, IDs — no details)

Available just-in-time:
  - Full file contents (loaded via read_file when needed)
  - Detailed entity data (loaded via search/query when needed)
  - Historical data (loaded via log search when needed)
```

Example — Claude Code uses this:
- CLAUDE.md is pre-loaded (project context, rules)
- Codebase is navigated via glob/grep just-in-time
- This avoids stale indexing and complex syntax tree issues

---

## 2. Compaction

When context nears the window limit, summarize and reinitialize.

### What to keep vs discard

| Keep (high priority) | Discard (low priority) |
|---|---|
| Architectural decisions and rationale | Old tool call raw outputs |
| Unresolved issues / active bugs | Redundant conversational messages |
| Current implementation state | Superseded information |
| Key facts discovered | Exploratory dead-ends |
| User preferences expressed | Verbose error logs (keep summary) |

### Implementation steps

1. Detect context approaching limit (~80% of window)
2. Pass full message history to model with compaction prompt:
   ```
   Summarize this conversation preserving:
   - All decisions made and their rationale
   - Current state of the task
   - Unresolved issues
   - Key facts and data discovered
   - User preferences and constraints expressed

   Discard:
   - Raw tool outputs (keep conclusions only)
   - Redundant back-and-forth
   - Superseded information

   Format as structured sections:
   ## Decisions Made
   ## Current State
   ## Open Issues
   ## Key Facts
   ## User Preferences
   ```
3. Start new context with: system prompt + compaction summary + last 5 messages + recently accessed files

### Tuning process

1. First pass: maximize **recall** — make sure compaction captures everything that matters
2. Second pass: improve **precision** — remove content that doesn't affect downstream decisions
3. Test: run agent on a complex task, trigger compaction, verify agent continues coherently

### Lightest-touch compaction: tool result clearing

The safest form of compaction is simply clearing old tool call results from message history. Once a tool has been called and the agent has acted on the result, the raw output is rarely needed again. Replace with a one-line summary:

```
Before: [full 2000-token API response]
After: "[Tool result cleared. Summary: found 3 matching records, selected record #42]"
```

---

## 3. Structured note-taking

Agent writes persistent notes outside the context window. Reads them back when needed.

### When to implement

- Task spans more than ~20 tool calls
- Task has clear milestones or checkpoints
- Information accumulates over time (discoveries, decisions, entity lists)
- Multiple sessions need continuity

### Note file patterns

**Progress tracker** (like project.md in novel-processor):
```markdown
# Project Status
Current phase: Phase 2 - Implementation
Completed: Steps 1-4
Next: Step 5 - Integration testing
Blockers: None

## Checkpoint Log
- [timestamp] Completed database schema design
- [timestamp] API endpoints implemented (8/12)
```

**Decision log** (like style.md):
```markdown
# Decisions
| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| Auth method | JWT | Stateless, scales horizontally | 2025-01-15 |
| DB | PostgreSQL | Team expertise, JSONB support | 2025-01-15 |
```

**Entity registry** (like glossary.md / characters.md):
```markdown
# Entities
| ID | Name | Type | Key attributes | First seen |
|----|------|------|---------------|------------|
| E001 | UserService | Service | handles auth, profiles | Sprint 1 |
```

### Update discipline

Define explicit update triggers — don't leave it to the agent's judgment:
- After completing each major step → update progress tracker
- After making a design decision → update decision log
- After discovering a new entity/term → update entity registry
- At session end → write session summary

---

## 4. Sub-agent architecture

Split work across specialized agents with isolated context windows.

### When to use

- Task has separable concerns (research + analysis + writing)
- Parallel exploration is valuable (searching multiple sources)
- Deep exploration generates too many tokens for one context (50K+ of search results condensed to 2K summary)

### Implementation pattern

```
Lead Agent (coordinator):
  Context: high-level plan + sub-agent summaries
  Role: decompose task, dispatch to sub-agents, synthesize results

Sub-Agent A (specialist):
  Context: clean window + specific sub-task instructions
  Role: deep exploration in focused domain
  Returns: condensed summary (1-2K tokens)

Sub-Agent B (specialist):
  Context: clean window + different sub-task
  Role: parallel exploration
  Returns: condensed summary (1-2K tokens)
```

### Key principle: context isolation

Each sub-agent's detailed work stays in its own context. The lead agent only sees summaries. This prevents context pollution — 50K tokens of raw search results never enter the coordinator's window.

### Communication via filesystem

For Claude Code / CLI environments, sub-agents communicate through files:
```
workspace/
├── plan.md              ← lead agent writes plan
├── sub-task-a/
│   ├── instructions.md  ← lead agent writes sub-task spec
│   └── results.md       ← sub-agent writes findings
├── sub-task-b/
│   ├── instructions.md
│   └── results.md
└── synthesis.md         ← lead agent combines results
```

---

## 5. FPL integration for system prompts

When the agent follows a complex workflow, use Flow Prompt Language (FPL) for the system prompt's instruction section. FPL structures instructions as executable workflow specifications rather than free-form text.

Key principle: agent instructions should be workflow specifications, not intent descriptions.

When to apply FPL within context architecture:
- Agent has multi-step processes with branching logic
- Agent must call tools at specific points
- Agent behavior must be deterministic and auditable

FPL building blocks (brief — see FPL skill for full reference):
- `## MAIN FLOW` — primary process
- `### SUB_FLOW` — conditional branches
- `## TRIGGER FLOW` — interrupt handlers
- `#### ROUTINE` — reusable logic blocks
- Numbered steps with explicit If-Then-Otherwise conditions

FPL fits into the "Static Context → System Prompt" layer of the context architecture. It doesn't replace context engineering — it's one tool within it, specifically for the instruction layer.

---

## 6. Filesystem-as-memory pattern

The filesystem is a natural context management system. Agents with file access can use it as unlimited external memory.

### Why filesystem works well for agents

- Single interface for store, retrieve, update (read/write/append)
- Hierarchical organization provides structure
- Metadata (names, paths, timestamps, sizes) gives navigation cues without loading content
- Standard tools (ls, grep, glob, cat, head) enable targeted discovery
- No additional infrastructure needed (unlike vector DBs or knowledge graphs)

### Pattern: scratchpad files

For intermediate results that are too large for context but needed later:

```
Agent receives large API response (5000 tokens)
  → Writes to workspace/api_response_raw.json
  → Keeps in context only: "API returned 42 records, saved to workspace/api_response_raw.json"
  → Later, if specific records needed: reads file with head/grep to extract just those records
```

This is **observation masking** — replacing verbose tool outputs with lightweight references, loading full data only when needed again.

### Pattern: cross-session state

For agents that run across multiple sessions:

```
project/
├── .state/
│   ├── session_log.md      ← append-only log of what happened each session
│   ├── current_status.md   ← overwritten each session with latest state
│   └── decisions.md        ← append-only decision record
├── data/                   ← working data files
└── outputs/                ← produced artifacts
```

At session start: agent reads `.state/current_status.md` to resume.
At session end: agent updates status and appends to session log.