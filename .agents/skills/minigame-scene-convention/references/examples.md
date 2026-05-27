# Code examples — Orchestrator and Sequence

## Orchestrator examples

### BlockBlast — full gameplay loop

The shape that SKILL.md trims for brevity. Use it to confirm structure, not as a template to copy verbatim — your domain has different state, hooks, and side effects.

```ts
class BlockBlastOrchestrator {
    onBlockPlaced?: (d: PlacementResult) => Promise<void>;
    onLinesCleared?: (d: ClearResult & { score: number; combo: number }) => Promise<void>;
    onTrayRefilled?: (d: { blocks: BlockShape[] }) => Promise<void>;
    onGameOver?: (d: { score: number; reason: GameOverReason }) => Promise<void>;

    private locked = false;
    private combo = 0;
    private score = 0;

    constructor(
        private grid: Grid,
        private tray: Tray,
        private shapes: ShapeFactory,
        private wallet: CoinWallet,
        private progression: BlockBlastProgression,
    ) {}

    async placeBlock(slot: number, ox: number, oy: number): Promise<void> {
        if (this.locked) return;
        const block = this.tray.peek(slot);
        if (!block || !PlacementValidator.canPlace(this.grid, block, ox, oy)) return;
        this.locked = true;
        try {
            const cells = this.grid.place(block, ox, oy);
            this.tray.consume(slot);
            await this.onBlockPlaced?.({ block, cells, slot });

            const clears = LineClearer.findClears(this.grid);
            if (clears.rows.length || clears.cols.length) {
                const cleared = this.grid.clearLines(clears.rows, clears.cols);
                const score = scoreForClear(clears, this.combo);
                this.combo += 1;
                this.score += score;
                this.wallet.add(coinForClear(clears), { source: { worldPos: centroid(cleared) } });
                await this.onLinesCleared?.({ ...clears, cells: cleared, score, combo: this.combo });
            } else {
                this.combo = 0;
            }

            if (this.tray.isEmpty()) {
                const blocks = this.shapes.next3();
                this.tray.refill(blocks);
                await this.onTrayRefilled?.({ blocks });
            }

            if (!PlacementValidator.anyPlaceable(this.grid, this.tray.peekAll())) {
                await this.onGameOver?.({ score: this.score, reason: 'no_moves' });
            }
        } finally {
            this.locked = false;
        }
    }
}
```

What this example shows:

- **`try / finally` for the re-entry guard.** A throwing hook handler must not strand `locked = true` — `finally` is the only safe place to release.
- **State mutation BEFORE the awaited hook.** Logic commits the state change first, then awaits the view animation. View binds against the post-state by querying the service.
- **Side-effects on other Services inline.** `this.wallet.add(...)` happens inside the Orchestrator method, not via a separate "WalletOrchestrator" — wallet is a Service.
- **Top-down readability.** Reading `placeBlock` top to bottom describes the entire move: validate → place → animate → clear → refill → check game over. No grepping needed.

What this example deliberately omits:

- Sequence wiring — that lives in the Scene, not the Orchestrator.
- View instances — Orchestrator never imports view code.
- EventBus — gameplay flow does not use it.

### BoardOrchestrator — hook ownership

A different game (single-tile drop, game-over on full board) showing the same script structure with two consecutive gating hooks. Useful as a reference when working out which hook belongs on the Orchestrator vs the Service.

```ts
class BoardOrchestrator {
    onTilePlaced?: (d: { pos: Pos }) => Promise<void>;
    onBoardFull?: (d: { board: BoardSnapshot }) => Promise<void>;
    onGameOver?: (d: { score: number }) => Promise<void>;

    private locked = false;
    private score = 0;

    constructor(
        private board: Board,
        private wallet: CoinWallet,
    ) {}

    async dropTile(slot: number, pos: Pos): Promise<void> {
        if (this.locked) return;
        this.locked = true;
        try {
            this.board.place(slot, pos);                       // Service: pure mutation, no hook
            await this.onTilePlaced?.({ pos });                // gate: tile-drop animation

            if (this.board.isFull()) {                         // Service: query
                await this.onBoardFull?.({ board: this.board.snapshot() });
                await this.onGameOver?.({ score: this.score });
            }
        } finally {
            this.locked = false;
        }
    }
}
```

