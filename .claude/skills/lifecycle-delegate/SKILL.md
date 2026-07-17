---
name: lifecycle-delegate
description: "Use when gameplay flow is hard to read because logic is scattered across EventBus listeners and animation timing; when you want a turn-based or sequential game flow to read as a top-to-bottom script that awaits animations between steps; when refactoring code that interleaves gameplay state with animation, sound, or UI updates; when deciding where hooks belong between game logic and the view; when writing testable headless game logic. Triggers: 'replace EventBus with hooks', 'read game flow as a script', 'await animation', 'orchestrator pattern', 'where to put callbacks', 'separate logic and view', 'unit test game logic', 'headless game logic'."
---

# Lifecycle Delegate Pattern

A pattern for writing turn-based / sequential gameplay so the **flow reads as a script from top to bottom** — and so logic runs headlessly without the engine.

## Why this pattern exists

EventBus turns gameplay into a fan-out web. Reading a method tells you nothing about what happens next — you grep an event name, find five listeners that may run in any order, each with its own delay to dodge the others. Animation timing is implicit. Adding a step means adding another listener somewhere else.

Two moves fix it:

1. **Concentrate flow in one method on an Orchestrator.** Reading top-to-bottom shows the entire moment: act → animate → resolve → check end. No grep needed.
2. **`await` hooks for the in-between view work.** Order is explicit in code, not implicit in timing. Logic gates on the view finishing, not on a guessed delay.

EventBus is no longer the spine of gameplay. It survives only for fire-and-forget side channels (analytics, achievements, ambient audio).

## The reading test

The pattern's value reduces to one question: **can a new reader open the Orchestrator method and see the whole moment?**

### Before — EventBus spaghetti

```ts
// in BattleUnit
receiveDamage(raw: number): void {
    this.hp = Math.max(0, this.hp - raw);
    EventBus.emit('unit_damaged', { unit: this, value: raw });
    if (this.hp <= 0) EventBus.emit('unit_died', { unit: this });
}

// What runs after damage? Grep 'unit_damaged' across the project:
//   UnitView   — plays hurt anim
//   HUD        — updates HP bar (after 50ms? before? race)
//   Sound      — plays SFX
//   Quest      — records progress
//   Camera     — shakes (only sometimes — has its own filter)
// Order between them: undefined. Timing: implicit, fragile.
// What runs after death? Grep 'unit_died'. Repeat.
```

### After — Orchestrator script

```ts
async processAttack(attacker: BattleUnit, target: BattleUnit): Promise<void> {
    const result = target.receiveDamage(attacker.atk, attacker);
    await this.onUnitDamaged?.({ unit: target, result });

    if (target.isDead()) {
        await this.onUnitDied?.({ unit: target });
        this.removeUnit(target);
        if (this.enemies.length === 0) {
            await this.onBattleWon?.({ score: this.score });
        }
    }
}
```

A new reader sees the whole moment in 10 lines. The view binds the hooks elsewhere — the **flow** lives here, in order, awaited.

## The three layers

```
Logic Entity  ── result ──→  Orchestrator  ── hook ──→  View
  pure data                  the script               binds lambdas
  no engine                  awaits view              animates / UI / sound
  no hooks                   owns flow                one Orchestrator ↔ one View
```

- **Logic entities** have no hooks and no engine deps. They mutate state and return result objects. They run in plain Node with no view.
- **Orchestrator** owns the flow. Its methods read like a script. Hooks are how it pauses for the view between steps.
- **View** binds lambdas to the Orchestrator's hooks. It is where engine APIs (animation, tween, audio, scene graph) live.

## When to use

Use it when **all** are true:

- Gameplay is **turn-based or sequential** — logic can pause for the view between steps
- A single moment triggers **multiple systems in a defined order** (animate → HUD → sound → camera → check end)
- You want the flow to be **debuggable by reading one method**, not by tracing event listeners

Do NOT use it for:

- **Real-time loops** (action, shooter, autoplay, physics) — logic runs on a fixed timestep and cannot await per-frame.
- **Pure data sync** — view mirrors a value (HP bar, timer, currency). Use a getter, not a hook. Hooks are for _moments_, not _state_.
- **Trivial UI** — a button opening a popup does not need an Orchestrator.

