# Timeout Layers

A workflow skill needs hard limits at multiple levels because agents will run forever if you let them. There are four practical layers — use whichever fit the runtime mode.

## Layer 1: `max_turns` per agent

Hard limit on Claude API round-trips inside one subagent. Set in the agent definition or per-call.

Starting points:

| Agent role shape | `max_turns` |
|---|---|
| Light extraction, single-question classification | 10–15 |
| Standard classification with reasoning | 20 |
| Multi-step research, proposal generation, multi-file edits | 30 |

When an agent hits `max_turns`, it returns whatever it has so far. The orchestrator treats this as a partial success: record what came back, mark the rest as "timeout" in the report.

Tune empirically. Watch a few real runs, then adjust per agent. Do not pick numbers in advance based on intuition.

## Layer 2: Wall-clock cap per phase

In the orchestrator's poll loop (see `filesystem-bus.md`), set a timeout in seconds. When it expires, the orchestrator moves to the next phase with whatever completed. Stragglers are marked "timeout" in the report.

Starting points:

| Batch shape | Cap |
|---|---|
| Small (< 10 agents, short tasks) | 300s (5 min) |
| Medium (10–30 agents, classification) | 600s (10 min) |
| Large or network-bound (slow enrichment, scraping) | 1200–1800s (20–30 min) |

These are starting points. Tune based on actual run times in the first few executions.

## Layer 3: Bash `timeout` on the whole job

For headless or cron runs. Wraps the entire skill invocation:

```bash
timeout 10800 claude --skill <workflow-name> "execute pipeline"
# 10800 = 3 hours
```

When this fires, the main process is killed. A second invocation (a "recovery" run) can wake up afterward to salvage partial state from disk and produce a degraded report. See `runtime-modes.md`.

Skip this layer for purely interactive runs — the user can interrupt.

## Layer 4: Container deadline

For deployed jobs. Set:

- `activeDeadlineSeconds` in the Kubernetes Job spec
- The job-level timeout in a CI runner
- The equivalent on whatever scheduler hosts the job

This is the hardest limit — it kills the container regardless of state. Always set longer than Layer 3 (e.g., 4h container vs 3h bash). The gap gives the recovery run room to produce a final report before the container dies.

## Recommended sequence by runtime mode

| Runtime | Layers to use |
|---|---|
| Interactive only | 1 + 2 |
| Background tab / long local session | 1 + 2 |
| Local cron | 1 + 2 + 3 |
| CI/CD, Kubernetes, scheduled remote agent | 1 + 2 + 3 + 4 |

## What goes in the generated SKILL.md

Inline the relevant layers as a table near the top of the skill, with the actual values used in poll loops. Example:

```markdown
## Timeout configuration

| Layer | Setting | Notes |
|---|---|---|
| max_turns per agent | 20 (classifier), 30 (proposer) | Tune per agent |
| Wall-clock per phase | 600s | Move on with what completed |
| Bash timeout | 10800s | Whole-job hard limit (headless) |
| Container deadline | 14400s | k8s activeDeadlineSeconds (deployed) |
```

Do NOT quote calendar time as a target (e.g., "should finish by Friday"). The job either finishes within the wall-clock caps or it does not — that is the contract.
