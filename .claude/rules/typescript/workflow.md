---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript — Workflow

## Definition of done

- A change is not done while typecheck, lint, or affected tests fail.
- Use the project's own scripts — check `package.json` for `typecheck`, `lint`, `test` or their equivalents. If no typecheck script exists, run `tsc --noEmit` through the project's package manager.
- Run the smallest relevant check first (single test file, one package); run the full affected suite before declaring the task complete.
- When reporting done, state: what changed, which checks ran with their results, and anything **not** verified.
- If no runnable check covers the change, say it is unverified. Re-reading the code is not verification.

## Gate integrity

- Never make a failing check pass by weakening the check itself: no suppression comments, no `eslint-disable`, no loosening `tsconfig` or lint config, no deleting or skipping tests. Fix the root cause.
- If the check itself seems wrong, stop and say so. Changing a gate (config, rule, test expectation) requires explicit user approval — with the reasoning stated.
- Stuck after a few genuine attempts? Stop and present the failing error with what you tried. Do not keep mutating code until something silences it.

## Change discipline

- Keep diffs minimal. Don't reformat, rename, or "improve" code unrelated to the task.
- Adding a dependency requires asking first. Check whether an existing dependency or the standard library already covers the need.
- Never hand-edit generated files or lockfiles. Regenerate them through their owning tool.
