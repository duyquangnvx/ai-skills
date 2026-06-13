# Project: Internal 2D Game Engine — PixiJS + React

A type-safe, opinionated 2D game engine for our internal team. **PixiJS v8** drives the canvas, **React 19** drives the UI overlay, bridged through framework-agnostic primitives (Zustand store + typed event bus + typed RPC). General-purpose 2D — slot, casual, action, puzzle — not slot-only. DX-first: factory APIs, no `new`, asset-key autocomplete, scene-scoped auto-cleanup, devtools baked in.

## Read before starting any work

Every session MUST read these first, in order:

1. `docs/progression.md` — current implementation status. Which stage, which tasks done, what's in progress, what's blocked, what's next. **Always read before writing code.**
2. `docs/architecture.md` — system architecture, packages, contracts (Engine, Scene, AssetManifest, bridge, hooks).
3. `docs/roadmap.md` — staged delivery plan (Stage 0–9) with explicit exit criteria per stage.
4. `docs/decisions.md` — stack choices, abstraction policy, type-system patterns, model mapping.

If `progression.md` shows Stage 0 incomplete, finish Stage 0 exit criteria before any other work. Don't skip stages.

## Update after finishing work

Every session MUST update `docs/progression.md` before ending, with:

- Tasks completed (move from "In progress" / "Next" → "Done").
- New blockers discovered.
- Decisions made that differ from `docs/decisions.md` (log a one-liner here, propose a new entry in `decisions.md` if material).
- Hand-off notes for the next session: what state the code is in, what's the next logical step, any gotchas (failing tests, half-done refactors, manifest changes pending).

This is the only memory between sessions — don't skip it. Also tick the matching exit-criteria checkbox in `roadmap.md` if a stage advanced.

## Working rules

- **Respect stage boundaries** in `roadmap.md`. Do NOT implement Stage 4 features during Stage 2 "because it's easier to add now." Conventions reserved in earlier stages exist so you don't need to pre-empt later stages.
- **Follow abstraction policy** in `decisions.md`: wrap Pixi / Howler / motion behind chainable handles with `.pixi`/`.howl`/`.motion` escape hatches. Do NOT abstract Zustand, mitt, Vite, Vitest, or React itself — they're consumed directly.
- **Two-layer split is the default**: React imports do not appear in `engine-core` or `engine-pixi`; Pixi imports do not appear in `engine-core` or `engine-react`. Cross-layer comms goes through bridge primitives only (store, events, RPC). The split is not a religious commitment — it is a default that buys four concrete properties (Node-runnable engine-core tests, headless simulation use cases, smaller engine-core bundle for store/events/RPC-only consumers, swappable renderer). To override for a specific module, open a `decisions.md` entry that names: (a) which of the four properties breaks, (b) why the cost is acceptable for this case, (c) what isolation remains. See `decisions.md` §"Abstraction Policy" for the full policy + the running list of concrete costs the split currently imposes (e.g. `ctx.timer` runs on wall-clock, not ticker time).
- **Pre-Stage-7 break-freely policy.** Until the first demo game ships (Stage 7), the engine API is **not frozen**. Breaking changes are preferred over backward-compat shims when they produce cleaner code. Required side-effects: (a) update `apps/playground/`, (b) log the break in `decisions.md` with the *why*, (c) tick the relevant gap or stage exit-criteria. After Stage 7's first demo lands, the freeze-with-migration rule kicks in. (User direction 2026-04-28: free hand still preferred even after Stage 7 — re-evaluate per-change.)
- **Type pattern: generic-passing factory**, not module augmentation. `createGameHooks<S, E, R, Sc>()` per game. Multi-game monorepo demands isolation.
- **Lifecycle owner = scene `ctx`.** Subscriptions, tweens, timers, listeners registered through `ctx.subscribe` / `ctx.on` / `ctx.tween` / `ctx.timer` are auto-cleaned on scene teardown. Raw `engine.store.subscribe(...)` is the caller's problem.
- **Default tween library: `motion`** (free). No GSAP dependency.
- **Default state lib: Zustand vanilla.** Selectors give re-render isolation; no Redux.
- **No `@pixi/react` reconciler.** Pixi stays imperative.
- **Engine never imports from `apps/` or `games/`.** Apps freely import from `engine-*`.
- **Asset manifest is the single source of truth** for keys; factories (`sprite`, `spine`, `audio`) accept only keys whose entry has a compatible `type`. Compile errors > runtime errors.
- **Test with Vitest** at the package level; type tests with `expectTypeOf` for bridge primitives. Smoke-test demo games with Playwright once Stage 7 lands.

