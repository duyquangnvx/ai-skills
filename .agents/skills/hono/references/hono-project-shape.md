# Hono Project Shape — Reference chuẩn

> **Phạm vi:** Fullstack app = Hono API (Node.js, deploy container/VPS) + SPA frontend (TypeScript), giao tiếp qua Hono RPC.
> **Cách dùng:** Đây là tài liệu nguồn khi scaffold project mới và khi thêm code vào project hiện có. Người mới và coding agent (Claude Code) đọc file này trước khi viết code.
> **Thứ tự ưu tiên khi mâu thuẫn:** ghi chú override trong README của từng project > file này > thói quen cá nhân.
> **Trạng thái ecosystem lúc viết (07/2026):** Hono v4.12.x, Zod v4. HonoX còn alpha — không dùng làm chuẩn.

---

## 1. Nguyên tắc

1. **Feature module, không layer toàn cục.** Code nhóm theo tính năng (`modules/posts/`), không nhóm theo tầng (`controllers/`, `services/` toàn cục). Lý do: switch project / onboard chỉ cần hiểu 1 module là hiểu cả app.
2. **Handler inline, logic trong service.** Handler viết inline ngay sau path (Hono chỉ suy được type của path param khi inline — đây là best practice chính thức). Business logic nằm ở service để test không cần HTTP.
3. **Type-safe end-to-end bằng RPC, không codegen.** Frontend gọi API qua `hc<AppType>`. Không viết type request/response thủ công ở web.
4. **Mọi dependency đi qua `Deps`.** `env`, `db`, `logger` được tạo trong `buildDeps()` và inject xuống — **không bao giờ** là module singleton, không đọc `process.env` ngoài `config/env.ts`. Đây là điều kiện để `testDeps()` hoạt động (cắm DB test, logger silent) mà không cần hack biến môi trường.
5. **`index.ts` là file duy nhất có side effect lúc import.** Mọi file khác export factory/hàm thuần. `app.ts` không import gì của Node; chỉ `index.ts` biết đến `@hono/node-server`, dotenv, static files, signals. Đổi runtime = đổi 1 file.
6. **Fail fast, một kiểu lỗi.** Env validate bằng Zod lúc boot. Mọi response lỗi cùng một envelope `{ error: { code, message, details? } }`.
7. **Đơn giản trước, escape hatch có sẵn.** Chuẩn tối ưu cho project nhỏ–vừa; mục "Escape hatches" quy định sẵn cách nâng cấp khi app lớn, để các project vẫn đồng dạng khi scale.

---

## 2. Cây thư mục monorepo

```
my-project/
├── apps/
│   ├── api/                  # Hono backend (xem mục 3)
│   └── web/                  # SPA — Vite + framework tuỳ chọn (variation point)
│       ├── src/
│       │   └── lib/api.ts    # nơi DUY NHẤT tạo RPC client
│       └── vite.config.ts    # proxy /api → api dev server
├── packages/
│   └── shared/               # (optional) code dùng chung — xem quy tắc mục 8
├── pnpm-workspace.yaml       # workspaces + catalog (pin version chung)
├── tsconfig.base.json        # strict: true — bắt buộc cho RPC
├── biome.json                # lint + format (variation: ESLint/Prettier)
├── Dockerfile
├── .env.example              # liệt kê đủ mọi biến env, kể cả optional
├── CLAUDE.md                 # trỏ về file này + ghi chú riêng của project
└── README.md
```

**Quy tắc version (MUST):** `hono` và `zod` khai báo qua pnpm catalog để api và web luôn cùng version — lệch version `hono` giữa hai bên làm hỏng type inference của RPC một cách khó hiểu.

```yaml
# pnpm-workspace.yaml
packages:
  - apps/*
  - packages/*
catalog:
  hono: ^4.12.0
  zod: ^4.0.0
```

```jsonc
// trong package.json của apps/api và apps/web
"dependencies": { "hono": "catalog:", "zod": "catalog:" }
```

---

## 3. Shape của `apps/api`

