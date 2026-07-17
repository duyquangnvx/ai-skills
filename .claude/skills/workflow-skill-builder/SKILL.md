---
name: workflow-skill-builder
description: |
  Build a new SKILL that orchestrates a multi-phase, repeatable workflow inside Claude Code — phases written in document order, parallel subagents spawned via the Task tool, results polled from the filesystem (.json success / .error failure), with explicit timeout layers and never-fully-fail semantics. Use this skill when the user wants to turn a repeatable multi-step process into a self-contained skill folder that can be invoked manually or run headless. Trigger phrases include "build me a workflow skill", "convert this pipeline into a skill", "scaffold an orchestrator skill for X then Y then Z", "create a skill that spawns parallel agents", "make a Claude Code workflow engine for ...", "tạo skill cho workflow X", "build skill pipeline", "skill cho quy trình lặp lại". Do NOT use for single-step skills, technique or pattern reference docs, or feature-level code generation. Do NOT regenerate over an existing skill — read it first and propose surgical edits. The output is a new folder under .claude/skills/<generated-name>/ containing SKILL.md, agent definitions, helper script signatures, and per-pipeline conventions.
---

# Workflow Skill Builder

Build a self-contained SKILL that orchestrates a multi-phase workflow inside Claude Code. The generated skill follows the **document-order = dependency graph** pattern: phases run in the order they appear in SKILL.md, with optional parallel fan-out via subagents and filesystem-based message passing.

## What this skill produces

A new folder under `.claude/skills/<generated-name>/` containing:

| File | Role |
|---|---|
| `SKILL.md` | The orchestrator — phase definitions, fan-out logic, poll loops, error handling |
| `agents/<role>.md` | Subagent definitions (one per role: scanner, classifier, proposer, transformer, ...) |
| `lib/<name>.py` | Python helpers — signature, docstring, example call. Body is `NotImplementedError` for the user to fill |
| `references/conventions.md` | Per-pipeline conventions (output format, schemas, naming) |

