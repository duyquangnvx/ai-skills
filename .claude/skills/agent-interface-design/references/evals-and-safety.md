# Process: Evals and Safety

Use this when a tool design needs evidence, iteration, or safety review.

## Contents

- Evaluation loop
- Metrics
- Review criteria
- Cross-surface review checks
- Using agents to improve tools
- Safety and trust boundaries (destructive actions, one approval gate, MCP annotations, lethal trifecta)

## Evaluation Loop

1. **Prototype the tool set.** Wire the tools into the actual or closest available runtime. Try realistic tasks by hand before optimizing descriptions.

2. **Write realistic eval tasks.** Prefer multi-step tasks grounded in real data over single-call smoke tests.

   Weak:

   ```text
   Search the logs for customer_id=9182.
   ```

   Strong:

   ```text
   Customer 9182 says they were charged three times for one purchase. Find relevant logs, determine whether other customers were affected, and summarize the likely cause.
   ```

3. **Define verifiers.** Use exact checks, regex, deterministic assertions, or an LLM judge where needed. Avoid overfitting to a single tool-call path when multiple correct strategies exist.

4. **Run programmatically.** Use an agentic loop that records task, tool calls, tool inputs, raw tool outputs, errors, final answer, token use, latency, and retry count.

5. **Log observable diagnostics, not hidden reasoning.** If the runtime exposes reasoning summaries, use what it provides. Do not require private chain-of-thought. A useful visible diagnostic block is:

   ```text
   Goal:
   Selected tool:
   Selection reason in one sentence:
   Parameters:
   Expected result:
   Uncertainty:
   Observed issue:
   Next action:
   ```

6. **Analyze transcripts.** Look for wrong-tool calls, redundant reads, invalid arguments, oversized results, ignored errors, and places where the agent stopped early.

7. **Iterate one change at a time when practical.** Description edits, names, schemas, validation, response shape, and tool granularity can each move metrics. Re-run held-out tasks to avoid overfitting.

## Metrics

Track more than final accuracy:

- Task success.
- Tool-call count.
- Invalid-call rate.
- Token consumption.
- Latency.
- Retry count.
- User approval prompts.
- Safety blocks or policy escalations.

These metrics reveal different failure classes. High token use can suggest response bloat or too many chained calls. Invalid-call rate usually points to schema, naming, description, or validation-error problems.

## Review Criteria

When judging a tool design qualitatively — during review rather than measurement — score it against five criteria:

- **Clarity**: can an agent determine when to use this tool over its siblings?
- **Completeness**: does the contract carry every convention a caller needs (formats, defaults, side effects)?
- **Recoverability**: does every error tell the agent what to change before retrying?
- **Efficiency**: are responses bounded, with verbosity options where size genuinely varies?
- **Consistency**: do names, parameters, and enums follow the catalog's conventions?

## Cross-Surface Review Checks

Apply to every surface, alongside the per-surface checklists in `instructions.md` and `tool-patterns.md`:

- [ ] No rule, field, or workflow documented in two homes.
- [ ] Untrusted input is separated from trusted instructions.
- [ ] Heavy references, schemas, and examples load on demand.
- [ ] Changes are verified with pressure scenarios or evals, not read-throughs.
- [ ] Evals track task success, tool-call count, invalid-call rate, tokens, and latency.
- [ ] Safety gates cover destructive actions and lethal-trifecta combinations, with exactly one approval gate per destructive action.

## Using Agents to Improve Tools

Agents can review transcripts and propose tool improvements. Ask for concrete changes:

```text
Given these failed eval traces, propose:
- tool name changes
- schema changes
- response-shape changes
- validation/error changes
- developer-prompt disambiguation
- evals that would prove the fix
```

Do not accept suggestions only because they sound plausible. Apply them to the eval set and compare.

## Safety and Trust Boundaries

Tool safety is not just a property of one tool. It is a property of the session and runtime.

Conversation I/O gets the same enforce-in-software treatment as tool calls: where the runtime ships input/output guardrail processors (moderation, PII), use them instead of prompt rules, ordered cheap deterministic checks first, model-based classifiers second.

### Destructive Actions

For delete, overwrite, send, publish, payment, permission, or external side-effect tools:

- Name the action plainly (`delete_scene`, `send_email`) — obvious in a trace.
- Provide dry-run or preview for high-stakes actions.
- Require user confirmation where effects are hard to reverse — through exactly one gate (next section).
- Validate permissions server-side.
- Return clear, bounded summaries of what changed — a destructive tool that answers with a dump forces the agent to re-verify its own action.

### One Approval Gate

Before writing any confirmation policy, check what the runtime already provides: MCP hosts gate calls based on annotations, agent frameworks support tool-level approval settings, harnesses have permission modes.

- **The runtime has a gate: use it.** The prompt then owns choreography, not a second ask — tell the user what is about to happen before calling, treat a conversational "yes" as context rather than the approval (make the call and let the gate decide), and on denial don't retry the same request.
- **No gate exists: fall back to prompt-level confirmation.** State the exact effect and get an explicit yes before calling.
- **Never both.** A framework gate plus a prompt or description rule saying "ask the user to approve first" makes the user approve the same action twice. When reviewing an existing catalog, check for this stack — it appears when a gate is added later without removing the prompt rule, or the reverse.

### MCP-Style Annotations

When the runtime supports annotations, set them deliberately:

- `readOnlyHint`
- `destructiveHint`
- `idempotentHint`
- `openWorldHint`
- human-readable `title`

A tool with no annotations is assumed non-read-only, potentially destructive, non-idempotent, and open-world — hosts then gate every call with confirmation friction, so omitting annotations is itself a choice with UX cost.

Treat these as hints, not guarantees. Annotations from untrusted servers can be wrong or malicious — a server can claim `readOnlyHint: true` and delete files anyway. Client policy, sandboxing, authorization, and network controls are where hard guarantees belong.

### Lethal Trifecta

A session becomes high risk when it combines:

1. Access to private data.
2. Exposure to untrusted content.
3. Ability to externally communicate.

Do not rely on a prompt instruction alone to make this safe. Practical defenses include:

- Least-authority tool sets per session.
- Read-only mode for untrusted-content workflows.
- Explicit approval before external communication after reading untrusted content.
- Egress allowlists.
- Separate sessions or subagents so no single context gets all three capabilities.
- Runtime policy that marks a session tainted after untrusted reads.
