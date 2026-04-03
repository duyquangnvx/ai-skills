---
name: lifecycle-delegate
description: "Pattern for separating game logic from view/presentation using lifecycle callbacks. Use whenever Claude helps with: (1) Logic-view separation in game code, (2) Writing entities/models that run headless without views, (3) Callback hooks between gameplay logic and animation/UI, (4) Refactoring tightly-coupled code where logic and visuals are mixed, (5) Testable/reusable game logic across client/server, (6) Turn-based or sequential gameplay where logic must await animation, (7) Game architecture or MVC-like patterns. Trigger on: 'separate logic and view', 'game architecture', 'MVC for game', 'await animation', 'headless game logic', 'unit test game logic', 'callback pattern game', 'lifecycle hook'. Also trigger when reviewing code mixing gameplay calculations with cc.tween, spine animations, or UI updates in the same class. Even 'my game code is messy' or 'logic and view are tangled' should trigger this skill."
---

# Lifecycle Delegate Pattern for Game Development

Separate logic from view using lifecycle callbacks — logic defines "moments" in its lifecycle, view hooks in to perform them visually.

## Core Principle

```
Logic Layer (pure data + rules)      View Layer (visual + animation)
┌─────────────────────────┐          ┌─────────────────────────┐
│ BattleUnit              │          │ BattleUnitView          │
│                         │          │                         │
│  hp, atk, def, buffs    │          │  spine, hpBar, vfx      │
│  receiveDamage()        │──hook──→ │  playHurtAnim()         │
│  castSkill()            │──hook──→ │  playSkillAnim()        │
│  die()                  │──hook──→ │  playDeathAnim()        │
│                         │          │                         │
│  // Runs WITHOUT view   │          │  // Only presentation   │
│  // Testable, headless  │          │  // No gameplay logic   │
└─────────────────────────┘          └─────────────────────────┘
```

**Logic runs without view.** Callbacks are optional — `?.()` skips gracefully when undefined.
**View contains no gameplay logic.** View receives data and decides *how* to present it.
**Flow control via Promise.** Logic `await`s callbacks when it needs to wait for animation to finish.

## When to Apply

Use this pattern when:
- An entity has both gameplay logic and a visual representation
- Logic must wait for animation to finish before continuing (turn-based, skill sequences)
- Logic needs to run headless (server, unit tests, AI simulation)
- You want to swap the view without touching logic (2D → 3D, change art style)

Do NOT use for:
- Cross-system broadcast (entity dies → notify quest, analytics) → use Event Bus instead
- Pure UI with no gameplay logic (settings menu, lobby UI)
- Realtime physics-driven gameplay where logic and visuals cannot be cleanly separated

## Callback Granularity Rules

**Each callback = one gameplay "moment" that the view needs to perform.** Not every field change.

### ❌ Too granular — view must reassemble logic from fragments

```typescript
onHpChanged?: (hp: number) => void;
onShieldChanged?: (shield: number) => void;
onCritTriggered?: () => void;
onKnockback?: (dir: Vec3) => void;
onDamageNumberSpawn?: (val: number) => void;
```

Problem: view receives 5 separate callbacks for a SINGLE hit, must reassemble the sequence itself,
prone to race conditions, hard to tell which callbacks belong to the same "moment".

### ❌ Too coarse — view must diff full state

```typescript
onChanged?: (state: FullUnitState) => void;
```

Problem: fires for every change, view cannot tell whether to play hurt anim or buff anim,
must diff old vs new state every frame, expensive and error-prone.

### ✅ Right level — each callback is one gameplay "moment"

```typescript
onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
```

`DamageResult` contains full context (damage, crit, shield, knockback). View receives one object
and decides how to present it.

### Always wrap params in a data object

```typescript
// ❌ Positional params — adding a field breaks all bound callbacks
onTakeDamage?: (result: DamageResult) => Promise<void>;
// Later you need sourceSkillId → must change to:
onTakeDamage?: (result: DamageResult, sourceSkillId: string) => Promise<void>;
// → EVERY view binding this hook must update its signature

// ✅ Data object — adding a field breaks nothing
onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
// Later add a field:
onTakeDamage?: (data: { result: DamageResult; sourceSkillId?: string }) => Promise<void>;
// → Existing views keep working, only views that need the new field use it
```

Principle: **every callback takes exactly 1 argument: a data object**, even when there is currently
only 1 field. The wrapper cost is near-zero, but it saves significant refactoring later.

### Self-check checklist

- [ ] Does view have to listen to multiple callbacks and combine them to play one animation? → merge callbacks
- [ ] Does adding a small feature in logic require a new callback? → abstraction is leaking
- [ ] Does a callback just forward a single field change without gameplay meaning? → you're observing data, not lifecycle
- [ ] Does a complex entity have more than 10 hooks? → consider merging
- [ ] Does view have to diff full state to decide what to play? → split into moment-based callbacks

