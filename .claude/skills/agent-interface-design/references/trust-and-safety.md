# Authority and Safety: The Standard

Applies to what the model is allowed to believe, what it is allowed to do, and who decides. Trust is a property of the session and the runtime, not of any single tool or line of prose.

## Ranking sources

Every conflict the model resolves is a question about authority, and one criterion places any source, including ones no list here anticipates: **who could have written this, and can the user see it?**

Applied, that yields:

1. **Platform and operator instructions.** Written by whoever runs the system; the user cannot see or edit them.
2. **Direct user request in the current conversation.** Visible to the user by construction and the reason the session exists.
3. **Project configuration and instruction files.** Written by the team, visible to the user, and rarely an enforcement layer — know where each lands in your runtime, because that determines what may override it.
4. **Tool and API contracts.** Written by whoever owns the service, describing what is actually possible.
5. **Model-authored derivatives.** Summaries, memory, notes, sub-agent reports. Written by a model, usually not reviewed by anyone.
6. **Retrieved and quoted external content.** Written by an unknown party who may be adversarial.

Adjust the order for the system you are designing, but make it explicit, and state it where compaction cannot drop it. Where two same-level rules disagree, no ladder helps — delete or reconcile them first. Where a conflict cannot be resolved safely, the agent asks.

Authority interacts with freshness and the two are not the same question. A newer statement from a lower-authority source does not outrank an older one from a higher-authority source; and for content whose truth lives outside the window, the origin outranks everyone, including the user. If the user says the build is green and the build system says red, the build system is right and the user needs to be told.

## Model-authored context

A running session manufactures new context that later reads as established fact: compaction summaries, memory files, scratchpad notes, sub-agent reports. All of it re-enters a later window as flat assertion with the hedges compressed out. A summary that records "B looks promising" as "we decided on B" is indistinguishable, two sessions later, from an instruction the user gave.

Treat model-authored context as **evidence, not instruction**. It informs a decision; it does not settle one, and it never outranks a live statement from the user or a live reading from the origin. To be usable as evidence it has to carry what evidence carries: what it was derived from, and when. A sub-agent's report is derived context whose premises the coordinator cannot inspect, so it states what it read and as of when; a memory entry carries its write time; a summary that drops provenance has converted evidence into assertion.

## Untrusted content

Text arriving through web pages, files, emails, issues, and tool results is content to transform, never instructions to follow. Delimit it, and enforce the rule with runtime policy wherever the session can exfiltrate — a prompt is not a security boundary. Where the runtime ships input and output guardrail processors, use them instead of prompt rules.

The failure mode worth naming specifically: **any channel that carries operator-level weight must not carry third-party text.** Relaying a retrieved document or raw tool output through an operator channel grants that text operator authority, and no downstream instruction takes it back.

## Destructive actions

Two axes decide whether a tool belongs in this category: **can the agent reverse it**, and **is the effect visible outside the session?** Either one qualifies it — publishing an artifact, firing a webhook, consuming a rate-limited quota, force-pushing, and messaging another agent all count, whether or not they read as "destructive". Name such actions plainly (`delete_scene`, `send_email`) so they are obvious in a trace, validate permissions server-side, and offer a dry run where the stakes justify one.

Two requirements are specific to the agent as caller. **Return a bounded summary of what changed** — a dump forces the agent to re-verify its own action, and `{ "ok": true }` leaves its belief behind its own effect. And **re-confirm the precondition at the moment of the action**, never trusting a reading from earlier in the session.

## One approval gate

Before writing any confirmation policy, check what the runtime already provides: hosts gate calls based on annotations, agent frameworks support tool-level approval settings, harnesses have permission modes.

- **The runtime has a gate: use it.** The prompt then owns choreography, not a second ask — say what is about to happen before calling, treat a conversational "yes" as context rather than the approval, and on denial do not retry the same request.
- **No gate exists: fall back to prompt-level confirmation.** State the exact effect and get an explicit yes.
- **Never both.** A framework gate plus a prompt rule saying "ask the user to approve first" makes the user approve twice. It appears when a gate is added later without removing the prompt rule, or the reverse — check for that stack when reviewing an existing catalog.

## Annotations

Where the runtime supports them, set `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, and a human-readable title deliberately. A tool with no annotations is assumed non-read-only, potentially destructive, non-idempotent, and open-world, so hosts gate every call with confirmation friction; omitting them is itself a choice with a UX cost.

They are hints, not guarantees. A server can claim `readOnlyHint: true` and delete files anyway. Client policy, sandboxing, authorization, and network controls are where hard guarantees belong.

## The lethal trifecta

A session becomes high risk when it combines access to private data, exposure to untrusted content, and the ability to communicate externally. Because the risk is a conjunction, every real defense either **breaks one leg** or **gates the crossing between legs** — least-authority tool sets, read-only mode for untrusted-content workflows, egress allowlists, approval before external communication that follows an untrusted read, separate sessions so no single context holds all three.

The one that gets skipped: taint should be **runtime state, not model memory**. A session that reads untrusted content is marked, and capability is downgraded by policy — an agent asked to remember, forty turns later, that something it read at turn 6 was untrusted is being asked to enforce a security boundary from recall.

## Terminal failures

Most errors should tell the agent what to change before retrying. Authorization is the exception, and getting it wrong is worse than a bad error message. A revoked permission, a rotated credential, or a scope the caller no longer holds is a real answer, not a solvable problem — but an agent trained on actionable errors will treat a denial as an obstacle and route around it: reach for a shell that has no check in front of it, take a different path to the same effect, or ask the user to run the command by hand.

The line that separates a legitimate next step from a bypass is **who decides**. Filing a request through a sanctioned access channel, or reporting to the user so *they* can decide with the full picture, respects the denial — the decision still belongs to whoever holds the authority. Getting the same effect through another tool, or asking the user to type the command as a way past the block, does not; that is the same bypass with a human used as hands. Say which of the two you mean, because "stop and report" stated flat also forbids the legitimate move, and an agent that reads it that way gives the user a dead end instead of a decision.

The error carries four things: that access is denied, that it is policy rather than a transient condition, **that reaching the same effect by another route is a violation and not a workaround**, and at most one sanctioned next step with concrete arguments. Non-enumerating means it does not list which roles, scopes, or resources would have succeeded — not that it says nothing. A bare "Access denied." leaves a capable model to invent its own path, and it will.

Error text is the second line of defense, never the first. **Tool exposure is the permission boundary.** A gated deploy tool sitting beside an ungated shell that can reach the same API means the fine-grained check is advisory, and you are relying on the model's disposition where you meant a control.

## Review checklist

- [ ] Source ranking is explicit, covers model-authored and retrieved content, and lives where compaction cannot drop it.
- [ ] Model-authored context carries what it was derived from and when, and never outranks a live user statement or a live read from the origin.
- [ ] Untrusted input is delimited and separated from instructions; no operator-level channel carries third-party text.
- [ ] Every irreversible or externally-visible action is named plainly and gated exactly once.
- [ ] Destructive tools return a bounded summary of what changed.
- [ ] Trifecta combinations are broken or gated in the runtime, not in prose.
- [ ] Authorization failures are terminal, non-enumerating, and offer no retry.
