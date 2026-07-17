# Communication contract — full tier model

The complete reference behind SKILL.md → *Communication tiers*. The contract is **Cocoa's delegation pattern** adapted to `async` TypeScript: a producer (logic) notifies or consults a consumer (view) without depending on it, through an **optional hook field** the consumer binds. Awaitability is the one extension — making a delegate call something the producer can pause on.

The producer holds the hook as an optional field, calls it only via `?.`, **never imports the consumer**, and the relationship has an explicit lifetime (bind/unbind — Cocoa's `weak`).

## The four tiers

| Tier | Verb | Field type | Producer does | Cocoa analog | Tapable analog |
|---|---|---|---|---|---|
| **Decision gate** | `should…` | `(d) => Promise<T>` | branches on the returned value | `shouldHighlightRowAt` (returns `Bool`) | `AsyncSeriesBailHook` |
| **Completion gate** | `onWill…` / `onDid…` | `(d) => Promise<void>` | `await`s, then continues | `willDisplay` / `didSelect` (awaited) | `AsyncSeriesHook` / `AsyncParallelHook` |
| **Notification** | `onDid…` | `(d) => Promise<void>` | calls `void`, does not wait | `didSelectRowAt` (informational) | — |
| **Data source** | query (`peek`, `next3`) | `(…) => T` | **pulls** a value to proceed | `numberOfRows`, `cellForRow` | — |

The honest part: **completion gate and notification are the same field type and tense** (`onDid…`, `Promise<void>`). The difference is *only the call site* — `await this.onX?.(d)` gates, `void this.onX?.(d)` does not. So a moment can be promoted from cosmetic to gating without touching the field. The decision gate is the one genuinely different tier: it is named `should…` and returns a value the producer reads.

### Decision gate — `should…` (the consumer can veto)

The producer asks the consumer to approve or alter something *before* acting. In games: i-frames (`shouldApplyDamage`), a tutorial blocking input (`shouldPlacePiece`), spawn rules, quit confirmation.

```ts
class CombatResolver {
  shouldApplyDamage?: (d: { target: string; amount: number }) => Promise<boolean>;

  async hit(target: string, amount: number): Promise<void> {
    const ok = await this.shouldApplyDamage?.({ target, amount });
    if (ok === false) return;            // shield / i-frame consumer vetoed
    this.applyDamage(target, amount);    // kind 1: mutate inline
  }
}
```

When several consumers may veto, this is Tapable's `AsyncSeriesBailHook` — run in series, the first conclusive answer wins; compose them in the wiring layer.

### Completion gate — await `onWill…` / `onDid…`

The producer commits state, then **waits** for the consumer's side effect (animation, transition, I/O) before its next step. The `await` itself is the gate; reading the Orchestrator top-to-bottom, each `await this.onX?.()` is a visible checkpoint. `onWill…` fires *before* the mutation (consumer prepares); `onDid…` fires *after* (consumer reacts to committed state, which it reads back via a query).

### Notification — fire-and-forget `onDid…`

Past tense, called with `void`. A **named** consumer reacts (badge, toast, SFX) but nothing downstream waits.

```ts
void this.onComboTick?.({ combo: this.combo });   // same field shape as a gate, just not awaited
```

### Data source — pull, not push

`tray.peek(slot)` and `shapes.next3()` are data sources: the producer *pulls* a value and reads the return. **Do not model a pull as a `did…` notification.** If the producer needs data on demand, expose a query method (or a getter), not an after-the-fact event.

## Delegate vs event bus — the audience decides

The single most-misapplied boundary. It is **not** decided by `await`:

- `await` decides *within* delegate (completion gate awaits, notification does not).
- **Audience** decides delegate-vs-bus: a **named, known** consumer ⇒ delegate hook; an **anonymous, arbitrary-N** audience ⇒ bus.
- Enforced by the signature, not by memory: needs waiting ⇒ `(d) => Promise<void>` (awaitable); anonymous and fire-and-forget ⇒ `emit(fact): void` (not awaitable). Every common bus's `emit` is sync + void, so a thing that needs `await` *cannot type-check* as a bus event.
- **If you ever feel you need to `await` a `bus.emit`, that is the litmus telling you it was a delegate.** Awaiting a broadcast is a code smell.

Coin-flight and quest-popup are **named** presentation consumers → **hooks**, even though they look like "just notifications." Analytics, achievements, ambient audio — *anonymous, arbitrary N* → **bus**.

```ts
// adapter / wiring layer (core never imports the bus):
orch.onLinesCleared = async (d) => {
  await fx.playClear(d.cells);                       // kind 2: ordered presentation, awaited hook
  void audio.play('clear');                          // kind 2: named notification, not awaited
  bus.emit('LinesCleared', { count: d.cells.length }); // kind 3: anonymous fact, sync, not awaited
};
```

The bus has **one** entry point (the wiring layer), so "the bus is hard to trace" dissolves: to see what feeds it, read the wiring. **Naming:** hooks are `onX` (single-cast, what the producer did); bus facts are completed-tense nouns with **no** `on` prefix (`LinesCleared`, `PlayerLeveledUp`). Quick read: `onX` = "someone may be awaiting me"; bare `X` = "X happened, whoever cares handles it."

## Gateway to the bus is NOT a class

When logic needs a fact on the bus, do **not** build a dedicated re-dispatch class — it becomes a second source of truth for "what happens after X." The **wiring layer** that binds the `onX` hooks is also where `bus.emit(Fact)` is called. (Likewise, do not build a class to own hook fan-out.)

## Fan-out — one field, one handler

A hook field holds exactly **one** handler. When several named consumers react to one moment, the **wiring layer** composes them; the producer stays unaware (Tapable's series/parallel split):

```ts
// completion-gate, parallel — producer waits for all (AsyncParallelHook):
orch.onPiecePlaced = (d) => Promise.all([boardView.snap(d), trayView.clear(d.slot)]).then(() => {});

// notification, parallel — no waiting:
orch.onPiecePlaced = (d) => { void boardView.snap(d); void trayView.clear(d.slot); };
```

## Lifecycle — bind / unbind (Cocoa's `weak` spirit)

A hook field is mutable state on the producer; treat it like a subscription with a matching teardown. This keeps the relationship honest: no stale handler fires after the consumer is gone, no consumer is kept alive only by the producer's closure. Forgetting `unbind` on scene change/destroy is the classic leak/crash.

```ts
class CoinBarView {
  constructor(private wallet: Wallet) {}
  bind(): void   { this.wallet.onCoinsAdded = async (d) => this.flyCoins(d.amount); }
  unbind(): void { this.wallet.onCoinsAdded = undefined; }
}
// composition root owns the lifetimes:
for (const v of boundViews) v.bind();
// on shutdown:
for (const v of boundViews) v.unbind();
```

## Errors & re-entrancy

An awaited handler that throws rejects the producer's awaiting call. Because the call is awaitable, **new input can arrive while control is out** at the consumer (a multi-second animation, a modal). Guard re-entry and release the guard in `finally` so a throwing handler can't strand it:

```ts
async placePiece(/* … */): Promise<void> {
  if (this.locked) return;
  this.locked = true;
  try {
    /* mutate inline + awaited hooks */
  } finally {
    this.locked = false;   // released even if a handler threw
  }
}
```

## Payload rules

- **One data object** `(d: { … })`, never positional — adding a field later won't break bound handlers.
- **No consumer/engine types in the payload.** Logic ships plain data (`{ x: number; y: number }`, indices), never a `Vec2`/`DOMRect`/sprite; the view translates.
- **Extract a named `interface`** for the payload when it is reused at 2+ binding sites, has 4+ fields, or hurts readability; inline `(d: { … })` is fine for single-use low-arity payloads. View-side, derive with `Parameters<typeof svc.onX>` rather than duplicating the shape.

## Testing

A hook field is plain mutable state, so tests stub it directly — no mocking framework, no engine:

```ts
const orch = new BoardOrchestrator(board, tray, wallet, nextPieces);
const seen: string[] = [];
orch.onPiecePlaced = async () => { seen.push('placed'); };
orch.onLinesCleared = async () => { seen.push('cleared'); };
await orch.placePiece(0, { x: 0, y: 0 });
expect(seen).toEqual(['placed', 'cleared']);   // asserts interleaving with logic
```

For a decision gate, stub it to return each branch and assert the producer takes the right path. For a completion gate, record before/after markers in the stub and assert ordering against the producer's observable state.
