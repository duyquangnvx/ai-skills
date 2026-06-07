# User & Workspace Data Storage

Read this when the CLI must persist anything for the user — config, credentials, projects, cache, backups, logs. The goal is a layout that respects OS conventions, keeps secrets safe, and stays easy to manage.

## The invariants — get these right regardless of layout

Layout style is a choice (see next section), but these four hold either way:

1. **Separate global from per-project, and mirror their structure.** Global data (applies across all projects) lives in the user's home area; per-project data lives inside that project directory, like `git` keeps `.git/`. Use the *same* subdirectory names in both scopes so one mental model applies everywhere, with project-scope overriding global-scope.
2. **Keep disposable data in a clearly-named subdirectory.** Cache and regenerable state (e.g. `cache/`, session transcripts) must be deletable without touching real data. Separability is the requirement — a named subdir is enough; a separate OS location is optional.
3. **Isolate credentials — OS keychain first.** Never default to a plaintext secrets file. Use the OS keychain; fall back to a restricted-permission file only where no keychain exists. Ordinary state may be a plaintext file protected by OS permissions, but secrets must not be.
4. **Make the root location overridable** via an environment variable, so power users and CI can relocate everything.

Do not spread data across many OS directories just because a spec says so. The only thing that buys you over a single well-organized directory is niche (cache on a separate volume, auto-exclusion from some backup tools). Optimize for the invariants above, then pick whichever layout shape fits the tool.

## Choose a layout shape

Two shapes are both legitimate. Pick by the nature of the tool.

### Shape A — Consolidated single directory (default for interactive / stateful / project-aware tools)

One global directory holds everything, with disposable parts as named subdirs. Often paired with a single top-level config file for instant editing.

```
~/.mytool.json            # primary config file — top-level, easy to find/edit
~/.mytool/                # everything else, global scope
  settings.json
  projects/               # per-project session/state, keyed by project path — durable
  cache/                  # disposable, the only thing safe to delete wholesale
  backups/                # durable — a sibling of cache, never inside it
  logs/  debug/           # state
  agents/ hooks/ skills/  # extensible config, mirrored per-project
# credentials -> OS keychain (no secrets file here)
```

Choose this when the tool is something users actively inspect, debug, and reset; when its state (sessions, projects, plugins) is a tightly-coupled whole; and when you want global↔per-project symmetry. Benefits: one place to look (`ls ~/.mytool/`), trivial uninstall/reset (`rm -rf ~/.mytool ~/.mytool.json`), and a per-project directory that can mirror the global one. This symmetry is impossible if global data is scattered across OS dirs — which is the main reason rich dev tools consolidate.

### Shape B — Spread / two-bucket (for simpler or Unix-philosophy tools)

Follow OS-standard locations per data category. Collapse to two buckets unless you have a concrete reason to split further: a **durable bundle** (config + data + backups + logs) and a separate **cache**.

```
~/.local/share/mytool/    # durable bundle (Linux; map per-OS, see table)
  config.json  data/  backups/  logs/
~/.cache/mytool/          # disposable, the only thing safe to nuke wholesale
# credentials -> OS keychain
```

Choose this for smaller CLIs, tools targeting tidy XDG-compliant Linux setups, or when the cache is large/volatile enough to benefit from living on a separate volume.

## Cross-platform locations (Shape B) — use a library, don't hardcode

Never write per-OS path logic by hand. Use a paths library (in Node, `env-paths`) that returns the right location per platform. The conventions:

| Category | Linux | Windows | macOS |
|---|---|---|---|
| config | `~/.config` | `%APPDATA%` | `~/Library/Application Support` |
| data | `~/.local/share` | `%APPDATA%` | `~/Library/Application Support` |
| cache | `~/.cache` | `%LOCALAPPDATA%` | `~/Library/Caches` |
| state | `~/.local/state` | `%LOCALAPPDATA%` | `~/Library/Application Support` |

macOS nuance: paths libraries default to `~/Library/...` (GUI convention), but many dev/devops CLIs use `~/.config` on macOS for cross-platform consistency. Pick `~/Library` for general-audience tools; consider `~/.config` for dev tooling. Make it overridable rather than guessing. Shape A on macOS typically just uses `~/.mytool/` directly, matching the dev-tool norm.

## Global ↔ per-project symmetry and precedence

Mirror the subdirectory layout in both scopes and resolve them as a cascade, later winning:

```
managed/enterprise policy  >  CLI flags  >  env vars  >  project scope  >  global scope  >  built-in defaults
```

Per-project files that are meant to be shared go in version control; personal/local overrides get a separate `*.local.*` file that is gitignored.

## Credentials

A plaintext secrets file exposes tokens to malware, other users on the machine, and leaks via backups or file sharing. Order of preference:

1. **OS keychain** (best) — macOS Keychain, Windows Credential Manager, Linux Secret Service. Use a native binding (in Node, `@napi-rs/keyring`; `keytar` is archived/unmaintained) and a descriptive service name tied to the tool (e.g. `com.you.mytool`), not a generic `api`.
2. **Restricted file** (fallback only where no keychain exists) — write with `0600` permissions, separate from config.

A common real-world pattern: store secrets in the keychain on macOS, and fall back to a permission-restricted file only on Linux/Windows. Regardless of method, never let credentials land in cache, backups, or logs, and never print full tokens in debug output.

## `.env` is a dev convention, not tool storage

`.env` is a project-local, development-time pattern and must be gitignored — it is not where a CLI persists global user config. A CLI should *read* config with clear precedence and never *write* its state into a `.env` file.

## Centralize path resolution in one module

Put all path logic in a single `lib/paths.ts` so the rest of the app references named paths, never hardcoded strings. This hides the layout choice (Shape A or B) and cross-platform differences behind one swappable module:

```typescript
// lib/paths.ts — single source of truth for where things live
import { homedir } from "node:os";
import { join } from "node:path";

const root = process.env.MYTOOL_CONFIG_DIR ?? join(homedir(), ".mytool"); // overridable

export const appPaths = {
  config:  join(root, "settings.json"),
  data:    join(root, "data"),
  backups: join(root, "backups"),
  logs:    join(root, "logs"),
  cache:   join(root, "cache"),     // the only directory safe to delete wholesale
};
// credentials are NOT here — they go through a keychain adapter
```

Swap the `root` resolution for an `env-paths`-based one to move from Shape A to Shape B without touching the rest of the app.