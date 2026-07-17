# Blueprint Vocabulary

Canonical lists for layout primitives, widget types, sizing units, action verbs, and style tokens. The skill enforces these as **closed sets** at the universal level. Project-specific extensions are declared in `_config.yaml`.

## Layout primitives — 6 containers + Spacer

These are the **only** allowed container types. No `Flex`, no `Absolute` — banning absolute positioning forces every spec to express constraints, eliminating resolution-dependence.

| Type | Semantics | Children sizing |
|---|---|---|
| `VStack` | Vertical column, top-to-bottom | per child: `height: <size>` or `flex: <int>`, plus `width: fill\|auto` |
| `HStack` | Horizontal row, left-to-right | per child: `width: <size>` or `flex: <int>`, plus `height: fill\|auto` |
| `ZStack` | Layered, last-on-top | per child: `align: <9-position>`, optional `offset: {x, y}`. May use `width: fill` and/or `height: fill` to fill the layer. |
| `Grid` | NxM uniform cells | `cols: <int>`, `rows: <int\|auto>`, `gap: <size>` |
| `Scroll` | Scrollable viewport, single axis | `axis: vertical\|horizontal`, single child |
| `Wrap` | Flow layout, breaks into multiple runs when overflowing | `axis: horizontal\|vertical` (run direction), `runGap: <size>`, `itemGap: <size>` |

`Spacer` is a leaf node (not a container) used inside stacks for flexible empty space:
```yaml
- type: Spacer
  flex: 1
```

`flex` is a child-level integer key (a stack-axis weight), **not** a sizing-unit string. Either fixed `width`/`height` size **or** `flex: <int>`, never both on the same child.

### 9-position align (for ZStack children)

`top-left` `top-center` `top-right` `center-left` `center` `center-right` `bottom-left` `bottom-center` `bottom-right`

`offset: {x, y}` is reserved for **anchor-tweak on a ZStack child** — small adjustments relative to the align point. Typical use cases: badge inset on an icon corner, focus-ring kerning, tooltip-arrow nudge, popover anchoring.

`offset` is **not** for full-layout positioning. If you find yourself using `offset` to place a top-bar, a footer, a panel, or any structural region — restructure with `VStack`/`HStack` + `padding` (or `Spacer` for flexible empty space).

| Designer spec | ❌ Wrong (offset for full layout) | ✅ Right |
|---|---|---|
| Title 24dp from top of panel | `align: top-center, offset: {y: 24dp}` | `VStack` with `padding: {t: 24dp}` |
| Button 16dp from bottom-left of panel | `align: bottom-left, offset: {x: 16dp, y: -16dp}` | `panel` (ZStack) with `padding: 16dp`; button has `align: bottom-left` |
| Badge inset from icon corner | `align: top-right, offset: {x: -4dp, y: 4dp}` | Keep as-is — anchor-tweak is the right use of `offset` |
| Tooltip arrow nudged from anchor | `align: bottom-center, offset: {y: -12dp}` | Keep as-is — anchor-tweak |

Heuristic: if the offset magnitude is large relative to the parent's dimension (e.g. > ~5%), it is probably structural positioning — restructure. The validator surfaces such offsets as warnings.

## Sizing units — 7 forms

| Form | Meaning |
|---|---|
| `<n>dp` | Density-independent pixels (e.g. `70dp`) |
| `<n>%w` / `<n>%h` | % of parent width / height |
| `<n>%sw` / `<n>%sh` | % of screen width / height (safe-area-aware when `safeArea: true`) |
| `auto` | Content-driven (Text/Image natural size) |
| `fill` | Take all available space along that axis. In VStack/HStack, applies to the cross-axis. In ZStack, applies to either or both axes. In Grid/Scroll, applies as the container resolves. |
| `min(<size>, <size>)` / `max(<size>, <size>)` | Combine two sizing units. **Only these two functions; no nesting.** |

For "fraction of remaining space along the stack axis", use the `flex: <int>` child key.

**Banned units**: `px`, `em`, `rem`, `vw`, `vh`, arithmetic expressions like `100% - 32dp`. If you find yourself wanting arithmetic, the layout is wrong — restructure with a `Spacer`, use `padding`, or split a parent.

## Spacing — padding

Containers and atomic widgets accept a `padding` field for inset spacing. Prefer `padding` over wrapping a child in `Spacer` sandwiches — it maps cleanly to SwiftUI `.padding`, Flutter `Padding`, UGUI `LayoutGroup.padding`, and CSS `padding`.