The split is deliberate: **Python does mechanics, agents do judgment.** A scanner agent reads input and decides "is this relevant?" — it does not write the HTTP fetch code (that's a helper). A classifier reads an item and produces a score — it does not invoke an external API to do the scoring.

## Layer this skill operates at

| Layer | Concern | Owner |
|---|---|---|
| Use-case spec | What pipeline ships, why, what success looks like | User — input to this skill |
| **Workflow skill** | **Phase decomposition, subagent roles, filesystem bus, timeouts, output delivery** | **This skill** |
| Domain code | The actual body of `lib/*.py` — parsing, API calls, transforms | User — out of scope |

This skill MUST NOT invent domain logic. If the user says "scrape source X", produce a `scanner` agent and a `fetch_source.py` helper signature — never the body of `fetch_source.py`. That belongs to the user.

## How to use this skill

Run the seven-phase interview below. Each phase produces decisions written into a working draft. Phase 7 generates files. **Confirm with the user at the end of each phase before proceeding.** Refuse to skip ahead even when the user pushes — the interview is the design.

Read the reference docs as the relevant topic comes up:

- `references/orchestration-pattern.md` — phase-order, fan-out, polling — the core mental model
- `references/subagent-design.md` — agent frontmatter, tool selection, model choice, permission mode
- `references/filesystem-bus.md` — file naming, atomic writes, poll loop patterns
- `references/timeout-layers.md` — the four layers explained
- `references/resilience-patterns.md` — never-fully-fail, anti-coding instruction, fallback chains
- `references/runtime-modes.md` — interactive vs headless: what differs

## Phase 1: Discover the pipeline

Ask three questions in sequence. Do not batch them.

1. "In one sentence, what does the pipeline do end to end?"
2. "List the natural phases in order. Use verbs (scan, enrich, classify, transform, report, deliver)."
3. "For each phase, is it single-step or fan-out across many items?"

Capture into a working sketch:

```
Pipeline: <one-sentence>
Phases:
  1. <verb>    [single | fan-out × N]
  2. <verb>    [single | fan-out × N]
  ...
```

Reject vague answers. "Process the data" is not a verb sequence — push for concrete steps. If the user can't list phases, the pipeline is not ready to be a skill yet.

Show the sketch to the user. Get explicit confirmation before Phase 2.

## Phase 2: Split mechanics from judgment

For each phase, ask: "What part is mechanical (deterministic, scriptable) and what part needs judgment (LLM reasoning)?"

Capture as a table:

```
Phase     | Python helper           | Agent role
----------+-------------------------+----------------------
scan      | fetch_<source>.py       | scanner
enrich    | fetch_detail.py         | (none — pure mechanical)
classify  | (none)                  | classifier
report    | render_report.py        | (none)
```

A phase may be pure-mechanical (no agent), pure-judgment (no helper), or both. Be explicit when there is no agent or no helper.

The anti-coding rule applies to every judgment agent. See `references/resilience-patterns.md`.

## Phase 3: State and output design

Ask:

1. "Where do intermediate files live? Suggested: `data/<phase>/<source-or-item>/<run-id>.json`"
2. "What is the final output? Markdown report, JSON dataset, pull request, posted to an API, written to a directory?"
3. "Does the pipeline need persistent cross-run state — for example a 'seen' list to dedupe, or a running history file?"

Filesystem bus convention: **`.json` = success, `.error` = failure**, one file per agent task. The orchestrator polls these instead of reading agent stdout. See `references/filesystem-bus.md`.

## Phase 4: Resilience choices

For each phase that can fail, ask: "If the primary method fails, what is the fallback?"

Generate a fallback table — one sentence per phase, no retry-count specifics. Examples of phrasing shape:

- "If the helper returns fewer items than scanned, use a Claude-driven fallback for the failed ones."
- "If the parser fails on the response, log the raw response and continue with what worked."
- "If the classifier times out on item X, mark it as classify-failed and keep the rest."

The skill must include the **never-fully-fail rule**: even a fully broken run produces a report listing what broke. See `references/resilience-patterns.md`.

## Phase 5: Timeout layers

Walk the user through the four layers. Ask only the questions that match their runtime mode (from Phase 6 if already known, otherwise ask both).

1. **`max_turns` per agent** — start at 20 for classification, raise for multi-step research.
2. **Wall-clock cap per phase** — how long before the orchestrator moves on with whatever finished.
3. **Bash `timeout` for the whole job** — headless only.
4. **Container deadline (`activeDeadlineSeconds` or equivalent)** — deployed only.

Capture as a table to inline near the top of the generated SKILL.md. See `references/timeout-layers.md`.

## Phase 6: Runtime mode

Confirm the modes the generated skill must support:

- **Interactive**: user invokes via `/skill`, can resume from a phase, may rerun one phase.
- **Headless**: runs unattended (cron, CI, scheduled remote agent), output reaches humans via PR / file / webhook, a recovery agent salvages partial state if the main run dies.

For interactive mode, the generated SKILL.md gets a "resume" section. For headless mode, it gets a "recovery" section and a "delivery" section. For both, write the skill for headless and let interactive users just watch it run — resume still works because phase isolation is identical. See `references/runtime-modes.md`.

## Phase 7: Generate files

Use the templates in `assets/`. Order of operations:

1. Create folder `.claude/skills/<generated-name>/` and subdirs `agents/`, `lib/`, `references/`.
2. Fill `assets/SKILL.md.template` → `<generated-name>/SKILL.md` with phase blocks rendered from `assets/phase-block.md.template`, the failure-handling block, the resume or recovery section, and the delivery block.
3. For each agent role identified in Phase 2: fill `assets/agent-definition.md.template` → `<generated-name>/agents/<role>.md`. Pick tools and model conservatively (see `references/subagent-design.md`).
4. For each helper identified in Phase 2: fill `assets/helper-script.py.template` → `<generated-name>/lib/<name>.py`. Include signature, docstring, example call, and `raise NotImplementedError("Domain logic — implement based on: <one-sentence purpose>")` as the body.
5. Write `<generated-name>/references/conventions.md` summarizing the decisions from Phase 3 (output format, schemas, naming patterns).

After generation, run a structural check:

- Every phase referenced in SKILL.md has a corresponding agent file (if it spawns one) and helper (if it needs one).
- Every subagent's tool list is minimal — `Read`, `Write`, `Bash` plus only what's justified.
- The "never-fully-fail" block is present at the end of SKILL.md.
- No domain logic lives inside helper bodies — only `NotImplementedError`.
- No mention of domain specifics from any single project — keep examples generic.

Report back to the user with a tree of created files and the suggested invocation command.

## Common mistakes to catch

- **Inventing domain logic.** Refuse to write the body of `fetch_source.py`. Refuse to specify classifier rubric questions. Push back to the user.
- **Skipping the fan-out question.** Always ask whether a phase is single or fan-out. The default assumption (single) leads to skills that do not scale.
- **Forgetting the poll loop.** When a phase fans out, the next phase needs a poll block. Without it, the orchestrator reads agent stdout and context explodes.
- **Over-specified retry logic.** "Three retries with exponential backoff" is engineer-speak. The one-sentence English instruction "if the helper fails, try the Claude fallback for the failed items" is what works here.
- **Missing the never-fully-fail rule.** A skill that crashes on first error is worse than one producing an "everything broke" report. Always include the rule.
- **Mentioning a specific domain.** Templates and reference material stay generic. Examples like "scan sources" or "transform records" are fine. Specific product names, file formats unique to one project, or company jargon are not.
- **Regenerating over an existing skill.** If the user invokes this skill on a folder that already exists, read the existing files first and propose surgical edits — do not overwrite.

## When NOT to use this skill

- Single-step skill (no phases) — write a normal skill directly.
- Reference, pattern, or technique skill (documentation only) — follow the writing-skills approach instead.
- Feature-level code generation — use feature-dev:feature-dev.
- Updating an existing workflow skill — read its files first, propose edits, do not regenerate.

## After generation

The generated skill is a draft. Walk the user through:

1. Filling in helper bodies (each has `NotImplementedError` with a one-line hint).
2. Running phase 1 in isolation as a smoke test before wiring up later phases.
3. Tuning `max_turns` empirically per agent — adjust after observing real runs.
4. Tightening agent descriptions if the orchestrator picks the wrong subagent for a job.

The "develop and run blend together" property of Claude Code (see `references/resilience-patterns.md`) means the user can edit the generated SKILL.md while running it. Encourage this — corrections discovered at runtime should be committed back into the skill.
