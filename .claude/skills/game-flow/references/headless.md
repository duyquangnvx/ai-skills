# Headless

Because logic depends on the port and never on a view class, the whole game runs with no renderer. This is the payoff of invariant 1 and it survives an engine change, so it is worth building on day one rather than when tests are needed.

## Null port

```ts
export class NullBoardPort implements BoardPort {
  readonly log: string[] = [];
  private rec(s: string) { this.log.push(s); }

  async clearPair(a: Pos, b: Pos) { this.rec(`clear ${fmt(a)} ${fmt(b)}`); }
  async mismatch(a: Pos, b: Pos)  { this.rec(`miss ${fmt(a)} ${fmt(b)}`); }
  async win()                     { this.rec('win'); }
  playSfx(id: string)             { this.rec(`sfx ${id}`); }
}
```

Every awaited method resolves immediately, so a full game runs in microseconds. The `log` doubles as the assertion surface: it is the exact sequence the player would have seen, which makes it a far better test target than poking at model internals.

## Loop

Headless needs no engine loop — step the clock and effects by hand between inputs:

```ts
function step(ms: number) { clock.tick(ms); effects.tick(ms); }

runtime.dispatch(new TapCommand(p1));
await settle();          // let the microtask queue drain
step(30_000);
expect(port.log).toEqual([...]);
```

```ts
const settle = () => new Promise<void>(r => setTimeout(r, 0));
```

`settle` is the one honest use of `setTimeout` in the codebase: it drains promises in the harness, never in game logic. Settle after every dispatch: the runtime stays busy for a microtask after even an instant command, so a second dispatch in the same tick is dropped by its `drop` policy.

## What to use it for

Beyond unit tests, the headless runner is the level pipeline:

- **Solvability.** Run a solver or a random-play loop over every shipped level and fail the build on an unsolvable one. This is the single highest-value use and it catches the bugs players report as "this level is broken".
- **Difficulty curve.** Play each level N times with a scripted policy; record moves used, time left, and win rate. A level whose win rate falls off the curve gets flagged before QA sees it.
- **Repro.** A bug report carrying `{ seed, inputs[] }` replays deterministically. Keep the RNG seeded and owned by logic for this to hold.
- **Regression on rules.** The port log makes rule changes visible as diffs.

## Determinism

The runner is deterministic only if logic gets randomness from a seeded generator it owns, time only from `dt` passed into `tick`, and nothing from `Math.random`, `Date.now`, or engine globals. Those three constraints are cheap when applied from the start and expensive to retrofit.
