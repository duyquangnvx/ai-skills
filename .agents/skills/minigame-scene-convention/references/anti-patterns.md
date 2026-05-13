# Anti-patterns and the convention's answer

Read when: reviewing existing code for convention compliance, or when a teammate proposes a design that feels off and you need to articulate why.

These are deviations seen often in TypeScript minigame codebases. Each row identifies which contract layer is violated and what the convention's compliant answer is.

| Deviation | What it violates | The convention's answer |
|---|---|---|
| Spine **on top of** the Orchestrator (SessionFlow / central dispatcher binding orchestrator hooks and fanning out to view + meta + observers) | Layer 2 (the Orchestrator IS already the spine; this is a double spine) | Each view binds its own logic service's hooks. Sequences for cross-system moments. Scene's `create()` for `Promise.all` cases. If `create()` is too long, extract `wireXxxScene(scene)` as a free function. |
| Mixed-role class (hooks + state + sequenced flow + view-binding-spine all in one) — regardless of name | Layer 2 (role-mix) | Decompose by role into Service(s) + Orchestrator + Sequence as needed. Naming is incidental. |
| Orchestrator for a feature that is a Service (`WalletOrchestrator`, `QuestOrchestrator`) | Layer 2 (Service mis-classified) | Demote to Service. Apply the decision tree. |
| EventBus driving gameplay (`EventBus.emit('match_made')` to notify view of a state change) | Layer 1 (logic→UI must be hook) | Add a hook field on the originating logic service. |
| Logic class importing engine (`import * as Phaser from 'phaser'`, `import { Vec2 } from 'cc'`, `import { Vector3 } from 'three'`) | Layer 1 (logic must be headless) | Move engine code to a corresponding View. Logic carries opaque payloads (`{x,y}`, indices); view translates to engine types. |
| Pure View class mutating logic state from inside a hook handler | Layer 1 (pure View hook handlers are animation only) | Either move the mutation to the Orchestrator's logic flow (before/after the hook), or recognize this is actually a Sequence and extract it. |
| Hook named for future intent (`onWillDie`, `onAboutToMatch`) | Layer 1 (hooks describe past logic events) | Rename to past-tense (`onUnitDied`, `onMatchSucceeded`). |
| Positional hook parameters (`onUnitDamaged?: (unit, value) => void`) | Layer 1 (params must be wrapped object) | Wrap in `{ unit, value }` data object. |
| Singleton/global service inside a game folder | Layer 2 + lifetime contract | Construct per-Scene in the composition root. Inject persistent values from a project-level store. |
| `interface IWallet { ... }` declarations alongside the Service class | Layer 1 (the hook field type and method signature already are the port) | Drop the interface. The TypeScript signature of `onCoinsAdded` and the method `add(amount)` is the port. |
| Hook payload shape duplicated at multiple binding sites | TS rule (don't duplicate shapes) | Extract `interface CoinsAddedPayload`, or derive view-side type with `Parameters<typeof service.onCoinsAdded>`. |
| Service query getter returns mutable array (`get items(): Item[]`) | Layer 1 (view can mutate by reference) | Return `readonly Item[]`. Keeps the read-only contract enforceable by the type system. |
| `<Game>Scene` with `create()` over ~100 lines doing all wiring inline | Readability | Extract free function `wireXxxScene(scene)` in the same folder. Do **not** introduce a `SceneFlow` / `SessionFlow` class — that creates a second spine on top of the Orchestrator. |
