---
name: structuring-typescript-clis
description: Use when structuring, organizing, or scaffolding a TypeScript/Node command-line tool (CLI) — especially one expected to grow large with many commands. Triggers when starting a new TS CLI, deciding project layout or layering, choosing where business logic lives, organizing many subcommands, splitting into a monorepo, or keeping a command-line app testable as it scales. Framework-agnostic; does not pick an argument-parsing library.
---

# Structuring TypeScript CLIs

Structure a TypeScript CLI so it stays testable and maintainable as the number of commands grows. These rules hold regardless of the argument-parsing framework.

## Core principle: thin commands, fat core

A command file does exactly three things: parse args/flags, call a core function, format the result for the terminal. Keep everything else — domain rules, calculations, talking to APIs/DB/filesystem — in a `core` layer that knows nothing about argv, the parsing framework, or `console`.

The core then becomes plain functions (plain data in, plain data out): unit-testable without spawning a process, and reusable unchanged behind other entry points — a library export, an HTTP handler, an MCP server. Logic welded into a command handler can only ever be a CLI and is painful to test.

```typescript
// commands/user/create.ts — thin: parse → delegate → format
import { createUser } from "../../core/services/user.js";

export async function run(args: { email: string; name: string }) {
  const user = await createUser(args); // delegate; no logic here
  printUser(user);                     // format for terminal
}

// core/services/user.ts — fat: framework-agnostic, testable
export async function createUser(input: CreateUserInput): Promise<User> {
  // business rules + orchestration via adapter interfaces.
  // no console, no process.exit, no argv, no flags.
}
```

## Project structure (single package)

Two layout shapes are legitimate. They differ only in the *top-level cut*; the layer boundaries and the thin-commands/fat-core rule are identical in both. Pick the axis that matches how the CLI actually changes.

**Shape A — layer-first (cut horizontally).** Top-level folders are technical layers. Best for a small-to-medium CLI with few resources, where the layer is the dominant axis of change and one person or team owns the whole surface.

```
src/
  cli.ts              # entry: shebang, register commands, start parsing — thin
  commands/           # one file per command; directory mirrors command tree
  core/
    services/         # use-cases: createUser(input) -> result
    domain/           # types, models, business rules — no I/O
  adapters/           # I/O across process boundaries: API, DB, fs, env, clock
  ui/                 # output rendering (table/json), prompts, spinners
  lib/                # shared utils: logger, config loader
```

**Shape B — feature-first (cut vertically / vertical slice).** Top-level folders are feature areas; each co-locates its own commands, services, domain, and adapters, and depends on a shared `core`/`lib`. Best for a large CLI with many independent resources, when whole features get added/removed often, owners split by feature, or a monorepo split is likely later. The layers still exist — they just live *inside* each feature, not at the top.

```
src/
  cli.ts              # entry: register each feature's commands — thin
  features/
    user/
      commands/       # user create | list | delete — thin, delegate inward
      service.ts      # use-cases for this feature
      domain.ts       # types + rules for this feature — no I/O
      adapter.ts      # this feature's I/O (its API/DB), behind an interface
    billing/
      commands/
      service.ts
      domain.ts
      adapter.ts
  core/               # cross-feature domain types + rules shared by features
  ui/                 # rendering/prompts, shared across features
  lib/                # logger, config loader, paths
```

**How to choose.** Default to Shape A; move to Shape B when adding a feature means touching five top-level folders and you find yourself hunting across the tree to understand or delete one feature. Shape B is also the natural precursor to the monorepo below — each `features/<area>/` folder becomes a candidate `core-<area>/` package, so the split is mechanical instead of a re-slice. A common hybrid keeps `commands/` top-level (mirroring the command tree, as an inbound adapter layer) and feature-slices only the logic under `features/<area>/`; prefer it when the command surface is the primary navigation/registration axis, and because it maps onto the monorepo split even more cleanly — `commands/`+`ui/` become the `cli/` shell while `features/<area>/` become `core-<area>/`. Two failure modes to avoid: forcing Shape B on a small CLI (feature folders with one file each — over-fragmentation, violates YAGNI), and letting layer discipline erode inside a feature because the I/O is "right there" next to the command. In both shapes, `core`/`service`/`domain` still take plain data and never import `commands/`, `ui/`, or the parsing framework.

## Layer rules

These are responsibilities of *layers*, not of fixed top-level folders: in Shape A each lives in its own top-level directory; in Shape B `commands`/`service`/`domain`/`adapter` live inside each feature while `ui`/`lib` stay shared. The boundaries below hold either way.

