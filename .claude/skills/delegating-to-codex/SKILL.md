---
name: delegating-to-codex
description: Use when delegating focused work to OpenAI's `codex exec` CLI — second-opinion diagnosis on a stuck bug, context-heavy investigation or refactor, screenshot or design-image analysis (`-i`), image asset generation (gpt-image-2), editing an existing image (overlay text, composite, regenerate a region), structured JSON extraction (`--output-schema`), parallel implementation in an isolated git worktree, repo code review (`codex exec review`), or LLM analysis embedded in a script. Trigger phrases include "get a second opinion", "analyze this screenshot", "generate an icon/banner", "edit this image / add a title", "delegate this to codex", "run a codex pass", or whenever one Claude-side diagnosis attempt has already failed.
---

# Delegating to Codex

## What this is for

`codex exec` is OpenAI's headless CLI — single-shot, no TUI, prints the final agent message to stdout. Use it as a *delegated specialist* when one of these is true:

- A different model would give a more useful second opinion than another Claude pass.
- The task would burn a large chunk of the current context window.
- The task is visual (a screenshot, mockup, layout image) and you need a model to look at it.
- The task needs a generated image asset (icon, banner, placeholder).
- The task is a self-contained sub-investigation whose result is one verdict, not a long collaboration.

If none of these apply, do the work yourself. Delegation has overhead — process spawn, prompt shaping, output parsing, verification. A 30-second edit is not worth that overhead.

## Prerequisite check (run once per session, only if uncertain)

```bash
codex --version    # expect ≥ 0.115 for image input, current is 0.130
```

If `codex` is not installed or the version is too old, stop and tell the user. Do not silently fall back to doing the task yourself — that hides a tooling problem.

If `codex exec` exits with an auth error, stop and direct the user to run `codex login`. Do not attempt other auth flows.

## When to delegate vs do it yourself

| Situation | Action |
|---|---|
| Single-file edit, clear scope, < 30 s of work | Do it yourself |
| Routine refactor inside one module | Do it yourself |
| Looked at the bug once, made one fix attempt, still failing | Delegate (second opinion) |
| Bug involves long stack trace or log file (> 200 lines) | Delegate (piped diagnosis) |
| User attached a screenshot of a UI bug, error dialog, or design | Delegate with `-i` |
| User asks for a placeholder asset, icon, banner, illustration | Delegate (image-gen) |
| User wants to modify an existing image (add title/watermark, swap region, restyle) | Delegate with `-i` + workspace-write |
| Repo-wide mechanical refactor across many files | Delegate in a worktree |
| Need a machine-readable verdict for a script or hook | Delegate with `--output-schema` |
| User explicitly says "use codex" / "ask codex" / "second opinion" | Delegate |

When in doubt and the task is non-trivial, delegate read-only first to get a verdict, then decide whether to apply the fix yourself or delegate write-mode.

## Core invocation patterns

Pick the pattern, copy the shape, fill in the prompt. Use the smallest sandbox that works.

### Pattern A — Second opinion (read-only)

```bash
codex exec -s read-only \
  "In src/auth/session.ts, the test 'refreshes silently on 401' is flaky. \
   Diagnose the root cause and propose one minimal fix. Output: \
   ROOT CAUSE: ...\nFIX: ...\nFILES TOUCHED: ..."
```

Capture stdout, quote the verdict, then decide. Do not paraphrase Codex's findings — the user wants the second opinion verbatim.

### Pattern B — Piped diagnosis

```bash
npm test 2>&1 | codex exec -s read-only \
  "Diagnose the failures above. Output one minimal fix and the file(s) it touches."
```

Piped stdin becomes a `<stdin>` block on top of the prompt. Use this whenever the context Codex needs is the output of another command — test failures, log tail, `git diff`, `grep` results.

### Pattern C — Screenshot / image analysis

```bash
codex exec -i ~/Downloads/bug-screenshot.png -s read-only \
  "Identify what's visually wrong here. State the most likely component file \
   in src/ and the CSS or markup change needed."
```

