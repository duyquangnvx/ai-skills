# UX & Interface Guidelines

Concrete rules for what the user sees and types. Grounded in the Command Line Interface Guidelines (clig.dev). Language-agnostic — applies regardless of implementation language.

## Contents
- [Help text](#help-text)
- [Documentation](#documentation)
- [Output](#output)
- [Errors](#errors)
- [Arguments and flags](#arguments-and-flags)
- [Interactivity](#interactivity)
- [Subcommands](#subcommands)
- [Configuration](#configuration)
- [Environment variables](#environment-variables)
- [Naming](#naming)
- [Distribution UX](#distribution-ux)

## Help text

- Show help on `-h` and `--help`, at every level (top-level and each subcommand). You should be able to append `-h` to anything and get help. Don't overload `-h` for any other meaning.
- When a command needs arguments but is run with none, show **concise** help: a one-line description, one or two example invocations, the main flags, and a pointer to `--help`. (Exception: tools that are interactive by default, like `npm init`.)
- **Lead with examples.** Users reach for examples before prose. Show the common, slightly-complex invocations first; tell a story building toward advanced use. If there are many examples, move them to a cheat-sheet command or a web page rather than bloating help.
- Display the most common flags/commands first. It's fine to have many flags; surface the important ones at the top.
- Use light formatting (bold section headings: USAGE, OPTIONS, EXAMPLES) for scannability — but emit it terminal-independently so piping through a pager doesn't dump escape characters.
- If the user mistypes and you can guess intent, **suggest** the correction ("Did you mean `ps`?"). Don't silently run the guessed command: a typo can also be a logic error, and auto-correcting both hides the real mistake and commits you to supporting the wrong syntax forever.
- Put a support path (website/GitHub issues link) in top-level help, and link to web docs for subcommands where deeper explanation exists.
- If the command expects piped input and stdin is an interactive terminal, print help and quit instead of hanging silently like `cat`.

## Documentation

Help text gives an immediate sense of what the tool does; documentation is the full detail — what it's for, what it isn't, how everything works.

- Provide **web docs** (searchable, linkable — the most inclusive format).
- Provide **terminal docs** (fast, version-matched, offline).
- Consider **man pages** — many users reflexively run `man mycmd`. Tools like `ronn` can generate both man pages and web docs from one source. Since `man` isn't everywhere, also expose terminal docs through the tool itself (e.g. `npm help ls`).

## Output

- **Human-readable is the priority; machine-readable second.** The simplest heuristic for "is a human reading this stream" is whether it's a TTY. (Node: `process.stdout.isTTY`.) Adapt formatting accordingly.
- **Stay composable.** Default to line-based text a user can pipe into `grep`/`awk` and get what they expect. "Expect the output of every program to become the input to another."
- **`--json`** — emit structured JSON for complex data, so it pipes into `jq` or web services via `curl`.
- **`--plain`** — if a rich human layout (multi-line cells, wrapping) breaks the one-record-per-line expectation, offer `--plain` for one record per line.
- **Show success output, but briefly.** Total silence makes a slow command look hung; a wall of text buries the point. Err toward less. Provide `-q`/`--quiet` to suppress non-essential output in scripts.
- **When you change state, say so.** Report what happened and the new state (cf. `git push` / `git status`), especially when the result doesn't map directly to what was requested.
- **Make current state easy to inspect** when the tool does complex, non-filesystem-visible state changes.
- **Suggest next commands** when commands form a workflow — it teaches the tool and aids discovery.
- **Make boundary-crossing actions explicit** — reading/writing files the user didn't pass, or talking to a remote server, should be visible, not silent.
- **Color with intention.** Use it to draw attention (e.g. red for errors); overuse makes color meaningless. **Disable color** when: not a TTY, `NO_COLOR` is set and non-empty, `TERM=dumb`, or `--no-color` is passed. Consider a `MYAPP_NO_COLOR` escape hatch.
- **No animations/progress bars when stdout isn't a terminal** — otherwise CI logs fill with garbage.
- **Page long output** (e.g. pipe to `less -FIRX`) only when stdin/stdout is an interactive terminal. `-FIRX`: don't page if it fits one screen, case-insensitive search, keep color, leave content on screen on quit.
- **Don't treat stderr as a log file by default** — no `ERR`/`WARN` labels or extra context unless in verbose mode. Hide developer-only diagnostics behind verbose mode.

## Errors

Errors are one of the top reasons users consult docs — turn the error itself into the documentation.

- **Rewrite errors for humans.** Catch expected failures and explain the fix conversationally: "Can't write to file.txt. You might need to make it writable: chmod +w file.txt."
- **Signal-to-noise is crucial.** More irrelevant output = slower diagnosis. Group many same-type errors under one header instead of printing dozens of near-identical lines.
- **Put the most important info last** — the eye lands at the end of output, and on red text. Use red sparingly and intentionally.
- **For unexpected errors**, provide debug/traceback info and clear instructions for filing a bug — but consider writing the debug log to a file rather than flooding the terminal. Pre-populate a bug-report URL where you can.
- **Give recurring errors a stable, documented code** (e.g. `MYAPP_E_AUTH_001`) users can search docs/issues for. Distinct from the process exit code — the in-message code identifies *which* failure, the exit code signals *that* it failed.

## Arguments and flags

Terminology: *arguments* (args) are positional (`cp foo bar` — order matters); *flags* are named (`-r`, `--recursive`, `--file foo.txt`) and order-independent.

- **Prefer flags to positional args.** Slightly more typing, much clearer, and easier to extend without breaking existing behavior or creating ambiguity. Exception: a common primary action where brevity is worth memorizing (`cp <source> <destination>`).
- **Two or more positional args for different things is usually a smell** — reach for flags instead (except the brevity-justified primary action above).
- **Multiple args are fine for the same kind of thing** — `rm file1 file2 file3`, which also makes globbing work (`rm *.txt`).
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
- **Honor `--` as end-of-options.** Everything after `--` stops being parsed as flags and is passed through verbatim — essential when the tool forwards args to a subprocess (`mytool run -- --port 8080`).
- **Accept `-` as a stdin filename** wherever a file argument makes sense, so the tool composes in pipes (`cat data | mytool process -`).

## Interactivity

- **Prompt for missing input** when a required arg/flag isn't supplied.
- **Never *require* a prompt.** Always allow passing the value via flag/arg. If stdin is not an interactive terminal, skip prompting and require the flags/args instead (and respect `--no-input`).
- **Confirm before anything dangerous.** Prompt for `y`/`yes` when interactive, or require `-f`/`--force` when not. Scale the friction to the destructiveness (e.g. typing the resource name for truly irreversible actions).

## Subcommands

- For `git`-like multi-tool CLIs, make help work at every level: `myapp help`, `myapp help sub`, `myapp sub --help`, `myapp sub -h`.
- Keep subcommand naming consistent: pick `noun verb` or `verb noun` and stick to it across the whole tool (e.g. `docker container ls`, `git remote add`). Ambiguous or inconsistent subcommand grammar is a common source of friction.
- Group related subcommands; surface the common ones first in help.

## Configuration

Resolve configuration in layers, later sources overriding earlier ones:

```
built-in defaults  <  config file  <  environment variables  <  command-line flags
```

This precedence is predictable and lets users set durable defaults in a file, override per-environment via env vars, and override per-invocation via flags. Document the precedence.

## Environment variables

- Respect cross-tool standards: `NO_COLOR`, `TERM`, and where relevant `PAGER`, `EDITOR`, `http_proxy`/`https_proxy`.
- Namespace your own variables with a prefix (`MYAPP_*`) to avoid collisions.
- Don't hide important configuration *only* in env vars — they're invisible and easy to forget; pair them with flags and/or config-file keys.

## Naming

- Command names: short, lowercase, memorable, easy to type, and not clashing with common existing commands.
- Be consistent in casing and word order across commands and flags. Consistency is what lets users guess correctly.

## Distribution UX

- Make installation a one-liner where possible and document it prominently.
- Ship `--version` and make upgrade guidance discoverable.
- Provide a clear support/feedback path in help output.
- **Any telemetry/analytics is strict opt-in.** Ask for explicit consent, say what's collected, and provide a documented way to turn it off and to disable it non-interactively (env var/flag) for CI.