Forms:

```yaml
padding: 16dp                      # uniform, all 4 edges
padding: { h: 16dp, v: 8dp }       # horizontal / vertical shortcuts
padding: { t: 12dp, r: 16dp, b: 12dp, l: 16dp }   # per-edge
```

Values use any `dp`/`%w`/`%h`/`%sw`/`%sh` sizing unit. `h` is shorthand for `l` + `r`; `v` for `t` + `b`. Per-edge values override shortcuts when both are present.

Use `padding` for "inset content N from container edge". Use `Spacer` only for distributing flexible empty space along a stack axis.

## Widget types

These are the **universal** widget types. Always available.

| Type | Required props | Optional props |
|---|---|---|
| `Text` | `text` (literal) or `bind.text` (i18n path preferred) | `bind.fmt`, `align`, `maxLines`, `style` |
| `Image` | `asset` or `bind.asset` | `fit: contain\|cover\|fill`, `tint` |
| `Icon` | `icon` (catalog key) | `size`, `tint` |
| `Button` | `label` or `bind.label` | `variant: primary\|secondary\|ghost`, `enabled.bind`, `style` |
| `IconButton` | `icon` | `enabled.bind`, `badge.bind` |
| `Toggle` | `bind.value` | `label` |
| `Slider` | `bind.value`, `min`, `max` | `step` |
| `ProgressBar` | `bind.value`, `min`, `max` | `variant` |
| `List` | `bind.items`, `itemTemplate` | `axis`, `separator` |
| `HitArea` | (no visual; usually inside ZStack as backdrop) | `size` |
| `Include` | `ref` (id of a `type: shared` blueprint) | `props: {...}` — values forwarded to the shared cluster's `data.*` namespace |
| `Custom` | `name` (engine widget id) | `props: {...}`, `bind` (single path) — escape hatch |

### `Text` content rule

Hard-coded `text:` literals are allowed only for symbols (`"+"`, `"x"`, `"→"`) and digits. All natural-language text MUST use `bind.text` pointing to an `i18n.*` namespace path. This keeps blueprints localizable.

### Bind syntax — two forms

- Object form (preferred for atomic widgets binding specific properties): `bind: { text: "level.displayIndex", fmt: "Level {n}" }`, `bind: { items: "level.leaderboard" }`.
- String form (only for `Custom` widgets that take a single bind path): `bind: "state.board"`.

Object form keys are widget-specific (see the table above). `fmt` lives inside `bind:`; a sibling `fmt:` is a schema error.

### `List.itemTemplate`

`itemTemplate` is a single-widget or single-container subtree describing how each item is rendered. Bind paths inside the template start with `item.*` referring to the current row.

```yaml
- id: lstLeaderboard
  type: List
  bind: { items: "level.leaderboard" }
  itemTemplate:
    type: HStack
    height: 48dp
    children:
      - { id: rank,  type: Text, bind: { text: "item.rank" },  width: 32dp }
      - { id: name,  type: Text, bind: { text: "item.name" },  flex: 1 }
      - { id: score, type: Text, bind: { text: "item.score" }, width: 64dp }
```

### `Include` — compose a shared blueprint

Use `Include` to embed a `type: shared` blueprint inside another. This is the only correct way to reuse a shared cluster — do not use `Custom` for it.

```yaml
- type: Include
  ref: hudTopBar              # id of a shared blueprint
  props:
    titleKey: "i18n.gameplay.title"
    showSettings: true
```

Inside the included shared blueprint, `props.*` are exposed as `data.*` (the shared blueprint declares its expected `data` shape via `dataBindings:`).

### `Custom` — escape hatch

Engine-specific complex widgets (board renderers, code editors, map views, particle systems) that the universal vocabulary cannot express:

```yaml
- id: board
  type: Custom
  name: BoardView           # the implementation's widget id, defined in code
  bind: "state.board"       # single bind path (string form is OK here)
  props:
    mode.bind: "level.mode"
  on:
    tap.tile:
      - emit("level.tileTap", "{cell}")
```

Difference vs `Include`:

- `Custom` → **engine code** defines the widget; blueprint passes typed props.
- `Include` → **another blueprint** defines the structure; current blueprint composes it.

If you reach for `Custom` for something expressible with universal containers + widgets, you are probably skipping a refactor. Use it only when the widget's behavior cannot be decomposed into vocabulary primitives.

