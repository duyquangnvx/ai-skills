# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones:

```

// Pseudocode
WRONG:  modify(original, field, value) → changes original in-place
CORRECT: update(original, field, value) → returns new copy with change

```

Rationale: Immutable data prevents hidden side effects, makes debugging easier, and enables safe concurrency.

## Core Principles

### KISS (Keep It Simple)

- Prefer the simplest solution that actually works
- Avoid premature optimization
- Optimize for clarity over cleverness

### DRY (Don't Repeat Yourself)

- Extract repeated logic into shared functions or utilities
- Avoid copy-paste implementation drift
- Introduce abstractions when repetition is real, not speculative
- Duplication is better than the wrong abstraction
- Extract shared logic only when repeated code has the same reason to change

### Build vs. Buy (Total Cost, Not Fewest Deps)

Decide by total cost of ownership — writing, maintaining, and owning its edge
cases forever — not by "fewest deps."

1. **Stdlib** when the built-in solves it cleanly in a line or two.
2. **A small, battle-tested leaf lib** for non-trivial logic (Unicode,
   parsing, locale, paths, security). Cheaper than hand-rolling it and owning
   its edge cases forever.
3. **Hand-roll** only when the logic is trivial *and* project-specific.

"Stdlib first" = don't add a dep for what the built-in already does — NOT
re-implement what a small lib solves.

**Engineers often underestimate the cost of hand-rolling. Counter that bias:**

- **Decide at write-time, not review-time.** Before writing >a few lines that
  parse/transform/normalize external input, name the leaf lib that already does it.
- **"Trivial" is about input space, not line count.** Unbounded or adversarial
  input is never trivial — can't enumerate it → use the lib.
- **Justify rejecting the lib, not adopting it.** "It's only a few lines" isn't
  a reason. Valid: output-model fight, large shape mismatch, heavy/abandoned dep.

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Extract utilities from large modules
- Organize by feature/domain, not by type

## Error Handling

ALWAYS handle errors comprehensively:
- Handle errors explicitly at every level
- Provide user-friendly error messages in UI-facing code
- Log detailed error context on the server side
- Never silently swallow errors

## Input Validation

ALWAYS validate at system boundaries:
- Validate at trust boundaries: user input, API responses, file uploads,
  environment variables, webhooks, and database records crossing into
  typed/domain code
- Validate all user input before processing
- Use schema-based validation where available
- Fail fast with clear error messages
- Never trust external data (API responses, user input, file content)

## Naming Conventions

- Variables and functions: `camelCase` with descriptive names
- Booleans: prefer `is`, `has`, `should`, or `can` prefixes
- Interfaces, types, and components: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Custom hooks: `camelCase` with a `use` prefix

## Code Smells to Avoid

### Deep Nesting

Prefer early returns over nested conditionals once the logic starts stacking.

### Magic Numbers

Use named constants for meaningful thresholds, delays, and limits.

### Long Functions

Split large functions into focused pieces with clear responsibilities.
