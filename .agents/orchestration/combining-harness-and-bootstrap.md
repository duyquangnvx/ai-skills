# Combining the harness and planning skills

`setting-up-harness` and `project-bootstrap` are deliberately independent — neither
references the other. This note is the *only* place their relationship lives. It is
not a skill; it has no frontmatter and is never auto-loaded.

## How to use it

Paste the snippet below into whatever you feed Claude Code when both skills are in
play — your load-skills prompt, a project `CLAUDE.md` include, or a one-off message
at the start of a setup session. It tells Claude how to layer the two without
duplicating files or re-introducing the lock-in the harness avoids.

## The snippet

```text
When setting up a new project, treat these two skills as layers, not alternatives:

- setting-up-harness owns the LIVING layer — CLAUDE.md, README, project rules,
  docs/architecture.md (system as-built), docs/decisions.md (revisable),
  progress.md, and per-story packets under docs/stories/ (in-flight notes). Run it first.
- project-bootstrap owns the FORWARD layer — roadmap.md (what ships, in what
  order) and progression.md (phase status). Run it after the harness, and only
  if the project is genuinely multi-phase with a shape clear enough to plan.

When combining:
- Don't duplicate. The harness owns architecture and decisions; do not generate
  project-bootstrap's architecture.md or decisions.md — point its roadmap and
  progression links at the harness's docs/ instead.
- Everything is revisable. The roadmap is a current best guess, not a contract;
  re-plan when implementation reveals what you couldn't know up front. Never
  treat a written phase or decision as binding.
- If the project shape is still being discovered, skip the roadmap entirely and
  let it emerge through per-feature planning.
```

## Why it is shaped this way

- **Division of labor avoids the file collision.** Both skills can produce
  `architecture.md` and `decisions.md`; left unmanaged you get two of each, with
  opposite doctrines. The snippet hands those to the harness and keeps only
  `project-bootstrap`'s unique forward view.
- **"Revisable, not binding" is the whole point.** It is what keeps an up-front
  roadmap from locking implementation into a plan made before the unknowns
  surfaced.
- **"Skip the roadmap if the shape is unclear"** matches the harness's emergent
  philosophy: plan as far as you can see, no further.
