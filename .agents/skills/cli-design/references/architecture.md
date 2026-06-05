# TypeScript/Node Architecture

How to structure CLI code so it stays testable and maintainable as it grows. These rules hold regardless of the argument-parsing framework chosen (see `frameworks.md`) — the framework only touches `cli.ts` and `commands/`, never the `core`.

## Contents
- [Core principle: thin commands, fat core](#core-principle-thin-commands-fat-core)
- [Structure principles](#structure-principles)
- [Layer rules](#layer-rules)
- [Inject context instead of touching globals](#inject-context-instead-of-touching-globals)
- [One reporter for all output](#one-reporter-for-all-output)
- [Multiple entry points: the second façade](#multiple-entry-points-the-second-façade)
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

## Structure principles

Authoritative CLI guidelines (clig.dev, 12 Factor CLI Apps) prescribe behavior contracts, never directory layouts — and so does this skill. What must hold is the set of **layer roles** below and the dependency direction between them; the directory names belong to the product. Name directories with the product's own vocabulary so the top-level tree alone conveys what the tool does — `pipeline/`, `providers/`, `workspace/` tell a newcomer more than `services/`, `adapters/`, `lib/` ever will. Two constraints make that freedom safe:

- Every directory maps to exactly **one** role — a domain name is never an excuse to mix I/O into domain logic.
- The project declares its tree and role mapping in its own docs, and encodes that mapping in the boundary tool (see "Enforce boundaries with tooling") so it is checked, not remembered.

| Role | What must be true | Common names |
|---|---|---|
| Entry | Shebang, bootstrap, fast-paths, command registration, the one error boundary — thin | `cli.ts`, `main.ts` |
| Inbound commands | One module per command, mirroring the command tree; parse → call core → format, nothing else | `commands/`, `cli/` |
| Use-cases | Business orchestration as plain functions `(input, deps) → result`; framework-free | `core/services/`, or domain slices: `pipeline/`, `sync/` |
| Domain | Types, models, rules, typed errors — no I/O | `core/domain/`, `domain/` |
| Ports | Interfaces core consumes — **owned by core**, implemented by the outbound layer | `core/ports/` |
| Outbound I/O | The only place crossing process boundaries (API, DB, fs, subprocess, clock/random/uuid) | `adapters/`, `providers/`, `infra/` |
| Rendering | Reporter + primitives + per-command views; the only TTY-aware layer | `ui/`, `output/` |
| Shared utils | Logger, config loader, path resolution | `lib/`, `shared/` |

The rest of this document uses `commands/`, `core/`, `adapters/`, `ui/`, `lib/` as **role labels** — shorthand for the rows above, not required names.

## Layer rules

- **`commands/`**: no business logic and no direct DB/API/filesystem calls. Validate raw input here, then hand a typed object to a core service.
- **`core/`**: deterministic where possible; receives plain data, returns plain data or throws domain errors. Imports nothing from `commands/`, `ui`, or the parsing framework.
- **`adapters/`**: the only place that performs I/O across process boundaries. In ports-and-adapters terms, `commands/` is the **inbound (driving)** adapter — the CLI is just one entry point — while these are the **outbound (driven)** adapters. Core depends on adapter *interfaces*, not concrete implementations, so it can be tested with fakes — and **core owns those interfaces** (the ports role): define them inside core, never inside the outbound directory. Ports placed with the adapters make "core imports adapters" literally true, so the tree misrepresents the very dependency direction it exists to express. This layer is also where to wrap nondeterministic sources (clock, random, UUID) so core stays deterministic and testable.
- **`ui/`**: two strata, mirroring a frontend design system. **Primitives** are shared and domain-agnostic — table renderer, color, spinner, error rendering, the reporter. **Per-command views** (`renderUserTable(users)`) compose primitives to render one command's human output — the CLI equivalent of a page component, where the command is the route. Unlike React components, views are pure one-shot functions (data in, output out — no state, no lifecycle; ink components are the exception). Views own only the *human* rendering path and never print directly — they render through the reporter (next section) so `--json`/quiet/color/TTY handling stays centralized. When two commands hand-roll similar output, extract a primitive and compose, exactly as you would in a design system. A view is often a six-line function — that's fine and not a reason to skip the stratum: its value is the canonical location every command renders through, not the size of each file. Build both strata upfront; retrofitting them after a dozen commands have each invented their own formatting is the expensive path.

## Inject context instead of touching globals

Pass commands their environment — streams, env, cwd — as an injected context object instead of letting them reach for `process` globals:

```typescript
interface CliContext {
  stdout: Writable;
  stderr: Writable;
  env: Record<string, string | undefined>;
  cwd: string;
  reporter: Reporter;   // see next section
}
```

Production wires it from the real `process` once, in the entry file; tests pass a fake with in-memory streams and assert on captured output — no process spawn, no module mocking. This single decision is what makes command-level tests cheap, and two major CLIs arrived at the same shape independently: Stricli's isolated `CommandContext` (injected `stdout`/`stderr`, extensible with app services like auth or config loaded once) and the GitHub CLI's `IOStreams` + factory pattern (every command writes through an injected streams object, never `os.Stdout` directly).

Don't pass the context into `core/` functions wholesale — core takes plain data and adapter interfaces. The context belongs to the command/UI layer.

## One reporter for all output

Route every byte of output through a single module in `ui/` that decides the rendering mode **once at startup**: human or `--json`, color on/off (TTY, `NO_COLOR`, `--no-color`), quiet level, spinners or not. Commands hand it structured data; it picks the stream and the format.

- Results go to stdout; logs, progress, and errors go to stderr — the reporter is the one place that knows this.
- `--json` is a **parallel rendering path, not a serialization of the human text**. It may carry more fields than the human table (raw timestamps, IDs, full lists). Never let individual commands call `console.log` *and* `JSON.stringify` themselves — formats drift across commands, and ad-hoc serialization breaks on the first circular reference or `BigInt`.
- All TTY-dependent libraries (color, spinners, progress) are called only from here, so non-interactive modes are suppressed in one place.

This makes the entire output rule-set from `ux-guidelines.md` one module's job instead of every command's.

## Multiple entry points: the second façade

The payoff of thin-command/fat-core is that `commands/` is just one inbound adapter. When the same tool must also be an agent-tool surface, an MCP server, an HTTP API, or a programmatic library, build each as a **sibling façade over the same core services** — never as a wrapper that shells out to the CLI, and never by duplicating logic:

```
src/
  commands/          # inbound façade 1: humans + scripts (parse flags → core → reporter)
  agent/tools/       # inbound façade 2: agent tools / MCP (schema in → same core fn → structured data out)
```

- **One operation, one core function, N façades.** Each tool definition wraps exactly the function the corresponding command calls. Logic that exists in a command but not in its tool (or vice versa) is the architecture violation to flag in review.
- **Share the boundary schemas.** Define each operation's input schema (Zod) once; the command validates flags against it, and the tool/MCP definition exports the same schema as its input schema. Two hand-written schemas for the same operation will drift.
- **The structured return is the `--json` path.** Human rendering is CLI-only; other façades return the same structured data `--json` would emit — this is *why* `--json` must be a parallel rendering path, not serialized human text. Typed domain errors map to structured error codes for tools exactly as they map to exit codes for the CLI: one error model, per-façade rendering.
- Façades stay thin, like commands: no business logic in tool handlers.

## Enforce boundaries with tooling

A correct layout is worthless if, two years on, someone imports across a boundary and the dependency direction quietly rots. Turn the convention into a build-time check so it doesn't depend on everyone's discipline over time. Two tools, two jobs — import edges and globals are checked differently:

- **Import edges** — **dependency-cruiser** or **eslint-plugin-boundaries** in CI: `core/` (services or domain) must not import the parsing framework or `ui/`; `core/domain` must not import `adapters/`; `commands/` must not import I/O modules directly instead of going through `core`.
- **Globals** — `console` and `process` are globals, not imports, so a dependency checker cannot see them. Ban them in `core/` with ESLint: `no-console` plus `no-restricted-globals` for `process`, scoped to the core directory.

This converts "rules in your head" into "the build goes red on violation" — which is what actually prevents architectural debt across a project's lifetime.

## Cross-cutting concerns: base command and errors

Define behavior shared by every command once — on a base command or middleware — so command files stay thin instead of re-wiring the same plumbing:

- Global flags (`--json`, `--verbose`, `--quiet`, `--no-color`, `--config`), config loading, and a single top-level error boundary live here, not copy-pasted per command.
- Define typed domain errors in `core` (`core/domain`); core throws them and never calls `process.exit` or `console`.
- The boundary catches errors, maps each type to an exit code, and renders through `ui` — clean message to stderr by default, full detail/stack only under `--verbose`/`DEBUG`, structured under `--json`. One mapping, not a `try/catch` in every command.
- Give each domain error a stable, documented code and an *actionable* message following the anatomy in `ux-guidelines.md` (code → title → description → fix → URL). For unexpected errors, print a bug-report URL prefilled with version and context.
- **Set `process.exitCode` instead of calling `process.exit()`.** Node documents that `process.exit()` forces termination even with writes to stdout/stderr still pending — output gets truncated, typically exactly when piping to a slower consumer. Set the code and let the event loop drain. The *only* legitimate `process.exit()` calls in the whole tool are the force-quit paths in signal handling: second Ctrl-C and the cleanup-timeout expiry. A `--version` fast-path does **not** need one — write the version and return; the loop drains on its own.

```typescript
// cli.ts — the one error boundary
main().catch((error: unknown) => {
  if (error instanceof CliError) {
    reporter.error(error.message, error.suggestion);
    process.exitCode = error.exitCode;
  } else {
    reporter.unexpectedError(error);  // traceback gated by --verbose + bug-report URL
    process.exitCode = 1;
  }
});
```

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

For a CLI invoked from scripts, shell hooks, git hooks, or tight loops, cold-start latency *is* a feature — aim well under ~100 ms for those cases (100–500 ms is the realistic Node target for interactive use; see `ux-guidelines.md`). Three patterns, in order of impact:

- **Lazy command modules**: register each command with a loader (`() => import('./commands/foo.js')`) instead of an eager import, so only the dispatched command's module graph evaluates. This is the single biggest win — practitioner measurements put eager-everything `--version` an order of magnitude slower than lazy.
- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers, alternate server modes) by inspecting `process.argv` directly *before* loading the parsing framework. The `--version` path should load zero extra modules — print a version string inlined at build time and return. One hazard: the framework registers its own `--version` flag, so version handling now exists in two places — wire both to the same inlined constant (or disable the framework's flag) so `tool --version` and `tool sub --version` can never diverge.
- **Bundling**: collapsing thousands of module files into one removes the module-resolution waterfall — measured at roughly a 25–30% cold-start cut on large CLIs, on top of its distribution benefits (see "Build and distribution").

Also: **build-time feature gates** — wrap optional subsystems (a daemon mode, an alternate transport) in `if (feature('FOO')) { ... }` resolved at build time, with the condition inline so the bundler dead-code-eliminates the whole branch.

Measure before optimizing: instrument the entry file with `performance.mark()` checkpoints and pick a budget. Published millisecond figures are directional, not benchmarks — your dependency graph is what matters. Without measurement, "optimizations" are folklore.

## Type safety

- Enable `strict` fully in tsconfig. It catches most CLI bugs early — unhandled null flags, uninitialized state.
- Validate args/flags at the command boundary with a schema validator (e.g. **Zod** or **Valibot**), then pass the parsed, typed object inward. Core should never receive raw strings it must re-parse. The validator's error messages double as the user-facing error for bad input (rewrite them for humans per `ux-guidelines.md`).
- **Define each schema once and derive everything else from it.** The same shape tends to appear at three boundaries — flag validation, config-file validation, persisted-entity validation — plus the domain type and any agent/MCP tool input schema (see the second-façade section). Hand-writing it at each boundary guarantees drift. Put the schema in `core/domain` (a schema library is a pure dependency — no I/O, so it doesn't violate the core's import rules), derive the TS type via `z.infer`, and have flag/config/tool schemas `pick`/`extend` from it rather than restate it.
- If end-to-end inference from flag definitions matters to you, that's a framework property — declarative frameworks infer it, method-chaining ones can't. See `frameworks.md`.
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## CLI behavior contract

These keep the tool scriptable and composable:

| Concern | Rule |
|---|---|
| Exit codes | `0` success, non-zero failure; distinguish business error from misuse. Don't `process.exit()` from inside `core/` — core throws, the boundary maps to exit codes (via `process.exitCode`, see above). Scripts and CI depend on this. |
| stdout vs stderr | Real results to stdout; logs, progress, errors to stderr — so output pipes cleanly. Enforced by the reporter. |
| Machine output | Support `--json` as a parallel rendering path through the reporter (see "One reporter for all output"). |
| Config precedence | Resolve in layers: system < user < project < env vars < flags; later overrides earlier. Centralize in a config loader in `lib/`. |
| Color / TTY | Detect non-TTY (pipe/CI) and disable color/spinners; honor `NO_COLOR`. Branch on `process.stdout.isTTY` inside the reporter; never animate when output is redirected. |
| Destructive actions | Confirmation scaled to severity (see `ux-guidelines.md`); `--force`/`--yes` to bypass for automation; idempotent operations plus `--dry-run`. |
| Verbosity | Provide `--quiet` and `--verbose`. |
| Stdin | Accept `-` as a filename to read stdin, so the tool composes in pipes. |
| End of options | Accept `--` to stop flag parsing and pass the rest through verbatim (e.g. to a spawned subprocess). |
| Interactivity | Prompt only when stdin is a TTY; every prompt needs an equivalent flag; respect `--no-input`. |
| Signals | Handle **both SIGINT and SIGTERM** (Docker/K8s/CI send SIGTERM). Announce immediately, bound cleanup with a timeout — and `.unref()` that timer so it can't itself hold the process open — and let a second Ctrl-C skip cleanup. Restore the cursor/terminal state spinners changed. Design crash-only so an interrupted run can resume. |

## Build and distribution

- Add a `bin` entry in package.json pointing at the built entry file, and start that file with `#!/usr/bin/env node`.
- Bundle into a single file. **tsdown** (Rolldown-based, the maintained successor to tsup — tsup itself is in maintenance mode and points users to it) or **esbuild** directly. Emit a runnable entry; generate declaration files only if shipping a library; externalize `dependencies`/`peerDependencies` so they are not inlined.
- Target a modern Node version with `platform: node`, and declare the floor in package.json `engines`. The stdlib APIs this skill leans on land at specific versions: `util.parseArgs` stable since **20**, `util.styleText` stable since **22.13**, `--env-file`/`process.loadEnvFile` stable in the **24** line. A floor of **Node ≥ 22** is the pragmatic default today — but minors matter: adopting `util.styleText` makes the real floor **22.13**, so declare the exact floor your stdlib usage implies; guard or polyfill anything newer than it.
- Prefer ESM-only output for a tool that only runs under Node. Add CJS output only when other packages import yours as a library — dual publishing adds real maintenance cost otherwise.
- For local development, run TypeScript directly (e.g. `tsx`) so you don't rebuild on every change.
- Inject build-time **macros** for static values: version, build timestamp, commit SHA. Inlining keeps the `--version` fast-path zero-import (no `import { version } from '../package.json'`) and makes telemetry stable across distribution channels.
- Set the `files` field in package.json (or an `.npmignore`) so only the built output ships — not `src/`, tests, or fixtures. Smaller installs, faster `npx`.
- Need a true standalone binary (no Node on the target machine)? **`bun build --compile`** is the mature path today. Node's own SEA (single executable applications) is still experimental — usable, recently simplified (`--build-sea`), but expect rough edges.

## Cross-platform

A Node CLI is expected to run on Windows, macOS, and Linux. Bake that in rather than retrofitting it:

- Build paths with `path.join`/`path.resolve`, never `'/'` concatenation. Use `process.cwd()` for user-supplied paths and `import.meta.url`/`__dirname` for files shipped with the tool.
- Don't assume a shell, `bash`, `/tmp`, or POSIX-only env vars in spawned commands; honor `TMPDIR`/`TEMP`. Prefer passing an args array to `spawn` over a shell string.
- The `#!/usr/bin/env node` shebang plus a `bin` entry is what makes the tool launch cross-platform — npm generates the Windows `.cmd` shim from it.

## Testing

- **Unit-test `core/` heavily** — fast, no process spawn, no terminal mocking. Most coverage belongs here. Inject fake adapters for I/O.
- **Test commands with a fake context**: call the command's `run` with an injected `CliContext` whose streams are in-memory buffers, and assert on captured output and the typed result. This is the payoff of context injection — no subprocess, no `console` mocking.
- **Snapshot-test `ui/` rendering** (help text, tables) when output stability matters — a `--help` snapshot also catches accidental interface breaks. Node's built-in test runner supports snapshots natively.
- **A few E2E tests** against the **built binary** via `execa`: assert exit codes and stdout on a handful of happy paths to exercise the shebang/`bin` wiring. Because logic lives in `core/`, these stay few — they cover wiring, not logic.

## Common mistakes

| Mistake | Fix |
|---|---|
| Business logic in a command handler | Move it to `core/services`; the handler only parses, delegates, formats. |
| `core/` importing the parsing framework or `ui` | Invert the dependency; core takes plain data and interfaces. |
| Core calling `process.exit` or `console` | Throw typed errors; let the CLI boundary map them to exit codes and render. |
| `process.exit(1)` at the boundary | `process.exitCode = 1` — force-exit truncates pending stdout/stderr writes. Only signal force-quit paths (second Ctrl-C, cleanup timeout) may call `process.exit()`. |
| Commands reading `process.stdout`/`process.env` directly | Inject a context; production wires the real process once, tests pass fakes. |
| Repeating flag/error/config wiring in each command | Centralize on a base command or middleware with one error boundary. |
| Each command hand-rolling `--json` via `JSON.stringify` | One reporter module owns rendering mode, picked once at startup. |
| One giant `commands.ts` | One file per command, directory mirroring the command tree. |
| Logs mixed into stdout | Results to stdout, everything else to stderr. |
| No machine-readable output | Add `--json` early; retrofitting every command later is costly. |
| Eager-importing every command to register them | Register through lazy loaders so only the dispatched command evaluates. |
| Loading the parsing framework before checking common flags | Handle `--version` and internal subprocess modes by inspecting `process.argv` in the entry file first, before importing the framework. |
| Reading config or env at module top level | Read inside an explicit init function the entry file calls once. Top-level side effects defeat fast-paths and make startup non-deterministic. |
| Only handling SIGINT | Handle SIGTERM too; bound cleanup with an `.unref()`ed timeout. |
| Monorepo or plugins built upfront | Stay single-package until the core has a real second consumer (programmatic API, plugin boundary) — then split within a monorepo, not across repos. |
| Dual CJS+ESM publishing by default | ESM-only unless consumed as a library. |

## Supporting libraries

A CLI needs leaf libraries for color, spinners, progress, tables, prompts, logging, config, paths, subprocess, and diff rendering. These belong in `ui/`, `lib/`, and `adapters/` — never in `core/` — and any TTY-dependent output stays gated behind `ui/`. Check the Node standard library before adding one (`util.styleText`, `util.parseArgs`, `--env-file`). For category-by-category selection criteria and representative packages, see `cli-libraries.md`. For the parsing framework specifically, see `frameworks.md`.

## Persisting user data

When the CLI needs to store anything for the user — config, credentials, projects, cache, backups, logs — read `user-data-storage.md` before designing the layout. It covers the invariants (global vs per-project separation, separable disposable data, keychain-first credentials, overridable root), the two legitimate layout shapes and how to choose, cross-platform locations, and the path-resolution module pattern.