```
apps/api/
├── src/
│   ├── index.ts              # entry Node: dotenv, loadEnv, buildDeps, serve, static SPA, graceful shutdown
│   ├── app.ts                # createApiRoutes(deps) + createApp(deps), export AppType
│   ├── client.ts             # RPC surface cho web import
│   ├── worker.ts             # (optional) createWorker(deps) — đăng ký + chạy background jobs (mục 4.8)
│   ├── deps.ts               # Deps interface + buildDeps(env) — seam DI duy nhất
│   ├── config/
│   │   └── env.ts            # Zod schema + loadEnv() — KHÔNG parse lúc import
│   ├── modules/
│   │   ├── health/
│   │   │   └── health.routes.ts
│   │   ├── posts/            # resource module mẫu (mục 4.1–4.4)
│   │   │   ├── posts.routes.ts
│   │   │   ├── posts.service.ts
│   │   │   ├── posts.schema.ts
│   │   │   └── posts.test.ts
│   │   └── checkout/         # process module: cắt ngang nhiều resource (mục 4.6)
│   │       ├── checkout.routes.ts
│   │       ├── checkout.service.ts   # orchestrate — gọi service của module khác
│   │       └── checkout.jobs.ts      # (optional) bước chạy nền (mục 4.8)
│   ├── db/
│   │   ├── index.ts          # createDb(url) — factory, không singleton; type Db/DbConn (mục 4.7)
│   │   └── schema/           # Drizzle table schemas, 1 file / nhóm bảng
│   ├── middleware/           # middleware cross-cutting, dạng factory nhận deps
│   │   └── request-logger.ts
│   ├── lib/
│   │   ├── logger.ts         # createLogger(level) — pino factory
│   │   ├── errors.ts         # createOnError(logger), notFound, error envelope
│   │   ├── validate.ts       # validate() — zValidator wrapper trả lỗi cùng envelope
│   │   └── queue.ts          # (optional) createQueue(url) — pg-boss factory (mục 4.8)
│   └── testing/
│       └── fixtures.ts       # testDeps() — fixture dùng chung cho mọi test
├── drizzle/                  # migrations (drizzle-kit generate)
├── drizzle.config.ts
├── tsconfig.json             # extends base
├── tsconfig.build.json       # cho prod build (emit dist/)
└── package.json
```

Vai trò từng file cố định — **không** thêm thư mục `controllers/`, `repositories/`, `dto/` toàn cục. Nếu một module cần file phụ (vd `posts.mapper.ts`), đặt trong chính module đó.

### 3.1 `deps.ts` — seam DI duy nhất

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

## 4. Module: quy tắc viết (phần quan trọng nhất)

Một module = một **capability**, không phải một bảng DB. Dạng phổ biến nhất là **resource module** — sở hữu một resource và các bảng của nó, gồm 4 file như ví dụ dưới (4.1–4.4). Chức năng cắt ngang nhiều resource (checkout, pipeline, workflow) là **process module** — xem 4.6, dùng chung quy ước file nhưng vai trò là orchestration. Ví dụ resource module đầy đủ:

### 4.1 `posts.schema.ts` — Zod schemas

```ts
import { z } from 'zod'

export const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1),
})

export const postIdParam = z.object({ id: z.uuid() })

export type CreatePostInput = z.infer<typeof createPostSchema>
```

### 4.2 `posts.service.ts` — business logic

```ts
// KHÔNG import gì từ 'hono'. Service không biết HTTP tồn tại.
// Db nhận qua tham số — không import singleton.
import type { Db } from '../../db'
import type { CreatePostInput } from './posts.schema'

export async function listPosts(db: Db) { /* ... */ }

export async function createPost(db: Db, input: CreatePostInput) { /* ... */ }

export async function getPost(db: Db, id: string) { /* trả null nếu không có */ }
```

- Service nhận/trả plain data, không nhận `Context`, không trả `Response`.
- `db` (và dependency khác nếu cần) là tham số đầu tiên — service test được với DB test mà không cần mock module.
- Lỗi nghiệp vụ dự đoán được (not found, conflict…) → trả về giá trị (null, discriminated union), **không** throw; handler quyết định status code.

