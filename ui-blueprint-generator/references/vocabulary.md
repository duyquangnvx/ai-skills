# Blueprint Vocabulary

Canonical lists for layout primitives, widget types, sizing units, action verbs, and style tokens. The skill enforces these as **closed sets** at the universal level. Project-specific extensions (custom widgets, custom action verbs) are declared in `_config.md` per project.

## Layout primitives — 6 containers

These are the **only** allowed container types. No `Flex`, no `Wrap`, no `Absolute` — banning absolute positioning forces every spec to express constraints, eliminating resolution-dependence.

| Type | Semantics | Children sizing |
|---|---|---|
| `VStack` | Vertical column, top-to-bottom | per child: `height: <size>` or `flex: <int>`, plus `width: fill\|auto` |
| `HStack` | Horizontal row, left-to-right | per child: `width: <size>` or `flex: <int>`, plus `height: fill\|auto` |
| `ZStack` | Layered, last-on-top | per child: `align: <9-position>`, optional `offset: {x, y}` |
| `Grid` | NxM uniform cells | `cols: <int>`, `rows: <int\|auto>`, `gap: <size>` |
| `Scroll` | Scrollable viewport, single axis | `axis: vertical\|horizontal`, single child |
| `Spacer` | Flexible empty space | `flex: <int>` (default 1) |

`flex` is a separate child-level integer key (a stack-axis weight), **not** a sizing-unit string. Either provide a fixed `width`/`height` size **or** provide `flex: <int>`, never both on the same child.

### 9-position align (for ZStack)

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

For "fraction of remaining space along the stack axis", use the separate `flex: <int>` child key (see Layout primitives). It is a child-level field, not a sizing-unit string.

**Banned units**: `px`, `em`, `rem`, `vw`, `vh`, arithmetic expressions like `100% - 32dp`. If you find yourself wanting arithmetic, the layout is wrong — restructure with a Spacer or split a region.

## Widget types — atomic / leaf

These are the **universal** widget types. Always available.

| Type | Required props | Optional props |
|---|---|---|
| `Text` | `text` or `bind.text` | `fmt`, `align`, `maxLines`, `style` |
| `Image` | `asset` or `bind.asset` | `fit: contain\|cover\|fill`, `tint` |
| `Icon` | `icon` (catalog key) | `size`, `tint` |
| `Button` | `label` or `child`, `on.tap` | `variant: primary\|secondary\|ghost`, `enabled.bind` |
| `IconButton` | `icon`, `on.tap` | `enabled.bind`, `badge.bind` |
| `Toggle` | `bind.value`, `on.change` | `label` |
| `Slider` | `bind.value`, `on.change`, `min`, `max` | `step` |
| `ProgressBar` | `bind.value`, `min`, `max` | `variant` |
| `List` | `bind.items`, `itemTemplate` | `axis`, `separator` |
| `HitArea` | `on.tap` (no visual) | `size` |
| `Custom` | `name` (engine widget id) | `props: {...}` — escape hatch |

### `Custom` — escape hatch

Engine-specific complex widgets (board renderers, code editors, map views, particle systems, custom game widgets) use `Custom`:

```yaml
- id: board
  type: Custom
  name: BoardView           # the implementation's widget id, defined in code
  region: board
  props:
    bind: "state.board"
    gravity.bind: "level.gravity"
  on:
    tap.tile: [ emit("level.tileTap", "{cell}") ]
```

The blueprint references the Custom widget by `name` and passes typed `props`. The implementation lives in code (e.g. `src/features/board/`). This is the only legitimate way to spec something the universal vocabulary can't express.

### Project-specific widget extensions

Some domains commonly need additional atomic widgets. List them in `_config.md`:

- **Game UI**: `Minimap`, `PromptIndicator` (input-mode-aware glyph), `HeartRow`, `BoosterBadge`
- **Web/mobile**: `Avatar`, `Chip`, `BottomSheet`, `Tabs`, `SearchField`
- **Forms-heavy**: `DatePicker`, `Combobox`, `Stepper`

If declared in `_config.md`, they may be used as if universal. If not declared, use `Custom` instead.

## Action verbs — universal pattern

Action verbs are a **controlled enum**. The universal pattern below is project-agnostic; the project's actual verb list lives in `_config.md`.

### Universal verb categories

| Category | Pattern | Examples |
|---|---|---|
| Navigation | `nav.*` | `nav.gotoScene`, `nav.back`, `nav.replace` |
| UI overlay | `ui.*` | `ui.openPopup`, `ui.closePopup`, `ui.showToast` |
| State machine | `state.*` | `state.set` |
| Event bus | `emit` | `emit(<event>, <payload>?)` |
| Service call | `service.call` | `service.call(<service>, <method>, <args>?)` |
| Data write | `data.*` | `data.set(<path>, <value>)`, `data.increment(<path>)` |
| Placeholder | `noop` | `noop()` |

Every verb is written as `verb(args)` — including `noop()` and verbs with no args. No inline JS, no arbitrary expressions, no chained method calls.

### Project verb list (declared in `_config.md`)

The project picks which universal verbs apply and adds project-specific ones. Example for a Cocos game:

```yaml
verbs:
  nav.gotoScene: { args: [sceneId, data?], maps_to: "ui.gotoScene" }
  nav.back:      { args: [], maps_to: "ui.back" }
  ui.openPopup:  { args: [popupId, data?], maps_to: "ui.openPopup" }
  ui.closePopup: { args: [popupId?], maps_to: "ui.closePopup" }
  state.set:     { args: [stateId] }
  emit:          { args: [eventName, payload?] }
  service.call:  { args: [serviceKey, method, args?] }
  noop:          { args: [] }
```

Example for a React web app:

```yaml
verbs:
  nav.push:    { args: [route, params?], maps_to: "router.push" }
  nav.replace: { args: [route, params?], maps_to: "router.replace" }
  nav.back:    { args: [], maps_to: "router.back" }
  ui.openModal:  { args: [modalId, data?] }
  ui.closeModal: { args: [modalId?] }
  state.set:     { args: [stateId] }
  emit:          { args: [eventName, payload?] }
  api.call:      { args: [endpoint, method, body?] }
  noop:          { args: [] }
```

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

### Universal pattern

```yaml
namespaces:
  <name>: { source: <TypeName>, scope: <where the data lives> }
```

### Common namespace patterns

| Domain | Typical namespaces |
|---|---|
| Game | `level.*`, `state.*`, `save.*`, `i18n.*` |
| Web app | `user.*`, `route.*`, `flags.*`, `session.*`, `i18n.*` |
| Mobile app | `user.*`, `device.*`, `prefs.*`, `i18n.*` |
| Generic | declare what makes sense for the project |

### `$state` pseudo-path

`$state` is **not** a data namespace. It refers to the **FSM state ID** of the current screen — useful in `where` guards on actions to check the current state-machine state.

Distinct from the `state.*` data namespace. A typical game has both: `state.timer` (data) and `$state === "paused"` (FSM).

## Bind syntax in widgets

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

## What goes where — quick reference

| Concern | Lives in |
|---|---|
| Container structure | `## layout` |
| Atomic widgets, content, bindings, interactions | `## widgets` |
| Modes / variants of the screen | `## states` |
| What input does what (with optional state guard) | `## actions` |
| Animation contracts (trigger / duration / blocksInput) | `## animations` |
| Test cases | `## acceptance` |
| Edge cases, rationale | `## notes` |
| Concrete colors / fonts / pixel values | `DESIGN.md` (NOT in blueprint) |
| Engine APIs / framework-specific code | code repo (NOT in blueprint) |