- `commands/`: no business logic, no direct DB/API/filesystem calls. Validate raw input, then hand a typed object to a core service.
- `core/services/`: orchestrates use-cases; receives plain data, returns plain data or throws domain errors. Imports nothing from `commands/`, `ui/`, or the parsing framework.
- `core/domain/`: pure types and rules, deterministic, no I/O — the easiest layer to test.
- `adapters/`: the only place performing I/O across process boundaries. Core depends on adapter *interfaces*, not concrete implementations, so it tests with fakes.
- `ui/`: all terminal rendering and interaction, kept out of core and out of command control flow.

## Cross-cutting concerns: base command and errors

Define behavior shared by every command once — on a base command or middleware — so command files stay thin instead of re-wiring the same plumbing:

- Global flags (`--json`, `--verbose`, `--quiet`, `--no-color`, `--config`), config loading, and a single top-level error boundary live here, not copy-pasted per command.
- Define typed domain errors in `core/`; core throws them and never calls `process.exit` or `console`.
- The boundary catches errors, maps each type to an exit code, and renders through `ui/` — clean message to stderr by default, full detail/stack only under `--verbose`, structured under `--json`. One mapping, not a `try/catch` in every command.

## Bootstrap and init order

Several things run between `node bin/cli.js` and the first command line of business logic. Make the order explicit, and keep modules side-effect free so the entry file controls it:

1. **Bootstrap**: process-level tweaks with no I/O cost (max heap size, signal handlers, env shims). At the very top of the entry file.
2. **Fast-paths**: handled before any framework loads — see "Startup performance" below.
3. **`setup()`**: resolves the working environment (cwd, project root, terminal capabilities) and registers cross-cutting handlers (logging sinks, file watchers, cleanup on exit).
4. **Config + auth resolution**: an explicit `enableConfigs()` call (or similar) loads the layered config and any cached credentials. Modules that need config import the *getter*, not the value.
5. **Command dispatch**: only now does the parsing framework see argv.

Why explicit: reading config or env at module top level defeats fast-paths (every `--version` invocation pays the cost) and makes startup non-deterministic (state depends on import order). Centralize init in one function called from the entry file.

## Command naming and discoverability

- Use **noun-verb (resource-first)** when there are many resources: `mycli user create`. Scales without action-name collisions across resources. Verb-noun (`mycli create user`) fits only small CLIs with few resources.
- Keep the command tree **shallow and consistent** — beyond three levels (`mycli a b c d`) is a signal to regroup.
- One file per command; the directory tree mirrors the command tree, so a large surface stays navigable.
- **Lazy-load command modules** so startup time stays flat regardless of command count.
- Keep flag names consistent across the whole CLI (not `--output` here, `--out` there); add short aliases for frequent flags.
- Provide `--help` at every level (root, topic, command) with at least one usage example — help text is the primary discovery surface for a large CLI.

## Scaling to a monorepo

Stay single-package until a part genuinely needs its own release cadence or owner. Split when commands span several independent feature areas, or a core package is consumed elsewhere.

```
packages/
  cli/          # CLI shell: commands + ui + bin entry
  core-<area>/  # logic per feature area, released/tested independently
  adapters-<x>/ # infrastructure implementations
  shared/       # types and utils used across packages
```

For user-extensible CLIs, add a **plugin architecture**: discover and load command modules dynamically (e.g. resolve installed plugin packages, or treat `mycli-<name>` executables on PATH as `mycli <name>`). Introduce plugins only when third parties must extend the CLI — not for internal organization, which packages already handle.

## Choosing a parsing framework

Stay framework-agnostic in `core/`; the choice only affects `commands/` and `cli.ts`. Evaluate candidates against the actual command surface, and prefer the lightest option until scale forces more batteries:

- **Nested subcommands**: clean support for multi-level commands and one-file-per-command, or must it be hand-wired?
- **Machine output**: a built-in structured/`--json` mode, or build the suppress-logs-and-serialize layer manually for every command?
- **Extensibility**: native plugin loading needed, or not?
- **Startup latency**: framework weight and cold-start cost — matters for commands run in tight loops, negligible for long batch operations.
- **Flag/arg type-safety** and **command test helpers**.

## Startup performance

For a CLI invoked from scripts, shell hooks, git hooks, or tight loops, cold-start latency *is* a feature. Three patterns matter, in order:

- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers, alternate server modes) by inspecting `process.argv` directly and `await import(...)`-ing the handler — *before* loading the parsing framework. The `--version` path should load zero modules beyond the entry file: print a version string inlined at build time and return.
- **Lazy command modules**: register each command with a loader (`() => import('./commands/foo.js')`) instead of an eager import, so only the dispatched command evaluates.
- **Build-time feature gates**: wrap optional subsystems (a daemon mode, an alternate transport, an internal-only feature) in `if (feature('FOO')) { ... }` where `feature()` is resolved at build time. Keep the condition inline — not behind a variable — so the bundler dead-code-eliminates the whole branch. Both bundle size and import time drop.