What this example shows about hook ownership:

- `Board` is a Service that exposes `place()` and `isFull()` but emits **no hook**. Its state changes are queried by the Orchestrator, not announced.
- `onTilePlaced`, `onBoardFull`, `onGameOver` all live on the Orchestrator because each one gates a subsequent line in `dropTile` (or terminates the flow).
- Compare with `wallet.onCoinsAdded` from BlockBlast: that lives on the Service because no Orchestrator line awaits it — only the CoinBarView reacts.

The principle: hook ownership follows *who needs to `await` it*, not *who owns the state*. See SKILL.md → "Hook ownership: Service or Orchestrator?".

---

## Sequence examples

### Class form — `LevelClearSequence`

Use a class when you have 4+ DI args or multiple `play*` methods sharing dependencies.

```ts
class LevelClearSequence {
    constructor(
        private chest: ChestView,
        private flight: CoinFlightView,
        private bar: CoinBarView,
        private wallet: CoinWallet,                  // logic DI — Sequence may write
        private progression: OnetProgression,        // logic DI — Sequence may write
    ) {}

    async play(reward: Reward, level: number): Promise<void> {
        await this.chest.playOpen();
        await this.flight.fly(this.chest.pos, this.bar.pos, reward.coins);
        this.wallet.add(reward.coins);                                     // commit
        const stars = this.progression.applyLevelClear(level, reward.score);
        await this.bar.popup.show(stars);
    }
}
```

Why this is a Sequence and not an Orchestrator:

- It is a one-shot script triggered from a specific hook (e.g., `orchestrator.onLevelCleared`).
- It does not own gameplay state or hooks of its own.
- It does not own the gameplay loop; it only choreographs one cross-system moment.

The composition root wires it:

```ts
const levelClear = new LevelClearSequence(chest, flight, bar, wallet, progression);
orchestrator.onLevelCleared = (d) => levelClear.play(d.reward, d.level);
```

### Function form — short DI list

For ≤ 3 DI args, use a free function instead. Same semantics, less ceremony.

```ts
async function playMatchPop(
    view: BoardView,
    sound: SoundService,
    cells: Cell[],
): Promise<void> {
    await view.popCells(cells);
    sound.play('match');
}

// in Scene wiring:
orchestrator.onMatchMade = ({ cells }) => playMatchPop(boardView, sound, cells);
```

### Multi-`play*` class — grouped related sequences

When several related sequences share dependencies, group them in a class. Each `play*` method is still a one-shot.

```ts
class BoosterSequences {
    constructor(
        private board: BoardView,
        private hud: BoosterHud,
        private sound: SoundService,
    ) {}

    async playRocket(row: number): Promise<void> { /* ... */ }
    async playBomb(cell: Cell): Promise<void> { /* ... */ }
    async playColorBomb(color: Color): Promise<void> { /* ... */ }
}
```

### Counter-example — when NOT to extract

If the choreography fits inline (≤ 5 lines, ≤ 2 UI components), keep it in the view hook handler:

```ts
class CoinBarView {
    bind(): void {
        this.wallet.onCoinsAdded = async ({ amount, newBalance }) => {
            await this.flight.fly(this.startPos, this.barPos, amount);
            this.label.setText(String(newBalance));
        };
    }
}
```

Extracting this into a `CoinAddSequence` is over-engineering — the choreography is the view's natural responsibility for that one hook.

### What a Sequence is NOT

- **Not an Orchestrator.** A Sequence has no `locked` flag, no hook fields of its own, no ownership of the gameplay loop. If it grows hook fields or a `locked` flag, you have created an Orchestrator-shaped class — apply the role decision tree.
- **Not a Service.** A Sequence holds no persistent state and is not queried by views. Its DI references are read-only handles to commit at the right moment, then discarded.
- **Not a manager / dispatcher.** A Sequence does not bind hooks on behalf of other classes; it is invoked by something else binding a hook to its `play()` method.
