## Cấu trúc repo

- Skills sống ở **`.claude/skills/<name>/`** — nguồn canonical **duy nhất**. Không dùng `.agents/skills`, không symlink, không copy sang nơi khác. Claude Code tự nạp skill từ đây.
- Thêm skill mới = tạo `.claude/skills/<name>/SKILL.md` (frontmatter `name` + `description`). Không cần đăng ký ở đâu khác.
- `.claude/rules/` là coding rules áp cho công việc **trong** repo này.
- `data/` là fixture/output local, **gitignored** — không commit.

## Skill creation rules:

- SKILL sống độc lập được, không references và không nhắc về nhau.
- Nội dung SKILL phải đọc hiểu được từ trên xuống dưới, không trùng nội dung với references.
- SKILL không tự chứa lịch sử của chính nó
- SKILL không tự giải thích về chính nó
- SKILL phục vụ frontier models (đã thông minh sẵn), nên SKILL chủ yếu là hướng dẫn và gợi ý
- SKILL không nên chứa nội dung mà model đã biết một cách hiển nhiên (không phải suy luận nhiều), nếu bạn biết thì model cũng biết. Ví dụ như rules trong project, các patterns phổ biến

- Triết lý skill của repo này: skill là bản chuẩn (khái niệm, kiến trúc, format, lifecycle, và trạng thái "một project đã setup đúng trông như thế nào"), không phải kịch bản thao tác. Bạn gõ /ten-skill setup, /ten-skill migrate docs/backlog.md, hay /ten-skill audit index — động từ nằm trong yêu cầu, skill chỉ cần đủ rõ để agent tự suy ra việc phải làm từ chuẩn. Grilling là hình mẫu đúng.