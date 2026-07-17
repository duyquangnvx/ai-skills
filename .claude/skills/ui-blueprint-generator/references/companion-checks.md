# Companion Checks

Cross-file and structural rules that JSON Schema cannot express. A companion validator script (or manual review) enforces these. Group by where the check runs.

## Per-blueprint structural checks

- **Single `initial` mode.** Exactly one entry in `modes` has `initial: true`.
- **Final modes have no outgoing transitions.** A mode with `final: true` must not appear as a `goto:` source.
- **`goto:` targets exist.** Every `goto: <id>` references a mode declared in the same file.
- **Widget references exist.** Every `widget: <id>` in mode-level `on:` resolves to a widget id in `ui`.
- **ZStack children require `align`.** Every direct child of a `ZStack` declares `align:` (9-position).
- **ZStack children at most one of width/flex.** A child in a ZStack may use `width: fill` or fixed sizing, never `flex:`.
- **`offset:` structural-use warning.** `offset` is for anchor-tweak on a ZStack child (badge inset, focus ring, tooltip arrow). Warn when `offset.x` or `offset.y` magnitude exceeds ~5% of the parent's resolved dimension along that axis — the value is almost always structural positioning that should be expressed via `padding` or stack restructure instead.
- **Hard-coded `text:` literals.** `text:` in a `Text` widget may be a symbol (`+`, `x`, `→`, etc.) or digits only. Anything natural-language is a violation; use `bind: { text: "i18n.<key>" }`.
- **`fmt` placement.** `fmt:` must live inside `bind:`, not as a sibling of `bind:`.
- **`Custom` requires `name`.** `type: Custom` without `name:` is invalid.
- **`Include` requires `ref`, forbids `name`.** `type: Include` must have `ref:`; presence of `name:` is invalid.
- **Unique IDs within file.** Every `id:` (widget, region, mode, acceptance) is unique per file.
- **Empty `modes` / `acceptance` use `null`.** Use the YAML literal `null` (not `[]`, not the legacy `_none_` token).

## Project-wide checks

- **Unique screen IDs.** Frontmatter `id` is unique across the entire `ui-blueprints/` tree.
- **Unique acceptance IDs.** Acceptance `id:` is unique across the project.
- **`parents` / `children` reciprocity.** If A lists B in `children`, B must list A in `parents`. (For `type: shared`, `parents` denotes consumers — same reciprocity rule applies if the consumer uses `type: Include, ref: <shared-id>`.)
- **`Include` references resolve.** Every `type: Include` `ref:` must point to a `type: shared` blueprint that exists in the project.
- **`Include` props/data shape match.** Every `data.<key>` used inside a shared blueprint's subtree must correspond to a key supplied by every consumer's `Include props:`. Mismatched keys silently render empty.
- **Wikilink targets exist.** `[[scenes/<id>]]`, `[[popups/<id>]]`, `[[shared/<id>]]`, `[[U-<...>]]` resolve to real files / acceptance IDs.

## Behavior / anti-pattern checks

- **Goto-self / unreachable mode loops.** A mode whose only outgoing transitions return to itself (without explicit `description:` flagging this is intentional), or any mode unreachable from the `initial: true` mode, is flagged.
- **Final mode reachability.** At least one path from the initial mode reaches a `final: true` mode (if any final mode exists).
- **Nested same-axis Scroll.** A `Scroll` node with the same `axis` as an ancestor `Scroll` causes gesture conflict — flagged.
- **`data.set` + `emit` on overlapping paths.** Within a single `do:` block, a `data.set("foo.bar", ...)` followed (or preceded) by an `emit(...)` whose payload references `foo.bar` has undefined ordering across renderer batching. Flagged unless the action list has a documented ordering note.
- **Per-frame bind on time-varying values.** A `bind: { text: "<path>" }` whose source declares `tick`-rate updates (e.g. `state.elapsedMs`) without `fmt:` quantization is flagged — bind to a quantized field (e.g. `state.timer` formatted `{mm:ss}`) instead.
- **Modal popup dismiss path.** Every popup with `modal: true` must have at least one outgoing `goto:` to a `final:` mode OR `dismissible: true` in frontmatter — otherwise the popup can wedge.
- **Missing i18n fallback.** Every `i18n.*` bind path used in `bind.text` should have a default-locale fallback declared somewhere in the project's i18n source. Surfaced as a warning if the project supplies an i18n key index.

## Config-conformance checks

- **Action verbs declared.** Every verb used in `do:`, `enter.do:`, `exit.do:` is in `_config.yaml` `actionVerbs`.
- **Bind namespaces declared.** Every bind path's leading namespace is declared in `_config.yaml` `bindNamespaces` (or is `data`/`item`/`props` for shared / list / include contexts).
- **Widget types in scope.** Every `type:` in `ui` is either universal (see `vocabulary.md`) or declared in `_config.yaml` `projectWidgets` (or is `Custom` / `Include`).
- **Style tokens resolve.** Every token referenced in `style:` exists in the project's token catalog (or `DESIGN.md`).
- **Config version match.** When a blueprint declares `configVersion:`, it must equal `_config.yaml` `version:`. Mismatch is a stale-blueprint signal.

## Bus-event checks

- **`emits` and `listens` complete.** Every event used as `event:` in mode-level `on:` is in frontmatter `listens`. Every event passed to `emit("<name>", ...)` is in frontmatter `emits`.
- **Event names follow convention.** Bus events match `<scope>.<verb>` in camelCase (see `conventions.md`).

## Recommended runtime behavior

- Schema-only failures fail the validator.
- Companion warnings (e.g. structural-use `offset`, hard-coded text not whitelisted) do not fail by default but appear in CI output. A project may promote warnings to failures via `_config.yaml`.
- A re-validation pass runs against all blueprints whenever `_config.yaml` changes (verb removed, namespace renamed, version bumped).