## Implementation Guide

### Step 1: Define Result Types

Bundle sufficient context into data objects. View receives one object and never needs to ask logic for more.

```typescript
// Each result type = one gameplay "moment"
interface DamageResult {
    value: number;
    isCrit: boolean;
    element: ElementType;
    shieldAbsorbed: number;
    remainingHp: number;
    maxHp: number;
    knockbackDir?: Vec3;
}

interface HealResult {
    value: number;
    overheal: number;
    remainingHp: number;
    maxHp: number;
    source: 'skill' | 'regen' | 'item';
}

interface SkillCastInfo {
    skillId: string;
    caster: BattleUnit;
    targets: BattleUnit[];
}
```

### Step 2: Define Lifecycle Hooks on Logic Entity

```typescript
class BattleUnit {
    // ~5-8 hooks for a complex entity
    onEnterBattle?: () => void;
    onTurnStart?: () => Promise<void>;
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onHealed?: (data: { result: HealResult }) => void;
    onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
    onDeath?: () => Promise<void>;

    // Logic methods invoke hooks at the right moment
    async receiveDamage(raw: number, element: ElementType, attacker: BattleUnit) {
        // ... calculate damage, shield, crit ...
        const result: DamageResult = { /* bundle everything here */ };

        this.hp = Math.max(0, this.hp - result.value);
        await this.onTakeDamage?.({ result });  // view performs, logic waits

        if (this.hp <= 0) {
            await this.onDeath?.();
            // No EventBus here — logic stays pure.
            // A centralized manager listens to onDeath and broadcasts events.
            // See references/advanced-patterns.md → Centralized Event Bridge.
        }
    }
}
```

### Step 3: View Binds to Hooks

```typescript
// Cocos Creator example
class BattleUnitView extends Component {
    private unit: BattleUnit;

    bind(unit: BattleUnit) {
        this.unit = unit;

        unit.onTakeDamage = async ({ result }) => {
            this.hpBar.animateTo(result.remainingHp, result.maxHp);
            this.spawnDamageNumber(result.value, result.isCrit);
            if (result.shieldAbsorbed > 0) this.playShieldBreakVFX();
            if (result.knockbackDir) {
                await this.playKnockback(result.knockbackDir);
            } else {
                await this.playSpineAndWait('hurt');
            }
        };

        unit.onDeath = async () => {
            await this.playSpineAndWait('death');
            await this.fadeOut(0.5);
        };

        // ... bind other hooks ...
    }

    unbind() {
        if (!this.unit) return;
        this.unit.onTakeDamage = undefined;
        this.unit.onDeath = undefined;
        // ... clear other hooks ...
        this.unit = null;
    }

    private playSpineAndWait(anim: string): Promise<void> {
        return new Promise(resolve => {
            this.spine.setAnimation(0, anim, false);
            this.spine.setCompleteListener(() => resolve());
        });
    }
}
```

### Step 4: Connect via Manager

```typescript
class BattleScene {
    private units: BattleUnit[] = [];
    private views: Map<string, BattleUnitView> = new Map();

    addUnit(unit: BattleUnit, viewNode: Node) {
        this.units.push(unit);
        const view = viewNode.getComponent(BattleUnitView);
        view.bind(unit);
        this.views.set(unit.id, view);
    }

    removeUnit(unit: BattleUnit) {
        const view = this.views.get(unit.id);
        view?.unbind();
        this.views.delete(unit.id);
        // logic unit can still exist for replay/history
    }
}
```

## Choosing Promise vs Fire-and-Forget

| Situation | Return type | Reason |
|-----------|-------------|--------|
| Logic must wait for animation | `Promise<void>` | `await` to sequence correctly |
| Logic continues immediately, view performs in background | `void` | Does not block game flow |
| Logic needs a result from view (rare) | `Promise<T>` | e.g. user picks a target |

Rule of thumb: **use Promise when gameplay ordering matters**, fire-and-forget when it is purely visual feedback.

### Example: Logic needs a result from view

This is uncommon but arises when the view must present a choice to the player and logic awaits the decision:

```typescript
class BattleUnit {
    // View resolves the Promise with the chosen target
    onChooseTarget?: (data: { candidates: BattleUnit[] }) => Promise<BattleUnit>;

    async castTargetedSkill(skillId: string) {
        const skill = SkillDB.get(skillId);
        const candidates = this.findValidTargets(skill);

        // View shows target picker UI, player chooses, Promise resolves
        const target = await this.onChooseTarget?.({ candidates })
            ?? candidates[0]; // fallback for headless: pick first

        await this.castSkill(skillId, [target]);
    }
}
```

