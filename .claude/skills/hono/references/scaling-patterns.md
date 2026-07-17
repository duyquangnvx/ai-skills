# Hono Scaling Patterns

Read this only when a task crosses resources, needs background work, or the app is outgrowing the simple standard. Base structure and rules are in [project-standard.md](project-standard.md); code templates in [module-skeletons.md](module-skeletons.md).

---

## Cross-domain features: process modules

A module is a **capability**, not a DB table. When a business operation spans several resources (checkout touches orders + inventory + payments; an import pipeline touches files + products + logs), **do not** stuff the orchestration into one resource module, and **do not** create a global `usecases/` layer — create a **process module** alongside the resource modules: `modules/checkout/`, `modules/import-pipeline/`.

- A process module *does not own* another module's resources; it orchestrates through their services. It *may* own its own process-state table (e.g. `import_runs`).
- Files as needed: `.service.ts` (required — orchestration lives here, takes deps like any service), `.schema.ts`, `.routes.ts` (when there is an endpoint — still a factory + narrow deps), `.jobs.ts` (when there is a background step), `.test.ts`.

**Dependency rules** (anti-spaghetti — violating these is what rots a multi-domain codebase; CI-enforce with Biome `noImportCycles`, which is not in the recommended set so must be enabled manually):

1. Cross-module calls happen **only service→service**. **NEVER** import another module's `*.routes.ts`; **NEVER** internal HTTP between modules.
2. One direction: process module → resource module. Resource modules **never** import process modules.
3. Resource ↔ resource: limited. Two resources that keep calling each other back and forth need a process module above them — or they are really one module.
4. Job handlers only call their own module's service (+ injected infra like a mailer); no logic in handlers.

**Cross-cutting reads** (dashboards, reports): a service may join tables directly via Drizzle — read-tier coupling is acceptable in a modular monolith, traded for simplicity. **Writes** must go through the owning module's service. Tradeoff to know: if you later split a service, these read-joins are the first thing to unpick.

**Routes of a process module** — two patterns, pick by runtime:

- **Done within one request:** an action endpoint, e.g. `POST /api/checkout`. Still chained, still RPC like any route; the business result (a discriminated union from the service) maps to an explicit status — `201` / `409 OUT_OF_STOCK` / `402 PAYMENT_DECLINED`…
- **Long / multi-step:** **model the "run" as a resource**. `POST /api/import-runs` creates the run, returns `202` + `{ id }`; `GET /api/import-runs/:id` returns `{ status, step, progress, result, error }` for polling (RPC-typed). The `import_runs` table belongs to this module. Upside: the pipeline matches the existing shape 100% (module + table + routes + RPC), and retry/resume/poll come naturally. For realtime, add an SSE route (`streamSSE`) — note that stream responses are not RPC-typed; the client reads them with `EventSource`.

---

## Cross-module transactions

So a process service can compose several resource services in **one** transaction, every DB-**writing** service function takes `DbConn` (instead of `Db`) as its first parameter:

```ts
// db/index.ts additions — derived from the type, no instance needed
export type Tx = Parameters<Parameters<Db['transaction']>[0]>[0]
export type DbConn = Db | Tx
```

```ts
// resource service — standard signature for a write function
export async function createOrder(conn: DbConn, input: CreateOrderInput) { /* ... */ }
```