Multi-image compare (mockup vs current):

```bash
codex exec -i mockup.png -i current.png -s read-only \
  "List pixel-level differences and rank them by user-visible impact."
```

Formats: PNG, JPEG, GIF, WebP. Keep each image under 5 MB — Codex will reject or truncate larger files. If the user pastes a >5 MB screenshot, downscale with `sips -Z 2000` (macOS) or `convert -resize 2000x` (ImageMagick) before passing.

### Pattern D — Image asset generation

```bash
codex exec -s workspace-write \
  "Generate a 512x512 PNG icon for a 'daily quest' feature in a casual game — \
   simple, flat-color, transparent background. Save to assets/icons/daily-quest.png."
```

Always state the output path explicitly inside the prompt. Without it, Codex picks a path and the file is harder to find. `workspace-write` is the correct sandbox here because the deliverable *is* a new file; the path is bounded by the cwd.

### Pattern E — Parallel implementation in a worktree

```bash
git worktree add ../alt-impl HEAD
codex exec -s workspace-write -C ../alt-impl \
  "Implement <feature> per <spec>. Keep changes minimal. \
   Add tests in <test-dir>. Do not touch unrelated files."
# review the result:
git -C ../alt-impl diff main
# done? merge or discard:
git worktree remove ../alt-impl
```

Use this when you want a second independent attempt to diff against your own. Never run `workspace-write` against the user's primary working tree unless the user has explicitly asked — keep the blast radius inside the worktree.

### Pattern F — Structured JSON extraction

Write a JSON schema file, then:

```bash
codex exec --output-schema ./tmp/schema.json \
  -o ./tmp/result.json -s read-only \
  "Analyze src/payments/ and return the schema-conforming JSON."
```

Use this when the verdict has to feed a script, a hook, or another tool — not when a human is going to read it. For human-facing verdicts, plain stdout is shorter and cheaper.

### Pattern G — Resume / drill deeper

```bash
codex exec resume --last "Now focus on the race in onTransactionCommit and propose the fix."
```

Resume preserves Codex's prior session context — useful for iterative drilling without re-paying the setup tokens. Only the most-recent session is addressable with `--last`; for older sessions, pass the session id.

### Pattern H — Image editing (modify an existing image)

```bash
codex exec -s workspace-write -i path/to/input.png - <<'PROMPT'
Edit the attached image by <specific change, e.g., add a title in the empty sky area>.
Title text (verbatim): NOBITA
Subtitle (verbatim): Cuộc Phiêu Lưu Xuyên Thời Gian
Keep <invariants — characters, background, composition> completely unchanged.
Preserve the original resolution.
Save the edited image to <absolute output path>. Output only the path on a single line.
PROMPT
```

Combine `-i <input>` (Pattern C) with `-s workspace-write` (Pattern D) when the deliverable is a *modified* version of an existing image — adding a title, watermark, badge, swapping a region, restyling.

Two things to know:

- **Codex may composite via ImageMagick instead of regenerating.** For pure overlays (text, logo, badge) this is the right move — original pixels stay pixel-perfect. To nudge Codex toward composite, say "do not redraw or restyle the characters/background, only composite on top". For region edits where regeneration is required (inpaint, change subject, change lighting), say "regenerate only the affected area, preserve everything else".
- **Save to a new path, not over the input.** Codex's imagegen guidance is to save non-destructively unless the user explicitly asked to overwrite. Use a suffix like `-titled.png`, `-v2.png`, or `-edited.png`.

Pass the verbatim text (titles, taglines, copy) inside a heredoc — see the prompting tip on quote safety below.

## Flag quick-reference