### 4.3 `posts.routes.ts` — Hono sub-app

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

Quy tắc route (các quy tắc MUST/NEVER ở đây là điều kiện sống còn của RPC — vi phạm sẽ làm type ở web thành `unknown` hoặc mất nhánh lỗi một cách âm thầm):

- **MUST** export dạng factory `create<Module>Routes(deps)` với **deps interface hẹp riêng** (`PostsRouteDeps`) — chỉ khai báo đúng thứ module dùng, không nhận cả bag `Deps`.
- **MUST** viết cả sub-app thành **một biểu thức chain duy nhất** (`new Hono().get(...).post(...)`). Tách rời `app.get(...)` từng dòng sẽ mất type.
- **MUST** dùng `c.json(data, status)` với status code tường minh ở **mọi** return.
- **NEVER** dùng `c.notFound()`, `c.body()` trong API routes (RPC không suy được type từ chúng); tránh cả `c.text()` — hc suy được nhưng phá tính đồng nhất JSON của API.
- **NEVER** throw `HTTPException` cho lỗi dự đoán được — response từ `onError` không nằm trong `AppType`, web sẽ không thấy nhánh lỗi đó. Throw chỉ dành cho lỗi bất ngờ (bug, mất DB).
- Handler chỉ làm 3 việc: đọc input đã validate → gọi service → map kết quả sang `c.json`. Handler > ~15 dòng là dấu hiệu logic cần chuyển xuống service.
- Validate mọi input bằng `validate()` từ `lib/validate.ts` (`json`, `param`, `query`) — chain nhiều validator khi cần. Không gọi `zValidator` trực tiếp: lỗi 400 mặc định của nó không cùng envelope.

### 4.4 `posts.test.ts` — test cạnh code

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

- Test route qua `testClient` (typed) hoặc `app.request()` — không cần chạy server.
- `testDeps()` import từ `testing/fixtures.ts` — **không** định nghĩa inline trong file test.
- Logic phức tạp: unit test thẳng vào service với DB test (nhanh, không HTTP).
- Nguồn DB test: variation point per project (SQLite → `:memory:`; Postgres → testcontainers hoặc `TEST_DATABASE_URL`) — ghi lựa chọn vào README, nhưng luôn expose qua `testDeps()`.

### 4.5 `testing/fixtures.ts`

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

Logger silent được inject — không cần hack `VITEST ? 'silent'` hay set env trong vitest config.

---

### 4.6 Chức năng đa domain: process module

Khi một nghiệp vụ chạm nhiều resource (checkout đụng orders + inventory + payments; import-pipeline đụng files + products + logs), **không** nhét orchestration vào một resource module và cũng **không** tạo tầng `usecases/` toàn cục — tạo một **process module** đứng ngang hàng: `modules/checkout/`, `modules/import-pipeline/`.

- Process module *không sở hữu* resource của module khác; nó orchestrate qua service của chúng. Nó *được* sở hữu bảng state riêng của quy trình (vd `import_runs`).
- Thành phần file theo nhu cầu: `.service.ts` (bắt buộc — orchestration ở đây, nhận deps như mọi service), `.schema.ts`, `.routes.ts` (khi có endpoint — vẫn factory + deps hẹp như 4.3), `.jobs.ts` (khi có bước chạy nền), `.test.ts`.

**Quy tắc phụ thuộc** (chống spaghetti — vi phạm ở đây là thứ làm codebase đa domain mục nát):

1. Cross-module **chỉ ở tầng service**: service gọi service. **NEVER** import `*.routes.ts` của module khác, **NEVER** gọi HTTP nội bộ giữa các module.
2. Chiều phụ thuộc một chiều: process module → resource module. Resource module **NEVER** import process module.
3. Resource ↔ resource: hạn chế. Hai resource cứ phải gọi nhau qua lại là dấu hiệu cần một process module đứng trên, hoặc chúng thực ra là một module.
4. Jobs handler chỉ gọi service của chính module nó (+ infra được inject như mailer) — không chứa logic.
5. Cấm vòng import — bật rule `noImportCycles` của Biome (thuộc project domain, không nằm trong recommended nên phải bật thủ công) để CI bắt thay vì dựa vào kỷ luật.