Measure before optimizing: instrument the entry file with named checkpoints (`performance.mark()`), sample on a small percentage of invocations, and emit phase durations. Pick a budget — for something people invoke from `.bashrc` or git hooks, anything over ~80 ms is noticeable. Without measurement, "optimizations" become folklore.

## Type safety

- Enable `strict` fully in tsconfig. It catches the common CLI bugs early — unhandled null flags, uninitialized state.
- Validate args/flags at the command boundary with a schema validator, then pass the parsed, typed object inward. Core never receives raw strings it must re-parse.
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## CLI behavior contract

These keep the tool scriptable and composable:

| Concern | Rule |
|---|---|
| Exit codes | `0` success, non-zero failure; distinguish business error from misuse. Scripts and CI depend on this. |
| stdout vs stderr | Real results to stdout; logs, progress, errors to stderr — so output pipes cleanly. |
| Machine output | Support `--json` (or `--output`) for structured data. Route both human and machine output through a single I/O module that picks a mode once at startup — never let individual commands call `console.log` *and* `JSON.stringify` themselves, or formats drift across commands and NDJSON streams break on the first circular reference or `BigInt`. |
| Config precedence | Resolve in layers: defaults < config file < environment variables < flags; later overrides earlier. |
| Color / TTY | Detect non-TTY (pipe/CI) and disable color/spinners; honor `NO_COLOR`. |
| Destructive actions | Default to confirmation; provide `--force`/`--yes` to bypass for automation. Make repeatable actions idempotent and offer `--dry-run`. |
| Verbosity | Provide `--quiet` and `--verbose`. |
| Stdin | Accept `-` as a filename to read stdin, so the tool composes in pipes. |

## Build and distribution

- Add a `bin` entry in package.json pointing at the built entry file; start that file with `#!/usr/bin/env node`.
- Bundle with an esbuild-based bundler: emit a runnable entry, generate declaration files only when shipping a library, and externalize `dependencies`/`peerDependencies` so they are not inlined.
- Target a modern Node version with `platform: node`.
- Prefer **ESM-only** output for a Node-only tool. Add CJS output only when other packages import yours as a library — dual publishing carries real maintenance cost otherwise.
- Inject build-time **macros** for static values: version, build timestamp, commit SHA. Inlining keeps the `--version` fast-path zero-import (no `import { version } from '../package.json'`) and makes telemetry stable across distribution channels.

## Testing

- Unit-test `core/` heavily — fast, no process spawn, no terminal mocking. Most coverage belongs here.
- Integration-test commands by invoking the parser with an argv array and asserting on the result and exit behavior.
- Snapshot-test `ui/` rendering (help text, tables) when output stability matters.
- Smoke-test end-to-end against the **built binary** on a handful of happy paths only: this exercises the shebang, `bin` wiring, bundle, and runtime module resolution that in-process command tests bypass, and verifies real process exit codes. Keep this layer thin — it is slow and brittle.

## Supporting libraries

A CLI needs leaf libraries for color, spinners, progress, tables, prompts, logging, config, paths, subprocess, and diff rendering. These belong in `ui/`, `lib/`, and `adapters/` — never in `core/` — and any TTY-dependent output stays gated behind `ui/`. Check the Node standard library before adding one (`util.styleText`, `util.parseArgs`, `--env-file`). For category-by-category selection criteria and representative packages, see `references/cli-libraries.md`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Business logic in a command handler | Move it to `core/`; the handler only parses, delegates, formats. |
| `core/` importing the parsing framework or `ui/` | Invert the dependency; core takes plain data and interfaces. |
| `core/` calling `process.exit` or `console` | Throw typed errors; let the CLI boundary map them to exit codes and render. |
| Repeating flag/error/config wiring in each command | Centralize on a base command or middleware with one error boundary. |
| One giant `commands.ts` / `index.ts` | One file per command, directory mirroring the command tree. |
| Logs mixed into stdout | Results to stdout, everything else to stderr. |
| No machine-readable output | Add `--json` early; retrofitting every command later is costly. |
| Eager-loading all commands | Lazy-load modules to keep startup fast. |
| Loading the parsing framework before checking common flags | Handle `--version` and internal subprocess modes by inspecting `process.argv` in the entry file first, before importing the framework. |
| Reading config or env at module top level | Read inside an explicit init function the entry file calls once. Top-level side effects defeat fast-paths and make startup non-deterministic. |
| Monorepo or plugins built upfront | Stay single-package until a part needs its own lifecycle. |
| Dual CJS+ESM publishing by default | ESM-only unless consumed as a library. |

## Persisting user data

When the CLI needs to store anything for the user — config, credentials, projects, cache, backups, logs — read references/user-data-storage.md before designing the layout. It covers the invariants (global vs per-project separation, separable disposable data, keychain-first credentials, overridable root), the two legitimate layout shapes and how to choose, cross-platform locations, and the path-resolution module pattern.