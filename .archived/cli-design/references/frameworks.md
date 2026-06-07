# Node/TS CLI Frameworks

Choosing the argument-parsing layer. All of these sit at the `commands/` boundary in the architecture (`architecture.md`); none of them should leak into the `core` (`core/services`/`core/domain`, the fat core). Pick by complexity, not popularity.

## The insight that splits the field: chaining vs declarative

Method-chaining/builder APIs (Commander, yargs, cac) are imperative: each `.option()` call mutates a parser instance at runtime, and TypeScript cannot accumulate the growing shape of the parsed-args object across a fluent chain. The handler's input type ends up being whatever you manually annotate — so the compile-time type and the runtime parser are maintained *separately* and can silently drift.

Declarative, type-driven APIs (stricli, citty, gunshi; clipanion via typed class fields) define the full argument spec as one data structure, so TypeScript infers the parsed-args type from a single source of truth and it flows end-to-end into the handler. Every framework with genuine end-to-end inference is declarative — this is structural, not an implementation detail (Bloomberg's stricli "Alternatives" analysis lays it out).

This doesn't disqualify the chaining family: Commander + Zod validation at the boundary recovers runtime safety and a typed object. But know which side of the line you're on.

## The main options

**Commander** — the minimalist default. Zero runtime dependencies, by far the most widely used parser in the ecosystem, TypeScript-native, fast startup. Does parsing, subcommands, help, and opt-in "did you mean" suggestions — and little else. Method-chaining API, so pair it with a schema validator (Zod) for typed, validated input. Best for the majority of small-to-medium CLIs.

**yargs** — the feature-rich middle ground. Built-in type coercion, choices validation, typo suggestions, shell completion, and a middleware layer that makes complex validation and layered configuration elegant. Heavier than Commander (several runtime dependencies, slower startup) and the TypeScript story requires manual typing. Good when configuration/validation is genuinely complex.

**oclif** (Salesforce/Heroku) — the full platform. Class-based commands, file-based command discovery, a plugin system, project scaffolding, auto-generated docs, and testing utilities. Heaviest dependency footprint (~two dozen runtime deps) and slowest startup, with the steepest learning curve; command config as static class properties couples definition to implementation, which is what forces its manifest workaround for startup cost. Worth it for large CLIs that need third-party plugins and will grow for years — its home turf is Salesforce/Heroku/Shopify/Twilio-scale tools.

**clipanion** (used by Yarn Berry) — class-based, with typed *fields* as the source of truth, so inference is good without a DSL. One runtime dependency (typanion). Two cautions: all commands must load at runtime for routing (no lazy per-command loading), and releases have stalled — v4 has sat in release-candidate state since late 2024 with the npm `latest` tag pointing at the prerelease; the stable line is v3.

**citty** (UnJS, used by Nuxt's `nuxi`) — the lightweight declarative option: zero dependencies, built on Node's native `util.parseArgs`. Typed args (string/boolean/positional/enum, `--no-` negation), recursively nested subcommands with lazy/async loading, auto `--help`/`--version`, and `setup`/`cleanup` lifecycle hooks. ESM-only, and still pre-1.0 — real adoption, but expect API movement. A natural fit in the UnJS ecosystem or when you want Commander-level simplicity with lazy subcommands and typed args built in.

**stricli** (Bloomberg, 2024) — built explicitly around the declarative thesis above. Zero dependencies. Command *definitions* and *implementations* live in separate modules linked by `import()`: the whole command tree loads for routing without pulling in any implementation, and a command's module evaluates only when it actually runs — lazy loading is the default architecture, not an opt-in. TypeScript introspects the `import()` so flag types are checked against the handler end-to-end. Ships an isolated `CommandContext` (injected streams/services — the context-injection pattern from `architecture.md`, built in), a scaffolder, and shell completion. Deliberately no plugin system. The tradeoff: young, small ecosystem and community.

Worth knowing about, one line each: **cac** (Vite's parser; stable but minimal activity), **brocli** (Drizzle's declarative parser, adoption mostly Drizzle itself), **gunshi** (modern declarative, tiny adoption so far), **trpc-cli** (generate a CLI from an existing tRPC router — niche but excellent if you're already there).

## Tradeoff summary

| Dimension | Commander | yargs | oclif | clipanion | citty | stricli |
|---|---|---|---|---|---|---|
| API style | method chaining | builder + middleware | class, file-based | class, typed fields | declarative objects | declarative, defs/impl split |
| End-to-end type inference | no (pair with Zod) | weak/manual | partial (static props) | good | good | best-in-class |
| Lazy per-command loading | no | no | via manifest | no | yes | yes (core design) |
| Typo suggestions | opt-in | built-in | built-in | partial | no | via completion |
| Plugin system | no | no | yes | no | no | no (by design) |
| Scaffolding / docs gen / test utils | no | no | yes | no | no | scaffolder only |
| Runtime dependencies | none | several | many | one | none (native `parseArgs`) | none |
| Relative startup cost | lowest | medium | highest | low | lowest | lowest |
| Maturity / ecosystem | huge | huge | large | stalled (v4 RC limbo) | pre-1.0, growing | young, small |

Download counts and benchmarks drift — treat the table as relative ordering, not absolute figures. Commander remains by far the most used; oclif the heaviest. If startup latency matters (a tool invoked constantly, or in tight CI loops), favor the lazy-loading column.

## Evaluate against your command surface

Pick by complexity, not popularity. Score the candidates against what the CLI actually needs, and prefer the lightest option until scale forces more batteries:

- **Nested subcommands**: clean support for multi-level commands and one-file-per-command, or must it be hand-wired?
- **Type safety**: is end-to-end inference from definitions a requirement, or is boundary validation with Zod enough?
- **Startup latency**: lazy per-command loading and framework weight — matters for commands run in tight loops, negligible for long batch operations.
- **Machine output**: a built-in structured/`--json` mode, or build the reporter layer yourself (you likely want your own anyway — see `architecture.md`)?
- **Extensibility**: native third-party plugin loading needed, or not? (Most CLIs never need it.)
- **Testability**: command test helpers, or an injectable context.

## Selection guidance

- **Default / small-to-medium CLI** → Commander + Zod (validate at the boundary) + tsdown or esbuild (bundle) + tsx (dev). The pragmatic stack for most tools.
- **Complex validation or layered config is the hard part** → yargs for its middleware, or stay on Commander + Zod if the team prefers explicit code.
- **Large, multi-command, third-party-plugin-extensible tool that will grow for years** → oclif.
- **Type-safety-first, lazy loading, and an injectable test context built in — and a young ecosystem is acceptable** → stricli.
- **In the UnJS ecosystem, or want the lightest zero-dependency declarative parser** → citty.
- **Class-based commands à la Yarn** → clipanion, pinned to the stable v3 line; check release activity before committing.

## What stays constant regardless of choice

The framework only replaces the `commands/` + parsing layer. The thin-command/fat-core split, the fat-core (`core/services`/`core/domain`) and `adapters/` layers, context injection, the reporter, Zod validation at the boundary, the stdout/stderr and exit-code contract, and the testing strategy are all framework-independent — keep them identical no matter which parser you pick. That decoupling is also what lets you switch frameworks later with low cost.

## Companion libraries

The parsing framework is only one dependency. For the rest — color, spinners, progress, tables, prompts, logging, config, paths, subprocess, diff — see `cli-libraries.md`, which maps each category to its layer (`ui/`, `lib/`, `adapters/` — never the `core`) with selection criteria and representative packages. Check what the chosen framework already bundles (some ship an `ux`-style namespace) before adding leaf libraries.