## When to add a hook

Add a hook **if and only if** the Orchestrator method has to pause between two lines and the pause depends on view work the Orchestrator cannot inline. The hook exists to make `await` legible inside the script.

| Situation                                                             | Hook?                         |
| --------------------------------------------------------------------- | ----------------------------- |
| Orchestrator must wait for animation before next logic step           | ✅ `Promise<void>`            |
| Several systems react to the same moment in a defined order           | ✅ — view body sequences them |
| Only one system reacts and the Orchestrator does not need to wait     | ❌ Direct method call         |
| Visual feedback that does not gate flow (e.g. floating damage number) | ❌ Direct method call         |
| View needs to mirror a value continuously                             | ❌ Getter, view polls         |

**Test for over-hooking:** delete the hook, replace with a direct method call. If the script still reads correctly and timing still works, the hook was unnecessary.

## Implementation

A complete pattern instance has five parts. The order below is the order a new reader should scan them — lead with the Orchestrator, because that is what makes the pattern legible.

### 1. Orchestrator — the script

```ts
class BattleOrchestrator {
  onUnitDamaged?: (data: {
    unit: BattleUnit;
    result: DamageResult;
  }) => Promise<void>;
  onUnitDied?: (data: { unit: BattleUnit }) => Promise<void>;
  onBattleWon?: (data: { score: number }) => Promise<void>;
  onBattleLost?: (data: { reason: "timeout" | "wiped" }) => Promise<void>;

  async processAttack(attacker: BattleUnit, target: BattleUnit): Promise<void> {
    const result = target.receiveDamage(attacker.atk, attacker);
    await this.onUnitDamaged?.({ unit: target, result });

    if (target.isDead()) {
      await this.onUnitDied?.({ unit: target });
      this.removeUnit(target);
      await this.checkEnd();
    }
  }

  private async checkEnd(): Promise<void> {
    if (this.enemies.length === 0) {
      await this.onBattleWon?.({ score: this.score });
    }
  }
}
```

### 2. Logic entity — pure, returns results

```ts
class BattleUnit {
  hp: number;
  maxHp: number;
  atk: number;

  receiveDamage(raw: number, attacker: BattleUnit): DamageResult {
    const isCrit = Math.random() < 0.2;
    const value = isCrit ? raw * 2 : raw;
    this.hp = Math.max(0, this.hp - value);
    return { value, isCrit, remainingHp: this.hp, maxHp: this.maxHp };
  }

  isDead(): boolean {
    return this.hp <= 0;
  }
}
```

The entity has no hooks, no engine imports, no `EventBus.emit`. It runs in a plain Node test.

### 3. Result type — bundle full context

```ts
interface DamageResult {
  value: number;
  isCrit: boolean;
  remainingHp: number;
  maxHp: number;
}
```

The view receives the full result and never queries the entity back. Adding an optional field is non-breaking.

### 4. View — binds hooks, runs cross-system response

```ts
class BattleView {
  private orchestrator: BattleOrchestrator | null = null;

  constructor(
    private unitViews: UnitViewRegistry,
    private hud: Hud,
    private sound: Sound,
    private camera: Camera
  ) {}

  bind(o: BattleOrchestrator): void {
    this.orchestrator = o;

    o.onUnitDamaged = async ({ unit, result }) => {
      const v = this.unitViews.get(unit);
      await v.playAnimation("hurt");
      this.hud.updateHpBar(unit, result.remainingHp, result.maxHp);
      this.hud.spawnDamageNumber(result.value, result.isCrit);
      this.sound.play("hurt");
      this.camera.shake(0.2);
    };

    o.onUnitDied = async ({ unit }) => {
      const v = this.unitViews.get(unit);
      await v.playAnimation("death");
      await v.fadeOut(0.5);
      this.sound.play("death");
    };

    o.onBattleWon = async ({ score }) => {
      await this.hud.showVictory(score);
    };
  }

  unbind(): void {
    if (!this.orchestrator) return;
    this.orchestrator.onUnitDamaged = undefined;
    this.orchestrator.onUnitDied = undefined;
    this.orchestrator.onBattleWon = undefined;
    this.orchestrator.onBattleLost = undefined;
    this.orchestrator = null;
  }
}
```