**Reads cắt ngang** (dashboard, report): service được phép join thẳng nhiều bảng qua Drizzle — coupling ở tầng *đọc* chấp nhận được trong modular monolith, đổi lấy sự đơn giản. **Writes** thì bắt buộc đi qua service của module sở hữu bảng. Tradeoff cần biết: nếu sau này tách service, các read-join này là chỗ phải gỡ đầu tiên.

**Routes của process module** — hai pattern, chọn theo thời gian chạy:

- Xong trong một request: endpoint hành động, vd `POST /api/checkout`. Vẫn chain, vẫn RPC như mọi route khác; kết quả nghiệp vụ (discriminated union từ service) map sang status tường minh — `201` / `409 OUT_OF_STOCK` / `402 PAYMENT_DECLINED`…
- Chạy lâu / nhiều bước: **model "run" như một resource**. `POST /api/import-runs` tạo run, trả `202` + `{ id }`; `GET /api/import-runs/:id` trả `{ status, step, progress, result, error }` để poll (RPC-typed). Bảng `import_runs` thuộc module này. Ưu điểm: pipeline khớp 100% shape sẵn có (module + bảng + routes + RPC), retry/resume/poll tự nhiên. Cần realtime thì thêm route SSE (`streamSSE`) — lưu ý response dạng stream không được RPC suy type, client đọc bằng `EventSource`.

### 4.7 Transaction xuyên module

Để process service compose được nhiều resource service trong **một** transaction, mọi service function **ghi DB** nhận `DbConn` (thay vì `Db`) làm tham số đầu:

```ts
// db/index.ts — bổ sung (derive từ type, không cần instance)
export type Tx = Parameters<Parameters<Db['transaction']>[0]>[0]
export type DbConn = Db | Tx
```

```ts
// resource service — chữ ký chuẩn cho hàm ghi
export async function createOrder(conn: DbConn, input: CreateOrderInput) { /* ... */ }
```

```ts
// process service sở hữu transaction boundary
import * as orders from '../orders/orders.service'
import * as inventory from '../inventory/inventory.service'

export async function checkout(deps: { db: Db }, input: CheckoutInput) {
  return deps.db.transaction(async (tx) => {
    const order = await orders.createOrder(tx, input.order)
    await inventory.reserveStock(tx, order.id, input.items)
    return order
  })
}
```

- Transaction mở ở tầng nhìn thấy toàn bộ nghiệp vụ (process service, hoặc handler của resource module khi chỉ một domain). Service nhận `conn` thì dùng `conn`, không tự mở transaction mới.
- **Abort có lý do typed:** `tx.rollback()` của Drizzle throw — `return` sau nó không thoát ra ngoài được. Muốn hủy transaction và mang kết quả nghiệp vụ ra ngoài (vd `{ status: 'out_of_stock' }`), throw một sentinel class chứa result rồi catch ngay bên ngoài `db.transaction`; lỗi không phải sentinel thì re-throw cho `onError`.
- Side-effect không cần atomic (gửi email, gọi webhook, gọi API ngoài) **NEVER** đặt trong transaction — enqueue job (4.8) **sau khi** commit.

### 4.8 Bước chạy nền & pipeline dài

Default: **pg-boss** — job queue chạy trên chính Postgres của app: không thêm hạ tầng mới, có sẵn retry/backoff/cron. (Variation: BullMQ nếu hạ tầng đã có Redis.) Wrap thành factory `lib/queue.ts` (`createQueue(env.DATABASE_URL)`) và thêm `queue` vào `Deps` — như mọi dependency khác.

