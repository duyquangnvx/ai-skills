# Common Patterns

## Skeleton Projects

When implementing new functionality:
1. Search for battle-tested skeleton projects
2. Evaluate candidates on security, extensibility, and relevance
3. Clone best match as foundation
4. Iterate within proven structure

## API Response Format

Use a consistent envelope for all API responses:
- Include a success/status indicator
- Include the data payload (nullable on error)
- Include an error message field (nullable on success)
- Include metadata for paginated responses (total, page, limit)

**Exception — statically typed RPC APIs** (e.g. Hono RPC via `hc<AppType>`): return the bare success payload with an explicit status code, and a structured error envelope `{ error: { code, message, details? } }` for failures. The type system plus `res.ok`/status replaces the success flag; adding one only pollutes every inferred type.
