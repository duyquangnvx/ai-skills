# Common Mistakes

## 1. Runtime state leaks into AppState

```typescript
// ❌ Timer, board, combo — không cần save, làm AppState phình to
class AppState {
    remainingSeconds: number = 60;   // runtime
    currentBoard: Tile[][] = [];     // runtime, không serializable tốt
    currentCombo: number = 0;        // runtime
    selectedTile: Tile | null = null; // runtime
}

// ✅ Chỉ kết quả của gameplay mới vào AppState
class AppState {
    levelResults: Record<number, LevelSaveData> = {};  // persistent
}

// Timer, board, combo vẫn nằm trong OnetPuzzleGame như cũ
class OnetPuzzleGame {
    private timer: Timer;
    private board: Board;
    private scoreManager: ScoreManager;
}
```

**Dấu hiệu:** AppState có field không thể JSON.stringify được (object phức tạp, circular reference) → đó là runtime state.

---

## 2. System giữ bản copy riêng của persistent field

```typescript
// ❌ BoosterManager cache lại inventory — mất sync với AppState
class BoosterManager {
    private inventory: BoosterInventory;  // copy riêng

    constructor(appState: AppState) {
        this.inventory = { ...appState.boosters };  // shallow copy → desync
    }

    spendBooster(type: BoosterType): void {
        this.inventory[type]--;
        // appState.boosters không được update → save sẽ lưu giá trị cũ
    }
}

// ✅ Đọc/ghi trực tiếp vào AppState
class BoosterManager {
    constructor(private appState: AppState) {}

    spendBooster(type: BoosterType): void {
        this.appState.boosters[type]--;  // AppState luôn là source of truth
    }
}
```

---

## 3. Save trong update loop hoặc quá thường xuyên

```typescript
// ❌ Save mỗi frame — tốn I/O, block main thread
update(dt: number): void {
    this.timer.update(dt);
    this.saveSystem.save(this.appState);  // đừng
}

// ❌ Save sau mỗi click nhỏ
onTileTapped(): void {
    this.matcher.selectTile(pos);
    this.saveSystem.save(this.appState);  // quá thường xuyên
}

// ✅ Save tại các checkpoint có ý nghĩa
onLevelComplete(): void { this.saveSystem.save(this.appState); }
onPurchaseComplete(): void { this.saveSystem.save(this.appState); }
onBoosterBought(): void { this.saveSystem.save(this.appState); }
onQuestClaimed(): void { this.saveSystem.save(this.appState); }
onAppPause(): void { this.saveSystem.save(this.appState); }  // Cocos onApplicationDidEnterBackground
```

---

## 4. Không có schema versioning

```typescript
// ❌ Không có version — không biết old save trông như thế nào
class AppState {
    coins: number = 0;
    // ...
}

// Sau update, đổi cấu trúc boosters → old save crash khi load
```

```typescript
// ✅ Luôn có schemaVersion, migrate trước khi dùng
class AppState {
    readonly schemaVersion: number = 2;  // bump khi cấu trúc thay đổi
    // ...
}
```

**Khi nào bump version:**
- Đổi tên field
- Thay đổi kiểu dữ liệu (string → number, flat → nested)
- Xóa field quan trọng và cần xử lý giá trị cũ

**Không cần bump version:**
- Thêm field mới với default value (`Object.assign` tự fill)
- Xóa field không quan trọng (old save giữ field thừa, không ảnh hưởng)

---

## 5. Không wrap save/load trong try/catch

```typescript
// ❌ LocalStorage có thể fail (private mode, storage full)
load(): AppState {
    return JSON.parse(LocalStorage.get('save'));  // crash nếu null hoặc JSON lỗi
}

// ✅ Fallback về fresh state nếu có lỗi
load(): AppState {
    try {
        const raw = LocalStorage.get('save');
        if (!raw) return new AppState();
        return this.migrate(JSON.parse(raw));
    } catch (e) {
        console.error('[SaveSystem] Load failed, using defaults:', e);
        return new AppState();
    }
}
```

---

## 6. Nhiều nơi tạo AppState mới thay vì dùng chung instance

```typescript
// ❌ Mỗi system tự load state riêng → không đồng bộ
class ShopSystem {
    private state = new SaveSystem().load();  // bản riêng
}
class QuestSystem {
    private state = new SaveSystem().load();  // bản riêng khác
}
// ShopSystem mua item → QuestSystem không thấy thay đổi

// ✅ Load một lần ở entry point, inject vào tất cả
class GameApp {
    onLoad(): void {
        const appState = new SaveSystem().load();  // một lần duy nhất
        this.shopSystem  = new ShopSystem(appState);
        this.questSystem = new QuestSystem(appState);
        // Cùng object reference → mọi thay đổi đều visible
    }
}
```

---

## 7. AppState chứa class instance thay vì plain data

```typescript
// ❌ Class instance không serialize được sạch
class AppState {
    levelResults: Map<number, LevelSaveData> = new Map();  // Map không JSON.stringify tốt
}

// JSON.stringify(new Map([[1, {stars: 3}]])) → '{}'  // mất data!

// ✅ Dùng plain object / array
class AppState {
    levelResults: Record<number, LevelSaveData> = {};  // plain object → serialize tốt
}
```

Tương tự với `Set` — dùng `number[]` hoặc `Record<string, boolean>` thay thế.