# TypeScript CLI Stack Reference

Library selection, code organization, and shipping recipes for Node/Bun CLIs. Ecosystem facts adversarially verified, snapshot June 2026 — versions and download counts drift; treat them as relative ordering and re-verify before pinning.

## Argument parsing / frameworks

| Tool | Position | Trade-offs |
|---|---|---|
| `node:util.parseArgs` | Built-in, zero-dep | No help generation or subcommand routing. Fine for tiny single-command tools. Works in Node/Bun/Deno. |
| **Commander** | Most popular general-purpose (~415M dl/week) | Zero deps, minimal API, fastest of the big established options. Stock `.opts()` is untyped — add **`@commander-js/extra-typings`** (official companion, typings-only, import it in place of commander) for inferred types on `.action()`/`.opts()`. |
| **cac** | Lightweight chaining parser (~37M dl/week) | Zero deps, ~41KB, ESM-only. Battle-tested via Vite ecosystem. |
| **citty** (UnJS) | Lightweight declarative builder | Zero deps, built on `util.parseArgs`. `defineCommand` with type inference (enum → union), nested subcommands with **lazy async imports**, auto usage, setup/cleanup hooks. ESM-only, pre-1.0; had since-fixed type-inference bugs — lower maturity signal. |
| **yargs** | Feature-rich parser | Built-in coercion, choices, typo suggestions, middleware, completion. Heavier, several deps. TS support largely automatic via the `type` key (use `parseSync` to avoid the Promise-union return). |
| **oclif** | Enterprise framework (Heroku/Salesforce) | Scaffolding, plugin system, auto-docs, test utilities. Heaviest deps, slowest startup: static class properties force loading every command — generate `oclif.manifest.json` to mitigate. Worth it only for large plugin-extensible CLIs. |
| **Clipanion** | Class-based, type-safe (powers Yarn) | Typed fields as source of truth, good inference. NOT zero-dep (typanion). All commands load at runtime (no lazy loading); release cadence has stalled (v4 long in RC) — verify activity before committing. |
| **Stricli** (Bloomberg) | Zero-dep, strict TS, lazy-by-design | Defs/impl split via `import()` so `--help` loads nothing; injected context for testing; shell-agnostic completion. Caution: its "alternatives" comparison page is vendor marketing — the claim that chaining libs can't have accurate types is false with extra-typings. Young, small ecosystem. |

Selection heuristic:

- One command, few flags → `util.parseArgs` or citty.
- Typical product CLI → **Commander + extra-typings** (safe default) or **citty** (declarative, ESM, lazy subcommands) or **cac** (minimal chaining).
- Strict type-flow with DI testability → Stricli or Clipanion (check maintenance first).
- Plugins / team scaffolding / auto-docs → oclif, accepting the startup cost.
- Invoked constantly (hot loops, per-save) → favor the lazy-loading column; measure `time mycli --version`.

## Interaction & presentation

- **Prompts**: `@inquirer/prompts` — the official Inquirer rewrite (~12kb vs legacy 242kb; legacy `inquirer` is frozen, do not use). `@clack/prompts` is the popular modern alternative (intro/outro, `group()`, handle `isCancel`). **Ink** (React TUI) only for genuinely stateful live-updating UIs.
- **Color**: `util.styleText` (native `node:util`, stable since Node 22.13) is the zero-dep default — Node publishes an official chalk-migration guide. Otherwise `picocolors` (small, no chaining) or `ansis` (chalk-like chaining, RGB/hex). Whatever you pick must honor the full disable matrix (non-TTY, `NO_COLOR`, `TERM=dumb`, `--no-color`) and `FORCE_COLOR`; wire `--no-color` yourself.
- **Spinners/progress**: `ora` or similar; must no-op when the stream isn't a TTY.
- **Tables**: prefer plain `padEnd` column layouts; avoid border-drawing table libs (borders break grep/wc).
- **TTY detection**: `process.stdout.isTTY` / `process.stderr.isTTY` — check each stream separately.

## Supporting libraries (stdlib first)

Check the built-in before adding a dependency: `util.styleText` (color), `util.parseArgs` (flags), `node --env-file` / `process.loadEnvFile()` (env files), global `fetch` (HTTP), `AbortController` (timeouts/cancellation), `Promise.allSettled` (fan-out), `fs.watch`, `process.on('SIGINT'|'SIGTERM')`. For paging long output, spawn the user's `$PAGER` (default `less -FIRX`) via execa when stdout is a TTY — npm pager packages are small and unmaintained, don't add one. Then prefer small maintained leaf libs:

