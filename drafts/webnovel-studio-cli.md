# `studio` — CLI Design Specification

> Skill-compliant command-surface design for `webnovel-studio`, derived from `docs/design.md` §9.
> The design doc is product truth: the pipeline DAG, casting model (entity/persona/voice), voiceprint
> locking, and TTS provider interface are taken as-is. Where the **cli-design** skill mandates something
> the doc underspecifies or contradicts, the skill wins and the conflict is flagged in §j.

`studio` is a **per-project workspace tool, like `git`**. You run it from inside a novel workspace; the
workspace directory *is* the project, the repo, and the source of truth. This framing drives every
storage and config decision below.

---

## a) Skill inputs used

### Skill files read (in full)

| File | Why it was read for this task |
|---|---|
| `cli-design/SKILL.md` | Master rules: non-negotiables, adaptive output, errors, args/flags, subcommands, config, agents, architecture rule, stack heuristic, review checklist. |
| `references/conventions.md` | Standard flag names, exit-code vocabulary, env vars to honor, config precedence, binary naming, deprecation. |
| `references/typescript-stack.md` | Framework selection (Commander vs citty), supporting libs, signal handling, build/test/distribution. |
| `references/architecture.md` | Thin-command/fat-core, context injection, the reporter, error boundary, lazy command loading, progress reporting, bootstrap order. |
| `references/user-data-storage.md` | Global vs per-project symmetry, keychain-first credentials, `.env` is dev-only, atomic writes, soft-deletes, central path module. |

### Major decisions → driving skill section

| Decision | Driving skill section |
|---|---|
| `noun verb` ordering kept (`chapter build`, `voice design`) | SKILL → Subcommands; design.md §9 already chose it |
| Single typed `ExitCode` map; gate failures get dedicated codes | SKILL → Non-negotiables; conventions → Exit codes |
| `--json` on every data command, stable schema = API contract | SKILL → Adaptive output, Agents are users too |
| stdout = data, stderr = logs/progress/spinners | SKILL → Adaptive output; architecture → reporter |
| API keys **out of `.env`**, into keychain / `--*-file` / stdin | SKILL → Non-negotiables (secrets); storage → Credentials |
| `.studio/` ↔ global `~/.studio/` symmetry; XDG-aware root override | storage → global/per-project symmetry & precedence |
| Config precedence flags → env → project → user → defaults | SKILL → Configuration; conventions → precedence |
| Destructive tiers: mild/moderate/severe + `--confirm=<token>` | SKILL → Arguments & flags (confirmation tiers), Agents |
| Atomic writes + soft-delete (tombstone) for registry JSONL | storage → Write state safely |
| Long-stage progress on stderr, logs dumped on failure | SKILL → Performance & robustness |
| Commander + `@commander-js/extra-typings`, lazy subcommands | SKILL → Choosing the stack; stack reference |
| Thin commands / fat core; DAG engine, resolver, registry, TTS in core | SKILL → The one architectural rule; architecture |
| `studio agent` is a second façade on the same core | SKILL → Agents are users too; design.md §9 |

---

## b) Complete command surface

### Conventions applied to every command

- Every data-emitting command supports `--json`. Human output is free to evolve; the JSON schema is frozen.
- `studio` with no args, `-h`, `--help`, and `--version` always work and load no business logic.
- Bare `studio chapter` (a noun with no verb) lists that noun's verbs — never runs a default action.
- `-` is accepted where a file path is expected (stdin/stdout). `--` stops flag parsing for pass-through.
- Numeric chapter ranges accept `12`, `12-40`, `12-40,55,90-` (parsed via `multi-integer-range`).

### Global flags (defined once on the base command)

| Flag | Default | Meaning |
|---|---|---|
| `--json` | off | Machine-readable output to stdout; structured errors to stderr |
| `-q`, `--quiet` | off | Suppress non-essential human output (progress, hints) |
| `-d`, `--debug` | off | Verbose logs + stack traces to stderr (also via `DEBUG=studio*`) |
| `--no-color` | auto | Force-disable ANSI (also `NO_COLOR`, `TERM=dumb`) |
| `--no-input` | auto-on when not a TTY | Never prompt; fail telling the user which flag to pass |
| `-C, --cwd <dir>` | `process.cwd()` | Run as if started in `<dir>` (locate the workspace from here) |
| `--config <file>` | `.studio/config.json` | Override project config path |
| `-n, --dry-run` | off | Plan/describe changes; perform no writes or synthesis |
| `--confirm <token>` | — | Non-interactive confirmation for destructive actions (see §e) |
| `-h, --help` / `--version` | — | Help / version; nothing else |

Env equivalents honored: `NO_COLOR`, `FORCE_COLOR`, `TERM`, `DEBUG`, `DO_NOT_TRACK`, `EDITOR`, `PAGER`,
`HTTP(S)_PROXY`, `NO_PROXY`, `TMPDIR`. App-scoped: `STUDIO_CONFIG_DIR` (global root override),
`STUDIO_NO_COLOR`, `STUDIO_TELEMETRY`.

---

### `studio init`

Scaffold a workspace in the current directory (the `git init` analogue): create `.studio/`, `project.json`,
`registry/`, `.gitignore`, and a git-lfs entry for `voiceprints/*.wav`.

