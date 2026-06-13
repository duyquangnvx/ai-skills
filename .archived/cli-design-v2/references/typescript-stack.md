# TypeScript CLI Stack (2025–2026)

Ecosystem picks verified via adversarial research, snapshot early June 2026. Version numbers and download counts will drift — treat them as order-of-magnitude; re-verify before relying on a specific version fact.

## Argument-parsing frameworks

| Framework | Verified state | Notes |
|---|---|---|
| **commander** | ~415.6M weekly downloads — dominant | Stock `.opts()` has NO inferred option types. Add [`@commander-js/extra-typings`](https://github.com/commander-js/extra-typings) (official, same maintainers, typings-only — runtime stays commander) for inferred types on `.action()`/`.opts()`. Import it *in place of* commander. |
| **cac** | v7.0.0 (Feb 2026), ~37.2M dl/week, zero deps, ~41KB, ESM-only | Lightweight, battle-tested choice. |
| **citty** (unjs) | v0.2.2, zero deps, built on native `util.parseArgs` | `defineCommand` helper with type inference; **lazy/async subcommand loading** — large CLIs import only the executed command. Caveat: had real type-inference bugs ([#148](https://github.com/unjs/citty/issues/148), enum/optional-boolean, since fixed) — lower maturity signal. |
| **clipanion** | Type-safe via class-based declarators (`Option.Boolean/String/...`) with TS overloads, no manual annotations | NOT zero-dependency (that claim was refuted 0-3 in verification). |
| **oclif** | Static class properties force loading every command module at runtime; mitigate with `oclif.manifest.json` (caches properties) — [oclif docs](https://oclif.io/docs/plugin_loading) confirm | Fits large plugin-based CLIs (Heroku/Salesforce style); heavy for small tools. |
| **yargs** | TS support is largely automatic via the `type` key; manual handling needed for the Promise-union return (`parseSync`) | No "plugin system" for TS, contrary to Stricli's marketing. |
| **stricli** (Bloomberg) | NOT independently verified | Its [alternatives page](https://bloomberg.github.io/stricli/docs/getting-started/alternatives) is vendor marketing; its blanket claim "method-chaining libs have no accurate TypeScript types" was REFUTED (true only for stock usage, false with extra-typings). |

Selection guide:
- Small–medium CLI, lean + type inference: **cac** or **citty** (citty when lazy subcommands matter).
- Largest ecosystem, long-term stability: **commander + @commander-js/extra-typings**.
- Very large plugin-based CLI: **oclif** (generate the manifest).

## Prompts

Use [`@inquirer/prompts`](https://github.com/SBoudrias/Inquirer.js/discussions/1214) (~12kb package) — the maintainer-endorsed official path for new projects. Legacy `inquirer` (~242kb) is "maintained but not actively developed". Maintainer rationale: "CLI programs are user facing... load time and performance matters."

(@clack/prompts, prompts, enquirer, ink were not covered by verified research — compare against current docs if considering them.)

## Colors / styling

The [e18e](https://e18e.dev/docs/replacements/chalk) ecosystem-performance community recommends replacing chalk with one of:

1. **`util.styleText`** (native `node:util`; added v20.12, stable v22.13) — zero dependency; Node publishes an [official migration guide](https://nodejs.org/en/blog/migrations/chalk-to-styletext). Sensible default.
2. **`picocolors`** — similar API, no chaining.
3. **`ansis`** — chalk-like chaining, RGB/hex support.

## ESM vs CJS

**ESM-only is now safe for CLIs.** `require(esm)` was marked stable in Node.js (Dec 2025, [PR #60959](https://github.com/nodejs/node/pull/60959)) and is unflagged on all supported LTS lines: v20.19.0+ and v22.12.0+ ([implementer's writeup](https://joyeecheung.github.io/blog/2025/12/30/require-esm-in-node-js-from-experiment-to-stability/)).

Conditions:
- Set `"engines": { "node": "^20.19.0 || >=22.12.0" }` (drops EOL Node ≤18).
- `require(esm)` cannot load modules using top-level await.

Confirmed trend: cac v7 and citty are already ESM-only.

## Bundling

**Do not use tsup** — its README states: "This project is not actively maintained anymore. Please consider using tsdown instead." Use **[tsdown](https://tsdown.dev/guide/migrate-from-tsup)** (Rolldown-based, rolldown org; automated migration via `npx tsdown-migrate`) or esbuild directly.

## Single-binary distribution

**Node.js SEA** ([docs](https://nodejs.org/api/single-executable-applications.html)): injects a blob (bundled script) into the node binary so the app runs without Node installed. Stability 1.1 (active development). Node **v25.5.0 (Jan 2026)** added `--build-sea`: the multi-step postject workflow collapsed to one command — `node --build-sea sea-config.json` ([writeup](https://joyeecheung.github.io/blog/2026/01/26/improving-single-executable-application-building-for-node-js/)).

**Bun**: `bun build --compile` produces a self-contained binary (~60MB, varies ~50–100+MB by platform/version; embeds JavaScriptCore runtime). Cross-compiles via `--target`.

Startup comparison (confidence: MEDIUM, methodology-dependent — do not generalize): one benchmark (Tigris, Feb 2026) measured Node ~0.064s vs Bun binary ~0.104s with Node using less memory, but the author noted "Nobody will notice"; an Evan You benchmark with Bun bytecode enabled showed Bun 25% faster than Node SEA. Results flip with configuration.

## Startup performance

The dominant factor is **how much code loads at boot**, not the framework per se. Two verified mechanisms:
- citty: lazy subcommand loading — `sub: () => import('./sub.mjs').then(m => m.default)`
- oclif: manifest file to avoid requiring every command

General pattern: lazy-import command handlers; keep the entry point thin.
