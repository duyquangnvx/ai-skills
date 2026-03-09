# Common Entity Lifecycle Templates

Template hooks cho các entity type thường gặp. Copy và điều chỉnh theo game cụ thể.

## Table of Contents

1. [BattleUnit (RPG/Turn-based)](#battleunit)
2. [Card (Card Game)](#card)
3. [Tower (Tower Defense)](#tower)
4. [Piece (Board Game / Puzzle)](#piece)
5. [Room / Level (Dungeon / Roguelike)](#room)
6. [Inventory Item](#inventory-item)

---

## BattleUnit

RPG, turn-based, auto-battler.

```typescript
class BattleUnit {
    // --- Lifecycle hooks: ~7 cái ---
    onEnterBattle?: () => void;
    onTurnStart?: () => Promise<void>;       // await ready anim
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onHealed?: (data: { result: HealResult }) => void;
    onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
    onDeath?: () => Promise<void>;           // await death anim
}
```

**Tại sao `onHealed` là void nhưng `onTakeDamage` là Promise?**
Heal thường không block gameplay flow — diễn nền được.
Damage thường cần chờ hurt anim (đặc biệt khi kèm knockback, death check).

---

## Card

Card game (TCG, deckbuilder, poker-style).

```typescript
class Card {
    // --- Lifecycle hooks: ~6 cái ---
    onDrawn?: () => Promise<void>;           // await draw animation
    onPlayed?: (data: { target?: Card | Slot }) => Promise<void>;
    onDiscarded?: () => Promise<void>;
    onRevealed?: () => void;                 // flip card, fire-and-forget
    onEffectApplied?: (data: { effect: CardEffect }) => Promise<void>;
    onDestroyed?: () => Promise<void>;       // remove from field anim

    play(target?: Card | Slot) {
        this.applyManaCost();
        await this.onPlayed?.({ target });   // view diễn card bay ra field
        await this.applyEffect(target);      // logic apply, có thể trigger target hooks
    }
}
```

**View example:**

```typescript
class CardView extends Component {
    bind(card: Card) {
        card.onDrawn = async () => {
            await this.animateFromDeckToHand();
        };

        card.onPlayed = async ({ target }) => {
            await this.animateFromHandToField(target);
            await this.playGlowEffect();
        };

        card.onDiscarded = async () => {
            await this.animateToGraveyard();
        };

        card.onRevealed = () => {
            this.flipCard();  // tween flip, không cần await
        };
    }
}
```

---

## Tower

Tower defense.

```typescript
class Tower {
    // --- Lifecycle hooks: ~5 cái ---
    onPlaced?: (data: { position: Vec2 }) => Promise<void>;
    onAttack?: (data: { target: Enemy; damage: number }) => void;
    onUpgraded?: (data: { fromLevel: number; toLevel: number }) => Promise<void>;
    onSold?: () => Promise<void>;
    onAbilityActivated?: (data: { abilityId: string }) => Promise<void>;

    attack(target: Enemy) {
        const damage = this.calculateDamage(target);
        this.onAttack?.({ target, damage });  // view bắn projectile — fire-and-forget
        // Không await vì tower attack liên tục, không chờ từng viên đạn
        target.receiveDamage(damage, this);
    }

    async upgrade() {
        if (!this.canUpgrade()) return;
        const from = this.level;
        this.level++;
        this.recalcStats();
        await this.onUpgraded?.({ fromLevel: from, toLevel: this.level });  // await upgrade anim
    }
}
```

**Lưu ý:** `onAttack` là fire-and-forget vì tower bắn liên tục.
Nếu chờ mỗi projectile bay xong mới bắn tiếp → game rất chậm.
Nhưng `onUpgraded` thì await vì upgrade là action rời rạc, cần diễn rõ.

---

## Piece

Board game, puzzle, match-3.

```typescript
class Piece {
    // --- Lifecycle hooks: ~5 cái ---
    onMoved?: (data: { from: GridPos; to: GridPos }) => Promise<void>;
    onMatched?: (data: { matchGroup: Piece[] }) => Promise<void>;
    onSwapped?: (data: { other: Piece }) => Promise<void>;
    onSpawned?: (data: { position: GridPos }) => Promise<void>;
    onSpecialActivated?: (data: { type: SpecialType }) => Promise<void>;

    // Hầu hết cần await vì puzzle game cần sequence rõ ràng:
    // swap → match check → destroy → gravity → spawn → match check lại
}
```

**Puzzle flow example:**

```typescript
class PuzzleBoard {
    async trySwap(a: Piece, b: Piece) {
        // 1. Swap animation
        await Promise.all([
            a.onSwapped?.({ other: b }),
            b.onSwapped?.({ other: a }),
        ]);

        // 2. Check match
        const matches = this.findMatches();
        if (matches.length === 0) {
            // Swap back
            await Promise.all([
                a.onSwapped?.({ other: b }),
                b.onSwapped?.({ other: a }),
            ]);
            return;
        }

        // 3. Destroy matched pieces (song song — tất cả nổ cùng lúc)
        await Promise.all(
            matches.flat().map(p =>
                p.onMatched?.({ matchGroup: matches.find(g => g.includes(p)) })
            )
        );

        // 4. Gravity — rơi xuống (tuần tự từ dưới lên)
        const moved = this.applyGravity();
        for (const { piece, from, to } of moved) {
            // Không await từng cái — cho rơi cùng lúc nhưng stagger
            piece.onMoved?.({ from, to });
        }
        await this.waitForAllAnimations();  // chờ tất cả rơi xong

        // 5. Spawn mới
        const spawned = this.spawnNewPieces();
        await Promise.all(spawned.map(p => p.onSpawned?.({ position: p.position })));

        // 6. Cascade — check match lại
        await this.tryResolveMatches();
    }
}
```

---

## Room / Level

Dungeon crawler, roguelike.

```typescript
class Room {
    // --- Lifecycle hooks: ~5 cái ---
    onEntered?: (data: { from: Direction }) => Promise<void>;
    onCleared?: () => Promise<void>;
    onTreasureOpened?: (data: { loot: Item[] }) => Promise<void>;
    onTrapTriggered?: (data: { trap: TrapData }) => Promise<void>;
    onExited?: (data: { to: Direction }) => void;

    async enter(from: Direction) {
        this.isActive = true;
        this.spawnEnemies();
        await this.onEntered?.({ from });  // camera pan + fog reveal

        if (this.hasTrap && this.shouldTriggerTrap()) {
            await this.onTrapTriggered?.({ trap: this.trapData });
            this.applyTrapEffect();
        }
    }

    async clear() {
        this.isCleared = true;
        this.unlockDoors();
        if (this.treasure) {
            await this.onTreasureOpened?.({ loot: this.treasure });
        }
        await this.onCleared?.();
    }
}
```

---

## Inventory Item

Khi item có visual representation (không chỉ data).

```typescript
class InventoryItem {
    // --- Lifecycle hooks: ~4 cái ---
    onAcquired?: (data: { source: 'loot' | 'shop' | 'craft' }) => void;
    onEquipped?: (data: { slot: EquipSlot }) => void;
    onUsed?: (data: { target: BattleUnit }) => Promise<void>;
    onDropped?: () => void;

    async use(target: BattleUnit) {
        if (!this.isUsable()) return;
        const effect = this.calculateEffect(target);
        await this.onUsed?.({ target });   // view diễn potion splash, etc.
        target.applyEffect(effect);      // logic apply sau khi view diễn
        this.consume();
    }
}
```

---

## General Guidelines Across All Entities

1. **Số hooks nên ở khoảng 4-8 per entity.** Dưới 4 có thể quá thô, trên 10 có thể quá chi tiết.

2. **Naming convention:** `on` + verb (past participle hoặc present).
   - Past: `onDamaged`, `onHealed`, `onDestroyed` — đã xảy ra, view diễn hậu quả
   - Present: `onAttack`, `onMove` — đang xảy ra, view diễn action

3. **Promise rule of thumb:**
   - Sequential gameplay (turn-based, puzzle cascade): hầu hết hooks là `Promise<void>`
   - Realtime gameplay (tower defense, action): hầu hết hooks là `void` (fire-and-forget)
   - Hybrid: action là `void`, milestone là `Promise` (upgrade, level clear)

4. **Data objects (Result types) nên immutable.** View không được modify result —
   truyền `ReadonlyArray`, freeze objects nếu cần.