| Arg / flag | Default | Notes |
|---|---|---|
| `[dir]` (positional) | `.` | Workspace directory; created if missing |
| `--title <s>` | prompt | Novel title → `project.json` |
| `--slug <s>` | derived from title | URL-safe id |
| `--language <code>` | prompt (`vi`) | Source/target language |
| `--narrator-voice <id>` | prompt or `auto` | Project-level narrator voice (`persona: null` segments) |
| `--source-url <url>` | optional | Recorded for `chapter import` default |
| `--force` | off | Overwrite an existing `project.json` (mild-destructive) |

```bash
# Human, interactive
studio init my-novel --title "Kiếm Tổ" --language vi

# Agent / script (no prompts)
studio init my-novel --no-input --json \
  --title "Kiếm Tổ" --slug kiem-to --language vi --narrator-voice auto
```

---

### Content pipeline (DAG, idempotent, resumable)

#### `studio chapter import <url|file>`

Fetch or copy a raw chapter into `chapters/NNNN/source.txt` (stage ①). `-` reads from stdin (clipboard paste).

| Arg / flag | Default | Notes |
|---|---|---|
| `<source>` positional | — | URL, file path, or `-` for stdin |
| `--number <n>` / `-N <n>` | auto-next | Target chapter number |
| `--source-url <url>` | from `project.json` | Override the configured source |
| `--force` | off | Overwrite an existing `source.txt` (mild) |

```bash
studio chapter import https://example.com/novel/ch12 --number 12
pbpaste | studio chapter import - --number 12 --json
```

#### `studio chapter build <n|--range a-b>`

Run the DAG (enhance → discover → segment → resolve → synth → stitch), skipping stages whose
`meta.json` status is `done` and whose content hash is unchanged. This is the workhorse; it spawns the
batch TTS CLI for synth.

| Arg / flag | Default | Notes |
|---|---|---|
| `[n]` positional | — | Single chapter |
| `-r, --range <spec>` | — | `12-40`, `12-40,55` (mutually exclusive with `[n]`) |
| `--from-stage <stage>` | auto (first stale) | Force re-run from `enhance\|discover\|segment\|resolve\|synth\|stitch` |
| `--to-stage <stage>` | `stitch` | Stop after this stage |
| `--force` | off | Ignore cache; re-run requested stages even if `done` (moderate) |
| `-j, --concurrency <int>` | config `concurrency` (4) | Parallel segments/chapters |
| `--timeout <ms>` | config | Per-TTS-call network/process timeout |
| `-n, --dry-run` | off | Print the DAG plan (which stages would run, why) and exit 0 |

```bash
# Human: build one chapter, watch progress
studio chapter build 12

# Re-run only the audio half after a voice rebind
studio chapter build 12 --from-stage resolve --force

# Agent: build a range, parse per-chapter result
studio chapter build --range 12-40 --json --no-input -j 8
```

#### `studio chapter render <n>`

Build **only** the audio-producing tail (resolve → synth → stitch) and require the casting-completeness
gate to pass first. Fails closed if the gate is not satisfied (see §c). Convenience over
`build --from-stage resolve`, but with the gate enforced.

| Arg / flag | Default | Notes |
|---|---|---|
| `<n>` positional / `-r, --range` | — | Chapter or range |
| `--force` | off | Re-synth overwriting cached `seg-*.wav` (moderate) |
| `-j, --concurrency` / `--timeout` | config | As above |

```bash
studio chapter render 12
studio chapter render --range 12-40 --json --no-input
```

---

### Registry — casting (entity / persona / voice)

Consistent verbs across nouns: `add`, `list`, `show`. JSONL/JSON writes are atomic; registry deletes are
soft (tombstone), per storage reference.

#### `studio entity add|list|show`

| Verb | Args / flags |
|---|---|
| `add` | `--id <s>` (default derived), `--kind human\|beast\|spirit\|system\|collective\|unknown`, `--name <s>`, `--true-voice <voiceId>`, `--lineage-from <entityId>`, `--lineage-type <s>` |
| `list` | `--kind <k>`, `--json`, `--plain` |
| `show` | `<id>` positional, `--json` |

#### `studio persona add|list|show`

| Verb | Args / flags |
|---|---|
| `add` | `--id <s>`, `--entity <entityId>` (required), `--alias <s>` (repeatable), `--voice <voiceId>`, `--age-stage child\|youth\|adult\|elder` |
| `list` | `--entity <id>`, `--json`, `--plain` |
| `show` | `<id>` positional, `--json` |

```bash
studio persona add --entity ent_trieu --alias "Triệu Công Tử" --alias "công tử" --voice voice_trieu
studio persona show per_trieu --json
```

#### `studio alias add|resolve|list`

`aliases.jsonl` is append-only and period-scoped. `resolve` answers "who is `<name>` at chapter N".

| Verb | Args / flags |
|---|---|
| `add` | `--alias <s>` (required), `--persona <id>` (required), `--from <chapter>` (default 1), `--to <chapter\|none>` (default `none`) |
| `resolve` | `<alias>` positional (required), `--at <chapter>` (required), `--json` |
| `list` | `--persona <id>`, `--at <chapter>`, `--json`, `--plain` |

```bash
# Human
studio alias resolve "Diệp cô nương" --at 30

# Agent
studio alias resolve "Diệp cô nương" --at 30 --json
```

#### `studio timeline add|list`

`timeline.jsonl` is append-only; only M2/M4/M5 events (`front`, `reveal`, `transform`).

