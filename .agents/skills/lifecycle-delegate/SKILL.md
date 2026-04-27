---
name: lifecycle-delegate
description: "Pattern for separating game logic from view/presentation using lifecycle callbacks on an Orchestrator. Use this skill whenever Claude helps with: (1) Logic-view separation in game code, (2) Callback hooks between gameplay logic and animation/UI, (3) Refactoring tightly-coupled code that mixes gameplay state and visual updates, (4) Turn-based or sequential gameplay where logic must await animation, (5) Writing testable headless game logic, (6) Game architecture decisions about where to put hooks or callbacks. Trigger on: 'separate logic and view', 'game architecture', 'MVC for game', 'await animation', 'headless game logic', 'unit test game logic', 'lifecycle hook', 'where to put callbacks', 'game orchestrator'. Also trigger when code mixes gameplay calculations with cc.tween, spine animations, or UI updates in the same class. Trigger when user asks who should own hooks/callbacks in a game system."
---

# Lifecycle Delegate Pattern for Game Development

Separate game logic from view using lifecycle callbacks. Logic is pure data + rules. An **Orchestrator** exposes hooks and sequences all systems. The view binds to the Orchestrator.

## The Three Layers

```
┌──────────────────────┐     returns      ┌─────────────────────────────┐     hooks     ┌──────────────────────────┐
│   Logic Entity       │ ──── result ───→ │      Orchestrator           │ ────────────→ │         View             │
│                      │                  │                             │               │                          │
│  Pure data + rules   │                  │  onUnitDamaged?()           │               │  unitView.playHurt()     │
│  No engine deps      │                  │  onUnitDied?()              │               │  hud.updateHpBar()       │
│  No hooks            │                  │  onMatchSuccess?()          │               │  sound.playHurt()        │
│  Returns results     │                  │  onGameWon?()               │               │  camera.shake()          │
│  Fully testable      │                  │                             │               │                          │
│                      │                  │  Sequences all systems      │               │  Binds to Orchestrator   │
│                      │                  │  Awaits animations          │               │  Not to entities         │
│                      │                  │  Owns game flow             │               │                          │
└──────────────────────┘                  └─────────────────────────────┘               └──────────────────────────┘
```

**Logic entities have NO hooks.** They return result objects. They run without any view.
**Orchestrator owns ALL hooks.** It sequences systems in the correct order and awaits animations.
**View binds to the Orchestrator only.** One Orchestrator ↔ One View.

## Why Hooks Must Be on the Orchestrator

A single gameplay moment triggers many systems simultaneously:

```
Unit takes damage
├── Unit view  → hurt animation, knockback, blink
├── HUD        → HP bar update, damage number
├── Sound      → hurt SFX
├── Camera     → shake
└── Quest      → "take 1000 damage" tracker
```

If hooks sit on the entity, the view must reach into every other system — it becomes coupled to HUD, Sound, Camera, Quest:

```typescript
// ❌ Hooks on entity — view knows too much, coupled to every system
unit.onTakeDamage = async ({ result }) => {
    await this.playHurtAnim();
    this.hud.updateHpBar(result);   // view không nên biết về HUD
    this.sound.playHurt();          // view không nên biết về Sound
    this.camera.shake();            // view không nên biết về Camera
    this.quest.record(result);      // view không nên biết về Quest
};

// ✅ Hooks on Orchestrator — each system does only its own job
orchestrator.onUnitDamaged = async ({ unit, result }) => {
    await unitView.playHurtAnim();  // unit view: only unit animation
    hud.updateHpBar(result);        // hud: only UI
    sound.play('hurt');             // sound: only audio
    camera.shake();                 // camera: only camera
    quest.record(result);           // quest: only tracking
};
```

The Orchestrator is the only layer with enough context to know the correct ordering and which systems to notify.

## Hook Placement Rule

```
Default:    Hooks go on the Orchestrator
Exception:  Hooks go on an entity ONLY when there is a specific requirement:
            - Object pooling where entity and view have strict 1:1 lifetime
            - Headless replay / AI simulation needing per-entity interception
            - A subsystem that truly has no other system involved
```

