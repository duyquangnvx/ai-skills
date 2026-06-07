# CLI Design Research — Source Material for `cli-design` Skill

> Purpose: comprehensive, source-grounded reference on CLI best practices, modern guidelines, standard patterns, and TypeScript implementation. Intended to be distilled into a SKILL.md (LLM-facing behavior contract) plus optional `references/` files.
> Compiled: June 2026.

## 1. Canonical sources & authority hierarchy

When sources conflict, prefer the more specific and more recent guidance in this order:

1. **Command Line Interface Guidelines (clig.dev)** — the de-facto modern standard. Open-source guide by the Docker Compose / Heroku CLI authors (Prasad, Firshman, Tashian, Parish). Updates traditional UNIX principles for human-first design. Frameworks like Bloomberg's Stricli explicitly state they were built on top of it.
2. **12 Factor CLI Apps (Jeff Dickey, Heroku)** — 12 UX principles that shaped oclif; mostly a subset of clig.dev today but adds concrete guidance on tables, speed budgets, and version reporting.
3. **POSIX Utility Conventions & GNU Coding Standards (Command-Line Interfaces, Program Behavior)** — the underlying syntax conventions (`-x` short options, `--long` options, `--` terminator, exit statuses).
4. **XDG Base Directory Specification (freedesktop.org)** — where config/data/cache files live.
5. **no-color.org (`NO_COLOR`)** — informal standard for disabling color, honored ecosystem-wide.
6. **Agent-first CLI design (2025–2026 writing: Arcjet, nibzard, "Designing CLI Tools for AI Agents")** — emerging consensus that CLIs are now agent APIs; adds structured output, schema introspection, and input-hardening requirements on top of clig.dev.

Links: https://clig.dev · https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46 · https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html · https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html · https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html · https://no-color.org · https://blog.arcjet.com/designing-a-cli-for-ai-agents/

## 2. Core philosophy (from clig.dev, paraphrased)

1. **Human-first design.** If humans are the primary users, design for humans, not for other programs — a reversal of the original machine-first UNIX assumption.
2. **Simple parts that work together.** Composability still matters: stdin/stdout/stderr, exit codes, signals, line-based text, and JSON are the glue. Your tool *will* be embedded in scripts, CI, and agents you didn't anticipate; choose to be a well-behaved part.
3. **Consistency across programs.** Follow existing conventions so the CLI is guessable; break convention only deliberately, when convention demonstrably hurts usability.
4. **Saying (just) enough.** Too little output looks broken; too much drowns the signal. Information is the interface — tune its density.
5. **Ease of discovery.** Steal from GUIs: rich help, examples, "what to run next" suggestions, error messages that teach.
6. **Conversation as the norm.** CLI usage is a multi-invocation dialogue (try → error → correct → retry; setup commands → run command). Design for it: suggest corrections, surface intermediate state, confirm before scary actions, support dry runs.
7. **Robustness — objective and perceived.** Handle bad input, be idempotent where possible, and also *feel* solid: responsive, informative, no raw stack traces.
8. **Empathy.** The user should feel the tool is on their side. Delight = exceeding expectations.
9. **Chaos (break rules deliberately).** The terminal is inconsistent; when you deviate from a standard, do it with intention and document it.

## 3. The non-negotiables ("The Basics")

These are the rules that, if violated, make a CLI broken or a bad citizen:

- **Use an argument-parsing library.** Never hand-roll parsing; libraries give consistent flags, help text, and typo suggestions. (TypeScript options in §15.)
- **Exit code 0 on success, non-zero on failure.** Map distinct non-zero codes to the most important failure modes. Scripts and agents key off this.
- **Primary/machine-readable output → stdout.** This is what pipes consume.
- **Messaging (logs, warnings, errors, progress) → stderr.** Keeps pipes clean while still showing messages to the user. Mnemonic: *stdout is for output, stderr is for messaging.*
- **`-h`/`--help` always shows help** (also bare `myapp` when args are required; also `myapp help sub`, `myapp sub --help` for git-like CLIs). `-h` must never be overloaded with another meaning.
- **Version is discoverable** via `--version` (and `version` subcommand for multi-command CLIs). The version output is a good place for extra diagnostic info; send it as User-Agent if the CLI talks to an API.

