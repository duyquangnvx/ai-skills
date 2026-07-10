# Hono Module Skeletons

Copy-paste code templates for the standard shape. The rules behind them live in [project-standard.md](project-standard.md); cross-domain / jobs in [scaling-patterns.md](scaling-patterns.md); web + deploy in [fullstack-deploy.md](fullstack-deploy.md).

Adding a module = 1 import + 1 `.route()` line in `createApiRoutes`. A handler over ~15 lines means logic belongs in the service.

---

## config/env.ts

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

- This is the **only** file that knows `process.env`, and it only reads it when `index.ts` (or `testDeps()`) calls `loadEnv()` — **never parses at import time**. Import-time parsing crashes every test that transitively imports env when a var is missing, and is a side effect outside `index.ts`.
- `dotenv` loads in `index.ts` (`import 'dotenv/config'`), not here.
- On Node do not use `c.env` for secrets (that is a Workers pattern).
- Boolean env vars: `z.stringbool()`, never `z.coerce.boolean()` — `"false"` coerces to `true`.
- Adding an env var → update both `env.ts` and `.env.example` in the same commit.

---

## deps.ts — the single DI seam

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

---

## db/index.ts — Drizzle + Postgres (default)

- Schema in `src/db/schema/*.ts`, tables snake_case plural, re-exported from `src/db/schema/index.ts`.
- `src/db/index.ts` exports `createDb(url)` (a factory — **not** an instance) plus the `Db` and `DbConn` types (see [scaling-patterns.md](scaling-patterns.md) for `DbConn`). Close the connection on shutdown via `db.$client.end()` (pg Pool) / `db.$client.close()` (better-sqlite3).
- Migrations: `drizzle-kit generate` → commit the `drizzle/` dir; apply with `drizzle-kit migrate` in CI/CD before starting a new container.
- Variation point: SQLite for small tools; Kysely if the team prefers. Changing the ORM must not change the directory shape.

---

## lib/logger.ts

```ts
import { pino, type Logger } from 'pino'
import type { Env } from '../config/env'

export type { Logger }

export function createLogger(level: Env['LOG_LEVEL']): Logger {
  return pino({ level })
}
```

Use structured logging (pino), not `hono/logger` (console, unstructured).

---

## lib/errors.ts — one envelope

Every error returns `{ "error": { "code": "UPPER_SNAKE", "message": "...", "details?": ... } }`.

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

Division of labor: expected errors → `c.json(..., 4xx)` in the handler (RPC sees them); `onError` only catches unexpected errors (RPC does not — fine, the web checks `res.ok`). The 500 message is always generic — details live only in the log.

---

## lib/validate.ts — validation errors in the same envelope

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

Reason it exists: `zValidator`'s default 400 has Zod's own shape, not the app's error envelope. Always use this wrapper.

---

## middleware/request-logger.ts

```ts
import { createMiddleware } from 'hono/factory'
import type { RequestIdVariables } from 'hono/request-id'
import type { Logger } from '../lib/logger'

export function requestLogger(logger: Logger) {
  return createMiddleware<{ Variables: RequestIdVariables }>(async (c, next) => {
    const start = Date.now()
    await next()
    logger.info(
      {
        requestId: c.var.requestId,
        method: c.req.method,
        path: c.req.path,
        status: c.res.status,
        ms: Date.now() - start,
      },
      'request',
    )
  })
}
```

---

## app.ts — assembly

```ts
import { Hono } from 'hono'
import { requestId } from 'hono/request-id'
import type { Deps } from './deps'
import { createOnError, notFound } from './lib/errors'
import { requestLogger } from './middleware/request-logger'
import { healthRoutes } from './modules/health/health.routes'
import { createPostsRoutes } from './modules/posts/posts.routes'

// Chain mount — alphabetical by path for easy scanning.
// Separate from createApp so AppType contains only API routes and
// testClient() can consume it directly.
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

- Every endpoint sits under `/api` (basePath) — the condition for a clean SPA fallback.
- Add a module = exactly 2 lines: 1 import + 1 `.route()` in the chain.
- This file imports **no** Node API and reads **no** `process.env`.
- `onError`/`notFound`/middleware attach outside the chain, so they don't affect `AppType`.

---

## A resource module — modules/posts/

### posts.schema.ts

```ts
import { z } from 'zod'

export const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1),
})

export const postIdParam = z.object({ id: z.uuid() })

export type CreatePostInput = z.infer<typeof createPostSchema>
```

### posts.service.ts

```ts
// Imports NOTHING from 'hono'. The service does not know HTTP exists.
// db comes in as a parameter — no singleton import.
import type { Db } from '../../db'
import type { CreatePostInput } from './posts.schema'

export async function listPosts(db: Db) { /* ... */ }

export async function createPost(db: Db, input: CreatePostInput) { /* ... */ }

export async function getPost(db: Db, id: string) { /* returns null if missing */ }
```

- Services take/return plain data, never a `Context`, never a `Response`.
- `db` (and other deps if needed) is the first parameter — the service is testable with a test DB, no module mocking.
- Expected domain failures (not found, conflict…) → return a value (null, discriminated union), **never** throw; the handler decides the status code.

### posts.routes.ts

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
      const input = c.req.valid('json')
      const post = await service.createPost(deps.db, input)
      return c.json({ post }, 201)
    })
    .get('/:id', validate('param', postIdParam), async (c) => {
      const { id } = c.req.valid('param')
      const post = await service.getPost(deps.db, id)
      if (!post) {
        return c.json({ error: { code: 'NOT_FOUND', message: 'Post not found' } }, 404)
      }
      return c.json({ post }, 200)
    })
}
```

The handler does exactly three things: read validated input → call service → map to `c.json`. See the RPC survival rules in [project-standard.md](project-standard.md) — the MUST/NEVER here are what keep the client types alive.

### posts.test.ts

```ts
import { describe, it, expect } from 'vitest'
import { testClient } from 'hono/testing'
import { createApiRoutes } from '../../app'
import { testDeps } from '../../testing/fixtures'

describe('posts', () => {
  it('creates a post', async () => {
    const client = testClient(createApiRoutes(testDeps()))

    const res = await client.api.posts.$post({
      json: { title: 'Hello', body: 'World' },
    })

    expect(res.status).toBe(201)
  })
})
```

- Test routes through `testClient` (typed) or `app.request()` — no server needed.
- `testDeps()` is imported from `testing/fixtures.ts` — **never** defined inline in the test file.
- Complex logic: unit-test the service directly with a test DB (fast, no HTTP).
- Test DB source is a per-project variation point (SQLite → `:memory:`; Postgres → testcontainers or `TEST_DATABASE_URL`) — record the choice in the README, but always expose it through `testDeps()`.

---

## testing/fixtures.ts

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

The silent logger is injected — no `VITEST ? 'silent'` hack, no env set in the vitest config. SQLite projects use `:memory:` + migrate here instead; the choice is a per-project variation recorded in its README, but always exposed as `testDeps()`.

---

## index.ts — Node entry (base, server-only)

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

For serving the SPA from this same entry (fullstack), see the `SERVE_WEB` block in [fullstack-deploy.md](fullstack-deploy.md).