Most games have at least one Orchestrator. Complex games have several — one per domain (Battle, Map, UI, Shop...) — each owning hooks for its domain, never sharing hooks across domains.

## Implementation

### Step 1 — Logic entity: pure, returns results, no hooks

```typescript
class BattleUnit {
    hp: number;
    maxHp: number;
    atk: number;

    // Returns a result — does NOT fire any hook
    receiveDamage(raw: number, attacker: BattleUnit): DamageResult {
        const isCrit = Math.random() < 0.2;
        const value = isCrit ? raw * 2 : raw;
        this.hp = Math.max(0, this.hp - value);
        return { value, isCrit, remainingHp: this.hp, maxHp: this.maxHp };
    }

    isDead(): boolean { return this.hp <= 0; }
}
```

### Step 2 — Define result types (one per gameplay moment)

```typescript
// Bundle all context the view needs — it should never need to call back into logic
interface DamageResult {
    value: number;
    isCrit: boolean;
    remainingHp: number;
    maxHp: number;
    knockbackDir?: Vec3;
    shieldAbsorbed?: number;
}

interface SkillCastResult {
    skillId: string;
    caster: BattleUnit;
    targets: BattleUnit[];
    damageResults: DamageResult[];
}
```

### Step 3 — Orchestrator: owns hooks, calls logic, sequences systems

```typescript
class BattleOrchestrator {
    // All hooks live here — ~5 to 10 for a full game domain
    onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
    onUnitDied?:    (data: { unit: BattleUnit }) => Promise<void>;
    onSkillCast?:   (data: { result: SkillCastResult }) => Promise<void>;
    onBattleWon?:   (data: { stars: number; score: number }) => Promise<void>;
    onBattleLost?:  (data: { reason: 'timeout' | 'wiped' }) => Promise<void>;

    async processAttack(attacker: BattleUnit, target: BattleUnit): Promise<void> {
        // 1. Logic runs, returns result
        const result = target.receiveDamage(attacker.atk, attacker);

        // 2. Orchestrator fires hook — view + all systems respond in sequence
        await this.onUnitDamaged?.({ unit: target, result });

        // 3. Orchestrator continues game flow after animation completes
        if (target.isDead()) {
            await this.onUnitDied?.({ unit: target });
            this.removeUnit(target);
            await this.checkWinCondition();
        }
    }

    private async checkWinCondition(): Promise<void> {
        if (this.enemies.length === 0) {
            const stars = this.scoreManager.calculateStars();
            await this.onBattleWon?.({ stars, score: this.scoreManager.getScore() });
        }
    }
}
```

### Step 4 — View: binds to Orchestrator only

```typescript
class BattleView extends Component {
    private orchestrator: BattleOrchestrator | null = null;

    bind(orchestrator: BattleOrchestrator): void {
        this.orchestrator = orchestrator;

        orchestrator.onUnitDamaged = async ({ unit, result }) => {
            const view = this.getUnitView(unit);
            // Unit animation first, then cross-system updates
            if (result.knockbackDir) {
                await view.playKnockback(result.knockbackDir);
            } else {
                await view.playSpine('hurt');
            }
            this.hud.updateHpBar(unit, result.remainingHp, result.maxHp);
            this.hud.spawnDamageNumber(result.value, result.isCrit);
            this.sound.play('hurt');
            this.camera.shake(0.2);
        };

        orchestrator.onUnitDied = async ({ unit }) => {
            const view = this.getUnitView(unit);
            await view.playSpine('death');
            await view.fadeOut(0.5);
            this.sound.play('death');
        };

        orchestrator.onBattleWon = async ({ stars, score }) => {
            await this.ui.showVictoryScreen(stars, score);
        };
    }

    unbind(): void {
        if (!this.orchestrator) return;
        this.orchestrator.onUnitDamaged = undefined;
        this.orchestrator.onUnitDied    = undefined;
        this.orchestrator.onSkillCast   = undefined;
        this.orchestrator.onBattleWon   = undefined;
        this.orchestrator.onBattleLost  = undefined;
        this.orchestrator = null;
    }

    // Cocos Creator lifecycle
    onDestroy(): void { this.unbind(); }
    // For pooled nodes: onDisable() { this.unbind(); }
    //                   onEnable()  { if (this.orchestrator) this.bind(this.orchestrator); }
}
```