| Verb | Args / flags |
|---|---|
| `add` | `--type front\|reveal\|transform` (required), `--at <chapter>` (required), plus type-specific: `--body-persona`, `--front-entity`, `--target`, `--audience-knows`, `--on-reveal-voice soul\|keep_body`, `--effect <json>`, `--to <chapter>` |
| `list` | `--type <t>`, `--from <ch>`, `--to <ch>`, `--json`, `--plain` |

```bash
studio timeline add --type front --at 12 --body-persona per_trieu --front-entity ent_lamphong --no-audience-knows
studio timeline add --type reveal --at 88 --target per_trieu --audience-knows --on-reveal-voice soul
```

---

### Voice

#### `studio voice list|show|assign`

| Verb | Args / flags |
|---|---|
| `list` | `--json`, `--plain` |
| `show` | `<voiceId>` positional, `--json` |
| `assign` | `<persona>` positional, `--voice <voiceId>` (required). **Rebind = destructive** (moderate, §e). `--from <chapter>` to scope as a new persona instead of mutating. `-n` shows invalidation set. |

#### `studio voice design <persona>`

Run the Voiceprint Factory once: design a reference WAV via a pluggable designer, clone-and-audition
through OmniVoice, then lock it. Calls the LLM/TTS designer providers.

| Arg / flag | Default | Notes |
|---|---|---|
| `<persona>` positional | — | Persona to design a voice for |
| `--designer gemini\|omnivoice\|clip` | config `tts.design.provider` | Designer backend |
| `--design-lang <code>` | project language | Cross-lingual design source |
| `--clip <file>` | — | Required when `--designer clip` (clean 3–10s sample) |
| `--instruct <s>` | derived from persona trait | Provenance only; never used at synth |
| `--lock` / `--no-lock` | `--lock` | Lock as voiceprint SoT after audition; `--no-lock` leaves provisional |
| `-y, --yes` | off | Skip the audition-accept prompt (agent path) |

```bash
studio voice design per_trieu --designer gemini --instruct "male, youth, arrogant"
studio voice design per_diep --designer clip --clip ./samples/diep.wav --no-input --yes --json
```

#### `studio voice distinctness`

Warn when locked voiceprints sound too similar across a large cast (deterministic acoustic distance).

| Flag | Default | Notes |
|---|---|---|
| `--threshold <0..1>` | config or `0.85` | Similarity above this is flagged |
| `--json` / `--plain` | — | Pairs over threshold, with scores |

#### `studio cast inspect <n>`

Show the resolved voices (`cast.jsonl`) for a chapter — per-segment voiceprint + effects + text.

| Flag | Notes |
|---|---|
| `<n>` positional | Chapter |
| `--json` / `--plain` | Machine / grep-friendly output |
| `--segment <i>` | Inspect one segment |

```bash
studio cast inspect 12
studio cast inspect 12 --json
```

---

### Validation & library

#### `studio validate <n|all>`

The **casting-completeness gate**. Deterministic, not LLM-judged. Also runs implicitly before `render`.

| Flag | Notes |
|---|---|
| `<n>` or `all` positional | One chapter or the whole workspace |
| `--json` | Branchable structured failures (schema in §d) |
| `--strict` | Treat warnings (alias conflicts, provisional voices) as failures too |

```bash
studio validate 12
studio validate all --json --no-input   # agent gates CI on exit code
```

#### `studio library list|pull <preset>|upgrade`

Vendor voice presets, each bundling a locked voiceprint. `pull` copies into `registry/` and pins
`presets.lock`. `upgrade` shows a version diff and requires confirmation to re-pin (changing a
voiceprint mid-novel breaks consistency).

| Verb | Args / flags |
|---|---|
| `list` | `--json`, `--plain` |
| `pull` | `<preset>` = `library:<vendor>/<preset>@<version>`, `--as <voiceId>`, `--force` |
| `upgrade` | `[preset]` (default all pinned), `-n, --dry-run` (shows diff), `--confirm <preset@ver>` to re-pin (severe, §e) |

```bash
studio library pull library:storio/young-male-arrogant@1.2
studio library upgrade --dry-run --json
studio library upgrade library:storio/young-male-arrogant --confirm young-male-arrogant@1.3
```

#### `studio agent "<task>"` (escape hatch)

A second façade on the same core. The agent orchestrates judgment-heavy steps (`design_voice`,
low-confidence attribution review, `add_identity_event`). **Every write to the SoT is human-in-the-loop**
unless an explicit non-interactive confirm path is given.

| Flag | Default | Notes |
|---|---|---|
| `"<task>"` positional | — | Natural-language task |
| `--chapter <n>` / `--range` | — | Scope |
| `--auto-confirm <scope>` | off | Non-interactive write approval for agents (`identity\|voice\|all`); audited |
| `--json` | — | Streamed structured tool-call trace |

```bash
studio agent "detect any soul-swap or disguise in chapter 88 and propose timeline events" --chapter 88
studio agent "design voices for all provisional personas" --auto-confirm voice --no-input --json
```

#### Roadmap commands (specified, marked future)

`studio thumbnail <n>` and `studio video <range> [--image ...]` are leaf downstream consumers of
`chapter.wav`; they follow the same flag conventions and are out of scope for the core surface.

---

## c) Exit code map

Single typed constant (`enum ExitCode`), never scattered. Stays inside 0 and 1–125 to avoid the
shell-reserved 126/127/128+N. Agents branch on these.

