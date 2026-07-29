# The Context Lifecycle: The Standard

Applies to a fact's whole life in the window: how it enters, how long it stays true, how it is corrected, what survives compaction and the session, and where it sits in the request. The static surfaces have their own standards; this one governs what happens to them and to everything else once a session is running.

## Provenance

One question separates three kinds of context: **if the window and the world disagree, which one is wrong?**

- **Sourced** — a copy of something with a canonical origin outside the window: file contents, database rows, API responses, build status, git state, another agent's output. On disagreement the window is wrong. It can always be re-fetched, and it must never be repaired by reasoning.
- **Authored** — the window *is* the origin: a preference the user stated, a constraint they set, a decision made and accepted. There is no external truth for it to be stale against; it can only be superseded by a later statement from the same authority. It is also irrecoverable — if it leaves the window unwritten, it is gone.
- **Derived** — a conclusion reached over other context: a summary, a sub-agent's report, "this module owns auth", "the parser is the problem". Its validity is inherited. It does not expire on a clock; it expires **when a premise changes**, and it will never re-examine itself.

Most rules below are this distinction applied to a different stage. Where a rule seems to need an exception, check whether the exception is really a different provenance.

## What enters, and how

Two orthogonal questions, and conflating them is the usual error. **Provenance and volatility decide how long a copy may be trusted. Shape and access frequency decide how it gets there.**

More context does not mean better answers. Every token is paid for on every turn from the moment it enters, latency scales with what you carry, and irrelevant content is an opportunity for a wrong decision that no window size removes. Attention also thins as the window fills, but treat that as the reason most likely to shrink with each model generation and the other three as the durable ones.

Three transports:

- **Preload** what is needed nearly every turn and cannot change under the agent: behavior rules, tone, output format, a glossary, stable conventions. Audit each preloaded item — if removing it doesn't degrade output on a realistic task, remove it.
- **Just-in-time** for large, conditional, or volatile data: the agent holds lightweight identifiers — file paths, stored queries, links — and loads content through tools when a need arises. Discovery returns names, snippets, and metadata; follow-up calls load exact items. File names, folder structure, and timestamps are navigation signal the agent uses without loading anything. JIT also avoids a whole class of staleness by never building the derived snapshot that would have to be kept in sync.
- **Mixed** — preload a small map, retrieve details just in time — fits content that is *not* dynamic: reference material, legal or financial corpora, a layout that changes on the scale of releases rather than turns. The more the underlying data moves during a session, the worse the preloaded half performs, because it is the half nothing will correct.

JIT is not free, and the cost is not only latency. Runtime exploration is slower than reading a precomputed answer, and an agent without good tools and clear navigation signal wastes context misusing them, chasing dead ends, or missing the thing it went looking for. Buying freshness this way obliges you to build the tools that make exploration cheap.

Retrieved content carries its source and an as-of marker, and enough surrounding context that a fragment cannot mislead. Semantic similarity is not task relevance: limit chunk count, and filter for whether a chunk helps the current question before injecting it.

## How long it stays true

Give every mutable item a **freshness horizon** — how long its copy stays true relative to how long the session runs — and then ask the question that actually decides the design: **would the agent find out if it were wrong?**

- **Write-detectable.** The agent will act on the fact through a write, and the write can check. This is the good case: hold a stable snapshot, and buy freshness at the commit point.
- **Read-undetectable.** The agent reads the fact, reasons, and answers. There is no write, so nothing errors and nothing corrects it. **Read-only tasks are the dangerous ones for staleness**, exactly opposite to the instinct that reads are safe. A fact whose staleness is read-undetectable and whose horizon is shorter than the session must not be held durably — fetch it at the point of use and report it with its as-of.

Prefer a snapshot to a refresh. An agent that re-reads its premises mid-task produces incoherent plans, because the plan written at turn 3 no longer describes the work being done at turn 20. And the window is append-only, so a refresh does not replace the old value — it puts a second one beside it. A refresh path is the **recovery** after something tells the agent it is stale; it is never the detection mechanism, because detection requires the agent to suspect a copy that looks exactly like a good one.

Detection therefore belongs in software, at the point of use:

