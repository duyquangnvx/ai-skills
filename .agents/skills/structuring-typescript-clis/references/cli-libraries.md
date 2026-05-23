# CLI Supporting Libraries

Categories of supporting libraries a production CLI typically needs, where each belongs in the layering, and what to look for when choosing. Library names below are representative starting points — they churn (maintenance status, ESM-only migrations, new entrants), so verify the current state before adopting. The durable parts are the **categories, the selection criteria, and the layering rules** — not the specific names.

## Check the standard library first

Reach for a dependency only when the built-in is insufficient. Modern Node covers several CLI needs natively:

- **Color**: `util.styleText` — respects `NO_COLOR`, `FORCE_COLOR`, `NODE_DISABLE_COLORS`. Removes the need for a color library in simple cases.
- **Arg parsing**: `util.parseArgs` — fine for basic flags; reach for a framework or heavier parser only for subcommands, validation, and help generation.
- **Env files**: `node --env-file=.env`, `process.loadEnvFile()`, `util.parseEnv` — replace `dotenv` for most uses.
- **Subprocess**: `node:child_process` exists, but a wrapper (below) is far more ergonomic for real use.

## Where each category lives

Map every supporting library to a layer; never import any of them into `core/`.

- `ui/`: color, spinners, progress, tables, prompts, diff rendering.
- `lib/`: logger, config loader, path resolution.
- `adapters/`: subprocess, HTTP, filesystem helpers.

**Gate all TTY-dependent output behind `ui/`** so a single place can disable spinners/color/progress/prompts when output is not a TTY, or when `--json` / `--quiet` is set. Do not call spinner/color libraries directly from command handlers.

## Note on batteries-included frameworks

Some CLI frameworks bundle color, table, spinner, and prompt helpers (e.g. an `ux`-style namespace). Check what the chosen framework already provides before adding leaf libraries — avoid duplicating it.

## Categories

| Category | What to look for | Representative libraries |
|---|---|---|
| Color / styling | Tiny, zero/few deps, honors `NO_COLOR` | stdlib `util.styleText`; `picocolors`, `chalk` (v5 is ESM-only), `kleur`, `colorette` |
| Spinner | `start`/`stop`/`succeed`/`fail`, TTY-aware | `ora`, `nanospinner`, `yocto-spinner` |
| Progress bar | Single determinate bar | `cli-progress` |
| Multi-step task runner | Task tree, concurrency, per-task status — for staged pipelines | `listr2` |
| Table / structured display | Column layout, wrapping, alignment | `cli-table3` |
| Interactive prompts | Confirm/select/multiselect/autocomplete, cancellation handling | `@clack/prompts` (modern default), `@inquirer/prompts`, `enquirer` (advanced types) |
| Full terminal UI (TUI) | When the CLI is stateful enough to need a render loop | `ink` (React for the terminal) |
| Logging | Structured JSON for machine/agent consumption, levels, redaction | `pino` (structured), `consola` (pretty CLI), `winston` |
| Config file loading | Discovery + precedence merge | `cosmiconfig` (discovery), `rc` |
| Persistent config store | Read/write a user config that survives runs | `conf` |
| Cross-platform paths | Correct config/data/cache dirs per OS (XDG, AppData, Library) | `env-paths` |
| Subprocess execution | Ergonomic spawn, piping, typed errors, cancellation | `execa` |
| Schema validation | Validate args/flags/config at the boundary | `zod`, `valibot` |
| Diff rendering | Text diff for previews and approval flows | `diff` (jsdiff) |
| Filesystem / globbing | Globbing, recursive ops beyond stdlib | `fast-glob` / `globby`, `fs-extra` |
| UX polish (optional) | Small touches added when needed | `boxen`, `figures` (cross-platform symbols), `terminal-link`, `wrap-ansi`, `cli-truncate`, `update-notifier` |

## Selection principles

- **Stdlib first, then small leaf libraries.** For color/spinner/parsing, prefer the built-in or a zero/few-dependency package over a heavy one.
- **Prefer actively maintained and ESM-compatible packages.** Many popular CLI libraries went ESM-only (e.g. `chalk` v5, `execa`); confirm the module format matches the build setup before adopting, or pin an older major when CJS is required.
- **Use structured (JSON) logging** for any CLI meant to be consumed by scripts, CI, or agents — not just pretty console output.
- **Do not duplicate framework-provided helpers**, and do not add a dependency for something the standard library now does.
- **Keep every TTY-dependent library behind the `ui/` layer** so non-interactive modes suppress them in one place.
