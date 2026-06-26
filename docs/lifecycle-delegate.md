# Lifecycle Delegate Pattern

A small, framework-agnostic way to let a side-effect-free object (logic, a service, a state machine) notify an effectful collaborator (UI, an animator, an I/O layer) **and optionally wait for it** — without the producer ever importing the consumer.

It is the classic delegate pattern (Cocoa, `UITableViewDelegate`) with two additions:

1. **Awaitable** — a delegate method returns a `Promise`, so the producer can pause its own flow until the consumer finishes (an animation, a network round-trip, a confirmation dialog).
2. **Lifecycle-bound** — the delegate is assigned and cleared over an explicit lifetime (`bind` / `unbind`), so wiring is symmetric and teardown is leak-free.

Nothing here is novel. The value is the *convention*: a fixed shape, fixed naming, and one rule for "does the producer wait or not" — applied the same way everywhere.

## The shape

The producer declares optional delegate fields. Each is named for something it **has already done** (past tense) and takes a single data object:

```ts
class UploadQueue {
  onItemUploaded?: (d: { id: string; url: string }) => Promise<void>;
  onQueueDrained?: (d: { count: number }) => Promise<void>;

  private items: UploadItem[] = [];

  async run(): Promise<void> {
    for (const item of this.items) {
      const url = await this.put(item);                 // do the work
      await this.onItemUploaded?.({ id: item.id, url }); // tell + wait
    }
    void this.onQueueDrained?.({ count: this.items.length }); // tell, don't wait
  }
}
```

The consumer assigns a handler:

```ts
class UploadList {
  constructor(private queue: UploadQueue) {}

  bind(): void {
    this.queue.onItemUploaded = async ({ id, url }) => {
      await this.row(id).fadeToDone(url);   // producer awaits this
    };
  }

  unbind(): void {
    this.queue.onItemUploaded = undefined;
  }
}
```

The producer never knows `UploadList` exists. It knows only the delegate field's type.

## The one decision: gate or don't gate

Every delegate call is one of two things. This is the whole pattern.

| Call site | Meaning | Use when |
|---|---|---|
| `await this.onX?.(d)` | **Gating.** The producer's next line depends on the consumer finishing. | The next step must not run until the animation/IO/confirmation completes. |
| `void this.onX?.(d)` | **Cosmetic.** Fire-and-forget notification. | The consumer reacts (badge, toast, sound) but nothing downstream waits on it. |

Reading the producer top-to-bottom, every `await this.onX?.()` is a visible checkpoint where control is handed out and comes back. That is the readability payoff: the flow and its pauses live in one method, in order.

```ts
async submit(form: FormData): Promise<void> {
  const draft = this.validate(form);
  await this.onValidated?.({ draft });          // gate: show "saving…" then continue
  const saved = await this.api.save(draft);
  await this.onSaved?.({ saved });              // gate: play success transition
  void this.onMetricsReady?.({ id: saved.id }); // cosmetic: fire analytics, don't wait
}
```

## Conventions

These keep delegate code uniform across a codebase.

- **Past-tense names.** `onItemUploaded`, `onSaved`, `onConnectionLost` — describe what the producer *did*, not what the consumer *should do*. The consumer decides the reaction; the name must not presume it. Avoid `onSaveButton` / `onShowToast`.
- **Single data-object parameter** `(d: { ... })`, never positional args. Adding a field later does not break existing handlers.
- **Optional field** (`?`). An unbound delegate is a no-op via `?.`. The producer never requires a consumer.
- **Return `Promise<void>`** even for cosmetic delegates. Uniform type means any call site can later switch from `void` to `await` without changing the field.
- **Extract a named payload type** when a payload is bound at 2+ sites, has 4+ fields, or hurts readability. Inline `(d: { ... })` is fine for single-use, low-arity payloads.
- **No leakage of consumer-side types into the producer.** If the producer is UI-agnostic, the payload carries plain data (`{ x: number; y: number }`), not a `DOMRect` or an engine `Vec2`. The consumer translates.

## Lifecycle: bind and unbind

A delegate field is mutable state on the producer. Treat it like a subscription: every `bind` has a matching `unbind`, called when the consumer's lifetime ends.