- `<module>.jobs.ts`: export tên job (hằng, dạng `'<module>.<action>'`) + handler **factory nhận deps** — handler chỉ gọi service, không chứa logic.
- `src/worker.ts`: `createWorker(deps)` import mọi `*.jobs.ts`, đăng ký `.work()` với pg-boss, export `startWorker(deps)` / `stopWorker()`.
- `index.ts`: `await deps.queue.start()` ở **mọi** role — process API cũng enqueue nên cũng cần start; chỉ việc đăng ký consumer (`startWorker`) mới gate bằng `if (env.RUN_WORKER)`. Shutdown theo thứ tự: `stopWorker()` → stop queue → đóng db. Thêm `RUN_WORKER: z.stringbool().default(true)` vào `env.ts` khi bắt đầu dùng jobs.
- Scale: cùng một Docker image, tách vai trò bằng env — container A `SERVE_WEB=true RUN_WORKER=false`, container B ngược lại. Không cần entry hay image mới.
- Pipeline nhiều bước: mỗi step một job; step nào xong thì cập nhật bảng `<x>_runs` (status/step/progress) **trong cùng transaction với công việc của step**, rồi enqueue step kế sau commit. Fail ở step nào retry đúng step đó (step phải idempotent — redelivery an toàn), resume được từ giữa chừng.
- Pipeline LLM/agent dùng đúng shape này: mỗi bước gọi model là một job có retry riêng, state nằm trong bảng runs (resume khi một call fail), progress trả về UI qua poll hoặc SSE.

---

## 5. `app.ts` — lắp ráp

```ts
import { Hono } from 'hono'
import { requestId } from 'hono/request-id'
import type { Deps } from './deps'
import { createOnError, notFound } from './lib/errors'
import { requestLogger } from './middleware/request-logger'
import { healthRoutes } from './modules/health/health.routes'
import { createPostsRoutes } from './modules/posts/posts.routes'

// Chain mount — thứ tự alphabet theo path cho dễ scan.
// Tách riêng khỏi createApp để AppType chỉ chứa API routes và
// testClient() dùng được trực tiếp.
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

- Mọi endpoint nằm dưới `/api` (basePath) — điều kiện để SPA fallback hoạt động sạch.
- Thêm module mới = thêm đúng 2 dòng: 1 import + 1 `.route()` trong chain.
- File này **không** import Node API, không đọc `process.env`.
- `onError`/`notFound`/middleware gắn ngoài chain nên không ảnh hưởng `AppType`.

## 6. `client.ts` — RPC surface

```ts
import { hc } from 'hono/client'
import type { AppType } from './app'

export type { AppType }
export type ApiClient = ReturnType<typeof hc<AppType>>
export const hcWithType = (...args: Parameters<typeof hc>): ApiClient =>
  hc<AppType>(...args)
```

**MUST:** trong `client.ts` chỉ được `import type` từ `./app` — đổi thành value import sẽ kéo toàn bộ server graph (db driver, env) vào bundle của web. Runtime import duy nhất cho phép ở file này là `hono/client`. (`AppType = ReturnType<typeof createApiRoutes>` vẫn là type thuần — import type không kéo runtime.)

`apps/api/package.json` export TS source trực tiếp (pattern "internal package" — bundler của web tự compile):

```jsonc
{
  "name": "@repo/api",
  "exports": { "./client": "./src/client.ts" }
}
```

Phía web — tạo client ở **một chỗ duy nhất**:

```ts
// apps/web/src/lib/api.ts
import { hcWithType } from '@repo/api/client'
export const api = hcWithType('/')   // same-origin: dev qua Vite proxy, prod cùng server

// Lấy type response khi cần truyền xuống component:
import type { InferResponseType } from 'hono/client'
export type Post = InferResponseType<typeof api.api.posts.$get, 200>['posts'][number]
```

Quy tắc RPC phía web:

- **MUST** `"strict": true` trong tsconfig của cả api lẫn web (đã ép qua `tsconfig.base.json`).
- Component **không** import `hc` trực tiếp — chỉ import `api` từ `lib/api.ts`.
- Type cho props/component lấy bằng `InferResponseType` từ client, không định nghĩa lại tay.

## 7. Config, lỗi, DB

### 7.1 `config/env.ts`

```ts
import { z } from 'zod'

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  LOG_LEVEL: z
    .enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace', 'silent'])
    .default('info'),
  DATABASE_URL: z.url(),
  SERVE_WEB: z.stringbool().default(false), // KHÔNG dùng z.coerce.boolean(): "false" sẽ coerce thành true
  WEB_DIST: z.string().default('./web-dist'),
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

