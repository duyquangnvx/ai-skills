# Hono Server Scaffolding — Standard Shape

Server-side quick reference for scaffolding Hono + Node API apps. **Source of truth: `docs/hono-project-shape.md`** (covers the full fullstack standard: monorepo layout, RPC client, web integration, deploy). When that doc exists in the repo, read it; this file summarizes the server-side rules so the shape stays consistent even in repos that only carry the skill.

The goal is that anyone switching between repos finds the same files, in the same places, with the same names. **Do not rename or reorganize — consistency across repos is the point, even where another layout would also work.**

## Canonical file tree

```
apps/api/src/
  index.ts                    # entry — the ONLY file with import-time side effects
  app.ts                      # createApiRoutes(deps) + createApp(deps), export AppType
  client.ts                   # RPC surface (type-only import from ./app)
  deps.ts                     # Deps interface + buildDeps(env) — the single DI seam
  config/
    env.ts                    # zod schema + loadEnv() — never parses at import time
  modules/
    health/
      health.routes.ts
    <resource>/               # one module per resource, always these 4 files
      <resource>.routes.ts    # create<Resource>Routes(<Resource>RouteDeps) — one chain
      <resource>.service.ts   # business logic, no hono imports, db as parameter
      <resource>.schema.ts    # zod schemas
      <resource>.test.ts      # tests via testClient + testDeps()
  db/
    index.ts                  # createDb(url) — factory, never a singleton instance
    schema/                   # drizzle tables
  middleware/
    request-logger.ts         # factories taking deps — never singletons
  lib/
    logger.ts                 # createLogger(level) — pino factory
    errors.ts                 # createOnError(logger), notFound, error envelope
    validate.ts               # validate() — zValidator wrapper, envelope-consistent 400
  testing/
    fixtures.ts               # testDeps() — shared by every test file
```

Fixed vocabulary:

| Name | Means | Never |
|------|-------|-------|
| `modules/<resource>/` | feature modules | `features/`, `routes/`, `controllers/`, global `services/` |
| `config/env.ts` | zod-validated env, exported as `loadEnv()` | parsing `process.env` at import time; Hono `Env`/`Variables` types |
| `deps.ts` | DI container | — |
| `lib/` | logger/errors/validate helpers | `http/`, `utils/`, `helpers/` |
| `testing/fixtures.ts` | shared `testDeps()` | inline `testDeps()` per test file |

## Invariants

1. **Every dependency flows through `Deps`.** `env`, `db`, `logger` are created in `buildDeps(env)` and injected — never module-level singletons, never `process.env` reads outside `config/env.ts`. (Singletons are what force `VITEST ? 'silent'` hacks and make tests crash on missing env vars.)
2. **`index.ts` is the only file with import-time side effects** (including `import 'dotenv/config'`). Every other file exports factories.
3. **Route modules are factories with narrow deps:** `create<Resource>Routes(deps: <Resource>RouteDeps)` declaring only what the module uses — never the whole `Deps` bag.
4. **Services take `db` (and friends) as parameters**, import nothing from `hono`, return plain data. Expected domain failures return values (null, discriminated union) — the handler maps them to status codes.
5. **Graceful shutdown** via `process.once("SIGINT"/"SIGTERM")`, closing the server then the db handle.

## RPC survival rules (violations silently break client types)

- **MUST** write each sub-app as **one chained expression** (`new Hono().get(...).post(...)`) and mount with chained `.route()` — splitting into statements loses the type.
- **MUST** use `c.json(data, status)` with an explicit status on **every** return.
- **NEVER** throw `HTTPException` for expected errors — `onError` responses are not part of `AppType`, so the client never sees that error branch. Return `c.json({ error: ... }, 4xx)` inline in the handler. Throwing is only for unexpected failures (bugs, lost DB).
- **NEVER** use `c.notFound()` / `c.body()` in API routes (untyped for RPC); avoid `c.text()` to keep the API uniformly JSON.
- `AppType = ReturnType<typeof createApiRoutes>`; `client.ts` may only `import type` from `./app` — a value import drags the server graph into the web bundle.

## Response contract

Success: bare payload with explicit status — `c.json({ posts }, 200)`, `c.json({ post }, 201)`. **No `{ success, data }` envelope** — with RPC, `res.ok` + `InferResponseType<..., 200>` is the discriminant; a success flag pollutes every inferred type.

Errors — one envelope everywhere:

```jsonc
{ "error": { "code": "UPPER_SNAKE", "message": "...", "details": /* optional */ } }
```

| Status | Meaning | Producer |
|--------|---------|----------|
| 400 | request shape invalid | `validate()` from `lib/validate.ts` (`code: "VALIDATION"`, zod issues in `details`) |
| 404 | resource not found | handler returns it inline (`code: "NOT_FOUND"`) — visible to RPC |
| 409/422 | domain rejection | handler inline, specific code (`EMAIL_TAKEN`, …) |
| 500 | unexpected error | `createOnError(logger)` — generic message, details only in logs, requestId correlated |

