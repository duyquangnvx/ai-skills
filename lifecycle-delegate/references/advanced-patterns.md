# Advanced Lifecycle Delegate Patterns

## Table of Contents

1. [Multi-Entity Sequences](#multi-entity-sequences)
2. [Object Pooling with Bind/Unbind](#object-pooling)
3. [Replay & Headless Mode](#replay-and-headless)
4. [Single Callback vs Multi-Listener](#single-vs-multi-listener)
5. [Nested Lifecycles](#nested-lifecycles)
6. [Centralized Event Bridge](#centralized-event-bridge)
7. [Error Handling in Async Hooks](#error-handling)
8. [Testing Logic Without View](#testing)

---

## Multi-Entity Sequences

When a skill affects multiple targets, decide whether to sequence or parallelize the animations.

### Sequential — turn-based, each hit plays out clearly

```typescript
class BattleUnit {
    async castSkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);
        this.consumeMp(skill.mpCost);

        // Caster plays cast animation
        await this.onSkillCast?.({ info: { skillId, targets } });

        // Each target receives damage sequentially — wait for each hurt anim before the next
        for (const target of targets) {
            await target.receiveDamage(skill.damage, skill.element, this);
        }
    }
}
```

### Parallel — AoE, all targets animate simultaneously

```typescript
class BattleUnit {
    async castAoESkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);
        await this.onSkillCast?.({ info: { skillId, targets } });

        // All targets receive damage in parallel
        await Promise.all(
            targets.map(t => t.receiveDamage(skill.damage, skill.element, this))
        );
    }
}
```

### Mixed — cast sequentially, but AoE damage in parallel

```typescript
class BattleUnit {
    async castMultiHitSkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);

        // Phase 1: cast anim (sequential)
        await this.onSkillCast?.({ info: { skillId, targets } });

        // Phase 2: each hit is sequential, but each hit affects all targets in parallel
        for (let i = 0; i < skill.hitCount; i++) {
            const dmgPerHit = Math.floor(skill.damage / skill.hitCount);
            await Promise.all(
                targets.map(t => t.receiveDamage(dmgPerHit, skill.element, this))
            );
        }
    }
}
```

---

## Object Pooling

When entities are reused (e.g. enemies in a wave-based game), the view must unbind/rebind cleanly.

```typescript
class EnemyPool {
    private pool: Node[] = [];
    private activeViews: Map<string, EnemyView> = new Map();

    spawn(unit: BattleUnit): EnemyView {
        const node = this.pool.pop() ?? instantiate(this.prefab);
        const view = node.getComponent(EnemyView);

        view.bind(unit);   // wire callbacks
        this.activeViews.set(unit.id, view);

        unit.onDeath = async () => {
            await view.playDeathAnim();
            this.recycle(unit);
        };

        return view;
    }

    private recycle(unit: BattleUnit) {
        const view = this.activeViews.get(unit.id);
        if (!view) return;

        view.unbind();      // CRITICAL: clear all callbacks before recycling
        view.reset();       // reset visual state
        this.activeViews.delete(unit.id);
        this.pool.push(view.node);
    }
}
```

**Critical:** `unbind()` must clear ALL callbacks. If you forget one, the new logic entity
bound to this recycled view will trigger a stale callback on the old entity's view — a bug
that is extremely hard to trace.

```typescript
class EnemyView extends Component {
    unbind() {
        if (!this.unit) return;
        // Clear everything — do not forget any hook
        this.unit.onEnterBattle = undefined;
        this.unit.onTakeDamage = undefined;
        this.unit.onDeath = undefined;
        this.unit.onBuffsChanged = undefined;
        this.unit = null;
    }

    reset() {
        this.spine.setAnimation(0, 'idle', true);
        this.hpBar.setFull();
        this.node.setPosition(Vec3.ZERO);
        this.node.active = true;
    }
}
```

### Helper: Auto-unbind pattern

To avoid forgetting to clear callbacks, use a helper that tracks all hook names:

```typescript
// Logic entity base class
abstract class GameEntity {
    // Declare all hook names to support auto-clear
    protected static readonly HOOKS: string[] = [];

    clearAllHooks() {
        const hooks = (this.constructor as typeof GameEntity).HOOKS;
        for (const key of hooks) {
            (this as any)[key] = undefined;
        }
    }
}

class BattleUnit extends GameEntity {
    protected static readonly HOOKS = [
        'onEnterBattle', 'onTurnStart', 'onSkillCast',
        'onTakeDamage', 'onHealed', 'onBuffsChanged', 'onDeath'
    ];

    onEnterBattle?: () => void;
    onTurnStart?: () => Promise<void>;
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onHealed?: (data: { result: HealResult }) => void;
    onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
    onDeath?: () => Promise<void>;
}

// View only needs one line
class EnemyView extends Component {
    unbind() {
        this.unit?.clearAllHooks();
        this.unit = null;
    }
}
```

---

## Replay and Headless

The biggest advantage of this pattern: logic runs entirely without a view.

### Headless simulation (server or AI)

```typescript
// No view bound — all callbacks are undefined, skipped via optional chaining
const battle = new BattleSimulation();
battle.addUnit(new BattleUnit(heroData));   // no view binding
battle.addUnit(new BattleUnit(enemyData));

// Logic runs normally; await resolves immediately because callback is undefined
// undefined?.() returns undefined, and await undefined resolves instantly
await battle.run();

console.log(battle.getResult()); // winner, turn count, damage dealt...
```

### Replay — record actions, replay with view

```typescript
interface BattleAction {
    type: 'skill' | 'item' | 'move';
    actorId: string;
    targetIds: string[];
    data: any;
    timestamp: number;
}

class BattleReplay {
    // Replay from action log — logic recalculates, view replays animations
    async replay(actions: BattleAction[], scene: BattleScene) {
        for (const action of actions) {
            const actor = scene.getUnit(action.actorId);
            const targets = action.targetIds.map(id => scene.getUnit(id));

            switch (action.type) {
                case 'skill':
                    // Logic recalculates damage, view plays animation
                    await actor.castSkill(action.data.skillId, targets);
                    break;
                case 'item':
                    await actor.useItem(action.data.itemId, targets[0]);
                    break;
            }
        }
    }

    // Fast-forward: run headless then apply final state
    async fastForward(actions: BattleAction[], scene: BattleScene) {
        // Unbind all views
        scene.unbindAllViews();

        // Run logic headless — no animations, resolves instantly
        for (const action of actions) {
            const actor = scene.getUnit(action.actorId);
            const targets = action.targetIds.map(id => scene.getUnit(id));
            if (action.type === 'skill') {
                await actor.castSkill(action.data.skillId, targets);
            }
        }

        // Rebind views, apply final state visually
        scene.rebindAllViews();
    }
}
```

---

## Single Callback vs Multi-Listener

By default, each hook is a single optional callback. This covers ~90% of use cases and keeps
things simple with clear ownership. However, some situations require multiple listeners on the
same hook.

### When to use which

| Scenario | Use | Reason |
|----------|-----|--------|
| One entity, one view | Single callback | Simple, clear ownership |
| Entity belongs to a group/team | **Multi-listener** | Both view AND team need to hook `onDeath` |
| Multiple systems react to same moment | **Multi-listener** | View plays anim, buff system checks expiry, etc. |
| Entity will be wrapped by higher-level logic | **Multi-listener** | Wrapping a single callback risks overwrite |

**Rule of thumb:** if the entity can be part of a composite structure (team, formation, deck),
prefer multi-listener from the start to avoid refactoring later.

### LifecycleHook utility class

```typescript
class LifecycleHook<T extends (...args: any[]) => any> {
    private listeners: T[] = [];

    add(fn: T) { this.listeners.push(fn); }
    remove(fn: T) {
        const idx = this.listeners.indexOf(fn);
        if (idx >= 0) this.listeners.splice(idx, 1);
    }
    clear() { this.listeners.length = 0; }

    async invoke(...args: Parameters<T>): Promise<void> {
        for (const fn of this.listeners) {
            await fn(...args);
        }
    }

    get hasListeners(): boolean {
        return this.listeners.length > 0;
    }
}

// Usage
class BattleUnit {
    readonly onDeath = new LifecycleHook<() => Promise<void>>();

    async die() {
        await this.onDeath.invoke();  // all listeners run sequentially
        // No EventBus here — bridge listener handles broadcast (see Centralized Event Bridge)
    }
}

// View hooks in
unit.onDeath.add(async () => { await view.playDeathAnim(); });
// Team hooks in
unit.onDeath.add(async () => { team.checkDefeat(); });
// Bridge hooks in (wired by BattleEventBridge)
unit.onDeath.add(async () => { eventBus.emit('unit_died', { unitId: unit.id }); });
```

### Headless compatibility with LifecycleHook

When no listeners are registered, `invoke()` simply iterates an empty array and resolves
immediately — same behavior as `undefined?.()` with single callbacks. No special handling needed.

---

## Nested Lifecycles

When an entity contains sub-entities (e.g. team contains units, unit contains equipment),
their lifecycles compose naturally.

```typescript
class BattleTeam {
    readonly onTeamTurnStart = new LifecycleHook<() => Promise<void>>();
    readonly onTeamDefeated = new LifecycleHook<() => Promise<void>>();

    private units: BattleUnit[] = [];

    addUnit(unit: BattleUnit) {
        this.units.push(unit);

        // Hook into unit's death to check team defeat
        // Using LifecycleHook means this does NOT overwrite the view's hook
        unit.onDeath.add(async () => {
            if (this.getAliveUnits().length === 0) {
                await this.onTeamDefeated.invoke();
            }
        });
    }

    async startTurn() {
        await this.onTeamTurnStart.invoke();

        for (const unit of this.getAliveUnits()) {
            await unit.startTurn();  // each unit has its own lifecycle
        }
    }

    private getAliveUnits(): BattleUnit[] {
        return this.units.filter(u => u.hp > 0);
    }
}
```

Notice how `LifecycleHook` eliminates the callback-overwrite problem entirely. The view adds
its death animation listener, the team adds its defeat-check listener, and both run in sequence
without interfering. This is why entities that participate in composite structures should use
multi-listener hooks from the start.

---

## Centralized Event Bridge

A key refinement: **logic entities should never import or call EventBus directly.** Instead,
a centralized manager listens to lifecycle hooks and emits events on their behalf. This keeps
logic completely pure — no broadcast dependencies, no imports beyond its own domain.

### The problem with EventBus inside logic

```typescript
// ❌ Logic entity knows about EventBus — impure
class BattleUnit {
    async receiveDamage(...) {
        // ...
        if (this.hp <= 0) {
            await this.onDeath?.();
            EventBus.emit('unit_died', this.id);       // logic depends on EventBus
            EventBus.emit('check_quest', this.id);     // and keeps growing...
            EventBus.emit('play_global_sfx', 'death');
        }
    }
}
```

Problems:
- Logic imports EventBus — cannot run in a pure headless environment without stubbing it
- Adding a new system listener means editing the logic class
- Hard to trace which events fire from which gameplay moment

### The solution: Centralized Bridge

```
Logic Entity              BattleEventBridge            Other Systems
─────────────             ─────────────────            ─────────────
onDeath fires  ────→      listens via hook    ────→    EventBus.emit('unit_died')
                          transforms data     ────→    EventBus.emit('check_quest')
                          decides what to              EventBus.emit('play_sfx')
                          broadcast
```

```typescript
// ✅ Logic entity is completely pure — no EventBus, no external imports
class BattleUnit {
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onDeath?: () => Promise<void>;
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;

    async receiveDamage(raw: number, element: ElementType, attacker: BattleUnit) {
        const result = this.calculateDamage(raw, element, attacker);
        this.hp = Math.max(0, this.hp - result.value);
        await this.onTakeDamage?.({ result });

        if (this.hp <= 0) {
            await this.onDeath?.();
            // Nothing else here. Logic is done. Bridge handles the rest.
        }
    }
}
```

```typescript
// Bridge: hooks → events. Lives outside logic layer.
class BattleEventBridge {
    constructor(private eventBus: EventBus) {}

    /** Wire all lifecycle hooks of a unit to the event bus */
    wire(unit: BattleUnit) {
        // Using LifecycleHook.add() so this does NOT overwrite view's hooks
        unit.onDeath.add(async () => {
            this.eventBus.emit('unit_died', { unitId: unit.id, team: unit.teamId });
            this.eventBus.emit('check_quest_progress', { trigger: 'kill', unitId: unit.id });
        });

        unit.onTakeDamage.add(async ({ result }) => {
            this.eventBus.emit('damage_dealt', {
                unitId: unit.id,
                value: result.value,
                element: result.element,
                isCrit: result.isCrit,
            });
            if (result.isCrit) {
                this.eventBus.emit('play_global_sfx', { sfx: 'crit_impact' });
            }
        });

        unit.onSkillCast.add(async ({ info }) => {
            this.eventBus.emit('skill_used', {
                casterId: unit.id,
                skillId: info.skillId,
                targetCount: info.targets.length,
            });
        });
    }

    /** Unwire when unit is removed from battle */
    unwire(unit: BattleUnit) {
        // If using LifecycleHook, store references to remove specific listeners.
        // Or simply clear all hooks if no other listeners remain.
        // See auto-unbind pattern in Object Pooling section.
    }
}
```

### Integration with BattleScene

```typescript
class BattleScene {
    private bridge = new BattleEventBridge(EventBus.global);
    private views: Map<string, BattleUnitView> = new Map();

    addUnit(unit: BattleUnit, viewNode: Node) {
        // View hooks: animation
        const view = viewNode.getComponent(BattleUnitView);
        view.bind(unit);
        this.views.set(unit.id, view);

        // Bridge hooks: cross-system events
        this.bridge.wire(unit);
    }

    removeUnit(unit: BattleUnit) {
        this.views.get(unit.id)?.unbind();
        this.views.delete(unit.id);
        this.bridge.unwire(unit);
    }
}
```

### Why this matters for headless mode

Without the bridge, headless mode requires a stub EventBus to avoid crashes.
With the bridge, headless mode simply never creates a BattleEventBridge — logic runs
with no hooks bound, all `?.()` calls resolve to undefined, and no events fire. Zero setup.

```typescript
// Headless: no view, no bridge, no EventBus — just logic
const battle = new BattleSimulation();
battle.addUnit(new BattleUnit(heroData));   // no view.bind(), no bridge.wire()
await battle.run();                         // runs cleanly
```

### Data transformation in the bridge

The bridge is also the right place to reshape hook data into event payloads. Logic result
types are designed for view consumption (rich, contextual). Event payloads are designed for
system consumption (flat, minimal). The bridge translates between them:

```typescript
// Hook data (rich, for view): DamageResult { value, isCrit, element, shieldAbsorbed, ... }
// Event payload (flat, for systems): { unitId, value, element, isCrit }
// Bridge does the mapping — neither logic nor systems need to know each other's shape.
```

### When to use the bridge vs direct hooks

| Scenario | Approach |
|----------|----------|
| View needs to animate THIS entity | Direct lifecycle hook |
| Team/group needs to react to THIS entity | LifecycleHook (multi-listener, same as view) |
| Unrelated systems need to know something happened | Centralized Event Bridge → EventBus |
| Debug/logging all lifecycle events | Bridge (single place to add logging) |

---

## Error Handling

View callbacks can throw (e.g. node destroyed mid-animation). Logic must remain robust.

```typescript
class BattleUnit {
    async receiveDamage(raw: number, element: ElementType, attacker: BattleUnit) {
        const result = this.calculateDamage(raw, element, attacker);
        this.hp = Math.max(0, this.hp - result.value);

        // View may crash — logic must continue regardless
        try {
            await this.onTakeDamage?.({ result });
        } catch (e) {
            console.warn(`View callback failed for unit ${this.id}:`, e);
            // Logic continues normally — game does not crash because of a view error
        }

        if (this.hp <= 0) {
            try {
                await this.onDeath?.();
            } catch (e) {
                console.warn(`Death callback failed for unit ${this.id}:`, e);
            }
            // Bridge listener on onDeath handles EventBus broadcast
        }
    }
}
```

### Timeout guard — prevent view from blocking logic forever

```typescript
function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
    return Promise.race([
        promise,
        new Promise<T>((_, reject) =>
            setTimeout(() => reject(new Error(`Timeout: ${label} took > ${ms}ms`)), ms)
        ),
    ]);
}

// Usage
await withTimeout(
    this.onTakeDamage?.({ result }) ?? Promise.resolve(),
    5000,
    `onTakeDamage unit ${this.id}`
);
```

### Safe invoke helper for LifecycleHook

When using multi-listener hooks, wrap invoke with error handling so one failing listener
does not prevent others from running:

```typescript
class LifecycleHook<T extends (...args: any[]) => any> {
    // ... add, remove, clear ...

    async invokeSafe(...args: Parameters<T>): Promise<void> {
        for (const fn of this.listeners) {
            try {
                await fn(...args);
            } catch (e) {
                console.warn('Lifecycle listener failed:', e);
            }
        }
    }
}
```

---

## Testing

Logic runs headless, so testing is straightforward — no engine mocking required.

```typescript
describe('BattleUnit.receiveDamage', () => {
    it('should reduce hp and trigger onTakeDamage', async () => {
        const unit = new BattleUnit({ hp: 100, maxHp: 100, def: 10 });
        const receivedResults: DamageResult[] = [];

        // "View" is just a callback that records results
        unit.onTakeDamage = async ({ result }) => {
            receivedResults.push(result);
        };

        const attacker = new BattleUnit({ atk: 50 });
        await unit.receiveDamage(50, ElementType.FIRE, attacker);

        expect(unit.hp).toBeLessThan(100);
        expect(receivedResults).toHaveLength(1);
        expect(receivedResults[0].element).toBe(ElementType.FIRE);
    });

    it('should work without view (headless)', async () => {
        const unit = new BattleUnit({ hp: 100, maxHp: 100, def: 10 });
        // No callback bound
        const attacker = new BattleUnit({ atk: 50 });

        // Does not throw, does not crash
        await unit.receiveDamage(50, ElementType.FIRE, attacker);
        expect(unit.hp).toBeLessThan(100);
    });

    it('should trigger onDeath when hp reaches 0', async () => {
        const unit = new BattleUnit({ hp: 1, maxHp: 100, def: 0 });
        let deathTriggered = false;
        unit.onDeath = async () => { deathTriggered = true; };

        const attacker = new BattleUnit({ atk: 50 });
        await unit.receiveDamage(50, ElementType.PHYSICAL, attacker);

        expect(unit.hp).toBe(0);
        expect(deathTriggered).toBe(true);
    });

    it('should support testing with LifecycleHook', async () => {
        const unit = new BattleUnit({ hp: 100, maxHp: 100, def: 10 });
        const log: string[] = [];

        // Multiple listeners — verify ordering
        unit.onTakeDamage.add(async () => { log.push('listener-1'); });
        unit.onTakeDamage.add(async () => { log.push('listener-2'); });

        const attacker = new BattleUnit({ atk: 50 });
        await unit.receiveDamage(50, ElementType.FIRE, attacker);

        expect(log).toEqual(['listener-1', 'listener-2']);
    });
});
```