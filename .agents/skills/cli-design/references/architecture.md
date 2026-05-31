# TypeScript/Node Architecture

How to structure a CLI's code so it stays testable and maintainable as the number of commands grows. These rules hold regardless of the argument-parsing framework chosen (see `frameworks.md`) — the framework only touches `cli.ts` and a feature's `commands/`, never the feature core.

## Contents
- [Core principle: thin commands, fat core](#core-principle-thin-commands-fat-core)
- [Project structure (feature-first, single standard)](#project-structure-feature-first-single-standard)
- [Three invariants that keep the shape stable](#three-invariants-that-keep-the-shape-stable)
- [Layer rules](#layer-rules)
- [Enforce boundaries with tooling](#enforce-boundaries-with-tooling)
- [Cross-cutting concerns: base command and errors](#cross-cutting-concerns-base-command-and-errors)
- [Bootstrap and init order](#bootstrap-and-init-order)
- [Command naming and discoverability](#command-naming-and-discoverability)
- [Scaling to a monorepo](#scaling-to-a-monorepo)
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

A command file does exactly three things: parse args/flags, call a core function, format the result for the terminal. Keep everything else — domain rules, calculations, talking to APIs/DB/filesystem — in a core layer that knows nothing about argv, the parsing framework, or `console`.

The core then becomes plain functions (plain data in, plain data out): unit-testable without spawning a process, and reusable unchanged behind other entry points — a library export, an HTTP handler, an MCP server. Logic welded into a command handler can only ever be a CLI and is painful to test.

```typescript
// features/user/commands/create.ts — thin: parse → delegate → format
import { createUser } from "../service.js";

export async function run(args: { email: string; name: string }) {
  const user = await createUser(args); // delegate; no logic here
  printUser(user);                     // format for terminal
}

// features/user/service.ts — fat: framework-agnostic, testable
export async function createUser(input: CreateUserInput): Promise<User> {
  // business rules + orchestration via adapter interfaces.
  // no console, no process.exit, no argv, no flags.
}
```

## Project structure (feature-first, single standard)

Organize by **feature/domain**, not by technical layer. This is the one structure to use from a 1-command tool to a 60-command tool — it never needs a reshape, because growth is *additive* (add a feature folder), not *transformative* (re-slice the whole app). A layer-first layout (top-level `commands/`, `services/`, `domain/`, `adapters/`) looks tidy when small but forces a costly app-wide migration once features multiply: a single feature ends up scattered across five folders (shotgun surgery), and the flat layer folders grow unscannably wide. Avoid that migration by starting feature-first.

```
src/
  cli.ts                  # entry: shebang, build program, register features (lazily), parse, map error → exit code. Thin.
  features/
    <feature>/            # one folder per domain. The ONLY place that grows — by adding folders.
      commands/           # thin: parse → call service → format. One file per command (verb).
      service.ts          # use-cases (fat core). Plain in/out. No argv, no console, no process.exit.
      domain.ts           # types, models, business rules. Pure. No I/O.
      ui.ts               # feature-specific rendering (optional; lift to shared/ui if reused).
      adapters/           # I/O used ONLY by this feature (optional).
      index.ts            # the feature's public API: registers its commands with the program (via a lazy loader).
  shared/
    adapters/             # I/O used by ≥2 features: db, http, fs, clock, env, uuid — behind interfaces.
    ui/                   # reusable primitives: table, spinner, prompt.
    domain/               # genuinely cross-cutting types.
    lib/                  # logger, config loader, error types.
```

A small feature need not fill every slot — it might be just `commands/` + `service.ts` + `domain.ts`. Don't create empty placeholder files; add a slot only when the feature needs it. Adding `ui.ts` or `adapters/` later is a local change inside one folder, not a reshape.

## Three invariants that keep the shape stable

These are what let the structure scale from small to large without ever being re-sliced:

1. **Top level is fixed**: always `cli.ts` + `features/` + `shared/`. One feature or fifty, the top level is identical. Adding a feature = adding one folder under `features/`. Purely additive.
2. **Every feature has the same slots.** You fill them as the feature grows; growth happens *inside* a feature's own folder, never across the tree. A one-command feature and a twenty-command feature share the same shape, differing only in how many files live inside.
3. **The promotion rule**: anything used by exactly one feature lives inside that feature; when a second feature needs it, promote it to `shared/`. Promotion is moving one file, triggered by a clear condition (≥2 consumers) — not an ambiguous architectural call, so it never accumulates as debt. If `features/billing` needs to import from `features/user`'s internals, that's a design smell: either the two are wrongly coupled, or the imported thing belongs in `shared/`.

## Layer rules

The thin-command/fat-core dependency direction holds *inside* each feature:

- **`commands/`**: no business logic and no direct DB/API/filesystem calls. Validate raw input here, then hand a typed object to the feature's `service`.
- **`service.ts` / `domain.ts`**: the fat core of the feature. Deterministic where possible; receives plain data, returns plain data or throws domain errors. Imports nothing from `commands/`, `ui`, or the parsing framework.
- **`adapters/`** (feature-local or `shared/adapters`): the only place that performs I/O across process boundaries. In ports-and-adapters terms, `commands/` is the **inbound (driving)** adapter — the CLI is just one entry point — while these are the **outbound (driven)** adapters. Core depends on adapter *interfaces*, not concrete implementations, so it can be tested with fakes. This is also where to wrap nondeterministic sources (clock, random, UUID) so core stays deterministic and testable. Keep an adapter feature-local while one feature uses it; promote it to `shared/adapters` the moment a second feature needs it — don't push every adapter up (it couples unrelated features) and don't trap a shared one inside one feature (it forces duplication).
- **Features never reach into each other's internals** — they interact only through `shared/` or another feature's public `index.ts`.

## Enforce boundaries with tooling

A correct layout is worthless if, two years on, someone imports across a boundary and the dependency direction quietly rots. Turn the convention into a build-time check so it doesn't depend on everyone's discipline over time. Use **dependency-cruiser** or **eslint-plugin-boundaries** in CI to forbid:

- a feature importing another feature's internals (only `shared/` or a feature's public `index.ts` is allowed);
- `service`/`domain` importing the parsing framework or `console`;
- `domain` importing `adapters`.

This converts "rules in your head" into "the build goes red on violation" — which is what actually prevents architectural debt across a project's lifetime.

## Cross-cutting concerns: base command and errors

Define behavior shared by every command once — on a base command or middleware — so command files stay thin instead of re-wiring the same plumbing:

- Global flags (`--json`, `--verbose`, `--quiet`, `--no-color`, `--config`), config loading, and a single top-level error boundary live here, not copy-pasted per command.
- Define typed domain errors in the feature core (or `shared/domain` if cross-cutting); core throws them and never calls `process.exit` or `console`.
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
- One file per command inside the feature's `commands/`; the directory tree mirrors the command tree, so a large surface stays navigable.
- **Lazy-load each feature's commands** (register a loader, not an eager import) so startup time stays flat regardless of command count.
- Keep flag names consistent across the whole CLI (not `--output` here, `--out` there); add short aliases for frequent flags.
- Provide `--help` at every level (root, topic, command) with at least one usage example — help text is the primary discovery surface for a large CLI.

## Scaling to a monorepo

Stay single-package until a part genuinely needs its own release cadence or owner. Split when commands span several independent feature areas, or a core package is consumed elsewhere. Because the layout is already feature-first, the split is mechanical, not a reshape: each `features/<area>/` lifts to a package and its `index.ts` becomes the package entry.

```
packages/
  cli/          # CLI shell: cli.ts + shared/ui + bin entry; depends on the feature packages
  core-<area>/  # one lifted features/<area>/, released/tested independently
  adapters-<x>/ # shared infrastructure implementations
  shared/       # cross-cutting types and utils used across packages
```

For user-extensible CLIs, add a **plugin architecture**: discover and load command modules dynamically (e.g. resolve installed plugin packages, or treat `mycli-<name>` executables on PATH as `mycli <name>`). Introduce plugins only when third parties must extend the CLI — not for internal organization, which packages already handle.

## Startup performance

For a CLI invoked from scripts, shell hooks, git hooks, or tight loops, cold-start latency *is* a feature. Three patterns matter, in order:

- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers, alternate server modes) by inspecting `process.argv` directly and `await import(...)`-ing the handler — *before* loading the parsing framework. The `--version` path should load zero modules beyond the entry file: print a version string inlined at build time and return.
- **Lazy feature registration**: register each feature with a loader (`() => import('./features/user/index.js')`) instead of an eager import, so only the dispatched feature evaluates. A per-feature `index.ts` registers commands, but `cli.ts` must reference it through the loader — eager-importing every feature's `index.ts` to register them defeats this and reloads the whole CLI on every `--version`.
- **Build-time feature gates**: wrap optional subsystems (a daemon mode, an alternate transport, an internal-only feature) in `if (feature('FOO')) { ... }` where `feature()` is resolved at build time. Keep the condition inline — not behind a variable — so the bundler dead-code-eliminates the whole branch. Both bundle size and import time drop.

Measure before optimizing: instrument the entry file with named checkpoints (`performance.mark()`), sample on a small percentage of invocations, and emit phase durations. Pick a budget — for something people invoke from `.bashrc` or git hooks, anything over ~80 ms is noticeable. Without measurement, "optimizations" become folklore.

## Type safety

- Enable `strict` fully in tsconfig. It catches the common CLI bugs early — unhandled null flags, uninitialized state.
- Validate args/flags at the command boundary with a schema validator (e.g. **Zod** or **Valibot**), then pass the parsed, typed object inward. Core never receives raw strings it must re-parse. The validator's error messages double as the user-facing error for bad input (rewrite them for humans per `ux-guidelines.md`).
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## CLI behavior contract

These keep the tool scriptable and composable:

| Concern | Rule |
|---|---|
| Exit codes | `0` success, non-zero failure; distinguish business error from misuse. Scripts and CI depend on this. |
| stdout vs stderr | Real results to stdout; logs, progress, errors to stderr — so output pipes cleanly. |
| Machine output | Support `--json` (or `--output`) for structured data. Route both human and machine output through a single I/O module that picks a mode once at startup — never let individual commands call `console.log` *and* `JSON.stringify` themselves, or formats drift across commands and NDJSON streams break on the first circular reference or `BigInt`. |
| Config precedence | Resolve in layers: defaults < config file < environment variables < flags; later overrides earlier. Centralize in a config loader in `shared/lib`. |
| Color / TTY | Detect non-TTY (pipe/CI) and disable color/spinners; honor `NO_COLOR`. |
| Destructive actions | Default to confirmation; provide `--force`/`--yes` to bypass for automation. Make repeatable actions idempotent and offer `--dry-run`. |
| Verbosity | Provide `--quiet` and `--verbose`. |
| Stdin | Accept `-` as a filename to read stdin, so the tool composes in pipes. |
| End of options | Accept `--` to stop flag parsing and pass the rest through verbatim (e.g. to a spawned subprocess). |
| Interactivity | Prompt only when stdin is a TTY; every prompt needs an equivalent flag so non-interactive/CI runs never block. |
| Signals | Exit promptly on SIGINT — announce before any cleanup, bound cleanup with a timeout, and skip it on a second Ctrl-C. Design crash-only so an interrupted run can resume. |

## Build and distribution

- Add a `bin` entry in package.json pointing at the built entry file; start that file with `#!/usr/bin/env node`.
- Bundle with an esbuild-based bundler (e.g. tsup or tsdown): emit a runnable entry, generate declaration files only when shipping a library, and externalize `dependencies`/`peerDependencies` so they are not inlined.
- Target a modern Node version with `platform: node`, and declare the floor in package.json `engines`. The stdlib-first APIs this skill leans on land at specific versions — `process.loadEnvFile`/`util.parseEnv` in 20.12, stable `util.styleText` in 22 — so target **Node ≥ 20.12** (or ≥ 22 to use `styleText` without a flag), and guard or polyfill anything newer than your floor.
- Prefer **ESM-only** output for a Node-only tool. Add CJS output only when other packages import yours as a library — dual publishing carries real maintenance cost otherwise.
- For local development, run TypeScript directly (e.g. `tsx`) so you don't rebuild on every change.
- Inject build-time **macros** for static values: version, build timestamp, commit SHA. Inlining keeps the `--version` fast-path zero-import (no `import { version } from '../package.json'`) and makes telemetry stable across distribution channels.
- Set the `files` field in package.json (or an `.npmignore`) so only the built output ships — not `src/`, tests, or fixtures. Smaller installs, faster `npx`.

## Cross-platform

A Node CLI is expected to run on Windows, macOS, and Linux. Bake that in rather than retrofitting it:

- Build paths with `path.join`/`path.resolve`, never `'/'` concatenation. Use `process.cwd()` for user-supplied paths and `import.meta.url`/`__dirname` for files shipped with the tool.
- Don't assume a shell, `bash`, `/tmp`, or POSIX-only env vars in spawned commands; honor `TMPDIR`/`TEMP`. Prefer passing an args array to `spawn` over a shell string.
- The `#!/usr/bin/env node` shebang plus a `bin` entry is what makes the tool launch cross-platform — npm generates the Windows `.cmd` shim from it.

## Testing

- **Unit-test the feature core (`service.ts`/`domain.ts`) heavily** — fast, no process spawn, no terminal mocking. Most coverage belongs here. Inject fake adapters for I/O.
- **Integration-test commands** by invoking the parser with an argv array and asserting on the result and exit behavior.
- **Snapshot-test rendering** (`ui.ts`, `shared/ui`, help text, tables) when output stability matters.
- Because logic lives in each feature's core, you rarely need brittle end-to-end shell tests — keep those few and reserved for the wiring (entry → parse → exit code), and smoke-test the **built binary** on a handful of happy paths to exercise the shebang/`bin` wiring and real exit codes. Tests can live beside each feature (`features/<feature>/*.test.ts`), keeping a feature self-contained.

## Common mistakes

| Mistake | Fix |
|---|---|
| Business logic in a command handler | Move it to the feature's `service.ts`; the handler only parses, delegates, formats. |
| A feature's `service`/`domain` importing the parsing framework or `ui` | Invert the dependency; core takes plain data and interfaces. |
| Core calling `process.exit` or `console` | Throw typed errors; let the CLI boundary map them to exit codes and render. |
| One feature importing another feature's internals | Go through the other feature's public `index.ts`, or promote the shared thing to `shared/`. |
| Repeating flag/error/config wiring in each command | Centralize on a base command or middleware with one error boundary. |
| One giant `commands.ts` / `index.ts` | One file per command, directory mirroring the command tree, inside the feature. |
| Logs mixed into stdout | Results to stdout, everything else to stderr. |
| No machine-readable output | Add `--json` early; retrofitting every command later is costly. |
| Eager-importing every feature to register them | Register through lazy loaders so only the dispatched feature evaluates. |
| Loading the parsing framework before checking common flags | Handle `--version` and internal subprocess modes by inspecting `process.argv` in the entry file first, before importing the framework. |
| Reading config or env at module top level | Read inside an explicit init function the entry file calls once. Top-level side effects defeat fast-paths and make startup non-deterministic. |
| Organizing by technical layer (`commands/`, `services/`, …) | Organize by feature; the layer-first cut forces an app-wide re-slice once features multiply. |
| Monorepo or plugins built upfront | Stay single-package until a part needs its own lifecycle. |
| Dual CJS+ESM publishing by default | ESM-only unless consumed as a library. |

## Supporting libraries

A CLI needs leaf libraries for color, spinners, progress, tables, prompts, logging, config, paths, subprocess, and diff rendering. These belong in `ui` (feature `ui.ts` or `shared/ui`), `shared/lib`, and `adapters` — never in a feature's `service`/`domain` — and any TTY-dependent output stays gated behind `ui`. Check the Node standard library before adding one (`util.styleText`, `util.parseArgs`, `--env-file`). For category-by-category selection criteria and representative packages, see `cli-libraries.md`. For the parsing framework specifically, see `frameworks.md`.

## Persisting user data

When the CLI needs to store anything for the user — config, credentials, projects, cache, backups, logs — read `user-data-storage.md` before designing the layout. It covers the invariants (global vs per-project separation, separable disposable data, keychain-first credentials, overridable root), the two legitimate layout shapes and how to choose, cross-platform locations, and the path-resolution module pattern.
