# Blueprint Format Specification

The contract for every `<screen-id>.blueprint.yaml` file. Read this before drafting.

## File structure

A blueprint is a single YAML document with 6 top-level keys, in this order:

```yaml
frontmatter:    # required — metadata block
  ...
purpose: |      # required — prose, 1-3 sentences
  ...
ui:             # required — nested UI tree (root container + children)
  ...
modes:          # required — array of modes, OR null for stateless clusters
  ...
acceptance:     # required — array of BDD rows, OR null
  ...
notes: |        # optional — prose, edge cases / rationale / open questions
  ...
```

Empty `modes` or `acceptance` use the YAML literal `null` (not `[]`, not `_none_`):

```yaml
modes: null
acceptance: null
```

The full document is a single `yaml.load`. The validator runs `blueprint.schema.yaml` against the loaded object directly.

File extension: `.blueprint.yaml`. File name (without extension) should match the `frontmatter.id`.

## Frontmatter

```yaml
frontmatter:
  id: <screen-id>              # required, camelCase, unique across project
  type: scene | popup | shared # required
  title: "<human label>"       # required
  configVersion: <semver>      # optional; matches version: in _config.yaml

  orientation: portrait | landscape | both  # optional, default: both. Forbidden for type: shared.
  safeArea: true | false                    # optional, default: true. Forbidden for type: shared.

  behavior: modal | sheet | drawer | toast | tooltip | banner | actionSheet
                              # popup only — overlay sub-class. default: modal
  modal: true | false         # popup only — true blocks input behind
  dismissible: true | false   # popup only — tap-outside / back-button closes
  autoDismissMs: <int>        # popup only, behavior=toast — auto-dismiss after ms
  anchorWidget: <widget-id>   # popup only, behavior=tooltip|popover — anchor widget
  snapPoints: [<size>, ...]   # popup only, behavior=sheet — height stops
  swipeToDismiss: true | false  # popup only, behavior=drawer|sheet

  parents: [<id>, ...]       # required for non-root scenes/popups (screens that navigate INTO this).
                             # For type: shared, parents = consumers (blueprints that include this cluster).
  children: [<id>, ...]      # popups this screen can open; required if any are opened

  sources:                   # optional — back-references to upstream docs
    - "<doc-path>#<anchor>"

  dataBindings:              # optional — typed data sources this screen reads
    - <namespace>: <TypeName>

  emits: [<event>, ...]      # bus events this screen publishes
  listens: [<event>, ...]    # bus events this screen subscribes to

  accessibility:             # optional — screen-level a11y declarations
    a11yLabel: <string|bindPath>
    a11yRole: <role>           # e.g. dialog, navigation, list
    a11yLiveRegion: polite | assertive | none
    focusOrder: [<widget-id>, ...]
```

### Frontmatter validation rules

- `id` is unique across the entire `ui-blueprints/` tree.
- `modal`, `dismissible`, `behavior`, `autoDismissMs`, `anchorWidget`, `snapPoints`, `swipeToDismiss` are only valid when `type: popup` — error otherwise.
- `autoDismissMs` is only valid when `behavior: toast`. `anchorWidget` is only valid when `behavior: tooltip` (or domain-specific `popover`). `snapPoints` is only valid when `behavior: sheet`. `swipeToDismiss` is only valid when `behavior: sheet | drawer`.
- `safeArea` and `orientation` are forbidden when `type: shared`.
- `sources` paths must resolve to real anchors in project documentation.
- `parents` / `children` must reference real blueprint IDs.
- `configVersion`, if present, must match the `version:` declared in `_config.yaml`.

## Section contracts

### 1. `purpose`

1-3 sentences of prose (block scalar `|`). Why does this screen exist? What is its role in the user/player experience? Cross-references to other screens or upstream specs use `[[wikilinks]]` (see `conventions.md`).

### 2. `ui`

A single nested object — the root container; children nest as containers or widgets.

```yaml
ui:
  type: <container-type>     # required: VStack | HStack | ZStack | Grid | Scroll | Wrap
  <container-options>        # cols/rows/gap/axis/runGap/itemGap as required by container type
  children:
    - id: <node-id>          # optional; required if referenced by modes or acceptance
      type: <container-or-widget-type>
      <sizing>               # width/height/flex (per parent's stack semantics)
      <padding-or-other-props>
      children: [...]        # only for container types
```

Universal rules:

- Container types, sizing units, widget types and their props — see `vocabulary.md`.
- `Spacer` is a leaf node used inside stacks for flexible empty space.
- Children of `ZStack` require `align:` (9-position).
- `bind:` uses bind paths (or templates with `fmt`); `visible:` / `enabled:` use the boolean DSL — see `conventions.md`.
- `on:` is a map of event → action-tuple list. **Use only for state-independent side-effects.** Any action that triggers a state transition (`goto:`) lives in `modes`, not on the widget.

The root container always fills its parent — no explicit `fill` directive.

### 3. `modes`

Declarative state machine. Transitions live with their source mode.

```yaml
modes:
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

Action verb YAML form — see `vocabulary.md#yaml-form-for-action-lists`. Validation rules (single `initial`, `goto` resolves, verb declared, etc.) — see `companion-checks.md`.

If a screen has no state changes (e.g. a pure shared widget cluster), set `modes: null`.

### 4. `acceptance`

BDD-style assertions.

```yaml
acceptance:
  - id: <U-prefix-id>             # default scheme: U-<screen>-<n>
    given: "<arrange>"
    when: "<act>"
    then: "<assert>"
    test_hint: "unit | UI E2E | integration"   # optional
```

Maps to test cases: Given→Arrange, When→Act, Then→Assert. Acceptance IDs are unique across the project so they can be cross-referenced from upstream specs and test results.

If a screen has no assertions worth recording (rare; usually shared clusters with no behavior), set `acceptance: null`.

### 5. `notes`

Optional prose (block scalar `|`). Edge cases, rationale, animation contracts (push to `DESIGN.md` if extensive), open questions, links to discussions. The only free-form section. Use `[[wikilinks]]` for cross-references.

Omit the key entirely when there is nothing to say.

## Parsing

A blueprint is a single YAML document. Consumers (validator, downstream code agent, future preview tooling) load the file with one `yaml.load` call and validate the resulting object against `blueprint.schema.yaml`. There are no embedded sub-documents or fenced islands.
