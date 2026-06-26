# Convention: Delegate Pattern vs Event Bus trong Game Dev

> Áp dụng Cocoa delegation pattern (mở rộng sang `async` TypeScript) cho game,
> và xác định rạch ròi khi nào dùng delegate, khi nào dùng event bus.
> Tài liệu này là bản game-dev của pattern delegation tổng quát: nó thêm vào phần
> mà bản gốc chưa có — game loop, orchestrator, gateway lên bus — và giữ nguyên
> contract/naming học từ Cocoa + Tapable.

---

## 0. TL;DR — một câu chỉ đường

**"Mutate xuống, await ngang, broadcast ra."**

- **Mutate xuống** — state gameplay có thẩm quyền: viết inline đồng bộ trong orchestrator. Không hook, không bus.
- **Await ngang** — presentation cần thứ tự: awaited delegate hook (`should` / `will` / `did`). Single-cast, orchestrator giữ quyền định thời.
- **Broadcast ra** — fact độc lập cho khán giả vô danh: `bus.emit(Fact)` sync, void, fire-and-forget, đi qua đúng một wiring layer.

Default-bias: **mặc định là delegate; bus là ngoại lệ phải biện minh được tính "vô danh / N tuỳ ý".**

---

## 1. Bối cảnh game: ba loại hậu quả

Sai lầm gốc là gộp mọi "hậu quả của một sự kiện game" vào một danh sách phẳng rồi ném hết lên event bus. Khi enemy chết / line bị clear / player place block, các hậu quả thực ra thuộc **ba loại khác nhau** với nhu cầu khác nhau:

| Loại | Ví dụ | Bản chất | Cơ chế |
|---|---|---|---|
| **1. State gameplay tất định** | `+score`, `+exp`, tính "có lên level không", trừ máu, cộng coin | Transaction có thứ tự, đồng bộ, deterministic, **nguồn sự thật** | Viết **inline** trong orchestrator. Không hook, không bus. |
| **2. Presentation / feedback cần thứ tự** | cập nhật UI, popup level-up, effect vỡ, animation chết, SFX khớp frame | Phụ thuộc đầu ra của (1), cần **sequencing/timing** | **Awaited delegate hook** single-cast |
| **3. Cross-cutting độc lập** | achievement, quest progress, analytics, telemetry | Không cần thứ tự, **khán giả vô danh** | **Event bus**, sync `emit`, không await |

Ranh giới quan trọng nhất **không** nằm trên trục "delegate vs bus" như một lựa chọn nhị phân. Nó nằm **giữa ba loại này**: (1) và (2) phải được **điều phối tường minh** bởi một orchestrator; chỉ (3) mới là đất của bus.

---

## 2. Litmus test — phân loại bất kỳ hậu quả mới nào

Chạy ba câu hỏi tuần tự. Mỗi câu tự trả lời qua việc bạn chọn cơ chế nào.

```
Hậu quả mới
│
├─ Q1. Có mutate game state CÓ THẨM QUYỀN không?
│      (điểm, máu, exp, vị trí, "đã thắng chưa")
│      └─ CÓ ⇒ LOẠI 1: viết inline đồng bộ trong orchestrator. Dừng.
│
├─ Q2. Producer có cần ĐỌC GIÁ TRỊ TRẢ VỀ để rẽ nhánh không?
│      └─ CÓ ⇒ DECISION GATE: `should…` => Promise<T>  (consumer được VETO)
│
├─ Q3. Producer có cần CHỜ side-effect xong mới đi bước
│      người chơi THẤY kế tiếp không?
│      └─ CÓ ⇒ COMPLETION GATE: await `onWill…` / `onDid…`
│
└─ Q4. Không chờ — KHÁN GIẢ có tên/nhỏ hay vô danh/N?
       ├─ Có tên, fan-out nhỏ tại 1 wiring layer ⇒ NOTIFICATION delegate: void `onDid…`
       └─ Vô danh, N tuỳ ý ⇒ EVENT BUS: emit(Fact)
```

