# ai-skills

Thư viện skill cá nhân cho Claude Code. Mỗi skill sống độc lập trong `.claude/skills/<name>/` và được Claude Code tự khám phá qua `description` trong `SKILL.md`. Index dưới đây là để **người** tra cứu.

## Cấu trúc

```
.claude/skills/   # 46 skill — nguồn canonical duy nhất
.claude/rules/    # coding rules áp cho công việc trong repo này
data/             # fixture/output local (gitignored)
```

## Skills

### Agent & LLM engineering
| Skill | Mục đích |
|---|---|
| `agent-interface-design` | Thiết kế mọi bề mặt model đọc và context runtime: system prompt, tool schema/description, response, MCP, load policy, memory, compaction, prompt caching |
| `flow-prompt-language` | Viết prompt cho agent bám workflow nghiệp vụ, route giữa các state |
| `delegating-to-codex` | Giao việc cho OpenAI `codex exec` CLI (chẩn đoán, refactor, ảnh) |
| `using-codex-cli` | Gọi Codex CLI từ script/agent; xử lý sự cố khi chạy codex |
| `workflow-skill-builder` | Dựng SKILL orchestrator nhiều pha, spawn subagent song song |

### Software design & code
| Skill | Mục đích |
|---|---|
| `codebase-design` | Từ vựng thiết kế deep module, seam, code dễ test/AI-navigable |
| `functional-core-imperative-shell` | Cấu trúc backend use case: pure core + IO shell mỏng (TypeScript) |
| `cli-design` | Thiết kế & xây công cụ command-line (TypeScript/Node/Bun) |
| `hono` | Xây web app Hono (routing, middleware, JSX, validation, streaming) |

### Game development
| Skill | Mục đích |
|---|---|
| `minigame-architecture` | Kiến trúc tổng thể cho minigame casual/puzzle offline |
| `minigame-convention` | Scaffold/refactor TypeScript trong folder minigame (logic↔view) |
| `app-state-casual-game` | Pattern app-state bền vững cho game casual/puzzle (Cocos) |
| `lifecycle-delegate` | Cho luồng game turn-based đọc như script await animation (delegate vs event bus) |

### Product, spec & docs
| Skill | Mục đích |
|---|---|
| `gdd-writer` | Viết game design document (GDD / design spec) |
| `product-brief-writer` | Viết product brief / one-pager / PR-FAQ trước khi có PRD |
| `spec-from-requirement` | Sinh spec chi tiết (CLI/API/schema) từ requirement, áp một chuẩn |
| `ui-blueprint-generator` | Biến PRD/GDD thành tài liệu UI (screen/wireframe spec) |
| `to-prd` | Biến hội thoại hiện tại thành PRD và đẩy lên issue tracker |

### Workflow & process
| Skill | Mục đích |
|---|---|
| `grilling` | Grill người dùng để stress-test một kế hoạch trước khi build |
| `guided-consultation` | Dẫn dắt qua bài toán quyết định/lập kế hoạch với ràng buộc ngầm |
| `handoff` | Nén hội thoại thành tài liệu handoff cho agent khác tiếp nhận |
| `zoom-out` | Đưa ra góc nhìn cao hơn/bối cảnh rộng hơn cho một đoạn code |
| `setting-up-harness` | Set up repo để làm việc với coding agent (CLAUDE.md, bootstrap harness) |

### Content pipelines
| Skill | Mục đích |
|---|---|
| `chapter-audio-pipeline` | Biến chương truyện thành audio (polish→segment→synthesize→concat) |
| `novel-processor` | Xử lý truyện Trung theo từng chương (translate→refine→visual→audio) |

### Metrics
| Skill | Mục đích |
|---|---|
| `tracker-metrics` | Phân tích metrics/KPI game từ tracker.zingplay.com |

## Thêm skill mới

Tạo `.claude/skills/<name>/SKILL.md` với frontmatter `name` + `description`. Không cần đăng ký ở đâu khác — Claude Code tự nạp. Xem `agent-interface-design` và `workflow-skill-builder` để viết skill tốt.
