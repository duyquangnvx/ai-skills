---
name: lifecycle-delegate
description: "Pattern for separating game logic from view/presentation layer using lifecycle callbacks. Use this skill whenever Claude needs to help with: (1) Architecting logic-view separation in game code, (2) Writing game entities/models that can run headless without views, (3) Designing callback hooks between gameplay logic and animation/UI, (4) Refactoring tightly-coupled game code where logic and visuals are mixed, (5) Making game logic testable or reusable across client/server, (6) Designing turn-based or sequential gameplay where logic must await animation completion. Trigger on phrases like 'separate logic and view', 'logic không phụ thuộc view', 'await animation', 'headless game logic', 'tách logic ra khỏi component', 'lifecycle hook', 'callback pattern game'. Also trigger when reviewing game code that has gameplay calculations mixed with cc.tween, spine animation calls, or UI updates inside the same class."
---

# Lifecycle Delegate Pattern for Game Development

Tách logic khỏi view bằng lifecycle callbacks — logic định nghĩa các "mốc" trong vòng đời, view hook vào để diễn.

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

**Logic chạy được không cần view.** Callback là optional (`?.()` skip khi undefined).
**View không chứa gameplay logic.** View chỉ nhận data và quyết định diễn thế nào.
**Flow control qua Promise.** Logic `await` callback khi cần chờ animation xong.

## When to Apply

Use this pattern when:
- Entity có cả gameplay logic lẫn visual representation
- Logic cần chờ animation xong mới tiếp tục (turn-based, skill sequence)
- Cần chạy logic headless (server, unit test, AI simulation)
- Muốn swap view mà không đổi logic (2D → 3D, change art style)

Do NOT use for:
- Cross-system broadcast (entity chết → notify quest, analytics) → dùng Event Bus
- Pure UI không gắn gameplay logic (settings menu, lobby UI)
- Realtime physics-driven gameplay nơi logic và visual không thể tách rõ

## Callback Granularity Rules

**Mỗi callback = 1 "nhịp" gameplay mà view cần diễn.** Không phải mỗi field thay đổi.

### ❌ Quá nhỏ — view phải tự ráp logic từ mảnh vụn

```typescript
onHpChanged?: (hp: number) => void;
onShieldChanged?: (shield: number) => void;
onCritTriggered?: () => void;
onKnockback?: (dir: Vec3) => void;
onDamageNumberSpawn?: (val: number) => void;
```

Vấn đề: view nhận 5 callback riêng lẻ cho MỘT lần bị đánh, phải tự ráp thứ tự diễn,
dễ race condition, khó biết mấy callback thuộc cùng một "nhịp".

### ❌ Quá to — view phải diff toàn bộ state

```typescript
onChanged?: (state: FullUnitState) => void;
```

Vấn đề: gọi cho mọi thay đổi, view không biết nên diễn hurt anim hay buff anim,
phải diff old vs new state mỗi frame, tốn performance.

### ✅ Đúng mức — mỗi callback là một "moment" gameplay

```typescript
onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
```

`DamageResult` chứa đủ context (damage, crit, shield, knockback). View nhận 1 object,
tự quyết diễn thế nào.

### Luôn wrap params trong data object

```typescript
// ❌ Positional params — thêm field = break tất cả callback đang bind
onTakeDamage?: (result: DamageResult) => Promise<void>;
// Sau này cần thêm sourceSkillId → phải sửa thành:
onTakeDamage?: (result: DamageResult, sourceSkillId: string) => Promise<void>;
// → TẤT CẢ view đang bind phải sửa signature

// ✅ Data object — thêm field không break gì
onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
// Sau này thêm field:
onTakeDamage?: (data: { result: DamageResult; sourceSkillId?: string }) => Promise<void>;
// → View cũ vẫn chạy bình thường, chỉ view nào cần field mới mới dùng
```

Nguyên tắc: **mọi callback đều nhận đúng 1 argument là data object**, kể cả khi hiện tại
chỉ có 1 field. Chi phí wrapper gần như zero, nhưng tiết kiệm rất nhiều refactor sau này.

### Checklist tự kiểm tra

- [ ] View có phải listen nhiều callback rồi gom lại mới đủ info để diễn 1 animation? → gom callback lại
- [ ] Thêm feature nhỏ ở logic phải thêm callback mới? → abstraction đang leak
- [ ] Callback chỉ forward 1 field thay đổi mà không mang "ý nghĩa gameplay"? → đang observe data, không phải lifecycle
- [ ] Một entity phức tạp có quá 10 hooks? → cân nhắc gom lại
- [ ] View phải diff full state để biết diễn gì? → cần tách thêm callback theo "moment"

## Implementation Guide

### Step 1: Define Result Types

Gom đủ context vào data objects. View nhận 1 object, không cần hỏi ngược logic.

```typescript
// Mỗi result type = 1 "nhịp" gameplay
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
    // ~5-8 hooks cho một entity phức tạp
    onEnterBattle?: () => void;
    onTurnStart?: () => Promise<void>;
    onSkillCast?: (data: { info: SkillCastInfo }) => Promise<void>;
    onTakeDamage?: (data: { result: DamageResult }) => Promise<void>;
    onHealed?: (data: { result: HealResult }) => void;
    onBuffsChanged?: (data: { buffs: ReadonlyArray<Buff> }) => void;
    onDeath?: () => Promise<void>;

    // Logic methods gọi hook ở đúng thời điểm
    async receiveDamage(raw: number, element: ElementType, attacker: BattleUnit) {
        // ... tính toán damage, shield, crit ...
        const result: DamageResult = { /* gom hết vào đây */ };

        this.hp = Math.max(0, this.hp - result.value);
        await this.onTakeDamage?.({ result });  // view diễn, logic chờ

        if (this.hp <= 0) {
            await this.onDeath?.();
            EventBus.emit('unit_died', this.id);  // broadcast cho system khác
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
        // logic unit có thể vẫn tồn tại cho replay/history
    }
}
```

## Choosing Promise vs Fire-and-Forget

| Situation | Return type | Reason |
|-----------|-------------|--------|
| Logic phải chờ animation xong | `Promise<void>` | `await` để sequence đúng |
| Logic tiếp tục ngay, view diễn nền | `void` | Không block game flow |
| Logic cần kết quả từ view (hiếm) | `Promise<T>` | Ví dụ: user chọn target |

Rule of thumb: **dùng Promise khi thứ tự gameplay matters**, fire-and-forget khi chỉ là visual feedback.

## Lifecycle vs Event Bus: Where to Draw the Line

```
onTakeDamage  ──→  lifecycle callback (view CỦA entity này diễn hurt)
unit_died     ──→  event bus (quest system, sound manager, camera shake)

onSkillCast   ──→  lifecycle callback (view CỦA caster diễn cast anim)
skill_used    ──→  event bus (combo tracker, cooldown UI, analytics)
```

**Lifecycle callback:** quan hệ 1:1 giữa logic và view của CÙNG entity.
**Event bus:** broadcast 1:N cho các system KHÔNG liên quan trực tiếp.

Xem chi tiết và ví dụ nâng cao trong:
- `references/advanced-patterns.md` — multi-entity sequences, object pooling, replay
- `references/common-entities.md` — template hooks cho các entity type phổ biến trong game
