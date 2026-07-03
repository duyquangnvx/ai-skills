# Hono Project Standard — Structure & Rules

> **Scope:** Fullstack app = Hono API (Node.js, deployed as a container/VPS) + SPA frontend (TypeScript), talking over Hono RPC. A server-only API is the same thing minus the web/deploy parts.
> **How to use:** This is the source of truth when scaffolding a new project and when adding code to an existing one. Read it before writing code.
> **Conflict order:** a project's own README overrides > this document > personal habit.
> **Ecosystem status (2026-07):** Hono v4.12.x, Zod v4. HonoX is still alpha — not the standard.

The point of this standard is that anyone switching between repos finds the same files, in the same places, with the same names. **Do not rename or reorganize — cross-repo consistency is the goal, even where another layout would also work.**

Related references: code templates live in [module-skeletons.md](module-skeletons.md); cross-domain / jobs / scaling in [scaling-patterns.md](scaling-patterns.md); web + deploy in [fullstack-deploy.md](fullstack-deploy.md).

---

## Principles

1. **Feature modules, not global layers.** Group code by feature (`modules/posts/`), not by tier (global `controllers/`, `services/`). Reason: switching projects / onboarding only requires understanding one module to understand the app.
2. **Handlers inline, logic in services.** Write handlers inline right after the path (Hono only infers path-param types when inline — this is the official best practice). Business logic lives in the service so tests need no HTTP.
3. **Type-safe end-to-end via RPC, no codegen.** The frontend calls the API through `hc<AppType>`. Never hand-write request/response types on the web side.
4. **Every dependency flows through `Deps`.** `env`, `db`, `logger` are created in `buildDeps()` and injected — **never** module-level singletons, and `process.env` is never read outside `config/env.ts`. This is what lets `testDeps()` swap in a test DB / silent logger without env hacks.
5. **`index.ts` is the only file with import-time side effects.** Every other file exports a factory / pure function. `app.ts` imports nothing from Node; only `index.ts` knows about `@hono/node-server`, dotenv, static files, signals. Changing runtime = changing one file.
6. **Fail fast, one error shape.** Env is validated with Zod at boot. Every error response uses one envelope: `{ error: { code, message, details? } }`.
7. **Simple first, escape hatches ready.** The standard optimizes for small–medium projects; the escape-hatch list in [scaling-patterns.md](scaling-patterns.md) prescribes how to grow so projects stay uniform when they scale.

---

## File trees

### Monorepo (fullstack)

```
my-project/
├── apps/
│   ├── api/                  # Hono backend (see apps/api tree below)
│   └── web/                  # SPA — Vite + framework of choice (variation point)
│       ├── src/
│       │   └── lib/api.ts    # the ONLY place the RPC client is created
│       └── vite.config.ts    # proxy /api → api dev server
├── packages/
│   └── shared/               # (optional) shared runtime code — see fullstack-deploy.md
├── pnpm-workspace.yaml       # workspaces + catalog (pin shared versions)
├── tsconfig.base.json        # strict: true — required for RPC
├── biome.json                # lint + format (variation: ESLint/Prettier)
├── Dockerfile
├── .env.example              # every env var listed, including optional
├── CLAUDE.md                 # points to this standard + project-specific notes
└── README.md
```

A server-only project keeps just `apps/api` (or the api tree at the repo root) and skips `apps/web`, `packages/shared`, and the monorepo wiring.

### apps/api

```
apps/api/
├── src/
│   ├── index.ts              # Node entry: dotenv, loadEnv, buildDeps, serve, static SPA, graceful shutdown
│   ├── app.ts                # createApiRoutes(deps) + createApp(deps), export AppType
│   ├── client.ts             # RPC surface for the web to import
│   ├── worker.ts             # (optional) createWorker(deps) — registers + runs background jobs
│   ├── deps.ts               # Deps interface + buildDeps(env) — the single DI seam
│   ├── config/
│   │   └── env.ts            # Zod schema + loadEnv() — never parses at import time
│   ├── modules/
│   │   ├── health/
│   │   │   └── health.routes.ts
│   │   ├── posts/            # sample resource module (4 files, always these)
│   │   │   ├── posts.routes.ts
│   │   │   ├── posts.service.ts
│   │   │   ├── posts.schema.ts
│   │   │   └── posts.test.ts
│   │   └── checkout/         # process module: cuts across resources
│   │       ├── checkout.routes.ts
│   │       ├── checkout.service.ts   # orchestrates — calls other modules' services
│   │       └── checkout.jobs.ts      # (optional) background steps
│   ├── db/
│   │   ├── index.ts          # createDb(url) — factory, never a singleton; types Db/DbConn
│   │   └── schema/           # Drizzle table schemas, one file per table group
│   ├── middleware/           # cross-cutting middleware, factories taking deps
│   │   └── request-logger.ts
│   ├── lib/
│   │   ├── logger.ts         # createLogger(level) — pino factory
│   │   ├── errors.ts         # createOnError(logger), notFound, error envelope
│   │   ├── validate.ts       # validate() — zValidator wrapper, envelope-consistent 400
│   │   └── queue.ts          # (optional) createQueue(url) — pg-boss factory
│   └── testing/
│       └── fixtures.ts       # testDeps() — fixture shared by every test
├── drizzle/                  # migrations (drizzle-kit generate)
├── drizzle.config.ts
├── tsconfig.json             # extends base
├── tsconfig.build.json       # prod build (emit dist/)
└── package.json
```

