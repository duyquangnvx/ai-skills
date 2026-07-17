---
name: minigame-architecture
description: "Overview architecture for offline casual/puzzle minigames (Onet, match-3, card, board games). Use this skill whenever Claude helps with: (1) Designing the overall structure of a new minigame, (2) Deciding how to organize logic, view, state, and persistence, (3) Understanding how components connect in a minigame codebase, (4) Reviewing or refactoring game architecture, (5) Choosing where new features belong in the architecture. Trigger on: 'game architecture', 'minigame structure', 'how to organize game code', 'logic vs view', 'game singleton', 'wire logic to view', 'where does this feature go'. Also trigger when the user starts a new minigame project or asks about the relationship between game systems."
---

# Minigame Architecture Overview

Architecture for offline casual/puzzle minigames. Six components, strict separation in one direction, pragmatic in the other.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     Game (singleton)                      │
│                                                          │
│  ┌──────────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Orchestrator(s)  │  │  GameState   │  │    Store    │ │
│  │                   │  │  (shared     │  │  (persist)  │ │
│  │  ┌─────────────┐  │  │   data)      │  │             │ │
│  │  │Logic Systems│  │  │             │  │             │ │
│  │  └─────────────┘  │  └─────────────┘  └─────────────┘ │
│  └──────────────────┘                                    │
│           │                                               │
│           │  Game wires orchestrator hooks to view         │
└───────────│──────────────────────────────────────────────┘
            │                        ▲
            │  delegate callbacks     │  Game.instance.*
            ▼                        │
┌──────────────────────────────────────────────────────────┐
│                          View                             │
│                                                          │
│  Scenes, UI, Animation, Sound, Effects                   │
│                                                          │
│  - Nhận delegate callbacks    (logic → view)             │
│  - Gọi Game.instance.*        (view → logic)             │
│  - Đọc GameState trực tiếp    (render UI state)          │
└──────────────────────────────────────────────────────────┘
```

## The Six Components

### 1. Game

Main class, singleton. Creates all other components and wires them together. The single point where logic meets view.

```typescript
class Game {
    static instance: Game;

    orchestrator: GameSession;
    meta: MetaOrchestrator;
    gameState: GameState;
    store: SaveSystem;

    init(): void {
        this.gameState = this.store.load();
        this.orchestrator = new GameSession({ gameState: this.gameState });
        this.meta = new MetaOrchestrator({ gameState: this.gameState });

        // Wire hooks to view — this is the ONLY place logic connects to view
        this.wireHooks();
    }

    private wireHooks(): void {
        this.orchestrator.onMatchSuccess = async (data) => {
            // View handles animation, sound, UI update
        };
        this.orchestrator.onLevelWon = async (data) => {
            this.meta.finishLevel(data.levelId, data.stars, data.score);
            this.store.save(this.gameState);
            // View handles victory screen
        };
    }
}
```

**Responsibilities:**
- Create orchestrators, state, store, view
- Wire orchestrator hooks to view (delegate callbacks)
- Expose actions that View calls directly (`selectTile()`, `useBooster()`, `pause()`)
- Persist state at meaningful moments (level complete, purchase)

### 2. Orchestrator

Coordinates gameplay flow. Owns lifecycle hooks. Calls logic systems in sequence and awaits animation before continuing.

```typescript
class GameSession {
    // Lifecycle hooks — one per gameplay "moment"
    onMatchSuccess?: (data: { tiles, path, combo, score }) => Promise<void>;
    onMatchFail?:    (data: { tiles }) => Promise<void>;
    onLevelWon?:     (data: { stars, score }) => Promise<void>;
    onLevelLost?:    (data: { reason }) => Promise<void>;

    async selectTile(row: number, col: number): Promise<void> {
        // 1. Logic systems compute result
        const result = this.matchValidator.findPath(a, b, grid);

        // 2. Fire hook — view animates, orchestrator waits
        await this.onMatchSuccess?.({ tiles, path, combo, score });

        // 3. Continue game flow after animation
        this.checkBoardState();
    }
}
```

A game typically has one gameplay orchestrator (`GameSession`) and one meta orchestrator (`MetaOrchestrator`). Complex games may split further by domain.

For detailed patterns on orchestrators, hooks, and sequencing, read the **lifecycle-delegate** skill.

### 3. Logic Systems

Pure data + rules. No engine dependencies. No hooks. Return result objects.

```typescript
class Board {
    removePair(a: TileData, b: TileData): void { /* mutate grid */ }
    countTiles(): number { /* pure computation */ }
}

