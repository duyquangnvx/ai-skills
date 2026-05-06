# Blueprint Conventions

Mechanical rules for IDs, binding paths, boolean DSL, YAML style, and cross-references. Agents follow these deterministically.

## ID naming

### Screen IDs (frontmatter `id`)

- `camelCase`. Unique across the entire `ui-blueprints/` tree. The validator enforces this.
- Match the upstream spec's screen name when possible (e.g. GDD calls it "in-level" → `inLevel`).

### Widget / region IDs (per file)

- `camelCase`. Unique within the file. The validator enforces this.
- Convention prefixes for atomic widgets:
  - `btn*` for `Button` / `IconButton`
  - `lbl*` for `Text`
  - `img*` for `Image`
  - `lst*` for `List`
  - `tgl*` for `Toggle`
  - `bar*` for `ProgressBar`
- For container regions, use descriptive role names: `topBar`, `hud`, `boosters`, `content`, `footer`, `sidebar`.
- For `Custom` widgets, the id follows the implementation widget id (e.g. `board`, `hearts`, `minimap`).

### Mode IDs (within `## modes`)

- `camelCase`, descriptive: `default`, `paused`, `gameOver`, `loading`, `error`, `confirmQuit`.
- `goto: <id>` references must resolve to a declared mode in the same file.

### Acceptance IDs

Default scheme: **`U-<screen>-<n>`** (scoped per screen). Example: `U-gameplayScene-1`, `U-confirmPopup-2`.

Project-wide simple sequence (`U1`, `U2`, ...) is allowed but discouraged — IDs become non-contiguous when blueprints are added/removed.

Acceptance IDs are unique across the project so they can be cross-referenced from upstream specs and test results.

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
i18n.popup.heartsEmpty.title
user.profile.avatar
```

### Forbidden in paths

- Array indexing (`items[0]`)
- Function calls (except whitelisted properties below)
- Arithmetic (`hp - 1`)

If you need an indexed item or computed value, the data source should expose it as a named field. The blueprint binds to that field.

### Format strings

The `fmt` field is a simple template:

- `{n}` — the bound value
- `{<key>}` — a named field (when binding to an object)
- `{mm:ss}` — a typed formatter (renderer interprets)

```yaml
bind: { text: "state.timer", fmt: "{mm:ss}" }
bind: { text: "level.displayIndex", fmt: "Level {n}" }
bind: { text: "{player.ammo} / {player.ammo_reserve}" }   # multi-value
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

- Bind paths starting with a declared namespace: `save.hearts.current`
- The `$mode` pseudo-path (FSM mode): `$mode === "paused"`
- Numeric literals: `0`, `25`, `100.5`
- String literals (double-quoted): `"paused"`, `"win"`
- Boolean literals: `true`, `false`
- Null literal: `null`

### Whitelisted properties

`.length` is allowed on collection bind paths only:

```yaml
visible: { bind: "level.tasks.length === 0" }
```

No other properties are whitelisted. If you need anything else, expose it as a named field.

### Forbidden

- Function calls: `Math.max(...)`, `path.endsWith(...)`
- Arithmetic: `hp - 1`, `score * 2`
- Ternary: `a ? b : c`
- Loops, regex, template literals
- Bitwise operators
- Assignment

### Examples

```yaml
visible: { bind: "save.hearts.current === 0" }
enabled: { bind: "save.boosters.hint > 0 && state.timer > 0" }
where: "$mode === \"tutorialBlocking\""
visible: { bind: "user.role !== \"guest\" && flags.betaUI === true" }
visible: { bind: "feed.items.length > 0" }
```

If you need anything outside this grammar, the computation belongs in the data source — bind to a named field.

## Section headers

Body sections use exact lowercase headers, no numbering, no punctuation:

```
## purpose
## ui
## modes
## acceptance
## notes
```

Extractable by regex: `^## (purpose|ui|modes|acceptance|notes)$`.

All headers required (except `notes`), in this exact order. Empty `modes` / `acceptance` use `_none_`:

```
## modes

_none_
```

## YAML islands

Each structured section has exactly one fenced YAML island immediately after the header:

````markdown
## ui

```yaml
type: VStack
children: [...]
```
````

Multiple islands per section are an error. Other content (prose) between header and island is also an error — the island must come immediately after the header.

## Cross-references — wikilinks

In prose sections (`## purpose`, `## notes`), reference using `[[wikilink]]`:

| Form | Resolves to |
|---|---|
| `[[scenes/inLevel]]` | Another blueprint file |
| `[[shared/hud]]` | A shared widget cluster |
| `[[sources:specs/gameplay#animations]]` | A specific anchor in upstream docs |
| `[[U-gameplayScene-1]]` | An acceptance test ID |

**Why wikilinks over markdown links**:

- Stable across renames (with an alias map, if used)
- Consistent syntax LLMs get right
- Easy to grep and validate

The validator can warn on broken wikilinks if a project maintains an index of valid targets.

## YAML style

- 2-space indentation
- Inline (flow) syntax for short declarations: `{ x: 0, y: 0 }`, `[a, b, c]`
- Block syntax for nested structures
- Quoted strings only when:
  - Contains special chars (`:`, `{`, `[`, `#`, `&`, `*`, `?`, `|`, `<`, `>`, `=`, `!`, `%`, `@`, ``` ` ```, `,`)
  - Looks like a number/boolean but should be a string (`"true"`, `"100"`)
  - Multi-line or has leading/trailing whitespace
- Single quotes for inner strings inside double-quoted DSL: `where: "$mode === \"paused\""` — escape with backslash
