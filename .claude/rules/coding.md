## Code style

- Default to writing no comments. Only add one when the WHY is non-obvious: a hidden constraint, a subtle invariant, a workaround for a specific bug, behavior that would surprise a reader.
- Don't explain WHAT the code does — well-named identifiers already do that. Don't reference the current task, fix, or callers — those belong in the PR description.
- Don't add error handling, fallbacks, or validation for scenarios that cannot happen. Trust internal code and framework guarantees. Only validate at system boundaries.
- Don't use feature flags or backwards-compatibility shims when you can just change the code.

## Responses

- Write for a person: flowing prose, led by the action. A simple question gets a direct answer, not headers and numbered sections.
