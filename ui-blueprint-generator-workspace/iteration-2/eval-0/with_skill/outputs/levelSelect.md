---
id: levelSelect
type: scene
title: "Level select"
orientation: portrait
safeArea: true
parents: [mainMenu]
children: []
sources:
  - "PRD#screen-3-level-select"
dataBindings:
  - save: SaveData
  - level: LevelData
emits: [levelSelect.chosen]
listens: []
---

## purpose

Lets the player choose a level from a scrollable grid. Each cell shows the level number, locked/unlocked state, and stars previously earned. Tapping an unlocked cell launches [[scenes/gameplayScene]] with the chosen levelId.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left,  icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,       bind: { text: "i18n.levelSelect.title" }, style: { text: token.h2 } }
      - { id: lblHearts, type: Text,      align: center-right, bind: { text: "save.hearts.current", fmt: "{n}" }, style: { text: token.body } }

  - id: scrollGrid
    type: Scroll
    flex: 1
    axis: vertical
    children:
      - id: lstLevels
        type: List
        bind: { items: "save.levelProgress" }
        itemTemplate:
          type: ZStack
          width: "30%sw"
          height: "30%sw"
          children:
            - { id: imgCell,   type: Image, align: center,    asset: "levelSelect.cellBg", fit: contain, width: fill, height: fill }
            - { id: lblNumber, type: Text,  align: center,    bind: { text: "item.displayIndex" }, style: { text: token.h1 } }
            - { id: stars,     type: Custom, align: bottom-center, name: StarRow, props: { bind: "item.stars", max: 3 } }
            - { id: imgLock,   type: Icon,   align: center,   icon: lock, visible: { bind: "item.unlocked === false" } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Grid scrollable; unlocked cells tappable"
  on:
    - { widget: btnBack,   event: tap,        do: [ nav.back() ] }
    - { widget: lstLevels, event: itemTap,    where: "item.unlocked === true", do: [ emit("levelSelect.chosen", "{item.id}"), nav.gotoScene("gameplayScene", { levelId: "{item.id}" }) ] }
    - { widget: lstLevels, event: itemTap,    where: "item.unlocked === false", do: [ ui.showToast("i18n.levelSelect.locked") ] }
```

## acceptance

```yaml
- id: U-levelSelect-1
  given: "save.levelProgress contains an entry where unlocked===true"
  when: "tap that cell in lstLevels"
  then: "levelSelect.chosen emitted, navigation to gameplayScene with levelId payload"
  test_hint: "UI E2E"

- id: U-levelSelect-2
  given: "save.levelProgress contains an entry where unlocked===false"
  when: "tap that cell in lstLevels"
  then: "ui.showToast displays locked message; no navigation"
  test_hint: "UI E2E"

- id: U-levelSelect-3
  given: "scene=levelSelect, mode=idle"
  when: "tap btnBack"
  then: "navigates back to mainMenu"
  test_hint: "UI E2E"

- id: U-levelSelect-4
  given: "a level entry has stars===2"
  when: "render its cell"
  then: "StarRow displays 2 of 3 filled stars"
  test_hint: "unit"
```

## notes

- The List uses a 3-column visual via `width: 30%sw`; downstream renderer wraps List rows into a flow when its parent is a Scroll. (If the engine prefers explicit Grid semantics, the resolver can map List+itemTemplate to a Grid of `cols: 3`. Both are valid; List keeps the data-binding contract straightforward.)
- `save.levelProgress` items expose `id`, `displayIndex`, `unlocked`, `stars` as named fields — no array indexing or arithmetic in bind paths.
- Locked-cell tap shows a toast rather than playing a deny animation. Deny animation (if added later) lives in `DESIGN.md#level-select` and is engine-side.
