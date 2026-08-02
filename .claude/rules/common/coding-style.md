# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones — update by returning a new copy with the change applied.

## Build vs. Buy (Total Cost, Not Fewest Deps)

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
