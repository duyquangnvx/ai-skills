---
name: cli-design
description: Best practices and standard patterns for designing and building command-line tools, primarily in TypeScript on Node/Bun. Use whenever the task involves creating a new CLI, adding commands or flags to an existing one, reviewing or refactoring CLI code, choosing CLI libraries (argument parsing, prompts, colors, output), designing help text, errors, exit codes, or configuration, persisting user config/credentials/cache, or making a CLI scriptable and safe for AI agents — even when the user says "terminal tool", "command", "script with flags", or "npx tool" instead of "CLI". Do NOT use for full-screen TUI applications (vim/emacs-style).
---

# CLI Design

A CLI's command surface — flags, output shapes, exit codes, config locations — is a public API. Design it like one. This skill condenses clig.dev, the 12-Factor CLI principles, POSIX/GNU conventions, and 2025–2026 agent-first practice; ecosystem facts were adversarially verified (June 2026 snapshot). Read `references/conventions.md` before inventing any flag, env var, or file location; read `references/typescript-stack.md` before picking libraries or project structure; read `references/user-data-storage.md` before persisting anything for the user.

## Non-negotiables

Violating these makes a CLI broken or a bad citizen in pipes, scripts, CI, and agents:

- **Exit 0 on success, distinct non-zero codes per failure class.** Define a single typed exit-code map; never scatter bare `process.exit(1)`. Scripts and agents branch on these.
- **stdout is for output, stderr is for messaging.** Data and machine-readable results → stdout. Logs, warnings, errors, progress → stderr, so pipes stay clean while humans still see messages.
- **Use an argument-parsing library** (see stack reference). Never hand-roll `process.argv` parsing for anything beyond a throwaway script.
- **`-h`/`--help` always shows help and means nothing else.** Bare invocation with missing required args shows concise help (description, 1–2 examples, key flags) instead of erroring or hanging. `--version` always works.
- **NEVER accept secrets via flags, never persist them into `.env`** — flags leak through `ps` (visible to every user) and shell history. Accept secrets via files (`--token-file`), stdin, stored credentials (see storage reference), or a `MYTOOL_API_KEY`-style env var — the standard injection path for dev and CI; just be aware env vars inherit into child processes and can leak via crash dumps, `docker inspect`, and verbose logs.
- **Never require interactivity.** Every prompt has a flag/arg equivalent. Skip prompts entirely when stdin is not a TTY or `--no-input` is passed — fail with the flag the user should pass instead.

## Adaptive output

Per-stream TTY detection is the master switch: check stdout and stderr individually (`process.stdout.isTTY`).

- TTY → human mode: color, spinners, formatted tables. Not a TTY → plain text, no ANSI codes, no animations (spinners become garbage in CI logs).
- Provide `--json` on every command that outputs data, with a stable schema treated as an API contract. Human-readable format may evolve freely; JSON may not.
- Disable color when any of: stream is not a TTY, `NO_COLOR` is set (non-empty), `TERM=dumb`, `--no-color`. Honor `FORCE_COLOR` to override.
- Print brief output on success (pure silence looks broken); offer `-q`/`--quiet` for scripts. When a command changes state, say what changed and suggest the next command (`git push` / `git status` are the models).
- Tables: one record per line, never borders, headers hideable — so `grep`/`wc` work. Offer `--plain` when the human layout wraps or merges lines.

## Errors

Errors are documentation. A good error has: what failed, why, **how to fix it** ("Can't write file.txt — run: chmod +w file.txt"), and optionally a docs URL. Put the most important line last (where the eye lands). Group repeated similar errors under one header. Never show raw stack traces by default — keep them behind `--verbose`/`DEBUG`, or write a debug log file and print its path. If the user typo'd a command and you can guess the fix, suggest it ("Did you mean `ps`?") but don't auto-run it.

## Arguments & flags

- **Prefer flags to positional args** — clearer and forward-compatible. One type of positional is fine, two is suspect, three is wrong (variable-length lists of the *same* type are fine: `rm a b c`).
- Every flag has a long form; reserve short letters for the most common operations. Use the standard names in `references/conventions.md` (`-f/--force`, `-n/--dry-run`, `-o/--output`, ...) before inventing new ones.
- Support `--` to stop flag parsing (pass-through wrappers) and `-` as a stdin/stdout placeholder for file args.
- Defaults must be right for most users — configurability doesn't excuse bad defaults.
- **Confirmation tiers for destructive actions:** mild (delete a file) → optional confirm; moderate (delete a directory/remote resource, bulk edit) → confirm + offer `--dry-run`; severe (delete an app/database) → require typing the resource name, with `--confirm=<name>` for scripts.

## Subcommands

For multi-command CLIs: `noun verb` ordering (`app db migrate`), consistent verbs across nouns, same flag names for the same concepts everywhere. Bare invocation lists commands/help — never runs a default action. Two traps that permanently block evolution: a catch-all subcommand (unknown first arg treated as implicit `run`) and arbitrary prefix abbreviations (`mycmd i` for `install`). Explicit stable aliases are fine.