Never call `zValidator` directly — its default 400 has zod's own shape, not the envelope. Always use the `validate()` wrapper.

## Cross-domain features: process modules

A module is a **capability**, not a DB table. Logic spanning several resources (checkout, import pipeline) goes in a **process module** (`modules/checkout/`) alongside the resource modules — never inside one of them, never in a global `usecases/` layer. Files as needed: `.service.ts` (required — orchestration), `.schema.ts`, `.routes.ts`, `.jobs.ts`, `.test.ts`.

Dependency rules (CI-enforce with Biome `noImportCycles`):

- Cross-module calls happen **only service→service**. NEVER import another module's `*.routes.ts`; NEVER internal HTTP between modules.
- One direction: process module → resource module. Resource modules never import process modules.
- Two resources calling each other back and forth means they need a process module above them — or they're really one module.
- Cross-cutting **reads** may join tables directly in a service; **writes** go through the owning module's service.
- Job handlers only call their own module's service (+ injected infra); no logic in handlers.

Long-running work is modeled **run-as-resource**: `POST /api/<x>-runs` → `202 { id }`, `GET /:id` → `{ status, step, progress, result, error }` for polling (RPC-typed); the `<x>_runs` table belongs to the process module. Optional SSE route for realtime — streams are not RPC-typed, client uses `EventSource`.

### Cross-module transactions

Write functions in resource services take `DbConn` (not `Db`) as first param so a process service can enlist them in one transaction:

```ts
// db/index.ts additions — derived from the type, no instance needed
export type Tx = Parameters<Parameters<Db['transaction']>[0]>[0]
export type DbConn = Db | Tx
```

```ts
export async function checkout(deps: { db: Db }, input: CheckoutInput) {
  return deps.db.transaction(async (tx) => {
    const order = await orders.createOrder(tx, input.order)
    await inventory.reserveStock(tx, order.id, input.items)
    return order
  })
}
```

- The transaction boundary lives where the whole business operation is visible (the process service). Services receiving `conn` use it — they never open their own transaction.
- To abort with a typed business result: drizzle's `tx.rollback()` throws, so throw a sentinel class carrying the result and catch it right outside `db.transaction`; re-throw anything else.
- Non-atomic side effects (email, webhooks, external APIs) NEVER go inside the transaction — enqueue a job after commit.

### Background jobs

Default queue: **pg-boss** on the app's existing Postgres (BullMQ+Redis only if Redis already exists). Wrap as `lib/queue.ts` `createQueue(url)` and add `queue` to `Deps`.

- `<module>.jobs.ts`: job name constants (`'<module>.<action>'`) + handler **factories taking deps**; handlers only call services.
- `worker.ts`: `createWorker(deps)` registers every `*.jobs.ts` via `.work()`; exports `startWorker(deps)`/`stopWorker()`.
- `index.ts`: `await deps.queue.start()` in **every** role (the API enqueues too); only consumer registration is gated by `env.RUN_WORKER` (`z.stringbool().default(true)`). Shutdown order: `stopWorker()` → stop queue → close db. Scale by role with the same Docker image via env.
- Multi-step pipelines: one job per step; each step updates the `<x>_runs` row **in the same transaction as its work**, then enqueues the next step after commit. Steps must be idempotent so retries/redelivery are safe and the run resumes mid-pipeline.

## Key skeletons

### config/env.ts

```ts
import { z } from 'zod'

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  LOG_LEVEL: z
    .enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace', 'silent'])
    .default('info'),
  DATABASE_URL: z.url(),
})

export type Env = z.infer<typeof envSchema>

export function loadEnv(
  source: Record<string, string | undefined> = process.env,
): Env {
  const parsed = envSchema.safeParse(source)
  if (!parsed.success) {
    throw new Error(`Invalid environment: ${z.prettifyError(parsed.error)}`)
  }
  return parsed.data
}
```

(Boolean env vars: `z.stringbool()`, never `z.coerce.boolean()` — `"false"` coerces to `true`.)

### deps.ts

```ts
import type { Env } from './config/env'
import { createDb, type Db } from './db'
import { createLogger, type Logger } from './lib/logger'

export interface Deps {
  env: Env
  db: Db
  logger: Logger
}

export function buildDeps(env: Env): Deps {
  return {
    env,
    db: createDb(env.DATABASE_URL),
    logger: createLogger(env.LOG_LEVEL),
  }
}
```

### modules/posts/posts.routes.ts

