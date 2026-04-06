# Common Orchestrator Templates

Templates for the most frequent game types in this project. Copy the relevant template and fill in the domain-specific logic.

---

## Battle Orchestrator

For turn-based or action RPG combat with units, skills, HP.

```typescript
class BattleOrchestrator {
    // Board setup
    onBoardCreated?: (data: {
        units: ReadonlyArray<BattleUnit>;
        enemies: ReadonlyArray<BattleUnit>;
    }) => void;

    // Combat moments
    onTurnStart?:   (data: { unit: BattleUnit }) => Promise<void>;
    onSkillCast?:   (data: { result: SkillCastResult }) => Promise<void>;
    onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
    onUnitHealed?:  (data: { unit: BattleUnit; result: HealResult }) => void;
    onBuffApplied?: (data: { unit: BattleUnit; buff: Buff }) => void;
    onUnitDied?:    (data: { unit: BattleUnit }) => Promise<void>;

    // Game flow
    onBattleWon?:  (data: { stars: number; score: number; elapsedSeconds: number }) => Promise<void>;
    onBattleLost?: (data: { reason: 'timeout' | 'wiped' }) => Promise<void>;
}
```

**Granularity note:** `onUnitDamaged` bundles the full `DamageResult` (value, isCrit, knockback, shield, remaining HP). Do not split into separate hooks per field.

---

## Puzzle / Board Orchestrator (e.g. Onet, Match-3)

For tile-based puzzle games where player selects tiles and the board responds.

```typescript
class PuzzleOrchestrator {
    // Setup
    onBoardCreated?: (data: {
        cols: number; rows: number;
        tiles: ReadonlyArray<Tile>;
        obstacles: ReadonlyArray<{ pos: GridPos; kind: string }>;
    }) => void;

    // Player input moments
    onTileSelected?:   (data: { tile: Tile }) => void;
    onTileDeselected?: (data: { tile: Tile }) => void;

    // Match outcomes
    onMatchSuccess?: (data: { result: MatchResult }) => Promise<void>;
    onMatchFailed?:  (data: { tile1: Tile; tile2: Tile; reason: 'mismatch' | 'no_path' }) => Promise<void>;
    onCoverBroken?:  (data: { tile: Tile; coverType: string; path: ConnectionPath }) => Promise<void>;

    // Board events
    onBoardShuffled?:   (data: { moves: ShuffleMove[]; reason: 'booster' | 'deadlock' }) => Promise<void>;
    onNoMovesDetected?: () => void;  // Only if no shuffle follows — otherwise merge into onBoardShuffled

    // Booster moments
    onBoosterUsed?: (data: { type: BoosterType; result: BoosterResult }) => Promise<void>;

    // Timer
    onTimerWarning?: (data: { remainingSeconds: number }) => void;

    // Game flow
    onGameWon?:  (data: { stars: number; score: number }) => Promise<void>;
    onGameLost?: (data: { reason: 'timeout' | 'unsolvable'; score: number }) => Promise<void>;
}
```

**What NOT to hook:** `onTimerUpdate` (fires every frame — view polls `getRemainingSeconds()` in its update loop instead). `onBoosterInventoryChanged` (view reads `getInventory()` after each action).

---

## Shop / Inventory Orchestrator

For item purchase, upgrade, equipment flows.

```typescript
class ShopOrchestrator {
    // Navigation
    onShopOpened?:  (data: { items: ReadonlyArray<ShopItem> }) => Promise<void>;
    onShopClosed?:  () => Promise<void>;
    onTabChanged?:  (data: { tab: ShopTab; items: ReadonlyArray<ShopItem> }) => void;

    // Purchase flow
    onPurchaseConfirmed?: (data: { item: ShopItem; result: PurchaseResult }) => Promise<void>;
    onPurchaseFailed?:    (data: { item: ShopItem; reason: 'insufficient_funds' | 'max_owned' }) => void;

    // Upgrade flow
    onUpgradeSuccess?: (data: { item: ShopItem; newLevel: number; result: UpgradeResult }) => Promise<void>;
    onUpgradeFailed?:  (data: { item: ShopItem; reason: string }) => void;
}
```

**What NOT to hook:** `onCurrencyChanged` (view reads `getCurrency()` after each transaction).

---

## Map / World Orchestrator

For overworld navigation, node unlocking, chapter progression.

```typescript
class MapOrchestrator {
    // Setup
    onMapLoaded?: (data: { nodes: ReadonlyArray<MapNode>; paths: ReadonlyArray<MapPath> }) => void;

    // Navigation
    onNodeSelected?:  (data: { node: MapNode }) => void;
    onNodeUnlocked?:  (data: { node: MapNode; unlockedBy: MapNode }) => Promise<void>;
    onChapterCleared?: (data: { chapter: number; stars: number }) => Promise<void>;

    // Travel
    onPlayerMoved?: (data: { from: MapNode; to: MapNode }) => Promise<void>;
}
```

---

## Naming Conventions

| Moment type | Naming | Async? |
|---|---|---|
| Setup / initial state | `onXCreated`, `onXLoaded` | Usually `void` |
| Player action result | `onXSelected`, `onXUsed` | Depends |
| State change with animation | `onXDamaged`, `onXDied`, `onXBroken` | `Promise<void>` |
| Game flow gate | `onGameWon`, `onGameLost`, `onLevelComplete` | `Promise<void>` |
| Pure visual feedback | `onCombo`, `onTimerWarning` | `void` |

---

## Multiple Orchestrators in One Scene

When a scene has multiple domains, each domain gets its own Orchestrator. They do not share hooks:

```typescript
class AdventureScene {
    private battleOrchestrator  = new BattleOrchestrator();
    private mapOrchestrator     = new MapOrchestrator();
    private shopOrchestrator    = new ShopOrchestrator();

    onLoad(): void {
        const battleView = this.battleNode.getComponent(BattleView);
        const mapView    = this.mapNode.getComponent(MapView);
        const shopView   = this.shopNode.getComponent(ShopView);

        battleView.bind(this.battleOrchestrator);
        mapView.bind(this.mapOrchestrator);
        shopView.bind(this.shopOrchestrator);
    }

    onDestroy(): void {
        this.battleNode.getComponent(BattleView)?.unbind();
        this.mapNode.getComponent(MapView)?.unbind();
        this.shopNode.getComponent(ShopView)?.unbind();
    }
}
```

Cross-domain communication (e.g., battle result → map unlocks a node) goes through EventBus, not through shared hooks.