# Process: Evals and Safety

Use this when a tool design needs evidence, iteration, or safety review.

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

### Destructive Actions

For delete, overwrite, send, publish, payment, permission, or external side-effect tools:

- Make the action obvious in the name.
- Provide dry-run or preview where useful.
- Require user confirmation for high-stakes effects.
- Validate permissions server-side.
- Return clear, bounded summaries of what changed.

### MCP-Style Annotations

When the runtime supports annotations, use them:

- `readOnlyHint`
- `destructiveHint`
- `idempotentHint`
- `openWorldHint`
- human-readable `title`

Treat these as hints, not guarantees. Annotations from untrusted servers can be wrong or malicious. Client policy, sandboxing, authorization, and network controls are where hard guarantees belong.

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
