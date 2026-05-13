# Orchestrator — full example

Read when: scaffolding the gameplay loop of a new game, or when an existing Orchestrator method has grown long and you need a reference shape to compare against.

This is the full `BlockBlastOrchestrator.placeBlock` shape that the SKILL.md trims for brevity. Use it to confirm structure, not as a template to copy verbatim — your domain has different state, hooks, and side effects.

## Full shape

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

## Things this example shows

- **`try / finally` for the re-entry guard.** A throwing hook handler must not strand `locked = true` — `finally` is the only safe place to release.
- **State mutation BEFORE the awaited hook.** Logic commits the state change first, then awaits the view animation. View binds against the post-state by querying the service.
- **Side-effects on other Services inline.** `this.wallet.add(...)` happens inside the Orchestrator method, not via a separate "WalletOrchestrator" — wallet is a Service.
- **Top-down readability.** Reading `placeBlock` top to bottom describes the entire move: validate → place → animate → clear → refill → check game over. No grepping needed.

## Things this example deliberately omits

- Sequence wiring — that lives in the Scene, not the Orchestrator.
- View instances — Orchestrator never imports view code.
- EventBus — gameplay flow does not use it.
