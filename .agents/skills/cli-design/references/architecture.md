# TypeScript/Node CLI Architecture

How to structure CLI code so it stays testable and maintainable as it grows. These rules hold regardless of the argument-parsing framework chosen (see `typescript-stack.md`) — the framework only touches the entry file and the command layer, never the core.

## Core principle: thin commands, fat core

A command file does exactly three things: parse args/flags, call a core function, format the result for the terminal. Everything else — domain rules, calculations, talking to APIs/DB/filesystem — lives in a core layer that knows nothing about argv, the parsing framework, or `console`.

The core then becomes plain functions (plain data in, plain data out) that can be unit-tested without spawning a process, and reused unchanged behind other entry points — a library export, an HTTP handler, or an MCP server. Logic welded into command handlers can only ever be a CLI and is painful to test.

```typescript
// commands/user/command.ts — thin: one slice per noun; each subcommand's action
import { createUser } from "../../core/user.js";

// inside the `user create` action — parse → delegate → format
export async function runCreate(args: { email: string; name: string }) {
  const user = await createUser(args);   // delegate, no logic here
  printUser(user);                       // format for terminal
}

// core/user.ts — fat: framework-agnostic, testable
export async function createUser(input: CreateUserInput): Promise<User> {
  // business rules; no console, no process.exit, no argv, no flags
}
```

## Structure scales with the CLI

Do NOT impose backend layering on a CLI *upfront*. Its commands are already its boundary, and premature layers add indirection that's hard to trace. The harm is three specific things — **not folder names**: (1) **interface/port indirection** — core depending on adapter *interfaces*, mocks, adapter classes; (2) **organizing by technical layer** so one feature scatters across folders; (3) **laying structure down before the code needs it**. Folder names are never the anti-pattern (see *Where the fat core lives* below). Grow the structure only when the current shape hurts:

1. **A single file** until it hurts.
2. **One file per command**, directory tree mirroring the command tree; keep the tree shallow — beyond three levels is a signal to regroup.
3. **Extract core functions** (plain data in, plain data out) where a test or a second entry point actually needs them — not preemptively for every command.

When a core function is hard to test because it performs I/O, pass the I/O in as a function parameter — plain dependency injection, no interface layer:

```typescript
// testable with inline fakes — no mocks, no adapter classes
export async function syncProjects(
  input: SyncInput,
  fetchProjects: () => Promise<Project[]>,
  writeManifest: (data: Manifest) => Promise<void>
): Promise<SyncResult> { ... }
```

Treat nondeterminism (clock, random, UUID) the same way: take it as a parameter where a test needs to pin it.

**Where the fat core lives scales the same way.** Inline in the command file at first; a per-command module next; a shared `core/` folder once logic is reused across commands (see the skeleton below; growing `core/` into role-named folders comes after it). None of this is the layering warned against: **"ports-and-adapters" names an *indirection* pattern** (core depending on adapter *interfaces*, mocks, adapter classes), **not a folder literally named `adapters/`**. A folder that merely groups concrete modules behind their `index.js` barrels — DI still by plain function parameters, feature slices still vertical (each command keeps its `{command, logic, view}` together) — is a grouping, not a layer.

### A grown-CLI skeleton

A worked layout once the CLI has grown past a single file — generic names, adapt freely. Smaller CLIs collapse the right-hand folders (no `core/` yet, logic inline in the slice); larger ones split `core/` as shown:

```
src/
  cli.ts                   # entry: bootstrap → fast-paths (--version) → dispatch
  context.ts               # CliContext: injected streams, env, cwd, reporter
  errors.ts  exit-codes.ts # typed domain errors + the single exit-code map
  commands/                # one folder per command (a noun); slice stays vertical
    user/                  #   noun verb: `mycli user create`, `mycli user list`
      command.ts           #     thin: define subcommands, parse → call core → reporter
      service.ts           #     the command's use-case logic
      view.ts              #     human rendering only (--json bypasses it)
  core/                    # framework-agnostic logic shared across commands
    user.ts                #   plain data in, plain data out; no argv/console
  lib/                     # primitives: reporter, paths, config loader, fs helpers
```

`core/` is the default home for shared logic, and the skeleton above (with `core/`) is the end-state for most CLIs. **Only when a flat `core/` grows to enough deep modules that scanning it hurts**, replace that single `core/` with two sibling folders sitting where it was — `domain/` (data-owners) and `adapters/` (boundary-crossers: HTTP/DB/LLM clients), both beside `commands/`. There is no `core/` afterward — the two folders take its place (they are siblings, never nested inside a `core/`). Everything else is unchanged: `commands/` stays vertical, `lib/` stays put. This split is optional polish, not a milestone to aim for.

