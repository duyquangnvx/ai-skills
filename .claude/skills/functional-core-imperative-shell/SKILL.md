---
name: functional-core-imperative-shell
description: "Use when designing or scaffolding a new backend use case, handler, service method, endpoint, worker, or background job in TypeScript that involves both business logic and IO (database, HTTP, queue, cache, filesystem, third-party SDK, clock, random, UUID). Trigger on prompts like 'implement X', 'build the Y endpoint', 'add a handler for Z', 'create a service method that...', 'design the flow for...', 'where should this logic go', or any greenfield backend feature where the user describes both decisions and side effects. Apply even when the user does not name a pattern — the goal is to produce code structured as pure domain + thin orchestration + injected IO from the start, not retrofit it later. Do NOT apply for pure CRUD passthrough with no business rules, frontend UI components, streaming/backpressure-heavy work, or one-shot scripts."
---

# Functional Core / Imperative Shell for TypeScript Backends

Design every new backend use case as **pure domain logic + thin orchestration + injected IO**. The pure core holds business rules and decisions. The shell loads dependencies and sequences calls. IO operations are injected as interfaces or functions, never imported directly into domain code.

This skill applies to **greenfield use cases** — new endpoints, handlers, service methods, jobs, or workers. For each piece of work, follow the structure below before writing code. Skip to "When NOT to Apply" first if the task looks like pure CRUD or streaming.

## The Three Layers

```
┌──────────────────────┐    pure call    ┌──────────────────────┐    injected IO    ┌──────────────────────┐
│   Domain (core)      │ ─── returns ──→ │  Use Case (shell)    │ ──── invokes ────→│   Infrastructure     │
│                      │                 │                      │                   │                      │
│  Pure functions      │                 │  Orchestrates only   │                   │  DB clients          │
│  Immutable types     │                 │  Calls domain        │                   │  HTTP / queue / cache│
│  Business rules      │                 │  Calls injected IO   │                   │  Clock / Random / UUID│
│  No async            │                 │  No business logic   │                   │  Logger / metrics    │
│  No imports of IO    │                 │  May be async        │                   │                      │
└──────────────────────┘                 └──────────────────────┘                   └──────────────────────┘
       /domain                              /application                               /infrastructure
```

The use case is the only layer that knows about all three. Domain knows nothing about infrastructure. Infrastructure knows nothing about domain types it doesn't need to satisfy a port.

## The Sandwich Pattern

Every use case follows this shape:

```
1. Read inputs from IO     ← imperative (load via injected deps)
2. Run pure domain logic   ← functional (decisions, validation, calculations)
3. Write outputs via IO    ← imperative (persist, publish, respond)
```

If you find yourself reading IO in the middle of step 2, the use case is doing too much — split into two sandwiches or move the decision earlier. A use case that genuinely needs alternating IO and decisions (rare) becomes multiple smaller use cases composed at the edge.

## Step 1 — Domain: Pure Types and Functions

```typescript
// domain/order.ts — NO async, NO IO imports, NO Date.now(), NO Math.random()

export type Money = { amount: number; currency: string };
export type LineItem = { sku: string; qty: number; unitPrice: Money };
export type Order = {
  id: string;
  customerId: string;
  items: LineItem[];
  placedAt: Date;
  status: "Draft" | "Placed" | "Cancelled";
};

export type DiscountTier = "None" | "Gold" | "Platinum";

export function calculateSubtotal(items: LineItem[]): Money {
  // pure: same input → same output, no side effects
  const total = items.reduce((sum, i) => sum + i.unitPrice.amount * i.qty, 0);
  return { amount: total, currency: items[0]?.unitPrice.currency ?? "USD" };
}

export function applyDiscount(subtotal: Money, tier: DiscountTier): Money {
  const rate = tier === "Platinum" ? 0.15 : tier === "Gold" ? 0.10 : 0;
  return { ...subtotal, amount: subtotal.amount * (1 - rate) };
}

export function placeOrderDecision(
  draft: Order,
  tier: DiscountTier,
  now: Date,
): { order: Order; total: Money } {
  // All branches, validation, computation live here
  if (draft.items.length === 0) throw new Error("Cannot place an empty order");
  const subtotal = calculateSubtotal(draft.items);
  const total = applyDiscount(subtotal, tier);
  return {
    order: { ...draft, status: "Placed", placedAt: now },
    total,
  };
}
```

Even `now: Date` is passed in — domain never calls `new Date()` itself. Same for `Math.random()`, `crypto.randomUUID()`, and `process.env`. Determinism makes domain trivially testable.

**Error style — pick one and stay consistent.** Two valid shapes for domain failure:

```typescript
// Style 1 — throw typed domain errors (TS/JS idiomatic)
export class CouponExpired extends DomainError {}
if (now > coupon.expiresAt) throw new CouponExpired();

// Style 2 — return Result<Ok, Err> (Go/Rust-flavored, no throws)
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
if (now > coupon.expiresAt) return { ok: false, error: "CouponExpired" };
```