Engine binding: call `bind()` when the view is created, call `unbind()` when the view is torn down. The exact lifecycle method depends on the engine — wire it into whatever "destroyed" / "disabled" callback the engine provides.

### 5. Scene wires it together

```ts
const orchestrator = new BattleOrchestrator();
const view = new BattleView(unitViews, hud, sound, camera);

view.bind(orchestrator);
orchestrator.loadLevel(config);
await orchestrator.startBattle();

// On scene teardown:
view.unbind();
```

## Hook signatures

### Always wrap params in a data object

```ts
// ❌ Positional — adding a field breaks every binding
onUnitDamaged?: (unit: BattleUnit, result: DamageResult) => Promise<void>;

// ✅ Data object — adding an optional field breaks nothing
onUnitDamaged?: (data: { unit: BattleUnit; result: DamageResult }) => Promise<void>;
```

### `Promise<void>` vs `void`

| Signature       | Meaning                              | Use when                                     |
| --------------- | ------------------------------------ | -------------------------------------------- |
| `Promise<void>` | Orchestrator awaits before next line | Animation must finish first                  |
| `void`          | Orchestrator fires and forgets       | Pure visual feedback that does not gate flow |
| `Promise<T>`    | View returns a value to logic        | Player picks a target, etc. (rare)           |

The signature is a contract: a `Promise<void>` hook tells the reader "this gates the flow."

### Naming

Use past-tense verbs on the moment that already happened in logic: `onUnitDamaged`, `onMatchSucceeded`, `onLevelLoaded`. Never name a hook for a future intent (`onAboutToDie`, `onWillDamage`) — that confuses logic and view boundaries.

## EventBus is the exception

Default = hook. EventBus is reserved for genuinely fire-and-forget side channels that have nothing to do with gameplay flow:

- Analytics / telemetry
- Achievement tracker (background)
- Ambient audio / music director

Everything that participates in the gameplay moment — animation, HUD, sound, camera, quest progress — goes through hooks. Otherwise the script becomes unreadable again.

```ts
private async handleUnitDied(unit: BattleUnit): Promise<void> {
    await this.onUnitDied?.({ unit });           // ordered, awaited gameplay
    EventBus.emit('unit_died', { unit });        // background side channels only
}
```

Logic entities **must not** call EventBus. The Orchestrator is the only emitter. This keeps logic headless-testable and the script readable.

## Cross-domain flow — `SceneFlow`

When a flow crosses domains (battle won → unlock map node → save profile), each domain has its own Orchestrator but the _cross-domain_ flow needs a script too. Promote a `SceneFlow` at scene level — an Orchestrator-of-Orchestrators:

```ts
class AdventureSceneFlow {
  onStageCleared?: (data: { stage: number; score: number }) => Promise<void>;

  constructor(
    private battle: BattleOrchestrator,
    private map: MapOrchestrator,
    private profile: ProfileOrchestrator
  ) {}

  async runStage(stage: number): Promise<void> {
    const result = await this.battle.runBattle(stage);
    if (!result.won) return;

    await this.map.unlockNext(stage);
    await this.profile.recordWin(stage, result.score);
    await this.onStageCleared?.({ stage, score: result.score });
    await this.profile.save();
  }
}
```

Same rule: read top-to-bottom. Do not glue domains with EventBus — that defeats the readability goal.

## Self-check (measure the goal)

- [ ] Can a new reader open the Orchestrator method and see the whole moment without opening another file?
- [ ] Is anything about gameplay flow (ordering, timing, win/lose) discoverable only via `EventBus.emit` or `EventBus.on`? → that part should be a hook.
- [ ] Is there a hook the Orchestrator never `await`s and never reads a return from? → it is a disguised method call. Drop the hook, call directly.
- [ ] Is there a hook only the View reacts to where the Orchestrator does not need to wait? → also a disguised method call.
- [ ] Does a logic entity import engine APIs, call `EventBus`, or expose hooks? → push that out. Logic must be headless.
- [ ] Does the flow cross multiple Orchestrators glued by EventBus? → introduce a `SceneFlow`.

## More patterns

For multi-target sequencing, request-response hooks (player input), headless tests, hook-safety guards, pooled-entity rebind, and a step-by-step migration from EventBus, see `references/extensions.md`.
