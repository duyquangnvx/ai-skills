# User & Workspace Data Storage

Read this when the CLI must persist anything for the user — config, credentials, projects, cache, backups, logs. The goal is a layout that survives OS conventions, keeps secrets safe, and stays easy to manage.

## First, separate the two kinds of data

These are different and must not share a directory:

- **Global tool data** — belongs to the user's *installation* of the tool (config, data, cache, state, credentials). Lives in OS-standard locations, never in the current working directory.
- **Per-project / workspace data** — belongs to the *project the user is working in* (project-local settings, local state). Lives inside that project directory, like `git` keeps `.git/`.

A common mistake is dumping both into one `~/.myapp/` folder. Sort each piece of data into one of these two first.

## Categorize global data by lifecycle

Classify every file by the "delete test" — what happens if it disappears:

| Category | Delete test |
|---|---|
| config | User must reconfigure |
| data | Real loss — databases, project registry, **backups** |
| state | Inconvenient but recoverable — logs, history, recent files |
| cache | No loss — the app regenerates it |

The single property that justifies splitting directories: **cache must be safely deletable without touching data.** Backups are data, not cache — never put backups in the cache directory or an OS cleaner may wipe them.

## Map paths cross-platform — use a library, don't hardcode

Never write per-OS path logic by hand. Use a paths library (in Node, `env-paths`) that returns the correct config/data/cache/log locations for each platform. The conventions it follows:

| Category | Linux | Windows | macOS |
|---|---|---|---|
| config | `~/.config` | `%APPDATA%` | `~/Library/Application Support` |
| data | `~/.local/share` | `%APPDATA%` | `~/Library/Application Support` |
| cache | `~/.cache` | `%LOCALAPPDATA%` | `~/Library/Caches` |
| state | `~/.local/state` | `%LOCALAPPDATA%` | `~/Library/Application Support` |

macOS nuance: paths libraries default to `~/Library/...` (the GUI convention), but many developer/devops CLI tools deliberately use `~/.config` on macOS for cross-platform consistency. Pick `~/Library` for general-audience tools; consider allowing `~/.config` for dev tooling. Make it overridable rather than guessing.

## Don't over-split — collapse to two buckets

Spreading data across four separate directories (config, data, state, cache) buys little beyond the cache property and is genuinely harder to manage. Default to two buckets:

- **Durable bundle** — one app directory holding `config`, `data/`, `backups/`, `logs/` together.
- **Cache** — separate directory, the only thing safe to nuke.

Split config/data/state into truly separate locations only when there's a concrete need (e.g. syncing config via a dotfiles repo without syncing data, or keeping cache on a different volume).

## Credentials — never a plaintext file in the config dir

Storing secrets in a plaintext file (`credentials.json`, `.env`) exposes them to malware, other users on the machine, and accidental leaks via backups or file sharing. Order of preference:

1. **OS keychain** (best) — macOS Keychain, Windows Credential Manager, Linux Secret Service. Use an abstraction library (in Node, a keytar-style binding). Use a descriptive service name tied to the tool (e.g. `com.you.myapp`), not a generic `api`.
2. **Restricted file** (fallback when no keychain is available) — write with `0600` permissions on Unix, in a file separate from config.

Regardless of method: keep credentials isolated from config, and **never** let them land in cache, backups, or logs. Never print full tokens in debug output.

## `.env` is a dev convention, not tool storage

`.env` is a project-local, development-time pattern and must be gitignored — it is not where a CLI persists global user config. A CLI should *read* config with clear precedence and never *write* its state into a `.env` file.

## Recommended layout

Global (shown via `env-paths` on Linux; the library maps it per-OS):

```
~/.local/share/myapp/      # durable bundle
  config.json              # one config file — don't also keep a separate settings.json globally
  data/
  backups/
  logs/
~/.cache/myapp/            # disposable
# credentials -> OS keychain, no file here
```

Per-project (lives inside the user's project directory):

```
<user-project>/
  .myapp/
    settings.json          # project-local config, overrides global
```

## Centralize path resolution in one module

Put all path logic in a single `core/paths.ts` so the rest of the app references named paths, never hardcoded strings. This makes the layout trivial to change and hides cross-platform differences:

```typescript
// core/paths.ts — single source of truth for where things live
import envPaths from "env-paths";
import { join } from "node:path";

const paths = envPaths("myapp", { suffix: "" });

export const appPaths = {
  config:  join(paths.data, "config.json"),
  data:    join(paths.data, "data"),
  backups: join(paths.data, "backups"),
  logs:    join(paths.data, "logs"),
  cache:   paths.cache,            // the only directory safe to delete wholesale
};
// credentials are NOT here — they go through a keychain adapter
```

## Config precedence

Resolve configuration in layers, later sources overriding earlier:

```
built-in defaults  <  config file  <  environment variables  <  command-line flags
```

Respect environment overrides for the storage location itself (e.g. honor `XDG_*` variables, or a `MYAPP_CONFIG_DIR`) so power users and CI can redirect where data lives.