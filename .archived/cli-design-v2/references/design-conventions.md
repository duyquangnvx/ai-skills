# CLI Design Conventions

Detailed conventions with source citations. All claims below passed 3-verifier adversarial verification unless noted. Canonical sources: [clig.dev](https://clig.dev/) ([repo](https://github.com/cli-guidelines/cli-guidelines)), [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46) (jdx — oclif author, ex-Heroku CLI lead), [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/).

Note on force: these guidelines say "should", not "must" — they are widely agreed conventions, not enforced standards.

## Human-first design

> "If a command is going to be used primarily by humans, it should be designed for humans first." — clig.dev

A deliberate departure from the classic UNIX assumption that commands are functions called by other programs. Human-first does NOT conflict with composability — a good CLI does both, switching on TTY detection.

## Stream discipline

- **stdout**: primary output, anything machine-readable — where piping sends data by default.
- **stderr**: log messages, errors, warnings, progress — visible even when stdout is redirected.

> clig.dev: "The primary output for your command should go to stdout... Log messages, errors, and so on should all be sent to stderr."
> 12 Factor (Factor 4): "stdout is for output, stderr is for messaging." Classic example: `curl` prints progress to stderr.

This is the foundation of composability: `mycli list | grep foo > out.txt` only works when streams are separated.

## TTY detection — colors, spinners, animations

Disable colors when ANY of these holds (clig.dev lists exactly these four):

1. stdout/stderr is not a TTY (piped to a file, another process, or CI)
2. `NO_COLOR` env var is set and non-empty ([no-color.org](https://no-color.org) — informal cross-tool standard)
3. `TERM=dumb`
4. The user passed `--no-color`

Also disable spinners and animations when output is not a TTY — clig.dev: "If stdout is not an interactive terminal, don't display any animations" (avoids progress bars becoming "Christmas trees" in CI logs).

Implementation detail: check the right file descriptor — use stderr's own isatty when deciding whether to color stderr; do not infer from stdout.

## Flags vs positional arguments

Prefer named flags. They make commands self-describing and order-independent.

> 12 Factor: "Flags require a bit more typing, but make the CLI much clearer."

Heuristic (jdx): **1 type of positional argument is fine, 2 types are very suspect, 3 are never good.** This counts *categories*, not raw count — `rm file1 file2 file3` is still one type.

The flag parser must accept `--` (POSIX convention): stop parsing flags, pass everything after as raw arguments.

## Interactivity and prompts

- Prompt only when stdin is a TTY.
- **Never require a prompt** — always provide a flag/argument path so the CLI can be scripted.
- Confirm destructive actions (e.g. retype the resource name, like `heroku destroy`), but allow bypass via flag (e.g. `--confirm="name"`).

> clig.dev: "Only use prompts or interactive elements if stdin is an interactive terminal (a TTY)... Never require a prompt. Always provide a way of passing input with flags or arguments... Confirm before doing anything dangerous."

## Configuration precedence

Highest to lowest (clig.dev, Configuration section, verbatim list):

```
1. Command-line flags
2. The running shell's environment variables
3. Project-level configuration (e.g. .env)
4. User-level configuration
5. System-wide configuration
```

## XDG Base Directory

Follow the XDG spec for file locations (yarn, fish, neovim, tmux all do). Defaults when the variable is unset or empty:

| Variable | Default | Purpose |
|---|---|---|
| `XDG_CONFIG_HOME` | `$HOME/.config` | Config |
| `XDG_DATA_HOME` | `$HOME/.local/share` | Data |
| `XDG_STATE_HOME` | `$HOME/.local/state` | State (history, logs) |
| `XDG_CACHE_HOME` | `$HOME/.cache` | Cache (deletable) |

`XDG_*_HOME` (user) takes precedence over `XDG_*_DIRS` (system search paths). Do not dump files into `~/.mycli` — use `~/.config/mycli/`.

## Signal handling (Node.js)

Per [Node.js process docs](https://nodejs.org/api/process.html):

- Register as ordinary process event listeners: `process.on('SIGINT', handle)`. The handler receives the **signal name as its first argument**, so one function can serve both signals.
- On non-Windows, `SIGINT`/`SIGTERM` have default handlers that reset terminal mode and exit with code `128 + signal number`.
- **Installing a listener removes that default behavior** — Node.js no longer exits on its own. The handler must perform cleanup and call `process.exit()` with the proper code.

```ts
function handle(signal: string) {
  // cleanup (temp files, restore terminal state...)
  process.exit(128 + (signal === 'SIGINT' ? 2 : 15))
}
process.on('SIGINT', handle)
process.on('SIGTERM', handle)
```

## Telemetry etiquette

Reference case: GitHub CLI v2.91.0 (April 2026) added usage telemetry with opt-out via both mechanisms ([docs](https://docs.github.com/en/github-cli/github-cli/github-cli-telemetry)):

- `DO_NOT_TRACK=true` — cross-tool convention every CLI should respect
- `GH_TELEMETRY=false` — tool-specific variable, takes precedence over `DO_NOT_TRACK`

Pattern: if a CLI ships telemetry, document it clearly, honor `DO_NOT_TRACK`, and add a tool-specific opt-out variable.
