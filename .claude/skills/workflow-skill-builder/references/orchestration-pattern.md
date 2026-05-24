# Orchestration Pattern

The core mental model behind a workflow skill: **the document is the DAG**.

## Document order = dependency graph

A workflow skill does not declare a separate DAG in YAML or Python. Phases run in the order they appear in SKILL.md. Phase 2 depends on Phase 1 because it is written after Phase 1. The orchestrator (the main Claude Code process) reads the file top to bottom and executes.

Why this works:

- Humans read top to bottom. So does the orchestrator.
- Editing the DAG = editing the document. No second source of truth.
- Conditional phases are written as English checks at the top of the phase ("Read X. If X is empty, skip this phase.") — no formal dependency language needed.

## Fan-out via subagents

A phase that processes N items in parallel does so by spawning N subagents through the `Task` tool with `run_in_background: true`. Each subagent receives:

- A `subagent_type` matching an agent role file in `agents/`
- A prompt referencing the specific item (e.g., `"Scan source: <source-name>"`)
- The tool restrictions and model defined in the agent file

The orchestrator does NOT wait for the subagents directly. Instead it polls the filesystem for `.json` (success) or `.error` (failure) files. See `filesystem-bus.md`.

## Why not just collect agent results in-context

The naive pattern:

```
results = [Task(...) for source in sources]
```

This works for ~4 agents. At ~18 it does not — the orchestrator's context fills with returned text and starts forgetting earlier results. The filesystem bus pattern keeps the orchestrator's context at `O(n × filename)` instead of `O(n × output_size)`.

## Single vs fan-out — recognize the shape

**Fan-out shape:**

- Same operation on many items
- Items are independent
- Order within the batch does not matter

**Single shape:**

- One operation that aggregates or transforms shared state
- Or: one operation with no parallelism gain

**Mixed shape** (real but rare): a single mechanical step that produces N items, then a fan-out judgment step on those items. Split into two phases.

## Phase block shape

Each phase in the generated SKILL.md has roughly this structure (see `assets/phase-block.md.template`):

```markdown
## Phase N: <verb>

**Goal:** <one sentence>

**Inputs:** <where data comes from>

**Outputs:** <success path pattern> or <error path pattern>

### Step N.1: <action>

[Single step: invoke helper script or run an inline action.]
[Fan-out step: spawn subagents in background, then poll the filesystem.]

### On failure

<fallback action — one paragraph, English>
```

## Anti-pattern: over-engineering the DAG

Do not try to formalize dependencies. Do not introduce condition expressions like `runIf` or `dependsOn`. If a phase is conditional, write the check in English at the top of the phase body. The orchestrator handles it.

Do not introduce a separate "config" file describing the phase order. The order is the file. Adding indirection breaks the "edit the workflow = edit the document" property that makes this pattern work for non-engineers.
