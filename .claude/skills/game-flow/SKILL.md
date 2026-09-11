---
name: game-flow
description: Architecture for sequencing game logic against an animated view in casual and puzzle games — serial command queue, awaitable view port, cancellation, countdown timers, boosters. Use when building or refactoring a game's input-to-logic-to-animation flow, when adding a command, booster or timer, when logic must wait for an animation before continuing, when input arriving during an animation causes double-resolve or model/view desync, or when replacing an EventBus that sits between logic and view.
---

# Game flow

Logic and view exchange control through a **port** (a `Promise`-returning interface that logic owns), driven by a single **command** queue. Every animation the logic waits on is an `await`, so one player input reads as one top-to-bottom function.

Five invariants carry the whole design. Check them by name; each is violated in a characteristic way.

## 1. Port

Logic reaches the view only through an interface logic declares. The return type states the contract:

- `Promise<void>` — logic waits for it. Board animations, dialogs, win sequences.
- `void` — **fire-and-forget**. Sfx, score popups, analytics, idle VFX, HUD repaints.

Reading the port tells you exactly where the sequencing points are. Keep that distinction sharp: mark a method `Promise<void>` only when a later line genuinely depends on it finishing.

A view implements the port; logic never imports a view class, a scene, a node, or an engine type. Split by role once one port passes ~15 methods (`BoardPort`, `HudPort`, `FxPort`), not by screen.

An EventBus still earns a place beside the port, carrying only fire-and-forget broadcasts with many listeners and no ordering: achievements, quests, analytics, audio. Anything with a "then" goes through the port.

## 2. Command

Every external input enters through `runtime.dispatch(cmd)`. The runtime runs commands strictly one at a time, so no two commands ever interleave on the model.

Each command declares a **policy**:

| Source | Policy | Why |
|---|---|---|
| Tap, drag, tile select | `drop` | Queued taps replay after the animation and feel haunted |
| Instant booster (shuffle, bomb, undo) | `drop` | Same; the UI already shows it as unavailable |
| Timer expiry, effect expiry, turn end | `queue` | Must never be lost — it waits for the current command instead |
| Quit, restart, level abort | `preempt` | Cancels whatever is running and clears the queue |

Pause, mute, and camera moves are **not** commands — see invariant 5.

## 3. Transaction

A command is a transaction against the model: it commits model state **before** awaiting the port.

```ts
this.selection = null;
this.board.remove(a, b);              // commit first
await this.view.clearPair(a, b, path); // then let the view catch up
if (this.board.isEmpty()) await this.view.win();
```

The model is always at or ahead of the view; the view is a lagging projection that reads its own copy. State committed after an `await` leaves the model wrong for the whole duration of the animation, and every read during that window is wrong with it.

## 4. Cancel

A preempt (or a scene teardown) cancels the running command through a **token**. Port adapters call `token.throwIfCancelled()` after each await and register their tweens with the token, so the command unwinds through `Cancelled` instead of running its remaining lines against a dead scene.

Anything a command turns on — targeting mode, highlights, input locks — is turned off in `finally`, because the cancel path skips the normal ending.

## 5. Clock

Time lives in a `Clock` that logic owns and the render loop ticks with `dt`. The clock mutates only its own numbers and repaints through a fire-and-forget port method; when it reaches zero it **dispatches** a `queue` command rather than touching the board itself.

Pause bypasses the queue entirely: it stops the clock and calls `tweens.pauseAll()`. Commands stay suspended at their `await` because the tweens they wait on are frozen. A pause that dispatches a command would wait for the running animation before taking effect, which reads as a broken button.

Logic gets elapsed time only from `Clock` and waiting only from the port. A `setTimeout` in logic is a missing port method.

## Building it

1. **Tween layer first.** The port cannot exist until animations return promises and can be killed and globally paused. Read `references/ports.md`.
2. **Runtime.** Copy the reference implementation into a shared package the games depend on — it is identical across games. Read `references/runtime.md`. If the repo already has it, read that source instead; it is the source of truth.
3. **Port + commands per game.** Declare the port, classify every method `Promise<void>` or `void`, then write one command per input source with its policy.
4. **Headless adapter.** Read `references/headless.md`.

Timed buffs ("x2 for 10s", freeze, auto-hint) run beside the queue, not in it: read `references/effects.md`.

## Symptoms

| Symptom | Invariant | Fix |
|---|---|---|
| Two taps during one animation resolve two moves | 2 | Input source is not `drop`, or bypasses `dispatch` |
| A tile reappears, or a match resolves against a stale board | 3 | State committed after the `await` |
| Time-up fires but the win from the last move also fires | 2 | Both ran concurrently; expiry must be `queue` |
| Errors about destroyed nodes after quitting | 4 | Adapter is not checking the token |
| Pause button feels laggy | 5 | Pause went through the queue |
| Highlights stuck on after an abort | 4 | Cleanup is not in `finally` |
| A booster's target prompt swallows the next real tap | — | Input router still holds a resolved request: see `references/runtime.md` |
| Countdown drifts, or keeps running under the win animation | 5 | Clock is driven by wall time instead of `dt`, or the win command forgot `clock.pause()` |

## Other languages

The shape is language-independent. In C#, the port returns `UniTask`/`Task` and the token is a `CancellationToken`. In an engine with coroutines and no async, a command is a coroutine and the port returns an enumerator the runtime yields on; the five invariants are unchanged.
