# The Context Lifecycle: The Standard

Applies to a fact's whole life in the window: how it enters, how long it stays true, how it is corrected, what survives compaction and the session, and where it sits in the request. The static surfaces have their own standards; this one governs what happens to them and to everything else once a session is running.

## Provenance

One question separates three kinds of context: **if the window and the world disagree, which one is wrong?**

- **Sourced** — a copy of something whose canonical origin is outside the window. On disagreement the window is wrong. Always re-fetchable; never to be repaired by reasoning.
- **Authored** — the window *is* the origin: a preference stated, a constraint set, a decision accepted. Nothing external for it to be stale against, so it can only be superseded by the same authority — and it is irrecoverable, gone if it leaves the window unwritten.
- **Derived** — a conclusion over other context. Validity inherited. It does not expire on a clock; it expires **when a premise changes**, and it will never re-examine itself.

Most rules below are this distinction applied at a different stage. Where a rule seems to need an exception, check whether the exception is really a different provenance.

## What enters, and how

Two orthogonal questions, and conflating them is the usual error. **Provenance and volatility decide how long a copy may be trusted. Shape and access frequency decide how it gets there.**

Preload what is needed nearly every turn and cannot change under the agent. Load large, conditional, or volatile data just in time, holding identifiers rather than content — which also avoids a whole class of staleness by never building the derived snapshot that would have to be kept in sync. Its cost is not only latency: an agent without good navigation signal and cheap lookup tools burns more context misusing them than the preload would have cost, so buying freshness this way obliges you to build those tools.

The **mixed** shape — preload a map, retrieve details on demand — fits content that is *not* dynamic: reference material, corpora, a layout that changes on the scale of releases rather than turns. The more the underlying data moves during a session, the worse the preloaded half performs, because it is the half nothing will correct.

That cut runs through a single artifact as readily as across several. A forty-term glossary of which four are used every turn is two items, not one: preload the four, leave the rest behind a lookup. Splitting by *what is actually reached for* usually saves more than splitting by kind, and it applies to instruction files, schemas, and catalogs as much as to data.

Audit each preloaded item by removing it: if output on a realistic task doesn't degrade, it wasn't earning its place. Retrieved content carries its source and an as-of marker, and enough surrounding context that a fragment cannot mislead.

Every token is paid on every turn from the moment it enters, and irrelevant content is an opportunity for a wrong decision that no window size removes. Attention thinning as the window fills is a fourth reason, and the one most likely to shrink with each model generation — plan against the other three.

## How long it stays true

Give every mutable item a **freshness horizon** — how long its copy stays true relative to how long the session runs — and then ask the question that actually decides the design: **would the agent find out if it were wrong?**

- **Write-detectable.** The agent will act on the fact through a write, and the write can check. This is the good case: hold a stable snapshot, buy freshness at the commit point.
- **Read-undetectable.** The agent reads, reasons, answers. No write, so nothing errors and nothing corrects it. **Read-only tasks are the dangerous ones for staleness**, exactly opposite to the instinct that reads are safe. A fact that is read-undetectable and whose horizon is shorter than the session must not be held durably — fetch it at the point of use and report it with its as-of.

"Point of use" is a scope, not a per-turn mandate, and the scope is **the unit of work bounded by the next consequential statement or write**. Reusing a two-turn-old value to keep discussing it is fine; carrying it across the boundary where the agent commits to something — an answer the user will act on, a write, an external message — is not. Set that boundary explicitly; left implicit it resolves to a re-fetch every turn or a snapshot that quietly lives as long as the session.

Prefer a snapshot to a refresh. An agent that re-reads its premises mid-task produces incoherent plans, because the plan written at turn 3 no longer describes the work being done at turn 20. And the window is append-only, so a refresh does not replace the old value — it puts a second one beside it. **A refresh path is the recovery after something tells the agent it is stale. It is never the detection mechanism**, because detection would require the agent to suspect a copy that looks exactly like a good one.

Detection therefore belongs in software, at the point of use:

- **The agent's own writes.** A write response that returns post-write state costs nothing extra and guarantees the agent never sees a copy older than its own action. `{ "ok": true }` is the shape that manufactures this failure.
- **Someone else's writes.** The caller hands back evidence of what it believed — a version, an etag, an opaque token — and the server refuses before applying if that belief is stale. Make the token a **required** schema field; an optional precondition protects only the callers who remember it, and the model is not that caller.
- **Time.** Where no write exists, the datum carries its own as-of stamp and the agent states it when reporting. A validity marker the model can read beats a duration nobody can pick.

A refusal caused by someone else's change is an **escalation signal, not a retry signal**. Refetch, diff, and if the conflicting change touches anything the agent intended to write, surface it. Auto-retry only where the operation commutes or the diff is disjoint from the agent's write set — otherwise the agent silently resolves a conflict a human would have wanted to see, and last-writer-wins arrives with extra steps.

When a refresh confirms a real change, correcting the value is not enough. State what was believed, what changed, which decisions came from the old value, which still stand, and which must be redone — then continue. Context repair is not effect repair: an issue already filed or a message already sent is not retracted by a newer value in the window, so a long-held fact should never be the sole basis for an irreversible external action.

