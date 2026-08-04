# Designing APIs for agents — đối chiếu với skill `agent-interface-design`

*Ghi ngày 2026-08-04. Nguồn chính:*

- Yan Xie, Virat Patel, Albert Chang (Webflow), "Designing APIs for agents", The New Stack, 2026-08-01 (bài sponsored, đăng lại từ webflow.com 2026-07-21). <https://thenewstack.io/designing-apis-for-agents/>
- Anthropic Engineering, "Writing effective tools for agents". <https://www.anthropic.com/engineering/writing-tools-for-agents>

## Claims chính của bài Webflow

1. **Developer API ≠ agent API.** API cho developer giả định người đọc docs, tự compose endpoint, tự quản state, tự xử lý lỗi. Agent chỉ có tool descriptions, schemas, responses và context window — API surface phải tự dẫn đường. Wrap API có sẵn thành MCP tools → quá low-level, quá chatty; mỗi tool call thêm là thêm latency, token, context pressure, xác suất fail.
2. **Intent-level tools.** `update_page_section({page, section, changes})` thay cho chuỗi list→find→fetch→inspect→update. Platform orchestrate nội bộ.
3. **Tool explosion ở scale** → hai lối thoát: (a) *layered tool architecture* — domain tools chứa typed actions, workflow tools, guide tools; (b) *filesystem/code representation* — agent thao tác trên project-as-files bằng read/write/shell, giảm phụ thuộc vào tool discovery. Webflow coi (a) là ngắn hạn, (b) là dài hạn.
4. **Observability cho agent khác về bản chất:** đo intent chứ không chỉ request success. Tín hiệu giá trị nhất: *missing-tool attempts* (tool agent kỳ vọng mà không có), session replay lộ workflow suy thoái không có hard error, clustering usage (58.7% sessions ở 3 workflows), silent error >10% sessions. Hạ tầng "healthy" trong khi agent experience fail âm thầm.
5. **Skills layer:** "Tools expose what an agent can do; skills encode how to do it well" — playbook, conventions, domain judgment giao qua kênh riêng, không nhét vào tool.
6. Hạ tầng (Durable Objects, WebSocket bridge tới Designer), distribution (hosted connector, 6.7X growth) — ngoài phạm vi interface design.

*Caveat:* bài sponsored của Webflow, có plug MCPCat; số liệu không kiểm chứng được. Giá trị nằm ở pattern, không ở số.

## Đối chiếu

- Bài Anthropic đã được skill hấp thụ gần như đầy đủ (consolidation, namespacing, response context, token efficiency, description là surface đòn bẩy cao nhất, eval methodology).
- Webflow bổ sung 3 điểm skill chưa có: **vị trí tác giả chỉ-sở-hữu-server** (không kiểm soát system prompt của client → kênh thay thế: server instructions, guide tools, MCP prompts/resources, skills); **production observability signals** (missing-tool attempts, session replay, clustering); **lộ trình thoát tool explosion** (layering vs deferred loading/tool search vs code representation).
- Điểm skill đúng hơn bài: layered domain tools trộn safety class (CMS tool gồm cả publishing) vi phạm "would I grant them together" — permission gắn vào tool name. Webflow tự thừa nhận layering "does not fundamentally eliminate the problem".
- Điểm skill cần cập nhật: "~20 tools per turn" nên chuyển thành ngân sách *loaded set* khi runtime có deferred loading / tool search.
