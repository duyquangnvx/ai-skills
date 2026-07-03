# Hono Fullstack & Deploy

Read this for the web side and deployment of a fullstack repo. A server-only API skips this file. Base structure and rules are in [project-standard.md](project-standard.md); server code in [module-skeletons.md](module-skeletons.md).

---

## Monorepo version pinning

**MUST:** declare `hono` and `zod` through a pnpm catalog so api and web always match — a mismatched `hono` version between the two silently breaks RPC type inference in confusing ways.

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
// in the package.json of apps/api and apps/web
"dependencies": { "hono": "catalog:", "zod": "catalog:" }
```

---

## client.ts — the RPC surface

```ts
import { hc } from 'hono/client'
import type { AppType } from './app'

export type { AppType }
export type ApiClient = ReturnType<typeof hc<AppType>>
export const hcWithType = (...args: Parameters<typeof hc>): ApiClient =>
  hc<AppType>(...args)
```

**MUST:** in `client.ts` only `import type` from `./app` — a value import drags the whole server graph (db driver, env) into the web bundle. The one runtime import allowed here is `hono/client`. (`AppType = ReturnType<typeof createApiRoutes>` stays a pure type — `import type` pulls no runtime.)

`apps/api/package.json` exports the TS source directly (the "internal package" pattern — the web bundler compiles it):

```jsonc
{
  "name": "@repo/api",
  "exports": { "./client": "./src/client.ts" }
}
```

---

## web — one client, one place

```ts
// apps/web/src/lib/api.ts
import { hcWithType } from '@repo/api/client'
export const api = hcWithType('/')   // same-origin: dev via Vite proxy, prod same server

// Pull a response type when passing data into a component:
import type { InferResponseType } from 'hono/client'
export type Post = InferResponseType<typeof api.api.posts.$get, 200>['posts'][number]
```

Web RPC rules:

- **MUST** `"strict": true` in the tsconfig of both api and web (forced via `tsconfig.base.json`).
- Components **never** import `hc` directly — only import `api` from `lib/api.ts`.
- Prop/component types come from `InferResponseType` off the client, never redefined by hand.

---

## packages/shared — anti-bloat rules

`shared` is **pull-based**: move something into `shared` only when the web needs its **runtime value** (e.g. a Zod schema reused for form validation, an enum/constant, a pure util). Pure types are already handled by RPC — no need for shared.

- Start a project **without** `packages/shared`. Create it on the first real need.
- Code in `shared` must run in both browser and Node: **NEVER** import Node built-ins, DB, or env in `shared`.
- Export TS source directly like `@repo/api` (no build step).

---

## Dev workflow: 2 processes, same-origin via proxy

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

Thanks to the proxy (dev) and a single container (prod), web and api are always same-origin → **no CORS needed**. Only enable `hono/cors` when the web is deployed separately (see escape hatch 4 in [scaling-patterns.md](scaling-patterns.md)).

---

## index.ts — serving the SPA in prod

The base entry lives in [module-skeletons.md](module-skeletons.md). For a fullstack build, add the `SERVE_WEB` block (and add `SERVE_WEB: z.stringbool().default(false)` + `WEB_DIST: z.string().default('./web-dist')` to `config/env.ts`):

```ts
import { serveStatic } from '@hono/node-server/serve-static'
// ...after createApp(deps), before serve():

if (env.SERVE_WEB) {
  // Note: serveStatic root is relative to the process CWD at runtime, not this file
  app.use('*', async (c, next) => {
    if (c.req.path.startsWith('/api')) return next()
    return serveStatic({ root: env.WEB_DIST })(c, next)
  })
  app.get('*', (c, next) => {
    if (c.req.path.startsWith('/api')) return next() // falls through to the JSON notFound
    return serveStatic({ root: env.WEB_DIST, path: 'index.html' })(c, next) // SPA fallback
  })
}
```

Every endpoint under `/api` (basePath) is what makes this fallback clean.

---

## Build & deploy — one container

Build order: `web build` (Vite → `apps/web/dist`) → `api build` (`tsc -p tsconfig.build.json` → `apps/api/dist`) → image copies both.

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

- The orchestrator's health check points at `GET /api/health`.
- Prod runs `node dist` — never `tsx` in the container.
