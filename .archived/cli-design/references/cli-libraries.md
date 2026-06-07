# CLI Supporting Libraries

Categories of supporting libraries a production CLI typically needs, where each belongs in the layering, and what to look for when choosing. Library names below are representative starting points — they churn (maintenance status, ESM-only migrations, new entrants), so verify the current state before adopting. The durable parts are the **categories, the selection criteria, and the layering rules** — not the specific names.

## Check the standard library first

Reach for a dependency only when the built-in is insufficient. Modern Node covers several CLI needs natively:

- **Color**: `util.styleText` (stable since Node 22.13) — respects `NO_COLOR`, `FORCE_COLOR`, `NODE_DISABLE_COLORS`. Removes the need for a color library in simple cases.
- **Arg parsing**: `util.parseArgs` (stable since Node 20) — fine for basic flags; reach for a framework or heavier parser only for subcommands, validation, and help generation.
- **Env files**: `node --env-file=.env` and `process.loadEnvFile()` (stable in the Node 24 line; available earlier behind experimental status) — replace `dotenv` for most uses. `util.parseEnv` is newer and still in active development.
- **Subprocess**: `node:child_process` exists, but a wrapper (below) is far more ergonomic for real use.
- **Async flow**: `AbortController`/`AbortSignal` handle cancellation and timeouts; `Promise.allSettled` handles fan-out. Reach for a concurrency/retry library only beyond these.
- **HTTP**: `fetch` is global — add a client library only for retry/timeout/instrumentation ergonomics.
- **Signals**: `process.on('SIGINT' | 'SIGTERM')` covers graceful shutdown and cleanup; a helper is only needed to restore terminal state (cursor) on exit.
- **Paging long output**: spawn the user's `$PAGER` (default `less -FIRX`) via the subprocess wrapper when stdout is a TTY — the few pager packages on npm are small and unmaintained; don't add one.

## Where each category lives

Map every supporting library to a layer; never import any of them into the `core` (`core/services`/`core/domain`).

- `ui/`: color, spinners, progress, tables, prompts, diff rendering, human-readable formatting, fuzzy filtering for pickers, terminal string handling.
- `lib/`: logger, config loader, format parsers (YAML/TOML/INI), human-input parsers (range/duration/size), semver, path resolution, cross-process locking, process lifecycle and cleanup.
- `adapters/`: subprocess, HTTP, filesystem, stdin, file watching, opening URLs/files, `$EDITOR` integration.

Human-input parsers are pure functions — call them from the command boundary as part of flag validation (alongside Zod), then hand core the parsed value, never the raw string.

**Gate all TTY-dependent output behind `ui`** so a single place can disable spinners/color/progress/prompts when output is not a TTY, or when `--json` / `--quiet` is set. Do not call spinner/color libraries directly from command handlers.

## Note on batteries-included frameworks

Some CLI frameworks bundle color, table, spinner, and prompt helpers (e.g. an `ux`-style namespace). Check what the chosen framework already provides before adding leaf libraries — avoid duplicating it.

## Categories

