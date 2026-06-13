---
name: cli-design
description: This skill should be used when designing or building a command-line interface (CLI), especially in TypeScript/Node.js. It encodes verified 2025-2026 best practices — human-first design, stdout/stderr stream discipline, TTY detection, flag/prompt/config conventions, XDG directories, signal handling — plus current ecosystem picks (parser, prompts, colors, bundler, ESM, single-binary). Trigger on "build a CLI", "design a CLI", "CLI tool", "command-line app", or when reviewing CLI UX/behavior.
---

# CLI Design

Design and build CLIs that are pleasant for humans and reliable for scripts. All guidance below was distilled from adversarially verified research (2 rounds, 47 sources, 46 confirmed claims) anchored in three canonical sources: [clig.dev](https://clig.dev/), [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46), and the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/).

## Core principle

Design human-first, but keep every behavior machine-consumable. The switch between the two modes is **TTY detection** — never a guess, never a config default. A CLI that prints colors into a pipe or hangs on a prompt in CI is broken.

## Workflow

When designing or implementing a CLI:

1. **Define the command surface.** Prefer named flags over positional arguments. Allow at most one *category* of positional argument (2 categories are suspect, 3 are never acceptable). Support `--` to stop flag parsing.
2. **Apply stream discipline.** Primary/machine-readable output → stdout. Logs, errors, warnings, progress → stderr. Verify by mentally piping the command: `mycli ... | jq` must receive only data.
3. **Gate all decoration on TTY.** Disable colors when: stream is not a TTY, `NO_COLOR` is set (non-empty), `TERM=dumb`, or `--no-color` is passed. Disable spinners/animations when output is not a TTY. Check the correct file descriptor (stderr's own isatty for stderr coloring).
4. **Make every prompt optional.** Prompt only when stdin is a TTY, and always provide a flag/argument equivalent so scripts never block. Confirm destructive actions, but allow bypass (e.g. `--confirm="name"`).
5. **Resolve config in standard order:** flags > environment variables > project-level config > user-level config > system-wide config. Place files per XDG (`~/.config/<tool>/`, not `~/.<tool>`).
6. **Handle signals.** Installing a `SIGINT`/`SIGTERM` listener in Node.js removes the default exit behavior — the handler must clean up and call `process.exit(128 + n)` itself.
7. **Pick the stack from verified current state** — see `references/typescript-stack.md`. Key traps as of 2026: tsup is unmaintained (use tsdown), legacy `inquirer` is frozen (use `@inquirer/prompts`), ESM-only is now safe (`require(esm)` stable on all supported LTS), chalk has lighter replacements (`util.styleText` is built in).

For the full convention details with verbatim source quotes, read `references/design-conventions.md`. For ecosystem comparisons, version facts, and packaging/single-binary guidance, read `references/typescript-stack.md`.

## Review checklist

Before shipping a CLI (or when reviewing one), verify:

- [ ] Data on stdout, messaging on stderr — `cmd | consumer` works
- [ ] Colors/spinners off when not a TTY, `NO_COLOR`, `TERM=dumb`, or `--no-color`
- [ ] No required prompts; every interactive input has a flag equivalent; prompts only when stdin is a TTY
- [ ] Destructive actions confirmed, bypassable by flag
- [ ] Flags preferred over positionals; `--` supported
- [ ] Config precedence flags > env > project > user > system; files under XDG paths
- [ ] SIGINT/SIGTERM handled with cleanup and correct exit code (`128 + signal`)
- [ ] Exit code 0 only on success
- [ ] If telemetry exists: documented, respects `DO_NOT_TRACK`, plus a tool-specific opt-out variable
- [ ] Command handlers lazy-imported; entry point stays thin (startup time)

## Scope

This skill covers CLI *design and behavior* plus stack selection. Detailed testing patterns (TTY mocking, execa integration tests, exit-code assertions), `bin`/shebang/npx publishing mechanics, and @clack/prompts-vs-ink comparison are out of scope — they were not covered by verified research. When those topics come up, verify against current primary docs rather than assuming.
