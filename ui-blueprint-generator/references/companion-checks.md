# Companion Checks

Cross-file and structural rules that JSON Schema cannot express. A companion validator script (or manual review) enforces these. Group by where the check runs.

## Per-blueprint structural checks

- **Single `initial` mode.** Exactly one entry in `## modes` has `initial: true`.
- **Final modes have no outgoing transitions.** A mode with `final: true` must not appear as a `goto:` source.
- **`goto:` targets exist.** Every `goto: <id>` references a mode declared in the same file.
- **Widget references exist.** Every `widget: <id>` in mode-level `on:` resolves to a widget id in `## ui`.
- **ZStack children require `align`.** Every direct child of a `ZStack` declares `align:` (9-position).
- **ZStack children at most one of width/flex.** A child in a ZStack may use `width: fill` or fixed sizing, never `flex:`.
- **`offset:` magnitude warning.** Warn when `offset.x` or `offset.y` exceeds 8dp — this is usually misuse for absolute positioning.
- **Hard-coded `text:` literals.** `text:` in a `Text` widget may be a symbol (`+`, `x`, `→`, etc.) or digits only. Anything natural-language is a violation; use `bind: { text: "i18n.<key>" }`.
- **`fmt` placement.** `fmt:` must live inside `bind:`, not as a sibling of `bind:`.
- **`Custom` requires `name`.** `type: Custom` without `name:` is invalid.
- **`Include` requires `ref`, forbids `name`.** `type: Include` must have `ref:`; presence of `name:` is invalid.
- **Unique IDs within file.** Every `id:` (widget, region, mode, acceptance) is unique per file.
- **YAML island count.** Each of `## ui`, `## modes`, `## acceptance` has exactly one fenced ```yaml island, OR the body is `_none_` (no fence).

## Project-wide checks

- **Unique screen IDs.** Frontmatter `id` is unique across the entire `ui-blueprints/` tree.
- **Unique acceptance IDs.** Acceptance `id:` is unique across the project.
- **`parents` / `children` reciprocity.** If A lists B in `children`, B must list A in `parents`. (For `type: shared`, `parents` denotes consumers — same reciprocity rule applies if the consumer uses `type: Include, ref: <shared-id>`.)
- **`Include` references resolve.** Every `type: Include` `ref:` must point to a `type: shared` blueprint that exists in the project.
- **Wikilink targets exist.** `[[scenes/<id>]]`, `[[popups/<id>]]`, `[[shared/<id>]]`, `[[U-<...>]]` resolve to real files / acceptance IDs.

## Config-conformance checks

- **Action verbs declared.** Every verb used in `do:`, `enter.do:`, `exit.do:` is in `_config.md` `## Action verbs`.
- **Bind namespaces declared.** Every bind path's leading namespace is declared in `_config.md` `## Bind namespaces` (or is `data`/`item`/`props` for shared / list / include contexts).
- **Widget types in scope.** Every `type:` in `## ui` is either universal (see `vocabulary.md`) or declared in `_config.md` `## Project widget types` (or is `Custom` / `Include`).
- **Style tokens resolve.** Every token referenced in `style:` exists in the project's token catalog (or `DESIGN.md`).
- **Config version match.** When a blueprint declares `configVersion:`, it must equal `_config.md` `version:`. Mismatch is a stale-blueprint signal.

## Bus-event checks

- **`emits` and `listens` complete.** Every event used as `event:` in mode-level `on:` is in frontmatter `listens`. Every event passed to `emit("<name>", ...)` is in frontmatter `emits`.
- **Event names follow convention.** Bus events match `<scope>.<verb>` in camelCase (see `conventions.md`).

## Recommended runtime behavior

- Schema-only failures fail the validator.
- Companion warnings (e.g. `offset` > 8dp, hard-coded text not whitelisted) do not fail by default but appear in CI output. A project may promote warnings to failures via `_config.md`.
- A re-validation pass runs against all blueprints whenever `_config.md` changes (verb removed, namespace renamed, version bumped).