Derived facts expire on a different trigger: their inputs being touched. A test result, a "this file has no callers", a "the build is broken" — each is a conclusion over state the agent then changed. Treat touching an input as the expiry event, and re-verify before claiming.

## Correcting what is already there

You cannot edit a belief in place. Editing history desynchronizes the model's own prior reasoning from the record it refers to, and invalidates the cached prefix from that point — a correctness argument and a cost argument reaching the same conclusion. A correction is always an append that **shadows**, and shadowing works only if the reader can tell it is about the same thing and that it is newer.

- **Name the key and the superseded value.** `config.timeout is now 30 (was 5)` beats `timeout is 30`: a model matching on the old token finds the record that kills it. A correction phrased as a fresh statement supersedes nothing — it adds a competitor.
- **Mark the loser, don't only outrank it.** A superseded fact left unlabelled is a distractor: topically identical to the truth, differing only in being wrong. One is enough to measurably degrade retrieval, and the damage grows with the window. Where it must stay visible, label it superseded and name what replaced it.
- **State the fact, don't issue an override.** "Files on disk changed; X is now Y" outperforms "ignore what you read earlier" — models are trained to resist instructions that appear to work against the user, and that resistance reaches operator channels too.
- **Land it where it will be read**, and carry long-lived corrections forward in whatever state the agent recites each step. A correction made at turn 6 and needed at turn 40 loses to the original unless it rides along.
- **Route it by authority.** Where the runtime has an operator-level channel that appends rather than rewrites, use it for operator facts — and keep tool output, retrieved documents, and other third-party content out of it, since putting external text there hands that text operator authority.

Do not rely on recency alone. Later-wins is a guarantee only where a provider specifies it for a specific channel; for ordinary window content there is no such guarantee, and contradictions left in place cost reasoning effort even when they resolve correctly. Rank by authority with recency as the tiebreak inside one level, and note that a *derived restatement* of a stale fact carries no independent authority however recent or confident it sounds.

## What survives

**Compaction** is where superseded beliefs actually leave the window, which makes it a correctness mechanism and not only a size-management one. Its keep/drop decision has one principle: **recoverability**. Keep what cannot be re-derived; drop what can be re-fetched cheaply.

That assigns everything without a list — authored context stays, raw sourced output goes, derived context survives only while its premises do. Recent failures stay, for two reasons pointing the same way: re-deriving a failure means re-running the failing action, and a model that can still see its own stack trace stops repeating the action that produced it. Compact a failure once resolved. Tune for recall first, since dropping a decision causes the agent to revert it later, then trim for precision.

Compaction is also a rewriter, and the one that most easily undoes the work above: it strips provenance, hardens hedged observations into flat assertions, and can drop a correction while keeping the original. Any precedence rule that lives only in message history dies at the first compaction, so it belongs in the stable instructions.

The lighter form is clearing an acted-on tool result and leaving a one-line summary. Gradual degradation over a long session usually comes from accumulated debris rather than any single item, so clear on a schedule rather than at the limit.

At a session or window boundary, prefer re-deriving state from ground truth to inheriting a summary of it. A scripted orientation — read the status file, read the log, run the smoke test — before the first action catches the failure where a fresh agent looks around, sees progress, and declares the work done.

**Memory** is context that outlives the session that verified it, which makes it the most staleness-exposed surface in the system.

- **Store authored and derived context only** — decisions with rationale, constraints, progress state, open issues, an entity registry. A memory file asserting a sourced fact is a bug factory; that fact belongs in its source and should be re-read.
- **Stamp every entry** with when it was written, so the model can discount an old one rather than reading undated content as present tense.
- **Write and read on explicit triggers**, not agent judgment: write after a milestone, a decision, a discovered entity, or session end; read at session start and before decisions that depend on history.
- **Resolve conflicts by provenance.** For authored content the latest statement from the same authority wins, so a stored preference never overrides one the user just stated. For sourced content the origin wins regardless of who said what. For derived content the premises decide.

## Request layout

This half is economics, not correctness. It shares a file with the lifecycle because the two constrain each other, and one rule resolves both directions: **layout is determined by rate of change, not by content type.**

The request is a hierarchy — tools, then system, then messages — and a change at any level invalidates that level and everything after it. Static content first, per-request content after; keep the prefix byte-stable, so a timestamp or request ID inside the cached region is a per-request cache miss. Segregate by volatility rather than trading freshness against cost: stable content in the prefix, volatile content in a small delimited late block that is cheap to replace. Injected runtime data is a bounded block near the end, never prose woven into instructions — and data arriving from outside the system is untrusted content, not instruction.

Where the runtime offers append-based mechanisms for changing operator instructions or the offered tool set mid-session, prefer them to editing the prefix; they exist precisely so a mid-session change costs one message rather than the whole conversation. Where they do not exist, treat a mid-session toolset change as expensive and expect it anyway — a server process exits, a session expires, a connection re-establishes with a different list, or the caller's authorization changes what it is allowed to see.

Placement advice worth keeping is operational: long data early, and the query and the rules governing the current turn late, near the generation point. In long loops have the agent rewrite its plan or task list each step — not as an attention trick, but because it externalizes loop state into the transcript, where it is re-read rather than remembered.

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
