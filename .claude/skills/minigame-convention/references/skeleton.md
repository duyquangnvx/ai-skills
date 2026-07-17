# Skeleton — project tree + key code

A fill-in-the-blanks template, not a specific game. One neutral thread runs through every file: a board where the player places a **Piece** from a **Tray**, lines clear, a **Wallet** awards coins. Copy it, rename the domain nouns, fill in your turn. The shapes — not the nouns — are the convention.

Logic is plain TypeScript with **zero engine imports**. Only `view/` and the Scene touch Phaser; swapping engines changes only those (see *Engine variations* at the end).

## Project tree

```
games/board/
├── BoardScene.ts                 # composition root: instantiate + wire + teardown
├── logic/
│   ├── core/
│   │   ├── types.ts              # plain payload + domain types (no engine)
│   │   ├── Board.ts              # Service: grid state, queries, pure mutation
│   │   ├── Tray.ts               # Service: current pieces, data-source queries
│   │   ├── PlacementValidator.ts # pure functions (callable from view)
│   │   └── BoardOrchestrator.ts  # the gameplay spine — placePiece()
│   └── wallet/
│       └── Wallet.ts             # Service: coins + standalone onCoinsAdded hook
├── view/
│   ├── core/
│   │   ├── BoardView.ts          # binds Orchestrator gating hooks
│   │   └── TrayView.ts           # drag input → Orchestrator command
│   ├── wallet/
│   │   └── CoinBarView.ts        # binds wallet.onCoinsAdded
│   └── sequences/
│       └── playGameOver.ts       # one-shot cross-system choreography
├── config/
│   └── constants.ts
└── index.ts
```

## logic/core/types.ts — plain data only

```ts
export interface GridPos { x: number; y: number }      // never an engine Vec2
export interface Piece { id: string; cells: GridPos[] }

export interface PlacementResult {
  piece: Piece;
  cells: GridPos[];          // committed grid cells
  slot: number;
}
export interface ClearResult {
  rows: number[];
  cols: number[];
  cells: GridPos[];          // cells that were cleared
}
```

## logic/core/Board.ts — a Service (state + queries + pure mutation, no hook here)

The Board mutates and answers queries synchronously. It exposes **no hook** for placement/clear: those moments gate the Orchestrator's next step, so the Orchestrator owns those hooks (see SKILL.md → Hook ownership). Collection getters are `readonly` so the view can't mutate state by reference.

```ts
import type { GridPos, Piece, ClearResult } from './types';

export class Board {
  private cells: (string | null)[][];

  constructor(private size: number) {
    this.cells = Array.from({ length: size }, () => Array<string | null>(size).fill(null));
  }

  get occupied(): readonly (readonly (string | null)[])[] { return this.cells; }   // query (readonly)

  place(piece: Piece, at: GridPos): GridPos[] {                                     // pure command
    const placed = piece.cells.map((c) => ({ x: at.x + c.x, y: at.y + c.y }));
    for (const c of placed) this.cells[c.y][c.x] = piece.id;
    return placed;
  }

  findClears(): ClearResult { /* scan rows/cols, return indices + cells */ return { rows: [], cols: [], cells: [] }; }
  clear(result: ClearResult): void { for (const c of result.cells) this.cells[c.y][c.x] = null; }
  isFull(): boolean { return this.cells.every((row) => row.every((c) => c !== null)); }
}
```

## logic/core/Tray.ts — a Service whose queries are a data source

`peek`/`peekAll` are **pull** queries (data source), not push notifications — the producer calls them to proceed.

```ts
import type { Piece } from './types';

export class Tray {
  private slots: (Piece | null)[];
  constructor(initial: Piece[]) { this.slots = [...initial]; }

  peek(slot: number): Piece | null { return this.slots[slot] ?? null; }   // data source: pull
  peekAll(): readonly (Piece | null)[] { return this.slots; }             // data source: pull (readonly)
  isEmpty(): boolean { return this.slots.every((p) => p === null); }

  consume(slot: number): void { this.slots[slot] = null; }
  refill(pieces: Piece[]): void { this.slots = [...pieces]; }
}
```

## logic/core/BoardOrchestrator.ts — the spine

The whole `placePiece` moment reads top-to-bottom. **State mutates inline (kind 1); presentation is an awaited hook (kind 2).** Hook fields are named for what the producer **did** — never for what the view should do. This thread shows one of each rarer tier: a `should…` veto gate and a `will…` pre-mutation gate; the rest are `did…`.

