---
id: levelSelectScene
type: scene
title: "Level select"
orientation: portrait
safeArea: true
parents: [mainMenuScene]
children: []
sources:
  - "PRD#screen-3"
dataBindings:
  - save: SaveData
  - i18n: I18nKeys
emits: [level.selected]
listens: []
---

## purpose

Players pick which level to play. Renders a scrollable grid of level tiles bound to `save.levels.list`; each tile shows level number, stars earned, and a locked/unlocked state. Tapping an unlocked level navigates to [[scenes/gameplayScene]] with that level id.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.levelSelect.title" } }

  - id: progressSummary
    type: HStack
    height: auto
    children:
      - { id: lblStars,    type: Text,   bind: { text: "save.progress.starsTotal", fmt: "★ {n}" } }
      - { id: spcSummary,  type: Spacer, flex: 1 }
      - { id: lblUnlocked, type: Text,   bind: { text: "save.progress.unlockedCount", fmt: "{n} unlocked" } }

  - id: scrollGrid
    type: Scroll
    flex: 1
    axis: vertical
    children:
      - id: lstLevels
        type: List
        bind: { items: "save.levels.list" }
        itemTemplate:
          type: VStack
          width: auto
          height: auto
          children:
            - id: tile
              type: Button
              bind: { label: "item.displayIndex" }
              enabled: { bind: "item.unlocked === true" }
              style: { variant: primary }
            - { id: lblTileStars, type: Text, bind: { text: "item.stars", fmt: "★ {n}/3" } }
```

## modes

```yaml
- id: browsing
  initial: true
  description: "Default — grid scrollable, unlocked tiles enabled"
  on:
    - { widget: btnBack, event: tap, do: [ nav.back() ] }
    - { widget: tile,    event: tap, do: [ emit("level.selected", "{item.id}"), nav.gotoScene("gameplayScene", { levelId: "{item.id}" }) ] }
```

## acceptance

```yaml
- id: U-levelSelectScene-1
  given: "scene=levelSelectScene, an unlocked tile is visible"
  when: "tap that tile"
  then: "navigates to gameplayScene with corresponding levelId"
  test_hint: "UI E2E"

- id: U-levelSelectScene-2
  given: "a tile has item.unlocked === false"
  when: "render that tile"
  then: "tile is disabled and tap does nothing"
  test_hint: "unit"

- id: U-levelSelectScene-3
  given: "scene=levelSelectScene"
  when: "tap btnBack"
  then: "navigates back to mainMenuScene"
  test_hint: "UI E2E"

- id: U-levelSelectScene-4
  given: "save.progress.starsTotal = 17"
  when: "render lblStars"
  then: "displays '★ 17'"
  test_hint: "unit"
```

## notes

- Spec says "grid of unlocked levels". Interpreted as a grid of all known levels with locked items rendered disabled rather than hidden — gives players a sense of progression. If the PRD truly means hide-locked, switch the bind source to `save.levels.unlocked` and remove the `enabled.bind`.
- `List` is rendered inside `Scroll` to support overflow when level count exceeds viewport.
- Per-tile star widget rendered as text with `★` symbol; for richer star visuals, swap to `Custom: StarRow` (declared in `_config.md` widgets).
- Tile layout (cols/rows) is governed by the `List` implementation. If a strict NxM grid is required, replace the `List` with `Grid` and bind a flat array — implementation choice deferred to downstream.