| Flag | What it does | When to use |
|---|---|---|
| `-s read-only` | No file writes, no shell side-effects | Default. Diagnosis, review, second opinions. |
| `-s workspace-write` | Writes allowed inside cwd / `--add-dir` | Image gen with explicit save path, worktree implementation. |
| `-s danger-full-access` | No sandbox | Never, unless user typed those words. |
| `-i <file>` | Attach image(s) | Screenshots, mockups, design comparisons. Repeat or comma-separate for multiple. |
| `--json` | Emit JSONL event stream | Only when you need event-level data (token usage, tool calls). Otherwise stdout is final message only. |
| `-o <file>` | Mirror final message to a file | Long verdicts you want to keep, or scripted reads. |
| `--output-schema <file>` | Force structured JSON output | Verdict feeding another tool. |
| `-C <dir>` | Set working root | Worktree pattern, or analysing a sibling repo. |
| `--add-dir <dir>` | Extra writable directory | When the deliverable spans cwd and a sibling. |
| `-m <model>` | Override default model | Only when the user specifies a model. |
| `--ephemeral` | Don't persist session to disk | One-off runs you won't resume. |
| `--skip-git-repo-check` | Allow running outside git | Standalone scripts, scratch directories. |
| `--ignore-user-config` | Skip `~/.codex/config.toml` | Reproducible CI-style runs. |
| `resume --last "<prompt>"` | Continue most-recent session | Iterative drilling. |

## Sandbox rule (calibrated to risk)

- Default to `-s read-only` for anything where the deliverable is a verdict, not a file change.
- `-s workspace-write` is fine *automatically* when (a) the task produces a file (image-gen, generated config) and the prompt names the output path, OR (b) you're using `-C <isolated-worktree>`.
- For `-s workspace-write` directly against the user's primary cwd with no `-C`, confirm with the user first. The blast radius is everything in the repo.
- NEVER pass `-s danger-full-access` or `--dangerously-bypass-approvals-and-sandbox` unless the user has typed those exact words.

## Reading the output

Default stdout is *just the final agent message*. Progress and reasoning go to stderr — let it scroll past, don't try to parse it.

Capture and present pattern:

```
1. Run codex exec, capture stdout (and stderr separately if you want it).
2. Quote the verdict verbatim to the user — do not paraphrase or "improve" it.
3. If Codex marked something as an inference, uncertainty, or follow-up, preserve that distinction.
4. State your own next step: apply the fix? verify with a test? ask the user?
```

Use `--json` only when a downstream consumer actually needs the event stream. It's verbose and burns tokens for no benefit when a human is reading.

## Prompting Codex well

These are inline because they're short and load-bearing:

1. **Scope the directory.** Name files or directories Codex should look at: "In `src/auth/`, …". Without scoping, Codex wanders.
2. **State the success criterion.** "Tests pass" / "Builds cleanly" / "Returns the file path" — Codex stops when the criterion is met.
3. **Prefer "one minimal fix" over "improve".** "Improve the pipeline" yields sprawl. "Fix the failing test with the smallest change that works" yields a fix.
4. **Ask for an explicit verdict line.** End the prompt with the output shape you want ("Output: ROOT CAUSE: ... / FIX: ... / FILES TOUCHED: ..."). Easy to parse, easy to quote.
5. **Don't repeat what stdin already says.** If you piped test output, the prompt should be the *instruction*, not the data.
6. **Use a heredoc when the prompt contains quotes, non-ASCII, or special chars.** Inline `"..."` arguments get mangled by zsh/bash when they wrap embedded quotes or backticks (verbatim titles, JSON snippets, code blocks). Pass `-` as the prompt arg and pipe the body via `<<'PROMPT' … PROMPT` — single-quoted heredoc preserves the text verbatim, no escaping needed. This is also how you safely feed multi-line specs to Pattern H (image editing).

## Auth and failure handling

| Symptom | Action |
|---|---|
| `codex: command not found` | Tell the user. Don't fall back. |
| `codex exec` exits non-zero with auth message | Tell the user to run `codex login`. Don't improvise auth. |
| `codex exec` exits non-zero with a stderr message | Surface the most actionable stderr lines verbatim. Stop. Do not silently retry the task yourself. |
| Codex returns "I can't" or refuses | Quote the refusal to the user and ask how to proceed. Don't retry with a workaround unless asked. |