## Skills to use

Always invoke the relevant skill via the `Skill` tool **before** writing or editing code in that area. Don't reason from memory of an API — load the skill.

### Process skills (run first when applicable)

- **`superpowers:brainstorming`** — use **before** designing any new feature, system, or API. Engine work is creative work; never jump to implementation without a brainstorm pass that explores intent and tradeoffs.
- **`superpowers:writing-plans`** — when a task spans multiple files or stages, write a plan first.
- **`superpowers:test-driven-development`** — bridge primitives, scene FSM, asset key derivations all benefit from TDD; write the type test or unit test first.
- **`superpowers:systematic-debugging`** — for any bug, test failure, or "the canvas is black" moment, run this skill before guessing.
- **`superpowers:verification-before-completion`** — run before claiming a task is done; evidence > assertions.
- **`superpowers:receiving-code-review`** — when feedback comes in on a PR, use this before mass-applying changes.

### TypeScript

- **`typescript-advanced-types`** — invoke whenever:
  - designing a public engine API (factories, hooks, scene defs, manifest helpers);
  - writing conditional / mapped / template-literal types;
  - implementing the patterns listed in `decisions.md` §"Type-System Patterns" (generic-passing factory, `const` generic, key narrowing, rest-tuple void, `infer` reductions, discriminated unions, branded IDs, assertion functions).

### PixiJS (v8 — every Pixi task)

Use the **router skill first**, then drill into the topic-specific skill it points to:

- **`pixijs`** — entry point for any PixiJS task; routes to specialized skills.

Topic-specific (load when working in that area):

- **`pixijs-application`** — `createGameApp`, `app.init` options, ticker plugin, resize plugin, destroy.
- **`pixijs-scene-core-concepts`** — scene-graph mental model.
- **`pixijs-scene-container`** — `Container`, render groups, sortable children, `cullable`.
- **`pixijs-scene-sprite`** — `Sprite`, `AnimatedSprite`, `NineSliceSprite`, `TilingSprite` (used in `sprite()` / `nineslice()` factories).
- **`pixijs-scene-text`** — `Text`, `BitmapText`, `HTMLText`, `SplitText` (used in `text()` factory).
- **`pixijs-scene-graphics`** — vector shapes, gradients, hit-testing.
- **`pixijs-scene-particle-container`** — for `particle()` factory.
- **`pixijs-assets`** — `Assets.init`, `Assets.load`, multi-resolution suffix handling, custom loaders.
- **`pixijs-events`** — `eventMode`, `FederatedEvent`, used by `onTap()` / `onHover()` chainable APIs and by `engine-core/input`.
- **`pixijs-ticker`** — `Ticker`, `UPDATE_PRIORITY`, `onRender` per-object hook.
- **`pixijs-math`** — `Point`, `Matrix`, `Rectangle`, `toGlobal`/`toLocal` for scaling + hit areas.
- **`pixijs-color`** — color conversions for tints.
- **`pixijs-blend-modes`** — additive / multiply for VFX.
- **`pixijs-filters`** — `BlurFilter`, `ColorMatrixFilter`, custom filter wrapping.
- **`pixijs-custom-rendering`** — only when writing a custom shader / batcher (rare).
- **`pixijs-performance`** — `Culler`, `cacheAsTexture`, GC system, batching rules; consult before optimisation.
- **`pixijs-environments`** — Web Worker / OffscreenCanvas / CSP edge cases.
- **`pixijs-accessibility`** — only if a game enables a11y mode.
- **`pixijs-create`** — only when scaffolding a brand-new app inside the monorepo.
- **`pixijs-migration-v8`** — reference if porting any v7 snippet.

### Game design / development

- **`game-engine`** — guide for our own `@duyquangnvx/pixi-game-engine` patterns when writing manager-style code.
- **`game-developer`** — when implementing systems (input, physics, networking-adjacent, perf optimisation).
- **`game-engineering-team`** — for architecture decisions, system design, code review of game-side code.
- **`game-concept-advisor`** — when brainstorming a demo game (Stage 7) or new mechanics.
- **`game-systems-doc`** — when writing GDD-style specs for demo games.

### Build / verification skills

- **`simplify`** — run after a feature lands to review for reuse and clarity.
- **`fewer-permission-prompts`** — run if permission prompts pile up.
- **`update-config`** — for `.claude/settings.json` changes (hooks, env, allowlist).

