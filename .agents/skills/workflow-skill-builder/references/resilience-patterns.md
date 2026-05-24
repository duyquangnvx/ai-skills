# Resilience Patterns

Workflow skills are accidentally resilient — Claude reads errors and adapts. But that resilience needs structure. Five patterns are mandatory in every generated workflow skill.

## Pattern 1: Never fully fail

Every generated SKILL.md ends with this block:

```markdown
## Failure handling

- <Phase 1 component> fails: log failure, continue with others.
- <Phase 2 component> fails: try fallback, then continue.
- <Phase 3 component> fails: log failure, continue with what worked.
- <Phase 4 component> fails: log failure, keep intermediate files.

Never fail the entire skill due to individual component failures.
Always produce a pipeline report — even one that says "everything broke".
```

Why: a report saying "all 18 inputs failed because the rate-limit kicked in" is more useful than a stack trace and a half-empty `data/` directory.

## Pattern 2: Fallback chains

For each phase that can fail, the generated SKILL.md states the fallback in plain English. Shape examples (not domain-specific):

- "If the primary helper returns fewer items than scanned, use a Claude-driven fallback (WebFetch + parse) for the failed items. Tag results with `method='fallback'`."
- "If the parser fails on the response, log the raw response and continue with the items that did parse."
- "If the judgment agent returns malformed JSON, ask it to fix the format once, then mark the item as failed and skip."

Keep it to one paragraph per phase. Resist specifying retry counts and backoff math — Claude figures out the details from "retry once" or "try the fallback".

## Pattern 3: Anti-coding instruction (judgment agents)

A classifier that's "just supposed to read and decide" will sometimes try to write an analysis script. Stop this with:

```markdown
At no point should you Write a script to perform the analysis. If you think
you need to write code to answer the question, you have misunderstood — re-read
the input and reason about it directly.
```

Add this to the body of every judgment agent. Without it, the agent burns turns writing helpers it does not need.

## Pattern 4: Partial state preservation

Intermediate files must remain on disk even when later phases fail. If Phase 3 crashes, Phase 1 and Phase 2 results stay in `data/`.

Concretely:

- Each phase writes to a stable path, not a temp dir cleared on exit.
- Reruns overwrite by identifier, not append.
- The skill never deletes intermediate state on failure — only the final delivery step may clean up.

The user can rerun a specific phase by deleting that phase's directory and re-invoking the skill — the orchestrator will detect missing files and only run that phase. This is the resume protocol; see `runtime-modes.md`.

## Pattern 5: Self-improvement note

The generated SKILL.md must include a one-sentence note that the orchestrator can edit the skill when it learns something:

```markdown
If you discover that an instruction in this skill was wrong, ambiguous, or
incomplete during execution, fix it inline and continue. The fix is part of
the run — commit it back with the report.
```

This is the "development and runtime blend together" property. Without the note, agents are too conservative to edit the skill file mid-run.

## Choosing the right amount of resilience

Two anti-patterns to push back on:

- **Over-engineered**: Spec'd retry counts, exponential backoff, dead-letter queues, retry budgets. If the user proposes this, point at Pattern 2 — one English sentence captures it better.
- **Under-engineered**: A phase with no fallback and no error handling. Push the user to articulate "if this fails, what happens" — even "log and continue" is a valid answer.

The right amount is: every fan-out phase has a one-sentence fallback. Every phase has a place in the failure table at the bottom of SKILL.md. The skill ends by producing a report no matter what.
