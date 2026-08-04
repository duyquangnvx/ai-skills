# Platform Facts

Checkable facts a frontier model tends to get wrong or a revision behind, because they are recent, negative ("the spec has no X"), or counterintuitive. Everything else in this skill is reasoning you can re-derive; this file is the part you cannot.

**Two halves, deliberately.** The first is prior art that has been stable for decades and will not move. The second is platform state with a date on it, and it *will* be wrong — the MCP entries below are one revision old within a day of being written. Treat the second half as an as-of reading, not a standing truth: verify against the revision you target before you build on it, and prefer citing what a spec *lacks* over the exact spelling of what it has, because absences outlive method names.

---

## Durable: how the lost-update problem was already solved

Three unrelated specifications, different decades, converge on one shape — **the caller hands back evidence of what it believed, the server compares it before applying, and the request is aborted on mismatch.** That convergence is the strongest signal available that this is the right shape for an agent tool layer.

- **RFC 9110 §13.1.1** — `If-Match` with a strong validator, evaluated before the method is applied; §15.5.13, `412 Precondition Failed` "prevent[s] the request method from being applied if the target resource is in an unexpected state." §13.1 names the target: the "lost update" problem, "one client accidentally overwriting the work of another client that has been acting in parallel." Note what is validated — §13.1 frames preconditions as evaluating "whether the state of the target resource has changed since a given state known by the client." It checks the client's *belief*, not the client's data.
- **RFC 6585 §3** — `428 Precondition Required` exists because 412 alone is not enough: a caller that simply omits the precondition sails through and clobbers. Its own §7.1 concedes "The 428 status code is optional; clients cannot rely upon its use to prevent 'lost update' conflicts."
- **Google AIP-154 / AIP-134** — the RPC-shaped rendering: an ordinary `etag` field on the resource and on the request, `ABORTED` on mismatch. Same strong/weak split as HTTP.

**The design lesson, and it is the load-bearing one:** every one of these defaults to *permitting* a write that omits the precondition. HTTP without 428 permits it; AIP says "if the user does not send an etag value at all, the service should permit the request." An optional safety mechanism protects only callers who opt in — and the model is exactly the caller that will not. In a tool schema, make the version a **required** field so omission is a validation error rather than a silent bypass.

Also worth copying: RFC 9110 permits answering a re-issued change that "appears to have already been applied" with a 2xx instead of 412 — convenient for retry loops, and the RFC's own warning is the governing one for anything non-idempotent: for resources where near-identical uncooperative writes collide, "an origin server is better off being stringent in sending 412 for every failed precondition."

---

## Dated: platform state

*Read against MCP revision `2026-07-28`; Claude Code docs and Anthropic platform docs as of 2026-07-29. Verify before relying.*

### MCP has the push half and none of the pull half

- **No conditional-write machinery of any kind.** No etag, no version field, no precondition parameter on `tools/call`, no precondition-failed error code — `grep -ci etag` over the normative schema returns 0. Consequence for design: a freshness token has to ride in the tool *arguments*, which means it passes through the model, which means the model must carry it forward. Keep it short, opaque, and adjacent to the value it validates.
- **Statelessness makes server-side staleness detection impossible in principle.** As of this revision MCP is formally stateless — "no state should be inferred from previous requests, even those on the same connection." A server holds no record of what it told a caller, so it cannot know the caller is stale unless the caller says so in-band.
- **Change notifications are optional at three independent levels and only ever `SHOULD`.** The server may not declare `listChanged`; the client may not request it in its `subscriptions/listen` filter; the server may silently drop it from the acknowledged set. There is no delivery guarantee, no sequence number, and no missed-notification recovery — a client that reconnects cannot ask what it missed. **Treat MCP notifications as a latency optimization on top of TTL, never as a correctness mechanism.**
- **`ttlMs` / `cacheScope` are the actual freshness answer**, added in this revision, with semantics the spec itself calls analogous to HTTP `Cache-Control: max-age`. Absent means treat as immediately stale. The spec is explicit that this is a bound, not a detector — "TTL is a freshness hint, not a guarantee. Servers MAY change the underlying data before the TTL expires" — and it explicitly tells clients not to poll on it: check freshness *when you need the data*.
- **The tool set may change under you, and one way has no signal at all.** The spec permits the set to "change over time" *and* to "vary by the authorization presented on the request." `tools/list_changed` covers the first. Nothing covers the second: a scope change or a revoked grant silently changes the answer with no notification defined.
- **The direction of travel is pull-at-point-of-use.** Roots were deprecated in this revision and their `list_changed` notification deleted outright; servers now request roots inside the request that needs them. The spec authors chose fetching at the point of use over fixing the push mechanism.
- **Pagination disclaims consistency**: "There is no cross-page consistency guarantee. If the underlying data changes between page fetches, clients may observe duplicates or gaps."
- **The spec reaches into model context exactly once**, to say deterministic tool ordering "improves LLM prompt cache hit rates when tools are included in model context." That is a billing argument, not a coherence one. Nothing in MCP addresses the gap between "the client's cache is stale" and "the model already believed the stale value."