- Đây là nơi **duy nhất** biết đến `process.env`, nhưng chỉ đọc khi `index.ts` (hoặc `testDeps()`) gọi `loadEnv()` — **không parse lúc import**. Parse lúc import làm mọi file test transitively import env crash khi thiếu biến, và là side effect ngoài `index.ts`.
- `dotenv` load ở `index.ts` (`import 'dotenv/config'`), không load ở đây.
- Trên Node không dùng `c.env` cho secrets (đó là pattern của Workers).
- Thêm biến env mới → cập nhật cả `env.ts` lẫn `.env.example` trong cùng commit.

### 7.2 `lib/errors.ts` — một envelope duy nhất

Mọi lỗi trả về dạng: `{ "error": { "code": "UPPER_SNAKE", "message": "...", "details?": ... } }`

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

Nhắc lại phân công: lỗi dự đoán được → `c.json(..., 4xx)` trong handler (RPC thấy được); `onError` chỉ đỡ lỗi bất ngờ (RPC không thấy — chấp nhận được vì web xử lý qua `res.ok`). Message của lỗi 500 luôn generic — chi tiết chỉ nằm trong log.

**Không dùng envelope `{ success: boolean, data }`:** với RPC, `res.ok` + `InferResponseType<..., 200>` đã là discriminant; flag `success` là thừa và làm bẩn type mọi response. (Đây là ngoại lệ có chủ đích so với rule API-envelope chung cho REST không typed.)

### 7.3 `lib/validate.ts` — validation lỗi cùng envelope

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

Lý do tồn tại: response 400 mặc định của `zValidator` có shape riêng của Zod, không cùng envelope lỗi của app.

### 7.4 Database — Drizzle + Postgres (default)

- Schema: `src/db/schema/*.ts`, table snake_case số nhiều, export từ `src/db/schema/index.ts`.
- `src/db/index.ts` export `createDb(url)` (factory — **không** export instance) và các type `Db`, `DbConn` (mục 4.7). Đóng kết nối khi shutdown qua `db.$client.end()` (pg Pool) / `db.$client.close()` (better-sqlite3).
- Migrations: `drizzle-kit generate` → commit thư mục `drizzle/`; apply bằng `drizzle-kit migrate` trong CI/CD trước khi start container mới.
- Variation point: SQLite cho tool nhỏ; Kysely nếu team quen. Đổi ORM không được đổi shape thư mục.

### 7.5 `middleware/request-logger.ts`

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

Structured log (pino) + correlate `requestId` từ đầu — không dùng `hono/logger` (console, không structured). `lib/logger.ts` chỉ là factory mỏng:

```ts
import { pino, type Logger } from 'pino'
import type { Env } from '../config/env'

export type { Logger }

export function createLogger(level: Env['LOG_LEVEL']): Logger {
  return pino({ level })
}
```

---

## 8. `packages/shared` — quy tắc chống phình

Shared là **pull-based**: chỉ chuyển một thứ vào `shared` khi web cần **giá trị runtime** của nó (vd: Zod schema dùng lại cho form validation, enum/constant, pure util). Type thuần thì RPC đã lo — không cần shared.

- Bắt đầu project **không có** `packages/shared`. Tạo khi có nhu cầu thật đầu tiên.
- Code trong shared phải chạy được ở cả browser lẫn Node: **NEVER** import Node built-ins, DB, hay env trong shared.
- Export TS source trực tiếp như `@repo/api` (không build step).

---

## 9. Dev workflow & serve SPA

### 9.1 Dev: 2 process, same-origin qua proxy

```jsonc
// apps/api: "dev": "tsx watch src/index.ts"
// apps/web: "dev": "vite"
// root:     "dev": "pnpm -r --parallel dev"
```

```ts
// apps/web/vite.config.ts
export default defineConfig({
  server: { proxy: { '/api': 'http://localhost:3000' } },
})
```

