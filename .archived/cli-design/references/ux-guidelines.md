# UX & Interface Guidelines

Concrete rules for what the user sees and types. Grounded in the Command Line Interface Guidelines (clig.dev), the Heroku CLI Style Guide, and 12 Factor CLI Apps. Language-agnostic — applies regardless of implementation language.

## Contents
- [Help text](#help-text)
- [Documentation](#documentation)
- [Output](#output)
- [Tables](#tables)
- [Errors](#errors)
- [Arguments and flags](#arguments-and-flags)
- [Secrets](#secrets)
- [Interactivity and confirmation](#interactivity-and-confirmation)
- [Subcommands](#subcommands)
- [Robustness and responsiveness](#robustness-and-responsiveness)
- [Signals and Ctrl-C](#signals-and-ctrl-c)
- [Configuration](#configuration)
- [Environment variables](#environment-variables)
- [Future-proofing](#future-proofing)
- [Naming](#naming)
- [Distribution UX](#distribution-ux)

## Help text

- Show help on `-h` and `--help`, at every level (top-level and each subcommand). You should be able to append `-h` to anything and get help. Don't overload `-h` for any other meaning. For git-like tools, `myapp help sub` should also work.
- When a command needs arguments but is run with none, show **concise** help: a one-line description, one or two example invocations, the main flags, and a pointer to `--help`. (Exception: tools that are interactive by default, like `npm init`.)
- **Lead with examples.** Users reach for examples before prose — they're the most-used part of help. Show the common, slightly-complex invocations first; tell a story building toward advanced use. If there are many examples, move them to a cheat-sheet command or a web page rather than bloating help.
- Display the most common flags/commands first, grouped logically (the way `git help` groups "start a working area" / "work on the current change"). It's fine to have many flags; surface the important ones at the top.
- Use light formatting (bold section headings: USAGE, OPTIONS, EXAMPLES) for scannability — but emit it terminal-independently so piping through a pager doesn't dump escape characters.
- If the user mistypes and you can guess intent, **suggest** the correction ("Did you mean `ps`?"). Don't silently run the guessed command: a typo can also be a logic error, and auto-correcting both hides the real mistake and commits you to supporting the wrong syntax forever.
- Put a support path (website/GitHub issues link) in top-level help, and link to web docs for subcommands where deeper explanation exists.
- If the command expects piped input and stdin is an interactive terminal, print help and quit instead of hanging silently like `cat`.
- Ship **shell completion** for a CLI with a real command surface — it's help the user never has to ask for.
- `--version` should print more than a bare number: include version plus useful diagnostics (platform, runtime version, install channel). Send the version string as the `User-Agent` on API calls so server-side debugging can correlate.

## Documentation

Help text gives an immediate sense of what the tool does; documentation is the full detail — what it's for, what it isn't, how everything works.

- Provide **web docs** (searchable, linkable — the most inclusive format).
- Provide **terminal docs** (fast, version-matched, offline).
- Consider **man pages** — many users reflexively run `man mycmd`. Tools like `ronn` can generate both man pages and web docs from one source. Since `man` isn't everywhere, also expose terminal docs through the tool itself (e.g. `npm help ls`).

## Output

- **Human-readable is the priority; machine-readable second.** The simplest heuristic for "is a human reading this stream" is whether it's a TTY — check stdout and stderr independently. (Node: `process.stdout.isTTY`.) Adapt formatting accordingly.
- **Stay composable.** Default to line-based text a user can pipe into `grep`/`awk` and get what they expect. "Expect the output of every program to become the input to another."
- **`--json`** — emit structured JSON for complex data, so it pipes into `jq` or web services via `curl`. Treat it as a parallel rendering path, not a post-hoc serialization of the human text — JSON output can and often should carry *more* fields than the human view (raw timestamps, full lists, IDs).
- **`--plain`** — if a rich human layout (multi-line cells, wrapping) breaks the one-record-per-line expectation, offer `--plain` for one record per line.
- **Show success output, but briefly.** Total silence makes a slow command look hung; a wall of text buries the point. Err toward less. Provide `-q`/`--quiet` to suppress non-essential output in scripts.
- **When you change state, say so.** Report what happened and the new state (cf. `git push` / `git status`), especially when the result doesn't map directly to what was requested.
- **Make current state easy to inspect** when the tool does complex, non-filesystem-visible state changes.
- **Suggest next commands** when commands form a workflow — it teaches the tool and aids discovery.
- **Make boundary-crossing actions explicit** — reading/writing files the user didn't pass, or talking to a remote server, should be visible, not silent.
- **Color with intention.** Reserve red/yellow for errors/warnings; use a restrained palette elsewhere — when everything is colored, color means nothing. **Disable color** when: not a TTY, `NO_COLOR` is set and non-empty, `TERM=dumb`, or `--no-color` is passed. Consider a `MYAPP_NO_COLOR` escape hatch.
- **No animations/progress bars when stdout isn't a terminal** — otherwise CI logs fill with garbage.
- **Page long output** (e.g. pipe to `less -FIRX`) only when stdin/stdout is an interactive terminal. `-FIRX`: don't page if it fits one screen, case-insensitive search, keep color, leave content on screen on quit.
- **Don't treat stderr as a log file by default** — no `ERR`/`WARN` labels or extra context unless in verbose mode. Hide developer-only diagnostics behind verbose mode.

## Tables

Tabular output has its own rules (from the Heroku style guide and 12 Factor CLI Apps), all serving one goal: every row is a complete, independent record so `mytool list | grep foo | wc -l` works.

- One row = one record. No border characters, no `=====` section banners — borders are noise for humans and a pain for parsers.
- Show a few high-value columns by default; offer `--columns` to customize.
- Truncate wide cells by default for readability; offer `--no-truncate`.
- Show headers by default; offer `--no-headers` for scripting.
- When tables grow long or wide, point users at `--json` (and `jq`) rather than cramming everything in.

## Errors

Errors are one of the top reasons users consult docs — turn the error itself into the documentation.

- **Rewrite expected errors for humans.** Catch them and explain the fix conversationally. The full anatomy, in order: **code → title → description → fix → URL**:

  ```
  Error: EPERM - Invalid permissions on myfile.out
  Cannot write to myfile.out, file does not have write permissions.
  Fix with: chmod +w myfile.out
  https://github.com/myorg/myapp/issues
  ```

  Not every error needs all five parts, but fix-it guidance is the part users actually need — include it whenever a fix is knowable.
- **Give recurring errors a stable, documented code** (e.g. `MYAPP_E_AUTH_001`) users can search docs/issues for. Distinct from the process exit code — the in-message code identifies *which* failure, the exit code signals *that* it failed.
- **Signal-to-noise is crucial.** More irrelevant output = slower diagnosis. Group many same-type errors under one explanatory header instead of printing dozens of near-identical lines.
- **Put the most important info last** — the eye lands at the end of output, and on red text. Use red sparingly and intentionally.
- **For unexpected errors**, provide debug/traceback info and clear instructions for filing a bug — pre-populate a bug-report URL with version and context where you can. Consider writing the debug log to a file (timestamped, ANSI-stripped, size-capped) rather than flooding the terminal; gate the full traceback behind `--verbose` or a `DEBUG` env var.

## Arguments and flags

Terminology: *arguments* (args) are positional (`cp foo bar` — order matters); *flags* are named (`-r`, `--recursive`, `--file foo.txt`) and order-independent.

- **Prefer flags to positional args.** Slightly more typing, much clearer, and easier to extend without breaking existing behavior or creating ambiguity. Exception: a common primary action where brevity is worth memorizing (`cp <source> <destination>`).
- **Rule of thumb: one *kind* of positional arg is fine, two kinds is suspect, three is wrong.** Multiple args of the *same* kind are fine — `rm file1 file2 file3`, which also makes globbing work (`rm *.txt`).
- **Always provide a long form** for every flag (`-h` *and* `--help`) — long forms are self-documenting in scripts.
- **Reserve single-letter flags for genuinely common options**, especially at top level, so you don't pollute the short-flag namespace and end up with awkward letters later.
- **Use standard flag names** so users can guess them:

  | Flag | Meaning |
  |------|---------|
  | `-a`, `--all` | all |
  | `-d`, `--debug` | debug output |
  | `-f`, `--force` | force; skip confirmation (useful in scripts) |
  | `-h`, `--help` | help — and *only* help |
  | `--json` | JSON output |
  | `-n`, `--dry-run` | describe changes without performing them |
  | `--no-input` | disable all prompting |
  | `-o`, `--output` | output file |
  | `-p`, `--port` | port |
  | `-q`, `--quiet` | less output |
  | `-u`, `--user` | user |
  | `--version` | version |
  | `-v` | verbose *or* version — pick one to avoid ambiguity |

- **Make the default right for most users.** Most won't find the perfect flag and remember to use it; if it isn't the default, most users get the worse experience.
- **Keep flags order-independent**, including relative to subcommands where the parser allows — "this flag only works before the subcommand" rules fight how users actually edit their last command.
- **If a flag's value is optional, accept an explicit word like `none`** (`ssh -F none`) rather than a blank value — blank values make flag-vs-arg parsing ambiguous.
- **Honor `--` as end-of-options.** Everything after `--` stops being parsed as flags and is passed through verbatim — essential when the tool forwards args to a subprocess (`mytool run -- --port 8080`).
- **Accept `-` as a stdin filename** wherever a file argument makes sense, so the tool composes in pipes (`cat data | mytool process -`).

## Secrets

The most-missed rule in CLI design: **never accept secrets via flags, and never read them from environment variables.**

- A `--password` flag leaks into `ps` output for every user on the machine and into shell history. `--password $(< secret.txt)` leaks the same way — the shell expands it before the process starts.
- Env vars leak too: they're inherited by every child process, dumped into logs and crash reports, readable via `docker inspect` and `systemctl show`.
- Accept secrets only via: a file path (`--password-file`), stdin, the OS keychain (see `user-data-storage.md`), or a secret-management service.
- Never print full tokens in any output, including debug logs; never let them land in cache, backups, or log files.

## Interactivity and confirmation

- **Prompt for missing input** when a required arg/flag isn't supplied — but only when stdin is an interactive terminal (TTY). In a script or CI, a prompt just hangs.
- **Never *require* a prompt.** Always allow passing the value via flag/arg. If stdin is not a TTY, or `--no-input` is passed, skip prompting — and on missing input, fail with a message naming the exact flag to pass.
- **Don't echo passwords** when prompting — disable terminal echo.
- **Scale confirmation friction to destructiveness:**
  - *Mild* (delete one local file, small reversible change): `y/n` prompt or no confirmation at all — if the command is literally named `delete`, asking again may be noise.
  - *Moderate* (delete a directory, bulk modification, remote deletion): `y/n` prompt, and offer `--dry-run` so users can preview.
  - *Severe* (delete a whole project/server/remote resource): make accidental confirmation hard — require typing the resource's name. For scripts, accept `--confirm="name-of-thing"`. Watch for non-obvious severe paths: changing a config from 10 instances to 1 implicitly destroys 9.
  - All tiers: `-f`/`--force` (or `--confirm`) bypasses for automation.
- **Let the user escape.** Make quitting obvious; keep Ctrl-C working even during network I/O (see [Signals](#signals-and-ctrl-c)).

## Subcommands

- For `git`-like multi-tool CLIs, make help work at every level: `myapp help`, `myapp help sub`, `myapp sub --help`, `myapp sub -h`.
- Keep subcommand naming consistent: pick `noun verb` or `verb noun` and stick to it across the whole tool (e.g. `docker container ls`, `git remote add`); use the same verbs across different nouns. Ambiguous or inconsistent grammar is a common source of friction.
- Avoid ambiguous or similar names — don't ship both `update` and `upgrade`; disambiguate with extra words.
- **No arbitrary abbreviations** (`i` for `install`) and **no catch-all subcommand** that routes unrecognized input somewhere. Both permanently lock the namespace: users script the abbreviations, and any new command can change the meaning of existing invocations. Explicit, stable aliases are fine.
- Group related subcommands; surface the common ones first in help.

## Robustness and responsiveness

- **Validate input early; fail before changing state.** Check what you received immediately, with an understandable message — not halfway through a mutation.
- **Responsiveness beats raw speed: print something within ~100 ms.** A tool that immediately says what it's doing *feels* faster than a silent faster one.
- **Print something before any network request** — otherwise a slow network looks like a hang.
- **Show progress for anything over a few seconds**; animate on a TTY to reassure. Hide detailed logs behind the progress display on success, but surface them on failure — the user needs them exactly then.
- **Network operations get timeouts** — sensible defaults, configurable, never hang indefinitely.
- **Design idempotent / crash-only / recoverable**: a failed or interrupted run should be resumable by pressing up-arrow + enter. Avoid cleanup *requirements*; assume any run may be killed before cleanup happens (see [Signals](#signals-and-ctrl-c)).
- **Anticipate misuse**: scripts wrapping the tool, flaky networks, two instances running at once, case-insensitive filesystems on macOS.
- User-perceived startup budget (from 12 Factor CLI Apps): under 100 ms feels instant; **100–500 ms is the realistic target for Node**; beyond ~2 s users avoid the tool. Engineering techniques for hitting this live in `architecture.md` (startup performance).

## Signals and Ctrl-C

- On SIGINT (Ctrl-C): **exit as fast as possible**, and print a message *immediately* — before starting any cleanup — so the user knows the keypress registered.
- Put a **timeout on cleanup** so it can't hang forever.
- **A second Ctrl-C skips cleanup and exits immediately** — and tell the user that's what it will do, especially mid-destructive-operation (the Docker Compose model: "Gracefully stopping... (press Ctrl+C again to force)").
- Handle **SIGTERM** the same way — it's what Docker, Kubernetes, systemd, and CI send.
- Design so skipped cleanup is survivable: the next run tolerates leftover state or cleans it up (crash-only design).

## Configuration

Three kinds of configuration, each with the right home:

| Kind | Examples | Mechanism |
|---|---|---|
| Varies per invocation | `--dry-run`, debug level | Flags |
| Stable per user/machine | proxy, color preference, tool paths | Env vars (paired with flags) |
| Stable per project, shared with the team | provider, model, project structure | Version-controlled config file |

Resolve in layers, later sources overriding earlier ones:

```
system config  <  user config  <  project config  <  environment variables  <  flags
```

This precedence is predictable and lets users set durable defaults in a file, override per-environment via env vars, and override per-invocation via flags. Document it. (For where each file lives on disk, see `user-data-storage.md`.)

- Follow the **XDG Base Directory spec** for user-level config (`~/.config/myapp`) to reduce home-directory dotfile sprawl.
- Get explicit consent before modifying config files you don't own (shell profiles, system files); prefer creating new files over appending.

## Environment variables

- Respect cross-tool standards: `NO_COLOR`, `FORCE_COLOR`, `TERM`, `DEBUG`, and where relevant `PAGER`, `EDITOR`, `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, `TMPDIR`.
- Namespace your own variables with a prefix (`MYAPP_*`) to avoid collisions; uppercase with underscores; keep values single-line (multi-line breaks `env`).
- Don't hide important configuration *only* in env vars — they're invisible and easy to forget; pair them with flags and/or config-file keys.
- A project-local `.env` file is fine to read for per-project values, but it's a dev convention, not a config system: no version history for most setups, strings only, and a magnet for secrets. Don't make it the primary config surface, and never *write* tool state into it.
- Never read secrets from env vars — see [Secrets](#secrets).

## Future-proofing

Subcommands, arguments, flags, config keys, and env vars are all **public interface** — people script against them, and those scripts break silently.

- **Prefer additive change**: add a new flag rather than changing what an existing flag means.
- **Deprecate gracefully**: when a deprecated form is used, warn in the output with concrete migration instructions; keep the deprecation period long; stop warning once the user has migrated.
- **Human-readable output is allowed to change** — that's how you iterate on UX. `--json` and `--plain` output are the stability contract; point script and agent authors at them explicitly.
- Avoid decisions that permanently constrain you: implicit abbreviations and catch-all commands (see [Subcommands](#subcommands)), and hard dependencies on services that may not outlive the tool.

## Naming

- Command names: short, lowercase, memorable, easy to type — `curl` good, `DownloadURL` bad — and not clashing with common existing commands. Reserve the very shortest names for tools used constantly.
- Be consistent in casing and word order across commands and flags. Consistency is what lets users guess correctly.

## Distribution UX

- Make installation a one-liner where possible and document it prominently. Make **uninstallation effortless** and document it at the end of the install docs — uninstall intent often follows install immediately.
- Ship `--version` and make upgrade guidance discoverable.
- Provide a clear support/feedback path in help output.
- **Any telemetry/analytics is strict opt-in.** Ask for explicit consent, say what's collected, and provide a documented way to turn it off and to disable it non-interactively (env var/flag) for CI.