```ts
import { Hono } from 'hono'
import type { Db } from '../../db'
import { validate } from '../../lib/validate'
import * as service from './posts.service'
import { createPostSchema, postIdParam } from './posts.schema'

export interface PostsRouteDeps {
  db: Db
}

export function createPostsRoutes(deps: PostsRouteDeps) {
  return new Hono()
    .get('/', async (c) => {
      const posts = await service.listPosts(deps.db)
      return c.json({ posts }, 200)
    })
    .post('/', validate('json', createPostSchema), async (c) => {
      const post = await service.createPost(deps.db, c.req.valid('json'))
      return c.json({ post }, 201)
    })
    .get('/:id', validate('param', postIdParam), async (c) => {
      const post = await service.getPost(deps.db, c.req.valid('param').id)
      if (!post) {
        return c.json({ error: { code: 'NOT_FOUND', message: 'Post not found' } }, 404)
      }
      return c.json({ post }, 200)
    })
}
```

Handlers do exactly three things: read validated input → call service → map to `c.json`. A handler over ~15 lines means logic belongs in the service.

### app.ts

```ts
import { Hono } from 'hono'
import { requestId } from 'hono/request-id'
import type { Deps } from './deps'
import { createOnError, notFound } from './lib/errors'
import { requestLogger } from './middleware/request-logger'
import { healthRoutes } from './modules/health/health.routes'
import { createPostsRoutes } from './modules/posts/posts.routes'

export function createApiRoutes(deps: Deps) {
  return new Hono()
    .basePath('/api')
    .route('/health', healthRoutes)
    .route('/posts', createPostsRoutes({ db: deps.db }))
}

export type AppType = ReturnType<typeof createApiRoutes>

export function createApp(deps: Deps) {
  const app = new Hono()
  app.use(requestId())
  app.use(requestLogger(deps.logger))
  app.onError(createOnError(deps.logger))
  app.notFound(notFound)
  app.route('/', createApiRoutes(deps))
  return app
}
```

`createApiRoutes` is separate so `AppType` contains only API routes and `testClient()` can consume it directly. Middleware/`onError`/`notFound` attach outside the chain and don't affect `AppType`. Adding a module = 1 import + 1 `.route()` line.

### lib/validate.ts

```ts
import { zValidator } from '@hono/zod-validator'
import type { ValidationTargets } from 'hono'
import type { ZodType } from 'zod'

export function validate<T extends keyof ValidationTargets, S extends ZodType>(
  target: T,
  schema: S,
) {
  return zValidator(target, schema, (result, c) => {
    if (!result.success) {
      return c.json(
        {
          error: {
            code: 'VALIDATION',
            message: `Invalid ${target}`,
            details: result.error.issues.map((i) => ({
              path: i.path.join('.'),
              message: i.message,
            })),
          },
        },
        400,
      )
    }
  })
}
```

### lib/errors.ts

```ts
import type { ErrorHandler, NotFoundHandler } from 'hono'
import { HTTPException } from 'hono/http-exception'
import type { RequestIdVariables } from 'hono/request-id'
import type { Logger } from './logger'

type AppEnv = { Variables: RequestIdVariables }

export function createOnError(logger: Logger): ErrorHandler<AppEnv> {
  return (err, c) => {
    if (err instanceof HTTPException) {
      return c.json({ error: { code: `HTTP_${err.status}`, message: err.message } }, err.status)
    }
    logger.error(
      { err, requestId: c.var.requestId, method: c.req.method, path: c.req.path },
      'unhandled error',
    )
    return c.json({ error: { code: 'INTERNAL', message: 'Internal Server Error' } }, 500)
  }
}

export const notFound: NotFoundHandler = (c) =>
  c.json({ error: { code: 'NOT_FOUND', message: 'Route not found' } }, 404)
```

### index.ts

```ts
import 'dotenv/config'
import { serve } from '@hono/node-server'
import { createApp } from './app'
import { loadEnv } from './config/env'
import { buildDeps } from './deps'

const env = loadEnv()
const deps = buildDeps(env)
const app = createApp(deps)

const server = serve({ fetch: app.fetch, port: env.PORT }, (info) => {
  deps.logger.info({ port: info.port }, 'api listening')
})

function shutdown() {
  server.close(async (err) => {
    if (err) {
      deps.logger.error({ err }, 'shutdown error')
      process.exit(1)
    }
    await deps.db.$client.end() // .close() for better-sqlite3
    process.exit(0)
  })
}
process.once('SIGTERM', shutdown)
process.once('SIGINT', shutdown)
```

### testing/fixtures.ts

```ts
import { loadEnv } from '../config/env'
import { createDb } from '../db'
import { createLogger } from '../lib/logger'
import type { Deps } from '../deps'

export function testDeps(overrides: Partial<Deps> = {}): Deps {
  const env = loadEnv({
    DATABASE_URL: process.env.TEST_DATABASE_URL ?? 'postgres://localhost:5432/app_test',
    LOG_LEVEL: 'silent',
  })
  return {
    env,
    db: createDb(env.DATABASE_URL),
    logger: createLogger('silent'),
    ...overrides,
  }
}
```

Tests go through `testClient(createApiRoutes(testDeps()))` — typed, no server, no env hacks. SQLite projects use `:memory:` + migrate here instead; the choice is a per-project variation recorded in its README, but always exposed as `testDeps()`.

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
