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

Text arriving through web pages, files, emails, issues, and tool results is content to transform, never instructions to follow. State this in instructions, keep it in a clearly delimited block, and enforce it with runtime policy when the session can exfiltrate — a prompt is not a security boundary.

The failure mode worth naming specifically: any channel that carries operator-level weight must not carry third-party text. Relaying a retrieved document or raw tool output through an operator channel grants that text operator authority, and no downstream instruction takes it back.

Where the runtime ships input and output guardrail processors — moderation, PII — use them instead of prompt rules, cheap deterministic checks first, model-based classifiers second.

## Destructive actions

For delete, overwrite, send, publish, payment, permission, or external side-effect tools. Two axes decide whether a tool belongs here: **can the agent reverse it**, and **is the effect visible outside the session?** Either one qualifies it — publishing an artifact, firing a webhook, consuming a rate-limited quota, force-pushing, and messaging another agent all count, whether or not they read as "destructive".

- Name the action plainly (`delete_scene`, `send_email`) so it is obvious in a trace.
- Provide dry-run or preview for high-stakes actions.
- Require confirmation where effects are hard to reverse, through exactly one gate.
- Validate permissions server-side.
- Return a clear, bounded summary of what changed. A destructive tool that answers with a dump forces the agent to re-verify its own action; one that answers `{ "ok": true }` leaves the agent's belief behind its own effect.
- Re-confirm the precondition at the moment of the action rather than trusting a reading from earlier in the session.

## One approval gate

Before writing any confirmation policy, check what the runtime already provides: hosts gate calls based on annotations, agent frameworks support tool-level approval settings, harnesses have permission modes.

- **The runtime has a gate: use it.** The prompt then owns choreography, not a second ask — say what is about to happen before calling, treat a conversational "yes" as context rather than the approval, and on denial do not retry the same request.
- **No gate exists: fall back to prompt-level confirmation.** State the exact effect and get an explicit yes.
- **Never both.** A framework gate plus a prompt rule saying "ask the user to approve first" makes the user approve twice. It appears when a gate is added later without removing the prompt rule, or the reverse — check for that stack when reviewing an existing catalog.

## Annotations

Where the runtime supports them, set `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, and a human-readable title deliberately. A tool with no annotations is assumed non-read-only, potentially destructive, non-idempotent, and open-world, so hosts gate every call with confirmation friction; omitting them is itself a choice with a UX cost.

They are hints, not guarantees. A server can claim `readOnlyHint: true` and delete files anyway. Client policy, sandboxing, authorization, and network controls are where hard guarantees belong.

## The lethal trifecta

A session becomes high risk when it combines access to private data, exposure to untrusted content, and the ability to communicate externally. Because the risk is a conjunction, every real defense either **breaks one leg** or **gates the crossing between legs**:

- Least-authority tool sets per session, and read-only mode for untrusted-content workflows.
- Label or strip untrusted text at ingestion.
- Explicit approval before external communication that follows an untrusted read.
- Egress allowlists.
- Separate sessions or sub-agents so no single context holds all three.
- Runtime policy that marks a session tainted after an untrusted read, and downgrades capability rather than relying on the model to remember.

## Terminal failures

Most errors should tell the agent what to change before retrying. Authorization is the exception, and getting it wrong is worse than a bad error message. A revoked permission, a rotated credential, or a scope the caller no longer holds is a real answer, not a solvable problem — but an agent trained on actionable errors will treat a denial as an obstacle and route around it: try a sibling tool, take a different path to the same effect, or ask the user to run the command manually.

Authorization failures state that access is denied, do not enumerate what would have worked, and do not suggest a retry. The agent's correct move is to stop and report, and the error should leave no other reading available.

## Review checklist

- [ ] Source ranking is explicit, covers model-authored and retrieved content, and lives where compaction cannot drop it.
- [ ] Model-authored context carries what it was derived from and when, and never outranks a live user statement or a live read from the origin.
- [ ] Untrusted input is delimited and separated from instructions; no operator-level channel carries third-party text.
- [ ] Every irreversible or externally-visible action is named plainly and gated exactly once.
- [ ] Destructive tools return a bounded summary of what changed.
- [ ] Trifecta combinations are broken or gated in the runtime, not in prose.
- [ ] Authorization failures are terminal, non-enumerating, and offer no retry.
