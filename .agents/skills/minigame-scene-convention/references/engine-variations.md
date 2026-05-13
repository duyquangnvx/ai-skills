# Engine variations

Read when: scaffolding a minigame on an engine other than Phaser.

The convention's role classification, communication contract, and folder structure all carry over to any engine. Only the host container of the composition root differs.

## Phaser (default assumption)

The composition root is a Scene class. `create()` is where logic, orchestrator, and views are instantiated and wired. Teardown happens in `shutdown()` — call each view's `unbind()` there.

## Cocos Creator (ECS-first, Node + Component)

The composition root is a bootstrap Component attached to the scene's root Node.

- Logic services and Orchestrator instantiate inside `onLoad()` or `start()`.
- Views are sibling Components or Components on child Nodes.
- Teardown in `onDestroy()` calls each view's `unbind()`.

Same wiring logic, different host. The `<Game>Scene.ts` file becomes `<Game>SceneRoot.ts` (a Component).

## PixiJS / custom canvas

The composition root is wherever the game loop is constructed — a `Game` class, a function, or a top-level module. The Scene file becomes a regular module that exports a setup function:

```ts
export function createBlockBlast(app: PIXI.Application): { destroy: () => void } {
    // instantiate logic, orchestrator, views
    // bind hooks
    // return cleanup
}
```

## Three.js / 3D

Same as PixiJS — composition root is wherever the renderer plus scene graph is created. The convention's role boundaries (logic headless, view side-effecting) do not change just because rendering is 3D.

## Common gotchas

- **Engine-typed positions in logic.** Even on Cocos, a `Vec2` from `cc` is an engine import. Logic should use plain `{ x: number; y: number }` and let view translate.
- **Engine-tied lifecycle hooks leaking into logic.** Logic services should not subscribe to `update()` / `tick()` — that is view's territory. If logic needs time, accept `dt` as a parameter on a tick method that the view calls.
- **Frameworks with their own DI container.** If using Angular-style or Cocos's component graph as DI, the composition root is still the place where logic instances are created and handed to views — do not let views grab logic from a global registry.
