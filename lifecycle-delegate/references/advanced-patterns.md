# Advanced Lifecycle Delegate Patterns

## Table of Contents

1. [Multi-Entity Sequences](#multi-entity-sequences)
2. [Object Pooling with Bind/Unbind](#object-pooling)
3. [Replay & Headless Mode](#replay-and-headless)
4. [Nested Lifecycles](#nested-lifecycles)
5. [Error Handling in Async Hooks](#error-handling)
6. [Testing Logic Without View](#testing)

---

## Multi-Entity Sequences

Khi một skill ảnh hưởng nhiều target, cần quyết định diễn tuần tự hay song song.

### Sequential — turn-based, mỗi hit diễn rõ ràng

```typescript
class BattleUnit {
    async castSkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);
        this.consumeMp(skill.mpCost);

        // Caster diễn cast animation
        await this.onSkillCast?.({ info: { skillId, targets } });

        // Từng target nhận damage tuần tự — mỗi target diễn hurt xong mới tới target kế
        for (const target of targets) {
            await target.receiveDamage(skill.damage, skill.element, this);
        }
    }
}
```

### Parallel — AoE, tất cả target diễn cùng lúc

```typescript
class BattleUnit {
    async castAoESkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);
        await this.onSkillCast?.({ info: { skillId, targets } });

        // Tất cả target nhận damage song song
        await Promise.all(
            targets.map(t => t.receiveDamage(skill.damage, skill.element, this))
        );
    }
}
```

### Mixed — cast tuần tự, nhưng AoE damage song song

```typescript
class BattleUnit {
    async castMultiHitSkill(skillId: string, targets: BattleUnit[]) {
        const skill = SkillDB.get(skillId);

        // Phase 1: cast anim (tuần tự)
        await this.onSkillCast?.({ info: { skillId, targets } });

        // Phase 2: mỗi hit tuần tự, nhưng mỗi hit ảnh hưởng tất cả target song song
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

Khi entity được tái sử dụng (ví dụ quái trong wave-based game), view phải unbind/rebind.

```typescript
class EnemyPool {
    private pool: Node[] = [];
    private activeViews: Map<string, EnemyView> = new Map();

    spawn(unit: BattleUnit): EnemyView {
        const node = this.pool.pop() ?? instantiate(this.prefab);
        const view = node.getComponent(EnemyView);

        view.bind(unit);   // hook callbacks
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

        view.unbind();      // QUAN TRỌNG: tháo hết callback trước khi recycle
        view.reset();       // reset visual state
        this.activeViews.delete(unit.id);
        this.pool.push(view.node);
    }
}
```

**Quan trọng:** `unbind()` phải clear TẤT CẢ callback. Nếu quên, logic entity mới sẽ
gọi callback trên view cũ đã bị recycle → bug rất khó trace.

```typescript
class EnemyView extends Component {
    unbind() {
        if (!this.unit) return;
        // Clear tất cả — không được quên cái nào
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

Để tránh quên clear callback, dùng helper gom tất cả hook names:

```typescript
// Logic entity base class
abstract class GameEntity {
    // Khai báo tất cả hook names để hỗ trợ auto-clear
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

// View chỉ cần gọi 1 dòng
class EnemyView extends Component {
    unbind() {
        this.unit?.clearAllHooks();
        this.unit = null;
    }
}
```

---

## Replay and Headless

Lợi thế lớn nhất của pattern: logic chạy hoàn toàn không cần view.

### Headless simulation (server hoặc AI)

```typescript
// Không có view, tất cả callback undefined → skip hết qua optional chaining
const battle = new BattleSimulation();
battle.addUnit(new BattleUnit(heroData));   // không bind view
battle.addUnit(new BattleUnit(enemyData));

// Logic chạy bình thường, await resolve ngay vì callback undefined
// undefined?.() returns undefined, await undefined resolves immediately
await battle.run();

console.log(battle.getResult()); // ai thắng, bao nhiêu turn, damage dealt...
```

### Replay — record actions, replay với view

```typescript
interface BattleAction {
    type: 'skill' | 'item' | 'move';
    actorId: string;
    targetIds: string[];
    data: any;
    timestamp: number;
}

class BattleReplay {
    // Phát lại từ action log — logic tính lại, view diễn lại
    async replay(actions: BattleAction[], scene: BattleScene) {
        for (const action of actions) {
            const actor = scene.getUnit(action.actorId);
            const targets = action.targetIds.map(id => scene.getUnit(id));

            switch (action.type) {
                case 'skill':
                    // Logic tính damage lại, view diễn animation
                    await actor.castSkill(action.data.skillId, targets);
                    break;
                case 'item':
                    await actor.useItem(action.data.itemId, targets[0]);
                    break;
            }
        }
    }

    // Fast-forward: chạy headless rồi apply final state
    async fastForward(actions: BattleAction[], scene: BattleScene) {
        // Unbind tất cả view
        scene.unbindAllViews();

        // Chạy logic headless — không có animation, chạy instant
        for (const action of actions) {
            const actor = scene.getUnit(action.actorId);
            const targets = action.targetIds.map(id => scene.getUnit(id));
            if (action.type === 'skill') {
                await actor.castSkill(action.data.skillId, targets);
            }
        }

        // Rebind view, apply final state
        scene.rebindAllViews();
    }
}
```

---

## Nested Lifecycles

Khi entity chứa sub-entities (ví dụ: team chứa units, unit chứa equipment).

```typescript
class BattleTeam {
    onTeamTurnStart?: () => Promise<void>;
    onTeamDefeated?: () => Promise<void>;

    private units: BattleUnit[] = [];

    async startTurn() {
        await this.onTeamTurnStart?.();

        for (const unit of this.getAliveUnits()) {
            await unit.startTurn();  // unit có lifecycle riêng
        }
    }

    // Khi unit chết, kiểm tra team còn ai không
    setupUnitDeathWatch(unit: BattleUnit) {
        const originalOnDeath = unit.onDeath;

        unit.onDeath = async () => {
            await originalOnDeath?.();  // view diễn death anim trước

            if (this.getAliveUnits().length === 0) {
                await this.onTeamDefeated?.();  // team-level lifecycle
            }
        };
    }
}
```

**Lưu ý:** wrapping callback như trên cần cẩn thận thứ tự. Nếu view bind SAU khi
`setupUnitDeathWatch`, view sẽ overwrite `onDeath` → mất team death check.
Giải pháp: dùng callback array thay vì single callback (xem phần dưới).

### Multi-listener variant (khi cần)

Khi nhiều nơi cần hook vào cùng một lifecycle event:

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
}

// Sử dụng
class BattleUnit {
    readonly onDeath = new LifecycleHook<() => Promise<void>>();

    async die() {
        await this.onDeath.invoke();  // tất cả listener chạy tuần tự
        EventBus.emit('unit_died', this.id);
    }
}

// View hook
unit.onDeath.add(async () => { await view.playDeathAnim(); });
// Team hook
unit.onDeath.add(async () => { team.checkDefeat(); });
```

**Khi nào dùng multi-listener vs single callback:**
- Single callback (default): đủ cho 90% trường hợp, đơn giản, rõ ownership
- Multi-listener: khi cùng entity cần phục vụ nhiều concern (view + team + buff system)

---

## Error Handling

Callback từ view có thể throw (ví dụ: node bị destroy giữa chừng). Logic phải robust.

```typescript
class BattleUnit {
    async receiveDamage(raw: number, element: ElementType, attacker: BattleUnit) {
        const result = this.calculateDamage(raw, element, attacker);
        this.hp = Math.max(0, this.hp - result.value);

        // View có thể crash — logic vẫn phải tiếp tục
        try {
            await this.onTakeDamage?.({ result });
        } catch (e) {
            console.warn(`View callback failed for unit ${this.id}:`, e);
            // Logic tiếp tục bình thường — game không crash vì view lỗi
        }

        if (this.hp <= 0) {
            try {
                await this.onDeath?.();
            } catch (e) {
                console.warn(`Death callback failed for unit ${this.id}:`, e);
            }
            EventBus.emit('unit_died', this.id);
        }
    }
}
```

### Timeout guard — tránh view treo logic mãi mãi

```typescript
function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
    return Promise.race([
        promise,
        new Promise<T>((_, reject) =>
            setTimeout(() => reject(new Error(`Timeout: ${label} took > ${ms}ms`)), ms)
        ),
    ]);
}

// Sử dụng
await withTimeout(
    this.onTakeDamage?.({ result }) ?? Promise.resolve(),
    5000,
    `onTakeDamage unit ${this.id}`
);
```

---

## Testing

Logic chạy headless → test dễ, không cần mock engine.

```typescript
describe('BattleUnit.receiveDamage', () => {
    it('should reduce hp and trigger onTakeDamage', async () => {
        const unit = new BattleUnit({ hp: 100, maxHp: 100, def: 10 });
        const receivedResults: DamageResult[] = [];

        // "View" chỉ là 1 callback ghi log
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
        // Không bind callback nào
        const attacker = new BattleUnit({ atk: 50 });

        // Không throw, không crash
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
});
```
