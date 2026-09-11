# Ports and the tween layer

The port (invariant 1) is only as good as the animation layer underneath it. Build that first.

## Tween layer contract

Every game needs these four capabilities before a port method can honestly return a promise:

```ts
export interface Tweener {
  to(target: unknown, props: object, ms: number, opts?: TweenOpts): Handle;
  sequence(...steps: (() => Handle)[]): Handle;  // factories: a created tween is already running
  parallel(...items: Handle[]): Handle;
  delay(ms: number): Handle;
  pauseAll(): void;
  resumeAll(): void;
}

export interface Handle {
  readonly done: Promise<void>;  // rejects with Cancelled when killed
  kill(): void;
}
```

Most engines ship the tweening and omit the promise and the kill. Wrap the engine's tween once, in one adapter file, rather than per call site. A tween reads its start values on its first tick, so a step created later in a sequence starts where the previous one ended.

`pauseAll`/`resumeAll` must be global, freezing tweens created while paused too, because pause (invariant 5) relies on them to suspend commands that are parked at an `await`. Logic reaches them only through a fire-and-forget port method (`setPaused(isPaused)`) whose adapter calls them.

`sequence` and `parallel` are what remove `setTimeout` from view code: a chained animation becomes one handle with one promise instead of nested callbacks with hand-counted delays.

## Binding tweens to the token

Every tween a command awaits registers with the token, so a preempt kills the animation and rejects the await:

```ts
export function run(h: Handle, token: CancelToken): Promise<void> {
  token.throwIfCancelled();
  const off = token.onCancel(() => h.kill());
  return h.done.finally(off);
}
```

Adapters use it uniformly:

```ts
class BoardView implements BoardPort {
  async clearPair(a: Pos, b: Pos, path: Pos[], token: CancelToken): Promise<void> {
    await run(this.tw.sequence(() => this.drawPath(path), () => this.pop(a, b)), token);
    token.throwIfCancelled();
    this.recycle(a, b);
  }
  playSfx(id: string): void { this.audio.play(id); }  // fire-and-forget
}
```

The `throwIfCancelled()` after the await matters: `kill()` may resolve rather than reject in some engines, and work after the await must not touch a torn-down scene either way.

## Designing the port

Name methods after **what the player sees**, not after the logic event that caused them: `clearPair`, `mismatch`, `shuffle`, `win`. A method named `onPairMatched` is an event bus wearing an interface, and it pushes the decision of what to animate back into the view.

Pass everything the view needs as arguments — positions, the path, a board snapshot. A port method that has to read the model back is broken by invariant 3: the model has already moved on.

Keep the port free of engine types. `Pos`, `Card`, `BoardSnapshot` are domain types; `Node`, `Sprite`, `Vec3` are not.

When a port method needs a decision from the player (targeting, a choice dialog), return the value rather than calling back: `askTile(prompt, token): Promise<Pos>`. Inside, the adapter waits on the input router.

## Checking a port

- Every method is `Promise<void>`/`Promise<T>` or `void`, and the choice reflects whether a later line depends on it.
- Every awaited method takes a token.
- No engine type appears in a signature.
- A `NullPort` implementing it with `Promise.resolve()` and empty `void` bodies compiles and runs the game to completion — see `headless.md`.
