# Blueprint Conventions

Conventions for IDs, binding paths, boolean DSL, section headers, and cross-references. These are mechanical rules — agents follow them deterministically.

## ID naming

### Screen IDs (frontmatter `id`)

- `camelCase` or `snake_case`, pick one and use it consistently across the project. Default: `camelCase`.
- Match the upstream spec's screen name when possible (e.g. if GDD calls it "in-level", use `inLevel` or `in_level`).
- Unique across the entire `ui-blueprints/` tree. The validator enforces this.

### Widget IDs (per file)

- `camelCase`, prefix-by-type:
  - `btn*` for `Button` / `IconButton`
  - `lbl*` for `Text`
  - `img*` for `Image`
  - `lst*` for `List`
  - `tgl*` for `Toggle`
  - `bar*` for `ProgressBar`
  - For `Custom` widgets, name follows the implementation widget id (e.g. `board`, `hearts`, `minimap`)
- Unique within the file. The validator enforces this.

### Region IDs (within `## layout`)

- `camelCase`, descriptive of role: `topBar`, `hud`, `board`, `boosters`, `content`, `footer`, `sidebar`.
- Widget references via `region: <id>` must resolve to a declared region.

### State IDs (within `## states`)

- `camelCase`, descriptive: `default`, `paused`, `gameOver`, `loading`, `error`, `confirmQuit`.
- Action references via `state.set("<id>")` must resolve to a declared state.

### Acceptance IDs

- `U1`, `U2`, `U3`, ... (project-wide sequential) **or** `U-<screen>-<n>` (scoped per screen).
- Pick one scheme per project, use consistently. Acceptance IDs are unique across the project.

## Binding paths

### Path syntax

Binding paths are **dot-separated** strings starting with a declared namespace:

```
<namespace>.<segment>.<segment>...
```

Examples:

```
level.displayIndex
level.gravity
state.timer
state.combo.count
save.hearts.current
save.boosters.hint
i18n.popup.heartsEmpty.title
user.profile.avatar
```

### Forbidden in paths

- Array indexing (`items[0]`)
- Function calls (`items.length`)
- Arithmetic (`hp - 1`)

If you need an indexed item, list length, or computed value, the data source should expose it as a named field. The blueprint binds to that field.

### Format strings

The `fmt` field is a simple template:

- `{n}` — the bound value
- `{<key>}` — a named field (when binding to an object)
- `{mm:ss}` — a typed formatter (renderer interprets)

```yaml
bind:
  text: "state.timer"
  fmt: "{mm:ss}"

bind:
  text: "level.displayIndex"
  fmt: "Level {n}"

bind:
  text: "{player.ammo} / {player.ammo_reserve}"
  # multi-value: each {path} is a separate bind path
```

## Boolean DSL grammar

Used in `visible.bind`, `enabled.bind`, `where`, and any boolean condition. Restricted grammar — agent gen-friendly, validator parseable.

### Operators (allowed)

| Category | Operators |
|---|---|
| Equality | `===`, `!==` |
| Comparison | `>`, `<`, `>=`, `<=` |
| Logical | `&&`, `\|\|`, `!` |
| Grouping | `(` `)` |

### Operands (allowed)

- Bind paths (must start with a declared namespace): `save.hearts.current`
- The `$state` pseudo-path (FSM state): `$state === "paused"`
- Numeric literals: `0`, `25`, `100.5`
- String literals (double-quoted): `"paused"`, `"win"`
- Boolean literals: `true`, `false`
- Null literal: `null`

### Forbidden

- Function calls of any kind: `items.length`, `Math.max(...)`, `path.endsWith(...)`
- Arithmetic: `hp - 1`, `score * 2`
- Ternary: `a ? b : c`
- Loops, regex, template literals
- Bitwise operators
- Assignment

### Examples

```yaml
visible: { bind: "save.hearts.current === 0" }
enabled: { bind: "save.boosters.hint > 0 && state.timer > 0" }
where: "$state === \"tutorialBlocking\""
visible: { bind: "user.role !== \"guest\" && flags.betaUI === true" }
```

If you need anything outside this grammar, the computation belongs in the data source, not the blueprint. Bind to a named field.

## Section headers

Body sections use exact lowercase headers, no numbering, no punctuation:

```
## purpose
## layout
## widgets
## states
## actions
## animations
## acceptance
## notes
```

Extractable by regex: `^## (purpose|layout|widgets|states|actions|animations|acceptance|notes)$`.

All headers required, in this exact order. Empty section bodies use `_none_`:

```
## animations

_none_
```

## YAML islands

Each structured section has exactly one fenced YAML island immediately after the header:

````markdown
## widgets

```yaml
- id: btnBack
  type: IconButton
  ...
```
````

Multiple islands per section are an error. Other content (prose) between header and island is also an error — the island must come immediately after the header.

## Cross-references — wikilinks

In prose sections (`## purpose`, `## notes`), reference using `[[wikilink]]`:

| Wikilink form | Resolves to |
|---|---|
| `[[scenes/inLevel]]` | Another blueprint file |
| `[[shared/hud]]` | A shared widget cluster |
| `[[gdd:10-ui-screens#in-level-layout]]` | A specific anchor in upstream docs |
| `[[U1]]` | An acceptance test ID (within or across blueprints) |

**Why wikilinks over markdown links**:
- Stable across renames (with an alias map, if used)
- Consistent syntax LLM gets right
- Easy to grep and validate

The validator can warn on broken wikilinks if a project maintains an index of valid targets.

## YAML style conventions

- 2-space indentation
- Inline (flow) syntax for short declarations: `{ x: 0, y: 0 }`, `[a, b, c]`
- Block syntax for nested structures
- Quoted strings only when:
  - Contains special chars (`:`, `{`, `[`, `#`, `&`, `*`, `?`, `|`, `<`, `>`, `=`, `!`, `%`, `@`, ``` ` ```, `,`)
  - Looks like a number/boolean but should be a string (`"true"`, `"100"`)
  - Multi-line or has leading/trailing whitespace
- Single quotes for inner strings inside double-quoted DSL: `where: "$state === \"paused\""` — escape with backslash

## Project naming flexibility

Some teams have stricter conventions. The skill respects project conventions when declared in `_config.md`:

```yaml
naming:
  screen_id_case: camelCase     # or snake_case
  widget_id_case: camelCase     # or snake_case
  widget_prefixes:
    Button: btn
    Text: lbl
    Image: img
    # ...
  acceptance_id_scheme: sequential   # U1, U2, ... or scoped: U-<screen>-<n>
```

If `_config.md` declares stricter rules, the validator and the skill enforce those. If absent, fall back to the defaults in this document.
