# Deliverable menus

Proven deliverable enumerations per spec type. The enumeration is what determines the document's shape — two dispatches with the same skill but different enumerations produce structurally different specs. Start from the matching menu and adapt items to the requirement; don't invent the list from scratch.

Every menu keeps the fixed bookends: `a) Inputs used` (traceability) and `z) Tensions`.

## What a spec must NOT contain

Stack/library choices, project structure, and skeleton code belong to the implementation plan, not the spec. A spec defines the observable contract; mixing in implementation concerns makes the document part-spec part-architecture-doc and forces re-review when implementation details change. If the dispatcher wants those too, request them as a SEPARATE deliverable file.

## Menu: CLI surface spec

For specifying a command-line tool's interface (commands, flags, output, exit codes).

- a) **Inputs used** — files read; table of major decisions → driving standard section
- b) **Global conventions** — typed exit-code map (per code: name, failure class, which commands return it); stdout/stderr contract; ONE unified `--json` envelope for success AND structured errors (error type = exit-code enum name, plus a machine-readable `offending` field agents can act on); color/TTY/`NO_COLOR` rules; `-q`/`--verbose`/`--debug` semantics; global semantics of `--dry-run`/`--force`/`--no-input`/`--confirm`; env vars honored; config precedence chain and file locations
- c) **Command reference** — PER command: synopsis, description citing the requirement section it implements, positionals, flag table (short+long, type, default, meaning), one human example AND one `--json` example with the actual output, the exit codes THIS command returns, error cases with exact message text (what failed / why / how to fix)
- d) **Interactivity matrix** — every prompt × its flag equivalent × exact non-TTY/`--no-input` behavior (one row per prompt; this is the table a tester checks line by line)
- e) **Destructive-action spec** — tier table (mild/moderate/severe) per action with rationale and the non-interactive confirm path; state explicitly what `--force` does NOT cover
- f) **Agent-tool surface** — the structured-error contract agents branch on, machine-readable gates, input hardening rules (reject control chars, traversal, malformed ids before side effects), confirm-token requirements, token/file-based auth path, help/`--describe` as a stable contract
- g) **Scaffold spec** — only if the tool has an init/scaffold command: exact files created, prompt-vs-flag for each value, what it deliberately does not do (e.g. `git init`)
- h) **Help & discoverability** — bare invocation behavior, `-h`/`--version`, missing-required-arg behavior, did-you-mean policy, no catch-all/no prefix abbreviation
- z) **Tensions** — every conflict, reconciliation, question for the owner

## Menu: Behavior spec (skill / agent / workflow)

For specifying an agent's, skill's, or guided workflow's observable behavior so an author can implement it and a tester can verify it.

- a) **Inputs used** — files read; decisions → driving standard section
- b) **Trigger & scope contract** — final frontmatter/description (trigger-only), in-scope and out-of-scope cases each with one concrete example utterance, routing target for each out-of-scope case
- c) **Process/flow contract** — each phase/state with entry condition, the decision(s) it resolves, exit criteria, and one example turn; explicit escape hatches and their behavior
- d) **Output template contract** — per output section: what "complete" means, required N/A wording when inapplicable, 1-2 line example, conditional rules for when a section is required
- e) **Testable rules** — restate the requirement's musts (safety, quality, evals) as numbered pass/fail criteria a reviewer can apply to a produced artifact
- f) **Stop & handoff rules** — default stopping point, optional follow-on artifacts, exact conditions under which each may be offered
- g) **Verification plan** — map existing test scenarios to RED/GREEN criteria; list requirements with NO covering scenario AND scenarios testing nothing the requirement asks for
- z) **Tensions** — including standard-vs-standard and requirement-internal conflicts

## Deriving a menu for a new spec type

No matching menu? Build one by asking: what does the implementer code against, and what does a tester check line by line? Each item needs a completeness definition ("not complete until ..."), at least one section must be a per-unit reference (per command / per endpoint / per phase) with worked examples, and one must turn the requirement's musts into checkable pass/fail rules. Keep the a/z bookends. After the run, fold what worked back into this file as a new menu.