## 4. Help & documentation

- **Concise help by default** when a command needs args and gets none: description, 1–2 examples, key flags, pointer to `--help` (jq is the model).
- **Full help on `-h`/`--help`**, ignoring other args.
- **Lead with examples** — they are the most-used part of help. Order: common → complex. If there are many, move them to a web page or cheat-sheet command.
- **Show the most common flags/commands first** (git's grouped command listing is the model).
- **Format help** (bold headings) but emit no escape codes when output is piped/paged.
- **Suggest corrections for typos** ("Did you mean `ps`?"); offer to run, don't auto-run — invalid input may be a logical mistake, and auto-correcting commits you to supporting the typo forever.
- **If stdin is a TTY and the command expects piped input, print help instead of hanging** (don't be `cat`).
- **Provide a feedback path** (issues URL) in top-level help; link from help to web docs (deep links per subcommand).
- **Web docs + in-terminal docs.** Web for searchability and linkability; terminal docs stay in sync with the installed version and work offline. Man pages are optional (`git`/`npm` pattern: expose them via `help` subcommand too); 12-Factor considers them skippable unless your audience expects them (they don't work on Windows).
- **Shell completion** is part of help/discoverability (oclif and Stricli ship it; Stricli's completions run JS at runtime so they can be dynamic and shell-agnostic).

## 5. Output design

- **TTY detection is the master switch.** Check stdout and stderr *individually* with isatty. TTY → human mode (color, animation, tables); not a TTY → machine mode (plain, no ANSI, no spinners). This single heuristic drives most adaptive behavior.
- **Machine-readable output where it doesn't hurt humans.** Line-based text composes with grep/awk/wc; "expect the output of every program to become the input of another" (McIlroy).
- **`--plain`** flag: one record per line, no decoration, for grep/awk when the human format wraps or merges lines.
- **`--json`** flag: structured output for jq, scripts, web APIs, and AI agents. In 2025+ this is considered table stakes, not nice-to-have.
- **Display brief output on success.** Pure silence looks broken to humans; offer `-q`/`--quiet` for scripts instead of defaulting to silence.
- **State changes must be narrated.** Tell the user what just happened (`git push` is the model) and make current state easy to inspect (`git status` is the model). Suggest next commands in workflow chains.
- **Crossing the program boundary should be explicit** — reading/writing files not given as args, or network calls, shouldn't happen silently.
- **Color with intention; disable it when:** not a TTY, `NO_COLOR` set (non-empty, any value), `TERM=dumb`, `--no-color` passed, or `MYAPP_NO_COLOR` set. Honor `FORCE_COLOR` to override detection.
- **No animations when not a TTY** (spinners become garbage in CI logs).
- **Symbols/emoji sparingly** to add structure and draw attention (yubikey-agent is the model); overuse makes a toy.
- **No developer-only output by default** — debug detail goes behind verbose/`DEBUG`. Don't treat stderr as a log file (no `WARN`/`ERR` level labels by default).
- **Pager (`less -FIRX`) for long output**, only when interactive (git diff is the model).
- **Tables (12-Factor #7):** one entry per row, never borders, mind screen width, headers by default with `--no-headers` to hide; consider `--columns`, `--sort`, `--filter`, plus CSV/JSON output.

## 6. Error design

- **Catch expected errors and rewrite them for humans**, with a fix: "Can't write to file.txt. Try: chmod +w file.txt".
- **Ideal error anatomy (12-Factor):** error code, title, optional description, how to fix, URL for more info.
- **Signal-to-noise is everything.** Group repeated similar errors under one header. Put the most important line at the *end* (where the eye lands); red sparingly.
- **Unexpected errors:** provide traceback/debug info and a pre-populated bug-report URL; consider writing the full debug log to a file instead of the screen. Support a `DEBUG` env var for verbose component-level logging.
- **Error logs on disk:** timestamps, rotation/truncation, no ANSI codes.

## 7. Arguments & flags

Terminology: *args* are positional (order matters); *flags* are named (`-r`, `--recursive`, with values via `--file foo` or `--file=foo`; order generally shouldn't matter).

- **Prefer flags to args** — clearer (`heroku fork --from A --to B` vs ambiguous positionals) and easier to evolve without breaking compatibility. Rule of thumb: one type of positional arg is fine, two is suspect, three is never good. Variable-length lists of the *same* type are fine (`rm a b c`, globbing).
- **Every flag has a full-length version** (`-h`/`--help`); long forms make scripts self-documenting (GNU standard).
- **Reserve single-letter flags for the most common operations** — don't pollute the short-flag namespace.
- **Use standard flag names.** Common conventions: `-a/--all`, `-d/--debug`, `-f/--force`, `--json`, `-h/--help` (help only), `-n/--dry-run`, `--no-input`, `-o/--output`, `-p/--port`, `-q/--quiet`, `-u/--user`, `--version`, `-v` (ambiguous: verbose or version — pick one and stay consistent).
- **Defaults should be right for most users** (`ls` would default to `ls -lhF` if designed today). Configurability doesn't excuse bad defaults.
- **Prompt for missing input, but never *require* a prompt** — everything must be passable via flags/args for scripting; skip prompts when stdin isn't a TTY.
- **Confirmation tiers for danger:**
  - *Mild* (delete a file): confirm or not, your call.
  - *Moderate* (delete a directory/remote resource, bulk edit): confirm; offer `--dry-run`.
  - *Severe* (delete an app/server): require typing the resource name; allow `--confirm=<name>` for scripts. Watch for non-obvious destructive paths (config change implying deletions).
- **Support `-` as stdin/stdout placeholder** for file args (`curl ... | tar xvf -`).
- **Optional flag values need an explicit sentinel** like `none` (ssh `-F none`), never a blank.
- **Order independence** between flags and subcommands where the parser allows (`mycmd --foo sub` ≡ `mycmd sub --foo`).
- **`--` terminator** stops flag parsing and passes the rest through verbatim — required for wrapper commands (`heroku run -a myapp -- script.sh -a x`).
- **Never accept secrets via flags** (leaks via `ps` and shell history) **and avoid env vars for secrets** (leak via logs, `docker inspect`, `systemctl show`). Accept secrets only via files (`--password-file`), stdin, pipes, sockets, or secret managers.

## 8. Interactivity

- **Prompt only when stdin is a TTY**; otherwise error with the flag the user should pass.
- **`--no-input` disables all interactivity** explicitly; if input is then required, fail with instructions.
- **Never echo passwords** while typing (disable terminal echo).
- **Let the user escape**: Ctrl-C must always work, even during network I/O; if you wrap something that swallows Ctrl-C (ssh/tmux-like), make the escape path obvious.
- **Prompt UX patterns** (12-Factor): confirmation dialogs for danger; checkboxes/radio selects for choosing among options; type-the-name confirmation for destructive ops.

## 9. Subcommands

- Use subcommands when a tool is complex, or merge closely-related tools into one command (RCS → git). Benefits: shared global flags, help, config, storage.
- **Be consistent across subcommands** — same flag names for the same concepts, same output formats.
- **Two-level pattern: `noun verb`** (`docker container create`); `noun verb` is more common than `verb noun`; keep verbs consistent across nouns. (Heroku used `topic:command` colons — works, but spaces are the dominant convention.)
- **No ambiguous siblings** (`update` vs `upgrade`).
- **Bare invocation lists subcommands / shows help**, never runs a default behavior.
- **No catch-all subcommand** (treating unknown first arg as implicit `run`) — it forecloses ever adding new subcommands safely.
- **No arbitrary prefix abbreviations** (`mycmd i` for install) — same forward-compatibility trap; explicit stable aliases are fine.

## 10. Robustness, performance & signals

- **Validate input early**, fail before side effects, with understandable errors.
- **Responsive > fast: print something within 100ms.** Print *before* slow network calls, not after.
- **Startup-speed budget (12-Factor):** <100ms great; 100–500ms the target for Node-class runtimes; 500ms–2s tolerable; >2s users avoid the tool. Benchmark with `time mycli`.
- **Progress for anything long**: spinners/progress bars (estimated time or animation so it never looks stuck); multiple bars for parallel work (docker pull is the model); if progress bars hide logs, dump the logs on failure.
- **Timeouts** on network ops, configurable, with sane defaults — never hang forever.
- **Recoverable & crash-only**: failure + up-arrow + enter should resume; design so no cleanup is required on exit (defer cleanup to next run). Crash-only design makes Ctrl-C safe and the tool feel instant.
- **Ctrl-C (SIGINT): exit ASAP**, say something immediately, timeout your cleanup; second Ctrl-C skips graceful cleanup (docker-compose model) — warn if that's destructive.
- **Expect misuse**: wrapped in scripts, flaky networks, parallel instances, case-insensitive filesystems.

## 11. Configuration & environment variables

**Three configuration categories → three mechanisms:**

| Varies per... | Examples | Mechanism |
|---|---|---|
| Invocation | debug level, dry-run | Flags (maybe env vars) |
| Machine/user | paths, color, proxy | Env vars (+ flags); config file if complex |
| Project (all users) | build matrix, services | Version-controlled file (`package.json`, `compose.yml` style) |

- **Precedence (highest → lowest): flags → env vars → project config (`.env`) → user config → system config.**
- **Follow XDG**: `$XDG_CONFIG_HOME` / `~/.config/myapp` for config, `~/.local/share/myapp` for data, `~/.cache/myapp` for cache (macOS: `~/Library/Caches/myapp`; Windows: `%LOCALAPPDATA%\myapp`). No new dotfiles in `$HOME`.
- **Don't silently edit config that isn't yours**; prefer a new file (`/etc/cron.d/myapp`) over appending; if you must append, use dated comments.
- **Env var hygiene**: `UPPER_SNAKE` names only, single-line values, don't shadow POSIX-standard names.
- **Honor general-purpose env vars**: `NO_COLOR`/`FORCE_COLOR`, `DEBUG`, `EDITOR`, `HTTP(S)_PROXY`/`NO_PROXY`, `SHELL`, `TERM`, `TMPDIR`, `HOME`, `PAGER`, `LINES`/`COLUMNS`.
- **Read `.env`** for project-scoped vars, but don't use `.env` as the config file (untracked, stringly-typed, encoding-fragile, tends to accumulate secrets).
- **No secrets from env vars** (see §7) — files/pipes/sockets/secret managers only.

## 12. Future-proofing (interfaces are contracts)

Subcommands, args, flags, config files, env vars are all public interfaces — breaking them requires deprecation.

- **Keep changes additive**: add a new flag rather than changing a flag's behavior.
- **Warn before non-additive changes**, in-program, with migration instructions; stop warning once the user has migrated.
- **Human output may change; machine output may not.** Point scripts at `--plain`/`--json` so you keep freedom to iterate on the human format.
- **No time bombs**: avoid hard runtime dependencies on servers that may disappear (including blocking analytics calls).
- **Semver applies, but monthly majors make it meaningless** — design to avoid breaks instead.

## 13. Naming, distribution & analytics

- **Name**: simple memorable word, lowercase, short but not `cd`-short, easy to type (Docker Compose's `plum` → `fig` story), not colliding with existing commands (`convert` collision: ImageMagick vs Windows).
- **Distribution**: single binary if possible; otherwise the platform's native installer; tread lightly on the user's disk; language-specific dev tools (linters) may assume the runtime exists. **Make uninstalling easy and documented.**
- **Analytics**: never phone home without consent; opt-in preferred; if opt-out, disclose loudly and make disabling trivial. Alternatives: instrument docs and downloads, talk to users.

## 14. Agent-first CLI design (the 2025–2026 layer)

The major new development since clig.dev: AI coding agents are now first-class CLI users, and CLIs are becoming "agent APIs". Comparative studies cited in the ecosystem found CLI-based agents dramatically cheaper on tokens (10–32×) and more reliable than MCP-based equivalents for developer tasks, accelerating CLI investment. Agents differ from humans: they don't google errors, they parse output literally, they hallucinate flags, they pay per token, and they keep going after failures unless told to stop.

Consensus principles across Arcjet, Memori, nibzard, and the emerging "agent-native CLI" specs:

1. **Dual output modes everywhere**: human-readable by default, structured JSON via `--json`/`--output json` on *every* command. Stable schemas; treat them as API contracts.
2. **Help text is a contract, not prose**: complete usage, args, flags, realistic examples, output modes, and exit codes; versioned and stable. Consider machine-readable self-description (`--describe`, `--help --json`, or a schema command) so agents can introspect at runtime.
3. **Exit codes as API**: explicit, distinct, documented codes per failure class; never exit 0 on failure.
4. **Structured errors**: in JSON mode emit a machine-parseable error object (type, message, offending input id) on stderr; errors should "teach" the recovery step.
5. **Strict input hardening**: validate everything before network calls/side effects; assume adversarial or hallucinated input (control characters, path traversal, pasted IDs in wrong slots); fail closed.
6. **Explicit confirmation for mutations**: agents lack judgment about risk; production-changing commands require an explicit confirmation round trip or `--confirm` token — never just an interactive "are you sure?" that an agent can't see.
7. **Determinism**: predictable command shapes, deterministic stdout/stderr separation, no output that requires inferring state from prose.
8. **Non-interactive auth paths**: agents can't drive a browser; provide token/file-based auth.
9. **Convergence claim** (worth keeping in the skill): designing for agents = designing well, period. Structured output, teaching errors, good defaults, and graceful degradation also improve the human experience.

## 15. TypeScript implementation patterns (2026 ecosystem)

### 15.1 Argument-parsing / framework landscape

| Tool | Position | Notes |
|---|---|---|
| `node:util.parseArgs` | Built-in, zero-dep | Fine for tiny single-command tools; no help generation, no subcommand routing; works in Node/Bun/Deno. |
| **citty** (UnJS) | Lightweight declarative builder | Zero-dep, built on `util.parseArgs`, typed args incl. enum→union types, nested subcommands with *lazy async imports*, auto usage, setup/cleanup hooks, ESM-only. Powers UnJS tooling. |
| **Commander** | Most popular general-purpose | ~Hundreds of millions of weekly downloads, zero dependencies, minimal API, good TS support, fastest of the big three (~18–25ms overhead in benchmarks vs ~12ms bare). Manual type coercion/choices. |
| **yargs** | Feature-rich parser | Built-in type coercion, choices validation, typo suggestions, middleware, completion; heavier (~35–48ms). |
| **oclif** | Enterprise framework (Heroku/Salesforce) | File-based command scaffolding, plugin system, auto-docs, testing utilities, hooks; ~30 deps and the slowest startup (~85–135ms); the 12-Factor reference implementation. |
| **Clipanion** | Class-based, type-safe | Powers Yarn; designed for very complex CLIs; type safety via class syntax. |
| **Stricli** (Bloomberg) | Zero-dep, strict TS | Explicitly built on clig.dev; types for flags/positionals flow through the whole app; commands defined separately from params → lazy ESM imports/code-splitting (`--help` without loading runtime deps); DI-friendly single context object for all system access (great for testing); runtime-JS shell-agnostic autocomplete; deliberately narrow scope (bring your own prompts/colors). Node/Bun/Deno. |

**Decision heuristic for the skill:**
- Tiny script/one command → `util.parseArgs` or citty.
- Typical product CLI, few–many commands → **Commander** (default), or **citty** if ESM/UnJS-style declarative is preferred.
- Strict type-flow, testability via DI, zero deps, large CLI → **Stricli** or Clipanion.
- Plugin ecosystem / team scaffolding / auto-docs needed → **oclif** (accept the startup cost).
- Startup time matters for frequently-invoked tools — measure with `time mycli --version`.

### 15.2 Interaction & presentation libraries

- **Prompts**: `@clack/prompts` is the modern default (TS-native, ESM, tiny, `intro/outro`, `group()`, cancellation via `isCancel`); **Enquirer** when you need exotic prompt types (autocomplete, scale, etc.); **Inquirer** is the legacy incumbent. Always pair prompts with non-interactive flag equivalents (§8).
- **Full TUI**: **Ink** (React for the terminal) only when genuinely stateful live-updating UI is needed (parallel progress dashboards); ~150KB + React overhead otherwise unjustified.
- **Color**: `picocolors` (smallest) or `chalk`; whatever you choose must respect the §5 disable matrix (most libs auto-detect TTY + `NO_COLOR`, but verify `FORCE_COLOR`).
- **Spinners/progress**: `ora`, `node-progress`-style libs; must no-op when not a TTY.
- **Tables**: keep §5 rules (no borders, one record/line) — prefer plain `string.padEnd` layouts or minimal table libs over border-drawing ones.

### 15.3 Project & code structure

- `package.json` `"bin"` field + `#!/usr/bin/env node` shebang; `"type": "module"` (ESM-first; ship CJS only if consumers demand it).
- One file per command (oclif convention; works in any framework) + lazy-load command modules so `--help`/`--version` stay fast (citty lazy `subCommands`, Stricli's separated command defs).
- Separate **pure core from I/O shell**: command handlers parse/validate, then call pure functions; all system access (fs, net, clock, stdout) behind an injected context (Stricli's context-object pattern) → unit-testable without spawning processes.
- Centralize the output layer: one module that knows about TTY detection, `--json`, `--plain`, `--quiet`, color — commands emit semantic events/records, the layer renders them. One error formatter used by every command (human vs JSON mode).
- Exit-code map as a typed constant (`enum ExitCode`), never scattered `process.exit(1)`.

### 15.4 Build, test, distribute

- **Bundle** with esbuild/tsup/tsdown into a single JS file for fast startup (fewer module resolutions) and clean `npx` usage.
- **Distribution tiers**: (a) npm (`npx mycli`, fine for dev-audience tools — clig.dev's "language-specific tool" exemption); (b) single executables for general audiences: `bun build --compile`, Node Single Executable Applications (SEA), or pkg-style bundlers — note binary size includes the runtime.
- **Testing**: unit-test the pure core; for parsing/integration, prefer in-process invocation of the command function with an injected context (Stricli/DI pattern) over spawning; add a small set of end-to-end `child_process` tests asserting exit codes, stdout vs stderr separation, `--json` schema, and `NO_COLOR` behavior — these encode the §3/§5 contracts as regression tests.
- **CI checks worth automating**: `time mycli --version` budget, `--help` snapshot, JSON-schema validation of `--json` output, no ANSI codes when piped.

## 16. Anti-pattern checklist (distill into the skill's NEVER list)

- Errors or logs on stdout; data on stderr.
- Exit 0 on failure; one generic exit 1 for everything (agents can't branch).
- Hand-rolled arg parsing; `-h` meaning anything but help.
- Required interactivity (prompt with no flag equivalent); prompting when stdin isn't a TTY.
- ANSI/spinners written to non-TTY (CI logs); ignoring `NO_COLOR`/`TERM=dumb`.
- Secrets via flags or env vars.
- Catch-all subcommands; prefix abbreviations; ambiguous sibling commands (`update`/`upgrade`).
- Silent state changes; silent file/network access outside given args.
- Table borders; multi-line records in machine output without `--plain`.
- Raw stack traces as the user-facing error; log-level labels by default.
- New dotfiles in `$HOME`; editing other programs' config silently.
- Telemetry without consent; blocking startup on network calls.
- Breaking flag semantics without a deprecation warning cycle.
- Hanging with no output >100ms; no timeout on network operations.

## 17. Notes for distilling into SKILL.md

Per instructions-best-practices: the skill should be a small testable behavior contract, not this document.

- **SKILL.md body**: the non-negotiables (§3), the decision heuristics (framework choice §15.1, config mechanism table §11, danger tiers §7), the NEVER list (§16), and the agent-first additions (§14 items 1–6) — these are the observable, transcript-testable behaviors.
- **`references/`**: full flag-name conventions table, env-var list, library comparison details, distribution recipes, and this document as the source dump.
- **Description/trigger**: fire when designing, building, reviewing, or refactoring a CLI (TypeScript/Node/Bun), or when choosing CLI libraries — not for general terminal usage questions.
- **Force calibration**: reserve MUST/NEVER for §3 + §16 (stdout/stderr, exit codes, secrets, required prompts); everything else is "prefer/default" guidance.