**Lưỡi dao quan trọng nhất** (và là chỗ lằn ranh hay bị hiểu sai):

- `await` **không** phân định delegate-vs-bus. Nó phân định *bên trong* delegate (completion gate có await vs notification không await).
- Cái phân định delegate-vs-bus là **khán giả**: tên-biết-trước ⇒ delegate; vô danh ⇒ bus.
- Hệ quả từ thực tế API: `emit` của mọi bus thông dụng là **sync + void**, nên một thứ cần await thì *về mặt kiểu* không thể là bus. Phân loại được **đóng cứng vào chữ ký**, không phải "quy ước hãy nhớ":
  - cần chờ ⇒ `(d) => Promise<void>` (await được)
  - không chờ + vô danh ⇒ `emit(fact): void` (không await được)
- **Nếu bạn từng thấy *cần* `await` một `bus.emit`, đó là litmus báo nó vốn là delegate, không phải bus.** Await một broadcast là code smell.

---

## 3. Bốn tier (theo Apple: `should` / `will` / `did` + data source)

| Tier | Verb | Chữ ký | Producer làm gì | Cocoa | Tapable |
|---|---|---|---|---|---|
| **Decision gate** | `should…` | `=> Promise<T>` | rẽ nhánh theo giá trị trả về | `shouldHighlightRowAt` | `AsyncSeriesBailHook` |
| **Completion gate** | `will…` / `did…` | `=> Promise<void>` | `await` rồi đi tiếp | `willDisplay` / `didSelect` (awaited) | `AsyncSeriesHook` / `AsyncParallelHook` |
| **Notification** | `did…` | `=> Promise<void>` | gọi `void`, không chờ | `didSelectRowAt` (informational) | — |
| **Data source** | query (`next3`, `peek`) | `=> T` | **kéo** dữ liệu để đi tiếp | `numberOfRows`, `cellForRow` | — |

Lưu ý quan trọng: **completion gate và notification dùng chung chữ ký** (`=> Promise<void>`). Khác nhau *chỉ ở call site*: `await this.onX?.(d)` thì gate, `void this.onX?.(d)` thì không. Decision gate mới thật sự khác: tên `should…` và trả về giá trị producer đọc.

### 3.1 Decision gate — `should…` (consumer được veto)

Trong game cực hợp cho: i-frame (`shouldApplyDamage`), tutorial chặn input (`shouldPlaceBlock`), luật spawn, xác nhận thoát màn.

```ts
class CombatResolver {
  shouldApplyDamage?: (d: { target: EntityId; amount: number }) => Promise<boolean>;

  async hit(target: EntityId, amount: number): Promise<void> {
    const ok = await this.shouldApplyDamage?.({ target, amount });
    if (ok === false) return;            // i-frame / shield consumer phủ quyết
    this.applyDamage(target, amount);    // loại 1: mutate inline
  }
}
```

### 3.2 Completion gate — await `will…` / `did…`

Producer commit state, rồi **chờ** side-effect (animation, transition, I/O) xong mới đi bước kế. Chính `await` là cái gate. Đọc orchestrator từ trên xuống, mỗi `await this.onX?.()` là một checkpoint thấy được.

```ts
const cleared = this.grid.clearLines(rows, cols);
this.score += scoreForClear(clears, this.combo);     // loại 1: mutate trước
await this.onLinesCleared?.({ ...clears, cells: cleared, score, combo }); // loại 2: chờ animation
if (leveledUp) await this.onLeveledUp?.({ level });  // popup nối tiếp animation, thứ tự = thứ tự await
```

`will…` báo *trước* mutation (consumer chuẩn bị); `did…` báo *sau* (consumer phản ứng với state đã commit).

### 3.3 Notification — fire-and-forget `did…`

