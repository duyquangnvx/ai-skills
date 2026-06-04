# CLI Best Practices

> Tổng hợp best practices cho CLI, dùng làm reference khi implement webnovel-studio. Nguồn chính:
> [clig.dev](https://clig.dev/) (Command Line Interface Guidelines), [12 Factor CLI Apps](https://jdxcode.medium.com/12-factor-cli-apps-dd3c227a0e46)
> (Jeff Dickey — Heroku CLI/oclif), và phân tích framework của [Bloomberg Stricli](https://bloomberg.github.io/stricli/docs/getting-started/alternatives).
> Liên quan trực tiếp tới nguyên tắc "CLI command = Agent tool" trong `design.md`: agent và user dùng
> chung một surface, khác biệt chỉ ở `--json` — nên các quy tắc output/exit code/error ở đây là bất biến hợp đồng.

## 1. Triết lý

1. **Human-first design.** CLI ngày nay do con người dùng trực tiếp là chính. Thiết kế cho người trước,
   máy sau — nhưng không đánh đổi composability.
2. **Composability.** Là "công dân tốt" của UNIX: stdout/stderr đúng vai, exit codes đúng nghĩa, pipe được.
3. **Consistency.** Theo convention sẵn có (tên flag, hành vi chuẩn) để user đoán được mà không cần docs.
4. **CLI là một cuộc hội thoại.** User gõ sai → sửa → chạy lại. Gợi ý lệnh đúng khi gõ sai, xác nhận
   trước hành động nguy hiểm, suggest bước tiếp theo sau mỗi lệnh (như `git status`).
5. **Saying (just) enough.** Im lặng quá lâu trông như treo; xả log quá nhiều thì chìm mất thông tin chính.

## 2. The Basics — bắt buộc

1. **Dùng argument parsing library**, không tự parse.
2. **Exit code 0 = thành công, non-zero = lỗi.** Map exit code cho các failure mode quan trọng. Script
   và agent đều phụ thuộc vào điều này.
3. **stdout cho output chính** (dữ liệu, thứ pipe được). **stderr cho messaging** (log, warning,
   progress, error). Quy tắc nhớ nhanh: *stdout is for output, stderr is for messaging*.

## 3. Help

- `-h`, `--help`, và chạy không args (khi thiếu args bắt buộc) → đều hiện help. Với CLI dạng subcommand:
  `mycli help sub`, `mycli sub --help`, `mycli sub -h` đều phải hoạt động.
- Help ngắn gọn mặc định (mô tả + 1–2 ví dụ + trỏ tới `--help`); đầy đủ khi `--help`.
- **Mở đầu bằng examples** — phần được dùng nhiều nhất. Flags/commands phổ biến nhất hiện trước.
- `--version` / `-V` xem version; kèm thông tin debug hữu ích.
- Gõ sai lệnh → gợi ý lệnh đúng ("Did you mean ps?"), nhưng không tự chạy thay user.
- Có docs trên web (search/link được) lẫn trong terminal.

## 4. Output

- **Phát hiện TTY** cho từng stream: stdout không phải terminal (đang pipe/CI) → tắt màu, tắt
  spinner/progress, không animation.
- Hỗ trợ `--json` cho structured output (bất biến, cho script/agent) và `--plain` cho dạng bảng đơn giản.
- Tắt màu khi: không phải TTY, `NO_COLOR` set, `TERM=dumb`, `--no-color`, hoặc env riêng
  (vd `WNS_NO_COLOR`).
- **Nếu thay đổi state, nói rõ đã làm gì** (như `git push`). Có lệnh xem state hiện tại (như `git status`).
- Hành động vượt ranh giới chương trình (ghi file ngoài args, gọi network) phải explicit.
- Bảng: mỗi dòng = 1 record, không kẻ viền — để `grep`/`wc` được.
- Output dài → pager (`less -FIRX`), chỉ khi là TTY.
- Thành công vẫn nên in gì đó ngắn gọn; có `-q/--quiet` để tắt khi cần.

## 5. Errors

Error message tốt gồm: **code → tiêu đề → mô tả → cách fix → URL**:

```
Error: EPERM - Invalid permissions on myfile.out
Cannot write to myfile.out, file does not have write permissions.
Fix with: chmod +w myfile.out
https://github.com/myorg/myapp/issues
```

- Lỗi expected → bắt và viết lại cho người đọc hiểu, kèm cách fix.
- Lỗi unexpected → traceback + cách báo bug; debug log ghi ra file thay vì xả terminal.
- Thông tin quan trọng nhất đặt **cuối** output. Đỏ dùng tiết chế.
- Signal-to-noise: nhiều lỗi cùng loại → gộp dưới một header.

## 6. Arguments & Flags

- **Ưu tiên flags hơn positional args.** Quy tắc: 1 loại arg là ổn, 2 loại đáng ngờ, 3 loại là sai.
  Nhiều args cùng loại thì ổn (`rm f1 f2 f3`). Ngoại lệ: thao tác chính quá phổ biến (`cp src dest`).
- Mọi flag có bản full-length; short flag chỉ dành cho flag dùng thường xuyên.
- Tên flag chuẩn: `-f/--force`, `-q/--quiet`, `-n/--dry-run`, `-o/--output`, `--json`, `-a/--all`,
  `-d/--debug`, `--no-input`.
- Default phải đúng cho đa số user.
- Hỗ trợ `-` để đọc stdin/ghi stdout; `--` để ngừng parse flags.
- Flags/args order-independent nếu được.
- **Không nhận secrets qua flags** (lộ qua `ps`, shell history) và **không đọc secrets từ env vars**
  (leak vào logs, `docker inspect`) — dùng file (`--password-file`), stdin, hoặc `.env` của workspace
  với quyền hạn chế.

## 7. Interactivity

- Thiếu input + stdin là TTY → prompt. **Không bao giờ *bắt buộc* prompt** — luôn có flag tương đương
  để script/agent hóa được. Tôn trọng `--no-input`: thiếu input thì fail và chỉ rõ flag cần truyền.
- Xác nhận trước hành động nguy hiểm, phân cấp:
  - *Nhẹ* (xóa 1 file): hỏi y/n hoặc không cần.
  - *Vừa* (xóa thư mục, bulk modify): hỏi y/n + nên có `--dry-run`.
  - *Nặng* (xóa cả project/resource remote): bắt gõ lại tên thứ bị xóa; script thì `--confirm="name"`.
- Ctrl-C luôn thoát được, thoát nhanh; cleanup có timeout, Ctrl-C lần 2 thì skip cleanup.

## 8. Subcommands

- Pattern: `noun verb` (vd `chapter add`, `voice bind`). Verb nhất quán giữa các noun.
- Tránh tên mơ hồ/na ná (update vs upgrade).
- **Không có catch-all subcommand, không cho viết tắt tùy ý** (`i` = `install`) — khóa namespace vĩnh
  viễn, thêm lệnh mới sẽ break script của user. Alias thì phải explicit và ổn định.

## 9. Robustness & Performance

- **Responsive hơn fast**: in gì đó trong <100ms; trước network call phải nói đang làm gì.
- Startup: <100ms rất tốt, 100–500ms là mục tiêu thực tế của Node, >2s là user né.
- Progress bar/spinner cho tác vụ lâu; lỗi thì in log đã ẩn sau progress bar ra.
- Network có timeout mặc định hợp lý, configurable.
- **Idempotent / crash-only / recoverable**: fail giữa chừng → chạy lại là tiếp tục được. Khớp
  nguyên tắc "Deterministic-first" của project.
- Validate input sớm, fail rõ ràng trước khi thay đổi state.

## 10. Configuration & Env vars

Thứ tự ưu tiên (cao → thấp): **flags > env vars > project config > user config > system config**.

| Loại config | Ví dụ | Nơi đặt |
|---|---|---|
| Đổi theo từng lần chạy | `--dry-run`, debug level | Flags |
| Theo máy/user | proxy, màu, đường dẫn tool | Env vars (+ flags) |
| Theo project, chung cho team | provider, model, cấu trúc | File config trong version control |

- **Theo XDG spec** cho config cấp user: `~/.config/myapp`; data `~/.local/share/myapp`; cache
  `~/.cache/myapp` (macOS: `~/Library/Caches/myapp`).
- Đọc `.env` của workspace cho giá trị theo-project, nhưng `.env` không thay thế config file thực sự
  (không có history, chỉ string, hay chứa secrets).
- Env var names: `UPPER_SNAKE_CASE`; tôn trọng các env chuẩn: `NO_COLOR`, `DEBUG`, `EDITOR`,
  `HTTP_PROXY`, `TMPDIR`, `PAGER`.

## 11. Future-proofing

- Subcommands, flags, config, env vars đều là **interface public — phải giữ ổn định**. Đổi
  non-additive phải có deprecation warning trước, kèm hướng migrate.
- Output cho human được phép đổi; output `--json`/`--plain` là hợp đồng — khuyến khích script/agent
  dùng chúng.
- Thay đổi ưu tiên dạng additive (thêm flag mới thay vì đổi nghĩa flag cũ).

## 12. Naming & Distribution

- Tên lệnh: ngắn, chữ thường, dễ gõ, dễ nhớ (`curl` tốt, `DownloadURL` tệ), không trùng lệnh phổ biến.
- Phân phối single binary nếu được; dễ uninstall; không phone-home analytics khi chưa được đồng ý.

---

# Architecture cho CLI TypeScript

## 13. Kiến trúc phân lớp

Sai lầm phổ biến nhất: viết business logic trong command handler. Chuẩn là tách lớp:

```
src/
├── bin.ts              # Entry: shebang, error handler trung tâm, gọi runMain()
├── commands/           # CLI layer: parse args → gọi core → render. Adapter mỏng.
│   └── chapter/        # nhóm theo noun
│       ├── add.ts
│       └── list.ts
├── core/               # Domain logic — KHÔNG biết gì về CLI
├── infra/              # FS, API clients (OmniVoice, LLM), config loading
└── ui/                 # Reporter: màu, spinner, --json, TTY detection
```

Quy tắc: command chỉ làm 3 việc — validate input, gọi core, render kết quả. Core không `console.log`,
không `process.exit`, không đọc `process.env` trực tiếp. Lợi ích:

- Test core như hàm thuần, không spawn process.
- Core dùng được như programmatic API song song với CLI (đúng tinh thần "CLI command = Agent tool").
- Đổi framework CLI không đụng logic.

## 14. Context injection thay vì globals

Truyền context object xuống command thay vì đụng trực tiếp globals (pattern "isolated context" của Stricli):

```typescript
interface CliContext {
  cwd: string
  env: Record<string, string | undefined>
  stdout: Writable
  stderr: Writable
  reporter: Reporter
}
```

Đây là điểm quyết định khả năng test: fake context với in-memory streams → assert output, không cần
mock module hay spawn process.

## 15. Chọn framework

| Framework | Dùng bởi | Mạnh | Yếu |
|---|---|---|---|
| commander | Vite (cac tương tự) | Đơn giản, phổ biến nhất | Method chaining → TS không infer được type args |
| yargs | nhiều tool cũ | Nhiều tính năng | TS phải config tay, nhiều deps |
| oclif | Heroku, Salesforce | Full framework: plugins, codegen, autocomplete | Nặng, load command qua FS ("magic"), gắn chặt Node |
| clipanion | yarn | Zero deps, type-safe từ field declaration | Class-based, load hết commands lúc runtime |
| stricli | Bloomberg | Type-safe triệt để, lazy load từng command, isolated context sẵn | Mới, ecosystem nhỏ |
| citty (unjs) | Nuxt (`nuxi`) | Nhẹ, functional, lazy subcommands | Ít tính năng cao cấp |

Insight chính (phân tích Bloomberg): method chaining không thể type-safe end-to-end — runtime parse và
compile-time type dễ lệch. Framework hiện đại (stricli, clipanion, citty + zod) suy type của flags từ
khai báo.

Chọn nhanh: tool nội bộ/vừa → **citty** hoặc **stricli**; cần plugin ecosystem → **oclif**; zero-dep
đã được yarn chứng minh → **clipanion**.

## 16. Thư viện bổ trợ tiêu chuẩn

- **Validation**: `zod` ở boundary (args, config file, API response).
- **Prompts**: `@clack/prompts` hoặc `@inquirer/prompts`.
- **Màu**: `picocolors` (nhẹ hơn chalk); **spinner**: `ora` hoặc của clack.
- **Config**: `c12` (unjs, có sẵn precedence + extends) hoặc `cosmiconfig`.
- **Chạy lệnh ngoài**: `execa`.
- **TUI phức tạp** (live dashboard): `ink` — chỉ khi thật sự cần.

## 17. Error handling

Một error handler trung tâm ở entry point + typed errors:

```typescript
class CliError extends Error {
  constructor(
    message: string,
    readonly exitCode: number = 1,
    readonly suggestion?: string,
  ) { super(message) }
}

// bin.ts
main().catch((error: unknown) => {
  if (error instanceof CliError) {
    reporter.error(error.message, error.suggestion)
    process.exitCode = error.exitCode
  } else {
    reporter.unexpectedError(error)  // traceback + link báo bug
    process.exitCode = 1
  }
})
```

- Core throw `CliError` có chủ đích; mọi thứ khác là bug → in traceback.
- `process.exitCode` thay vì `process.exit()` để stream kịp flush.
- Bắt `SIGINT` để cleanup có timeout.

## 18. Reporter — một chỗ duy nhất cho output

Command trả structured data; reporter quyết định render (human table hay JSON tùy `--json`), xử lý TTY
detection, `--quiet`, `NO_COLOR`:

```typescript
interface Reporter {
  info(msg: string): void          // → stderr
  result(data: unknown): void      // → stdout
  error(msg: string, fix?: string): void
}
```

Toàn bộ quy tắc output ở mục 4 trở thành một chỗ duy nhất phải implement đúng.

## 19. Packaging & startup performance

- **ESM-only** (Node 20+).
- Bundle bằng **tsup**/tsdown thành 1 file `dist/cli.js` → giảm cost module resolution, startup nhanh
  rõ rệt. `package.json` có `"bin"` + `"engines"`.
- **Lazy-load** command và heavy deps: `await import()` trong handler thay vì import top-level. Mục
  tiêu startup <150ms (mức tốt nhất của Node).
- Cần single binary thật → `bun build --compile`.

## 20. Testing theo lớp

- **Core**: unit test thuần — chiếm phần lớn coverage.
- **Commands**: gọi `run(fakeContext, args)` trực tiếp, assert output trên in-memory stream.
- **E2E** (ít, chỉ critical flows): `execa` chạy CLI đã build, assert exit code + stdout; snapshot test
  cho `--help` để phát hiện breaking change interface.

## Nguồn

- [clig.dev — Command Line Interface Guidelines](https://clig.dev/)
- [12 Factor CLI Apps — Jeff Dickey](https://jdxcode.medium.com/12-factor-cli-apps-dd3c227a0e46)
- [Stricli — Alternatives Considered](https://bloomberg.github.io/stricli/docs/getting-started/alternatives)
- [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide)
- [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
