# Advanced Patterns

## Multi-Entity Sequence

When a skill hits multiple targets, the Orchestrator sequences each target's response in order:

```typescript
class BattleOrchestrator {
    onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
    onUnitDied?:    (data: { unit: BattleUnit }) => Promise<void>;

    async processSkill(caster: BattleUnit, skill: Skill, targets: BattleUnit[]): Promise<void> {
        // Targets animate one at a time — or in parallel depending on design
        for (const target of targets) {
            const result = target.receiveDamage(skill.power, caster);
            await this.onUnitDamaged?.({ unit: target, result });

            if (target.isDead()) {
                await this.onUnitDied?.({ unit: target });
                this.removeUnit(target);
            }
        }
        // All animations finished — continue game flow
        await this.startNextTurn();
    }
}
```

For parallel animations (e.g. area attack where all targets react simultaneously):

```typescript
await Promise.all(targets.map(async target => {
    const result = target.receiveDamage(skill.power, caster);
    await this.onUnitDamaged?.({ unit: target, result });
}));
```

---

## Ordered Async Pipeline (Cross-System Sequencing)

When multiple systems must react to the same event IN ORDER and each may be async:

```typescript
class BattleOrchestrator {
    // One hook, view handles all systems in the right order
    onUnitDied?: (data: { unit: BattleUnit }) => Promise<void>;
}

// View implementation — sequencing is view's responsibility
orchestrator.onUnitDied = async ({ unit }) => {
    // 1. Unit animation first
    await unitView.playDeath();
    await unitView.fadeOut(0.5);

    // 2. Quest check (may show popup — must await)
    await questSystem.checkUnitKilled(unit);

    // 3. Sound after quest popup resolves
    sound.play('victory_sting');

    // 4. Camera transition last
    await camera.panToNextUnit();
};
```

If the ordering needs to be configurable (different scenes want different order), use a handler array:

```typescript
class GameSequencer {
    private handlers: Array<(unit: BattleUnit) => Promise<void>> = [];

    registerOnUnitDied(handler: (unit: BattleUnit) => Promise<void>): void {
        this.handlers.push(handler);
    }

    async fireUnitDied(unit: BattleUnit): Promise<void> {
        for (const h of this.handlers) {
            await h(unit);  // sequential, not concurrent
        }
    }
}

// Setup — order of registration = order of execution
sequencer.registerOnUnitDied(async u => await unitView.playDeath(u));
sequencer.registerOnUnitDied(async u => await questSystem.check(u));
sequencer.registerOnUnitDied(async u => sound.play('death'));
sequencer.registerOnUnitDied(async u => await camera.transition());
```

---

## EventBus Bridge

Logic entities must NOT call EventBus directly. The Orchestrator acts as the bridge — it fires hooks (for ordered, awaited systems) and emits events (for fire-and-forget systems) after the hook resolves:

```typescript
class BattleOrchestrator {
    onUnitDied?: (data: { unit: BattleUnit }) => Promise<void>;

    private async handleUnitDied(unit: BattleUnit): Promise<void> {
        // 1. Ordered systems via hook — await completes before continuing
        await this.onUnitDied?.({ unit });

        // 2. Fire-and-forget systems via EventBus — don't block game flow
        EventBus.emit('unit_died', { unit });
        // → AchievementSystem listens
        // → AnalyticsSystem listens
        // → AudioAmbientSystem listens
    }
}
```

EventBus listeners must never be awaited by the Orchestrator. If a listener needs to await (e.g., showing a "Achievement Unlocked" popup), it manages its own async internally.

---

## Object Pooling

When nodes are pooled (reused instead of destroyed), unbind on disable and rebind on enable:

```typescript
class BattleView extends Component {
    private orchestrator: BattleOrchestrator | null = null;

    bind(orchestrator: BattleOrchestrator): void {
        this.orchestrator = orchestrator;
        orchestrator.onUnitDamaged = async ({ unit, result }) => { /* ... */ };
        // ... other hooks
    }

    unbind(): void {
        if (!this.orchestrator) return;
        this.orchestrator.onUnitDamaged = undefined;
        // ... clear all hooks
        this.orchestrator = null;
    }

    // For pooled nodes: clear hooks when deactivated
    onDisable(): void { this.unbind(); }

    // Re-establish hooks when reused
    onEnable(): void {
        if (this.orchestrator) this.bind(this.orchestrator);
    }

    // For non-pooled nodes: just use onDestroy
    // onDestroy(): void { this.unbind(); }
}
```

**Rule:** If a node is destroyed (not pooled) → use `onDestroy`. If a node is deactivated and reused → use `onDisable/onEnable`.

---

## Headless Testing

Because logic entities have no hooks and return result objects, they test trivially:

```typescript
describe('BattleUnit', () => {
    it('should apply damage correctly', () => {
        const unit = new BattleUnit({ hp: 100, maxHp: 100 });
        const attacker = new BattleUnit({ hp: 100, maxHp: 100, atk: 30 });
        const result = unit.receiveDamage(30, attacker);

        expect(result.value).toBe(30);
        expect(result.remainingHp).toBe(70);
        expect(unit.hp).toBe(70);
    });

    it('should report dead when hp reaches 0', () => {
        const unit = new BattleUnit({ hp: 10, maxHp: 100 });
        const attacker = new BattleUnit({ hp: 100, maxHp: 100, atk: 50 });
        unit.receiveDamage(50, attacker);

        expect(unit.isDead()).toBe(true);
        expect(unit.hp).toBe(0);  // never goes negative
    });
});
```

To test the Orchestrator's sequencing without a view, bind a mock hook:

```typescript
it('should fire onUnitDied after hp reaches 0', async () => {
    const orchestrator = new BattleOrchestrator();
    orchestrator.loadUnits([attacker, target]);

    let diedFired = false;
    orchestrator.onUnitDied = async ({ unit }) => { diedFired = true; };

    await orchestrator.processAttack(attacker, target);

    expect(diedFired).toBe(true);
});
```

---

## Refactoring Tightly-Coupled Code

When a class mixes gameplay state and visual updates:

### Step 1 — Identify the logic core

Highlight every line that changes gameplay state (hp, position, score, inventory). Everything else is view. Test: "Would a headless server need this line?"

### Step 2 — Extract result types

```typescript
// BEFORE: view reads fields directly after logic mutates them
this.hp -= damage;
this.hpBar.progress = this.hp / this.maxHp;
this.spawnDamageNumber(damage);

// AFTER: logic returns result, Orchestrator distributes it
const result = unit.receiveDamage(damage);
await this.onUnitDamaged?.({ unit, result });
// View hook handles hpBar and damage number
```

### Step 3 — Create logic class (no hooks, no engine deps, returns results)

### Step 4 — Create Orchestrator (hooks, calls logic, sequences systems)

### Step 5 — Create View (binds to Orchestrator hooks)

### Step 6 — Verify headless

```typescript
// No view attached — if this runs without error, separation is correct
const orchestrator = new BattleOrchestrator();
orchestrator.loadLevel(config);
await orchestrator.processAttack(unit1, unit2);
// All hooks are undefined → ?.() skips gracefully
```

### Common pitfalls

- **Hooks on entities** — the most common mistake. Move them to the Orchestrator.
- **View touching other systems** — if the hook body calls HUD/Sound/Camera it is Orchestrator work. Move it up.
- **`scheduleOnce`/`setTimeout` in original code** — these were animation timing. Replace with `await` on the hook.
- **View mutating logic state** — view must only READ from result objects. Logic owns state.
- **Engine singletons in logic** — `cc.find()`, `director.getScene()` in a logic class = view dependency. Move to view layer.