Nhờ proxy (dev) và single container (prod), web và api luôn same-origin → **không cần CORS**. Chỉ bật `hono/cors` khi tách deploy web (xem Escape hatches).

### 9.2 `index.ts` — entry Node (prod serve luôn SPA)

```ts
import 'dotenv/config'
import { serve } from '@hono/node-server'
import { serveStatic } from '@hono/node-server/serve-static'
import { createApp } from './app'
import { loadEnv } from './config/env'
import { buildDeps } from './deps'

const env = loadEnv()
const deps = buildDeps(env)
const app = createApp(deps)

if (env.SERVE_WEB) {
  // Lưu ý: root của serveStatic tính từ CWD lúc chạy process, không phải từ file này
  app.use('*', async (c, next) => {
    if (c.req.path.startsWith('/api')) return next()
    return serveStatic({ root: env.WEB_DIST })(c, next)
  })
  app.get('*', (c, next) => {
    if (c.req.path.startsWith('/api')) return next() // rơi xuống notFound JSON
    return serveStatic({ root: env.WEB_DIST, path: 'index.html' })(c, next) // SPA fallback
  })
}

const server = serve({ fetch: app.fetch, port: env.PORT }, (info) => {
  deps.logger.info({ port: info.port }, 'api listening')
})

function shutdown() {
  server.close(async (err) => {
    if (err) {
      deps.logger.error({ err }, 'shutdown error')
      process.exit(1)
    }
    await deps.db.$client.end()
    process.exit(0)
  })
}
// process.once — signal thứ hai khi đang close không được re-enter shutdown
process.once('SIGTERM', shutdown)
process.once('SIGINT', shutdown)
```

## 10. Build & deploy (1 container)

Thứ tự build: `web build` (Vite → `apps/web/dist`) → `api build` (`tsc -p tsconfig.build.json` → `apps/api/dist`) → image copy cả hai.

```dockerfile
FROM node:22-alpine AS base
RUN corepack enable

FROM base AS build
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile && pnpm -r build && pnpm prune --prod

FROM base AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 hono
COPY --from=build --chown=hono:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=hono:nodejs /app/apps/api/node_modules ./apps/api/node_modules
COPY --from=build --chown=hono:nodejs /app/apps/api/dist ./apps/api/dist
COPY --from=build --chown=hono:nodejs /app/apps/web/dist ./web-dist
USER hono
ENV SERVE_WEB=true WEB_DIST=./web-dist
EXPOSE 3000
CMD ["node", "apps/api/dist/index.js"]
```

- Health check của orchestrator trỏ vào `GET /api/health`.
- Prod chạy `node dist` — không dùng tsx trong container.

---

## 11. Naming — bảng tra nhanh

| Đối tượng | Quy ước | Ví dụ |
|---|---|---|
| Thư mục module | kebab-case, danh từ số nhiều của resource | `modules/order-items/` |
| File trong module | `<module>.<vai trò>.ts` | `posts.routes.ts`, `posts.service.ts` |
| URL path | kebab-case, số nhiều, không version | `/api/order-items/:id` |
| Export sub-app | factory `create<Module>Routes` + `<Module>RouteDeps` | `createPostsRoutes(deps: PostsRouteDeps)` |
| DB table | snake_case số nhiều | `order_items` |
| Env var | UPPER_SNAKE | `DATABASE_URL` |
| Error code | UPPER_SNAKE | `NOT_FOUND`, `EMAIL_TAKEN`, `VALIDATION` |
| Process module | danh từ quy trình, kebab-case | `modules/checkout/`, `modules/import-pipeline/` |
| Job name | `<module>.<action>`, kebab-case | `import.process-file` |

## 12. Escape hatches — khi project lớn lên

Áp dụng theo trigger, không áp dụng trước (tránh ceremony ở project nhỏ):

