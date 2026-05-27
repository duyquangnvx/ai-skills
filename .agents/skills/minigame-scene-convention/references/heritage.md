# Heritage and stated assumptions

This convention is an opinionated combination of established patterns adapted for TypeScript minigames. Knowing the lineage helps make informed deviations.

## Heritage

- **Functional Core / Imperative Shell** (Bernhardt) and **Hexagonal Architecture / Ports and Adapters** (Cockburn) — the rule that logic does not import engine, and view is the side-effect surface.
- **Saga: orchestration over choreography** — the case for a single Orchestrator owning the flow over EventBus-driven gameplay where order is scattered across listeners.
- **Async game state machines** (HalfMaid.Async, Unity Awaitable, lifecycle-delegate pattern) — awaitable hooks make gameplay flow read top-down with explicit animation gating.
- **Service Layer** (Fowler, PoEAA) — what the Service role inherits from.
- **Sequence controller** (common pattern in Phaser production guides) — formalized here as the Sequence role.

## Stated assumptions

These are assumptions of THIS convention, not universal truths. If your game violates them, the convention does not fit.

### Mutable state with explicit locking

Logic services own mutable state (`board.place()` mutates, `wallet.balance += amount`). The Orchestrator uses a `locked` flag to prevent re-entry while an awaited hook is animating.

If the game requires immutability for replay, undo, or time-rewind, prefer Redux/MVU-style architecture — this convention does not apply cleanly.

### Hook-style over return-style

Logic exposes hook fields instead of returning event descriptions for the shell to interpret. Trade-off:

- **Hook awaitable (this convention):** animation gating with `await` reads naturally; logic depends on externally-set hook fields, so unit tests stub hooks.
- **Return-style (FC/IS pure):** logic stays pure and easier to test; harder to gate animation natively.

Pick this convention when animation gating matters. For games without significant animation gating (auto-resolved flow, idle ticking), return-style FC/IS is simpler — do not force this convention onto it.

## Mental model — ports and adapters

If you already think in Hexagonal terms, this convention maps cleanly:

- Hook field on a logic class = **driven port** (logic exposes; UI plugs in).
- Public command method on a logic class = **driver port** (UI calls in).
- View binding the hook = **driven adapter**.
- Scene wiring pointer events to Orchestrator commands = **driver adapter**.

There is no formal `interface Port` declaration — the hook field type and the method signature are the port.
