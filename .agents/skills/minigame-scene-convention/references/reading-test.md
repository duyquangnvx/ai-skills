# Reading test — sanity check after scaffolding

Read when: after scaffolding any feature touching the gameplay loop, or when reviewing a teammate's PR.

## The principle

Open the Orchestrator method (or, if no Orchestrator, the Service method that drives the moment) and read top-to-bottom. A new reader must see the entire moment without:

- Grepping event names.
- Opening other files.
- Chasing listeners across an EventBus.

If they cannot, the feature is over-decomposed. Consolidate.

If a private method called from the Orchestrator hides essential gameplay flow, either inline it OR rename so the call site is self-explanatory (`this.applyLineClearScoring(clears)` is fine; `this.handleStuff(clears)` is not).

## Pass — flow visible top-to-bottom

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

## Fail — flow hidden behind opaque names and dispatch

```ts
async placeBlock(slot: number, ox: number, oy: number): Promise<void> {
    this.eventBus.emit('block_place_requested', { slot, ox, oy });
    await this.handleStuff();             // does what?
    await this.session.advance();          // owns flow somewhere else
}
```

This forces a reader to grep `block_place_requested`, open `handleStuff`, and trace `session.advance` to reconstruct the move. Three of the symptoms named at the top: grepping, opening other files, chasing listeners.

## Common consolidations

- **EventBus.emit replacing a hook**: replace with a hook field on the originating service. The fan-out the EventBus was hiding becomes explicit at the binding site (Scene `create()` with `Promise.all`, or one binder per view).
- **`SessionFlow.advance()` hiding the next step**: inline the advance logic into the Orchestrator method. If it doesn't fit, the `SessionFlow` was a second spine — see anti-patterns.md.
- **Private methods with opaque names** (`handleStuff`, `processInput`, `doNext`): rename to describe what gameplay step they perform, or inline if they're under 5 lines.