### Step 5 — Scene connects everything

```typescript
class BattleScene extends Component {
    private orchestrator = new BattleOrchestrator();

    onLoad(): void {
        const view = this.node.getComponent(BattleView);
        view.bind(this.orchestrator);
        this.orchestrator.loadLevel(config);
        this.orchestrator.startBattle();
    }

    onDestroy(): void {
        this.node.getComponent(BattleView)?.unbind();
    }
}
```

## Callback Granularity

**Each hook = one gameplay "moment".** Not every field change, not every internal step.

### ❌ Too granular — caller must reassemble fragments

```typescript
onHpChanged?:      (hp: number) => void;      // 5 callbacks
onCritTriggered?:  () => void;                // for one
onKnockback?:      (dir: Vec3) => void;       // single
onShieldBroke?:    () => void;                // hit
onDamageNumber?:   (val: number) => void;
```

### ❌ Data observation — not a lifecycle moment, remove these

```typescript
onHpBarNeedsUpdate?: (hp: number) => void;      // view reads hp directly
onTimerTick?:        (remaining: number) => void; // view polls in update loop
onInventoryChanged?: (inv: Inventory) => void;    // view reads after each action
```

These are not gameplay moments — they are data sync. View reads state via getters, never via hooks.

### ✅ Right level — one hook per gameplay moment, full context bundled

```typescript
onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
onUnitHealed?:  (data: { unit: BattleUnit; result: HealResult })   => void;
onSkillCast?:   (data: { result: SkillCastResult })                => Promise<void>;
```

### Always wrap params in a data object

```typescript
// ❌ Positional — adding a field forces every binding to update its signature
onUnitDamaged?: (unit: BattleUnit, result: DamageResult) => Promise<void>;

// ✅ Data object — adding an optional field breaks nothing
onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
// Later: add sourceSkillId? — existing bindings still compile and run
```

## Promise vs Fire-and-Forget

| Situation | Type | Reason |
|---|---|---|
| Logic must wait for animation to complete | `Promise<void>` | Next action depends on anim finishing |
| Visual feedback only, logic continues | `void` | No ordering dependency |
| View must return a value to logic (rare) | `Promise<T>` | e.g., player picks a target |

## Lifecycle vs EventBus

```
Orchestrator hook  →  systems that must run IN ORDER, or that must AWAIT animation
EventBus           →  fire-and-forget broadcast where order does not matter
```

```typescript
// Hook: view + HUD + sound must sequence correctly after damage
await this.onUnitDamaged?.({ unit, result });

// EventBus: quest, analytics, achievements don't block the game flow
EventBus.emit('unit_damaged', { unit, result });
```

**Logic entities must NOT call EventBus directly.** The Orchestrator emits events after firing hooks. This keeps logic pure and headless-compatible.

## Self-Check

- [ ] Are hooks on an entity instead of the Orchestrator? → move them up unless there is a specific reason
- [ ] Is the view reaching into HUD/Sound/Camera inside a hook? → that is Orchestrator work, move it up
- [ ] Does a hook fire on every frame or every field change? → not a lifecycle moment, remove it and use a getter
- [ ] Does the Orchestrator have more than 10 hooks? → consider splitting into sub-orchestrators by domain
- [ ] Does adding a small feature require a new hook? → the abstraction is leaking

## Reference Files

For advanced patterns and real project examples, read the relevant file:

- `references/advanced-patterns.md` — Multi-entity sequences, ordered async pipeline, EventBus bridge, object pooling, headless testing
- `references/common-orchestrators.md` — Templates for common game types: battle, puzzle, board game, shop/inventory