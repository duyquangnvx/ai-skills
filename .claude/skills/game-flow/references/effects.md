# Timed effects

Instant boosters (shuffle, bomb, undo, hint-once) are plain commands and need nothing here. Read this file only for effects with a **duration**: x2 score for 10s, freeze the clock for 5s, auto-hint pulsing in the background, a combo window.

A duration does not fit the queue. The queue is serial and a buff has to survive across many commands, so an effect that sat in the queue would block every input for its whole lifetime. Effects live beside the queue and are ticked by the same render loop as the clock.

## Shape

```ts
export interface Effect {
  readonly id: string;          // one live instance per id
  remaining: number;
  onStart?(): void;
  onExpire?(): void;
}

export class EffectSystem {
  private live = new Map<string, Effect>();

  add(e: Effect): void {
    const existing = this.live.get(e.id);
    if (existing) { existing.remaining = Math.max(existing.remaining, e.remaining); return; }
    this.live.set(e.id, e);
    e.onStart?.();
  }

  has(id: string): boolean { return this.live.has(id); }

  tick(dt: number): void {
    for (const e of [...this.live.values()]) {
      e.remaining -= dt;
      if (e.remaining <= 0) { this.live.delete(e.id); e.onExpire?.(); }
    }
  }

  clear(): void { for (const e of [...this.live.values()]) { this.live.delete(e.id); e.onExpire?.(); } }
}
```

`add` on a live id refreshes instead of stacking, which is the right default for casual games and removes a whole class of double-tap bugs. Stacking effects need an explicit list per id and an explicit stack cap.

## Reading and expiring

Commands **read** effects synchronously while computing — that is safe because it touches no view and no queue:

```ts
const gained = base * (this.effects.has('x2') ? 2 : 1);
```

Expiry that only changes a number or a visual runs inline in `onExpire`. Expiry that **changes what the player can do** — a freeze ending, a board-altering buff wearing off — dispatches a `queue` command instead, so it lands between commands rather than inside one:

```ts
this.effects.add({
  id: 'freeze', remaining: 5000,
  onStart: () => { this.clock.paused = true; this.view.showFrozen(); },
  onExpire: () => this.runtime.dispatch(new UnfreezeCommand()),  // policy 'queue'
});
```

## Pause, cancel, and the clock

- Pause skips `effects.tick` exactly as it skips `clock.tick`. Both are in the same `update(dt)`.
- Freeze pausing the clock and the pause menu pausing the clock are two writers to one flag; use a counter or separate flags (`menuPaused`, `frozen`) and derive `clock.paused` from both.
- Level end calls `effects.clear()`; every `onExpire` must be safe to run early and out of order.

## Testing

Effects need no special harness: drive `effects.tick(dt)` from the headless loop with large `dt` values and assert the boundary — a buff read at `remaining = 1` still applies, at `0` it does not.