Style 1 is lighter and matches typical TS code. Style 2 makes failures part of the type signature, harder to ignore. Either works inside FC/IS — what matters is consistency across the codebase. Mixing both forces readers to remember which use case throws and which returns.

## Step 2 — Ports: Interfaces for IO

Define the **capabilities** the use case needs, in the application layer (or domain if shared widely). Never in infrastructure.

```typescript
// application/ports.ts — what the use case asks the world to provide

export interface CustomerReader {
  byId(id: string): Promise<{ id: string; tier: DiscountTier } | null>;
}

export interface OrderWriter {
  save(order: Order): Promise<void>;
}

export interface EventPublisher {
  publish(event: { type: string; payload: unknown }): Promise<void>;
}

export interface Clock {
  now(): Date;
}
```

Ports describe **capabilities**, not implementations. Domain never imports them. The use case takes them as parameters (or constructor args).

## Step 3 — Use Case: Thin Orchestration

```typescript
// application/placeOrder.ts

import { Order, placeOrderDecision } from "../domain/order";
import { CustomerReader, OrderWriter, EventPublisher, Clock } from "./ports";

export type PlaceOrderCommand = { draft: Order };
export type PlaceOrderDeps = {
  customers: CustomerReader;
  orders: OrderWriter;
  events: EventPublisher;
  clock: Clock;
};

export async function placeOrder(
  cmd: PlaceOrderCommand,
  deps: PlaceOrderDeps,
): Promise<{ orderId: string; total: Money }> {
  // 1. Read (IO)
  const customer = await deps.customers.byId(cmd.draft.customerId);
  if (!customer) throw new Error("Customer not found");

  // 2. Decide (PURE)
  const { order, total } = placeOrderDecision(
    cmd.draft,
    customer.tier,
    deps.clock.now(),
  );

  // 3. Write (IO)
  await deps.orders.save(order);
  await deps.events.publish({
    type: "OrderPlaced",
    payload: { orderId: order.id, total },
  });

  return { orderId: order.id, total };
}
```

The use case has **no business decisions**. It loads, calls pure functions, and writes. New rules (tax, fraud check, inventory reservation) go into the domain — never as `if`s here.

## Step 4 — Adapters: Implement Ports at the Edges

```typescript
// infrastructure/postgresOrderWriter.ts

import { Pool } from "pg";
import { Order } from "../domain/order";
import { OrderWriter } from "../application/ports";

export class PostgresOrderWriter implements OrderWriter {
  constructor(private pool: Pool) {}
  async save(order: Order): Promise<void> {
    await this.pool.query(
      `INSERT INTO orders (id, customer_id, status, placed_at) VALUES ($1, $2, $3, $4)`,
      [order.id, order.customerId, order.status, order.placedAt],
    );
  }
}
```

Adapters are the **only** place that imports infrastructure SDKs (`pg`, `axios`, `redis`, `aws-sdk`, etc.). They translate between domain types and external schemas — they don't decide anything.

## Step 5 — Composition Root: Wire in main.ts

```typescript
// main.ts — the ONLY file that knows the full graph

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const customers = new PostgresCustomerReader(pool);
const orders = new PostgresOrderWriter(pool);
const events = new KafkaEventPublisher(kafkaClient);
const clock: Clock = { now: () => new Date() };

const deps: PlaceOrderDeps = { customers, orders, events, clock };

app.post("/orders", async (req, res) => {
  const result = await placeOrder({ draft: req.body }, deps);
  res.json(result);
});
```

Composition root is the only place real implementations meet abstractions. Tests provide fakes here without touching production code.

**Translating domain errors at the edge.** Domain throws domain errors (`CouponExpired`, `InsufficientBalance`). The use case lets them propagate. The composition root — where HTTP, queue, or CLI lives — is the only place that maps them to transport-specific shapes:

```typescript
app.post("/orders", async (req, res) => {
  try {
    const result = await placeOrder({ draft: req.body }, deps);
    res.json(result);
  } catch (e) {
    if (e instanceof DomainError) return res.status(409).json({ error: e.code });
    if (e instanceof NotFoundError) return res.status(404).json({ error: e.message });
    throw e; // unknown → 500 via error middleware
  }
});
```

Keep this mapping in one place per transport (HTTP middleware, queue handler wrapper). Do not push HTTP status codes into use cases or domain.

## DI Style: Function Object vs Class

Two equivalent shapes — pick one and stay consistent within a codebase:

```typescript
// Style A — function + deps object (lighter, FP-flavored)
export async function placeOrder(cmd, deps: PlaceOrderDeps) { ... }

// Style B — class with constructor injection (OOP-flavored)
export class PlaceOrderHandler {
  constructor(private deps: PlaceOrderDeps) {}
  async handle(cmd: PlaceOrderCommand) { ... }
}
```

