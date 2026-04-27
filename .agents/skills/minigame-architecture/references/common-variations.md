# Common Variations

## By Game Complexity

### Simple (one screen, one mode)
Single orchestrator, no MetaOrchestrator. Game class is thin — just wire hooks and go.

```
Game
├── GameSession (only orchestrator)
├── GameState
├── Store
└── View (one scene)
```

Examples: Flappy Bird, 2048, simple card matching.

### Medium (multiple screens, progression)
Two orchestrators: gameplay + meta. Game class manages transitions between screens.

```
Game
├── GameSession       (gameplay flow)
├── MetaOrchestrator  (progression, shop, rewards)
├── GameState
├── Store
└── View (multiple scenes: menu, gameplay, shop, results)
```

Examples: Onet, match-3 with levels, puzzle games with meta-progression.

### Complex (multiple game modes, events, social)
Multiple orchestrators by domain. Consider adding an EventBus for cross-cutting concerns.

```
Game
├── GameSession        (gameplay)
├── MetaOrchestrator   (progression, rewards)
├── EventOrchestrator  (time-limited events)
├── SocialOrchestrator (leaderboard, friends)
├── GameState
├── Store
├── EventBus           (analytics, achievements)
└── View (many scenes)
```

At this scale, evaluate whether the architecture is still appropriate or if a more formal framework (ECS, state machine framework) would serve better.

## Singleton Trade-offs

### When singleton Game.instance is fine
- Small team (1-3 devs)
- Single game mode active at a time
- No need for parallel game instances (replay, preview)
- Minigame scope — not scaling to MMO or complex multiplayer

### When to avoid singleton
- Need to run two game instances (e.g., replay while playing)
- Large team where invisible dependencies cause integration pain
- Writing a reusable game engine/framework

### Middle ground: explicit passing
Pass Game reference into View components at construction instead of using `Game.instance`. Same convenience, but dependencies stay visible. Slightly more wiring code.

```typescript
// Instead of Game.instance inside View:
class BoardView {
    constructor(private game: Game) {}

    onTileTapped(row: number, col: number): void {
        this.game.selectTile(row, col);
    }
}
```

## Callbacks vs EventBus — When to Switch

| Situation | Use |
|---|---|
| One orchestrator, one view listener | Typed callbacks |
| Multiple listeners for same event | EventBus |
| Analytics / achievements / quest tracking | EventBus |
| View animation that logic must await | Typed callback with Promise |
| Fire-and-forget broadcast | EventBus |

Both can coexist: orchestrator fires callback (for view), then emits to EventBus (for cross-cutting).

```typescript
// In orchestrator method:
await this.onMatchSuccess?.(data);          // view animates
EventBus.emit('match_success', data);       // analytics, achievements
```

## Source Code Folder Conventions

A typical folder structure for the logic + state layers:

```
src/
├── logic/
│   ├── core/              # Gameplay systems (Board, Timer, ScoreKeeper...)
│   │   └── obstacles/     # Optional: sub-domain systems
│   ├── meta/              # Meta-game systems (Shop, Rewards, DailyQuest...)
│   ├── orchestrators/     # GameSession, MetaOrchestrator
│   ├── state/             # GameState, SaveSystem, GameSessionState
│   ├── data/              # Level configs, shop catalog, milestones
│   └── types.ts           # Shared type definitions
├── scenes/                # Engine-specific scene files
├── views/                 # UI components, animations, effects
├── GameApp.ts             # Game singleton, wiring
└── main.ts                # Entry point
```

The key constraint: everything under `logic/` must have zero engine imports. If a file needs engine types, it belongs in `scenes/` or `views/`.

## Hook Lifecycle Ordering

Wire hooks **before** calling any method that might trigger them:

```typescript
// ✅ Wire first, then load
this.orchestrator.onBoardReady = async (data) => { /* ... */ };
this.orchestrator.loadLevel(config);

// ❌ Load first — if loadLevel triggers onBoardReady synchronously, it's lost
this.orchestrator.loadLevel(config);
this.orchestrator.onBoardReady = async (data) => { /* ... */ };
```