| Category | What to look for | Representative libraries |
|---|---|---|
| Color / styling | Tiny, zero/few deps, honors `NO_COLOR` | stdlib `util.styleText`; `picocolors`, `chalk` (v5 is ESM-only), `kleur`, `colorette` |
| Spinner | `start`/`stop`/`succeed`/`fail`, TTY-aware | `ora`, `nanospinner`, `yocto-spinner` |
| Progress bar | Single determinate bar | `cli-progress` |
| Live output region | Overwrite previous lines for custom multi-line status — the step between a spinner and full ink | `log-update` |
| Multi-step task runner | Task tree, concurrency, per-task status — for staged pipelines | `listr2` |
| Table / structured display | Column layout, wrapping, alignment | `cli-table3` |
| Interactive prompts | Confirm/select/multiselect/autocomplete, cancellation handling | `@clack/prompts` (modern default), `@inquirer/prompts`, `enquirer` (advanced types) |
| Fuzzy filtering | Match-as-you-type filtering of long lists in pickers/autocomplete (distinct from typo suggestions below) | `fzf` (JS port of the fzf algorithm), `fuzzysort` (fast, small), `fuse.js` (weighted/configurable) |
| `$EDITOR` integration | Long free-form input via the user's editor, git-commit style | `@inquirer/external-editor` (`external-editor` is unmaintained) |
| Full terminal UI (TUI) | A bounded interactive view inside an otherwise command-based CLI (a live progress dashboard, a picker). Reach for this only for that contained surface — a full-screen, vim/emacs-style app is outside this skill's scope. | `ink` (React for the terminal) |
| Logging | Structured JSON for machine/agent consumption, levels, redaction | `pino` (structured), `consola` (pretty CLI), `winston` |
| Config file loading | Discovery + precedence merge | `cosmiconfig` (discovery), `rc` |
| Config format parsers | Parse/serialize YAML, TOML, INI, JSON5/JSONC config and data files | `yaml`, `smol-toml`, `ini`, `jsonc-parser` / `json5`; `confbox` bundles all of these; `csv-parse` / `papaparse` for CSV data |
| Persistent config store | Read/write a user config that survives runs | `conf` |
| Cross-platform paths | Correct config/data/cache dirs per OS (XDG, AppData, Library) | `env-paths` |
| Subprocess execution | Ergonomic spawn, piping, typed errors, cancellation | `execa` |
| Stdin input | Read piped stdin; support `-` as a filename per the behavior contract | `get-stdin`, `file-or-stdin` |
| Shell quoting / splitting | Safely quote args for display/forwarding; split a command string into argv (tests, `--exec`-style flags) | `shell-quote`, `string-argv` |
| Async concurrency & resilience | Bounded parallelism, retry with backoff, timeouts for batch/network work | `p-limit`, `p-queue`, `p-map`, `p-retry`, `p-timeout` |
| Schema validation | Validate args/flags/config at the boundary | `zod`, `valibot` |
| Human-input parsing | Parse human-friendly flag values at the boundary: ranges (`--pages 1-5,8`), durations (`--timeout 30s`), sizes (`--max-size 1.5GB`) | `multi-integer-range` (normalized range pairs; `parse-numeric-range` only for small flat lists), `ms` / `parse-duration` (durations), `bytes` (sizes, parses both ways); `chrono-node` for natural-language dates ("yesterday") when the use case calls for it |
| Semver handling | Compare/parse versions: update checks, `engines` checks, stored-config schema migrations | `semver` (the parser npm itself uses) |
| Diff rendering | Text diff for previews and approval flows | `diff` (jsdiff) |
| Filesystem / globbing | Globbing, recursive ops beyond stdlib | `fast-glob` / `globby`, `fs-extra` |
| HTTP client | Retry, timeout, typed responses over `fetch` | global `fetch`; `ky`, `got`, `undici` |
| Open URLs / files | Launch the default browser or app (OAuth, reveal output) | `open` |
| File watching | `--watch` mode: rerun on change | stdlib `fs.watch`; `chokidar` |
| Human-readable formatting | Durations, byte sizes, relative times for display | `pretty-ms`, `pretty-bytes`, `ms` |
| Process lifecycle & cleanup | Graceful `SIGINT`/`SIGTERM` shutdown; restore cursor/terminal after spinners | stdlib `process.on(...)`; `signal-exit`, `restore-cursor` |
| Cross-process locking | Prevent two concurrent runs corrupting shared state/config files; single-instance daemons | `proper-lockfile` (stale-lock detection, crash cleanup) |
| Terminal string handling | Correct display width (CJK/emoji), strip ANSI, cursor escapes for custom rendering | `string-width`, `strip-ansi`, `ansi-escapes` |
| Terminal capability detection | Truly-interactive check (TTY *and* not CI/dumb), Unicode support for symbol fallbacks, size even when piped | `is-interactive`, `is-unicode-supported`, `terminal-size` |
| Command suggestions | "Did you mean?" on typos; fuzzy command/option matching | `leven`, `didyoumean2` (often built into frameworks) |
| Shell completion | Generate/install tab-completion scripts | framework built-ins first (yargs, oclif, stricli ship it); `@pnpm/tabtab` (maintained fork of `tabtab`) |
| UX polish (optional) | Small touches added when needed | `boxen`, `figures` (cross-platform symbols), `terminal-link`, `wrap-ansi`, `cli-truncate`, `update-notifier` |
| Situational | Add only when the use case calls for it | `node-notifier` (desktop notify), `clipboardy` (clipboard), `marked` + `marked-terminal` (render markdown), `cli-highlight` (syntax-highlight code output; widely used but dormant), `eta`/`handlebars` (templating for scaffolders) |

## Selection principles

- **Stdlib first, then small leaf libraries.** For color/spinner/parsing, prefer the built-in or a zero/few-dependency package over a heavy one.
- **Prefer actively maintained and ESM-compatible packages.** Many popular CLI libraries went ESM-only (e.g. `chalk` v5, `execa`); confirm the module format matches the build setup before adopting, or pin an older major when CJS is required.
- **Use structured (JSON) logging** for any CLI meant to be consumed by scripts, CI, or agents — not just pretty console output.
- **Do not duplicate framework-provided helpers**, and do not add a dependency for something the standard library now does.
- **Keep every TTY-dependent library behind the `ui` layer** so non-interactive modes suppress them in one place.