### Project-specific widget extensions

Some domains commonly need additional atomic widgets. List them in `_config.yaml`:

- **Game UI**: `Minimap`, `PromptIndicator`, `HeartRow`, `BoosterBadge`
- **Mobile**: `Avatar`, `Chip`, `BottomSheet`, `Tabs`, `SearchField`
- **Forms-heavy**: `DatePicker`, `Combobox`, `Stepper`

If declared in `_config.yaml`, they may be used as if universal. If not declared, use `Custom`.

## Action verbs — universal pattern

Action verbs are a **controlled enum**. The universal pattern below is project-agnostic; the project's actual verb list lives in `_config.yaml`.

### Universal verb categories

| Category | Pattern | Examples |
|---|---|---|
| Navigation | `nav.*` | `nav.gotoScene`, `nav.back`, `nav.replace`, `nav.push` |
| UI overlay | `ui.*` | `ui.openPopup`, `ui.closePopup`, `ui.showToast` |
| Event bus | `emit` | `emit(<event>, <payload>?)` |
| Service call | `service.call` | `service.call(<service>, <method>, <args>?)` |
| Data write | `data.*` | `data.set(<path>, <value>)`, `data.increment(<path>)` |
| Placeholder | `noop` | `noop()` |

Every verb is written as `verb(args)` — including `noop()` and verbs with no args. No inline JS, no arbitrary expressions, no chained method calls.

State transitions are **not** action verbs — use `goto: <mode-id>` directly on a mode's `on:` entry.

### YAML form for action lists

`do:` uses block form. Flow form `[ ... ]` breaks when an action contains a comma between quoted args. Single-action lists without embedded commas may stay inline: `do: [ ui.openPopup("settings") ]`. When an action argument contains `{...}`, single-quote-wrap the whole action: `- 'ui.openPopup("x", { result: "y" })'`.

### Project verb list

The project picks which universal verbs apply and adds project-specific ones in `_config.yaml`. See `references/config-template.md` for canonical examples (game + mobile-app).

A blueprint can only use verbs declared in the project's verb list. The validator checks this.

## Style tokens

Color, font, spacing referenced by **token name only**. Concrete values live in `DESIGN.md` (or equivalent design system doc). Engine adapter resolves tokens at implementation time.

Universal token namespace:

```yaml
style:
  text:    token.h1 | token.h2 | token.body | token.caption | token.button
  color:   token.primary | token.danger | token.success | token.muted | token.bg
  spacing: token.s1 | token.s2 | token.s3 | token.s4 | token.s5
```

Project token catalog declared in `_config.yaml` (or referenced from `DESIGN.md`). If no design system exists yet, omit `style` entirely from blueprints — let downstream pick defaults rather than inventing tokens.

## Bind namespaces

A blueprint reads data only through declared **bind namespaces**. Each namespace has a typed source.

### Common namespace patterns

| Domain | Typical namespaces |
|---|---|
| Game | `level.*`, `state.*`, `save.*`, `i18n.*` |
| Mobile app | `user.*`, `feed.*`, `prefs.*`, `flags.*`, `i18n.*` |
| Generic | declare what makes sense for the project |

### Reserved context namespaces

These three namespaces are always available — do **not** declare them in `_config.yaml`:

| Namespace | Where it's exposed |
|---|---|
| `data.*` | Inside a `type: shared` blueprint — values injected by the consumer's `Include props:`. Declared via `dataBindings:` on the shared blueprint frontmatter. |
| `item.*` | Inside `List.itemTemplate` — refers to the current row of the bound collection. |
| `props.*` | Alias used by some validators when describing what the parent passes into an `Include`. From the shared blueprint's perspective, read as `data.*`. |

The validator does not require these to be declared in `_config.yaml` `bindNamespaces`.

### Bind syntax in widgets

```yaml
bind:
  text: "level.displayIndex"     # path
  fmt: "Level {n}"               # optional formatter; {n} = bound value
visible:
  bind: "save.hearts.current === 0"   # boolean DSL expression
```

For bound text with multiple values:

```yaml
bind:
  text: "{player.ammo} / {player.ammo_reserve}"
```

The renderer resolves bind paths at runtime. Blueprints stay engine-agnostic.

### Event-name convention

Bus events follow `<scope>.<verb>` in camelCase — see `conventions.md#event-names`.
