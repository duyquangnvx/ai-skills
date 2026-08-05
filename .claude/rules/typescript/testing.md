---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

<!-- Scoped to all TS files, not just *.test.ts: these rules govern behavior while
     editing source too. -->

# TypeScript — Testing

- Use the project's existing test runner, layout, and naming. Before writing a test, read one or two neighboring test files and match their style — don't introduce a new pattern.
- Test observable behavior through the public API. Don't assert on private internals, and don't make "mock was called with …" the primary assertion.
- Mock only true boundaries: network, clock, fs, external services. Don't mock modules the project owns just to make a test easier to write.
- Tests must be deterministic: fake time, seed randomness, no real network.
- Bug fixes are regression-test-first: write the failing test, confirm it fails for the right reason, then fix. Keep the test.
- A failing test is information. Decide which is wrong — the code or the test. Fixing the code needs no permission; changing a test's expectations does: state why the old expectation was wrong and get confirmation first.

## E2E

- Use **Playwright** for E2E tests of critical user flows. Delegate to the **e2e-runner** agent where available.
