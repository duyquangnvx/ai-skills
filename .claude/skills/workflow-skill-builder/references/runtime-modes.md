# Runtime Modes

Workflow skills run in two distinct modes. The phase code is the same in both — only the wrapper differs.

## Interactive mode

User invokes the skill via `/skill <name>` or a natural-language prompt. They watch progress, can interrupt, and may want to resume or rerun individual phases.

The generated SKILL.md must include:

### Resume section

```markdown
## Resume

If a previous run left intermediate files in `data/`, the skill detects them
and skips phases whose outputs are already present.

To force a rerun of a specific phase:
1. Delete `data/<phase>/` for that phase.
2. Re-invoke the skill.

To rerun from a specific phase forward:
1. Note the phase number.
2. Invoke with prompt: "resume from phase N — earlier outputs are in data/".
```

### Phase isolation

Each phase reads its inputs from a predictable path and writes outputs to a predictable path. No phase reads orchestrator-process state — only files on disk.

This is the property that makes resume work. It also lets the user step in mid-run, edit a file, and continue.

## Headless mode

Pipeline runs unattended — cron, CI, scheduled remote agent. No human is watching. Output reaches humans some other way.

The generated SKILL.md must include:

### Bash and container timeouts

See `timeout-layers.md`, Layers 3 and 4.

### Recovery agent block

```markdown
## Recovery

If the main run is killed by the Layer 3 bash timeout, a second invocation
salvages what's on disk:

1. Inspect `data/` for partial outputs.
2. Identify the last phase that completed by looking at the latest .json files.
3. Produce a degraded report listing what completed and what did not.
4. Mark the run as "incomplete — partial recovery".

The recovery invocation runs after the main job is killed, before the
container deadline fires. It produces the same output artifacts the main
run would have produced, just with degraded content.
```

### Delivery block

Headless runs cannot show a UI to the user. The skill must end with one of:

- **Git branch + PR.** The orchestrator creates a branch, commits the report and state files (e.g., `seen.txt`), pushes, opens a PR. The PR description summarizes the run.
- **Static file output.** Write the final report to a known location (e.g., `output/report-<date>.md`) for downstream tooling or a viewer to pick up.
- **Webhook post.** Ping an external endpoint with a summary payload and a URL to the report.

Pick one and inline the exact commands in the generated SKILL.md. Avoid speculative "or" — commit to a delivery method.

### Why GitHub-as-UI works

For non-technical reviewers, a PR is a familiar surface:

- The report shows as rendered markdown.
- State files (a "seen" list, a config snapshot, etc.) version cleanly.
- PR comments are a natural feedback channel.
- Approval = merge = the run is acknowledged.

No dashboard install, no metrics endpoint, no auth dance. GitHub is the database, the UI, and the audit log. Use it when the reviewer is a person, not another service.

## Supporting both modes

A workflow skill that targets both modes:

- Uses interactive-style phase isolation (so resume works in either mode).
- Includes recovery and delivery blocks (used only when headless).
- Detects runtime via a flag (`--headless`) or env var, OR
- Documents both invocation patterns at the top and trusts the caller to use the right one.

Simplest path: write the skill for headless, let interactive users just watch it run. Resume still works because phase isolation is identical. This is the default for the workflow-skill-builder unless the user has a reason to bias toward interactive.