```ts
export enum ExitCode {
  Success         = 0,   // command completed
  GeneralError    = 1,   // unclassified failure
  UsageError      = 2,   // bad flags/args, unknown command, missing required arg
  ValidationError = 3,   // input failed boundary validation (bad chapter id, malformed range)
  NotFound        = 4,   // workspace/chapter/entity/persona/voice not found
  CastingGate     = 5,   // casting-completeness gate FAILED (validate / render) — branchable
  ConfigError     = 6,   // missing/invalid config, missing required secret
  ProviderError   = 7,   // LLM/TTS provider call failed (network, process, quota)
  ConflictError   = 8,   // alias conflict, concurrent-write lock, duplicate id
  ConfirmRequired = 9,   // destructive op needs --confirm/--force and none given (non-interactive)
  Interrupted     = 130, // SIGINT (128+2); SIGTERM → 143. Set by the signal handler, not mapped here
}
```

### Casting-completeness gate semantics

`validate` and `render` share one core function `checkCastingCompleteness(chapter)`. It fails (exit
**`5 CastingGate`**) when **either**:

1. a `dialogue` segment cannot be resolved to a persona (unmatched alias / new-persona queue), **or**
2. a persona present in the chapter's cast has no resolvable voice (no `persona.voice`, no
   `entity.trueVoice`, and not covered by a timeline event).

The gate is **deterministic** — it never asks an LLM. On failure it routes the caller to the agent/user
and returns the precise blocking records in `--json` so an agent can branch and act. `validate --strict`
additionally fails on warnings (alias conflicts, provisional/unlocked voices). `render` calls the gate
first and refuses to synthesize when it fails — this is the hard enforcement of design.md principle #1.

---

## d) Output behavior

### TTY vs piped (decided once in the reporter)

- **stdout** carries results only. **stderr** carries logs, progress, spinners, errors — pipes stay clean.
- stdout TTY → human format (color, aligned tables). Not a TTY → plain text, no ANSI, no spinners.
- Color disabled when: stream not a TTY, `NO_COLOR`/`STUDIO_NO_COLOR` set, `TERM=dumb`, or `--no-color`.
  `FORCE_COLOR` overrides.
