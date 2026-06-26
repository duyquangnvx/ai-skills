# Lifecycle Delegate Pattern

This is not a new pattern. It is **Cocoa's delegation pattern** — the one Apple has shipped and documented for decades — adapted to framework-agnostic, `async` TypeScript. The only thing added on top is the part Cocoa does synchronously: making a delegate call **awaitable** so the producer can pause its own flow until the consumer finishes. That extension is itself established prior art (Swift wraps sync delegates with *continuations*; webpack's *Tapable* formalizes awaitable series/parallel hooks).

We learn the contract and the naming from those sources rather than invent our own. See [Prior art](#prior-art) for links.

## The contract (from Cocoa delegation)

A **producer** (logic, a service, a state machine) needs to notify or consult a **consumer** (UI, an animator, an I/O layer) without depending on it. Per Apple's delegation pattern:

- The producer holds an **optional** delegate reference and calls it **only if it is set** — in TS, an optional field invoked through `?.`. Cocoa does the same with `respondsToSelector:` for optional protocol methods.
- The producer **never imports the consumer**. It knows only the field's type (Cocoa: the protocol).
- The reference is **weak in spirit**: the consumer is "free to come and go," so the relationship has an explicit lifetime — assigned on `bind`, cleared on `unbind` (the *lifecycle* half of the name; in Cocoa, the literal `weak` qualifier).

```ts
class UploadQueue {
  onItemUploaded?: (d: { id: string; url: string }) => Promise<void>;

  private items: UploadItem[] = [];

  async run(): Promise<void> {
    for (const item of this.items) {
      const url = await this.put(item);
      await this.onItemUploaded?.({ id: item.id, url }); // call only if bound
    }
  }
}
```

## The three tiers (Apple's `should` / `will` / `did`)

Apple categorizes delegate methods by the **temporal status** of the event, and notes this maps directly onto whether the call **expects a value back**:

> "This verb indicates whether the event is about to occur (**Should** or **Will**) or whether it has just occurred (**Did** or **Has**). This temporal distinction helps to categorize those messages that **expect a return value** and those that **don't**." — Apple, *Delegates and Data Sources*

Two yes/no questions decide which tier a call is, and they answer themselves through the verb you pick:

1. Does the producer need a **decision/value** back before it can continue? → **`should…`**
2. If not, does the producer need to **wait** for the consumer's side effect to finish? → **await a `will…` / `did…`**
3. Neither — just announcing? → **fire a `did…` and don't wait**

| Tier | Verb | Field type | Producer does | Cocoa analog | Tapable analog |
|---|---|---|---|---|---|
| **Decision gate** | `should…` | `=> Promise<T>` | branches on the returned value | `shouldHighlightRowAt` (returns `Bool`) | `AsyncSeriesBailHook` |
| **Completion gate** | `will…` / `did…` | `=> Promise<void>` | `await`s, then continues unconditionally | `willDisplay` / `didSelect` (awaited) | `AsyncSeriesHook` / `AsyncParallelHook` |
| **Notification** | `did…` | `=> Promise<void>` | fires with `void`, does not wait | `didSelectRowAt` (informational) | — |

The crucial honesty here: **completion gate and notification share the same field type and tense** (`did…`, `Promise<void>`). The difference is *only the call site* — `await this.onX?.(d)` gates, `void this.onX?.(d)` doesn't. The decision gate is genuinely different: it is named `should…` and returns a value the producer reads.

### Decision gate — `should…`

The producer asks the consumer to **approve or alter** something before acting. This is the tier the consumer can *veto*. Cocoa's `tableView(_:shouldHighlightRowAt:)` returns `Bool`; the TS equivalent returns a `Promise` of whatever decision the producer needs:

```ts
class Editor {
  shouldDiscardChanges?: (d: { fileName: string }) => Promise<boolean>;

  async close(): Promise<void> {
    if (this.dirty) {
      const ok = await this.shouldDiscardChanges?.({ fileName: this.name });
      if (ok === false) return;          // consumer vetoed via a dialog
    }
    this.dispose();
  }
}
```

When several consumers may veto, this is exactly Tapable's `AsyncSeriesBailHook`: run them in series, the first conclusive answer wins.

### Completion gate — await a `will…` / `did…`

The producer commits, then **waits for the consumer's side effect** (an animation, a transition, an I/O flush) before its next step. No value is returned — the `await` itself is the gate. Reading the producer top-to-bottom, each `await this.onX?.()` is a visible checkpoint where control is handed out and comes back.

```ts
async submit(form: FormData): Promise<void> {
  const draft = this.validate(form);
  await this.onWillSave?.({ draft });    // consumer plays "saving…" intro
  const saved = await this.api.save(draft);
  await this.onDidSave?.({ saved });     // consumer plays success transition; producer waits
  this.advanceToNextStep();
}
```

`will…` announces *before* the mutation (consumer prepares); `did…` announces *after* (consumer reacts to committed state by querying the producer).

### Notification — fire-and-forget `did…`

Past-tense, called with `void`. The consumer reacts (badge, toast, sound, analytics) but nothing downstream waits on it.

```ts
void this.onDidSave?.({ saved });        // same field as above, just not awaited
void this.onMetricsReady?.({ id: saved.id });
```

## Data source vs. delegate (pull vs. push)

Apple splits the consumer relationship into two roles, and it is worth keeping the distinction:

> "A data source is like a delegate except that, instead of being delegated control of the user interface, it is delegated control of **data**." — Apple

- **Delegate** = *push*: "something happened" (`did…`) or "may I?" (`should…`). The three tiers above.
- **Data source** = *pull*: "give me what I need to proceed" (`numberOfRows`, `cellForRow`). The producer calls a **query** and uses the return value.

Don't model a pull as a `did…` delegate. If the producer needs data on demand, expose a query method (a data-source-style field or a plain getter), not an after-the-fact notification.

## Lifecycle: bind and unbind

A delegate field is mutable state on the producer; treat it like a subscription with a matching teardown. This is what keeps the "weak" spirit honest: no stale handler fires after the consumer is gone, and no consumer is kept alive only by the producer's closure.

```ts
class UploadList {
  constructor(private queue: UploadQueue) {}
  bind(): void   { this.queue.onItemUploaded = async (d) => this.row(d.id).fadeToDone(d.url); }
  unbind(): void { this.queue.onItemUploaded = undefined; }
}

// composition root owns the lifetimes:
const bound: Array<{ unbind(): void }> = [list, statusBar];
for (const b of bound) b.bind();
// teardown:
for (const b of bound) b.unbind();
```

## Conventions

- **Verb signals the tier** (per Apple): `should…` returns a decision; `will…` is about-to-commit; `did…`/past-tense is after-the-fact. Never name a delegate for what the consumer *should do* (`onShowToast`) — name it for what the producer *did* (`onDidSave`). The consumer decides the reaction.
- **Single data-object parameter** `(d: { … })`, never positional — adding a field later won't break existing handlers.
- **Optional field** (`?`) called via `?.` — an unbound delegate is a no-op; the producer never requires a consumer.
- **Completion gate and notification use the identical `=> Promise<void>` field type** — uniform type lets a call site switch from `void` to `await` without touching the field.
- **No consumer-side types in the payload.** A producer that is UI-agnostic ships plain data (`{ x: number; y: number }`), not a `DOMRect` or engine `Vec2`. The consumer translates.

## Fan-out: one field, one handler

A delegate field holds exactly **one** handler. When several consumers react to the same moment, the **wiring layer** composes them — the producer stays unaware. This is precisely Tapable's series/parallel distinction:

```ts
// completion-gate, parallel — producer waits for all (Tapable AsyncParallelHook):
queue.onItemUploaded = (d) => Promise.all([list.markDone(d), bar.advance(d)]).then(() => {});

// notification, parallel — no waiting:
queue.onItemUploaded = (d) => { void list.markDone(d); void bar.advance(d); };
```

If you want a dedicated class whose only job is to own this fan-out and re-dispatch, stop — it becomes a second source of truth for "what happens after upload." Compose in the wiring layer with the rest of the wiring.

## Errors and re-entrancy

An `await`ed handler that throws rejects the producer's awaiting call. Because the call is awaitable, new input can arrive *while control is out* at the consumer (a multi-second animation, a modal). Guard against re-entry and release the guard in `finally` so a throwing handler can't strand it:

```ts
class Checkout {
  onDidPay?: (d: { receipt: Receipt }) => Promise<void>;
  private busy = false;

  async pay(cart: Cart): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    try {
      const receipt = await this.gateway.charge(cart);
      await this.onDidPay?.({ receipt });
    } finally {
      this.busy = false;     // released even if the handler threw
    }
  }
}
```

## When to use it

- A producer must stay unaware of its consumer (logic ↛ UI, core ↛ adapter), **and**
- the relationship is **1-to-1 or small, named fan-out** decided at one wiring layer, **and**
- at least one of: the producer needs a **decision** back (`should`), or it must **wait** for a side effect (`await`-ed `will`/`did`), or it just needs to **notify** (`did`).

It shines when a sequence of producer steps must interleave with consumer-side effects and you want that sequence to read top-to-bottom in one place.

## When to reach for something else

| Situation | Use instead |
|---|---|
| Many anonymous listeners, no ordering, no waiting (analytics, logging) | Event emitter / observer / pub-sub. Delegation is the wrong tool for ambient N-to-1. |
| The producer can stay **pure** and never wait on effects | Return-style: return a description of what happened, let the caller interpret it. Easier to test. |
| Real-time / fixed-timestep loops where you can't pause per frame | Consumer **polls** the producer's state each tick. |
| Replay / undo / time-travel needing immutable history | A reducer / event-sourcing model, not mutable delegate fields. |

The line against an event bus: a delegate is an **intentional contract between two named parties, possibly awaited or consulted**; a bus is **broadcast to unknown parties, never awaited**. Reaching for a bus "to decouple" a 1-to-1 awaited relationship scatters an ordered flow across listeners and loses the top-to-bottom readability.

## Testing

The delegate field is plain mutable state, so tests stub it directly — no mocking framework:

```ts
const queue = new UploadQueue([itemA, itemB]);
const seen: string[] = [];
queue.onItemUploaded = async ({ id }) => { seen.push(id); };
await queue.run();
expect(seen).toEqual(['a', 'b']);
```

For a decision gate, stub it to return each branch and assert the producer takes the right path. For a completion gate, have the stub record before/after markers and assert interleaving with the producer's own observable state.

## Prior art

- **Cocoa delegation** (Apple) — the contract, the weak/lifecycle reference, optional methods: [Delegation](https://developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/Delegation.html), [common mistakes (QA1554)](https://developer.apple.com/library/archive/qa/qa1554/_index.html).
- **`should` / `will` / `did` naming and the return-value distinction**, plus **delegate vs. data source**: [Delegates and Data Sources](https://developer.apple.com/library/archive/documentation/General/Conceptual/CocoaEncyclopedia/DelegatesandDataSources/DelegatesandDataSources.html).
- **Making delegates awaitable** — Cocoa delegates are synchronous; Swift bridges them to `async`/`await` with continuations (`withCheckedContinuation`): [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/).
- **Awaitable hooks formalized in TS/JS** — webpack's [Tapable](https://github.com/webpack/tapable): `AsyncSeriesHook` (await in series), `AsyncParallelHook` (await all), `AsyncSeriesBailHook` (first conclusive value wins) — the direct analogs of the completion gate, parallel fan-out, and decision gate above.
- **Ports & Adapters / Hexagonal** — the delegate field is a *driven port*; the consumer that binds it is the *adapter*.

This project's `minigame-convention` skill is one application of this pattern, specialized for animation-gated game scenes (logic → view hooks). This document is the domain-neutral form.