Thì quá khứ, gọi bằng `void`. Consumer-**có tên** phản ứng (badge, toast, SFX) nhưng không có gì downstream chờ.

```ts
void this.onComboTick?.({ combo: this.combo });      // cùng field, chỉ là không await
```

### 3.4 Data source — pull, không phải push

`shapes.next3()` và `tray.peek()` trong BlockBlast **chính là** data source: producer *kéo* dữ liệu và đọc giá trị trả về — khác hẳn *push* một `did…`.

> **Luật:** đừng mô hình hoá một *pull* thành delegate `did…`. Cần dữ liệu on-demand ⇒ expose query method, không phải notification sau-khi-rồi.

---

## 4. Naming convention

- **Verb báo tier** (theo Apple): `should…` trả quyết định; `will…` sắp-commit; `did…`/quá-khứ sau-khi-rồi.
- **Đặt tên theo việc *producer LÀM*, không theo việc *consumer phản ứng*.**
  `onDidSave` / `onLinesCleared` ✅ — `onShowToast` / `onPlaySound` ❌. Consumer tự quyết phản ứng.
- **Hook (delegate):** `onX`, single-cast, số ít. `onBlockPlaced`, `onLinesCleared`, `onLeveledUp`.
- **Bus fact:** danh từ thì hoàn thành, **không** tiền tố `on`. `BlockPlaced`, `LinesCleared`, `PlayerLeveledUp`.
- Mẹo đọc nhanh: `onX` = "có người đang chờ tôi làm xong X" (await được). `X` trần = "X đã xảy ra, ai quan tâm tự lo" (fire-and-forget).
- **Một data-object parameter** `(d: { … })`, không positional — thêm field sau không vỡ handler cũ.
- **Field optional** (`?`) gọi qua `?.` — delegate chưa bind là no-op; producer không bao giờ *bắt buộc* phải có consumer.
- **Không nhét type của consumer vào payload.** Producer ship plain data (`{ x, y }`), không `DOMRect` / engine `Vec2`. Consumer tự dịch.

---

## 5. Orchestrator + Gateway (phần game-dev mà bản gốc chưa có)

### 5.1 Orchestrator

Một method/đối tượng duy nhất chạy state gameplay tất định *đồng bộ*, từ trên xuống, trace được. (`placeBlock` của BlockBlast là ví dụ.) Mọi loại-1 nằm ở đây; loại-2 được orchestrator **kéo** qua awaited hook, không tự bay.

### 5.2 Gateway lên bus — KHÔNG phải class mới

Khi cần đẩy fact lên bus, **không** tạo một class chuyên re-dispatch (nó thành nguồn-sự-thật-thứ-hai cho "điều gì xảy ra sau X"). Thay vào đó, chính **wiring/adapter layer** — nơi bind các `onX` — cũng là nơi gọi `bus.emit(Fact)`.

```ts
// adapter layer (KHÔNG nằm trong core; core không hề import bus):
game.onLinesCleared = async (d) => {
  await fx.playClear(d.cells);    // loại 2: presentation, được await
  void audio.play('clear');       // loại 2: notification có-tên, không await
  bus.emit('LinesCleared', { count: d.cells.length }); // loại 3: fact, sync, không await
};
```

Vì bus chỉ có **một** cửa vào, nỗi sợ "khó trace" tan: muốn biết bus được nuôi từ đâu, đọc đúng wiring layer.

> "Hook wrap bus" của bạn đúng — và đúng chỗ là **trong adapter, sync, không await.** Cái duy nhất bị cấm là cố biến một presentation-cần-thứ-tự thành bus event để né viết hook; lúc đó sync-void của `emit` sẽ âm thầm làm sai thứ tự mà không báo lỗi.

---

## 6. Fan-out: một field, một handler

Delegate field giữ đúng **một** handler. Khi nhiều consumer-có-tên cùng phản ứng một thời điểm, **wiring layer** compose chúng — producer không biết. Đây đúng là phân biệt series/parallel của Tapable.