## Configuration

Precedence, highest first: **flags → env vars → project config → user config → system config**. Choose the mechanism by volatility: per-invocation values → flags; per-machine/user values → env vars; per-project shared values → a version-controlled file. Follow XDG (`~/.config/myapp`, `~/.cache/myapp`) — no new dotfiles in `$HOME`. Honor general-purpose env vars (`NO_COLOR`, `DEBUG`, `EDITOR`, `HTTP_PROXY`, `PAGER`, ...; full list in conventions reference). For where every file lives, credentials, and cache layout, see `references/user-data-storage.md`.

## Performance & robustness

- **Print something within 100ms**; print *before* slow network calls, not after. Startup budget: aim for 100–500ms on Node; bundle to a single file and lazy-load command modules so `--help` stays fast.
- Show progress (spinner/bar with motion or ETA) for anything long; if progress bars hide logs, dump the logs on failure. Network calls always have configurable timeouts.
- Ctrl-C exits as soon as possible: acknowledge immediately, time-box cleanup, let a second Ctrl-C skip graceful shutdown. Prefer crash-only design (no required cleanup; recover on next run) so interruption is always safe. Node detail: installing a `SIGINT`/`SIGTERM` listener removes the default exit — the handler must clean up and `process.exit(128 + n)` itself (see stack reference).
- Validate input early and fail before any side effect.

## Agents are users too

AI agents are now first-class CLI users, and they fail differently from humans: they parse output literally, hallucinate flags, can't read interactive prompts, and keep going after errors. Design accordingly — it improves the human experience too:

- `--json` everywhere, with structured errors in JSON mode (machine-parseable `type`, message, offending input) on stderr.
- Help text is a contract: complete usage, flags, realistic examples, output modes, and exit codes, kept stable across versions. Consider `--describe`/schema introspection for API-backed CLIs.
- Harden inputs: assume pasted/hallucinated values — reject control characters, path traversal, malformed IDs — before any network call.
- Mutations to shared/production state require an explicit non-interactive confirmation path (`--confirm` token), not just a TTY prompt.
- Provide token/file-based auth; agents can't drive a browser.

## The one architectural rule that matters most

Keep commands thin and the core fat. A command file does exactly three things — parse args/flags, call a core function, format the result. Business rules live in core functions that know nothing about argv, the parsing framework, or `console`. This is what makes the CLI unit-testable without spawning processes. Structure scales with the CLI — a single file until it hurts, then one module per command; do NOT impose backend layering before the code needs it, or add interface indirection (core depending on adapter interfaces/mocks) — premature indirection is hard to trace, and folder *names* are never the issue. Grouping deep modules into folders, context-injection, reporter, and error-boundary patterns: `references/architecture.md`.

## Choosing the TypeScript stack

Quick heuristic (details, corrections to vendor marketing, and build/test/distribution recipes in `references/typescript-stack.md`):

- Tiny one-command tool → `node:util.parseArgs` or **citty**.
- Typical product CLI → **Commander + @commander-js/extra-typings** (default) or **citty** (declarative/ESM, lazy subcommands).
- Plugin ecosystem, scaffolding, auto-docs → **oclif** (accept the startup cost; generate the manifest).
- Prompts → `@inquirer/prompts` or `@clack/prompts`. Colors → `util.styleText` (built-in). Bundler → **tsdown** (tsup is unmaintained). ESM-only is now safe.

## Review checklist

Before shipping a CLI change, verify: exit codes distinct and mapped · stdout/stderr separation · `-h`, `--help`, `--version` work · no ANSI when piped, `NO_COLOR` honored · `--json` schema stable · every prompt has a flag equivalent and is skipped when not a TTY · destructive ops have the right confirmation tier and `--dry-run` · errors say how to fix · no secrets via flags/env · config in XDG paths with correct precedence · credentials in the OS keychain · first output under 100ms · commands thin, core framework-free · breaking changes preceded by an in-program deprecation warning.

## References

- `references/conventions.md` — standard flag names, env vars, exit codes, XDG paths, config precedence, deprecation protocol. Read when naming anything.
- `references/typescript-stack.md` — framework comparison (verified, vendor-bias corrected), supporting libraries, signal handling, testing, bundling and distribution. Read when picking dependencies.
- `references/architecture.md` — thin-command/fat-core, progressive structure, context injection, the reporter, error boundary, bootstrap order, startup performance, cross-platform. Read when scaffolding or restructuring a CLI codebase.
- `references/user-data-storage.md` — persisting config, credentials, projects, cache: layout shapes, cross-platform locations, credential storage (`0600` file vs keychain tradeoff), atomic writes and sync-safe soft-deletes, path-resolution module. Read when the CLI must store anything for the user.
