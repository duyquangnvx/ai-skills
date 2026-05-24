# Subagent Design

When the generated workflow skill spawns subagents, each is defined as a markdown file under `<skill-name>/agents/<role>.md` with YAML frontmatter.

## Frontmatter

```yaml
---
name: <role-kebab-case>
description: <one-line role description used by the orchestrator's Task tool to pick the right agent>
tools: <comma-separated tool list>
model: <sonnet | opus | haiku>
permissionMode: <default | acceptEdits | bypassPermissions>
---
```

Keep the description specific. The orchestrator decides which subagent to use based on the description and the prompt — vague descriptions cause mis-routing in fan-out phases with multiple agent types.

## Tool selection

Be restrictive. Each agent gets the minimum tools it needs. A bloated tool list signals an under-specified role.

| Tool | When to grant |
|---|---|
| `Read` | Almost always |
| `Write` | When the agent produces output files |
| `Bash` | When the agent calls a helper script or uses CLI tools |
| `Grep`, `Glob` | When the agent searches the filesystem |
| `WebFetch` | When the agent fetches URLs as a fallback or primary source |
| `Task` | Only for sub-orchestrators (rare — flag for review) |

Avoid granting `Write` to judgment-only agents (classifiers, reviewers) — they should output their decision via the single success file the orchestrator polls, not write arbitrary files.

## Model selection

| Model | When |
|---|---|
| `haiku` | Light classification, simple extraction, parallel-heavy phases where cost matters |
| `sonnet` | Default for most agent roles — good balance of cost and reasoning |
| `opus` | Complex judgment, multi-step reasoning, generation tasks |

For headless runs spawning many agents in parallel, prefer haiku or sonnet over opus. The orchestrator itself may run on opus to do the coordination — that is a separate choice from per-agent models.

## permissionMode

- `default` — agent asks before file edits. Use for interactive runs and when granting `Write` to less-trusted agents.
- `acceptEdits` — auto-approve edits within the workspace. Use for trusted producers (scanners writing to `data/`).
- `bypassPermissions` — for headless containers with restricted credentials. Use when the entire pipeline runs unattended inside a sandbox.

For workflow-skill output that targets headless mode, default to `bypassPermissions` because workflow skills are typically run in dedicated environments. The user can downgrade to `default` for interactive runs.

## Anti-coding instruction

For judgment agents (read-and-decide roles), include this in the agent body:

```markdown
At no point should you Write a script to perform the analysis. If you think
you need to write code to answer the question, you have misunderstood — re-read
the input and reason about it directly.
```

This stops classifiers from trying to write analysis scripts when they should just be reading the input and producing a judgment.

## Agent body shape

```markdown
---
<frontmatter>
---

# Role: <role>

## Purpose
<one paragraph>

## Input
<exact path or format the agent receives>

## Output
Write exactly one file: `<output path pattern>`.
On any error, write `<output path>.error` with the error message.

Write atomically:

  echo "$RESULT" > "$OUT.tmp" && mv "$OUT.tmp" "$OUT"

## Procedure
1. <step>
2. <step>
3. <step>

## Output schema
<JSON schema or markdown structure>

## Anti-coding rule (judgment agents only)
<the anti-coding block above>
```

## When NOT to spawn a subagent

- The work is purely mechanical — call a helper script from the orchestrator directly.
- The work is small enough to fit in the orchestrator's context.
- The work modifies shared state that other phases depend on — subagents can't easily coordinate writes.

A phase with three agents and three helpers is usually two phases plus a refactor of one helper. Push back when the user proposes too many agents for one phase.
