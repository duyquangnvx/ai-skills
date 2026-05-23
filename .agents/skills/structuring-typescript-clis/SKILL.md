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

## Layer rules

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
| Machine output | Support `--json` (or `--output`) printing structured data, separate from human rendering. |
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

## Testing

- Unit-test `core/` heavily — fast, no process spawn, no terminal mocking. Most coverage belongs here.
- Integration-test commands by invoking the parser with an argv array and asserting on the result and exit behavior.
- Snapshot-test `ui/` rendering (help text, tables) when output stability matters.
- Smoke-test end-to-end against the **built binary** on a handful of happy paths only: this exercises the shebang, `bin` wiring, bundle, and runtime module resolution that in-process command tests bypass, and verifies real process exit codes. Keep this layer thin — it is slow and brittle.

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
| Monorepo or plugins built upfront | Stay single-package until a part needs its own lifecycle. |
| Dual CJS+ESM publishing by default | ESM-only unless consumed as a library. |
