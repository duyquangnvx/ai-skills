# AppState Template — Casual / Puzzle Game (Onet)

Full template covering the most common features in a casual puzzle game. Remove sections that don't apply to your project.

```typescript
// ── Supporting types ──────────────────────────────────────────────────────────

export interface BoosterInventory {
    hint:    number;
    bomb:    number;
    rocket:  number;
    shuffle: number;
    magic:   number;
}

export interface LevelSaveData {
    stars:     1 | 2 | 3;
    bestScore: number;
    bestTime:  number;   // seconds
}

export interface QuestTask {
    id:      string;
    type:    'match' | 'use_booster' | 'complete_level' | 'earn_stars';
    target:  number;
    current: number;
}

export interface DailyQuestSaveData {
    date:      string;   // ISO date string 'YYYY-MM-DD'
    tasks:     QuestTask[];
    claimed:   boolean;
    reward:    { coins: number; boosters: Partial<BoosterInventory> };
}

export interface SettingsData {
    sfxEnabled:   boolean;
    musicEnabled: boolean;
    language:     string;
    notifications: boolean;
}

export interface ShopPurchaseRecord {
    itemId:      string;
    purchasedAt: string;   // ISO timestamp
}

// ── AppState ──────────────────────────────────────────────────────────────────

export class AppState {
    // Bump this whenever AppState structure changes in a breaking way
    readonly schemaVersion: number = 1;

    // ── Resources ──
    coins: number = 0;
    gems:  number = 0;

    // ── Boosters ──
    boosters: BoosterInventory = {
        hint:    3,
        bomb:    1,
        rocket:  1,
        shuffle: 2,
        magic:   0,
    };

    // ── Level Progression ──
    highestUnlockedLevel: number = 1;
    levelResults: Record<number, LevelSaveData> = {};

    // ── Daily Quest ──
    dailyQuest: DailyQuestSaveData = {
        date:    '',
        tasks:   [],
        claimed: false,
        reward:  { coins: 0 },
    };

    // ── Shop ──
    purchaseHistory: ShopPurchaseRecord[] = [];

    // ── Settings ──
    settings: SettingsData = {
        sfxEnabled:    true,
        musicEnabled:  true,
        language:      'vi',
        notifications: true,
    };

    // ── Meta ──
    firstInstallDate: string = '';    // ISO timestamp, set on first boot
    totalPlaySeconds: number = 0;
    lastSessionDate:  string = '';    // ISO date, for daily quest reset
}
```

---

## SaveSystem with Full Migration Support

```typescript
export class SaveSystem {
    private static readonly KEY = 'onet_app_state';

    save(state: AppState): void {
        try {
            LocalStorage.set(SaveSystem.KEY, JSON.stringify(state));
        } catch (e) {
            console.error('[SaveSystem] Failed to save:', e);
        }
    }

    load(): AppState {
        try {
            const raw = LocalStorage.get(SaveSystem.KEY);
            if (!raw) return this.createFresh();
            return this.migrate(JSON.parse(raw));
        } catch (e) {
            console.error('[SaveSystem] Failed to load, using fresh state:', e);
            return this.createFresh();
        }
    }

    private createFresh(): AppState {
        const state = new AppState();
        state.firstInstallDate = new Date().toISOString();
        state.lastSessionDate  = new Date().toISOString().slice(0, 10);
        return state;
    }

    private migrate(raw: any): AppState {
        const defaults = new AppState();
        const version  = raw.schemaVersion ?? 0;

        // ── v0 → v1 ──────────────────────────────────────────────
        if (version < 1) {
            // Boosters were flat fields in v0
            if (raw.hintCount !== undefined) {
                raw.boosters = {
                    hint:    raw.hintCount    ?? defaults.boosters.hint,
                    bomb:    raw.bombCount    ?? defaults.boosters.bomb,
                    rocket:  raw.rocketCount  ?? defaults.boosters.rocket,
                    shuffle: raw.shuffleCount ?? defaults.boosters.shuffle,
                    magic:   0,
                };
                delete raw.hintCount;
                delete raw.bombCount;
                delete raw.rocketCount;
                delete raw.shuffleCount;
            }
        }

        // ── Add future migrations here ────────────────────────────
        // if (version < 2) { ... }

        // Merge: raw data on top of fresh defaults
        // New fields added to AppState get their default values automatically
        // Removed fields are dropped silently
        const merged = Object.assign(defaults, raw);
        merged.schemaVersion = defaults.schemaVersion;
        return merged;
    }
}
```

---

## Daily Quest Reset Helper

```typescript
export class DailyQuestSystem {
    constructor(private appState: AppState) {}

    checkAndReset(): void {
        const today = new Date().toISOString().slice(0, 10);
        if (this.appState.dailyQuest.date !== today) {
            this.appState.dailyQuest = {
                date:    today,
                tasks:   this.generateTasks(),
                claimed: false,
                reward:  { coins: 100, boosters: { hint: 1 } },
            };
        }
    }

    private generateTasks(): QuestTask[] {
        return [
            { id: 'match_30',    type: 'match',          target: 30, current: 0 },
            { id: 'booster_x1',  type: 'use_booster',    target: 1,  current: 0 },
            { id: 'level_3',     type: 'complete_level',  target: 3,  current: 0 },
        ];
    }

    claimReward(): boolean {
        const quest = this.appState.dailyQuest;
        if (quest.claimed) return false;
        if (!quest.tasks.every(t => t.current >= t.target)) return false;

        quest.claimed = true;
        this.appState.coins += quest.reward.coins ?? 0;
        for (const [type, amount] of Object.entries(quest.reward.boosters ?? {})) {
            this.appState.boosters[type as BoosterType] += amount ?? 0;
        }
        return true;
    }
}
```