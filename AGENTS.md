# Repository agent instructions

## Session protocol

- Design decisions are grilled with the user one question at a time, each with a recommendation; the user decides. Don't build past an ungrilled decision.
- When a domain term crystallises, update `CONTEXT.md` immediately. Hard-to-reverse + surprising + real trade-off → new ADR.
- Research runs as a background agent against primary sources → one cited note in `docs/research/`.

## Conventions

- English for code; **Vietnamese** when talking to the user.

## Project status

- We are greenfield project with no deployment or people using this anywhere, breaking change is freely allow and no need to concern yourself with backward compatible.
- Keep the codebase clean and the architecture responsive for the future.

## Agent skills

### Domain docs

Single-context — `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.