```ts
// completion-gate, parallel — producer chờ tất cả (AsyncParallelHook):
game.onItemDone = (d) => Promise.all([list.markDone(d), bar.advance(d)]).then(() => {});

// notification, parallel — không chờ:
game.onItemDone = (d) => { void list.markDone(d); void bar.advance(d); };
```

Đừng tạo class chuyên đi fan-out. Compose ngay tại wiring layer.

---

## 7. Lifecycle: bind / unbind (tinh thần `weak` của Cocoa)

Delegate field là mutable state; coi như subscription có teardown. Đây là chỗ giữ "weak spirit" cho thật: không handler cũ nào còn bắn sau khi consumer đã chết, không consumer nào bị giữ sống chỉ vì closure của producer. **Đây chính là lý do Cocoa khai báo `delegate` là `weak`**, và là nguồn rò rỉ/crash kinh điển nhất khi quên trong game.

```ts
class HudAdapter {
  constructor(private game: BlockBlast) {}
  bind()   { this.game.onLinesCleared = async (d) => this.flash(d); }
  unbind() { this.game.onLinesCleared = undefined; }
}
// composition root sở hữu vòng đời:
for (const a of adapters) a.bind();
// teardown khi đổi scene / destroy:
for (const a of adapters) a.unbind();
```

---

## 8. Lỗi & re-entrancy

Hook được `await` mà throw thì reject lời gọi của producer. Vì call await được, **input mới có thể tới khi control đang ở ngoài** consumer (animation dài, modal). Khoá re-entry và nhả trong `finally` để handler throw không kẹt cờ.

```ts
async placeBlock(...): Promise<void> {
  if (this.locked) return;
  this.locked = true;
  try {
    /* mutate + awaited hooks */
  } finally {
    this.locked = false;   // nhả kể cả khi handler throw
  }
}
```

(`locked` trong BlockBlast của bạn chính là pattern này.)

---

## 9. Game loop: đừng event hoá trạng thái liên tục

Trạng thái đổi *mỗi frame* (vị trí, máu giảm theo thời gian, cooldown) **poll trong `update(dt)`**, không event-driven. Delegate/bus chỉ dành cho **thời điểm rời rạc** (đặt block, clear, chết, lên level). Event hoá per-frame state vừa tốn vừa loạn thứ tự.

---

## 10. Bảng quyết định nhanh

| Tình huống | Dùng |
|---|---|
| Mutate game state có thẩm quyền | **Inline** trong orchestrator (loại 1) |
| Consumer cần được **veto** producer | `should…` => Promise\<T\> |
| Producer cần **chờ** side-effect (animation/transition) | await `onWill…` / `onDid…` |
| Consumer-**có tên** phản ứng, không ai chờ | `void onDid…` (notification) |
| Producer cần **kéo dữ liệu** để đi tiếp | Data source query (`next3`, `peek`) |
| Khán giả **vô danh, N tuỳ ý**, không thứ tự (analytics, achievement) | **Event bus** `emit(Fact)` |
| Trạng thái đổi mỗi frame | **Poll** trong `update(dt)` |
| Cần replay / undo / time-travel | Reducer / event-sourcing, không phải mutable delegate field |

---

## 11. Prior art

- **Cocoa delegation** (Apple) — contract, weak/lifecycle, optional methods qua `respondsToSelector:`.
- **`should` / `will` / `did`** + return-value distinction + **delegate vs data source** — Apple, *Delegates and Data Sources*.
- **Awaitable delegates** — Swift bridge sync delegate sang `async` bằng continuation (`withCheckedContinuation`).
- **Tapable** (webpack) — `AsyncSeriesHook` / `AsyncParallelHook` / `AsyncSeriesBailHook` = completion gate / parallel fan-out / decision gate.
- **Ports & Adapters / Hexagonal** — delegate field là *driven port*; consumer bind nó là *adapter*; core không import adapter.