### Skill priority

When multiple skills could apply, follow `superpowers:using-superpowers`:

1. Process skills first (`brainstorming`, `systematic-debugging`, `tdd`, `verification-before-completion`).
2. Domain skills second (`typescript-advanced-types`, `pixijs-*`, `game-*`).

## Reference links

### PixiJS v8

- Main docs: https://pixijs.com/8.x/guides
- API reference: https://pixijs.download/release/docs/index.html
- Migration v7→v8: https://pixijs.com/8.x/guides/migrations/v8
- Examples: https://pixijs.com/8.x/examples
- Spine runtime (Pixi v8): https://github.com/EsotericSoftware/spine-runtimes/tree/4.2/spine-ts/spine-pixi-v8

### React 19

- Docs: https://react.dev
- `useSyncExternalStore`: https://react.dev/reference/react/useSyncExternalStore (Zustand bridge depends on this)
- React Compiler: https://react.dev/learn/react-compiler

### State / events / tween / audio

- Zustand: https://docs.pmnd.rs/zustand/getting-started/introduction
- Zustand vanilla: https://docs.pmnd.rs/zustand/recipes/recipes#using-zustand-without-react
- mitt: https://github.com/developit/mitt
- motion (formerly Framer Motion vanilla): https://motion.dev
- Howler.js: https://howlerjs.com
- Zod: https://zod.dev

### Build / test

- Vite library mode: https://vitejs.dev/guide/build.html#library-mode
- Vitest: https://vitest.dev
- `expectTypeOf`: https://vitest.dev/api/expect-typeof
- pnpm workspaces: https://pnpm.io/workspaces

### Type-system references

- TypeScript handbook (deep-link to advanced types): https://www.typescriptlang.org/docs/handbook/2/types-from-types.html
- Total TypeScript (advanced patterns): https://www.totaltypescript.com
- type-fest (utilities, idioms): https://github.com/sindresorhus/type-fest

### Game architecture (design comparison, not adoption)

- Phaser scene system: https://newdocs.phaser.io/docs/3.85.0/Phaser.Scenes.Scene (what we deliberately don't copy)
- ct.js: https://ctjs.rocks (small-engine inspiration)
- LittleJS: https://github.com/KilledByAPixel/LittleJS (factory-style API inspiration)
- Excalibur.js: https://excaliburjs.com (TS-first 2D engine — compare patterns)

### Asset tooling (out-of-band)

- TexturePacker: https://www.codeandweb.com/texturepacker
- free-tex-packer: https://free-tex-packer.com
- Spine editor: http://esotericsoftware.com/spine-in-depth
- DragonBones (free alternative): https://dragonbones.com

### Internal references (drafts in this repo)

- `references/scaling.ts` — letterbox/cover/extend math; will move to `engine-core/scaling`.
- `references/bridge/` — `RPC`, `Store` drafts; **will be refactored** away from `RegisteredRPC`/`RegisteredState` augmentation toward generic-passing.
- `references/react/` — `GameCanvas`, `OverlayLayer`, hooks; same refactor.
- `references/draft.md` — high-level engine design draft (precedes `architecture.md`).

### Framework docs (prefer context7 MCP if available)

When the `context7` MCP is loaded, query it for current docs of any library above before relying on training data — Pixi v8 in particular has frequent minor releases.

## Session handoff protocol

1. **Read** `docs/progression.md` (always) and the other three docs (if not recently visited this conversation).
2. **Brainstorm** — if the task is creative (new feature, new API, new system), invoke `superpowers:brainstorming` before any code.
3. **Plan** — if the task spans multiple files/packages, invoke `superpowers:writing-plans`.
4. **Pick the next task** from the "Next" section of `progression.md`. If unclear, pick from the current stage's roadmap exit criteria.
5. **Load the right skills** — `typescript-advanced-types` for any public type, `pixijs-*` for any Pixi work, `superpowers:test-driven-development` before implementation.
6. **Implement** — respect abstractions and stage boundaries.
7. **Verify** with Vitest (`pnpm vitest run`) and the running playground before marking anything done. Use `superpowers:verification-before-completion`.
8. **Update `progression.md`**: move task → Done, add handoff notes, log new blockers.
9. **Update `roadmap.md`**: tick exit-criteria checkboxes if a stage advanced.
10. **Commit** with a message referencing the stage/task: `stage-N: <task>`. Don't commit until the user asks.
