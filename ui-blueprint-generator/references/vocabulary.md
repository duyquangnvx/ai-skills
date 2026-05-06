# Blueprint Vocabulary

Canonical lists for layout primitives, widget types, sizing units, action verbs, and style tokens. The skill enforces these as **closed sets** at the universal level. Project-specific extensions are declared in `_config.md`.

## Layout primitives — 5 containers + Spacer

These are the **only** allowed container types. No `Flex`, no `Wrap`, no `Absolute` — banning absolute positioning forces every spec to express constraints, eliminating resolution-dependence.

| Type | Semantics | Children sizing |
|---|---|---|
| `VStack` | Vertical column, top-to-bottom | per child: `height: <size>` or `flex: <int>`, plus `width: fill\|auto` |
| `HStack` | Horizontal row, left-to-right | per child: `width: <size>` or `flex: <int>`, plus `height: fill\|auto` |
| `ZStack` | Layered, last-on-top | per child: `align: <9-position>`, optional `offset: {x, y}` |
| `Grid` | NxM uniform cells | `cols: <int>`, `rows: <int\|auto>`, `gap: <size>` |
| `Scroll` | Scrollable viewport, single axis | `axis: vertical\|horizontal`, single child |

`Spacer` is a leaf node (not a container) used inside stacks for flexible empty space:
```yaml
- type: Spacer
  flex: 1
```

`flex` is a child-level integer key (a stack-axis weight), **not** a sizing-unit string. Either fixed `width`/`height` size **or** `flex: <int>`, never both on the same child.

### 9-position align (for ZStack children)

`top-left` `top-center` `top-right` `center-left` `center` `center-right` `bottom-left` `bottom-center` `bottom-right`

Use `offset: {x: <size>, y: <size>}` for fine adjustment from the align point. Negative offsets allowed for inward offsets from edges.

## Sizing units — 7 forms

| Form | Meaning |
|---|---|
| `<n>dp` | Density-independent pixels (e.g. `70dp`) |
| `<n>%w` / `<n>%h` | % of parent width / height |
| `<n>%sw` / `<n>%sh` | % of screen width / height (safe-area-aware when `safeArea: true`) |
| `auto` | Content-driven (Text/Image natural size) |
| `fill` | Take all available perpendicular space (only for stack cross-axis) |
| `min(<size>, <size>)` / `max(<size>, <size>)` | Combine two sizing units. **Only these two functions; no nesting.** |

For "fraction of remaining space along the stack axis", use the `flex: <int>` child key.

**Banned units**: `px`, `em`, `rem`, `vw`, `vh`, arithmetic expressions like `100% - 32dp`. If you find yourself wanting arithmetic, the layout is wrong — restructure with a `Spacer` or split a parent.

## Widget types

These are the **universal** widget types. Always available.

| Type | Required props | Optional props |
|---|---|---|
| `Text` | `text` (literal) or `bind.text` (i18n path preferred) | `fmt`, `align`, `maxLines`, `style` |
| `Image` | `asset` or `bind.asset` | `fit: contain\|cover\|fill`, `tint` |
| `Icon` | `icon` (catalog key) | `size`, `tint` |
| `Button` | `label` or `bind.label` | `variant: primary\|secondary\|ghost`, `enabled.bind`, `style` |
| `IconButton` | `icon` | `enabled.bind`, `badge.bind` |
| `Toggle` | `bind.value` | `label` |
| `Slider` | `bind.value`, `min`, `max` | `step` |
| `ProgressBar` | `bind.value`, `min`, `max` | `variant` |
| `List` | `bind.items`, `itemTemplate` | `axis`, `separator` |
| `HitArea` | (no visual; usually inside ZStack as backdrop) | `size` |
| `Custom` | `name` (engine widget id) | `props: {...}` — escape hatch |

### `Text` content rule

Hard-coded `text:` literals are allowed only for symbols (`"+"`, `"x"`, `"→"`) and digits. All natural-language text MUST use `bind.text` pointing to an `i18n.*` namespace path. This keeps blueprints localizable.

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

### `Custom` — escape hatch

Engine-specific complex widgets (board renderers, code editors, map views, particle systems) use `Custom`:

```yaml
- id: board
  type: Custom
  name: BoardView           # the implementation's widget id, defined in code
  props:
    bind: "state.board"
    gravity.bind: "level.gravity"
  on:
    tap.tile: [ emit("level.tileTap", "{cell}") ]
```

`Custom` is for engine-implemented widgets that the universal vocabulary can't express. **For structural reuse using only universal vocabulary, use `type: shared` blueprints** referenced by id from `## ui` (the resolver maps the shared id to a Custom-like compose-time widget). Do not confuse the two:

- `Custom` → engine code defines the widget; blueprint passes typed props.
- `shared` → another blueprint defines the structure; current blueprint includes it.

### Project-specific widget extensions

Some domains commonly need additional atomic widgets. List them in `_config.md`:

- **Game UI**: `Minimap`, `PromptIndicator`, `HeartRow`, `BoosterBadge`
- **Mobile**: `Avatar`, `Chip`, `BottomSheet`, `Tabs`, `SearchField`
- **Forms-heavy**: `DatePicker`, `Combobox`, `Stepper`

If declared in `_config.md`, they may be used as if universal. If not declared, use `Custom`.

## Action verbs — universal pattern

Action verbs are a **controlled enum**. The universal pattern below is project-agnostic; the project's actual verb list lives in `_config.md`.

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

### Project verb list

The project picks which universal verbs apply and adds project-specific ones in `_config.md`. See `references/config-template.md` for canonical examples (game + mobile-app).

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

Project token catalog declared in `_config.md` (or referenced from `DESIGN.md`). If no design system exists yet, omit `style` entirely from blueprints — let downstream pick defaults rather than inventing tokens.

## Bind namespaces

A blueprint reads data only through declared **bind namespaces**. Each namespace has a typed source.

### Common namespace patterns

| Domain | Typical namespaces |
|---|---|
| Game | `level.*`, `state.*`, `save.*`, `i18n.*` |
| Mobile app | `user.*`, `feed.*`, `prefs.*`, `flags.*`, `i18n.*` |
| Generic | declare what makes sense for the project |

### `$mode` pseudo-path

`$mode` refers to the **current FSM mode** of the screen — useful in `where:` guards on actions to check the current mode.

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
