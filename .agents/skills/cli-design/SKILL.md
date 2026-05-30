---
name: cli-design
description: Use when designing, building, reviewing, or refactoring a command-line tool (CLI) — covering both UX/interface design (commands, flags, output, errors, help text, config) and TypeScript/Node.js code architecture (project structure, argument parsing, build, distribution, testing). Trigger whenever the user is creating a CLI, adding commands or flags, designing CLI output or help text, choosing a CLI framework (Commander/oclif/yargs/clipanion), publishing a CLI to npm, or asks about CLI conventions and best practices — even if they don't say "best practices" explicitly. Do NOT use for full-screen TUI applications (vim/emacs-style) or for GUI apps.
---

# CLI Design

Build command-line tools that are pleasant for humans and well-behaved for scripts. This skill covers two halves that must both be right: the **UX/interface** the user sees, and the **code architecture** behind it (TypeScript/Node focus). Get both halves right and the tool is intuitive, scriptable, testable, and maintainable as it grows.

The guidance is grounded in the Command Line Interface Guidelines (clig.dev) for UX, and a thin-command/fat-core architecture for code. See the `references/` files for the full detail; this file is the entry point and decision layer.

## When this applies

Reach for this skill for any of: scaffolding a new CLI, adding/redesigning commands or flags, designing terminal output (human + machine readable), writing help text, handling errors, choosing or comparing a CLI framework, or publishing to npm. It is language-agnostic for the UX half and TypeScript/Node-specific for the architecture half — the UX rules still apply if the implementation language differs.

## Core philosophy (always keep in mind)

Modern CLIs are **human-first**: a text UI a person uses directly, not just a machine interface for scripts. Design for the human first, but stay composable so the tool is a well-behaved part of a larger pipeline — these two goals are compatible, not opposed.

Five principles to weigh on every decision:

- **Consistency** — follow existing terminal conventions (flag names, exit codes, stdout/stderr split) so the tool is guessable. Break a convention only with intention, when it demonstrably helps usability.
- **Say just enough** — silence makes a long-running command look broken; a wall of debug output buries what matters. Aim for the middle.
- **Discoverability** — compensate for the lack of a GUI with good help text, examples, "did you mean" suggestions, and next-step hints.
- **Conversation** — users interact through a loop of try → error → fix. Make errors corrective, surface intermediate state, confirm before scary actions.
- **Robustness + empathy** — handle bad input gracefully, prefer idempotency, never dump raw stack traces at users, and make the user feel the tool is on their side.

## The non-negotiable basics

Get these wrong and the tool is broken or a bad CLI citizen. Verify all four on every CLI:

1. **Use an argument-parsing library** — don't hand-roll parsing. (Node: Commander, yargs, oclif, clipanion — see `references/frameworks.md`.)
2. **Exit codes** — `0` on success, non-zero on failure; map important failure modes to distinct non-zero codes. Scripts and CI depend on this.
3. **stdout = results** — primary output and anything machine-readable goes to stdout (that's where pipes read from).
4. **stderr = messaging** — logs, progress, errors go to stderr, so piping the real output downstream still works.

## How to use this skill

1. **Identify which half (or both) the task touches.** Designing output/flags/help/errors → UX half. Structuring code, parsing, build, tests → architecture half. Most real tasks touch both.
2. **Always apply the four basics above** regardless of task.
3. **Load the relevant reference file(s)** for concrete rules and examples:

   - `references/ux-guidelines.md` — help text, output (TTY/JSON/color/paging), error messages, arguments vs flags + standard flag names, interactivity & confirmation, configuration precedence, environment variables, subcommands, naming, distribution UX. **Read this for any task about what the user sees or types.**
   - `references/architecture-ts.md` — thin-command/fat-core layering, project structure, layer rules, type safety (strict + Zod at the boundary), build & distribution (bin/shebang, esbuild bundling, ESM, `files` field), cross-platform path handling, CLI behavior contract, startup performance (fast-paths, lazy loading, build-time gates), testing strategy. **Read this for any task about how the code is organized in TypeScript/Node.**
   - `references/frameworks.md` — Commander vs yargs vs oclif vs clipanion: tradeoffs, startup cost, when to pick which, and the pragmatic default stack. **Read this when choosing or comparing a framework.**
   - `references/checklist.md` — a fast review checklist covering both halves. **Read this when reviewing an existing CLI or doing a final pass.**

4. **When reviewing existing code**, walk `references/checklist.md` and report concrete gaps with the fix, not just "this is wrong."

## The one architectural rule that matters most

If you take only one thing from the architecture half: keep commands thin and the core fat. A command file does exactly three things — parse args/flags, call a core function, format the result for the terminal. Everything else (business rules, calculations, talking to APIs/DB/filesystem) lives in a `core` layer that knows nothing about argv, the parsing framework, or `console`.

This is what makes the logic unit-testable without spawning a process, and reusable unchanged behind other entry points — a library export, an HTTP handler, or an MCP server. Logic welded into command handlers can only ever be a CLI and is painful to test. `references/architecture-ts.md` has the full structure.
