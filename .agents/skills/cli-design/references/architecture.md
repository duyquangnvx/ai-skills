# TypeScript/Node Architecture

How to structure CLI code so it stays testable and maintainable as it grows. These rules hold regardless of the argument-parsing framework chosen (see `frameworks.md`) — the framework only touches `cli.ts` and `commands/`, never the `core`.

## Contents
- [Core principle: thin commands, fat core](#core-principle-thin-commands-fat-core)
- [Project structure](#project-structure)
- [Layer rules](#layer-rules)
- [Enforce boundaries with tooling](#enforce-boundaries-with-tooling)
- [Cross-cutting concerns: base command and errors](#cross-cutting-concerns-base-command-and-errors)
- [Bootstrap and init order](#bootstrap-and-init-order)
- [Command naming and discoverability](#command-naming-and-discoverability)
- [Startup performance](#startup-performance)
- [Type safety](#type-safety)
- [CLI behavior contract](#cli-behavior-contract)
- [Build and distribution](#build-and-distribution)
- [Cross-platform](#cross-platform)
- [Testing](#testing)
- [Common mistakes](#common-mistakes)
- [Supporting libraries](#supporting-libraries)
- [Persisting user data](#persisting-user-data)

## Core principle: thin commands, fat core

A command file does exactly three things: parse args/flags, call a core function, format the result for the terminal. Keep everything else — domain rules, calculations, talking to APIs/DB/filesystem — in a separate `core` layer that knows nothing about argv, the parsing framework, or `console`.

This matters because the core then becomes plain functions (plain data in, plain data out) that can be unit-tested without spawning a process, and reused unchanged behind other entry points — a library export, an HTTP handler, or an MCP server. Logic welded into command handlers can only ever be a CLI and is painful to test.

```typescript
// commands/user/create.ts — thin: parse → delegate → format
import { createUser } from "../../core/services/user.js";

export async function run(args: { email: string; name: string }) {
  const user = await createUser(args);   // delegate, no logic here
  printUser(user);                       // format for terminal
}

// core/services/user.ts — fat: framework-agnostic, testable
export async function createUser(input: CreateUserInput): Promise<User> {
  // business rules + orchestration via adapters
  // no console, no process.exit, no argv, no flags
}
```

## Project structure

```
src/
  cli.ts              # entry: shebang, register commands, start parsing — thin
  commands/           # one file per command; parse → call core → format
  core/
    services/         # use-cases: createUser(input) -> result
    domain/           # types, models, business rules — no I/O
  adapters/           # I/O across process boundaries: API, DB, fs, env, clock
  ui/                 # output rendering (table/json), prompts, spinners
  lib/                # shared utils: logger, config loader
```

## Layer rules

- **`commands/`**: no business logic and no direct DB/API/filesystem calls. Validate raw input here, then hand a typed object to a core service.
- **`core/`**: deterministic where possible; receives plain data, returns plain data or throws domain errors. Imports nothing from `commands/`, `ui`, or the parsing framework.
- **`adapters/`**: the only place that performs I/O across process boundaries. In ports-and-adapters terms, `commands/` is the **inbound (driving)** adapter — the CLI is just one entry point — while these are the **outbound (driven)** adapters. Core depends on adapter *interfaces*, not concrete implementations, so it can be tested with fakes. This is also where to wrap nondeterministic sources (clock, random, UUID) so core stays deterministic and testable.

## Enforce boundaries with tooling

A correct layout is worthless if, two years on, someone imports across a boundary and the dependency direction quietly rots. Turn the convention into a build-time check so it doesn't depend on everyone's discipline over time. Use **dependency-cruiser** or **eslint-plugin-boundaries** in CI to forbid:

- `core/` (services or domain) importing the parsing framework or `console`;
- `core/domain` importing `adapters/`;
- `commands/` performing I/O directly instead of going through `core`.

This converts "rules in your head" into "the build goes red on violation" — which is what actually prevents architectural debt across a project's lifetime.

## Cross-cutting concerns: base command and errors

Define behavior shared by every command once — on a base command or middleware — so command files stay thin instead of re-wiring the same plumbing:

- Global flags (`--json`, `--verbose`, `--quiet`, `--no-color`, `--config`), config loading, and a single top-level error boundary live here, not copy-pasted per command.
- Define typed domain errors in `core` (`core/domain`); core throws them and never calls `process.exit` or `console`.
- The boundary catches errors, maps each type to an exit code, and renders through `ui` — clean message to stderr by default, full detail/stack only under `--verbose`, structured under `--json`. One mapping, not a `try/catch` in every command.
- Give each domain error a stable, documented code and an *actionable* message (what to do next, not just what broke). For unexpected errors, print a bug-report URL prefilled with version and context, and gate full tracebacks behind `--verbose`/`DEBUG`.

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
- One file per command inside `commands/`; the directory tree mirrors the command tree, so a large surface stays navigable.
- **Lazy-load command modules** (register a loader, not an eager import) so startup time stays flat regardless of command count.
- Keep flag names consistent across the whole CLI (not `--output` here, `--out` there); add short aliases for frequent flags.
- Provide `--help` at every level (root, topic, command) with at least one usage example — help text is the primary discovery surface for a large CLI.

## Startup performance

For a CLI invoked from scripts, shell hooks, git hooks, or tight loops, cold-start latency *is* a feature — aim well under ~100 ms for those cases. Three patterns, in order of impact:

- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers, alternate server modes) by inspecting `process.argv` directly and `await import(...)`-ing the handler *before* loading the parsing framework. The `--version` path should load zero extra modules — print a version string inlined at build time and return.
- **Lazy command modules**: register each command with a loader (`() => import('./commands/foo.js')`) instead of an eager import, so only the dispatched command evaluates (the lazy-loading rule from the contract above).
- **Build-time feature gates**: wrap optional subsystems (a daemon mode, an alternate transport) in `if (feature('FOO')) { ... }` resolved at build time, with the condition inline so the bundler dead-code-eliminates the whole branch — both bundle size and import time drop.

Measure before optimizing: instrument the entry file with `performance.mark()` checkpoints, sample on a small percentage of invocations, and pick a budget — anything over ~80 ms is noticeable for a tool run from `.bashrc` or git hooks. Without measurement, "optimizations" are folklore.

## Type safety

- Enable `strict` fully in tsconfig. It catches most CLI bugs early — unhandled null flags, uninitialized state.
- Validate args/flags at the command boundary with a schema validator (e.g. **Zod** or **Valibot**), then pass the parsed, typed object inward. Core should never receive raw strings it must re-parse. The validator's error messages double as the user-facing error for bad input (rewrite them for humans per `ux-guidelines.md`).
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## CLI behavior contract

These keep the tool scriptable and composable:

| Concern | Rule |
|---|---|
| Exit codes | `0` success, non-zero failure; distinguish business error from misuse. Don't `process.exit()` from inside `core/` — let core throw, and have the command/entry layer translate errors to exit codes. Scripts and CI depend on this. |
| stdout vs stderr | Real results to stdout; logs, progress, errors to stderr — so output pipes cleanly. |
| Machine output | Support `--json` (or `--output`) for structured data. Route both human and machine output through a single I/O module (in `ui/`) that picks a mode once at startup — never let individual commands call `console.log` *and* `JSON.stringify` themselves, or formats drift across commands and NDJSON streams break on the first circular reference or `BigInt`. |
| Config precedence | Resolve in layers: defaults < config file < environment variables < flags; later overrides earlier. Centralize in a config loader in `lib/`. |
| Color / TTY | Detect non-TTY (pipe/CI) and disable color/spinners; honor `NO_COLOR`. Branch on `process.stdout.isTTY`; never animate when output is redirected. |
| Destructive actions | Default to confirmation; provide `--force`/`--yes` to bypass for automation. Make repeatable actions idempotent and offer `--dry-run`. |
| Verbosity | Provide `--quiet` and `--verbose`. |
| Stdin | Accept `-` as a filename to read stdin, so the tool composes in pipes. |
| End of options | Accept `--` to stop flag parsing and pass the rest through verbatim (e.g. to a spawned subprocess). |
| Interactivity | Prompt only when stdin is a TTY; every prompt needs an equivalent flag so non-interactive/CI runs never block. |
| Signals | Exit promptly on SIGINT/SIGTERM — announce before any cleanup, bound cleanup with a timeout, and skip it on a second Ctrl-C. Clean up temp files and restore the cursor/terminal. Design crash-only so an interrupted run can resume. |

## Build and distribution

- Add a `bin` entry in package.json pointing at the built entry file, and start that file with `#!/usr/bin/env node`.
- Bundle with an esbuild-based bundler (e.g. tsup or tsdown): emit a runnable entry, generate declaration files only if shipping a library, and externalize `dependencies`/`peerDependencies` so they are not inlined.
- Target a modern Node version with `platform: node`, and declare the floor in package.json `engines`. The stdlib-first APIs this skill leans on land at specific versions — `process.loadEnvFile`/`util.parseEnv` in 20.12, stable `util.styleText` in 22 — so target **Node ≥ 20.12** (or ≥ 22 to use `styleText` without a flag), and guard or polyfill anything newer than your floor.
- Prefer ESM-only output for a tool that only runs under Node. Add CJS output only when other packages import yours as a library — dual publishing adds real maintenance cost otherwise.
- For local development, run TypeScript directly (e.g. `tsx`) so you don't rebuild on every change.
- Inject build-time **macros** for static values: version, build timestamp, commit SHA. Inlining keeps the `--version` fast-path zero-import (no `import { version } from '../package.json'`) and makes telemetry stable across distribution channels.
- Set the `files` field in package.json (or an `.npmignore`) so only the built output ships — not `src/`, tests, or fixtures. Smaller installs, faster `npx`.

## Cross-platform

A Node CLI is expected to run on Windows, macOS, and Linux. Bake that in rather than retrofitting it:

- Build paths with `path.join`/`path.resolve`, never `'/'` concatenation. Use `process.cwd()` for user-supplied paths and `import.meta.url`/`__dirname` for files shipped with the tool.
- Don't assume a shell, `bash`, `/tmp`, or POSIX-only env vars in spawned commands; honor `TMPDIR`/`TEMP`. Prefer passing an args array to `spawn` over a shell string.
- The `#!/usr/bin/env node` shebang plus a `bin` entry is what makes the tool launch cross-platform — npm generates the Windows `.cmd` shim from it.

## Testing

- **Unit-test `core/` heavily** — fast, no process spawn, no terminal mocking. Most coverage belongs here. Inject fake adapters for I/O.
- **Integration-test commands** by invoking the parser with an argv array and asserting on the result and exit behavior.
- **Snapshot-test `ui/` rendering** (help text, tables) when output stability matters.
- Because logic lives in `core/`, you rarely need brittle end-to-end shell tests — keep those few and reserved for the wiring (entry → parse → exit code), and smoke-test the **built binary** on a handful of happy paths to exercise the shebang/`bin` wiring and real exit codes.

## Common mistakes

| Mistake | Fix |
|---|---|
| Business logic in a command handler | Move it to `core/services`; the handler only parses, delegates, formats. |
| `core/` importing the parsing framework or `ui` | Invert the dependency; core takes plain data and interfaces. |
| Core calling `process.exit` or `console` | Throw typed errors; let the CLI boundary map them to exit codes and render. |
| Repeating flag/error/config wiring in each command | Centralize on a base command or middleware with one error boundary. |
| One giant `commands.ts` | One file per command, directory mirroring the command tree. |
| Logs mixed into stdout | Results to stdout, everything else to stderr. |
| No machine-readable output | Add `--json` early; retrofitting every command later is costly. |
| Eager-importing every command to register them | Register through lazy loaders so only the dispatched command evaluates. |
| Loading the parsing framework before checking common flags | Handle `--version` and internal subprocess modes by inspecting `process.argv` in the entry file first, before importing the framework. |
| Reading config or env at module top level | Read inside an explicit init function the entry file calls once. Top-level side effects defeat fast-paths and make startup non-deterministic. |
| Monorepo or plugins built upfront | Stay single-package until a part needs its own lifecycle. |
| Dual CJS+ESM publishing by default | ESM-only unless consumed as a library. |

## Supporting libraries

A CLI needs leaf libraries for color, spinners, progress, tables, prompts, logging, config, paths, subprocess, and diff rendering. These belong in `ui/`, `lib/`, and `adapters/` — never in `core/` — and any TTY-dependent output stays gated behind `ui/`. Check the Node standard library before adding one (`util.styleText`, `util.parseArgs`, `--env-file`). For category-by-category selection criteria and representative packages, see `cli-libraries.md`. For the parsing framework specifically, see `frameworks.md`.

## Persisting user data

When the CLI needs to store anything for the user — config, credentials, projects, cache, backups, logs — read `user-data-storage.md` before designing the layout. It covers the invariants (global vs per-project separation, separable disposable data, keychain-first credentials, overridable root), the two legitimate layout shapes and how to choose, cross-platform locations, and the path-resolution module pattern.
</content>
</invoke>
