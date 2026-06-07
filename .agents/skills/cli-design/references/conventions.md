# CLI Conventions Reference

Lookup tables for naming and placement decisions. Source: clig.dev, GNU Coding Standards, POSIX Utility Conventions, XDG Base Directory spec, no-color.org.

## Standard flag names

Use these before inventing new names. A user who knows one CLI should be able to guess yours.

| Flag | Meaning | Notes |
|---|---|---|
| `-a`, `--all` | Include everything | `ps`, `fetchmail` |
| `-d`, `--debug` | Debug output | |
| `-f`, `--force` | Skip confirmation / force destructive action | Required for scripting dangerous commands |
| `--json` | JSON output | Should exist on every data-emitting command |
| `--plain` | One record per line, no decoration | For grep/awk when human layout wraps lines |
| `-h`, `--help` | Help — and nothing else | Never overload `-h` |
| `-n`, `--dry-run` | Describe changes without applying | `rsync`, `git add -n` |
| `--no-input` | Disable all prompts | Fail with instructions if input was required |
| `--no-color` | Disable color | Alongside `NO_COLOR` env |
| `-o`, `--output` | Output file | `sort`, `gcc` |
| `-p`, `--port` | Port | `psql`, `ssh` |
| `-q`, `--quiet` | Suppress non-essential output | For scripts |
| `-u`, `--user` | User | `ps`, `ssh` |
| `--version` | Version | Also `version` subcommand for multi-command CLIs |
| `-v` | Ambiguous: verbose OR version | Pick one meaning and never both; consider `-d` for verbose |
| `--confirm=<name>` | Scriptable severe-action confirmation | Pairs with type-the-name interactive confirm |

Other syntax rules:

- `--flag value` and `--flag=value` should both work.
- `--` terminates flag parsing; everything after passes through verbatim (essential for wrapper commands).
- `-` as a file argument means stdin (input) or stdout (output).
- Optional flag values need an explicit sentinel like `none` (`ssh -F none`), never a blank.
- Flags should work in any position relative to subcommands where the parser allows.

## Exit codes

- `0` = success. Anything else = failure. Map distinct codes to your most important failure classes (e.g. `1` general, `2` usage/validation error, higher codes per domain failure) and document them in help.
- Keep the map in one typed constant (`enum ExitCode`) — never scatter magic numbers.
- BSD `sysexits.h` (64–78) is an optional vocabulary (64 = usage, 69 = unavailable, 77 = permission); consistency within your CLI matters more than matching it.
- Reserved by shells: 126 (found but not executable), 127 (not found), 128+N (killed by signal N). Don't use these for your own meanings.

## Environment variables to honor

| Variable | Behavior |
|---|---|
| `NO_COLOR` | Non-empty (any value) → disable color |
| `FORCE_COLOR` | Enable color, overriding TTY detection |
| `TERM=dumb` | Disable color and fancy output |
| `MYAPP_NO_COLOR` | App-specific color kill switch (recommended) |
| `DEBUG` | Verbose/component-level debug logging |
| `EDITOR` | Editor to open for multi-line input |
| `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` | Proxy network calls (HTTP libs often handle this) |
| `SHELL` | User's preferred interactive shell |
| `TMPDIR` | Temp file location |
| `HOME` | Locating user config |
| `PAGER` | Pager for long output (default `less -FIRX`, only when TTY) |
| `LINES`, `COLUMNS` | Screen-size-dependent layout |

Defining your own: `UPPER_SNAKE` only, no leading digit, single-line values, prefix with the app name (`MYAPP_*`), never shadow POSIX-standard names.

## Configuration precedence and placement

Precedence (highest wins): **flags → shell env vars → project config (`.env` / committed file) → user config → system config**.

Mechanism by volatility:

| Configuration varies per... | Examples | Mechanism |
|---|---|---|
| Invocation | debug level, dry-run | Flags |
| Machine / user | paths, proxy, color preference | Env vars (+ flags); own config file only if complex |
| Project, shared by all users | services, build matrix | Version-controlled file (like `package.json`, `compose.yml`) |

XDG paths (respect the env vars; fall back to defaults):

| Purpose | Env var | Default |
|---|---|---|
| Config | `XDG_CONFIG_HOME` | `~/.config/myapp` |
| Data | `XDG_DATA_HOME` | `~/.local/share/myapp` |
| Cache | `XDG_CACHE_HOME` | `~/.cache/myapp` (macOS: `~/Library/Caches/myapp`; Windows: `%LOCALAPPDATA%\myapp`) |

Rules:

- No new dotfiles directly in `$HOME`.
- Read `.env` for project-scoped vars, but `.env` is not a config file (untracked, stringly-typed, attracts secrets).
- Never silently modify config that belongs to another program; prefer creating a new file (`/etc/cron.d/myapp`), and use dated comments if you must append.
- Secrets: files, stdin, pipes, OS keychain, or secret managers only — never flags, never env vars.

## Naming the binary

Simple memorable word · lowercase, dashes only if necessary · short but not `cd`-short · easy to type with two hands · no collision with existing commands (the `convert` collision between ImageMagick and Windows is the cautionary tale).

## Deprecation protocol

Subcommands, flags, args, config keys, env vars, and JSON output schemas are all public interfaces.

1. Prefer additive change (new flag) over changed behavior.
2. If a break is unavoidable: emit an in-program warning when the old form is used, with exact migration instructions; suppress the warning once usage has migrated; only then remove.
3. Human-readable output may change freely — direct scripts to `--plain`/`--json`, whose formats are frozen contracts.
4. Never make the CLI's startup depend on a network endpoint (no blocking analytics, no online-only version checks).

## Telemetry

Off by default or clearly disclosed opt-out at minimum; opt-in preferred. Disclose what, why, anonymization, retention. Trivial to disable. Alternatives: instrument docs/downloads, talk to users.
