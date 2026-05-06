# Blueprint Format Specification

The contract for every `<screen-id>.md` file. Read this before drafting.

## File structure

Every blueprint has, in this exact order:

1. **YAML frontmatter** — required metadata
2. **Five body sections** — fixed names, fixed order, lowercase headers (`## purpose`, `## ui`, `## modes`, `## acceptance`, `## notes`). All required except `notes`.

````markdown
---
<frontmatter>
---

## purpose
<prose>

## ui
```yaml
<nested UI tree>
```

## modes
```yaml
<modes / state machine>
```

## acceptance
```yaml
<BDD assertions>
```

## notes
<prose, optional>
````

Empty `modes` or `acceptance` use body `_none_` (still keep the header).

Section headers are extractable by regex: `^## (purpose|ui|modes|acceptance|notes)$`. Do not number them, do not change capitalization, do not add punctuation.

## Frontmatter schema

```yaml
---
id: <screen-id>              # required, camelCase, unique across project
type: scene | popup | shared # required
title: "<human label>"       # required
configVersion: <semver>      # optional; matches version: in _config.md frontmatter

orientation: portrait | landscape | both  # optional, default: both. Ignored for type: shared.
safeArea: true | false                    # optional, default: true. Ignored for type: shared.

modal: true | false        # popup only — true blocks input behind
dismissible: true | false  # popup only — tap-outside / back-button closes

parents: [<id>, ...]       # required for non-root scenes/popups (screens that navigate INTO this).
                           # For type: shared, parents = consumers (blueprints that include this cluster).
children: [<id>, ...]      # popups this screen can open; required if any are opened

sources:                   # optional — back-references to upstream docs
  - "<doc-path>#<anchor>"

dataBindings:              # optional — typed data sources this screen reads
  - <namespace>: <TypeName>

emits: [<event>, ...]      # bus events this screen publishes
listens: [<event>, ...]    # bus events this screen subscribes to
---
```

### Frontmatter validation rules

- `id` is unique across the entire `ui-blueprints/` tree.
- `modal` and `dismissible` are only valid when `type: popup` — error otherwise.
- `safeArea` and `orientation` are ignored (or error, depending on validator) when `type: shared`.
- `sources` paths must resolve to real anchors in project documentation.
- `parents` / `children` must reference real blueprint IDs.
- `configVersion`, if present, must match the `version:` declared in `_config.md`.

## Section contracts

### 1. `## purpose`

1-3 sentences of prose. Why does this screen exist? What is its role in the user/player experience? Cross-references to other screens or upstream specs use `[[wikilinks]]` (see `conventions.md`).

### 2. `## ui`

A single nested YAML tree. Top-level is the root container; children nest as containers or widgets.

```yaml
type: <container-type>     # required: VStack | HStack | ZStack | Grid | Scroll
<container-options>        # cols/rows/gap/axis as required by container type
children:
  - id: <node-id>          # optional; required if referenced by modes or acceptance
    type: <container-or-widget-type>
    <sizing>               # width/height/flex (per parent's stack semantics)
    <type-specific props>  # see vocabulary.md
    children: [...]        # only for container types
```

Universal rules:

- Container types, sizing units, widget types and their props — see `vocabulary.md`.
- `Spacer` is a leaf node used inside stacks for flexible empty space.
- Children of `ZStack` require `align:` (9-position).
- `bind:`, `visible:`, `enabled:` use bind paths and the boolean DSL — see `conventions.md`.
- `on:` is a map of event → action-tuple list. **Use only for state-independent side-effects.** Any action that triggers a state transition (`goto:`) lives in `## modes`, not on the widget.

The root container always fills its parent — no explicit `fill` directive.

### 3. `## modes`

Declarative state machine. Transitions live with their source mode.

```yaml
- id: <mode-id>                  # required, camelCase
  initial: true                  # exactly one mode must have initial: true
  final: true                    # optional; final modes have no outgoing transitions
  description: "<what this mode means>"
  enter:                         # optional; runs on entering this mode
    do:
      - <action>
  exit:                          # optional; runs on exiting this mode
    do:
      - <action>
  on:                            # optional; events handled in this mode
    - widget: <widget-id>        # widget event source
      event: <event-name>
      where: "<bool-expr>"       # optional guard (boolean DSL)
      do:                        # optional side-effects
        - <action>
      goto: <mode-id>            # optional transition target
    - event: <event-name>        # bus event source (must be in frontmatter listens)
      do:
        - <action>
      goto: <mode-id>
```

#### Action verb syntax

`do:` uses YAML block form. Flow form breaks on action arguments that contain commas inside `(...)`. Single-action lists with no embedded commas may stay inline: `do: [ ui.openPopup("settings") ]`. When an action argument contains `{...}` (object literal), single-quote-wrap the whole action: `- 'ui.openPopup("x", { result: "y" })'`.

Validation:

- Exactly one mode has `initial: true`.
- Modes with `final: true` cannot be the source of any `goto:`.
- Every `goto:` target references a declared mode in this file.
- Every `widget:` references a real widget id in `## ui`.
- Every bus `event:` appears in frontmatter `listens`.
- Every action verb is declared in project `_config.md`.

If a screen has no state changes (e.g. a pure shared widget cluster), use `_none_`.

### 4. `## acceptance`

BDD-style assertions.

```yaml
- id: <U-prefix-id>             # default scheme: U-<screen>-<n>
  given: "<arrange>"
  when: "<act>"
  then: "<assert>"
  test_hint: "unit | UI E2E | integration"   # optional
```

Maps to test cases: Given→Arrange, When→Act, Then→Assert. Acceptance IDs are unique across the project so they can be cross-referenced from upstream specs and test results.

If a screen has no assertions worth recording (rare; usually shared clusters with no behavior), use `_none_`.

### 5. `## notes`

Optional prose. Edge cases, rationale, animation contracts (push to `DESIGN.md` if extensive), open questions, links to discussions. The only free-form section. Use `[[wikilinks]]` for cross-references.

## YAML island parsing

Each YAML island is delimited by a fenced ` ```yaml ` block immediately after a section header. There is exactly one YAML island per structured section (`ui`, `modes`, `acceptance`). Multiple islands per section are an error. Other content between header and island is also an error.

For `_none_`, write the literal token `_none_` as plain prose between the header and the next header — no fence:

```markdown
## modes

_none_

## acceptance
```

The validator parses each YAML island independently against its sub-schema in `blueprint.schema.yaml`.
