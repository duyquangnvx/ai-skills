# Dedup backlog

Các cặp skill trùng/lấn mục đích, cần review biên tập riêng (đọc kỹ cả hai, test trigger) — **không** gộp vội trong đợt dọn cấu trúc. Mỗi mục là một pass độc lập.

## 1. `tool-design` ↔ `agent-tool-design` — ĐÃ XỬ LÝ (2026-07-17)

Đã gộp cả hai, cùng với `instructions-best-practices`, thành **`agent-interface-design`** (mọi bề mặt model đọc: instructions + tool layer). Nội dung riêng của `tool-design` được hấp thụ (architectural reduction, MCP qualified naming, guardrail over-consolidation); `scripts/description-generator.py` bị bỏ vì là rule-based scaffolding mâu thuẫn với chính guidance của skill.

## 2. `delegating-to-codex` ↔ `using-codex-cli`

Cùng liên quan tới OpenAI Codex CLI.

| | `delegating-to-codex` | `using-codex-cli` |
|---|---|---|
| SKILL.md | 254 dòng | 51 dòng |
| Trọng tâm | *Khi nào / tại sao* giao việc cho Codex (chẩn đoán, refactor, ảnh, review) | *Cách gọi* Codex CLI từ script/agent; xử lý sự cố (hang, ghi file ngoài ý muốn) |

Có thể **bổ trợ nhau** (chiến lược vs cơ chế) hơn là trùng. **Cần quyết:** giữ cả hai với ranh giới rõ ràng, hay gộp phần "cách gọi" vào một reference của `delegating-to-codex` rồi bỏ `using-codex-cli`.

---

Ghi chú: `guided-consultation` ↔ `grilling` có họ hàng (tư vấn quyết định vs stress-test kế hoạch) nhưng mục đích đủ khác — tạm coi là **giữ cả hai**, chỉ review nếu thấy trigger chồng lấn thực tế.
