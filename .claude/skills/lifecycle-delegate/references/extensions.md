# Extensions

Patterns that come up after the basic Orchestrator + hooks structure is in place. Same goal as SKILL.md: keep the gameplay flow readable top-to-bottom.

## 1. Multiple targets in one moment

When a single action affects several entities (area attack, board cascade), pick serial or parallel pacing per method.

### Serial — dramatic pacing

```ts
async resolveArea(skill: Skill, targets: Entity[]): Promise<void> {
    for (const target of targets) {
        const result = target.takeDamage(skill.power);
        await this.onDamaged?.({ target, result });
        if (target.isDead()) {
            await this.onDied?.({ target });
            this.remove(target);
        }
    }
}
```

### Parallel — snappy

```ts
async resolveArea(skill: Skill, targets: Entity[]): Promise<void> {
    await Promise.all(targets.map(async (target) => {
        const result = target.takeDamage(skill.power);
        await this.onDamaged?.({ target, result });
        if (target.isDead()) {
            await this.onDied?.({ target });
            this.remove(target);
        }
    }));
}
```

The choice is per-method, made by the Orchestrator. The view never decides pacing — it only animates.

## 2. Request-response hooks (player input)

Sometimes logic needs the view to ask the player something before continuing. Use `Promise<T>`:

```ts
class CombatOrchestrator {
  onPickTarget?: (data: {
    caster: Entity;
    candidates: Entity[];
  }) => Promise<Entity | null>;

  async castTargeted(caster: Entity, skill: Skill): Promise<void> {
    const candidates = this.findValidTargets(caster, skill);
    const target = await this.onPickTarget?.({ caster, candidates });
    if (!target) return; // null = player cancelled

    const result = target.takeDamage(skill.power);
    await this.onDamaged?.({ target, result });
  }
}
```

The Orchestrator script still reads top-to-bottom. "Wait for player" is just another `await`.

## 3. Headless tests

Logic entities have no hooks and no engine deps, so they test trivially:

```ts
test("damage reduces hp and never goes negative", () => {
  const u = new BattleUnit({ hp: 10, maxHp: 100, atk: 0 });
  u.receiveDamage(50, attacker);
  expect(u.hp).toBe(0);
  expect(u.isDead()).toBe(true);
});
```

Test the Orchestrator's flow without a view by binding mock hooks:

```ts
test("fires onUnitDied when target hp reaches 0", async () => {
  const o = new BattleOrchestrator();
  o.loadUnits([attacker, target]);

  let fired = false;
  o.onUnitDied = async ({ unit }) => {
    fired = true;
    expect(unit).toBe(target);
  };

  await o.processAttack(attacker, target);
  expect(fired).toBe(true);
});
```

You can run an entire scenario without the engine. If a test cannot run because logic imports engine APIs or talks to EventBus, the separation is leaking. Fix the leak — do not mock the engine.

## 4. Hook-safety guards

Between an `await` and the next line, the scene may have torn down or the view may have thrown. Three guards keep the script honest.

### View checks its own teardown after each `await`

```ts
o.onDamaged = async ({ target, result }) => {
  const v = this.unitViews.get(target);
  await v.playAnimation("hurt");
  if (this.disposed) return;
  this.hud.updateHpBar(target, result.remainingHp, result.maxHp);
};
```

`disposed` is a flag the view sets on `unbind()`. Whatever the engine's "is this still alive" check is, use that — the principle is the same.

### Orchestrator wraps fires so a buggy view does not corrupt logic

```ts
private async fire<T>(hook: ((data: T) => Promise<void> | void) | undefined, data: T): Promise<void> {
    if (!hook) return;
    try { await hook(data); }
    catch (e) { console.error('[Orchestrator] hook threw:', e); }
}

await this.fire(this.onUnitDamaged, { unit: target, result });
```

Logic state has already been mutated by the time the hook fires. A throwing view should not stop the game flow.

### No re-entrant hooks

If a hook body causes another logic step (cascading deaths), let the Orchestrator drive the chain serially in its own loop. Do not call hooks from inside hooks.

