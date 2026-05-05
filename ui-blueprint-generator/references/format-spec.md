# Blueprint Format Specification

The contract for every `ui-spec.<screen-id>.md` file. Read this before drafting.

## File structure

Every blueprint file has, in this exact order:

1. **YAML frontmatter** — required metadata (delimited by `---`)
2. **Eight body sections** — fixed names, fixed order, lowercase headers (`## purpose`, `## layout`, ...). All required except `notes`.

```markdown
---
<frontmatter>
---

## purpose
<prose>

## layout
\```yaml
<layout YAML island>
\```

## widgets
\```yaml
<widgets YAML island>
\```

## states
\```yaml
<states YAML island>
\```

## actions
\```yaml
<actions YAML island>
\```

## animations
\```yaml
<animations YAML island>
\```

## acceptance
\```yaml
<acceptance YAML island>
\```

## notes
<prose, optional content; section header is required>
```

Empty sections still keep their header. Body is `_none_`.

Section headers are extractable by regex: `^## (purpose|layout|widgets|states|actions|animations|acceptance|notes)$`. Do not number them, do not change capitalization, do not add punctuation.

## Frontmatter schema

```yaml
---
id: <screen-id>              # required, snake_case or camelCase, must be unique across project
type: scene | popup | shared # required
title: "<human label>"       # required
zIndex: <int>                # required for type=scene|popup; forbidden for type=shared
                             #   - type=scene  → zIndex == 0 (or in 0..99)
                             #   - type=popup  → zIndex == 100 (or in 100..199)

orientation: portrait | landscape | both  # optional, default: both
safeArea: true | false                    # optional, default: true

modal: true | false        # popup only — true blocks input behind
dismissible: true | false  # popup only — tap-outside / back-button closes

extends: <blueprint-id>    # optional — inherit base blueprint
parents: [<id>, ...]       # screens that can navigate INTO this; required for non-root scenes/popups
children: [<id>, ...]      # popups this screen can open; required if any are opened

gdd:                       # optional — back-references to upstream sources
  - "<doc-path>#<anchor>"

dataBindings:              # optional — data sources this screen reads (declared types help downstream)
  - <namespace>: <TypeName>

emits: [<event>, ...]      # events this screen publishes
listens: [<event>, ...]    # events this screen subscribes to
---
```

### Frontmatter validation rules

- `id` is unique across the entire `ui-blueprints/` tree.
- `zIndex` constraints by type (above) are enforced.
- `modal` and `dismissible` are only valid when `type: popup` — error otherwise.
- `gdd` paths must resolve to real anchors in the project's documentation.
- `parents` / `children` must reference real blueprint IDs.
- `extends` must reference a real blueprint that has compatible `type`.

## Section contracts

### 1. `## purpose`

1-3 sentences of prose. Why does this screen exist? What is its role in the user/player experience? Cross-references to other screens or upstream specs use `[[wikilinks]]` (see `conventions.md`).

### 2. `## layout`

A single YAML island declaring **structural skeleton** only — containers and regions. No widgets, no content.

```yaml
root: { type: <container-type>, <container-options> }
regions:
  - { id: <region-id>, <sizing>, <container-options> }
  - ...
```

The root container always fills its parent — no explicit `fill` directive.

Each region is a child of root with a sizing declaration. Regions can themselves be containers if a screen needs nested layout (rare; usually a flat region list is enough).

See `vocabulary.md` for container types and sizing units.

### 3. `## widgets`

Flat YAML list of widgets, each placed in a declared region.

```yaml
- id: <widget-id>
  type: <widget-type>
  region: <region-id>            # which Layout region it sits in
  align: <9-position>            # for ZStack regions; optional otherwise
  <widget-specific props>
  bind: { <field>: <bind-path>, fmt: "<format>" }   # optional
  visible: { bind: "<bool-expr>" }                  # optional
  enabled: { bind: "<bool-expr>" }                  # optional
  on:                                                # optional
    <event>: [ <action-tuple>, ... ]
  children: [ ... ]                                  # only for container-typed widgets
```

