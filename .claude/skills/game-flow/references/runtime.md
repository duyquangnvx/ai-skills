# Runtime

Reference implementation of the machinery behind invariants 2, 4 and 5. Copy it once into a shared package; it carries no game rules and no engine types, so every game depends on the same copy. Once the package exists in the repo, read that source rather than this file.

## Cancellation token

```ts
export class Cancelled extends Error {
  constructor() { super('Cancelled'); this.name = 'Cancelled'; }
}

export interface CancelToken {
  readonly cancelled: boolean;
  throwIfCancelled(): void;
  /** Runs `fn` when cancelled (immediately if already cancelled). Returns an unsubscribe. */
  onCancel(fn: () => void): () => void;
}

export class TokenSource implements CancelToken {
  cancelled = false;
  private hooks = new Set<() => void>();

  cancel(): void {
    if (this.cancelled) return;
    this.cancelled = true;
    const hooks = [...this.hooks];
    this.hooks.clear();
    for (const h of hooks) h();
  }

  throwIfCancelled(): void { if (this.cancelled) throw new Cancelled(); }

  onCancel(fn: () => void): () => void {
    if (this.cancelled) { fn(); return () => {}; }
    this.hooks.add(fn);
    return () => { this.hooks.delete(fn); };
  }
}
```

## Runtime

```ts
export type Policy = 'drop' | 'queue' | 'preempt';

export interface Command {
  readonly kind: string;
  readonly policy: Policy;
  run(token: CancelToken): Promise<void>;
}

export class Runtime {
  private queue: Command[] = [];
  private pumping = false;
  private current: TokenSource | null = null;
  /** Set by InputRouter while the running command waits on the player. */
  waitingForPlayer = false;

  constructor(private readonly onError: (e: unknown, cmd: Command) => void) {}

  get busy(): boolean { return this.pumping; }

  dispatch(cmd: Command): void {
    if (cmd.policy === 'preempt') {
      this.queue.length = 0;
      this.current?.cancel();
    } else if (cmd.policy === 'drop' && this.pumping) {
      return;
    } else if (cmd.policy === 'queue' && this.waitingForPlayer) {
      this.current?.cancel();
    }
    this.queue.push(cmd);
    void this.pump();
  }

  /** Cancels the running command and drops the queue without enqueuing anything. */
  abort(): void {
    this.queue.length = 0;
    this.current?.cancel();
  }

  private async pump(): Promise<void> {
    if (this.pumping) return;
    this.pumping = true;
    try {
      while (this.queue.length) {
        const cmd = this.queue.shift()!;
        const token = new TokenSource();
        this.current = token;
        try {
          await cmd.run(token);
        } catch (e) {
          if (!(e instanceof Cancelled)) this.onError(e, cmd);
        } finally {
          this.current = null;
        }
      }
    } finally {
      this.pumping = false;
      // A dispatch that arrived while the loop was unwinding still needs a pump.
      if (this.queue.length) void this.pump();
    }
  }
}
```

Two details that look optional and are not:

- `preempt` clears the queue **before** cancelling, so the cancelled command's `finally` cannot resurrect stale work into a queue that is about to be drained.
- The trailing re-pump in `finally` covers a `dispatch` that lands between the loop exiting and `pumping` flipping to `false`.

A `drop` arriving while the queue is non-empty but the pump is idle still enqueues — that gap only exists for one microtask, and dropping there would lose the very first input of a frame.

## Input router

A command that stops to ask the player ("pick a tile to bomb") needs the next tap to be an *answer*, not a new command.

```ts
export class InputRouter<T> {
  private pending: ((v: T) => void) | null = null;

  constructor(private readonly runtime: Runtime) {}

  ask(token: CancelToken): Promise<T> {
    token.throwIfCancelled();
    return new Promise<T>((resolve, reject) => {
      this.runtime.waitingForPlayer = true;
      const off = token.onCancel(() => {
        this.pending = null;
        this.runtime.waitingForPlayer = false;
        reject(new Cancelled());
      });
      this.pending = (v: T) => { off(); this.runtime.waitingForPlayer = false; resolve(v); };
    });
  }

  /** True if the value was consumed as an answer. */
  offer(value: T): boolean {
    const p = this.pending;
    if (!p) return false;
    this.pending = null;
    p(value);
    return true;
  }
}
```

Raw input goes through the router first:

```ts
onTapRaw(p: Pos): void {
  if (this.paused) return;
  if (this.router.offer(p)) return;
  this.runtime.dispatch(new TapCommand(p));
}
```

A command parked on the router waits on the player, whose answer has no deadline, so a `queue` arrival (time-up, effect expiry) would sit behind it indefinitely. The runtime cancels the parked command instead and the arrival runs at once. A game that would rather keep the pick open stops the arrival at its source, e.g. `clock.hold('targeting')` for the duration of the ask.

Cleanup belongs in the command, not the router:

```ts
async run(token: CancelToken) {
  this.view.enterTargeting();
  try {
    const p = await this.router.ask(token);
    this.board.remove(p);
    await this.view.explode(p, token);
  } finally {
    this.view.exitTargeting();
  }
}
```

## Clock

```ts
export class Clock {
  private holds = new Set<string>();
  private fired = false;

  constructor(
    public remaining: number,
    private readonly onTick: (remaining: number) => void,
    private readonly onExpire: () => void,
  ) {}

  get stopped(): boolean { return this.holds.size > 0; }
  hold(reason: string): void { this.holds.add(reason); }
  release(reason: string): void { this.holds.delete(reason); }

  tick(dt: number): void {
    if (this.stopped || this.fired) return;
    this.remaining = Math.max(0, this.remaining - dt);
    this.onTick(this.remaining);
    if (this.remaining === 0) { this.fired = true; this.onExpire(); }
  }

  add(ms: number): void { this.remaining += ms; }
}
```

Wire it so expiry becomes a command:

```ts
const clock = new Clock(60_000,
  ms => view.renderTime(ms),                    // fire-and-forget
  () => runtime.dispatch(new TimeUpCommand()),  // policy 'queue'
);
// render loop:
update(dt) { if (paused) return; clock.tick(dt); effects.tick(dt); }
```

`dt` comes from the engine's frame delta, never from `Date.now()` deltas computed inside logic — that is what makes the clock replayable at any speed in headless runs.
