---
name: app-state-casual-game
description: "Centralized persistent app state pattern for casual and puzzle games in Cocos Creator (TypeScript). Use this skill whenever Claude helps with: (1) Designing state management for casual/puzzle games, (2) Separating persistent state from runtime/gameplay state, (3) Implementing save/load without coupling to individual systems, (4) Sharing state across systems like booster, shop, daily quest, progression, (5) Migrating from per-system internal state to a shared AppState, (6) Schema versioning when AppState changes between game updates. Trigger on: 'save load game state', 'shared state between systems', 'app state', 'per-system state', 'state management game', 'booster shop quest state', 'how to save game', 'serialize state'. Also trigger when a system class defines its own coins/boosters/progress fields that overlap with other systems, or when save/load requires touching multiple system classes."
---

# Centralized App State for Casual / Puzzle Games

Separate **persistent state** from **runtime state**. Persistent state lives in one plain object (`AppState`) shared across all systems. Runtime state lives inside each system as before.

## The Core Problem

When each system owns its own state, save/load must know the internals of every system:

```typescript
// ❌ Per-system state — save must interview every system
const save = {
    boosters: boosterManager.getInventory(),
    coins:    shopSystem.getCoins(),
    quests:   questSystem.getProgress(),
    level:    progressSystem.getCurrentLevel(),
};

// Load must inject back into every system
boosterManager.setInventory(save.boosters);
shopSystem.setCoins(save.coins);
// ... add one system → update save AND load
```

## The Solution: One AppState Object

```
Persistent state  →  AppState (plain data, shared, serializable, needs saving)
Runtime state     →  inside each system (gameplay only, not saved)
```

```typescript
// AppState = plain data class, no logic, no methods except defaults
class AppState {
    // Schema version — increment when structure changes
    readonly schemaVersion: number = 1;

    // Player resources
    coins: number = 0;
    gems: number = 0;

    // Boosters
    boosters: BoosterInventory = { hint: 3, bomb: 1, rocket: 1, shuffle: 2, magic: 0 };

    // Level progression
    highestUnlockedLevel: number = 1;
    levelResults: Record<number, LevelSaveData> = {};

    // Daily quest
    dailyQuest: DailyQuestSaveData = { date: '', tasks: [] };

    // Settings
    settings: SettingsData = { sfx: true, music: true, language: 'vi' };
}
```

## Systems Receive AppState via Constructor

Systems read and write directly to `AppState`. They do not define their own copy of persistent fields.

```typescript
class BoosterManager {
    constructor(private appState: AppState) {}

    getInventory(): Readonly<BoosterInventory> {
        return this.appState.boosters;
    }

    hasBooster(type: BoosterType): boolean {
        return this.appState.boosters[type] > 0;
    }

    // Writes directly to AppState — no internal copy
    spendBooster(type: BoosterType): boolean {
        if (!this.hasBooster(type)) return false;
        this.appState.boosters[type]--;
        return true;
    }

    addBooster(type: BoosterType, amount: number): void {
        this.appState.boosters[type] += amount;
    }
}

class ShopSystem {
    constructor(private appState: AppState) {}

    canAfford(price: number): boolean {
        return this.appState.coins >= price;
    }

    purchase(item: ShopItem): boolean {
        if (!this.canAfford(item.price)) return false;
        this.appState.coins -= item.price;
        this.appState.boosters[item.boosterType]++;
        return true;
    }
}

class DailyQuestSystem {
    constructor(private appState: AppState) {}

    recordMatch(): void {
        const task = this.appState.dailyQuest.tasks
            .find(t => t.type === 'match' && t.current < t.target);
        if (task) task.current++;
    }

    isComplete(): boolean {
        return this.appState.dailyQuest.tasks.every(t => t.current >= t.target);
    }
}
```

## Save / Load — Trivial

Save serializes one object. Load deserializes and merges with defaults.