- **The agent's own writes.** A write response that returns the post-write state costs nothing extra and guarantees the agent never sees a copy older than its own action. `{ "ok": true }` is the shape that manufactures this failure.
- **Someone else's writes.** The caller hands back evidence of what it believed — a version, an etag, an opaque token — and the server refuses the write before applying it if that belief is stale. Make the token a required schema field rather than an optional one; an optional precondition protects only the callers who remember to use it.
- **Time.** Where no write exists, the datum carries its own as-of stamp and the agent states it when reporting. A validity marker the model can read beats a duration nobody can pick.

A refusal on someone else's change is an **escalation signal, not a retry signal**. Refetch, diff, and if the conflicting change touches anything the agent intended to write, surface it. Auto-retry only when the operation commutes or the diff is disjoint from the agent's write set — otherwise the agent resolves a conflict a human would have wanted to see, and last-writer-wins arrives with extra steps.

When a refresh confirms a real change, correcting the value is not enough. State what was believed, what changed, which decisions were made from the old value, which still stand, and which must be redone — then continue. Context repair is not effect repair: an issue already filed or a message already sent is not retracted by a newer value in the window, so a long-held fact should never be the sole basis for an irreversible external action. Re-confirm at the moment of the action.

Derived facts need the same discipline with a different trigger: they expire when their inputs are touched. A test result, a "this file has no callers", a "the build is broken" — each is a conclusion over state the agent then changed. Re-verify before claiming, and treat touching an input as the expiry event.

## Correcting what is already there

You cannot edit a belief in place. Editing history desynchronizes the model's own prior reasoning from the record it refers to, and it invalidates the cached prefix from that point on — a correctness argument and a cost argument reaching the same conclusion. So a correction is always an append that **shadows**, and shadowing only works if the reader can tell it is about the same thing and that it is newer.

- **Name the key and the superseded value.** `config.timeout is now 30 (was 5)` beats `timeout is 30`: a model matching on the old token finds the record that kills it. A correction phrased as a fresh statement supersedes nothing; it just adds a competitor.
- **Mark the loser, don't only outrank it.** A superseded fact left unlabelled is a distractor — topically identical to the truth, differing only in being wrong — and a single distractor measurably degrades retrieval, with the damage growing as the window grows. Where a superseded fact must stay visible, label it as superseded and name what replaced it.
- **State the fact, don't issue an override.** "Files on disk changed; X is now Y" works better than "ignore what you read earlier". Models are trained to resist instructions that appear to work against the user, and that resistance applies to operator-level channels too.
- **Land it where it will be read**, near the generation point rather than buried mid-history, and carry long-lived corrections forward in whatever state the agent recites each step. A correction made at turn 6 and needed at turn 40 loses to the original unless it rides along.
- **Route it by authority.** Where the runtime has an operator-level channel that appends rather than rewrites — a mid-conversation system message and its tool-addition and tool-removal counterparts — use it for operator facts, and keep tool output, retrieved documents, and other third-party content out of it. Putting external text in an operator channel hands that text operator authority.

Do not rely on recency alone to resolve the conflict. Later-wins is a guarantee only where a provider specifies it for a specific channel; for ordinary content in the window there is no such guarantee, and contradictions left in place cost reasoning effort even when they resolve correctly. Rank by authority, using recency as the tiebreak within one authority level, and remember that a *derived restatement* of a stale fact carries no independent authority no matter how recent or how confident it sounds.

## What survives

**Compaction** is where superseded beliefs actually leave the window, which makes it a correctness mechanism and not only a size-management one. Its keep/drop decision has one principle: **recoverability**. Keep what cannot be re-derived; drop what can be re-fetched cheaply.

That principle assigns everything without a list. Authored context is irrecoverable by construction — decisions, rationale, constraints, open issues stay. Sourced context is recoverable by construction — raw tool outputs go. Derived context survives only while its premises do. Recent failures stay, for two reasons that point the same way: re-deriving a failure means re-running the failing action, and a model that can still see its own stack trace stops repeating the action that produced it. Compact a failure once it is resolved. Tune for recall first, since a compaction that drops a decision causes the agent to revert it later, then trim for precision.

