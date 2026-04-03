# Common Entity Lifecycle Templates

Template hooks for common game entity types. Copy and adjust for your specific game.

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
    // --- Lifecycle hooks: ~7 ---
    onEnterBattle?: () => void;
    onTurnStart?: () => Promise<void>;       // await ready anim
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onHealed?: (data: { result: HealResult }) => void;
    onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
    onDeath?: () => Promise<void>;           // await death anim
}
```

**Why is `onHealed` void but `onTakeDamage` is Promise?**
Healing usually does not block gameplay flow — it can animate in the background.
Damage typically needs to wait for hurt animation (especially with knockback or death checks).

---

## Card

Card game (TCG, deckbuilder, poker-style).

```typescript
class Card {
    // --- Lifecycle hooks: ~6 ---
    onDrawn?: () => Promise<void>;           // await draw animation
    onPlayed?: (data: { target?: Card | Slot }) => Promise<void>;
    onDiscarded?: () => Promise<void>;
    onRevealed?: () => void;                 // flip card, fire-and-forget
    onEffectApplied?: (data: { effect: CardEffect }) => Promise<void>;
    onDestroyed?: () => Promise<void>;       // remove from field anim

    async play(target?: Card | Slot) {
        this.applyManaCost();
        await this.onPlayed?.({ target });   // view animates card moving to field
        await this.applyEffect(target);      // logic applies effect, may trigger target hooks
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
            this.flipCard();  // tween flip, no need to await
        };
    }
}
```

---

## Tower

Tower defense.

```typescript
class Tower {
    // --- Lifecycle hooks: ~5 ---
    onPlaced?: (data: { position: Vec2 }) => Promise<void>;
    onAttack?: (data: { target: Enemy; damage: number }) => void;
    onUpgraded?: (data: { fromLevel: number; toLevel: number }) => Promise<void>;
    onSold?: () => Promise<void>;
    onAbilityActivated?: (data: { abilityId: string }) => Promise<void>;

    attack(target: Enemy) {
        const damage = this.calculateDamage(target);
        this.onAttack?.({ target, damage });  // view fires projectile — fire-and-forget
        // No await because tower attacks continuously; waiting for each projectile would stall the game
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

**Note:** `onAttack` is fire-and-forget because tower fires continuously.
If it waited for each projectile to land before firing the next → game would be very sluggish.
But `onUpgraded` does await because upgrade is a discrete action that deserves clear visual feedback.

---

## Piece

Board game, puzzle, match-3.

```typescript
class Piece {
    // --- Lifecycle hooks: ~5 ---
    onMoved?: (data: { from: GridPos; to: GridPos }) => Promise<void>;
    onMatched?: (data: { matchGroup: Piece[] }) => Promise<void>;
    onSwapped?: (data: { other: Piece }) => Promise<void>;
    onSpawned?: (data: { position: GridPos }) => Promise<void>;
    onSpecialActivated?: (data: { type: SpecialType }) => Promise<void>;

    // Most hooks are Promise because puzzle games need clear sequencing:
    // swap → match check → destroy → gravity → spawn → check again
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

        // 2. Check for matches
        const matches = this.findMatches();
        if (matches.length === 0) {
            // No match — swap back
            await Promise.all([
                a.onSwapped?.({ other: b }),
                b.onSwapped?.({ other: a }),
            ]);
            return;
        }

        // 3. Destroy matched pieces (parallel — all explode simultaneously)
        await Promise.all(
            matches.flat().map(p =>
                p.onMatched?.({ matchGroup: matches.find(g => g.includes(p))! })
            )
        );

        // 4. Gravity — pieces fall down (staggered but parallel)
        const moved = this.applyGravity();
        for (const { piece, from, to } of moved) {
            // Fire without awaiting each one — let them fall simultaneously with stagger
            piece.onMoved?.({ from, to });
        }
        await this.waitForAllAnimations();  // wait for all to finish falling

        // 5. Spawn new pieces
        const spawned = this.spawnNewPieces();
        await Promise.all(spawned.map(p => p.onSpawned?.({ position: p.position })));

        // 6. Cascade — check for new matches
        await this.tryResolveMatches();
    }
}
```

---

## Room / Level

Dungeon crawler, roguelike.

```typescript
class Room {
    // --- Lifecycle hooks: ~5 ---
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

When an item has a visual representation (not just data in a list).

```typescript
class InventoryItem {
    // --- Lifecycle hooks: ~4 ---
    onAcquired?: (data: { source: 'loot' | 'shop' | 'craft' }) => void;
    onEquipped?: (data: { slot: EquipSlot }) => void;
    onUsed?: (data: { target: BattleUnit }) => Promise<void>;
    onDropped?: () => void;

    async use(target: BattleUnit) {
        if (!this.isUsable()) return;
        const effect = this.calculateEffect(target);
        await this.onUsed?.({ target });     // view plays potion splash, etc.
        target.applyEffect(effect);          // logic applies after view performs
        this.consume();
    }
}
```

---

## General Guidelines Across All Entities

1. **Aim for 4-8 hooks per entity.** Fewer than 4 may be too coarse; more than 10 is likely too granular.

2. **Naming convention:** `on` + verb (past participle or present).
   - Past: `onDamaged`, `onHealed`, `onDestroyed` — it already happened, view shows the aftermath
   - Present: `onAttack`, `onMove` — it is happening, view shows the action

3. **Promise rule of thumb:**
   - Sequential gameplay (turn-based, puzzle cascade): most hooks are `Promise<void>`
   - Realtime gameplay (tower defense, action): most hooks are `void` (fire-and-forget)
   - Hybrid: actions are `void`, milestones are `Promise` (upgrade, level clear)

4. **Data objects (Result types) should be immutable.** View must not modify results.
   Use `ReadonlyArray`, `Readonly<T>`, or `Object.freeze()` if enforcement is needed.

5. **Single callback vs LifecycleHook:** if the entity can belong to a composite structure
   (team, deck, formation, wave), start with `LifecycleHook` to avoid refactoring when
   you later need multiple listeners. For standalone entities, single callback is fine.