```typescript
class SaveSystem {
    private static readonly SAVE_KEY = 'app_state_v1';

    save(state: AppState): void {
        LocalStorage.set(SaveSystem.SAVE_KEY, JSON.stringify(state));
    }

    load(): AppState {
        const raw = LocalStorage.get(SaveSystem.SAVE_KEY);
        if (!raw) return new AppState();

        const parsed = JSON.parse(raw);
        return this.migrate(parsed);
    }

    private migrate(raw: any): AppState {
        const current = new AppState();
        const version = raw.schemaVersion ?? 0;

        if (version < 1) {
            // v0 → v1: boosters moved from flat fields to inventory object
            raw.boosters = {
                hint:    raw.hintCount    ?? 3,
                bomb:    raw.bombCount    ?? 1,
                rocket:  raw.rocketCount  ?? 1,
                shuffle: raw.shuffleCount ?? 2,
                magic:   0,
            };
        }

        // Merge saved data onto fresh defaults
        // Fresh defaults fill in any new fields added since player's last save
        return Object.assign(current, raw, { schemaVersion: current.schemaVersion });
    }
}
```

## Schema Versioning

Increment `schemaVersion` whenever `AppState` structure changes. Add a migration block in `SaveSystem.migrate()` for each version step.

```typescript
// When adding a new field → just add it with a default value
// Object.assign(current, raw) will use raw's value if present,
// or fall back to current's default if the field didn't exist in the old save.
// No migration needed for additive changes.

// When renaming or restructuring a field → add a migration block:
if (version < 2) {
    // v1 → v2: dailyQuest.tasks restructured
    raw.dailyQuest = convertOldQuestFormat(raw.dailyQuest);
}

// When removing a field → just remove it from AppState.
// Old saves will carry the dead field but Object.assign ignores it.
// No migration needed for removals.
```

**Rule of thumb:**
- Adding field → no migration needed, just set a default
- Renaming / restructuring → add migration block, bump version
- Removing field → no migration needed

## Wiring in the App Entry Point

```typescript
class GameApp extends Component {
    private appState: AppState;
    private saveSystem  = new SaveSystem();
    private boosterManager: BoosterManager;
    private shopSystem: ShopSystem;
    private dailyQuest: DailyQuestSystem;

    onLoad(): void {
        // Load once on boot
        this.appState = this.saveSystem.load();

        // All systems share the same AppState object
        this.boosterManager = new BoosterManager(this.appState);
        this.shopSystem     = new ShopSystem(this.appState);
        this.dailyQuest     = new DailyQuestSystem(this.appState);
    }

    // Save at meaningful moments — not every frame
    private persist(): void {
        this.saveSystem.save(this.appState);
    }

    onLevelComplete(result: LevelResult): void {
        // AppState already mutated by systems during gameplay
        this.persist();
    }

    onPurchaseComplete(): void {
        this.persist();
    }
}
```

## Persistent vs Runtime — Decision Guide

| Field | Persistent (AppState) | Runtime (system) |
|---|---|---|
| Coins, gems | ✅ | |
| Booster inventory | ✅ | |
| Level stars / high score | ✅ | |
| Daily quest progress | ✅ | |
| Settings | ✅ | |
| Current board tiles | | ✅ |
| Timer remaining | | ✅ |
| Current combo count | | ✅ |
| Selected tile in Matcher | | ✅ |
| Animation state | | ✅ |

**Rule:** "Would this data matter to the player if they close and reopen the app?" → Yes = persistent. No = runtime.

## Self-Check

- [ ] Does any system define `coins`, `boosters`, or `progress` as its own internal field? → move to AppState
- [ ] Does save/load call into more than one system? → those systems should read from AppState instead
- [ ] Does load require injecting data back into systems? → systems should read AppState directly
- [ ] Did AppState structure change without bumping `schemaVersion`? → old saves may corrupt
- [ ] Is runtime state (timer, board, selected tile) in AppState? → remove it, keep AppState serializable

## Reference Files

- `references/app-state-template.md` — Full AppState template for Onet / casual puzzle games
- `references/common-mistakes.md` — Common mistakes and how to fix them