class ScoreKeeper {
    addMatchScore(distance: number): ScoreResult {
        // Calculate, return result — no side effects outside this system
        return { points, total, starRating };
    }
}
```

Logic systems receive `GameState` via constructor for persistent data access. Runtime state (board grid, timer remaining) lives inside each system.

### 4. GameState

Plain data object holding all persistent state. Shared across systems via dependency injection.

```typescript
class GameState {
    readonly schemaVersion: number = 1;
    coins: number = 0;
    boosters: BoosterInventory = { hint: 3, shuffle: 2 };
    highestUnlockedLevel: number = 1;
    levelResults: Record<number, LevelSaveData> = {};
    settings: SettingsData = { sfx: true, music: true };
}
```

Systems read and write directly — no getters/setters, no event dispatch on change. View reads directly for rendering.

For detailed patterns on GameState, save/load, and schema migration, read the **app-state-casual-game** skill.

### 5. Store

Serializes and deserializes GameState. Handles schema versioning and migration.

```typescript
class SaveSystem {
    save(state: GameState): void {
        localStorage.set('save', JSON.stringify(state));
    }
    load(): GameState {
        const raw = localStorage.get('save');
        return raw ? this.migrate(JSON.parse(raw)) : new GameState();
    }
}
```

Game calls `store.save()` at meaningful moments — level complete, purchase, settings change. Not every frame.

### 6. View

Everything the player sees and hears. Scenes, UI, sprites, animations, particles, sound.

View has two communication channels:

**Receiving from logic (passive):** Game wires orchestrator hooks to view methods. View doesn't know about orchestrators — it just receives calls.

**Calling into logic (active):** View accesses `Game.instance` directly. No abstraction layer, no input interfaces.

```typescript
// In a scene or UI component:
onTileTapped(row: number, col: number): void {
    Game.instance.selectTile(row, col);
}

renderCoins(): void {
    this.label.text = Game.instance.gameState.coins.toString();
}
```

This is a pragmatic choice: View is inherently engine-coupled and tested visually, not via unit tests. Adding abstraction between View and Game creates boilerplate without testability benefit.

## Data Flow

Two directions, asymmetric by design:

```
Logic → View:   Orchestrator.onX()  →  Game wires  →  View receives call
                (delegate pattern — logic never imports or references view)

View → Logic:   View  →  Game.instance.action()
                (direct access — pragmatic, no abstraction)

View reads:     Game.instance.gameState.*
                (direct read for rendering coins, inventory, progress...)
```

The delegate pattern protects only the direction that matters: **logic must not depend on view**, so logic can be tested headless without any engine. The reverse direction doesn't need protection because view is never tested independently.

## Async Hooks — Logic Waits for Animation

Hooks that return `Promise<void>` let the orchestrator pause until animation completes:

```typescript
// Orchestrator sequences: logic → await animation → continue logic
const result = board.removePair(a, b);
await this.onMatchSuccess?.({ tiles, path, score });  // view animates
this.checkBoardState();                                // continues after animation
```

| Situation | Hook return type | Reason |
|---|---|---|
| Logic must wait for animation | `Promise<void>` | Next step depends on animation finishing |
| Visual feedback only, logic continues | `void` | No ordering dependency |
| View must return a choice to logic | `Promise<T>` | e.g., player picks a target |

Guard against ticks during async: when a hook fires and awaits, continuous systems (`tick(dt)`) keep running. Set a phase/state flag before the await to prevent conflicting actions.

## Persistent vs Runtime State

| Ask yourself | → | Where it goes |
|---|---|---|
| Player closes app and reopens — does this data matter? | Yes | GameState (persistent) |
| | No | Inside the system (runtime) |

| Persistent (GameState) | Runtime (inside systems) |
|---|---|
| Coins, gems | Current board tiles |
| Booster inventory | Timer remaining |
| Level stars / high score | Selected tile |
| Settings | Combo count |
| Daily quest progress | Animation state |
| Unlocked content | Game phase |

## Extension Points

**EventBus for cross-cutting concerns.** When analytics, achievements, or quest trackers need to listen to events from multiple orchestrators, add an EventBus. Orchestrator fires hooks first (for view), then emits to EventBus (for cross-cutting systems). Logic systems never emit to EventBus directly.

**Multiple Orchestrators.** Most minigames need two: gameplay (`GameSession`) and meta-game (`MetaOrchestrator`). Larger games may add more by domain — never share hooks across orchestrators.

**Action log for debugging.** A lightweight array of `{ type, payload, timestamp }` in the orchestrator helps debug "how did the game get into this state" without full event sourcing.

## Self-Check

- [ ] Can logic systems run without any engine import? → if not, extract engine deps to view
- [ ] Do logic systems fire hooks or events directly? → move hooks to orchestrator
- [ ] Does View import or reference orchestrator types? → route through Game instead
- [ ] Is runtime state stored in GameState? → move to the owning system
- [ ] Is persistent state stored inside a system? → move to GameState
- [ ] Does save/load touch more than one system? → systems should read GameState directly
- [ ] Does adding a View feature require changing logic? → separation is leaking
- [ ] Are hooks firing every frame or on data change? → not lifecycle moments, use getters instead

## Related Skills

- **lifecycle-delegate** — detailed patterns for orchestrator hooks, callback granularity, async sequencing, and hook placement rules
- **app-state-casual-game** — detailed patterns for GameState structure, save/load, schema versioning, and migration

## Reference Files

- `references/common-variations.md` — variations by game complexity, singleton trade-offs, source code folder conventions
