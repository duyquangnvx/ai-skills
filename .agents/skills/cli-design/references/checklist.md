# CLI Review Checklist

A fast pass for designing a new CLI or reviewing an existing one. When reviewing, report each gap with the concrete fix, not just a pass/fail. Group findings under these headings.

## Non-negotiable basics (must all pass)
- [ ] Uses an argument-parsing library (not hand-rolled).
- [ ] Exit code `0` on success, non-zero on failure; important failure modes mapped to distinct codes.
- [ ] Results and machine-readable output go to **stdout**.
- [ ] Logs, progress, and errors go to **stderr**.
- [ ] `-h`/`--help` work at every level; `--version` exists (with useful diagnostics, not just a number).

## Help & discoverability
- [ ] Concise help shown when a command needs args but is run with none.
- [ ] Help leads with examples (common, slightly-complex first).
- [ ] Common flags/commands surfaced first; light scannable formatting.
- [ ] "Did you mean…?" suggestion on likely typos (without silently auto-running).
- [ ] Support/feedback path and web-docs link present; shell completion for a real command surface.

## Output
- [ ] Human-readable by default; adapts on `process.stdout.isTTY`.
- [ ] `--json` for structured output (a parallel rendering path, not serialized human text); `--plain` if rich layout breaks line-based parsing.
- [ ] Brief success output (not silent, not a wall); `-q`/`--quiet` available.
- [ ] State changes are reported; current state is inspectable; next commands suggested in workflows.
- [ ] Tables: one row = one record, no borders/banners; truncation and headers toggleable.
- [ ] Color is intentional and disabled on non-TTY / `NO_COLOR` / `TERM=dumb` / `--no-color`.
- [ ] No animations/progress bars when stdout isn't a terminal.
- [ ] Long output paged only when interactive.

## Errors
- [ ] Expected errors rewritten for humans with the fix suggested (code → title → description → fix → URL).
- [ ] Good signal-to-noise; similar errors grouped; key info last.
- [ ] Unexpected errors give debug info + a clear path to file a bug (no raw stack traces by default; full trace behind `--verbose`/`DEBUG`).
- [ ] Recurring errors carry a stable, documented code users can look up (distinct from the exit code).

## Arguments & flags
- [ ] Flags preferred over positional args (except a brevity-justified primary action); at most one *kind* of positional arg.
- [ ] Every flag has a long form; single-letter flags reserved for common ones.
- [ ] Standard flag names used (`--force`, `--dry-run`, `--output`, `--quiet`, etc.).
- [ ] Defaults are right for most users; flags order-independent.
- [ ] `--` ends option parsing (passthrough to subprocess); `-` accepted as a stdin filename where it composes.
- [ ] **No secrets via flags or env vars** — file path, stdin, or keychain instead; tokens never printed or logged.

## Interactivity & config
- [ ] Prompts for missing input but never *requires* a prompt; respects non-TTY and `--no-input`; names the missing flag on failure.
- [ ] Confirmation scaled to destructiveness (y/n → `--dry-run` offered → type-the-name / `--confirm="name"`); `--force` bypass for automation.
- [ ] Password prompts don't echo.
- [ ] Config precedence: system < user < project < env vars < flags, and documented.
- [ ] Own env vars namespaced (`MYAPP_*`); cross-tool standards respected (`NO_COLOR`, `EDITOR`, proxies…).
- [ ] Any telemetry/analytics is strict opt-in with explicit consent and a non-interactive off switch.

## Robustness & signals
- [ ] Input validated early; fails before changing state.
- [ ] Something printed within ~100 ms; network calls announced before they start; progress shown for long tasks.
- [ ] Network operations have configurable timeouts with sensible defaults.
- [ ] Idempotent / crash-only: an interrupted run can be re-run and resume.
- [ ] SIGINT **and** SIGTERM handled: immediate message, cleanup bounded by an `.unref()`ed timeout, second Ctrl-C exits immediately (and says so), terminal state restored.

## Future-proofing
- [ ] Subcommands, flags, config keys, and env vars treated as public interface; changes are additive.
- [ ] Deprecations warn on use with migration instructions, over a long period.
- [ ] `--json`/`--plain` documented as the stable formats for scripts; human output free to evolve.
- [ ] No arbitrary subcommand abbreviations; no catch-all subcommand.

## Naming & subcommands
- [ ] Command name short, lowercase, no clash with common commands.
- [ ] Consistent casing and `noun verb` / `verb noun` grammar across subcommands; `noun verb` (resource-first) when there are many resources; no `update`-vs-`upgrade` ambiguity.
- [ ] Command tree shallow (regroup beyond three levels); one file per command mirroring the tree.
- [ ] Help works at every subcommand level.

## Architecture (TypeScript/Node)
- [ ] Layout is `cli.ts` + `commands/` + `core/` (`services`/`domain`) + `adapters/` + `ui/` + `lib/`.
- [ ] Dependency direction holds: `commands/` → `core/` → `adapters/` (interfaces); `core/` never imports `commands/`/`ui`/the framework; `core/domain` never imports `adapters/`.
- [ ] Boundaries enforced in CI (dependency-cruiser / eslint-plugin-boundaries), not just by convention.
- [ ] Thin commands / fat core: commands only parse → delegate → format.
- [ ] Core has no argv, no framework, no `console`, no `process.exit`.
- [ ] Commands receive an injected context (streams, env, cwd, reporter) instead of touching `process` globals.
- [ ] One reporter module owns all output (human/`--json`/quiet/color/TTY), picked once at startup.
- [ ] `ui/` split into shared primitives and per-command views; views are pure one-shot functions rendering through the reporter, repeated output extracted into primitives.
- [ ] Error boundary sets `process.exitCode` (not `process.exit()`); typed domain errors mapped to exit codes in one place.
- [ ] I/O isolated in `adapters/` behind interfaces; nondeterminism (clock/random/uuid) wrapped.
- [ ] `strict` on; args/flags validated with Zod/Valibot at the boundary.
- [ ] `bin` + `#!/usr/bin/env node` shebang; bundled (tsdown/esbuild); ESM-only unless shipping a library; `files` field limits published output; Node floor declared in `engines`.
- [ ] Commands lazy-loaded if there are many; pre-framework fast-path for `--version`/subprocess modes; startup budget measured for hot-loop tools.
- [ ] Cross-platform paths (`path.join`, no shell/`/tmp` assumptions); runs on Windows.
- [ ] Config/env read inside an explicit init function, not at module top level; flag/error/config wiring centralized on a base command or one error boundary.

## Persisting user data (if it stores anything)
- [ ] Global vs per-project separated and mirrored; disposable data (cache) in a clearly-named, deletable subdir.
- [ ] Credentials in the OS keychain (restricted-permission file only as fallback), never in cache/backups/logs.
- [ ] Root location overridable via env var; path logic centralized in one module.

## Testing
- [ ] Heavy unit coverage on `core/` (`core/services`/`core/domain`) with fake adapters.
- [ ] Command tests run with an injected fake context (in-memory streams), asserting output + exit behavior — no subprocess.
- [ ] Snapshot tests on `ui/` output where stability matters (`--help` snapshot catches interface breaks).
- [ ] Thin end-to-end smoke test against the built binary (shebang, `bin` wiring, real exit codes).
