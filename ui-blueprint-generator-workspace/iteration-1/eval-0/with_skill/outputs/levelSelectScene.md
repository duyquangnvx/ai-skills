---
id: levelSelectScene
type: scene
title: "Level select"
orientation: portrait
safeArea: true
parents: [mainMenuScene]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - save: SaveData
  - level: LevelData
  - i18n: I18nKeys
emits: [level.selected]
listens: []
---

## purpose

Browsable grid of all levels showing unlocked, locked, and completed states. Each cell shows level index and earned stars (for completed). Tapping an unlocked level routes to [[scenes/gameplayScene]] with the chosen level. Locked cells are non-interactive.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.levelSelect.title" }, style: { text: token.h2 } }
      - { id: hearts,   type: Custom,     name: HeartRow,     align: center-right, props: { bind: "save.hearts.current" } }

  - id: scrollArea
    type: Scroll
    axis: vertical
    flex: 1
    children:
      - id: lstLevels
        type: List
        bind: { items: "save.progress.levels" }
        axis: vertical
        itemTemplate:
          type: VStack
          width: fill
          height: auto
          children:
            - id: cell
              type: ZStack
              width: "30%sw"
              height: "30%sw"
              children:
                - { id: imgCellBg,    type: Image,  align: center,        asset: ui.levelCellBg, fit: cover, width: fill, height: fill }
                - { id: lblIndex,     type: Text,   align: center,        bind: { text: "item.displayIndex" }, style: { text: token.h1 } }
                - { id: stars,        type: Custom, name: StarRow,        align: bottom-center, props: { bind: "item.stars" } }
                - { id: imgLock,      type: Icon,   align: center,        icon: lock, visible: { bind: "item.locked === true" } }
                - { id: hitCell,      type: HitArea, align: center,       width: fill, height: fill, enabled: { bind: "item.locked === false" } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — list rendered, scroll enabled"
  on:
    - { widget: btnBack, event: tap, do: [ nav.back() ] }
    - { widget: hitCell, event: tap, where: "item.locked === false", do: [ emit("level.selected", "{item.id}"), nav.gotoScene("gameplayScene", { levelId: "{item.id}" }) ] }
    - { widget: hitCell, event: tap, where: "item.locked === true",  do: [ ui.showToast("i18n.levelSelect.lockedToast", 1500) ] }
```

## acceptance

```yaml
- id: U-levelSelectScene-1
  given: "scene=levelSelectScene, save.progress.levels has at least one unlocked level"
  when: "render"
  then: "unlocked cells show their displayIndex and earned stars; locked cells show a lock icon"
  test_hint: "unit"

- id: U-levelSelectScene-2
  given: "scene=levelSelectScene, mode=idle, item.locked=false"
  when: "tap hitCell"
  then: "level.selected emitted with item.id, navigates to gameplayScene with levelId param"
  test_hint: "UI E2E"

- id: U-levelSelectScene-3
  given: "scene=levelSelectScene, mode=idle, item.locked=true"
  when: "tap hitCell"
  then: "no navigation occurs; locked toast shown"
  test_hint: "UI E2E"

- id: U-levelSelectScene-4
  given: "scene=levelSelectScene"
  when: "tap btnBack"
  then: "navigates back to mainMenuScene"
  test_hint: "UI E2E"
```

## notes

- The PRD says "grid of unlocked levels" but in practice level-select grids show locked levels too (greyed out). Inferred locked-cell rendering and toast — surface to product if pure unlocked-only is required.
- Each row of the grid should hold 3 cells; achieved by parent `Scroll`+`List` with `width: 30%sw` cells wrapping. If the engine's List does not auto-wrap to a grid, swap `lstLevels` for a `Grid` with `cols: 3, rows: auto` and bind `cells` directly. Surface to engineering.
- Star/lock visuals defined in `DESIGN.md#levelSelect-cells`.
- Open question: pagination vs single long scroll vs world-map? Inferred single scroll for the casual-game default.