In headless mode, `onChooseTarget` is undefined, so `?.()` returns `undefined` and the `??` fallback picks the first candidate automatically. This keeps the pattern consistent.

## Lifecycle vs Event Bus: Where to Draw the Line

```
onTakeDamage  ──→  lifecycle callback (THIS entity's view plays hurt)
unit_died     ──→  event bus (quest system, sound manager, camera shake)

onSkillCast   ──→  lifecycle callback (THIS caster's view plays cast anim)
skill_used    ──→  event bus (combo tracker, cooldown UI, analytics)
```

**Lifecycle callback:** 1:1 relationship between logic and view of the SAME entity.
**Event bus:** 1:N broadcast to systems NOT directly related to this entity.

**Key principle: logic entities should NOT call EventBus directly.** Keep logic pure by using
a centralized manager that listens to lifecycle hooks and emits events on behalf of the entity.
This keeps logic free of broadcast dependencies and makes headless mode trivial.

See `references/advanced-patterns.md` → **Centralized Event Bridge** for the full pattern.

## Refactoring Tightly-Coupled Code

When you encounter a class that mixes gameplay logic and view code (common in Cocos Creator
projects), follow these steps to extract the lifecycle delegate pattern:

### Step 1: Identify the logic core

Read the class and highlight every line that changes gameplay state (hp, position, buffs,
score, inventory). Everything else is view. A useful test: "Would a headless server need this line?"

### Step 2: Extract result types

Find the data that view code reads after a logic action. Bundle it into a result type.

```typescript
// BEFORE: view reads fields directly after logic mutates them
this.hp -= damage;
this.hpBar.progress = this.hp / this.maxHp;  // view reads this.hp
this.spawnDamageNumber(damage, isCrit);       // view needs damage + isCrit

// AFTER: bundle into DamageResult
interface DamageResult {
    value: number;
    isCrit: boolean;
    remainingHp: number;
    maxHp: number;
}
```

### Step 3: Create logic class, move state + rules

Move all gameplay fields and methods into a plain class with no engine dependencies.
Replace view code with hook invocations.

### Step 4: Create view class, bind to hooks

Move all visual code into a Component subclass. In `bind()`, wire each hook to the
appropriate animation/UI update.

### Step 5: Verify headless

Instantiate the logic class without a view. Run a gameplay scenario. If it completes
without errors, the separation is correct. Write a unit test to lock this in.

### Common pitfalls during refactoring

- **Forgetting async:** if the original code used `scheduleOnce` or `setTimeout` to delay
  between logic steps, those delays were *animation timing*. Replace them with `await` on
  the hook so the view controls the timing, not the logic.
- **Shared references:** if view code directly mutates logic state (e.g. `this.hp = 0` in
  a death animation callback), break that dependency. Logic owns state; view only reads.
- **Engine singletons:** logic code that calls `cc.find()`, `director.getScene()`, or
  `this.node.getComponent()` has view dependencies. Extract those into injected references
  or move them to the view layer.

## Integration with Cocos Creator Component Lifecycle

When using this pattern in Cocos Creator, the engine's own component lifecycle
(`onLoad`, `onEnable`, `onDisable`, `onDestroy`) interacts with bind/unbind:

```typescript
class BattleUnitView extends Component {
    private unit: BattleUnit | null = null;

    // Bind externally — called by the manager/scene after both
    // the node and logic entity are ready
    bind(unit: BattleUnit) { /* ... wire hooks ... */ }

    // Option A: unbind on destroy (most common)
    // Use when the view's lifetime matches the logic entity's lifetime
    onDestroy() {
        this.unbind();
    }

    // Option B: unbind on disable (for pooled/reusable nodes)
    // Use when the node may be deactivated and reactivated later
    onDisable() {
        this.unbind();
    }
    onEnable() {
        // Re-bind only if a logic entity is assigned
        if (this.unit) this.bind(this.unit);
    }

    unbind() {
        if (!this.unit) return;
        this.unit.onTakeDamage = undefined;
        this.unit.onDeath = undefined;
        // ... clear all hooks ...
        this.unit = null;
    }
}
```

**Which option to choose:**
- `onDestroy` unbind: default choice. Simple, predictable. The node is gone, hooks are gone.
- `onDisable/onEnable` unbind: use for object-pooled nodes that get deactivated instead of destroyed. Prevents stale callbacks on inactive nodes, and re-establishes them when the node is reused.
- **Never bind in `onLoad`** unless the logic entity is guaranteed to exist at that point. Prefer explicit `bind()` calls from the manager that owns both the logic entity and the view node.

See detailed examples and advanced patterns in:
- `references/advanced-patterns.md` — centralized event bridge, multi-entity sequences, object pooling, replay, error handling, testing
- `references/common-entities.md` — template hooks for common game entity types