1. **IDE/typecheck chậm rõ rệt (thường >100–200 routes):** chuyển RPC sang **precompiled types** — thêm `tsc` emit `dist/` cho api, đổi `exports["./client"]` trỏ vào `dist/client.js` + `dist/client.d.ts`, dev chạy thêm `tsc -b -w`. Code web không đổi (vẫn import `hcWithType`). Đây là hướng chính thức Hono khuyến nghị cho app lớn.
2. **Vẫn chậm sau (1):** tách `hc` theo từng module thay vì một `AppType` tổng — mỗi module export type riêng, `lib/api.ts` tạo nhiều client con.
3. **Cần expose API cho bên thứ ba / mobile:** thêm `hono-openapi` + Scalar cho các route public; route nội bộ giữ nguyên RPC.
4. **Web cần CDN / tách deploy:** `apps/web/dist` đẩy lên CDN, api set `SERVE_WEB=false`, bật `hono/cors` với origin cụ thể.
5. **>2–3 packages hoặc CI chậm:** thêm Turborepo (task graph + cache). Không bắt buộc từ đầu.
6. **Cần auth:** khuyến nghị better-auth (tích hợp Hono tốt), mount ngoài chain RPC nếu SDK không chain được — ghi rõ trong README project.
7. **Route cần resolve `:paramId` lặp lại ở nhiều handler:** thêm middleware `with<Resource>` trong `modules/<name>/` (validate id → 400, check tồn tại → 404, `c.set()` object đã resolve vào Variables typed).
8. **Workflow cần durable execution thực sự** (timer chạy nhiều ngày, human-in-the-loop, fan-out lớn, versioning workflow đang chạy dở): chuyển tầng thực thi sang Temporal hoặc Inngest/Trigger.dev — process service gọi client của engine, shape module giữ nguyên. Queue cần throughput vượt mức Postgres chịu thoải mái: BullMQ + Redis.

## 13. Checklist

### Scaffold project mới
1. Copy template repo (hoặc dựng theo cây mục 2–3) — giữ nguyên tên file/thư mục chuẩn.
2. Đặt tên package: `@repo/api`, `@repo/web` (scope `@repo` cố định cho mọi project để import path đồng nhất).
3. Điền `.env.example` → `.env`; chạy `pnpm dev`; xác nhận `GET /api/health` trả 200 qua web proxy.
4. Chỉnh `CLAUDE.md`: trỏ về file shape này + ghi các variation point đã chọn (DB, auth, logger).

### Thêm module mới (việc lặp lại nhiều nhất — làm đúng thứ tự)
1. Tạo `src/modules/<name>/` với 4 file: `.schema.ts` → `.service.ts` (db qua tham số) → `.routes.ts` (factory + deps hẹp, một chain duy nhất) → `.test.ts` (dùng `testDeps()`).
2. Nếu cần bảng mới: thêm `db/schema/<name>.ts`, chạy `drizzle-kit generate`, commit migration.
3. Mount vào chain trong `createApiRoutes` (1 import + 1 `.route()`).
4. Chạy `pnpm typecheck && pnpm test` — typecheck xanh nghĩa là RPC phía web đã tự có type mới.

Với **process module**: như trên nhưng file theo nhu cầu (`.routes.ts` chỉ khi có endpoint, thêm `.jobs.ts` khi có bước chạy nền); orchestrate qua service của module khác và tuân thủ quy tắc phụ thuộc mục 4.6; hàm ghi của resource service nhận `DbConn` để enlist vào transaction (4.7); pipeline chạy lâu thì model theo "run-as-resource" (bảng `<x>_runs` + POST/GET run).

## 14. Làm việc với coding agent

- Đặt nội dung file này (hoặc symlink/trích) làm `CLAUDE.md` ở root mỗi project. Giao việc dạng: *"Thêm module `invoices` theo shape chuẩn, các trường: …"* — checklist mục 13 là quy trình agent phải theo.
- Verification cho agent = `pnpm typecheck && pnpm test` (không cần review bằng mắt việc tuân thủ RPC — typecheck bắt được vi phạm chain/status).
- Không dùng code generator cứng (plop/hygen) để scaffold module — convention doc + agent + typecheck thay thế được và không phải bảo trì template.

---

*Cập nhật file này khi ecosystem đổi (Hono major mới, HonoX ra stable, Zod major mới). Mọi project trỏ về cùng một bản — sửa một nơi, áp dụng mọi nơi.*