## Inject context instead of touching globals

Pass commands their environment — streams, env, cwd — as an injected context object instead of letting them reach for `process` globals:

```typescript
interface CliContext {
  stdout: Writable;
  stderr: Writable;
  env: Record<string, string | undefined>;
  cwd: string;
  reporter: Reporter;
}
```

Production wires it from the real `process` once, in the entry file; tests pass a fake with in-memory streams and assert on captured output — no process spawn, no module mocking. Two major CLIs arrived at this shape independently: Stricli's isolated `CommandContext` and the GitHub CLI's `IOStreams` + factory pattern (every command writes through injected streams, never `os.Stdout` directly).

Don't pass the context into core functions wholesale — core takes plain data and, where it needs I/O, explicit function parameters. The context belongs to the command/UI layer.

## One reporter for all output

Route every byte of output through a single module that decides the rendering mode **once at startup**: human or `--json`, color on/off (TTY, `NO_COLOR`, `--no-color`), quiet level, spinners or not. Commands hand it structured data; it picks the stream and the format.

- Results go to stdout; logs, progress, and errors go to stderr — the reporter is the one place that knows this.
- `--json` is a **parallel rendering path, not a serialization of the human text**. It may carry more fields than the human table (raw timestamps, IDs, full lists). Never let individual commands call `console.log` *and* `JSON.stringify` themselves — formats drift across commands, and ad-hoc serialization breaks on the first circular reference or `BigInt`.
- All TTY-dependent libraries (color, spinners, progress) are called only from here, so non-interactive modes are suppressed in one place.

## Views as components

The UI layer mirrors a frontend design system, and the analogy is worth using when organizing it:

| Frontend | CLI |
|---|---|
| Design-system components (Button, Table, Badge) | Primitives — `renderTable()`, `statusBadge()`, spinner, keyValue list |
| Page components (UserUpdatePage) | Views — `renderUserUpdate(result)`, `renderDeployStatus(deploy)` |
| Route | Command |
| Two pages share UI → extract a component | Two commands print similar output → extract a primitive |

Three differences from React — and they are the boundaries to hold:

1. **Views are pure one-shot functions** — data in, text out, done. No state, no lifecycle, no re-render: the terminal is append-only, printed output can't be updated (spinners/log-update in a TTY are the narrow exception). The day a view needs to be genuinely stateful and live-updating (a parallel-deploy dashboard), switch that surface to **Ink** — real React for the terminal — instead of smuggling state into views.
2. **A view owns only the human rendering path** — unlike a React component, it is not the only way out. The command hands structured data to the reporter; the reporter calls the view in human mode and serializes directly in `--json` mode, skipping the view entirely. Putting `--json` logic inside a view breaks the pattern.
3. **Views never print** — they return/render through the injected reporter, never `console.log`, so TTY/color/quiet handling stays centralized.

```typescript
// ui/views/deploy.ts — "page component", pure
export function renderDeploy(deploy: DeployResult): string {
  return [
    statusBadge(deploy.status),                     // primitive
    keyValue({ env: deploy.env, sha: deploy.sha }), // primitive
    renderTable(deploy.services, ["name", "state"]) // primitive
  ].join("\n")
}

// commands/deploy.ts — the command never knows how the view renders
const result = await runDeploy(input)
ctx.reporter.result(result, renderDeploy)  // human → view; --json → serialize
```

## Cross-cutting concerns: base command and errors

Define behavior shared by every command once — on a base command or middleware — so command files stay thin:

- Global flags (`--json`, `--verbose`, `--quiet`, `--no-color`, `--config`), config loading, and a single top-level error boundary live here, not copy-pasted per command.
- Core defines and throws typed domain errors; it never calls `process.exit` or `console`. The boundary catches, maps each error type to an exit code, and renders through the reporter — clean message to stderr by default, stack only under `--verbose`/`DEBUG`, structured under `--json`. For unexpected errors, print a bug-report URL prefilled with version and context.
- **Set `process.exitCode` instead of calling `process.exit()`.** Forced exit truncates pending stdout/stderr writes — typically exactly when piping to a slower consumer. Set the code, let the event loop drain.
- Signals: handle both SIGINT and SIGTERM; bound cleanup with a timeout and `.unref()` that timer so it can't itself hold the process open; restore the cursor/terminal state spinners changed.

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

