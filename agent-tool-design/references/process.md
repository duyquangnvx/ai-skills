# Process: evaluation and safety

Operational concerns that apply to every tool system. Read when the user is setting up evals, iterating with measurement, or dealing with destructive or sensitive actions.

## Contents

1. The evaluation-driven improvement loop
2. Safety annotations (MCP)
3. The lethal trifecta threat model

---

## 1. The evaluation-driven improvement loop

Anthropic's core methodology — and the most reliable way to get tools right — is evaluation-driven. The raw model is not the bottleneck; the tool layer is. And you can only improve what you measure.

### The loop

1. **Prototype.** Stand up the tool quickly, wire it into a local MCP server or direct API test, try it hands-on. Collect feedback from real or realistic users to build intuition about the prompts the tool needs to serve.

2. **Generate eval tasks.** Realistic, multi-step tasks grounded in real data sources. Anthropic reports strong vs. weak task patterns:

   Weak (don't stress-test enough):
   - "Schedule a meeting with jane@acme.corp next week."
   - "Search the payment logs for `purchase_complete` and `customer_id=9182`."

   Strong (exercise multiple tools and real reasoning):
   - "Schedule a meeting with Jane next week to discuss our latest Acme Corp project. Attach the notes from our last project planning meeting and reserve a conference room."
   - "Customer ID 9182 reported being charged three times for a single purchase attempt. Find all relevant log entries and determine if any other customers were affected by the same issue."

   Each prompt needs a verifier — exact string comparison, regex, or LLM-as-judge. Avoid over-strict verifiers that reject correct responses due to formatting differences.

3. **Run programmatically** with an agentic loop (while loop alternating LLM + tool calls). One loop per task. In the evaluation agent's system prompt, instruct it to output reasoning and feedback *before* tool calls — this triggers chain-of-thought and makes the traces much more diagnostic. If running on Claude, interleaved thinking gives similar benefit off-the-shelf.

4. **Collect metrics** beyond accuracy: total runtime per task, total tool-call count, total token consumption, tool error rate. These reveal redundant-call patterns (rightsize pagination), high-error parameters (fix descriptions), and tool-use efficiency problems.

5. **Analyze.** Read transcripts. Watch where the agent gets stumped, which tools it avoids, which ones it misuses. Agents often don't say explicitly what confused them — read between the lines. What the agent *omits* from its reasoning is often more important than what it includes.

6. **Iterate.** Small description edits often yield dramatic gains. Anthropic reported that tool-description refinements alone moved Claude Sonnet 3.5 meaningfully on SWE-bench Verified — no model change.

### Let agents improve their own tools

Anthropic's power move: paste entire eval transcripts into Claude Code and ask it to refactor the tools. Models are good at analyzing their own traces and proposing tool improvements. This creates a self-improving loop on the tool layer, orthogonal to improvements in the underlying model.

### Hold out a test set

Always separate training and test sets. Iteration on the training set can overfit to quirks — a tool description tuned to pass ten specific prompts may regress on everything else. Anthropic's internal work on Slack and Asana tools used held-out test sets to verify that gains generalized.

### Metrics to watch

- **Accuracy** — did the agent complete the task correctly?
- **Total tokens** — high token use with high accuracy suggests consolidation opportunities (chained calls that could be one tool).
- **Tool-call count** — spikes suggest redundant reads (bad pagination) or confusion (wrong tool, re-try).
- **Tool error rate** — invalid-parameter errors usually mean a description or schema needs work.
- **Runtime** — user-experience proxy; long-tail spikes often indicate retry loops.

---

## 2. Safety annotations (MCP)

MCP formalized a small set of tool annotations worth considering in any tool system, not just MCP:

- `readOnlyHint` — tool does not modify state (like a GET).
- `destructiveHint` — tool may make significant, potentially irreversible changes.
- `idempotentHint` — calling twice with the same arguments has the same effect as once.
- `openWorldHint` — tool touches external systems whose state changes unpredictably between calls.
- `title` — human-readable display name for UI.

### Two critical caveats

**Annotations are hints, not guarantees.** The MCP spec is explicit: clients MUST treat annotations from untrusted servers as untrusted. Use them to inform UI decisions (e.g., "show a confirmation prompt for destructive calls") and agent strategy — but not to enforce security. Trust the server; verify server-side.

**Clients should ignore annotations from untrusted servers entirely.** This is the compromise position that made it into the spec. A self-reported "read-only" hint from a malicious server is worthless. Base trust on how the server was installed, who runs it, and whether it's behind authentication — not on what it says about itself.

### Regardless of MCP

Destructive tools (delete, overwrite, send-email, make-payment) should be:

- **Named so destructiveness is obvious.** `delete_scene`, not `update_scene(data=null)`. The agent's tool-selection reasoning reads names first.
- **Called out in the system prompt** as "confirm before calling" where appropriate.
- **Offered with a dry-run or preview mode** when the stakes are high. "Show me what this would delete" before "actually delete it."

---

## 3. The lethal trifecta threat model

Named by Simon Willison, this is now a widely-used threat model for agent tool systems:

> An agent session that combines **(a) access to private data**, **(b) exposure to untrusted content**, and **(c) the ability to externally communicate** is at risk of prompt-injection exfiltration.

The attack mechanism is simple: LLMs follow instructions in content, and they can't reliably tell a user's instructions apart from ones an attacker embedded in a web page, email, calendar invite, or document. If all three legs are present in one session, a malicious instruction can direct the agent to read private data and send it elsewhere.

### What this means for tool design

The trifecta is a **property of the session**, not of any single tool. An individual tool being "safe" doesn't help if the session loads two other tools that complete the triad. Practical implications:

- **Notice combinations.** A CRM integration + a web-fetch tool + an email-send tool is the triad. A code-execution tool with unrestrained shell access can single-handedly be "(c)" since shell access enables exfiltration over network.
- **Gate the combinations, not just the tools.** Some systems add session-level policy: if the context is "tainted" (the agent has read any untrusted content), require explicit human approval before any action with exfiltration potential.
- **Annotation proposals for this.** Some MCP clients are exploring annotations like `reads_private_data`, `sees_untrusted_content`, `can_exfiltrate`, with runtime rules that refuse to allow all three in a single tainted execution path. This is largely unshipped as of 2026, but the conceptual framing is useful even without formal annotations.

### Practical defenses

- **Separate contexts.** Split tasks across sessions so no single context accumulates all three legs.
- **Human-in-the-loop confirmation.** For any action with exfiltration potential after the agent has seen untrusted content, require user confirmation.
- **Egress allowlists.** If the agent can only talk to pre-approved domains/endpoints, exfiltration is constrained.
- **Read-only modes.** For sessions dealing with untrusted content, restrict the agent to read tools only. GitHub's MCP has a read-only mode enabled by about 17% of users for this reason.
- **Principle of least authority.** Each session should have only the tools it actually needs for the task at hand, not the full set.

The trifecta framing is useful because it's concrete: engineers can look at a session's tool list and ask "are all three legs present?" and know when to add a gate. That's much more actionable than generic "prompt injection is dangerous" advice.