Compaction is also a rewriter, and the one that most easily undoes the work above: it strips provenance, hardens hedged observations into flat assertions, and can drop a correction while keeping the original. Any precedence rule that lives only in message history dies at the first compaction, so it belongs in the stable instructions.

The lighter form is clearing an acted-on tool result and leaving a one-line summary. Gradual degradation over a long session usually comes from accumulated debris rather than any single item, so clear on a schedule rather than at the limit.

At a session or window boundary, prefer re-deriving state from ground truth over inheriting a summary of it. A scripted orientation — read the status file, read the log, run the smoke test — before the first action catches the failure where a fresh agent looks around, sees progress, and declares the work done.

**Memory** is context that outlives the session that verified it, which makes it the most staleness-exposed surface in the system. Define it as a write path:

- **Store** authored and derived context: decisions with rationale, constraints, progress state, open issues, an entity registry. A memory file asserting a sourced fact is a bug factory — that fact belongs in its source and should be re-read.
- **Write triggers**: after a milestone, a decision, a discovered entity, or session end. Explicit triggers, not agent judgment.
- **Read triggers**: session start, and before decisions that depend on history.
- **Stamp every entry** with when it was written, so the model can discount an old one rather than treating undated content as present tense.
- **Resolve conflicts by provenance.** For authored content, the latest statement from the same authority wins — a stored preference never overrides one the user just stated. For sourced content, the origin wins regardless of who said what: if the user says the build is green and the build system says red, the build system is right. For derived content, the premises decide.

The filesystem is a natural substrate: one interface for store, retrieve, and update; hierarchy and file metadata as navigation cues; standard tools for targeted discovery. Write oversized results to a file and keep a one-line pointer in context, re-reading selectively later.

## Request layout

This half is economics, not correctness. It shares a file with the lifecycle because the two constrain each other, and the resolution is the same rule in both directions: **layout is determined by rate of change, not by content type.**

The request is a hierarchy — tools, then system, then messages — and a change at any level invalidates that level and everything after it. So:

- Static content first: tool definitions, system instructions, reference context, examples. Per-request content after.
- Keep the prefix byte-stable. A timestamp, request ID, or per-user counter inside the cached region breaks the cache on every request; volatile data goes after the last stable block.
- Append, don't rewrite. History edits invalidate everything after the edit point; summaries, state updates, and corrections go in new messages.
- Where the API takes explicit breakpoints, place one on the last block identical across the requests that should share the cache.
- Segregate by volatility rather than trading freshness against cost: stable content in the prefix, volatile content in a small delimited late block that is cheap to replace. Injected runtime data is a clearly bounded block near the end, not prose woven into instructions — and data arriving from outside the system is untrusted content, not instruction.

Where the runtime offers append-based mechanisms for changing operator instructions or the offered tool set mid-session, prefer them to editing the prefix; they exist precisely so that a mid-session change costs one message rather than the whole conversation. Where they do not exist, treat a mid-session toolset change as expensive and expect it to happen anyway — a server process exits, a session expires, a connection re-establishes with a different list, or the caller's authorization changes what it is allowed to see.

Placement advice worth keeping is operational: put long data early, and put the query and the rules that govern the current turn late, near the generation point. In long loops, have the agent rewrite its plan or task list each step — not as an attention trick, but because it externalizes loop state into the transcript where it is re-read rather than remembered.

## Review checklist

- [ ] Every item's provenance is identified; memory holds no sourced facts.
- [ ] Every mutable item has a freshness horizon and an answer to "would the agent find out if this were wrong?"
- [ ] Read-undetectable facts with a short horizon are fetched at the point of use, not held.
- [ ] Write responses return post-write state; stale writes are refused before the effect, with the current state in the error.
- [ ] A conflict caused by someone else's change escalates rather than auto-retries.
- [ ] Corrections name the key and the superseded value, and are appended, not rewritten.
- [ ] Precedence is ranked by authority with recency as a tiebreak, and it lives in stable instructions so it survives compaction.
- [ ] Compaction keeps what cannot be re-derived and drops what can be re-fetched.
- [ ] The request prefix is byte-stable; volatile content sits in a delimited late block; history is append-only.