Style A is preferable for stateless use cases (most of them). Style B helps when the use case is invoked many times from a long-lived component (controller, scheduler) and you want to keep deps wired once.

## Diagnostic Checklist — Red Flags

After writing a draft, scan for these. Each one indicates a layer violation. Fix before considering the work done.

### Domain layer red flags

- `async` / `await` / `Promise` appears in any domain function
- Imports from `pg`, `axios`, `node:fs`, `redis`, ORM clients, AWS/GCP SDKs, logger, or any HTTP/queue library
- `Date.now()`, `new Date()` (without argument), `Math.random()`, or `crypto.randomUUID()` called inside a domain function instead of being passed in
- Reads from `process.env` or any global config
- Errors thrown that mention infrastructure ("DB connection lost", "HTTP 503") — domain throws domain errors only
- Mutates objects passed in as arguments instead of returning new ones

### Use case (shell) red flags

- Business `if/else` based on domain rules ("if order > $1000 and customer is Gold...") — move into a domain function
- Multi-step calculations inline — wrap into a named domain function and call it
- More than ~7 dependencies injected — the use case is doing too much, split it
- Imports concrete adapters (`PostgresOrderWriter`) instead of port interfaces (`OrderWriter`)
- IO call in the middle of decisions (read → decide → read → decide) — restructure or split
- Try/catch wrapping domain logic to translate errors — let domain errors propagate, catch only IO errors

Existence guards (`if (!entity) throw ...`), authorization checks (`if (caller.id !== resource.ownerId)`), and idempotency short-circuits (`if (alreadyProcessed) return`) are **not** business decisions — they are preconditions for invoking the domain at all. They belong in the shell. Only branching that depends on domain rules (tiers, thresholds, state transitions, validation) needs to move into a domain function.

### Infrastructure / adapter red flags

- Adapter contains business logic (filtering by rules, computing totals, validating beyond schema) — move to domain
- Adapter imports from domain types it doesn't need to satisfy the port
- Use case imports the concrete adapter class instead of the port interface

If any item triggers, fix before continuing. Most quality regressions in FC/IS systems trace back to one of these.

## When NOT to Apply

This pattern earns its complexity when there are real business rules. Skip or simplify when:

- **Pure CRUD passthrough** — endpoint maps request → DB row → response with no validation or computation. A single function in the adapter is fine; do not invent a domain layer for an empty domain.
- **Streaming / backpressure-heavy work** — processing 10M rows from S3, video transcoding, real-time pipelines. The sandwich shape assumes data fits in memory; use streams or reactive patterns instead.
- **One-shot scripts and migrations** — testability win is not worth the structure for code that runs once.
- **Frontend components** — different patterns (state machines, container/presentational). FC/IS belongs at the architecture level there, not per component.

When in doubt, start simple and refactor toward FC/IS the moment a use case grows a real decision. Do not pre-build the structure for a 5-line function.

## Common Mistakes

**"Domain" is a folder name, not a guarantee.** Putting code in `/src/domain` does not make it pure. Run the red-flag checklist.

**Use case grows business logic over time.** Each new requirement adds an `if` in the use case. Audit periodically and pull conditions into the domain.

**A port for everything.** `Math.max` and `JSON.parse` do not need ports. Only IO and non-determinism (clock, random, UUID, env) need injection.

**Domain types co-located with infrastructure types.** Domain types live in `/domain` and never import from `/infrastructure`. If a type has both, split it into a domain type and a separate DB row type — the adapter maps between them.

**Mocking everything in tests.** If a use case test mocks 5 things, the test is verifying orchestration, not logic. Test pure domain functions with plain inputs (zero mocks). Test use cases with small in-memory fake adapters (a Map for storage, a list for events).

## Test Shapes per Layer

```
Domain:        plain inputs/outputs, no mocks                → many tests, fast
Use case:      injected fakes (in-memory Map, list, clock)   → moderate, fast
Adapter:       integration test against real DB/HTTP         → few tests, slow
End-to-end:    full stack via composition root               → smoke tests only
```

A typical healthy ratio: 80% domain tests, 15% use case tests, 5% integration. If most tests live at the use case level with deep mocks, the domain is too thin — pull logic out of orchestration.

## Output Expectations

When applying this skill to a greenfield request, produce:

1. The **domain file(s)** — types + pure functions, with `placeOrderDecision`-style functions that take all non-determinism as arguments.
2. The **ports file** — interfaces only, no implementation.
3. The **use case file** — the sandwich, async, depends only on ports.
4. **At least one adapter stub** — concrete implementation against the named stack (Postgres, Redis, etc.), enough to show the wiring.
5. The **composition root snippet** — how it gets wired in `main.ts`.
6. A short **checklist confirmation** — list which red-flag items were checked and passed.

Do not produce all five at once for tiny features. For a feature with 10 lines of real logic, the domain + use case + one adapter is enough; mention in prose how composition would extend.