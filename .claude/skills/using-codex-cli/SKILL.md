---
name: using-codex-cli
description: Use when calling the OpenAI Codex CLI from a script or agent — asking Codex/GPT for a second opinion, delegating a coding task, running a code review, or resuming a Codex session; also when codex hangs, writes files unexpectedly, or burns tokens on a trivial prompt
---

# Using Codex CLI

## Overview

Bare `codex` opens an interactive TUI — never run it from a script or agent; use `codex exec`. Always pin `--sandbox` explicitly: otherwise the run inherits the user's `~/.codex/config.toml` defaults, which may be `workspace-write` — wrong for a read-only question.

Default model settings: `-m gpt-5.5 -c model_reasoning_effort=high`. Drop to `-c model_reasoning_effort=low` for trivial prompts.

## Quick reference

| Goal | Command |
|---|---|
| Question / second opinion | `codex exec -m gpt-5.5 -c model_reasoning_effort=high --sandbox read-only "..."` |
| Delegate a coding task | `codex exec -m gpt-5.5 -c model_reasoning_effort=high --cd DIR --sandbox workspace-write "..."` |
| Follow-up with context kept | `codex exec resume --last "..."` |
| Review working tree changes | `codex review --uncommitted` |
| Review vs branch / commit | `codex review --base main` / `codex review --commit SHA` |
| Trivial task, keep it cheap | add `-c model_reasoning_effort=low` |
| Capture just the answer | add `-o /path/answer.md` (writes last message to file) |
| Machine-readable output | add `--json` (JSONL events) or `--output-schema FILE` |
| Run outside a git repo | add `--skip-git-repo-check` |
| Don't save the session | add `--ephemeral` |
| Diagnose install/auth | `codex doctor` |

Sandbox modes: `read-only`, `workspace-write`, `danger-full-access`. Pick the weakest that does the job.

**workspace-write caveat:** besides the workdir, `/tmp` and `$TMPDIR` are writable by default. To confine writes strictly to the workdir add:
`-c sandbox_workspace_write.exclude_tmpdir_env_var=true -c sandbox_workspace_write.exclude_slash_tmp=true`

## Reading the output

- The answer is the final `codex` block on stdout; with `-o FILE` you get only the last message, clean — prefer it over parsing stdout.
- Harmless noise to ignore: `Reading additional input from stdin...` (still pass the prompt as an argument), `ERROR rmcp::transport::worker ... /mcp` lines (user-configured MCP server unreachable), and the `tokens used` footer.

## Common mistakes

| Mistake | Fix |
|---|---|
| Bare `codex "..."` from a script | Launches the TUI, hangs without a TTY — use `codex exec` |
| Omitting `--sandbox` for a question | Inherits user default (often workspace-write) — pin `read-only` |
| Default reasoning effort on trivial prompts | Add `-c model_reasoning_effort=low` |
| Re-explaining context in a follow-up | `codex exec resume --last "..."` continues the session |
| Assuming workspace-write only writes the workspace | `/tmp` and `$TMPDIR` are writable too — see caveat above |
| `--dangerously-bypass-approvals-and-sandbox` for convenience | Only valid inside an already-sandboxed environment |

If a flag is rejected, check `codex exec --help`.