## 5. Pooled / reused entity views

When entity views are reused (deactivated and recycled, not destroyed), unbind on deactivate and rebind on activate so a recycled view never receives stale lambdas:

```ts
class UnitView {
  private orchestrator: BattleOrchestrator | null = null;
  private bound = false;

  bind(o: BattleOrchestrator): void {
    this.orchestrator = o;
    this.attach();
  }

  unbind(): void {
    if (!this.orchestrator) return;
    this.detach();
    this.orchestrator = null;
  }

  onActivate(): void {
    if (this.orchestrator && !this.bound) this.attach();
  }
  onDeactivate(): void {
    if (this.bound) this.detach();
  }

  private attach(): void {
    // assign hook lambdas
    this.bound = true;
  }

  private detach(): void {
    // clear hook lambdas
    this.bound = false;
  }
}
```

Wire `onActivate` / `onDeactivate` into whatever activate/deactivate callback the engine provides. Destroyed (not pooled) views just need `unbind()` on destroy.

## 6. Migrating from EventBus

When a class mixes gameplay state, EventBus emits, and view updates, the goal is to extract one Orchestrator method that reads top-to-bottom.

### Step 1 — List the moments

Read the old code and list each _gameplay moment_ — discrete events like "unit takes damage", "match succeeds", "tile falls". Each moment becomes one Orchestrator method.

### Step 2 — Separate logic from view per moment

Highlight every line that mutates gameplay state (hp, position, score, board). Test each: "would a headless server need this?" Lines that pass go to the logic entity. Lines that fail (animation, sound, camera) belong in the view binding.

### Step 3 — Extract result types

Bundle everything the view needs into a result object. The view receives the result; it does not query the entity back.

```ts
// before
this.hp -= damage;
this.hpBar.progress = this.hp / this.maxHp;
this.spawnDamageNumber(damage);
EventBus.emit("unit_damaged", { unit: this, value: damage });

// after
const result = unit.receiveDamage(damage, attacker); // logic
await this.onUnitDamaged?.({ unit, result }); // Orchestrator
// view hook updates hpBar and damage number
```

### Step 4 — Reflow each EventBus chain as a sequential script

```ts
// before — fan-out via EventBus
EventBus.emit('match_success', { tile1, tile2, path });
// listeners elsewhere: tileView, scoreSystem, cover system, win check…

// after — Orchestrator method, top-to-bottom
async processMatch(t1: Tile, t2: Tile): Promise<void> {
    const path = this.board.findPath(t1, t2);
    if (!path) {
        await this.onMatchFailed?.({ t1, t2, reason: 'no_path' });
        return;
    }
    const result = this.board.removeMatch(t1, t2, path);
    await this.onMatchSuccess?.({ result });

    for (const cover of result.brokeCovers) {
        await this.onCoverBroken?.({ tile: cover.tile, kind: cover.kind });
    }

    if (this.board.isCleared()) {
        await this.onWon?.({ score: this.score });
    }
}
```

### Step 5 — Move view code to `bind()`

Each old EventBus listener becomes one hook lambda inside `view.bind(orchestrator)`. The view's bind body is where cross-system response sequencing now lives.

### Step 6 — Verify headless

Comment out `view.bind()` and run the orchestrator. If it executes without error and you can detect the moment via mock hooks, the separation is correct. If it crashes on an engine import or a missing EventBus listener, find the leak.

### Common pitfalls

- **Hook on the entity** — the most common mistake. Move to the Orchestrator.
- **EventBus inside logic** — replace with a `return` value the Orchestrator can use.
- **`setTimeout` / scheduled delays in the original code** — those were animation timing dodges. Replace with `await` on the hook.
- **View mutating logic state** — view must only READ from result objects. Logic owns state.
- **Engine singletons in logic** — anything like "find current scene" / "get root node" inside a logic class is a view dependency. Move it to the view layer.
- **Forgotten `await`** — on a `Promise<void>` hook, missing the `await` is a silent race. Audit during code review.
