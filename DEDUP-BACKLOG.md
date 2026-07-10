# Dedup backlog

Các cặp skill trùng/lấn mục đích, cần review biên tập riêng (đọc kỹ cả hai, test trigger) — **không** gộp vội trong đợt dọn cấu trúc. Mỗi mục là một pass độc lập.

## 1. `tool-design` ↔ `agent-tool-design`

Cả hai cùng chủ đề: thiết kế **lớp tool-interface của agent** (tool description, schema, response format, naming, MCP).

| | `tool-design` | `agent-tool-design` |
|---|---|---|
| SKILL.md | 295 dòng | 102 dòng |
| Kèm theo | `references/architectural-reduction.md`, `references/best-practices.md`, `scripts/description-generator.py` | `references/{process,sources,testing,patterns}.md` |

Hai cách tiếp cận khác cấu trúc, không phải bản sao. **Cần quyết:** gộp thành một (giữ tên nào, hợp nhất references + script), hay tách vai trò rạch ròi để cùng tồn tại (vd `agent-tool-design` = quy trình/nguyên tắc, `tool-design` = mức một tool + tooling script).

## 2. `delegating-to-codex` ↔ `using-codex-cli`

Cùng liên quan tới OpenAI Codex CLI.

| | `delegating-to-codex` | `using-codex-cli` |
|---|---|---|
| SKILL.md | 254 dòng | 51 dòng |
| Trọng tâm | *Khi nào / tại sao* giao việc cho Codex (chẩn đoán, refactor, ảnh, review) | *Cách gọi* Codex CLI từ script/agent; xử lý sự cố (hang, ghi file ngoài ý muốn) |

Có thể **bổ trợ nhau** (chiến lược vs cơ chế) hơn là trùng. **Cần quyết:** giữ cả hai với ranh giới rõ ràng, hay gộp phần "cách gọi" vào một reference của `delegating-to-codex` rồi bỏ `using-codex-cli`.

---

Ghi chú: `guided-consultation` ↔ `grilling` có họ hàng (tư vấn quyết định vs stress-test kế hoạch) nhưng mục đích đủ khác — tạm coi là **giữ cả hai**, chỉ review nếu thấy trigger chồng lấn thực tế.