- Success always prints a brief line (silence looks broken) and, after state changes, names what changed
  and suggests the next command (e.g. after `chapter build 12` → "Built chapter 12. Next: `studio cast
  inspect 12`"). `-q/--quiet` suppresses these.
- Tables: one record per line, no borders, headers hideable; `--plain` for grep/awk when layout wraps.

### Long-running stage progress (synth of hundreds of segments)

- First output within 100ms; print the plan *before* spawning the batch TTS process, not after.
- Progress goes to **stderr** so `--json` stdout stays parseable. TTY → a live bar with ETA
  (`synth ch0012  ▓▓▓▓▓░░░  142/318 segments  eta 2m`); non-TTY/CI → periodic plain lines
  (`synth ch0012 142/318`). The batch CLI's per-segment logs are captured; if the bar hides them and the
  stage fails, the captured logs are dumped to stderr and a debug-log path is printed.
- `--json` mode streams **NDJSON progress events to stderr** (one object per line) so agents can track
  without parsing prose; the final result object goes to stdout.

```jsonc
// stderr, --json progress stream (NDJSON)
{"event":"stage.start","chapter":12,"stage":"synth","total":318}
{"event":"stage.progress","chapter":12,"stage":"synth","done":142,"total":318,"etaMs":124000}
{"event":"stage.done","chapter":12,"stage":"synth","done":318,"cached":120,"synthesized":198}
```

### `--json` schemas (frozen contracts)

**`studio chapter build` / `render`** (stdout, final result):

```jsonc
{
  "schemaVersion": 1,
  "command": "chapter.build",
  "chapters": [
    {
      "number": 12,
      "stages": [
        { "stage": "enhance",  "status": "cached", "hash": "ab12…" },
        { "stage": "discover", "status": "done",   "hash": "cd34…", "newPersonas": ["per_x"] },
        { "stage": "segment",  "status": "done",   "hash": "ef56…", "segments": 318 },
        { "stage": "resolve",  "status": "done",   "hash": "0a7b…" },
        { "stage": "synth",    "status": "done",   "hash": "9c8d…", "synthesized": 198, "cached": 120 },
        { "stage": "stitch",   "status": "done",   "output": "chapters/0012/chapter.wav" }
      ],
      "ok": true
    }
  ],
  "ok": true
}
// stage.status ∈ "done" | "cached" | "skipped" | "failed"
```

**`studio validate`** (stdout):

```jsonc
{
  "schemaVersion": 1,
  "command": "validate",
  "ok": false,
  "chapters": [
    {
      "number": 12,
      "ok": false,
      "blocking": [
        { "type": "unresolved_persona", "segment": 7, "alias": "sư huynh",
          "reason": "alias matches 2 personas in chapter range", "fix": "studio alias resolve \"sư huynh\" --at 12" },
        { "type": "persona_without_voice", "persona": "per_diep",
          "fix": "studio voice design per_diep" }
      ],
      "warnings": [
        { "type": "provisional_voice", "persona": "per_npc_3", "fix": "studio voice design per_npc_3 --lock" }
      ]
    }
  ]
}
// exit 5 when any blocking[] is non-empty; exit 5 on warnings too under --strict
```

**`studio alias resolve`** (stdout):

```jsonc
{
  "schemaVersion": 1,
  "command": "alias.resolve",
  "alias": "Diệp cô nương",
  "at": 30,
  "match": { "persona": "per_diep_conuong", "entity": "ent_diep", "from": 12, "to": 50 },
  "ambiguous": false,
  "candidates": [
    { "persona": "per_diep_conuong", "from": 12, "to": 50 }
  ]
}
// ambiguous=true with candidates.length>1 → exit 8 ConflictError; no match → exit 4 NotFound
```

**`studio cast inspect`** (stdout):

```jsonc
{
  "schemaVersion": 1,
  "command": "cast.inspect",
  "chapter": 12,
  "segments": [
    { "i": 1, "persona": "per_trieu", "voiceprint": "voiceprints/voice_trieu.wav",
      "effect": [], "tags": ["[scoff]"], "text": "Ngươi cũng xứng?" },
    { "i": 2, "persona": null, "voiceprint": "voiceprints/narrator.wav",
      "effect": [], "tags": [], "text": "Hắn quay lưng bỏ đi." }
  ]
}
```

### Quiet / verbose

`-q/--quiet` → results + errors only (no progress, no hints). `-d/--debug` (or `DEBUG=studio*`) →
full logs + stack traces to stderr. Default sits between: brief progress + next-step hints, no traces.

---

## e) Destructive / confirmation design

Per the skill's three-tier model, each destructive op gets a tier, a `--dry-run` where it removes/overwrites
in bulk, and a non-interactive path for agents.

| Operation | Why destructive | Tier | Interactive | Non-interactive (agent) |
|---|---|---|---|---|
| `init --force` | Overwrites existing `project.json` | mild | optional y/N | `--force` |
| `chapter import --force` | Overwrites `source.txt` (the import SoT) | mild | optional y/N | `--force` |
| `chapter build/render --force` | Re-runs stages, overwriting derived files (`enhanced.md`, `segments.jsonl`, `cast.jsonl`, `audio/*.wav`) | moderate | confirm + `--dry-run` shows invalidation set | `--force` |
| `voice assign` (rebind) | Changes a locked voice → re-render; alters how a character sounds across the novel | moderate | confirm, show affected chapter count | `--force` (or `--from <ch>` to scope as new persona instead) |
| `timeline add` (front/reveal/transform) | Mutates derived voices for a chapter range (invalidates ④⑤⑥) | moderate | confirm + `--dry-run` shows invalidation range | `--force` |
| `library upgrade` re-pin | Swaps a voiceprint mid-novel — breaks consistency across all chapters using it | **severe** | type the `preset@version` | `--confirm <preset@version>` |
| `voice design --lock` overwriting an existing locked voiceprint | Replaces timbre SoT | **severe** | type the voice id | `--confirm <voiceId>` |

Rules:

- Tier escalates with **blast radius**: a single file → mild; a derived range → moderate; the timbre SoT
  used across the whole novel → severe.
- Severe actions require typing the exact resource name interactively, or `--confirm=<exact-name>` in
  scripts. A mismatched token aborts with exit `9 ConfirmRequired`.
- Under `--no-input` with no `--force`/`--confirm`, any tier above mild **fails fast** with exit
  `9 ConfirmRequired` and prints the exact flag to pass — agents never hang on a prompt.
- `--dry-run` is honored by every moderate+ op and prints the invalidation set (which chapters/stages
  would be recomputed) without writing.

---

## f) Config, storage & secrets

`studio` is a project workspace tool. Two scopes, mirrored structure (storage reference invariant #1):

```
~/.studio/                      # GLOBAL (Shape A consolidated) — applies across novels
  config.json                   # default provider, baseURL, model, concurrency
  library/                      # vendor presets cached across projects
  cache/                        # disposable
# overridable via STUDIO_CONFIG_DIR (invariant #4)

<workspace>/.studio/            # PER-PROJECT — overrides global
  config.json                   # this novel's provider/model/tts/scoping/concurrency
  cache/                        # content-addressed derived state — disposable
  state.json                    # resume cursor / build progress
<workspace>/project.json        # version-controlled product metadata
<workspace>/.env                # dev-only, gitignored — see secrets below
<workspace>/registry/           # version-controlled SoT (voiceprints via git-lfs)
```

The same subdir names (`config.json`, `cache/`) appear in both scopes, so one mental model applies and
project scope overrides global.

### Config precedence (skill-mandated, highest first)

```
CLI flags  >  shell env vars  >  project .studio/config.json  >  user ~/.studio/config.json  >  built-in defaults
```

`project.json` is product data (title, language, narratorVoice), not tool config — it sits beside, not in,
the precedence chain. `.env` is read for project-scoped vars but is **not** a config file and `studio`
never writes state into it (storage reference).

### Secrets — the key reconciliation

design.md §5 puts API keys in `.env`. The skill **forbids secrets via env vars** (they leak through logs,
`docker inspect`, `systemctl show`) and via flags. Reconciliation:

1. **Preferred**: OS keychain via `@napi-rs/keyring`, service name `com.webnovel.studio`. `studio` reads
   provider keys (`llm`, `tts.design`) from the keychain. A one-time `studio init` (or `studio config
   set-secret --stdin`) stores them.
2. **File fallback** where no keychain exists (CI, headless Linux): `--llm-key-file <path>` /
   `--tts-key-file <path>`, or piped via stdin. Files only, `0600`.
3. **`.env` tolerated as a dev convenience, never the documented path.** If a key is found *only* in
   `.env`, `studio` uses it but prints a one-time warning to stderr: "Reading OPENAI_API_KEY from .env —
   prefer the keychain: run `studio config set-secret llm`." This keeps design.md's dev ergonomics while
   steering toward the safe path.

Keys never appear in flags, never in `--json` output, never in debug logs (printed as `***`).

### Atomic writes & soft-deletes (registry JSONL)

Storage reference, applied to the SoT:

- **Atomic writes** for every durable write — `entities/*.json`, `personas/*.json`, `voices/*.json`,
  `presets.lock`, `state.json`, `meta.json`: write `*.tmp` in the same dir, then `rename()` over the
  target. A Ctrl-C mid-write leaves the previous file intact (crash-only design holds).
- **Append-only JSONL** (`aliases.jsonl`, `timeline.jsonl`) is written by appending a complete line then
  `fsync`; never rewritten in place.
- **Soft-delete** because `registry/` syncs through git across machines: removing an alias/persona writes
  a tombstone record (`"deleted": true`, bumped `updatedAt`) rather than deleting the line, so a pull on
  another clone can't resurrect it. Normal reads filter tombstones; GC happens only on explicit
  `studio registry compact`. (`.studio/cache/` is purely local → hard-delete is fine there.)
- A cross-process lock (`proper-lockfile`) guards concurrent registry writes → exit `8 ConflictError` if held.

---

## g) Stack choice (one-line rationales)

| Concern | Choice | Rationale |
|---|---|---|
| Runtime | Node ESM-only, `engines: ^20.19 \|\| >=22.12` | `require(esm)` stable; drop CJS dual-build |
| Arg parsing | **Commander + `@commander-js/extra-typings`** | Skill's safe default for a typical multi-noun product CLI; typed `.opts()`/`.action()` |
| Lazy loading | per-command `() => import()` loaders | Keep `--version`/`--help` fast despite a large surface |
| Validation | **zod** at the command boundary | Schema validation; messages double as user errors; reject path traversal/control chars |
| Color | `util.styleText` (built-in) | Zero-dep; honor the full disable matrix in the reporter |
| Spinners/progress | `ora` + `log-update`, no-op when not a TTY | Live bars in a TTY, plain lines in CI |
| Subprocess (batch TTS, ffmpeg) | **execa** with args array | Safe spawning, cross-platform, timeouts via `AbortController` |
| Concurrency / retry / timeout | `p-limit`, `p-retry`, `p-timeout` | Bounded synth fan-out, provider retries |
| Numeric ranges | `multi-integer-range` | `--range 12-40,55,90-` |
| Keychain | `@napi-rs/keyring` | Keytar is archived; secrets out of `.env` |
| Cross-process lock | `proper-lockfile` | Guard concurrent registry writes |
| Logging | `pino` (machine) / `consola` (pretty) | Structured logs to stderr |
| Build | **tsdown** → single bundled file | tsup unmaintained; faster cold start, clean `npx` |
| Test | vitest, in-process command invocation + small execa E2E | Core unit-tested pure; E2E asserts exit codes / stdout-stderr / `--json` / `NO_COLOR` |

---

## h) Project structure (thin commands / fat core)

Grown per the architecture reference — one module per command, fat framework-free core, no hexagonal
layering. Three levels deep maximum.

```
src/
  bin/studio.ts              # shebang entry; fast-paths (--version/--help) before framework loads
  cli.ts                     # base command, global flags, ONE error boundary, signal handlers, dispatch
  context.ts                 # CliContext: { stdout, stderr, env, cwd, reporter } injected per run
  reporter/
    reporter.ts              # picks human|json + color + quiet ONCE; routes stdout vs stderr
    progress.ts              # TTY bar / NDJSON stderr events for long stages
    views/                   # pure one-shot render functions (cast, validate, build, alias…)
  commands/                  # THIN — parse → call core → reporter.result(); each lazy-loaded
    init.ts
    chapter/{import,build,render}.ts
    entity/{add,list,show}.ts
    persona/{add,list,show}.ts
    alias/{add,resolve,list}.ts
    timeline/{add,list}.ts
    voice/{list,show,assign,design,distinctness}.ts
    cast/inspect.ts
    validate.ts
    library/{list,pull,upgrade}.ts
    agent.ts
  core/                      # FAT — framework-agnostic, no console/argv/process.exit, throws typed errors
    dag/{engine.ts,stages.ts,hash.ts}     # DAG: idempotency, content-hash cache, stage runners
    registry/{entities.ts,personas.ts,voices.ts,aliases.ts,timeline.ts,store.ts}  # atomic + soft-delete
    resolver/resolve-voice.ts             # resolveVoice(personaId, at) from §2.2
    casting/gate.ts                        # deterministic completeness gate (validate + render share)
    scale/{discover.ts,attribute.ts,alias-index.ts}  # two-pass, text-led candidate set
    tts/{provider.ts,omnivoice-batch.ts,designer.ts}  # TTS provider INTERFACE + impls
    effects/dsp.ts                         # ffmpeg/sox post effects (M4/M5)
    stitch/concat.ts                       # ffmpeg concat
  lib/
    paths.ts                 # SINGLE source of truth: global ~/.studio vs project .studio; STUDIO_CONFIG_DIR
    config.ts                # layered load (flags>env>project>user>defaults); getter, not top-level read
    secrets.ts               # keychain-first; file/stdin fallback; .env-warn path
    errors.ts                # CliError subclasses → ExitCode map
    exit-codes.ts            # the single ExitCode enum
test/
  core/**                    # bulk of coverage — pure functions, fake I/O passed in
  e2e/**                     # built binary: exit codes, stdout/stderr, --json schema, NO_COLOR
```

Key boundaries: `commands/` never contains business logic; `core/` never imports Commander, the reporter,
or calls `console`/`process.exit`. The TTS provider interface (`core/tts/provider.ts`) is the seam that
lets a second vendor plug in without touching the DAG (design.md §8).

---

## i) Key skeleton code

### Entry point (`src/bin/studio.ts`) — fast-paths before the framework

```ts
#!/usr/bin/env node
// Fast-path --version / --help: load zero business logic (architecture: startup performance).
const argv = process.argv.slice(2)
if (argv[0] === "--version" || argv[0] === "-V") {
  process.stdout.write(`${__STUDIO_VERSION__}\n`) // inlined at build time by tsdown
  process.exit(0)
}

const { run } = await import("../cli.js")
await run(process.argv)
```

### Error boundary + dispatch (`src/cli.ts`)

```ts
import { Command } from "@commander-js/extra-typings"
import { createContext } from "./context.js"
import { CliError } from "./lib/errors.js"
import { ExitCode } from "./lib/exit-codes.js"

export async function run(argv: string[]): Promise<void> {
  const ctx = createContext(process)            // inject real streams/env/cwd once
  installSignalHandlers(ctx)                     // SIGINT→130, SIGTERM→143, .unref() the cleanup timer

  const program = new Command("studio")
    .description("Produce audiobooks from webnovels via a deterministic pipeline.")
    .option("--json").option("-q, --quiet").option("-d, --debug")
    .option("--no-color").option("--no-input")
    .option("-C, --cwd <dir>").option("--config <file>")
    .option("-n, --dry-run").option("--confirm <token>")
    .showHelpAfterError()

  // Lazy subcommand registration — only the dispatched module evaluates.
  program.command("validate <target>")
    .option("--strict")
    .action(async (target, opts) => (await import("./commands/validate.js")).run(ctx, target, opts))
  // … chapter/voice/alias/… registered the same way

  try {
    await program.parseAsync(argv)
  } catch (error: unknown) {
    if (error instanceof CliError) {
      ctx.reporter.error(error.message, error.suggestion)   // stderr; how-to-fix last
      process.exitCode = error.exitCode
    } else {
      ctx.reporter.unexpectedError(error)                   // trace gated by --debug + bug-report URL
      process.exitCode = ExitCode.GeneralError
    }
  }
  // Set exitCode, never process.exit() — let stdout/stderr drain.
}
```

### One command end-to-end — `studio alias resolve` (`src/commands/alias/resolve.ts`)

Thin: validate input, call core, hand structured data to the reporter.

```ts
import { z } from "zod"
import type { CliContext } from "../../context.js"
import { resolveAlias } from "../../core/registry/aliases.js"
import { renderAliasResolve } from "../../reporter/views/alias.js"
import { CliError } from "../../lib/errors.js"
import { ExitCode } from "../../lib/exit-codes.js"

const schema = z.object({
  alias: z.string().min(1).regex(/^[^ -]+$/, "control characters not allowed"),
  at: z.coerce.number().int().positive(),
})

export async function run(
  ctx: CliContext,
  aliasArg: string,
  opts: { at?: string }
): Promise<void> {
  const input = schema.parse({ alias: aliasArg, at: opts.at }) // boundary validation → harden input

  const result = await resolveAlias(input, { workspace: ctx.cwd })

  if (result.ambiguous) {
    throw new CliError(
      `"${input.alias}" is ambiguous at chapter ${input.at} (${result.candidates.length} personas).`,
      `Disambiguate with: studio alias add --alias "${input.alias}" --persona <id> --from <ch>`,
      ExitCode.ConflictError
    )
  }
  if (!result.match) {
    throw new CliError(
      `No persona for "${input.alias}" at chapter ${input.at}.`,
      `Register it: studio alias add --alias "${input.alias}" --persona <id>`,
      ExitCode.NotFound
    )
  }

  ctx.reporter.result(result, renderAliasResolve) // human → view; --json → serialize the same data
}
```

### One core module — the architecture pattern (`src/core/registry/aliases.ts`)

Fat core: plain data in/out, I/O injected, no console/argv/exit, throws typed errors. Atomic +
period-scoped + soft-delete-aware, per the storage reference.

```ts
// Plain data shapes — no framework types leak in.
export interface ResolveAliasInput { alias: string; at: number }
export interface AliasRecord { alias: string; persona: string; from: number; to: number | null; deleted?: boolean }
export interface ResolveAliasResult {
  alias: string; at: number
  match: { persona: string; from: number; to: number | null } | null
  ambiguous: boolean
  candidates: Array<{ persona: string; from: number; to: number | null }>
}

// I/O injected as a parameter (DI without interfaces) → unit-testable with an inline fake.
export async function resolveAlias(
  input: ResolveAliasInput,
  io: { workspace: string; readAliases?: (ws: string) => Promise<AliasRecord[]> }
): Promise<ResolveAliasResult> {
  const read = io.readAliases ?? readAliasesJsonl
  const all = await read(io.workspace)

  const candidates = all
    .filter((r) => !r.deleted)                                  // tombstones filtered out of normal reads
    .filter((r) => r.alias === input.alias)
    .filter((r) => input.at >= r.from && (r.to === null || input.at <= r.to)) // period-scoped
    .map(({ persona, from, to }) => ({ persona, from, to }))

  const distinctPersonas = new Set(candidates.map((c) => c.persona))
  return {
    alias: input.alias,
    at: input.at,
    match: distinctPersonas.size === 1 ? candidates[0] : null,
    ambiguous: distinctPersonas.size > 1,
    candidates,
  }
}

// Append-only write helper (used by `alias add`) — complete line, fsync, never rewrite in place.
export async function appendAlias(workspace: string, record: AliasRecord): Promise<void> {
  await appendJsonlLine(aliasesPath(workspace), record) // fsync inside; crash-safe append
}
```

The same `resolveAlias` core is reused unchanged by the `studio agent` façade and by the resolver stage —
exactly the "one core, two façades" guarantee design.md principle #2 asks for.

---

## j) Skill vs design.md tensions

Each conflict, the reconciliation, and what I'd ask the product owner.

### T1 — Secrets in `.env` (design.md §5) vs skill forbids secrets via env vars

**Conflict.** §5 lists `.env # API keys (gitignored)`. The skill's non-negotiable: never accept secrets via
flags or env vars — only files, stdin, or the OS keychain.
**Reconciliation (skill wins, dev ergonomics preserved):** keychain-first via `@napi-rs/keyring`; file
(`--llm-key-file`) / stdin fallback for CI; `.env` tolerated as a dev convenience with a one-time
steering warning, never the documented happy path (see §f).
**Ask the owner:** Is a CI/headless deployment in scope (decides whether the file fallback is mandatory),
and are you comfortable with a one-time `.env` deprecation warning in the dev loop?

### T2 — `.studio/config.json` is committed (design.md §5) vs config-vs-secrets separation

**Tension.** §5 keeps `.studio/config.json` in git (provider, baseURL, model). That's fine for non-secret
config, but baseURLs/model ids sometimes smuggle tenant identifiers, and the doc has no global user scope.
**Reconciliation:** committed `project.json` + `.studio/config.json` for shared non-secret config; add a
**global `~/.studio/config.json`** (absent from the doc) for per-user defaults, with project overriding
global. Secrets never live in either. Provide `.studio/config.local.json` (gitignored) for personal
overrides.
**Ask the owner:** Do you want a global user-scope config at all, or is `studio` strictly per-workspace
with no machine-level defaults?

### T3 — design.md §9 says "exit non-zero" generically vs skill wants a distinct typed map

**Underspecified.** The gate just says "exit non-zero". The skill requires distinct branchable codes.
**Reconciliation:** the `ExitCode` enum in §c, with the casting gate getting its own code (`5`) so agents
can distinguish a gate failure from a provider failure (`7`) or a usage error (`2`).
**Ask the owner:** Confirm agents need to branch on gate-vs-provider failures (they almost certainly do for
CI) — if so the dedicated code stays.

### T4 — design.md §9 doesn't specify `--json` error shape; skill mandates structured errors in JSON mode

**Underspecified.** §9 says every command supports `--json` but says nothing about errors.
**Reconciliation:** in `--json` mode, errors are emitted as a structured object on **stderr**
(`{ "error": { "type", "message", "fix", "exitCode" } }`) while stdout stays empty — agents parse
stderr for the failure, stdout for results.
**Ask the owner:** none — this is a pure skill addition, but worth confirming agents read stderr JSON.

### T5 — Append-only registry deletes (design.md) vs git-synced soft-delete (storage reference)

**Tension.** design.md makes `aliases.jsonl`/`timeline.jsonl` append-only (good) but doesn't say how
records are *removed*, and `registry/` syncs via git across machines.
**Reconciliation:** soft-delete with tombstones (`deleted: true`) filtered from normal reads, GC'd only via
an explicit `studio registry compact`, so a git pull can't resurrect a deletion on another clone.
**Ask the owner:** Is `registry/` ever edited on more than one machine/clone concurrently? If strictly
single-clone, hard-delete would be acceptable and simpler — confirm before adding tombstone machinery.

### T6 — `library upgrade` re-pin & `voice assign` rebind: design.md says "confirm", skill demands a tier + scriptable token

**Underspecified.** §10 says upgrade "không tự đổi … nếu chưa confirm" but not how an agent confirms.
**Reconciliation:** library re-pin and overwriting a locked voiceprint are **severe** (type-the-name /
`--confirm=<preset@version>`); rebind is **moderate** (`--force`, or `--from <ch>` to scope as a new
persona). Under `--no-input` without the token → exit `9 ConfirmRequired` with the exact flag.
**Ask the owner:** Should a mid-novel voiceprint swap ever be allowed non-interactively at all, or is the
`--confirm` token sufficient guard given its blast radius?

### T7 — design.md keeps a `scoping.activeWindow` as a *prior only*; risk of it being misread as a candidate source

**Not a conflict, a guardrail.** The doc is explicit that the K-window is a disambiguation prior, not a
candidate source. The CLI surface keeps no flag that lets a caller use it as a candidate source; `--at` is
always the authoritative period key for resolution.
**Ask the owner:** none — flagged only so it isn't "fixed" later into a recency-based candidate flag.

---

### Notes / non-conflicts worth recording

- design.md's `noun verb` surface is already skill-compliant; I kept every command and only added the
  globally-required pieces (global flags, exit map, JSON error shape, secret handling, global config scope).
- `studio agent` as a second façade on the same core matches the skill's "agents are users too" exactly —
  no redesign needed, just the non-interactive `--auto-confirm` path for SoT writes.
- Roadmap commands (`thumbnail`, `video`) are specified to the same conventions but left out of the core
  build surface, matching design.md §11/§12 (YAGNI).