A widget tree is allowed when a widget is itself a container, but prefer flat: hoist sub-structure into Layout regions whenever possible. Diffs stay smaller.

See `vocabulary.md` for widget types and props.

### 4. `## states`

Declarative state machine.

```yaml
states:
  - id: <state-id>
    description: "<what this state means>"
    initial: true | false       # exactly one state must have initial: true
    final: true | false         # final states have no outgoing transitions; optional
    enter: { do: [ <action-tuple>, ... ] }   # optional; same shape as ## actions items
    exit:  { do: [ <action-tuple>, ... ] }   # optional; same shape as ## actions items
```

Validation:
- Exactly one state has `initial: true`.
- States with `final: true` cannot be the `target` of any action's transition.
- `enter` / `exit` actions must use the verbs declared in project `_config.md`.

States describe **what is true** in each mode of the screen. Transitions are not declared here — they're declared in `## actions` via `state.set(<state-id>)`.

### 5. `## actions`

Imperative input → effect map.

```yaml
- on: { widget: <widget-id>, event: <event-name> }   # widget event
  do: [ <action-tuple>, ... ]

- on: { event: <event-name> }                        # bus event (must be in frontmatter `listens`)
  do: [ <action-tuple>, ... ]

- on: { widget: <widget-id>, event: <event-name>, where: "<bool-expr>" }
  do: [ <action-tuple>, ... ]
```

Each action item:
- `on.widget` references a `widget-id` from `## widgets`. Optional if `on.event` is present.
- `on.event` references an event name. For widget events, must match a valid event for the widget type. For bus events, must appear in frontmatter `listens`.
- `on.where` is an optional boolean DSL guard. Use `$state` to check FSM state.
- `do` is an ordered list of action tuples. Each is `verb(args)`.

See `vocabulary.md` for the universal action-verb pattern; project verb list lives in `_config.md`.

### 6. `## animations`

```yaml
- id: <anim-id>
  trigger: "<short prose: what triggers it>"
  spec: "<short prose: animation intent>"
  duration: <ms>ms
  blocksInput: true | false
```

`spec` is intentionally free-form prose. Easing curves, particle details, exact tween chains belong to the engine layer. The blueprint locks down `trigger` / `duration` / `blocksInput` and gives implementers a textual hint via `spec`.

If a screen has no animations, write `_none_` (still keep the header).

### 7. `## acceptance`

BDD-style assertions.

```yaml
- id: <U-prefix-id>     # e.g. U1, U2, or U-inLevel-1
  given: "<arrange>"
  when: "<act>"
  then: "<assert>"
  test_hint: "<unit | UI E2E | integration>"   # optional, helps downstream tester
```

Maps directly to test cases: Given→Arrange, When→Act, Then→Assert. Acceptance IDs are unique across the project so they can be cross-referenced from upstream specs (e.g. GDD acceptance criteria) and from test results.

### 8. `## notes`

Optional prose. Edge cases, rationale, open questions, links to discussions. The only section that's free-form. Use `[[wikilinks]]` for cross-references.

## Inheritance via `extends`

A blueprint may inherit a base blueprint:

```yaml
extends: shared/popup-base
```

The inheritor:
- Inherits frontmatter fields (overrides allowed except `id`)
- Inherits Layout regions (can add or override by region `id`)
- Inherits Widgets, States, Actions, Animations, Acceptance (can add new entries by `id`; cannot remove inherited entries — explicit conflict if same ID with different content)

Use sparingly. Most reuse should go through `type: shared` blueprints referenced from Widgets via `Custom: { name: <shared-id> }` rather than inheritance.

## YAML island parsing

Each YAML island is delimited by a fenced ` ```yaml ` block immediately after a section header. There is exactly one YAML island per section that has structured content (`layout`, `widgets`, `states`, `actions`, `animations`, `acceptance`). Multiple islands per section are an error.

The validator parses each island independently against its sub-schema (in `blueprint.schema.yaml`).