Each file's role is fixed — **do not** add global `controllers/`, `repositories/`, `dto/` directories. If a module needs an extra file (e.g. `posts.mapper.ts`), put it inside that module.

### Fixed vocabulary

| Name | Means | Never |
|------|-------|-------|
| `modules/<resource>/` | feature modules | `features/`, `routes/`, `controllers/`, global `services/` |
| `config/env.ts` | zod-validated env, exported as `loadEnv()` | parsing `process.env` at import time; Hono `Env`/`Variables` types |
| `deps.ts` | DI container | — |
| `lib/` | logger/errors/validate helpers | `http/`, `utils/`, `helpers/` |
| `testing/fixtures.ts` | shared `testDeps()` | inline `testDeps()` per test file |

---

## Invariants

1. **Every dependency flows through `Deps`.** `env`, `db`, `logger` are created in `buildDeps(env)` and injected — never module-level singletons, never `process.env` reads outside `config/env.ts`. (Singletons are what force `VITEST ? 'silent'` hacks and make tests crash on missing env vars.)
2. **`index.ts` is the only file with import-time side effects** (including `import 'dotenv/config'`). Every other file exports factories.
3. **Route modules are factories with narrow deps:** `create<Resource>Routes(deps: <Resource>RouteDeps)` declaring only what the module uses — never the whole `Deps` bag.
4. **Services take `db` (and friends) as parameters**, import nothing from `hono`, return plain data. Expected domain failures return values (null, discriminated union) — the handler maps them to status codes.
5. **Graceful shutdown** via `process.once("SIGINT"/"SIGTERM")`, closing the server then the db handle. `process.once`, not `process.on` — a second signal must not re-enter shutdown.

---

## RPC survival rules

Violating any of these silently breaks the client types (web types become `unknown`, or an error branch disappears):

- **MUST** write each sub-app as **one chained expression** (`new Hono().get(...).post(...)`) and mount it with a chained `.route()` — splitting into separate statements loses the type.
- **MUST** use `c.json(data, status)` with an explicit status on **every** return — status codes are part of RPC inference.
- **MUST** export the factory `create<Module>Routes(deps)` with a **narrow deps interface** (`PostsRouteDeps`) — declaring only what the module uses, not the whole `Deps` bag.
- **NEVER** throw `HTTPException` for expected errors (404, conflict) — `onError` responses are not part of `AppType`, so the client never sees that branch. Return `c.json({ error: ... }, 4xx)` inline in the handler. Throwing is only for unexpected failures (bugs, lost DB).
- **NEVER** use `c.notFound()` / `c.body()` in API routes (untyped for RPC); avoid `c.text()` too — `hc` can infer it, but it breaks the API's uniform JSON.
- `AppType = ReturnType<typeof createApiRoutes>`; `client.ts` may only `import type` from `./app` — a value import drags the whole server graph into the web bundle.

Validate every input through `validate()` from `lib/validate.ts` (`json`, `param`, `query`) — chain multiple validators when needed. Never call `zValidator` directly: its default 400 does not use the app's error envelope.

---

## Response contract

**Success:** bare payload with an explicit status — `c.json({ posts }, 200)`, `c.json({ post }, 201)`. **No `{ success, data }` envelope** — with RPC, `res.ok` + `InferResponseType<..., 200>` is the discriminant; a success flag pollutes every inferred type. (This is a deliberate exception to the generic REST API-envelope rule, which applies to untyped REST.)

**Errors — one envelope everywhere:**

```jsonc
{ "error": { "code": "UPPER_SNAKE", "message": "...", "details": /* optional */ } }
```

| Status | Meaning | Producer |
|--------|---------|----------|
| 400 | request shape invalid | `validate()` from `lib/validate.ts` (`code: "VALIDATION"`, zod issues in `details`) |
| 404 | resource not found | handler returns it inline (`code: "NOT_FOUND"`) — visible to RPC |
| 409/422 | domain rejection | handler inline, specific code (`EMAIL_TAKEN`, …) |
| 500 | unexpected error | `createOnError(logger)` — generic message, details only in logs, requestId correlated |

