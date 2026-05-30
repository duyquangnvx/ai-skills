# CLI Review Checklist

A fast pass for designing a new CLI or reviewing an existing one. When reviewing, report each gap with the concrete fix, not just a pass/fail. Group findings under these headings.

## Non-negotiable basics (must all pass)
- [ ] Uses an argument-parsing library (not hand-rolled).
- [ ] Exit code `0` on success, non-zero on failure; important failure modes mapped to distinct codes.
- [ ] Results and machine-readable output go to **stdout**.
- [ ] Logs, progress, and errors go to **stderr**.
- [ ] `-h`/`--help` work at every level; `--version` exists.

## Help & discoverability
- [ ] Concise help shown when a command needs args but is run with none.
- [ ] Help leads with examples (common, slightly-complex first).
- [ ] Common flags/commands surfaced first; light scannable formatting.
- [ ] "Did you mean…?" suggestion on likely typos (without silently auto-running).
- [ ] Support/feedback path and web-docs link present.

## Output
- [ ] Human-readable by default; adapts on `process.stdout.isTTY`.
- [ ] `--json` for structured output; `--plain` if rich layout breaks line-based parsing.
- [ ] Brief success output (not silent, not a wall); `-q`/`--quiet` available.
- [ ] State changes are reported; current state is inspectable.
- [ ] Color is intentional and disabled on non-TTY / `NO_COLOR` / `TERM=dumb` / `--no-color`.
- [ ] No animations/progress bars when stdout isn't a terminal.
- [ ] Long output paged only when interactive.

## Errors
- [ ] Expected errors rewritten for humans with the fix suggested.
- [ ] Good signal-to-noise; similar errors grouped; key info last.
- [ ] Unexpected errors give debug info + a clear path to file a bug (no raw stack traces by default).
- [ ] Recurring errors carry a stable, documented code users can look up (distinct from the exit code).

## Arguments & flags
- [ ] Flags preferred over positional args (except a brevity-justified primary action).
- [ ] Every flag has a long form; single-letter flags reserved for common ones.
- [ ] Standard flag names used (`--force`, `--dry-run`, `--output`, `--quiet`, etc.).
- [ ] Defaults are right for most users.
- [ ] `--` ends option parsing (passthrough to subprocess); `-` accepted as a stdin filename where it composes.

## Interactivity & config
- [ ] Prompts for missing input but never *requires* a prompt; respects non-TTY and `--no-input`.
- [ ] Confirmation (or `--force`) before destructive actions.
- [ ] Config precedence: defaults < file < env vars < flags, and documented.
- [ ] Own env vars namespaced (`MYAPP_*`); cross-tool standards respected.
- [ ] Any telemetry/analytics is strict opt-in with explicit consent and a non-interactive off switch.

## Naming & subcommands
- [ ] Command name short, lowercase, no clash with common commands.
- [ ] Consistent casing and `noun verb` / `verb noun` grammar across subcommands; `noun verb` (resource-first) when there are many resources.
- [ ] Command tree shallow (regroup beyond three levels); one file per command mirroring the tree.
- [ ] Help works at every subcommand level.

## Architecture (TypeScript/Node)
- [ ] Thin commands / fat core: commands only parse → delegate → format.
- [ ] `core/` has no argv, no framework, no `console`, no `process.exit`.
- [ ] I/O isolated in `adapters/` behind interfaces; nondeterminism (clock/random/uuid) wrapped.
- [ ] `strict` on; args/flags validated with Zod/Valibot at the boundary.
- [ ] `bin` + `#!/usr/bin/env node` shebang; bundled with esbuild/tsup; ESM-only unless shipping a library; `files` field limits published output.
- [ ] Commands lazy-loaded if there are many; `SIGINT`/`SIGTERM` cleaned up.
- [ ] Pre-framework fast-path for `--version`/subprocess modes; startup budget measured for hot-loop tools.
- [ ] Cross-platform paths (`path.join`, no shell/`/tmp` assumptions); runs on Windows.
- [ ] Config/env read inside an explicit init function, not at module top level; flag/error/config wiring centralized on a base command or one error boundary.

## Persisting user data (if it stores anything)
- [ ] Global vs per-project separated and mirrored; disposable data (cache) in a clearly-named, deletable subdir.
- [ ] Credentials in the OS keychain (restricted-permission file only as fallback), never in cache/backups/logs.
- [ ] Root location overridable via env var; path logic centralized in one module.

## Testing
- [ ] Heavy unit coverage on `core/` with fake adapters.
- [ ] Integration tests invoke the parser with argv and assert result + exit behavior.
- [ ] Snapshot tests on `ui/` output where stability matters.
- [ ] Thin end-to-end smoke test against the built binary (shebang, `bin` wiring, real exit codes).
