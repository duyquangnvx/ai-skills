# Node/TS CLI Frameworks

Choosing the argument-parsing layer. All of these sit at the `commands/` boundary in the architecture (`architecture.md`); none of them should leak into a feature's `service`/`domain` (the fat core). Pick by complexity, not popularity.

## The main options

**Commander** — the minimalist default. Small, near-zero runtime dependencies, TypeScript-native, fastest startup. Does parsing, subcommands, and help and little else. Best for the majority of small-to-medium CLIs. Pair it with a schema validator (Zod) for typed, validated input.

**yargs** — the feature-rich middle ground. Built-in type coercion, choices validation, typo suggestions, shell completion, and a middleware layer that makes complex validation and layered configuration elegant. Heavier than Commander (more dependencies, slower startup). Good when configuration/validation is genuinely complex.

**oclif** (Salesforce/Heroku) — the full platform. Class-based commands, file-based subcommands, a plugin system, project scaffolding, auto-generated docs, and testing utilities. Heaviest dependency footprint and slowest startup, with the steepest learning curve. Worth it for large CLIs with many commands that need plugins and will grow over years.

**clipanion** (used by Yarn) — class-based and designed around type safety, with idiomatic syntax that minimizes boilerplate. A good fit when you want strict TypeScript ergonomics and class-based commands without oclif's full platform weight.

**citty** (UnJS, used by Nuxt/Nitro) — the lightweight, zero-dependency option, built directly on Node's native `util.parseArgs`, so startup is fast and the install is tiny. Declarative command objects with typed args (string/boolean/positional/enum→union types, `--no-` negation), recursively nested subcommands with lazy/async loading (`Resolvable<T>`), auto `--help`/`--version`, and `setup`/`cleanup` lifecycle hooks for cross-cutting concerns. TypeScript-first and ESM. A natural fit when you're already in the UnJS/Nitro ecosystem, or want Commander-level simplicity with lazy subcommands and typed args built in.

## Tradeoff summary

| Dimension | Commander | yargs | oclif | clipanion | citty |
|---|---|---|---|---|---|
| API style | functional, minimal | builder + middleware | class, file-based | class, type-first | declarative objects |
| Type coercion / choices validation | manual | built-in | built-in | strong (type-driven) | built-in (typed args + enum) |
| Typo suggestions | no | built-in | no | partial | no |
| Plugin system | no | no | yes | no | no (lifecycle hooks) |
| Scaffolding / auto docs / test utils | no | no | yes | no | no |
| Runtime dependencies | ~none | several | many | few | none (native `parseArgs`) |
| Relative startup cost | lowest | medium | highest | low | lowest |

Numbers (download counts, exact dependency counts, millisecond benchmarks) reported across sources vary and drift over time — treat the table as relative ordering, not absolute figures. Commander is consistently reported as by far the most widely used; oclif as the heaviest. If startup latency matters (a tool invoked constantly, or in tight CI loops), favor the lighter end and lazy-load commands.

## Evaluate against your command surface

Pick by complexity, not popularity. Score the candidates against what the CLI actually needs, and prefer the lightest option until scale forces more batteries:

- **Nested subcommands**: clean support for multi-level commands and one-file-per-command, or must it be hand-wired?
- **Machine output**: a built-in structured/`--json` mode, or build the suppress-logs-and-serialize layer manually for every command?
- **Extensibility**: native plugin loading needed, or not?
- **Startup latency**: framework weight and cold-start cost — matters for commands run in tight loops, negligible for long batch operations.
- **Flag/arg type-safety** and **command test helpers**.

## Selection guidance

- **Default / small-to-medium CLI** → Commander + Zod (validate at the boundary) + esbuild/tsup (bundle) + tsx (dev). This is the pragmatic stack for most tools.
- **Complex validation or layered config is the hard part** → yargs for its middleware, or stay on Commander + Zod if the team prefers explicit code.
- **Large, multi-command, plugin-extensible tool that will grow for years** → oclif.
- **Strict TypeScript, class-based commands, minimal boilerplate, no need for oclif's platform** → clipanion.
- **In the UnJS/Nitro ecosystem, or want the lightest zero-dependency parser (native `util.parseArgs`) with lazy subcommands and typed args built in** → citty.

## What stays constant regardless of choice

The framework only replaces the `commands/` + parsing layer. The thin-command/fat-core split, the fat-core (`service`/`domain`) and `adapters/` layers, Zod validation at the boundary, the stdout/stderr and exit-code contract, and the testing strategy are all framework-independent — keep them identical no matter which parser you pick. That decoupling is also what lets you switch frameworks later with low cost.

## Companion libraries

The parsing framework is only one dependency. For the rest — color, spinners, progress, tables, prompts, logging, config, paths, subprocess, diff — see `cli-libraries.md`, which maps each category to its layer (`shared/ui` or feature `ui.ts`, `shared/lib`, `adapters/` — never a feature's `service`/`domain`) with selection criteria and representative packages. Check what the chosen framework already bundles (some ship an `ux`-style namespace) before adding leaf libraries.
