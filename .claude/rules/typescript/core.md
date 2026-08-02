<!-- Reusable TS rule set — canonical home. Keep generic; copy into another project's
     .claude/rules/typescript (or ~/.claude/rules/typescript for global use) to reuse. -->

# TypeScript — Core

If a project instruction (CLAUDE.md, project rules) conflicts with anything in these TypeScript rules, the project wins.

## Type discipline

- No `any`. Use `unknown` for genuinely unknown values and narrow before use.
- No non-null assertions (`!`). Prove non-null via narrowing, or handle the null/undefined case.
- No `as` casts to make a type error go away (`as const` is fine). A cast that "fixes" an error is hiding a real bug.
- `@ts-expect-error` requires a same-line reason comment and explicit user approval. `@ts-ignore` is never acceptable.
- Explicit return types on exported functions. Rely on inference inside function bodies and for locals.

## Modeling

- Model alternatives as discriminated unions; make illegal states unrepresentable. Not optional-field bags like `{ loading: boolean; data?: Data; error?: Error }`.
- No `enum`, no `namespace`, no class parameter properties. Use `as const` objects plus derived union types instead. Reason: staying inside erasable syntax keeps code runnable under native type stripping (Node, and the direction the ecosystem is moving) and portable across runtimes.
- Data crossing a boundary (network, fs, env, CLI args, LLM output) is untrusted. Type it `unknown`, parse it with the project's schema library (zod, valibot, arktype, …), and derive the static type from the schema — one source of truth. Never hand-write a type that mirrors a schema.

## Errors

- Never swallow errors: no empty `catch`, and no `catch` that logs and then continues as if the operation succeeded.
- When rethrowing, preserve context: `new Error("higher-level message", { cause: err })`.
- Follow the project's existing error-handling style (exceptions vs Result-style returns). Do not introduce a second style into a codebase.

## Conventions

- `interface` for object shapes; `type` for unions, intersections, and function types.
- Named exports. Default exports only where a framework requires them.
- `import type` for type-only imports; `node:` prefix for Node builtins.
- File names in kebab-case (`passage-command.ts`).
- Don't use `||` for defaults where `0`, `""`, or `false` are valid values — use `??`.
