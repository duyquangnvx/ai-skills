# Code review — anti-patterns and reading test

Two angles:

1. **Anti-patterns table** — concrete deviations and the convention's compliant answer. Use when something looks structurally wrong.
2. **Reading test** — top-to-bottom legibility check on the Orchestrator (or driving Service) method. Use after scaffolding to verify the result is actually readable.

---

## Anti-patterns table

The **canonical source** for deviations and fixes; SKILL.md highlights only the most-violated four. Each row names the violated contract and the answer.

| Deviation | What it violates | The convention's answer |
|---|---|---|
| **View implements a `GameView` / `BoardView` interface that the Orchestrator calls** (`view.lockPiece()`, `view.animatePops()`) | Contract direction (logic→view is delegate hooks, not a consumer-implemented port) | Invert it: logic exposes optional **hook fields** (`onPiecePlaced?`); the view **binds** them and decides its own reaction. Delete the `interface` — the hook field signature *is* the port. |
| **Imperative hook/method names** telling the view what to do (`flyCoins`, `playClearAnim`, `showPopup`, `animateDrops`) | Naming rule (name for what the producer *did*) | Rename to a past-tense producer fact (`onCoinsAdded`, `onLinesCleared`, `onTilesDropped`). The consumer maps the fact to its own action. |
| **EventBus carrying named presentation** (coin-flight, level-up popup, quest popup routed through `bus.emit`) | Litmus (named audience ⇒ delegate; only anonymous ⇒ bus) | Make it a hook on the originating Service/Orchestrator. Bus is reserved for *anonymous, arbitrary-N* ambient listeners (analytics, achievements, ambient audio). |
| **EventBus driving gameplay** (`bus.emit('match_made')` to advance the turn) | Layer 1 (gameplay order belongs to the Orchestrator) | Concentrate the order in the Orchestrator; emit facts to the bus only for kind-3 cross-cutting reactions. |
| **Missing `bind`/`unbind`** on a view that sets a hook | Lifecycle (Cocoa `weak` teardown) | Pair every `bind()` with `unbind()` that nulls the field; the composition root calls `unbind()` on shutdown. Orphaned handlers are the classic leak. |
| Spine **on top of** the Orchestrator (SessionFlow / GameManager binding orchestrator hooks and fanning out) | Layer 2 (the Orchestrator IS the spine; this is a second one) | Each view binds its own service's hooks; Sequences for cross-system moments; Scene `create()` for `Promise.all`. If `create()` is too long, extract `wireXxxScene(scene)` as a free function. |
| Mixed-role class (hooks + state + sequenced flow + view-binding all in one) — `BattleManager`, `GameManager`, … | Layer 2 (role-mix) | Decompose by role into Service(s) + Orchestrator + Sequence. The `*Manager` name is incidental; the role-mix is the smell. |
| Orchestrator for a feature that is a Service (`WalletOrchestrator`, `QuestOrchestrator`) | Layer 2 (Service mis-classified) | Demote to Service; apply the decision tree. |
| Hook on the Service when the Orchestrator must `await` it (`board.onBoardFull` when the next step is game-over) | Hook ownership (gating hooks belong to the Orchestrator) | Move the hook to the Orchestrator; the Service stays a pure state holder it queries, then the Orchestrator emits the gating hook. |
| Same moment emitted by both a Service hook and an Orchestrator hook (double-emit) | Hook ownership (one source per moment) | Pick one — usually the Orchestrator owns the gating hook and the Service stays hook-less for that change. |
| Logic importing the engine (`import Phaser`, `import { Vec2 } from 'cc'`, `Vector3`) | Layer 1 (logic is headless) | Move engine code to a View; logic carries opaque payloads (`{x,y}`, indices), the view translates. |
| Hook named for **future intent of a past event** (`onWillDie` for a death that already happened) | Naming (future tense is only for genuine gates) | `should…` (veto) and `will…` (pre-mutation prepare) are correct; a past event mislabeled as future is not — rename to `onDied`. |
| Positional hook params (`onDamaged?: (unit, value) => void`) | Payload rule | Wrap in one data object `{ unit, value }`. |
| Singleton/global service **inside** a game folder | Layer 2 + lifetime | Construct per-Scene in the composition root; inject persisted values. The `minigame-architecture` `Game` singleton is an app-level shell *outside* the folder, not an in-folder locator. |
| `interface IWallet { … }` alongside the Service | Layer 1 (the method/hook signatures already are the port) | Drop the interface. |
| Service query getter returns a mutable array (`get items(): Item[]`) | Layer 1 (view can mutate by reference) | Return `readonly Item[]`. |
| `<Game>Scene.create()` over ~100 lines of inline wiring | Readability | Extract a free function `wireXxxScene(scene)`; do **not** introduce a `SessionFlow`/`GameManager` class. |
| Hybridizing — "just this one class breaks the convention because…" | Authority (no per-file hybridization) | If it doesn't fit the whole feature, use a different convention (reducer/MVU, return-style FC/IS) — don't mix two in one file. |

---

## Reading test

### The principle

Open the Orchestrator method (or, if there is no Orchestrator, the Service method that drives the moment) and read top-to-bottom. A new reader must see the **entire moment** without:

- grepping event names,
- opening other files,
- chasing listeners across a bus.

If they can't, the feature is over-decomposed — consolidate. A private helper called from the Orchestrator is fine only if its name says what gameplay step it performs.

### Pass — flow visible top-to-bottom

```ts
async placePiece(slot: number, at: GridPos): Promise<void> {
  if (this.locked) return;
  this.locked = true;
  try {
    const cells = this.board.place(piece, at);
    await this.onPiecePlaced?.({ piece, cells, slot });

    const clears = this.board.findClears();
    if (clears.rows.length || clears.cols.length) {
      this.board.clear(clears);
      this.applyClearScoring(clears);          // self-explanatory name
      await this.onLinesCleared?.({ ...clears, score: this.score });
    }

    if (this.tray.isEmpty()) this.tray.refill(this.nextPieces());
  } finally {
    this.locked = false;
  }
}
```

A reader sees: lock → place → animate → clear+score+animate → refill → unlock. Whole move in one file.

### Fail — flow hidden behind dispatch and opaque names

```ts
async placePiece(slot: number, at: GridPos): Promise<void> {
  this.bus.emit('piece_place_requested', { slot, at });
  await this.handleStuff();        // does what?
  await this.session.advance();     // owns flow somewhere else
}
```

This forces the reader to grep `piece_place_requested`, open `handleStuff`, and trace `session.advance` to reconstruct the move — all three symptoms at once.

### Common consolidations

- **`bus.emit` replacing a hook** → replace with a hook field on the originating service; the fan-out the bus hid becomes explicit at the binding site (`Promise.all`, or one binder per view).
- **`SessionFlow.advance()` hiding the next step** → inline it into the Orchestrator; if it won't fit, it was a second spine.
- **Opaque private methods** (`handleStuff`, `processInput`, `doNext`) → rename to the gameplay step they perform, or inline if under ~5 lines.