| Need | Reach for |
|---|---|
| Subprocess | `execa` |
| Schema validation at the boundary | `zod`, `valibot` |
| Config discovery + merge | `cosmiconfig` |
| Config format parsers (YAML/TOML/INI/JSONC) | `yaml`, `smol-toml`, `ini` (`confbox` bundles all) |
| Cross-platform config/data/cache dirs | `env-paths` |
| OS keychain | `@napi-rs/keyring` (`keytar` is archived) |
| Globbing / fs extras | `fast-glob` or `tinyglobby` (lighter, used by vitest/tsdown), `fs-extra` |
| Structured logging | `pino` (machine), `consola` (pretty) |
| Terminal strings: strip ANSI, width, wrap, truncate | `strip-ansi`, `string-width`, `wrap-ansi`, `cli-truncate` |
| Cross-platform symbols (✔ → √ fallback) | `figures`, `is-unicode-supported` |
| Semver | `semver` |
| "Did you mean" | `leven`, `didyoumean2` (often framework built-in) |
| Shell completion | framework built-ins first (yargs, oclif, Stricli ship it); `@pnpm/tabtab` |
| Cross-process locking | `proper-lockfile` |
| Multi-step task runner (staged pipelines) | `listr2` |
| Live multi-line status (between spinner and Ink) | `log-update` |
| Bounded concurrency, retry, timeout | `p-limit`, `p-retry`, `p-timeout` |
| Read piped stdin / `-` placeholder | `get-stdin` |
| Diff rendering (`--dry-run` previews, approvals) | `diff` (jsdiff) |
| Open URL/file in default app (OAuth, reveal output) | `open` |
| Restore terminal state on exit (cursor after spinners) | `signal-exit`, `restore-cursor` |
| Durations & sizes (parse and format) | `ms`, `bytes`, `pretty-ms`, `pretty-bytes` |
| Numeric ranges (`--pages 1-5,8`) | `multi-integer-range` (normalized pairs); `parse-numeric-range` only for small flat lists |
| `--watch` mode | `chokidar` — stdlib `fs.watch` is unreliable for recursive cross-platform watching |
| Detect CI / non-interactive env | `std-env` (`isCI`) — gate prompts and spinners on TTY **and** not CI |
| Locate external binaries (preflight/`doctor` checks) | `which` |
| `$EDITOR` for long free-form input | `@inquirer/external-editor` (`external-editor` is unmaintained) |
| Update notification (npm-distributed CLIs) | `update-notifier` — skips CI, honors `NO_UPDATE_NOTIFIER` |
| Situational only | `clipboardy` (clipboard), `node-notifier` (desktop notify), `marked` + `marked-terminal` (markdown output), `shell-quote` / `string-argv` (quote/split argv), `chrono-node` (natural-language dates) |

Gate every TTY-dependent library behind one output layer (below) — never call spinner/color libs directly from command handlers.

## Code organization

Layering, context injection, the reporter pattern, error boundary, and startup-performance patterns live in `architecture.md` — read it before scaffolding. One Node-specific fact belongs here:

**Signal handling** (verified Node behavior): installing a `SIGINT`/`SIGTERM` listener **removes the default exit** — Node no longer exits on its own. The handler receives the signal name, must clean up (time-boxed, `.unref()` the timer) and exit itself:

```ts
function handle(signal: string) {
  // time-boxed cleanup, then:
  process.exit(128 + (signal === 'SIGINT' ? 2 : 15))
}
process.on('SIGINT', handle)
process.on('SIGTERM', handle)
```

## Build, distribute

- **ESM-only is now safe**: `require(esm)` is stable and unflagged on all supported LTS lines (v20.19.0+, v22.12.0+). Ship ESM, drop CJS, set `"engines": { "node": "^20.19.0 || >=22.12.0" }`. (Caveat: `require(esm)` can't load top-level-await modules.)
- **Bundle to a single file** with **tsdown** (Rolldown-based) or esbuild — fewer module resolutions = faster startup, clean `npx`. **Do not use tsup** — officially unmaintained; its maintainer recommends tsdown (`npx tsdown-migrate`).
- `package.json` `"bin"` + `#!/usr/bin/env node` shebang; `files` field limits published output.
- **Distribution tiers**: (1) npm/`npx` — fine for dev-audience tools; (2) single executable for general audiences: `node --build-sea sea-config.json` (one command since Node v25.5; replaces postject) or `bun build --compile` (~60MB, embeds runtime, cross-compiles via `--target`). Startup differences between the two are methodology-dependent and practically negligible.
- Document uninstall at the end of the install instructions.

## Testing

- Unit-test the core directly (pure functions, fake I/O passed as parameters) — the bulk of coverage.
- Invoke command functions in-process with an injected context (streams, env, cwd) instead of spawning, asserting output + exit behavior.
- A small `child_process`/execa end-to-end suite against the built binary asserting: exit codes per failure class · stdout vs stderr separation · `--json` validates against its schema · no ANSI when piped · `NO_COLOR` honored · `--no-input` prevents hanging.
- Vitest snapshots for output contracts: `toMatchInlineSnapshot()` for short stdout/stderr, `toMatchFileSnapshot()` for larger output; a `--help` snapshot catches interface breaks. Strip ANSI before snapshotting.
- CI extras: `time mycli --version` against the startup budget; test `npx` cold-start from a clean cache.

## Common pitfalls

(Architecture-level mistakes — logic in handlers, eager imports, `process.exit()` — are tabled in `architecture.md`.)

- Prompt libraries hanging in CI because stdin isn't a TTY — gate every prompt on `isTTY && !noInput`.
- Forgetting Windows: paths (`path.join`), no `man`, `%LOCALAPPDATA%`, shell quoting differences.
- Publishing without testing `npx` cold-start from a clean cache.
- Trusting vendor comparison pages for framework choice — verify claims against npm/GitHub directly.
