## Cấu trúc repo

- Skills sống ở **`.claude/skills/<name>/`** — nguồn canonical **duy nhất**. Không dùng `.agents/skills`, không symlink, không copy sang nơi khác. Claude Code tự nạp skill từ đây.
- Thêm skill mới = tạo `.claude/skills/<name>/SKILL.md` (frontmatter `name` + `description`). Không cần đăng ký ở đâu khác.
- `.claude/rules/` là coding rules áp cho công việc **trong** repo này.
- `data/` là fixture/output local, **gitignored** — không commit.

## Skill creation rules:

- Các skill sống độc lập được, không references và không nhắc về nhau