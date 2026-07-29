# Architecture Decisions: The Standard

How much machinery the task needs: workflow vs agent, multi-agent topology, stop conditions, and how many tools. Start minimal and escalate on evidence — sophistication is a cost, not a feature.

## The escalation ladder

The discipline that governs tool count governs agency itself. Four rungs, each a real step up in latency, spend, and debuggability:

1. **Single call** — one model call with the right context.
2. **Workflow** — fixed steps composed in code (chain, route, parallelize); the model fills in steps, code decides the path.
3. **Agent loop** — the model decides the path: which tool, when to stop. Buy it only for open-ended tasks where step count and order cannot be predicted.
4. **Multi-agent** — several loops with separate contexts.

Climb a rung only when evidence shows the rung below failing, and name the failure that justified the climb. The common error is starting at rung 3 or 4 for a task a workflow serves predictably.

## Multi-agent

Sub-agents cannot see each other's decisions, and every action carries implicit decisions. The mechanism behind that is **write skew**: each agent reads a consistent snapshot, each makes a choice that is valid on its own, and together they violate an invariant neither could see. No amount of briefing fixes it, because the conflicting information did not exist when either was briefed.

- **Parallelize reads, not writes.** Research, search, review, and evaluation fan out well. Work whose outputs must form one coherent artifact stays single-threaded with full shared context. Where concurrent writers are unavoidable, the thing that makes it safe is ownership — one writer per region of state — not coordination through prose.
- **Scale effort to complexity.** A simple lookup is one agent making a handful of calls. Spawn many sub-agents only for genuinely divisible, read-heavy work, and state the budget in the brief.
- **The orchestrator is taught, not assumed.** Delegation quality is prompt content: the brief is the sub-agent's entire context, so it carries the deliverable, the constraints, and every reference the sub-agent needs.

Isolation is the point: each sub-agent explores in its own window and returns a condensed result, so the coordinator sees conclusions rather than raw exploration. That return is derived context whose premises the coordinator cannot inspect, so it states what was read and as of when. Where the runtime supports it, communicate through files — the coordinator writes task specs, sub-agents write findings, the coordinator synthesizes.

A fact copied into several briefs is now held in several windows with no channel between them. When one sub-agent discovers it was wrong, nothing tells the others. That is a reason to keep the shared premise small and re-verified at the point of use, not a reason to build an invalidation protocol between agents.

## Stop conditions

Framework step limits and budgets are backstops, not design. Decide what the loop does at the boundary:

- Give the loop an observable done condition — the same completion-criterion discipline instructions get.
- **Retry only when the failure is plausibly transient and nothing about the call changed. Change strategy when the failure is a property of the call itself.** A rate limit, a lock, a cold cache, or an eventually-consistent read fails identically twice and succeeds on the third attempt; a malformed argument fails forever. The error contract is what distinguishes them, which is why retryability is a field the server sets rather than a count the agent keeps.
- Bound the retries that are legitimate, and escalate rather than loop. Where each attempt performs a real write, an unbounded retry is not a wasted budget — it is repeated side effects.
- When stuck — ambiguity, repeated failure, missing access — escalate with state: what was tried, what failed, what is needed. An agent that silently burns its budget fails worse than one that asks.
- **Ask when the cost of a wrong assumption exceeds the cost of the interruption and the user holds information the agent cannot obtain.** Otherwise state the assumption and proceed. Over-asking is a real failure mode, and an escape hatch phrased as "ask the user" with no threshold produces it.

## How many tools

Ask of each specialized tool: **does it enable a capability the model lacks, or constrain reasoning the model could handle?** The second kind is scaffolding that must be recalibrated every time the model improves.

Taken to its end, this is architectural reduction: replace most specialized tools with a few primitive, general-purpose capabilities and let the model reason. A production text-to-SQL agent replaced seventeen specialized tools with a sandboxed shell and a SQL executor over well-structured semantic-layer files, and got faster, cheaper, and more accurate on its own evals. Reproduce on your workload before committing; the result is a direction, not a constant.

It presupposes two conditions: the environment must be **legible enough to explore** — well-structured files, consistent naming, clear definitions, domain knowledge that can be written down — and **bounded enough to explore safely** — a sandbox, and no compliance requirement for constrained operations. Where the data layer is messy, reduction produces faster bad answers.

Signals that reduction deserves a spike, none of them derivable from the argument above because they are observations about your own project:

- More time goes to maintaining scaffolding than improving outcomes.
- Failure analysis blames tool constraints more often than model limitations.
- The model has improved meaningfully since the tools were designed.
- The data layer is already legible enough for a human to navigate by file inspection.

Build minimal architectures that benefit from model improvements rather than sophisticated ones that lock in current limitations.
