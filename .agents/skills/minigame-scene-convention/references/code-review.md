# Code review reference — anti-patterns and reading test

Two angles:

1. **Anti-patterns table** — concrete deviations and the convention's compliant answer. Use when something looks structurally wrong.
2. **Reading test** — top-to-bottom legibility check on the Orchestrator (or driving Service) method. Use after scaffolding to verify the result is actually readable.

---

## Anti-patterns table

This is the **canonical source** for deviations and their fixes. SKILL.md only highlights the three most-violated rationalizations; the rest live here.

Each row identifies which contract layer is violated and what the convention's compliant answer is.

| Deviation | What it violates | The convention's answer |
|---|---|---|
| Spine **on top of** the Orchestrator (SessionFlow / central dispatcher binding orchestrator hooks and fanning out to view + meta + observers) | Layer 2 (the Orchestrator IS already the spine; this is a double spine) | Each view binds its own logic service's hooks. Sequences for cross-system moments. Scene's `create()` for `Promise.all` cases. If `create()` is too long, extract `wireXxxScene(scene)` as a free function. |
| Mixed-role class (hooks + state + sequenced flow + view-binding-spine all in one) — including `BattleManager`, `GameManager`, etc. | Layer 2 (role-mix) | Decompose by role into Service(s) + Orchestrator + Sequence as needed. The `*Manager` name is incidental; the role-mix is the smell. |
| Orchestrator for a feature that is a Service (`WalletOrchestrator`, `QuestOrchestrator`) | Layer 2 (Service mis-classified) | Demote to Service. Apply the decision tree. |
| Hook placed on the Service when the Orchestrator must `await` it (`board.onBoardFull` when the next gameplay step is game-over) | Hook-ownership rule (gating hooks belong to the Orchestrator) | Move the hook to the Orchestrator. The Service stays a pure state holder; Orchestrator calls `service.query()` then emits the gating hook itself. See SKILL.md → Hook ownership. |
| Same moment emitted both by Service hook and Orchestrator hook (double-emit) | Hook-ownership rule (one source of truth per moment) | Pick one. Default: Orchestrator owns the gating hook, Service stays hook-less for that change. If two views need different gating, model as a Sequence. |
| EventBus driving gameplay (`EventBus.emit('match_made')` to notify view of a state change) | Layer 1 (logic→UI must be hook) | Add a hook field on the originating logic service or Orchestrator. EventBus is for genuine N-to-1 ambient listeners only. |
| Logic class importing engine (`import * as Phaser from 'phaser'`, `import { Vec2 } from 'cc'`, `import { Vector3 } from 'three'`) | Layer 1 (logic must be headless) | Move engine code to a corresponding View. Logic carries opaque payloads (`{x,y}`, indices); view translates to engine types. |
| Pure View class mutating logic state from inside a hook handler | Layer 1 (pure View hook handlers are animation only) | Either move the mutation to the Orchestrator's logic flow (before/after the hook), or recognize this is actually a Sequence and extract it. |
| Hook named for future intent (`onWillDie`, `onAboutToMatch`) | Layer 1 (hooks describe past logic events) | Rename to past-tense (`onUnitDied`, `onMatchSucceeded`). |
| Positional hook parameters (`onUnitDamaged?: (unit, value) => void`) | Layer 1 (params must be wrapped object) | Wrap in `{ unit, value }` data object. |
| Singleton/global service inside a game folder | Layer 2 + lifetime contract | Construct per-Scene in the composition root. Inject persistent values from a project-level store. |
| `interface IWallet { ... }` declarations alongside the Service class | Layer 1 (the hook field type and method signature already are the port) | Drop the interface. The TypeScript signature of `onCoinsAdded` and the method `add(amount)` is the port. |
| Hook payload shape duplicated at multiple binding sites | TS rule (don't duplicate shapes) | Extract `interface CoinsAddedPayload`, or derive view-side type with `Parameters<typeof service.onCoinsAdded>`. |
| Service query getter returns mutable array (`get items(): Item[]`) | Layer 1 (view can mutate by reference) | Return `readonly Item[]`. Keeps the read-only contract enforceable by the type system. |
| `<Game>Scene` with `create()` over ~100 lines doing all wiring inline | Readability | Extract free function `wireXxxScene(scene)` in the same folder. Do **not** introduce a `SceneFlow` / `SessionFlow` class — that creates a second spine on top of the Orchestrator. |
| Hybridizing — "just this one class breaks the convention because [reason]" | Authority rule (no per-file hybridization) | If the convention does not fit the whole feature, change the convention or use a different one (Redux/MVU, return-style FC/IS). Mixing two conventions in one file leaves both readers and tooling guessing. |

---

## Reading test

### The principle

Open the Orchestrator method (or, if no Orchestrator, the Service method that drives the moment) and read top-to-bottom. A new reader must see the entire moment without:

- Grepping event names.
- Opening other files.
- Chasing listeners across an EventBus.

If they cannot, the feature is over-decomposed. Consolidate.

If a private method called from the Orchestrator hides essential gameplay flow, either inline it OR rename so the call site is self-explanatory (`this.applyLineClearScoring(clears)` is fine; `this.handleStuff(clears)` is not).

### Pass — flow visible top-to-bottom

```ts
async placeBlock(slot: number, ox: number, oy: number): Promise<void> {
    if (this.locked) return;
    this.locked = true;
    try {
        const cells = this.grid.place(block, ox, oy);
        await this.onBlockPlaced?.({ block, cells });

        if (clears.any) {
            this.applyLineClearScoring(clears);     // self-explanatory name
            await this.onLinesCleared?.({ ... });
        }

        if (this.tray.isEmpty()) {
            this.tray.refill(this.shapes.next3());
            await this.onTrayRefilled?.({ ... });
        }
    } finally {
        this.locked = false;
    }
}
```

A reader sees: lock → place → animate → score+animate → refill+animate → unlock. Whole move in one file.

### Fail — flow hidden behind opaque names and dispatch

```ts
async placeBlock(slot: number, ox: number, oy: number): Promise<void> {
    this.eventBus.emit('block_place_requested', { slot, ox, oy });
    await this.handleStuff();             // does what?
    await this.session.advance();          // owns flow somewhere else
}
```

This forces a reader to grep `block_place_requested`, open `handleStuff`, and trace `session.advance` to reconstruct the move. Three of the symptoms named at the top: grepping, opening other files, chasing listeners.

### Common consolidations

- **EventBus.emit replacing a hook**: replace with a hook field on the originating service. The fan-out the EventBus was hiding becomes explicit at the binding site (Scene `create()` with `Promise.all`, or one binder per view).
- **`SessionFlow.advance()` hiding the next step**: inline the advance logic into the Orchestrator method. If it doesn't fit, the `SessionFlow` was a second spine — see the anti-patterns table above.
- **Private methods with opaque names** (`handleStuff`, `processInput`, `doNext`): rename to describe what gameplay step they perform, or inline if they're under 5 lines.
