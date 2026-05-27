# Composition root — full example, fan-out patterns, engine variations

The Scene is the only place that knows about every part. It does seven things, in order:

1. Instantiate logic services (with profile/save data injected).
2. Instantiate the Orchestrator (if any) with logic services injected.
3. Instantiate views with their logic services injected.
4. Call each view's `bind()` to wire hooks of the service it owns.
5. Wire Sequences to Orchestrator hooks.
6. Wire pointer/input handlers to view methods or Orchestrator commands.
7. On shutdown, call `unbind()` to release hooks.

## Phaser example (default)

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

If `create()` exceeds ~100 lines, extract a free function `wireBlockBlastScene(scene)` in the same folder. Do NOT introduce a `SceneFlow` / `SessionFlow` class — that role does not exist in this convention; it would create a second spine on top of the Orchestrator (see `code-review.md` → anti-patterns).

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

---

## Engine variations

The convention's role classification, communication contract, and folder structure all carry over to any engine. Only the host container of the composition root differs.

### Cocos Creator (ECS-first, Node + Component)

The composition root is a bootstrap Component attached to the scene's root Node.

- Logic services and Orchestrator instantiate inside `onLoad()` or `start()`.
- Views are sibling Components or Components on child Nodes.
- Teardown in `onDestroy()` calls each view's `unbind()`.

Same wiring logic, different host. The `<Game>Scene.ts` file becomes `<Game>SceneRoot.ts` (a Component).

### PixiJS / custom canvas

The composition root is wherever the game loop is constructed — a `Game` class, a function, or a top-level module. The Scene file becomes a regular module that exports a setup function:

```ts
export function createBlockBlast(app: PIXI.Application): { destroy: () => void } {
    // instantiate logic, orchestrator, views
    // bind hooks
    // return cleanup
}
```

### Three.js / 3D

Same as PixiJS — composition root is wherever the renderer plus scene graph is created. The convention's role boundaries (logic headless, view side-effecting) do not change just because rendering is 3D.

### Common gotchas

- **Engine-typed positions in logic.** Even on Cocos, a `Vec2` from `cc` is an engine import. Logic should use plain `{ x: number; y: number }` and let view translate.
- **Engine-tied lifecycle hooks leaking into logic.** Logic services should not subscribe to `update()` / `tick()` — that is view's territory. If logic needs time, accept `dt` as a parameter on a tick method that the view calls.
- **Frameworks with their own DI container.** If using Angular-style or Cocos's component graph as DI, the composition root is still the place where logic instances are created and handed to views — do not let views grab logic from a global registry.