```ts
import type { GridPos, PlacementResult, ClearResult } from './types';
import { PlacementValidator } from './PlacementValidator';
import { Board } from './Board';
import { Tray } from './Tray';
import { Wallet } from '../wallet/Wallet';

export class BoardOrchestrator {
  // Decision gate (rare): consumer may veto, e.g. a tutorial blocking input.
  shouldPlacePiece?: (d: { slot: number; at: GridPos }) => Promise<boolean>;
  // Completion gate, pre-mutation (rare): view "arms" the row before it disappears.
  onWillClear?: (d: ClearResult) => Promise<void>;
  // Completion gates, post-mutation (the common case): view animates, producer waits.
  onPiecePlaced?: (d: PlacementResult) => Promise<void>;
  onLinesCleared?: (d: ClearResult & { score: number }) => Promise<void>;
  onGameOver?: (d: { score: number }) => Promise<void>;

  private locked = false;
  private score = 0;

  constructor(
    private board: Board,
    private tray: Tray,
    private wallet: Wallet,
    private nextPieces: () => import('./types').Piece[],
  ) {}

  async placePiece(slot: number, at: GridPos): Promise<void> {
    if (this.locked) return;
    const piece = this.tray.peek(slot);                                  // data source: pull
    if (!piece || !PlacementValidator.canPlace(this.board, piece, at)) return;

    const ok = await this.shouldPlacePiece?.({ slot, at });              // decision gate
    if (ok === false) return;                                            // vetoed

    this.locked = true;
    try {
      const cells = this.board.place(piece, at);                         // kind 1: mutate down
      this.tray.consume(slot);
      await this.onPiecePlaced?.({ piece, cells, slot });                // kind 2: await across

      const clears = this.board.findClears();
      if (clears.rows.length || clears.cols.length) {
        await this.onWillClear?.(clears);                                // gate BEFORE mutation
        this.board.clear(clears);                                        // kind 1: mutate down
        this.score += clears.cells.length;                              // kind 1: mutate down
        this.wallet.add(clears.cells.length);                           // kind 1: inline, NOT a WalletOrchestrator
        await this.onLinesCleared?.({ ...clears, score: this.score });  // kind 2: await across
      }

      if (this.tray.isEmpty()) this.tray.refill(this.nextPieces());

      if (!PlacementValidator.anyPlaceable(this.board, this.tray.peekAll())) {
        await this.onGameOver?.({ score: this.score });                 // kind 2: await across
      }
    } finally {
      this.locked = false;                                              // released even if a handler threw
    }
  }
}
```

## logic/wallet/Wallet.ts — a Service that owns a standalone hook

No Orchestrator step awaits the coin flight, so the **Service** owns `onCoinsAdded` and fires it `void` (notification tier). Persistent balance is injected, not loaded here.

```ts
export class Wallet {
  onCoinsAdded?: (d: { amount: number; balance: number }) => Promise<void>;
  private balance_: number;

  constructor(initial: number) { this.balance_ = initial; }
  get balance(): number { return this.balance_; }                       // query

  add(amount: number): void {                                           // command
    this.balance_ += amount;
    void this.onCoinsAdded?.({ amount, balance: this.balance_ });       // notification: not awaited
  }
}
```

## view/core/BoardView.ts — binds hooks, decides its own reaction

The view **binds** the producer's hook fields; it does not implement a `GameView` interface and the Orchestrator never calls it directly. `bind`/`unbind` is the lifecycle teardown (Cocoa's `weak` spirit). The handler reacts however it wants — the hook name (`onPiecePlaced`) said only what logic *did*.

```ts
import Phaser from 'phaser';
import type { BoardOrchestrator } from '../../logic/core/BoardOrchestrator';

export class BoardView {
  constructor(private scene: Phaser.Scene, private orch: BoardOrchestrator) {}

  bind(): void {
    this.orch.onPiecePlaced = async ({ cells }) => { await this.snap(cells); };
    this.orch.onWillClear  = async ({ cells })  => { await this.arm(cells); };
    this.orch.onLinesCleared = async ({ cells, score }) => {
      await this.burst(cells);
      this.setScore(score);
    };
  }
  unbind(): void {
    this.orch.onPiecePlaced = undefined;
    this.orch.onWillClear = undefined;
    this.orch.onLinesCleared = undefined;
  }

  private snap(_c: { x: number; y: number }[]): Promise<void> { return tween(this.scene, {}); }
  private arm(_c: { x: number; y: number }[]): Promise<void> { return tween(this.scene, {}); }
  private burst(_c: { x: number; y: number }[]): Promise<void> { return tween(this.scene, {}); }
  private setScore(_s: number): void {}
}

// the linchpin: a tween resolves a Promise on complete, so `await` gates the flow.
function tween(scene: Phaser.Scene, cfg: Phaser.Types.Tweens.TweenBuilderConfig): Promise<void> {
  return new Promise((resolve) => { scene.tweens.add({ ...cfg, onComplete: () => resolve() }); });
}
```

## view/core/TrayView.ts — input flows view → logic via a direct command

