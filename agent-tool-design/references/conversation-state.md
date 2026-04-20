# State across turns: designing for conversation memory

How to carry state across an agent's turns without fighting the conversation-memory model or breaking prefix caching. This file covers the mechanics, the stateful-tool-responses pattern, and when to fall back to injection.

Read this when designing agents that operate over many turns on a mutating domain (editors, workflow builders, long-running assistants), or when a production agent is chewing through tokens because it re-queries state every turn.

## Contents

1. How prefix caching interacts with conversation turns
2. The three places you could inject state — and their cache cost
3. The stateful tool responses pattern
4. Combining with actionable errors
5. Cumulative growth and how to mitigate it
6. Out-of-band state changes (the escape hatch case)
7. Recipe: when to use which pattern

---

## 1. How prefix caching interacts with conversation turns

Request structure for any multi-turn agent call looks like:

```
[system prompt] → [tool schemas] → [msg_1, reply_1, msg_2, reply_2, ..., msg_N]
```

Prefix caching hashes from the start of the request forward until it hits bytes it has never seen. Everything up to that point is a cache hit; everything after is new tokens billed at full rate. Anthropic and OpenAI both implement this with some variant of cache breakpoints and a TTL (Anthropic's is ~5 minutes at time of writing).

The core implication: **bytes that were in a previous request are stable; bytes that are new in this request are not cached**. A message from turn 3 is cached by turn 4 because turn 4's request starts with the exact same bytes through turn 3. But change any byte in turn 3's message and turn 4's cache is destroyed from that point on.

This is why where you put state matters.

---

## 2. Three places you could inject state — and their cache cost

When an agent needs to know current state (e.g., "these characters exist", "this project has 47 scenes"), there are three plausible injection points:

| Where | Cache effect |
|---|---|
| **System prompt** | Destroys everything. System prompt is the cache prefix root. Every state change → prompt changes → every byte after misses. |
| **Earlier messages (msg_1..msg_{N-1})**, retroactively | Destroys everything from that point. History bytes changed → the tail of the request misses. |
| **Only msg_N (the latest user message)** | No cache cost. msg_N is new in this request by definition — it was never cached. |

**The non-obvious insight:** injecting into the latest user message is free from a caching standpoint. The trick is that after you send the request, you store the *already-injected* version in your conversation history. Next turn, that message becomes msg_{N-1} — with its original snapshot embedded — and stays cache-stable forever. The new msg_N gets a fresh injection of current state.

Example flow:

```
Turn 1 sent: [msg_1 + state_v1]
Stored:      [msg_1 + state_v1, reply_1]

Turn 2 sent: [msg_1 + state_v1, reply_1, msg_2 + state_v2]
             └─── cache hit ───┘  └── new ──┘

Turn 3 sent: [msg_1 + state_v1, reply_1, msg_2 + state_v2, reply_2, msg_3 + state_v3]
             └────────── cache hit ──────────┘             └── new ──┘
```

Each message carries the state snapshot as of when it was sent. The model is not confused by v1 → v2 → v3 because that progression reflects the actual history — state genuinely was v1 at turn 1.

Injection cost: zero. But there's a better pattern that avoids injection entirely.

---

## 3. The stateful tool responses pattern

Instead of client-side injection, put state summaries in tool responses. Every tool response is already an entry in conversation history; it's already cached in subsequent turns; the agent already reads it as part of its own memory.

**Minimal tool response (common default):**

```json
createCharacter → { "characterId": "nobita" }
```

The agent knows an ID was created but has no continuing awareness of the roster.

**Stateful tool response:**

```json
createCharacter → {
  "characterId": "nobita",
  "name": "Nobita",
  "summary": "Created character 'Nobita' (id: nobita). Characters now: Nobita, Shizuka, Suneo."
}
```

The agent reads the summary, absorbs it as context, and on every subsequent turn already knows the roster — no re-query needed. When it later calls `createScene` referencing a character, it can emit `"nobita"` confidently because the summary from a past turn is still in history.

**Why this is better than injection:**

- No client-side logic to inject state at the right point.
- No risk of injected state drifting out of sync with actual backend state — the tool response came directly from the backend.
- Aligns naturally with the "agent reads its own memory" mental model.
- Fully cache-stable — tool responses enter history like any other turn and stay byte-stable forever after.

**What to put in the summary:**

- Current state of the relevant slice, not a diff. `"Characters: Nobita, Shizuka, Suneo"` beats `"Added Suneo to existing Nobita, Shizuka"`. Current-state framing means the latest summary is always self-sufficient; older summaries become historical artifacts that don't need to be consulted.
- Scoped to what this mutation touched. `createCharacter` returns the character roster, not the entire project overview. `createScene` returns the scene list. Keep each summary narrow.
- Short. One or two sentences. The goal is to leave a useful breadcrumb, not a dump.

**Where to use it:**

- All mutation tools (`create_*`, `update_*`, `delete_*`).
- Optionally on read tools that return a slice of state the agent is likely to act on next.
- Not on pure queries that the agent is unlikely to rely on as future memory (e.g., a `search` tool returning one-off results).

---

## 4. Combining with actionable errors

Stateful responses and actionable errors compound beautifully. Both patterns rely on the same idea — responses carry information the agent can use to self-correct or self-orient without an extra round-trip.

**Success case carries state:**

```json
createCharacter(name="Suneo") → {
  "characterId": "suneo",
  "summary": "Characters: Nobita, Shizuka, Suneo."
}
```

**Error case also carries state:**

```json
createCharacter(name="Nobita") → {
  "error": "Character 'nobita' already exists.",
  "summary": "Characters: Nobita, Shizuka, Suneo.",
  "hint": "Use updateCharacter(id='nobita', ...) to modify the existing one."
}
```

The agent receives both the diagnostic and the current-state snapshot in one response. It self-corrects with full information — no `list_characters` call needed before retrying. This is one of the highest-leverage design moves in an agent tool system.

---

## 5. Cumulative growth and how to mitigate it

Stateful responses do have a cost: summary tokens accumulate in history across turns. After 20 mutations, there are 20 summaries in history, many of them semantically stale (the character roster after turn 3 has been superseded by the roster after turn 17, but the turn-3 bytes are still there).

This is usually fine — bytes in history are cached and cheap. But watch for:

- **Very long sessions** (50+ turns with frequent mutations). Old summaries become dead weight.
- **Summaries that quote full content** rather than naming it. `"Created scene 'Opening' with 47 dialogue nodes..."` is heavier than `"Created scene 'Opening' (47 nodes)."`.
- **Summaries that duplicate each other**. If every mutation returns the full project overview, you're paying for the same 200 tokens every turn.

**Mitigations:**

- **Current-state framing, narrowly scoped.** As above. Each summary describes just the slice relevant to the mutation — character roster for character ops, scene list for scene ops.
- **Delta summaries for large changes.** A bulk import might return `"Created 12 scenes (opening, lobby, ...). Total scenes now: 15."` instead of listing all 15.
- **Compaction for marathon sessions.** If the agent harness supports it, compact older turns into a condensed "here's what happened so far" block when context crosses a threshold.

In practice, for typical agent sessions (10-30 turns), cumulative growth from stateful responses is invisible next to the context savings from not re-querying state every turn.

---

## 6. Out-of-band state changes (the escape hatch case)

Stateful responses work when all state changes flow through the agent's tool calls. Reality: users also change state directly in the product UI, outside the chat. When the user edits a scene in the editor and then turns to the agent, the agent's conversation memory is now stale.

Two escape-hatch patterns:

### Workflow rule: re-orient when uncertain

Simplest. System prompt includes guidance like *"If you think the project state may have changed outside the chat (e.g., the user mentions editing something directly), call `get_project_overview` to refresh before acting."* The agent will mostly obey when cues are present; it won't catch silent UI edits but will catch mentioned ones.

### msg_N injection for out-of-band notifications

When the client knows state changed (e.g., the editor fires an event when the user edits a scene), prepend a system-style notice to the latest user message:

```
[State change notice: 2 scenes added via the editor since last turn.
 Call get_project_overview if this may affect your current task.]

<user's actual message>
```

This is cache-safe (msg_N is always new) and gives the agent a strong signal. The tradeoff: it's client-side logic to maintain. Use it when silent UI edits are common enough that workflow rules alone produce stale behavior.

### Synthetic tool result injection

More elaborate: insert a synthetic tool result into history right before msg_N, framed as an auto-called `get_project_overview` with the fresh state. Natural from the agent's perspective (it sees a recent overview in memory) but more complex to maintain. Worth it only if you want the agent to feel like it just re-oriented without being told.

**When to skip all of this:** if state can only change through tool calls (the chat is the only mutation path), out-of-band changes don't exist and stateful responses alone are sufficient.

---

## 7. Recipe: when to use which pattern

A decision order for designing state flow in a multi-turn agent:

1. **Default: stateful tool responses.** Every mutation returns a compact current-state summary for its slice. Every actionable error returns state + hint. This covers 80-90% of cases cleanly and for free.

2. **Add at the start of conversation: an `overview` / `orient` tool.** System prompt rule: "call this first." Its response enters history and is cached for the whole session. This seeds the agent's memory so the first turn isn't dependent on guessing.

3. **Add a workflow rule for re-orientation:** "if the state may have changed outside the chat, call `get_project_overview` to refresh." Cheap, catches most out-of-band drift.

4. **If silent UI edits are common: add msg_N injection** for state-change notices from the client. Cache-safe; adds complexity but eliminates a staleness class.

5. **Avoid: injecting state into system prompt or earlier messages.** Both destroy prefix caching. If you find yourself wanting to do this, step back — stateful responses plus msg_N injection almost always cover the same ground without the cache cost.

The guiding principle: **design tool responses to be the agent's memory, and let the conversation protocol do the rest**. Injection is a workaround for things the response protocol can't carry; stateful responses use the grain of how agents already work.