```ts
const list = new UploadList(queue);
list.bind();
// ...later, on teardown:
list.unbind();
```

A composition root that owns many consumers tracks them and tears them all down together:

```ts
const bound: Array<{ unbind: () => void }> = [list, statusBar, toaster];
for (const b of bound) b.bind();
// teardown:
for (const b of bound) b.unbind();
```

This is the "lifecycle" half of the name. It prevents the two classic leaks: a stale handler firing after the consumer is gone, and a consumer kept alive only because the producer still holds its closure.

## One field, one binder — fan out at the wiring layer

A delegate field holds exactly one handler. When several consumers must react to the same moment, **the wiring layer composes them**, not the producer:

```ts
// gating fan-out: producer waits for all consumers
queue.onItemUploaded = async (d) => {
  await Promise.all([
    list.markDone(d),
    progressBar.advance(d),
  ]);
};

// cosmetic fan-out: no waiting
queue.onItemUploaded = (d) => {
  void list.markDone(d);
  void progressBar.advance(d);
};
```

If you find yourself wanting a dedicated class whose job is to own this fan-out and re-dispatch, stop — that class becomes a second source of truth for "what happens after upload". Keep the composition in the wiring layer where everything else is wired.

## Error handling and re-entrancy

A handler that throws rejects the `Promise` the producer is awaiting. The producer must not be left in a half-locked state. If the producer guards against re-entry while a gating delegate is in flight, release that guard in `finally`:

```ts
class Checkout {
  onPaid?: (d: { receipt: Receipt }) => Promise<void>;
  private busy = false;

  async pay(cart: Cart): Promise<void> {
    if (this.busy) return;          // ignore double-submit while a delegate animates
    this.busy = true;
    try {
      const receipt = await this.gateway.charge(cart);
      await this.onPaid?.({ receipt });
    } finally {
      this.busy = false;            // released even if the handler threw
    }
  }
}
```

The `busy` guard matters specifically *because* delegates are awaitable: while control is handed to the consumer (a multi-second animation, a confirmation modal), new input can arrive. The guard makes "one flow at a time" explicit.

## When to use it

- A producer must stay unaware of its consumer (logic ↛ UI, core ↛ adapter), **and**
- The producer sometimes needs to **wait** for the consumer before continuing, **and**
- The relationship is **1-to-1 or small, named fan-out** decided at a single wiring layer.

It shines when a sequence of producer steps must interleave with consumer-side effects and you want that sequence to read top-to-bottom in one place.

## When to reach for something else

| Situation | Use instead |
|---|---|
| **Many anonymous listeners** for the same event (analytics, logging, achievements) with no ordering or waiting | An event emitter / observer / pub-sub bus. Delegates are the wrong tool for ambient N-to-1. |
| **The producer can be pure** and never needs to wait on effects | Return-style: have the producer return a description of what happened and let the caller interpret it. Easier to test, no mutable delegate field. |
| **Real-time / fixed-timestep loops** where you cannot pause per frame to await | Have the consumer poll the producer's state each tick. |
| **Replay / undo / time-travel** requiring immutable history | A reducer / event-sourcing model, not mutable delegate fields. |

The dividing line against an event bus: a delegate is an **intentional contract between two named parties, possibly awaited**. A bus is **broadcast to unknown parties, never awaited**. Reaching for a bus "to decouple" a 1-to-1 awaited relationship scatters an ordered flow across listeners and loses the top-to-bottom readability.

## Testing

Because the delegate field is plain mutable state, tests stub it directly — no mocking framework needed:

```ts
const queue = new UploadQueue([itemA, itemB]);
const seen: string[] = [];
queue.onItemUploaded = async ({ id }) => { seen.push(id); };

await queue.run();

expect(seen).toEqual(['a', 'b']);
```

To assert gating order, have the stub record before/after markers and check interleaving with the producer's own observable state.

## Heritage

Delegation (Cocoa/`UIKit`), Ports & Adapters / Hexagonal (the delegate field is a *driven port*; the consumer is its adapter), and awaitable state machines (Unity `Awaitable`, async sagas) where `await` makes flow and its pauses explicit. This document generalizes the logic→view hook contract from the project's `minigame-scene-convention` skill into a domain-neutral form; that skill is one application of this pattern, specialized for animation-gated game scenes.
