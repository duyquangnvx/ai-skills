# Node/TS CLI Frameworks

Choosing the argument-parsing layer. All of these sit at the `commands/` boundary in the architecture (`architecture-ts.md`); none of them should leak into `core/`. Pick by complexity, not popularity.

## The four mainstream options

**Commander** — the minimalist default. Small, near-zero runtime dependencies, TypeScript-native, fastest startup. Does parsing, subcommands, and help and little else. Best for the majority of small-to-medium CLIs. Pair it with a schema validator (Zod) for typed, validated input.

**yargs** — the feature-rich middle ground. Built-in type coercion, choices validation, typo suggestions, shell completion, and a middleware layer that makes complex validation and layered configuration elegant. Heavier than Commander (more dependencies, slower startup). Good when configuration/validation is genuinely complex.

**oclif** (Salesforce/Heroku) — the full platform. Class-based commands, file-based subcommands, a plugin system, project scaffolding, auto-generated docs, and testing utilities. Heaviest dependency footprint and slowest startup, with the steepest learning curve. Worth it for large CLIs with many commands that need plugins and will grow over years.

**clipanion** (used by Yarn) — class-based and designed around type safety, with idiomatic syntax that minimizes boilerplate. A good fit when you want strict TypeScript ergonomics and class-based commands without oclif's full platform weight.

## Tradeoff summary

| Dimension | Commander | yargs | oclif | clipanion |
|---|---|---|---|---|
| API style | functional, minimal | builder + middleware | class, file-based | class, type-first |
| Type coercion / choices validation | manual | built-in | built-in | strong (type-driven) |
| Typo suggestions | no | built-in | no | partial |
| Plugin system | no | no | yes | no |
| Scaffolding / auto docs / test utils | no | no | yes | no |
| Runtime dependencies | ~none | several | many | few |
| Relative startup cost | lowest | medium | highest | low |

Numbers (download counts, exact dependency counts, millisecond benchmarks) reported across sources vary and drift over time — treat the table as relative ordering, not absolute figures. Commander is consistently reported as by far the most widely used; oclif as the heaviest. If startup latency matters (a tool invoked constantly, or in tight CI loops), favor the lighter end and lazy-load commands.

## Selection guidance

- **Default / small-to-medium CLI** → Commander + Zod (validate at the boundary) + esbuild/tsup (bundle) + tsx (dev). This is the pragmatic stack for most tools.
- **Complex validation or layered config is the hard part** → yargs for its middleware, or stay on Commander + Zod if the team prefers explicit code.
- **Large, multi-command, plugin-extensible tool that will grow for years** → oclif.
- **Strict TypeScript, class-based commands, minimal boilerplate, no need for oclif's platform** → clipanion.

## What stays constant regardless of choice

The framework only replaces the `commands/` + parsing layer. The thin-command/fat-core split, the `core/` and `adapters/` layers, Zod validation at the boundary, the stdout/stderr and exit-code contract, and the testing strategy are all framework-independent — keep them identical no matter which parser you pick. That decoupling is also what lets you switch frameworks later with low cost.

## Companion libraries (optional, mix as needed)

- Prompts/interactivity: `@inquirer/prompts`, `prompts`, or `clack`.
- Spinners/progress: `ora`.
- Color: `picocolors` (tiny) or `chalk`; always gate on TTY / `NO_COLOR`.
- Tables: `cli-table3`.
- Rich/interactive UIs: `ink` (React for the terminal) — only when a static text UI genuinely isn't enough.