```ts
// process service owns the transaction boundary
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

- The transaction opens where the whole business operation is visible (the process service, or a resource module's handler when it is a single domain). A service receiving `conn` uses it — it never opens its own transaction.
- **Abort with a typed result:** Drizzle's `tx.rollback()` throws, so a `return` after it does not escape. To abort the transaction and carry a business result out (e.g. `{ status: 'out_of_stock' }`), throw a sentinel class holding the result and catch it right outside `db.transaction`; re-throw anything that is not the sentinel so `onError` handles it.
- Non-atomic side effects (email, webhooks, external APIs) **NEVER** go inside the transaction — enqueue a job **after** commit.

---

## Background steps & long pipelines

Default: **pg-boss** — a job queue running on the app's existing Postgres: no new infrastructure, retry/backoff/cron built in. (Variation: BullMQ if Redis already exists; **SQLite → the variant below**, because pg-boss/BullMQ both need Postgres/Redis.) Wrap it as a factory `lib/queue.ts` (`createQueue(env.DATABASE_URL)`) and add `queue` to `Deps` like any dependency.

- `<module>.jobs.ts`: export job names (constants, `'<module>.<action>'`) + handler **factories taking deps** — handlers only call services, no logic.
- `src/worker.ts`: `createWorker(deps)` imports every `*.jobs.ts`, registers `.work()` with pg-boss, exports `startWorker(deps)` / `stopWorker()`.
- `index.ts`: `await deps.queue.start()` in **every** role — the API process enqueues too, so it also starts; only consumer registration (`startWorker`) is gated by `if (env.RUN_WORKER)`. Shutdown order: `stopWorker()` → stop queue → close db. Add `RUN_WORKER: z.stringbool().default(true)` to `env.ts` when jobs start being used.
- Scale: same Docker image, split roles by env — container A `SERVE_WEB=true RUN_WORKER=false`, container B the reverse. No new entry or image.
- Multi-step pipeline: one job per step; a finished step updates the `<x>_runs` row (status/step/progress) **in the same transaction as its work**, then enqueues the next step after commit. A failure retries that step (steps must be idempotent — redelivery-safe) and resumes mid-pipeline.
- An LLM/agent pipeline uses exactly this shape: each model call is a job with its own retry, state lives in the runs table (resume when a call fails), progress reaches the UI via poll or SSE.

### SQLite variant — self-rolled resource-lane queue

pg-boss/BullMQ both need Postgres/Redis. When the DB is **SQLite** (a single-node tool) and work is gated by a **specific scarce resource** — one GPU, a rate-limited API, a politeness-limited scraper — rather than by throughput, rolling the queue on a `jobs` table is the right size and adds no infrastructure. Keep run-as-resource for long pipelines; only the *run mechanism* changes from pg-boss to a hand loop.

**`jobs` table** (`db/schema/jobs.ts`): `id`, `type` (partitions lanes), `status` (`queued|running|done|failed|cancelled`), `priority` (int, default 0), `payload` (json nullable, e.g. `{ itemIds }`), `error`, `created_at`. One job spans many items — **never** one row per item.

**Lane = one sequential loop filtered by `type`.** Lanes run in parallel because they consume **different resources** (network / external-LLM / GPU); each lane is serial. Single-threaded Node is fine — lanes are IO-bound (HTTP to external services) or child processes (ffmpeg), both yield the CPU. Group lanes by *resource*, not *speed*: two kinds of work contending the same GPU share a lane.

Rules:

1. **MUST claim a job atomically** with better-sqlite3's synchronous transaction: in one `db.transaction`, pick the lane's `queued` job by `priority DESC, created_at ASC LIMIT 1` and `UPDATE status='running'` in the same transaction. SQLite's single-writer + short transaction prevents two lanes grabbing the same job — this is why sync better-sqlite3 over an async driver.
2. **MUST resume on boot:** all `running` → `queued`. Steps stay idempotent so redelivery is safe.
3. **Granularity:** the worker loops items *inside* a job. **Priority and cancel act at the item level**, not the job: check the `cancelled` flag **between items**, let the running item finish.
4. **Cancel/pause:** set `status='cancelled'`; do not kill mid-item.
5. Lane sort: `priority DESC, created_at ASC`. "Prioritize this work" = enqueue with high priority; backlog is priority 0.

**Files mirror the pg-boss layout — only the internals change:**

- `lib/queue.ts`: `createQueue(db)` — a factory wrapping the `jobs` table (`enqueue`, `claim`, `complete`, `fail`, `cancel`, `resetRunning`); add `queue` to `Deps` like any dependency. **NEVER** let a lane import a db singleton.
- `<module>.jobs.ts`: job names (`'<module>.<action>'`) + handler factories taking deps — only call services, no logic (same as pg-boss).
- `worker.ts`: `startWorker(deps)` spawns the lane loops, `stopWorker()` halts them at an **item boundary**. Map job type → lane here.

**Where it runs:** default in-process with the API (single node, single writer — simplest; call `startWorker(deps)` in `index.ts` after `buildDeps`). A separate worker process **must** enable **WAL mode** and keep **exactly one writer** — SQLite forbids concurrent writers. Gate the role by env (`RUN_WORKER`) as with pg-boss.

**Progress to the UI:** poll `GET /api/<x>-runs/:id` (RPC-typed) or SSE `streamSSE` for realtime; on client connect, **emit a snapshot read from the DB first**, then stream — a client joining mid-job should not see a blank.

**Leaving this variant → escape hatch:** need multiple nodes/writers, or throughput past a single SQLite writer → back to the default (Postgres + pg-boss) or BullMQ + Redis. The module shape is unchanged when switching.

---

## Escape hatches — when the project grows

Apply on trigger, not preemptively (avoid ceremony in small projects):

1. **IDE/typecheck noticeably slow (usually >100–200 routes):** switch RPC to **precompiled types** — add `tsc` emitting `dist/` for the api, point `exports["./client"]` at `dist/client.js` + `dist/client.d.ts`, run `tsc -b -w` in dev. Web code is unchanged (still imports `hcWithType`). This is Hono's official recommendation for large apps.
2. **Still slow after (1):** split `hc` per module instead of one aggregate `AppType` — each module exports its own type, `lib/api.ts` builds several sub-clients.
3. **Need to expose the API to third parties / mobile:** add `hono-openapi` + Scalar for the public routes; internal routes stay on RPC.
4. **Web needs a CDN / separate deploy:** push `apps/web/dist` to a CDN, set the api `SERVE_WEB=false`, enable `hono/cors` with a specific origin.
5. **>2–3 packages or slow CI:** add Turborepo (task graph + cache). Not required from the start.
6. **Need auth:** better-auth is recommended (integrates well with Hono); mount it outside the RPC chain if the SDK can't chain — note it in the project README.
7. **A `:paramId` resolved repeatedly across handlers:** add a `with<Resource>` middleware in `modules/<name>/` (validate id → 400, existence check → 404, `c.set()` the resolved object into typed Variables).
8. **A workflow needs true durable execution** (timers running for days, human-in-the-loop, large fan-out, versioning in-flight workflows): move the execution layer to Temporal or Inngest/Trigger.dev — the process service calls the engine's client, the module shape stays the same. A queue needing throughput beyond what Postgres handles comfortably: BullMQ + Redis.
