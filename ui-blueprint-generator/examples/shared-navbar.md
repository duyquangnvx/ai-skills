---
id: hudTopBar
type: shared
title: "HUD top bar (back, title, settings)"
orientation: portrait
parents: [gameplayScene, levelSelect, settingsScene, resultPopup]
gdd:
  - "specs/ux/navigation.md#top-bar"
dataBindings:
  - data: TopBarData         # { titleKey: i18nPath, showSettings: bool }
emits: []
listens: []
---

## purpose

Reusable top bar widget cluster used across multiple scenes and popups. Provides a consistent back button on the left, title in the center, and optional settings icon on the right. Parents inject context via `data.titleKey` (i18n path) and `data.showSettings` (visibility flag).

This is a `type: shared` blueprint — it has no `zIndex` and is not navigated to directly. Parents include it via `Custom: { name: HudTopBar, props: { ... } }` in their own widgets list, or via `extends:` if the parent's full layout starts from this skeleton.

## layout

```yaml
root: { type: ZStack }
regions:
  - id: bar
    type: ZStack
    width: fill
    height: "10%sh"
```

## widgets

```yaml
- id: btnBack
  type: IconButton
  region: bar
  align: center-left
  icon: chevron-left
  on:
    tap: [ nav.back() ]

- id: lblTitle
  type: Text
  region: bar
  align: center
  bind: { text: "data.titleKey" }
  style: { text: token.h2 }

- id: btnSettings
  type: IconButton
  region: bar
  align: center-right
  icon: gear
  visible: { bind: "data.showSettings === true" }
  on:
    tap: [ ui.openPopup("settingsPopup") ]
```

## states

_none_

## actions

_none_

## animations

_none_

## acceptance

```yaml
- id: U1
  given: "shared=hudTopBar, data.showSettings=false"
  when: "render"
  then: "btnSettings is not visible"
  test_hint: "unit"

- id: U2
  given: "shared=hudTopBar inside any parent"
  when: "tap btnBack"
  then: "navigation pops the current scene/popup"
  test_hint: "UI E2E"

- id: U3
  given: "shared=hudTopBar, data.titleKey=\"i18n.gameplay.title\""
  when: "render"
  then: "lblTitle shows the resolved i18n string for that key"
  test_hint: "unit"
```

## notes

- This cluster has no states, actions, or animations of its own — those sections are empty (`_none_`). It's purely structural reuse.
- Parents that need a different left-button behavior (e.g. opening a confirm popup before navigating back) should NOT extend this — they should declare their own top bar inline. Keeping this cluster's `nav.back` behavior fixed is the point of sharing.
- Future variants (e.g. `hudTopBarWithCoins` for a top bar that also shows currency) should be **separate shared blueprints**, not extensions of this one. Inheritance complicates diffs more than it saves writing.
