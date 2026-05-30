# TypeScript/Node Architecture

How to structure CLI code so it stays testable and maintainable as it grows. These rules hold regardless of the argument-parsing framework chosen (see `frameworks.md`).

## Contents
- [Core principle: thin commands, fat core](#core-principle-thin-commands-fat-core)
- [Project structure](#project-structure)
- [Layer rules](#layer-rules)
- [Type safety](#type-safety)
- [Build and distribution](#build-and-distribution)
- [Cross-platform](#cross-platform)
- [CLI behavior contract](#cli-behavior-contract)
- [Startup performance](#startup-performance)
- [Testing](#testing)

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
- **`core/`**: deterministic where possible; receives plain data, returns plain data or throws domain errors. Imports nothing from `commands/` or the parsing framework.
- **`adapters/`**: the only place that performs I/O across process boundaries. Core depends on adapter *interfaces*, not concrete implementations, so it can be tested with fakes. This is also where to wrap nondeterministic sources (clock, random, UUID) so core stays deterministic and testable.

## Type safety

- Enable `strict` fully in tsconfig. It catches most CLI bugs early — unhandled null flags, uninitialized state.
- Validate args/flags at the command boundary with a schema validator (e.g. **Zod** or **Valibot**), then pass the parsed, typed object inward. Core should never receive raw strings it must re-parse. The validator's error messages double as the user-facing error for bad input (rewrite them for humans per the UX guidelines).
- Use `satisfies` for command/flag config objects to keep precise literal types while checking shape.

## Build and distribution

- Add a `bin` entry in package.json pointing at the built entry file, and start that file with `#!/usr/bin/env node`.
- Bundle with an esbuild-based bundler (e.g. tsup or tsdown): emit a runnable entry, generate declaration files only if shipping a library, and externalize `dependencies`/`peerDependencies` so they are not inlined.
- Target a modern Node ES version with `platform: node`.
- Prefer ESM-only output for a tool that only runs under Node. Add CJS output only when other packages import yours as a library — dual publishing adds real maintenance cost otherwise.
- For local development, run TypeScript directly (e.g. `tsx`) so you don't rebuild on every change.
- Set the `files` field in package.json (or an `.npmignore`) so only the built output ships — not `src/`, tests, or fixtures. Smaller installs, faster `npx`.

## Cross-platform

A Node CLI is expected to run on Windows, macOS, and Linux. Bake that in rather than retrofitting it:

- Build paths with `path.join`/`path.resolve`, never `'/'` concatenation. Use `process.cwd()` for user-supplied paths and `import.meta.url`/`__dirname` for files shipped with the tool.
- Don't assume a shell, `bash`, `/tmp`, or POSIX-only env vars in spawned commands; honor `TMPDIR`/`TEMP`. Prefer passing an args array to `spawn` over a shell string.
- The `#!/usr/bin/env node` shebang plus a `bin` entry is what makes the tool launch cross-platform — npm generates the Windows `.cmd` shim from it.

## CLI behavior contract

These keep the tool scriptable and composable — they mirror the UX rules but are listed here as concrete code obligations:

- **Exit codes**: return `0` on success, non-zero on failure. Map important failure modes to distinct non-zero codes. Don't `process.exit()` from inside `core/` — let core throw, and have the command/entry layer translate errors to exit codes.
- **stdout vs stderr**: write real results to stdout; write logs, progress, and errors to stderr, so output can be piped.
- **Machine-readable output**: support a `--json` (or `--output`) flag printing structured data, kept separate from human-friendly rendering (which lives in `ui/`).
- **Config precedence**: resolve config in layers — built-in defaults < config file < environment variables < command-line flags — with later sources overriding earlier ones. Centralize this in a config loader in `lib/`.
- **TTY awareness**: branch on `process.stdout.isTTY` for color, spinners, and paging; never animate when output is redirected.
- **Lazy command loading**: with many commands, load command modules lazily so startup stays fast regardless of command count.
- **Signals**: handle `SIGINT`/`SIGTERM` to clean up (remove temp files, restore the cursor/terminal) before exiting.

## Startup performance

For a CLI invoked from scripts, shell hooks, git hooks, or tight loops, cold-start latency *is* a feature — aim well under ~100 ms for those cases. Three patterns, in order of impact:

- **Pre-framework fast-paths**: in the entry file, handle well-known argv shapes (`--version`, internal subprocess workers) by inspecting `process.argv` directly and `await import(...)`-ing the handler *before* loading the parsing framework. The `--version` path should load zero extra modules — print a version string inlined at build time and return.
- **Lazy command modules**: register each command with a loader (`() => import('./commands/foo.js')`) instead of an eager import, so only the dispatched command evaluates (the lazy-loading rule from the contract above).
- **Build-time feature gates**: wrap optional subsystems (a daemon mode, an alternate transport) in `if (feature('FOO')) { ... }` resolved at build time, with the condition inline so the bundler dead-code-eliminates the whole branch — both bundle size and import time drop.

Measure before optimizing: instrument the entry file with `performance.mark()` checkpoints and pick a budget — anything over ~80 ms is noticeable for a tool run from `.bashrc` or git hooks. Without measurement, "optimizations" are folklore.

## Testing

- **Unit-test `core/` heavily** — fast, no process spawn, no terminal mocking. Most coverage belongs here. Inject fake adapters for I/O.
- **Integration-test commands** by invoking the parser with an argv array and asserting on the result and exit behavior.
- **Snapshot-test `ui/` rendering** (help text, tables) when output stability matters.
- Because logic lives in `core/`, you rarely need brittle end-to-end shell tests — keep those few and reserved for the wiring (entry → parse → exit code).