Expected errors → `c.json(..., 4xx)` in the handler (RPC sees them). `onError` only catches unexpected errors (RPC does not see them — acceptable, the web handles them via `res.ok`). A 500 message is always generic; details live only in the log.

---

## Naming — quick table

| Object | Convention | Example |
|---|---|---|
| Module directory | kebab-case, plural noun of the resource | `modules/order-items/` |
| File within a module | `<module>.<role>.ts` | `posts.routes.ts`, `posts.service.ts` |
| URL path | kebab-case, plural, no version | `/api/order-items/:id` |
| Sub-app export | factory `create<Module>Routes` + `<Module>RouteDeps` | `createPostsRoutes(deps: PostsRouteDeps)` |
| DB table | snake_case plural | `order_items` |
| Env var | UPPER_SNAKE | `DATABASE_URL` |
| Error code | UPPER_SNAKE | `NOT_FOUND`, `EMAIL_TAKEN`, `VALIDATION` |
| Process module | process noun, kebab-case | `modules/checkout/`, `modules/import-pipeline/` |
| Job name | `<module>.<action>`, kebab-case | `import.process-file` |

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Throwing `HTTPException` for expected errors (404, conflict) | Return `c.json({ error: ... }, 4xx)` inline — `onError` responses are invisible to RPC |
| `{ success: true, data }` envelope | Bare payload + explicit status; error envelope only for failures |
| `envSchema.parse(process.env)` at module top level | Export `loadEnv()`; only `index.ts`/`testDeps()` call it |
| Module-level `db`/`logger`/`env` singletons | Factories, wired in `buildDeps`, injected via `Deps` |
| Route factory taking the whole `Deps` | Declare `<Resource>RouteDeps` with only what the module uses |
| Raw `zValidator` (zod-shaped 400) | `validate()` from `lib/validate.ts` |
| Splitting a sub-app into separate `app.get(...)` statements | One chained expression — statements lose `AppType` |
| `c.json(data)` without status | Always `c.json(data, status)` — status types are part of RPC inference |
| `features/`, `routes/`, `controllers/` directories | `modules/<resource>/` — fixed vocabulary above |
| `process.on` for shutdown signals | `process.once` — a second signal must not re-enter shutdown |
| `z.coerce.boolean()` for env flags | `z.stringbool()` — `"false"` coerces to `true` |
| Cross-resource orchestration inside a resource module or a global `usecases/` layer | Process module (`modules/checkout/`) calling other modules' services |
| Importing another module's `*.routes.ts` or internal HTTP between modules | Service→service imports only, process→resource direction |
| Email/webhook/external API call inside a transaction | Enqueue a job after commit |
| Long pipeline as one giant job or one blocking request | Run-as-resource: `_runs` table + one idempotent job per step |

---

## Checklists

### Scaffold a new project

1. Copy the template repo (or build the tree above) — keep the standard file/dir names.
2. Name packages `@repo/api`, `@repo/web` (the `@repo` scope is fixed across all projects for uniform import paths).
3. Fill `.env.example` → `.env`; run `pnpm dev`; confirm `GET /api/health` returns 200 through the web proxy.
4. Edit `CLAUDE.md`: point to this standard + record the variation points chosen (DB, auth, logger).

### Add a new module (the most repeated task — do it in this order)

1. Create `src/modules/<name>/` with the 4 files: `.schema.ts` → `.service.ts` (db as a parameter) → `.routes.ts` (factory + narrow deps, one chain) → `.test.ts` (uses `testDeps()`). Skeletons in [module-skeletons.md](module-skeletons.md).
2. New table needed: add `db/schema/<name>.ts`, run `drizzle-kit generate`, commit the migration.
3. Mount into the chain in `createApiRoutes` (1 import + 1 `.route()`).
4. Run `pnpm typecheck && pnpm test` — green typecheck means the web's RPC types already updated.

For a **process module**: same as above but files as needed (`.routes.ts` only when there is an endpoint, add `.jobs.ts` when there is a background step); orchestrate through other modules' services and follow the dependency rules in [scaling-patterns.md](scaling-patterns.md); resource-service write functions take `DbConn` to enlist in a transaction; model long-running work as run-as-resource.

---

## Working with a coding agent

- Put this standard (or a symlink/excerpt) as the root `CLAUDE.md` of each project. Assign work like: *"Add an `invoices` module following the standard shape, fields: …"* — the add-module checklist is the process the agent must follow.
- Agent verification = `pnpm typecheck && pnpm test` (no need to eyeball RPC compliance — typecheck catches chain/status violations).
- Do not use a rigid code generator (plop/hygen) to scaffold modules — the convention doc + agent + typecheck replace it and need no template maintenance.

*Update this standard when the ecosystem changes (new Hono major, HonoX stable, new Zod major). Every project points to the same copy — fix it once, apply everywhere.*