Make the order between `node bin/cli.js` and the first line of business logic explicit, and keep modules side-effect free so the entry file controls it:

1. **Bootstrap**: process-level tweaks with no I/O cost (heap size, signal handlers, env shims).
2. **Fast-paths**: handled before any framework loads (next section).
3. **Setup**: resolve the working environment (cwd, project root, terminal capabilities), register cross-cutting handlers.
4. **Config + auth resolution**: an explicit init call loads layered config and cached credentials. Modules that need config import the *getter*, not the value.
5. **Command dispatch**: only now does the parsing framework see argv.

Reading config or env at module top level defeats fast-paths (every `--version` pays the cost) and makes startup non-deterministic (state depends on import order).

## Startup performance

Cold-start latency is a feature for tools invoked from scripts, hooks, or tight loops. Three patterns, in order of impact:

- **Lazy command modules**: register each command with a loader (`() => import('./commands/foo.js')`) instead of an eager import, so only the dispatched command's module graph evaluates. The single biggest win — practitioner measurements put eager-everything `--version` an order of magnitude slower.
- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers) by inspecting `process.argv` directly *before* loading the parsing framework. The `--version` path should load zero extra modules — print a string inlined at build time and return.
- **Bundling**: collapsing module files into one removes the resolution waterfall — roughly a 25–30% cold-start cut on large CLIs in practitioner reports, on top of distribution benefits.

Also: **build-time feature gates** — wrap optional subsystems in `if (feature('FOO'))` with the condition inline so the bundler dead-code-eliminates the branch. And **build-time macros** for static values (version, commit SHA) — inlining keeps the `--version` fast-path zero-import.

Measure before optimizing: instrument the entry file with `performance.mark()` checkpoints and pick a budget. Published millisecond figures are directional — your dependency graph is what matters.

## Type safety

- Enable `strict` fully in tsconfig.
- Validate args/flags at the command boundary with a schema validator (**Zod**/**Valibot**), then pass the parsed, typed object inward. Core never receives raw strings it must re-parse. The validator's messages double as user-facing errors for bad input — rewrite them for humans.
- End-to-end inference from flag definitions is a framework property — declarative frameworks infer it natively; Commander gets it via `@commander-js/extra-typings` (see `typescript-stack.md`).
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## Cross-platform

A Node CLI is expected to run on Windows, macOS, and Linux:

- Build paths with `path.join`/`path.resolve`, never `'/'` concatenation. `process.cwd()` for user-supplied paths; `import.meta.url` for files shipped with the tool.
- Don't assume a shell, `bash`, `/tmp`, or POSIX-only env vars in spawned commands; honor `TMPDIR`/`TEMP`. Prefer an args array to `spawn` over a shell string.
- The `#!/usr/bin/env node` shebang plus a `bin` entry is what makes the tool launch cross-platform — npm generates the Windows `.cmd` shim from it.
- For local development, run TypeScript directly (e.g. `tsx`) instead of rebuilding on every change.

## Architecture mistakes

| Mistake | Fix |
|---|---|
| Business logic in a command handler | Move to a core function; the handler only parses, delegates, formats. |
| Hexagonal/ports-and-adapters layering imposed upfront | Grow structure with the CLI: single file → one module per command → extract core functions where tests need them. |
| Core importing the parsing framework, `ui`, or calling `process.exit`/`console` | Invert: core takes plain data (plus I/O as function parameters), throws typed errors. |
| `process.exit(1)` at the boundary | `process.exitCode = 1` — force-exit truncates pending writes. |
| Commands reading `process.stdout`/`process.env` directly | Inject a context; production wires the real process once, tests pass fakes. |
| Repeating flag/error/config wiring in each command | Centralize on a base command with one error boundary. |
| Each command hand-rolling `--json` via `JSON.stringify` | One reporter owns rendering mode, picked once at startup. |
| Eager-importing every command to register them | Register through lazy loaders. |
| Loading the framework before checking common flags | Handle `--version`/subprocess modes from raw `process.argv` first. |
| Reading config/env at module top level | Read inside an explicit init function the entry file calls once. |
| Only handling SIGINT | Handle SIGTERM too (Docker/K8s/CI send it); `.unref()` the cleanup timer. |
| Monorepo or plugins built upfront | Stay single-package until the core has a real second consumer. |

For library selection, build/distribution, and testing recipes, see `typescript-stack.md`. For persisting config/credentials/cache, see `user-data-storage.md`.
