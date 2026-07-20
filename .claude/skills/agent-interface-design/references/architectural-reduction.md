# Architecture Decisions

How much machinery the task needs: workflow vs agent, multi-agent topology, stop conditions, and tool reduction. Start minimal and escalate on evidence — sophistication is a cost, not a feature.

## Contents

- The escalation ladder
- Multi-agent: when and how
- Stop conditions are design
- Architectural reduction (case study, prerequisites, deciding)

## The Escalation Ladder

The discipline that governs tool count governs agency itself. Four rungs, each a real step up in latency, spend, and debuggability:

1. **Single call** — one model call with the right context.
2. **Workflow** — fixed steps composed in code (chain, route, parallelize); the model fills in steps, code decides the path.
3. **Agent loop** — the model decides the path: which tool, when to stop. Buy it only for open-ended tasks where step count and order cannot be predicted.
4. **Multi-agent** — several loops with separate contexts.

Climb a rung only when evals show the rung below failing, and name the failure that justified the climb. The common error is starting at rung 3 or 4 for a task a workflow serves predictably.

## Multi-Agent: When and How

Sub-agents cannot see each other's decisions, and every action carries implicit decisions — two writers with separate contexts produce conflicting work. The reconciling heuristics:

- **Parallelize reads, not writes.** Research, search, review, and evaluation fan out well; work whose outputs must form one coherent artifact (one codebase, one document) stays single-threaded with full shared context.
- **Scale effort to complexity.** A simple lookup is one agent making a handful of tool calls; spawn many sub-agents only for genuinely divisible, read-heavy work — and state the budget in the task brief.
- **The orchestrator is taught, not assumed.** Delegation quality is prompt content: each sub-agent brief must be self-contained (the agents-as-tools standard in `tool-patterns.md`), because the sub-agent knows nothing the brief doesn't carry.

## Stop Conditions Are Design

Framework step limits and budgets are backstops, not design. Decide what the loop does at the boundary:

- Give the loop an observable done condition — the same completion-criterion discipline instructions get.
- The same call failing twice with the same arguments is a signal to change strategy or stop, never to retry a third time.
- When stuck — ambiguity, repeated failure, missing access — the agent escalates with state: what it tried, what failed, what it needs. An agent that silently burns its budget retrying fails worse than one that asks.

## Architectural Reduction

Consolidation taken to its logical end: replace most specialized tools with a few primitive, general-purpose capabilities and let the model reason. Production evidence shows this can outperform sophisticated multi-tool architectures — under specific prerequisites. Treat the numbers below as one workload's results, not a universal constant.

## Case Study: Text-to-SQL Agent

Vercel rebuilt a production text-to-SQL agent ("We removed 80% of our agent's tools", Dec 2025). The original architecture used 17 specialized tools — schema search, join-path finding, catalog loading, query planning, syntax validation, and so on — each built because the team anticipated the model would get lost, make bad joins, or hallucinate table names.

The reduced architecture used two primitives:

- `execute_command`: run bash in a sandbox containing the semantic-layer files.
- `execute_sql`: run SQL against the database.

The agent explores dimension definitions, measure calculations, and join relationships with `grep`, `cat`, `find`, and `ls` over well-structured YAML/Markdown files.

| Metric | Original (17 tools) | Reduced (2 tools) |
| --- | --- | --- |
| Average execution time | 274.8s | 77.4s |
| Success rate | 80% (4/5) | 100% (5/5) |
| Average token usage | ~102k | ~61k |
| Average steps | ~12 | ~7 |

Small eval set (5 tasks) — directionally strong, statistically thin. Reproduce on your own workload before committing.

## Why Reduction Can Win

- **File systems are proven abstractions.** Models understand `grep`/`cat`/`find` deeply; standard tools behave predictably. Custom tools that wrap what Unix already solves add surface without value.
- **Specialized tools can constrain reasoning.** Pre-filtering context, constraining options, and wrapping interactions in validation solve problems the model may handle on its own — and each guardrail becomes maintenance that must be recalibrated per model update.
- **Legible data beats tool sophistication.** If the data layer is well-documented and consistently named, the model needs direct read access, not summarization layers on top.

## Prerequisites

Reduction works when all of these hold:

1. **Documentation quality is high** — well-structured files, consistent naming, clear definitions.
2. **Model capability is sufficient** — the model can navigate the complexity without hand-holding.
3. **Safety constraints permit** — a sandbox bounds what the agent can reach and modify.
4. **The domain is navigable** — the problem space can be explored through file inspection.

## When Not to Reduce

- The data layer is messy: legacy naming, undocumented joins, inconsistent structure. The model will produce faster bad queries.
- Required domain knowledge cannot be written into files.
- Security or compliance demands constrained operations.
- Workflows genuinely benefit from structured orchestration.

## Deciding

Ask, for each specialized tool: does it enable a capability the model lacks, or constrain reasoning the model could handle? Signals that reduction deserves a spike:

- More time goes to maintaining scaffolding than improving outcomes.
- Failure analysis blames tool constraints more often than model limitations.
- The model has improved meaningfully since the tools were designed.
- The data layer is already legible enough for a human to navigate by file inspection.

Build minimal architectures that benefit from model improvements rather than sophisticated ones that lock in current limitations. Start simple, add tools only when evals prove the need, and keep questioning whether each tool still earns its place.