## Web search

Codex CLI has built-in web search. Don't use it. For one-shot info lookups, Claude's own `WebSearch` is faster, cheaper, and the result lands directly in your context where it can inform the next step. Reach for Codex only when the research and the code work need to happen together in the same delegated turn.

## Image generation details

- Default model is `gpt-image-2` (as of Codex CLI ≥ 0.124). It renders text at >99% accuracy, so it's viable for labelled diagrams.
- Image gen counts against Codex usage limits ~3–5× faster than a text turn. Don't generate placeholder assets speculatively.
- Always specify the output path in the prompt. Specify the format (PNG / JPEG / WebP), size (e.g., 512x512, 1024x1024), and whether transparency is required.
- Don't pass `-m gpt-image-2` or invent flags like `--image-size` or `--output` — they don't exist. The model auto-selects when the prompt asks for an image; the output path goes in the prompt text; the file goes where the prompt says.
- For batch generation (multiple variants), put one explicit save path per variant in the prompt.
- **Editing existing images can take two paths inside Codex.** When you pass `-i input.png` + workspace-write and ask for an edit, Codex may either (a) regenerate the image with gpt-image-2, or (b) composite locally via ImageMagick. Composite preserves the original pixels exactly — ideal for adding titles, watermarks, or badges. Regenerate is needed when you actually want pixels in the original area to change (inpaint, restyle, change lighting). Steer Codex with explicit wording: "do not redraw, only composite on top" vs "regenerate only the affected area, preserve everything else". See Pattern H.

## Common mistakes — STOP and reconsider

- **Delegating a 30-second edit.** Codex spin-up and verification cost more than the edit.
- **Treating Codex's verdict as ground truth.** Verify before applying: re-run the failing test, eyeball the diff, check the logic.
- **`-s workspace-write` against the user's primary cwd with no `-C`.** Blast radius is the whole repo.
- **`--json` when a human is reading.** Burns tokens, hides the actual message.
- **Forgetting `-i` for screenshot tasks.** Without it Codex is guessing from text alone.
- **Forgetting to specify the save path for image gen.** Output ends up somewhere unexpected.
- **Image > 5 MB passed as-is.** Downscale first.
- **Re-running with the same prompt after a failure.** Read stderr, change the prompt, or stop and ask the user.
- **Inline-quoting a prompt that contains `"`, backticks, or non-ASCII.** Shell mangles it and Codex gets garbage or nothing (look for `Reading prompt from stdin... No prompt provided`). Use the heredoc form — `codex exec ... - <<'PROMPT' … PROMPT`.
- **Overwriting the original image on an edit task.** Always save to a new path (`*-edited.png`, `*-v2.png`); preserves the input so you can iterate.

### Red flags — these thoughts mean STOP

| Rationalisation | Reality |
|---|---|
| "I'll degrade gracefully and debug locally if codex fails" | That hides the tooling problem from the user. Stop, surface stderr, point them to `codex login` or the install fix. |
| "I'll quickly check the file myself before delegating" | If the task is delegate-worthy, the read happens inside Codex. Skip the redundant local read unless you need it to *shape the prompt*. |
| "Codex's verdict matches my hypothesis, so I'll skip verification" | The match could be coincidence or the same wrong inference. Verify by re-running the test, not by re-reading the diagnosis. |
| "I'll pass `-s workspace-write` here, it's just one file" | One wrong write in cwd is a corrupted user state. Use `-C <worktree>` or `-s read-only`. |
| "I'll try `--model gpt-image-2` to force the image model" | That flag doesn't do what you think; image-gen auto-selects. Inventing flags fails silently and wastes a Codex turn. |

## Optional: the `openai-codex` plugin

If the user has the `openai-codex` plugin installed and explicitly invokes `/codex:rescue` or `/codex:setup`, those flows are theirs — don't override them with the patterns above. This skill is for *Claude-initiated* delegation during normal work, regardless of whether that plugin is installed.
