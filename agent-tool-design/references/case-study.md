# Worked example: a visual-novel editor agent

A concrete walkthrough applying all the principles to a realistic agent. Useful as a template for any structurally similar system — domain editor, CMS, story builder, rule builder, config editor.

## Starting state

The agent is "Mina," an AI copilot for visual-novel creators who helps modify, improve, and extend stories through conversation. Tool-layer facts:

- System prompt duplicates the full node JSON Schema as prose (~5k tokens per request).
- A single `add_nodes` tool with a deep `oneOf` of 11 node variants (dialogue, narration, bg_change, show_char, hide_char, move_char, express, reset_stage, choice, goto, end).
- No server-side validation of `choice.target`, `dialogue.character_id`, or `show_char.expression`.
- Tool descriptions are one line each; no "when to call vs sibling tools."
- Tool responses include raw UUIDs for scenes and characters.
- No `response_format` control; every response is fully detailed.
- The `required` arrays in the prompt's schema copy have drifted from the tool's actual schema — they no longer match.

## Diagnosis against the pillars

- **Pillar 1 (right tools):** `add_nodes` is defensible — scenes are built as batches. But `choice` has distinct reference semantics (its `target` must resolve to a real scene). Candidate for splitting.
- **Pillar 2 (namespacing):** Flat list, no prefix. Low urgency while the tool count stays under 15.
- **Pillar 3 (meaningful context):** UUIDs in list/get responses are causing hallucinations when the agent references them in subsequent calls. Major issue.
- **Pillar 4 (token efficiency):** No response truncation. Schema duplication in the prompt wastes ~5k tokens per request.
- **Pillar 5 (descriptions):** Thin descriptions. Once a second node-adding tool is introduced, the agent will misroute without clearer boundary-setting.

## Other diagnostic observations

- **Schema-as-source-of-truth violation.** Prompt and tool schema disagree on `required` arrays. The agent gets contradictory contracts.
- **Reference integrity sits entirely in the prompt** ("choice/goto targets must reference valid scene IDs — use listScenes() to verify"). This is aspiration, not guarantee; nothing stops the agent from emitting `target: "scene_99"` that doesn't exist.
- **No `validate` tool.** After a batch of edits, the agent has no single-call way to check structural integrity. Each broken reference will only surface as a later per-tool error, increasing round-trips.

## Interventions, ordered by ROI

### 1. Delete the "## Node schema" section from the system prompt

- **Why first:** highest-impact, near-zero-risk.
- **Effect:** ~5k tokens saved per request. Eliminates drift between prompt and schema. Eliminates the "which contract wins?" ambiguity.
- **What stays in the prompt:** workflow order ("Call listScenes before creating a choice"), destructive-action policy, persona, and the writing guidelines section.
- **Pillars:** 5, and "schema as single source of truth."

### 2. Add server-side validation in `add_nodes`

- Validate `character_id`, `expression` (per-character), `choice.target` against current project state.
- On failure, return actionable error: `"Unknown character 'mari'. Existing characters: nobita, shizuka, doraemon. Call listCharacters() to confirm."`
- **Effect:** reference errors become self-healing loops instead of silent failures. Removes the need for the agent to remember prompt-level rules about reference validity.
- **Pillars:** 3 and 4 (actionable errors), plus reference integrity.

### 3. Replace UUIDs with human-readable slugs in responses

- List/get responses return `scene_id: "opening"`, not `"f47ac10b-58cc-..."`.
- Add `response_format: "concise" | "detailed"` so detailed responses still include UUIDs for consumers that need them.
- **Effect:** agent reasoning becomes more reliable on identifiers; cross-tool references are easier to emit correctly; token cost on concise mode drops.
- **Pillar:** 3.

### 4. Rewrite tool descriptions

- Include what each tool does, does NOT do, when to call siblings.
- Especially important: clear boundaries between `add_nodes` / `update_node` / `remove_nodes`, and between `update_scene` / `delete_scene`.
- Add format conventions to parameter descriptions (e.g., "`expression` must be an expression ID already declared for this character — use `getCharacter(id)` to enumerate").
- **Effect:** tool-selection accuracy up; invalid-parameter errors down.
- **Pillar:** 5.

### 5. Add a `validate` tool

- One read-only call that surfaces all structural issues at once: broken scene refs, invalid character/expression refs, unreachable scenes, duplicate IDs, rich-text formatting problems.
- The system prompt recommends calling it after non-trivial edits.
- **Effect:** saves many round-trips; gives the agent a clean "is the project healthy?" signal.
- **Pillars:** tool-set design (orient/validate layer).

### 6. Consider splitting out `add_choice` as a dedicated tool

- `choice` has unique reference semantics (cross-scene targets, branching). A dedicated tool with richer validation and a sharper description could reduce misroutes.
- Measure first with evals. Only ship if it moves the metric — this is optional optimization, not critical.
- **Pillar:** 1.

### 7. Dynamic enums for `character_id`, `target`, `expression`

- Generate the tool schema per-request with current-state enums.
- The agent physically cannot emit invalid references under strict mode.
- Tradeoff: breaks prompt caching. Weigh against traffic patterns.
- **Pillar:** 3 / reference integrity.

## End state

After 1-5 (the "core" interventions):

- System prompt is a compact policy document (~500 tokens, down from ~5k).
- Reference errors are self-healing via actionable messages.
- Agent reasons over human-readable identifiers.
- Tool selection is unambiguous because descriptions state boundaries.
- A single `validate` call gives a post-edit health check.

Interventions 6 and 7 are measured add-ons that may or may not pay off in a specific deployment. That determination comes from the evaluation loop, not from principle.

## What this case study illustrates more generally

- **High-ROI interventions are usually structural** (delete the duplicated schema, add server-side validation) rather than decorative (reword a description).
- **Schema-as-source-of-truth is almost always the first fix** when it's been violated, because it unblocks everything downstream.
- **A `validate` or `overview` tool is frequently missing** and always underrated. Agents spend too much time reconstructing state the server could summarize cheaply.
- **Name the destructiveness.** Even in this editor domain, `deleteScene` being obvious from the name reduces misclicks by the agent.
- **Some interventions need evals before shipping.** Don't guess whether a tool split helps; measure.
