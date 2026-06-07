# TypeScript CLI Stack Reference

Library selection, project structure, and shipping recipes for Node/Bun CLIs. Ecosystem state: 2026.

## Argument parsing / frameworks

| Tool | Position | Trade-offs |
|---|---|---|
| `node:util.parseArgs` | Built-in, zero-dep | No help generation or subcommand routing. Fine for tiny single-command tools. Works in Node/Bun/Deno. |
| **citty** (UnJS) | Lightweight declarative builder | Zero-dep, built on `util.parseArgs`. Typed args (enum → union types), nested subcommands with lazy async imports, auto-generated usage, setup/cleanup hooks. ESM-only. |
| **Commander** | Most popular general-purpose | Zero dependencies, minimal API, solid TS support, fastest of the big three (~18–25ms overhead vs ~12ms bare Node in published benchmarks). Type coercion and choice validation are manual. |
| **yargs** | Feature-rich parser | Built-in coercion, choices, typo suggestions, middleware, completion. Heavier (~35–48ms). |
| **oclif** | Enterprise framework (Heroku/Salesforce) | File-based command scaffolding, plugin system, auto-docs, testing utilities, hooks. ~30 deps, slowest startup (~85–135ms). The 12-Factor CLI reference implementation. |
| **Clipanion** | Class-based, type-safe | Powers Yarn. Designed for very complex CLIs. |
| **Stricli** (Bloomberg) | Zero-dep, strict TS | Built explicitly on clig.dev. Flag/positional types flow through the app; commands defined separately from implementations → lazy ESM imports (`--help` loads no runtime deps); all system access behind one injected context object (excellent for testing); runtime-JS shell-agnostic autocomplete. Deliberately narrow — bring your own prompts/colors. Node/Bun/Deno. |

Selection heuristic:

- One command, few flags → `util.parseArgs` or citty.
- Typical product CLI → Commander (safe default) or citty (declarative, ESM, lazy subcommands).
- Large CLI with strict typing and DI testability → Stricli or Clipanion.
- Need plugins / team scaffolding / auto-generated docs → oclif, accepting the startup cost.
- The CLI is invoked constantly (per-keystroke, per-save, in hot loops) → minimize: parseArgs/citty/Commander, bundle aggressively, measure `time mycli --version`.

## Interaction & presentation

- **Prompts**: `@clack/prompts` is the modern default — TS-native, ESM, tiny, `intro`/`outro`, `group()` for multi-step flows, cancellation via `isCancel` (always handle it: `cancel(); process.exit(0)`). **Enquirer** for exotic prompt types (autocomplete, scale, multiselect). **Ink** (React for terminals) only when the UI is genuinely stateful and live-updating (parallel progress dashboards); otherwise its React overhead is unjustified.
- **Color**: `picocolors` (smallest) or `chalk`. Verify the lib's auto-detection covers the full disable matrix (non-TTY, `NO_COLOR`, `TERM=dumb`, `--no-color`) and respects `FORCE_COLOR`; wire `--no-color` yourself.
- **Spinners/progress**: `ora` or equivalent; must no-op when the stream isn't a TTY.
- **Tables**: prefer plain `padEnd` column layouts; avoid border-drawing table libs (borders break grep/wc and violate the one-record-per-line rule).
- **TTY detection**: `process.stdout.isTTY` / `process.stderr.isTTY` — check each stream separately.

## Code organization

Structure scales with the CLI: a single file until it hurts, then one module per command. Do NOT impose backend layering (hexagonal / ports-adapters, `core`/`domain`/`infrastructure` folders) — a CLI's commands are already its boundary, and the extra indirection makes the code harder to trace. Extract a pure function only where a test actually needs it. Three CLI-specific patterns that DO matter:

- **Lazy-load command modules.** Keep the entry file (`#!/usr/bin/env node`, `"bin"` in package.json, `"type": "module"`) tiny: parse and route only, importing each command on demand (citty: `subCommands: { x: () => import("./commands/x.js") }`; Stricli separates definitions from implementations for the same effect). This is what keeps `--help`/`--version` inside the 100ms budget.
- **One output layer.** Commands emit semantic records; a single module decides human vs `--json` vs `--plain` vs `--quiet` rendering and owns TTY/color detection. Prevents the classic drift where some commands respect `--json` and others don't.
- **One error formatter.** Every thrown error funnels through it: human mode renders "what failed / why / how to fix"; JSON mode emits a structured object (`{ type, message, input_id }`) on stderr; the exit code is drawn from the error type, defined in one `enum ExitCode`.

## Build, test, distribute

**Build**: bundle with esbuild / tsup / tsdown into a single JS file — fewer module resolutions = faster startup, and `npx` works cleanly. Ship ESM; add CJS only if consumers demand it.

**Distribution tiers**:

1. npm (`npm i -g`, `npx mycli`) — appropriate for developer-audience tools (the clig.dev "language-specific tool" exemption: assuming Node exists is fine for a JS linter).
2. Single executable for general audiences: `bun build --compile`, Node Single Executable Applications (SEA), or pkg-style bundlers. Binary embeds the runtime — dependency size now matters.
3. Whatever the channel: document uninstall at the bottom of the install instructions.

**Testing** (encode the contracts as regression tests):

- Unit-test pure logic directly where it exists.
- Invoke command functions in-process with a mocked context (Stricli's DI pattern works in any framework) instead of spawning for most cases.
- A small `child_process` end-to-end suite asserting: exit codes per failure class · stdout vs stderr separation · `--json` output validates against its schema · no ANSI codes when piped · `NO_COLOR` honored · `--no-input` prevents hanging.
- CI extras: `time mycli --version` against the startup budget; `--help` snapshot test (help is a contract).

## Common pitfalls in Node CLIs

- Importing the whole dependency tree at startup → 500ms+ before `--help`. Lazy-load commands.
- `console.log` for errors/progress → corrupts piped output. Route through the output layer (stderr).
- Prompt libraries hanging in CI because stdin isn't a TTY — gate every prompt on `isTTY && !noInput`.
- `process.exit()` inside async work truncating buffered stdout — flush or use `process.exitCode = N` and return.
- Forgetting Windows: paths, no `man`, different config dir (`%LOCALAPPDATA%`), shell quoting differences.
- Publishing without testing `npx` cold-start from a clean cache.