### Preloaded instructions do not reload themselves

Claude Code is the worked example, and the shape generalizes: **whether a preloaded surface can be refreshed is decided by where it sits relative to the cached prefix, not by how important it is.**

- **Project-root and user `CLAUDE.md` are read once at session start and a mid-session edit does not apply** — new content loads on the next `/clear`, `/compact`, or restart. The docs file this under *actions that keep the cache*, i.e. not-reloading is documented as a feature.
- **Repo files the agent read get a push**: editing one appends a `<system-reminder>` noting the change, and the agent re-reads if needed. The stale read stays in history — nothing is edited in place.
- **Skills hot-reload live**; settings including permissions and hooks reload via a file watcher; output style and model do not. Same session, same repo, three different freshness policies, and the discriminator is architectural.
- **Compaction is when preloaded instructions get re-read from disk** — project-root CLAUDE.md and auto memory are re-injected; path-scoped rules and nested CLAUDE.md are lost until a matching file is read again.
- **Auto-memory entries carry a `modified` timestamp** whose documented purpose is to show "how current the fact is, both to you and to Claude when it reads the memory back." This is the as-of stamp, shipping in production, solving staleness by annotation rather than by refresh.

### Deferred tool loading is shipping

- **Claude Code exposes large catalogs as names only** (as of 2026-08-04): deferred tools appear by name in the session, and the model fetches full schemas on demand, in batches, through a search tool. Context cost is paid per loaded schema, not per registered tool — so a tool-count budget stated per turn applies to the *loaded* set, and trimming the catalog to protect context is the wrong lever on runtimes that have this.

### Corrections have a supported channel

- **Mid-conversation system messages** append a `{"role": "system"}` message rather than editing the top-level `system` field, so the cached prefix survives. The precedence is specified: "later system messages take precedence over earlier ones, and mid-conversation system messages take precedence over the top-level `system` field for the turns that follow them." Named triggers include "a freshness note" and "files changed on disk."
- **Phrasing is specified too**, and it is not what most people reach for: "Phrase the system content as context rather than as a command that overrides the user. State the fact ... and let Claude act on it." The reason is that models are trained to resist instructions that appear to work against the user, and that resistance applies to the operator role as well.
- **Append, never edit** — "If the instruction needs to evolve, append a new system message rather than rewriting the old one."
- **Not a channel for third-party text**: putting tool output or retrieved documents in a system message "gives that text operator-level authority."
- **The tool set can change mid-session without invalidating the cache** via `tool_addition` / `tool_removal` blocks (beta `mid-conversation-tool-changes-2026-07-01`): the `tools` array is declared once and never changes. Any advice to freeze the tool set at session start for cache reasons is out of date on runtimes that have this.

### What no vendor has published

Useful because it tells you where you are on your own.

- **No lab publishes a policy for staleness inside a running window.** Guidance exists at exactly two moments: authoring time ("don't include information that will become outdated") and session boundaries (re-derive state from the filesystem, git log, and a smoke test rather than inheriting a summary). Between them, nothing.
- **Both labs currently tune agents *against* re-examination.** OpenAI's GPT-5 guidance: "Search again only if validation fails or new unknowns appear. Prefer acting over more searching," and "don't repeat queries." Anthropic's: "Avoid revisiting decisions unless you encounter new information that directly contradicts your reasoning." Sound advice for cost; it also means the default agent reuses point-in-time snapshots and has no way to tell whether one is still true.
- **The definitive first-party tool-design guidance never mentions tool-result staleness.** It treats response *size* exhaustively — pagination, filtering, truncation, token caps — and shelf life not at all.
- **Context editing is framed as redundancy, not wrongness**: old tool results "are no longer needed once Claude has processed them." The trigger is a token threshold, not an invalidation event.
- **The cost of leaving a superseded fact in the window is measured, by independent research, and no vendor has engaged with it.** A distractor — content topically related to the answer but not actually answering it, which is exactly what a superseded fact is — measurably degrades retrieval even at one distractor, and the damage compounds with more and grows with input length. The same work found *no* position effect across eleven needle positions, so "put it at the end and it will win" is not a mechanism you can rely on.
