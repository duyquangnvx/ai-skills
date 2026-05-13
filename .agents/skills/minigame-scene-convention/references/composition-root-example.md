# Composition root — full example

Read when: scaffolding a new game's Scene file, or when `create()` is getting tangled and you need a reference shape.

The Scene is the only place that knows about every part. It does seven things, in order:

1. Instantiate logic services (with profile/save data injected).
2. Instantiate the Orchestrator (if any) with logic services injected.
3. Instantiate views with their logic services injected.
4. Call each view's `bind()` to wire hooks of the service it owns.
5. Wire Sequences to Orchestrator hooks.
6. Wire pointer/input handlers to view methods or Orchestrator commands.
7. On shutdown, call `unbind()` to release hooks.

## Phaser example

```ts
class BlockBlastScene {
    private bindings: Array<{ unbind: () => void }> = [];

    create(): void {
        // 1. Logic
        const grid       = new Grid(GRID_SIZE);
        const shapes     = new ShapeFactory(SHAPES);
        const tray       = new Tray(shapes.next3());
        const wallet     = new CoinWallet(profile.coins);
        const progression= new BlockBlastProgression(profile.blockBlast);

        // 2. Orchestrator
        const orchestrator = new BlockBlastOrchestrator(
            grid, tray, shapes, wallet, progression,
        );

        // 3. Views (DI logic)
        const gridView    = new GridView(this, grid);
        const trayView    = new TrayView(this, tray, grid, gridView, orchestrator);
        const hud         = new BlockBlastHud(this, orchestrator, progression);
        const coinBar     = new CoinBarView(this, wallet, gridView);
        const highScorePopup = new HighScorePopup(this, progression);

        // 4. Each view binds its own logic service's hooks
        gridView.bind(orchestrator);
        coinBar.bind();                    // wallet.onCoinsAdded
        highScorePopup.bind();             // progression.onNewHighScore
        this.bindings.push(gridView, coinBar, highScorePopup);

        // 5. Sequences wired to Orchestrator hooks
        const comboSeq = new ComboSequence(gridView, hud, this.cameras.main);
        orchestrator.onLinesCleared = (d) => comboSeq.play(d);

        // When two views must react to the same hook, fan out with Promise.all
        orchestrator.onBlockPlaced = async (d) => {
            await Promise.all([
                gridView.playBlockSnap(d),
                trayView.removeFromSlot(d.slot),
            ]);
        };

        // 6. Input wiring
        this.input.on('pointerdown', (p) => trayView.onPointerDown(p));
    }

    shutdown(): void {
        // 7. Teardown
        for (const b of this.bindings) b.unbind();
        this.bindings = [];
    }
}
```

## When `create()` gets too long

If `create()` exceeds ~100 lines, extract a free function `wireBlockBlastScene(scene)` in the same folder. Do NOT introduce a `SceneFlow` / `SessionFlow` class — that role does not exist in this convention; it would create a second spine on top of the Orchestrator (see anti-patterns).

```ts
// games/blockBlast/wireBlockBlastScene.ts
export function wireBlockBlastScene(scene: BlockBlastScene): { teardown: () => void } {
    // ... all the wiring above ...
    return { teardown: () => { for (const b of bindings) b.unbind(); } };
}

// games/blockBlast/BlockBlastScene.ts
class BlockBlastScene {
    private wired?: { teardown: () => void };
    create(): void { this.wired = wireBlockBlastScene(this); }
    shutdown(): void { this.wired?.teardown(); }
}
```

## Fan-out patterns

When N views need to react to a single Orchestrator hook:

- **Animation-gating fan-out** — Scene wires the lambda with `Promise.all` (logic awaits all view animations before continuing).
- **Cosmetic fan-out** — Scene wires the lambda with parallel `void` calls (no await, no gating).
- **Sequenced cross-system moment** — extract a Sequence; Scene wires the Orchestrator hook to call `sequence.play(d)`.

If you find yourself wanting a class to own the fan-out, you are recreating the spine. Use one of the three patterns above instead.