```ts
import Phaser from 'phaser';
import type { BoardOrchestrator } from '../../logic/core/BoardOrchestrator';

export class TrayView {
  constructor(private scene: Phaser.Scene, private orch: BoardOrchestrator) {}

  onDrop(slot: number, at: { x: number; y: number }): void {
    void this.orch.placePiece(slot, at);                                // command call, no event bus
  }
}
```

## view/wallet/CoinBarView.ts — binds the Service hook

```ts
import type { Wallet } from '../../logic/wallet/Wallet';

export class CoinBarView {
  constructor(private wallet: Wallet) {}
  bind(): void {
    this.wallet.onCoinsAdded = async ({ amount, balance }) => {
      await this.flyCoins(amount);      // the view names its OWN action; the hook did not
      this.setLabel(balance);
    };
  }
  unbind(): void { this.wallet.onCoinsAdded = undefined; }
  private flyCoins(_n: number): Promise<void> { return Promise.resolve(); }
  private setLabel(_b: number): void {}
}
```

## view/sequences/playGameOver.ts — a Sequence (one-shot, no state, no hooks)

Extract a Sequence when choreography crosses 2+ UI components or exceeds ~5 lines. A free function suffices for ≤ 3 DI args; use a class for more or for multiple `play*` methods. A Sequence holds DI handles and may commit logic at controlled visual moments — the explicit exception to "the view doesn't write logic state."

```ts
import type { BoardView } from '../core/BoardView';

export async function playGameOver(
  board: BoardView,
  overlay: { reveal: (score: number) => Promise<void> },
  score: number,
): Promise<void> {
  await overlay.reveal(score);
}
```

## BoardScene.ts — composition root

The only place that knows every part: instantiate logic (persisted values injected) → Orchestrator → views (logic injected) → `bind()` each view → wire Sequences and `Promise.all` fan-out to Orchestrator hooks → wire input → `unbind()` on shutdown. No singletons; everything is per-Scene.

```ts
import Phaser from 'phaser';
import { Board } from './logic/core/Board';
import { Tray } from './logic/core/Tray';
import { Wallet } from './logic/wallet/Wallet';
import { BoardOrchestrator } from './logic/core/BoardOrchestrator';
import { BoardView } from './view/core/BoardView';
import { TrayView } from './view/core/TrayView';
import { CoinBarView } from './view/wallet/CoinBarView';
import { playGameOver } from './view/sequences/playGameOver';

export class BoardScene extends Phaser.Scene {
  private bindings: Array<{ unbind(): void }> = [];

  create(profile: { coins: number }): void {
    // 1. logic (persisted values injected)
    const board = new Board(8);
    const tray = new Tray([/* initial pieces */]);
    const wallet = new Wallet(profile.coins);

    // 2. orchestrator
    const orch = new BoardOrchestrator(board, tray, wallet, () => [/* next pieces */]);

    // 3. views (DI logic) + 4. bind
    const boardView = new BoardView(this, orch);
    const trayView = new TrayView(this, orch);
    const coinBar = new CoinBarView(wallet);
    boardView.bind(); coinBar.bind();
    this.bindings.push(boardView, coinBar);

    // 5. Sequence + fan-out wired at the Scene (the producer stays unaware)
    const overlay = { reveal: (_s: number) => Promise.resolve() };
    orch.onGameOver = (d) => playGameOver(boardView, overlay, d.score);
    // when two views react to one moment, compose with Promise.all here:
    // orch.onPiecePlaced = (d) => Promise.all([boardView.snap(d.cells), trayView.clear(d.slot)]).then(() => {});

    // 6. input wiring (view → logic command)
    this.input.on('drop', (_p: unknown, slot: number, at: { x: number; y: number }) => trayView.onDrop(slot, at));
  }

  shutdown(): void {
    for (const b of this.bindings) b.unbind();   // 7. teardown
    this.bindings = [];
  }
}
```

If `create()` outgrows ~100 lines, extract a free function `wireBoardScene(scene)` in the same folder — **never** a `SessionFlow`/`GameManager` class (that is a second spine; see `code-review.md`).

## Engine variations

Role classification, the communication contract, and the folder tree carry over to any engine; only the **host of the composition root** changes.

- **Cocos Creator** — the root is a bootstrap `Component` on the scene's root Node: instantiate in `onLoad`/`start`, `unbind()` in `onDestroy`. `<Game>Scene.ts` becomes `<Game>SceneRoot.ts`. Note: a `Vec2` from `cc` is an engine import — logic still uses plain `{ x, y }`.
- **PixiJS / custom canvas** — the root is wherever the loop is built; export `createBoard(app): { destroy(): void }`.
- **Three.js / 3D** — same as Pixi; logic/view boundaries don't change because rendering is 3D.
- **Common gotcha** — logic services must not subscribe to `update()`/`tick()`; if logic needs time, accept `dt` on a method the view calls.
