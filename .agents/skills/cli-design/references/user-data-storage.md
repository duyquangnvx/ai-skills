# User & Workspace Data Storage

Read this when the CLI must persist anything for the user — config, credentials, projects, cache, backups, logs. The goal is a layout that respects OS conventions, keeps secrets safe, and stays easy to manage.

## The invariants — get these right regardless of layout

Layout style is a choice (see next section), but these four hold either way:

1. **Separate global from per-project, and mirror their structure.** Global data (applies across all projects) lives in the user's home area; per-project data lives inside that project directory, like `git` keeps `.git/`. Use the *same* subdirectory names in both scopes so one mental model applies everywhere, with project-scope overriding global-scope.
2. **Keep disposable data in a clearly-named subdirectory.** Cache and regenerable state (e.g. `cache/`, session transcripts) must be deletable without touching real data. Separability is the requirement — a named subdir is enough; a separate OS location is optional.
3. **Isolate credentials from ordinary state.** Persist secrets in a dedicated `0600` file or the OS keychain (see Credentials below for the tradeoff) — never mixed into world-readable config, and never written into a project's `.env`.
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
# credentials -> 0600 credentials file or OS keychain (see Credentials)
```

Choose this when the tool is something users actively inspect, debug, and reset; when its state (sessions, projects, plugins) is a tightly-coupled whole; and when you want global↔per-project symmetry. Benefits: one place to look (`ls ~/.mytool/`), trivial uninstall/reset (`rm -rf ~/.mytool ~/.mytool.json`), and a per-project directory that can mirror the global one. This symmetry is impossible if global data is scattered across OS dirs — which is the main reason rich dev tools consolidate.

### Shape B — Spread / two-bucket (for simpler or Unix-philosophy tools)

Follow OS-standard locations per data category. Collapse to two buckets unless you have a concrete reason to split further: a **durable bundle** (config + data + backups + logs) and a separate **cache**.

```
~/.local/share/mytool/    # durable bundle (Linux; map per-OS, see table)
  config.json  data/  backups/  logs/
~/.cache/mytool/          # disposable, the only thing safe to nuke wholesale
# credentials -> 0600 credentials file or OS keychain
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

Secrets mixed into ordinary config leak via backups, file sharing, and accidental commits — isolate them regardless of mechanism. Two legitimate mechanisms; pick by audience, not by a fixed ranking:

- **Restricted file** — a dedicated secrets file with `0600` permissions, separate from config. The pragmatic default for dev tools (`aws`, `gcloud`, `kubectl`, Claude Code on Linux/Windows all do this): transparent to inspect and rotate, debuggable, and works everywhere including headless servers, containers, WSL, and CI.
- **OS keychain** — macOS Keychain, Windows Credential Manager, Linux Secret Service. Stronger at-rest protection; worth it for general-audience tools and high-value, long-lived tokens. Use a native binding (in Node, `@napi-rs/keyring`; `keytar` is archived/unmaintained) and a descriptive service name tied to the tool (e.g. `com.you.mytool`), not a generic `api`. Know the platform pain before committing: Linux Secret Service needs dbus plus a desktop environment (fails on headless servers, containers, WSL), Windows Credential Manager caps blobs at ~2.5KB (an OAuth token plus refresh token can exceed it), and macOS re-prompts whenever the binary's signature changes. If you go keychain, ship a `0600`-file fallback (what `gh` does).

Also accept a `MYTOOL_API_KEY`-style env var at runtime, overriding stored credentials — that is how CI and scripts inject secrets without touching persistent storage.

Regardless of mechanism, never let credentials land in cache, backups, or logs, and never print full tokens in debug output.

## `.env` is a dev convention, not tool storage

`.env` is a project-local, development-time pattern and must be gitignored — it is not where a CLI persists global user config. A CLI should *read* config with clear precedence and never *write* its state into a `.env` file.

## Write state safely: atomic writes and sync-safe deletes

Durable state files need two protections that are cheap to add and painful to retrofit:

- **Atomic writes.** Write to a temp file in the same directory, then `rename()` over the target — rename is atomic on the same filesystem, so a crash or Ctrl-C mid-write leaves the old file intact instead of a half-written JSON. This is what makes crash-only design (no required cleanup, recover on next run) actually hold for file-backed state.
- **Soft-delete records that sync.** If local data syncs with a remote, deleting a record must leave a tombstone (`deleted: true`, bump `updatedAt`), not remove the row — otherwise the next sync can't distinguish "deleted here" from "never arrived here" and deleted records resurrect from the remote. Filter tombstones out of normal reads; garbage-collect them only after the remote has acknowledged the deletion. Purely local stores can hard-delete.

```typescript
async function persist(path: string, store: Store): Promise<void> {
  const tmp = `${path}.tmp`;
  await writeFile(tmp, JSON.stringify(store, null, 2), { mode: 0o600 });
  await rename(tmp, path); // atomic swap — readers see old or new, never partial
}
```

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
// credentials are NOT here — they go through a credential adapter (0600 file or keychain)
```

Swap the `root` resolution for an `env-paths`-based one to move from Shape A to Shape B without touching the rest of the app.