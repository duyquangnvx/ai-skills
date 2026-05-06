---
id: mainMenuScene
type: scene
title: "Main menu"
orientation: portrait
safeArea: true
parents: [splashScene]
children: []
sources:
  - "PRD#screen-2"
dataBindings:
  - save: SaveData
  - i18n: I18nKeys
emits: []
listens: []
---

## purpose

Top-level hub after splash. Offers three primary actions: play (→ [[scenes/levelSelectScene]]), settings (→ [[scenes/settingsScene]]), profile (→ [[scenes/profileScene]]). Surfaces lightweight player context (current level, hearts) so players see their progress at a glance.

## ui

```yaml
type: VStack
children:
  - id: header
    type: VStack
    height: "20%sh"
    children:
      - { id: imgLogo,  type: Image, asset: img.brand.logo, width: "50%sw", height: auto, fit: contain }
      - { id: lblTitle, type: Text,  bind: { text: "i18n.mainMenu.title" } }

  - id: statusBar
    type: HStack
    height: auto
    children:
      - { id: hearts,        type: Custom, name: HeartRow, props: { bind: "save.hearts.current" } }
      - { id: spcStatus,     type: Spacer, flex: 1 }
      - { id: lblCurrentLvl, type: Text,   bind: { text: "save.progress.currentLevel", fmt: "Level {n}" } }

  - id: spcMid
    type: Spacer
    flex: 1

  - id: actions
    type: VStack
    height: auto
    children:
      - { id: btnPlay,     type: Button, bind: { label: "i18n.mainMenu.play" },     style: { variant: primary } }
      - { id: btnSettings, type: Button, bind: { label: "i18n.mainMenu.settings" }, style: { variant: secondary } }
      - { id: btnProfile,  type: Button, bind: { label: "i18n.mainMenu.profile" },  style: { variant: secondary } }

  - id: spcBottom
    type: Spacer
    flex: 1
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — all three buttons enabled, awaiting input"
  on:
    - { widget: btnPlay,     event: tap, do: [ nav.gotoScene("levelSelectScene") ] }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { widget: btnProfile,  event: tap, do: [ nav.gotoScene("profileScene") ] }
```

## acceptance

```yaml
- id: U-mainMenuScene-1
  given: "scene=mainMenuScene, mode=idle"
  when: "tap btnPlay"
  then: "navigates to levelSelectScene"
  test_hint: "UI E2E"

- id: U-mainMenuScene-2
  given: "scene=mainMenuScene, mode=idle"
  when: "tap btnSettings"
  then: "navigates to settingsScene"
  test_hint: "UI E2E"

- id: U-mainMenuScene-3
  given: "scene=mainMenuScene, mode=idle"
  when: "tap btnProfile"
  then: "navigates to profileScene"
  test_hint: "UI E2E"

- id: U-mainMenuScene-4
  given: "save.progress.currentLevel = 7"
  when: "render lblCurrentLvl"
  then: "displays 'Level 7'"
  test_hint: "unit"
```

## notes

- The status bar is intentionally lightweight; richer player profile data lives in [[scenes/profileScene]].
- Hearts widget is shared; same `Custom: HeartRow` widget appears in [[scenes/gameplayScene]].
- No deep links / push-notification entry points were specified in PRD; if added later, route them as `nav.gotoScene` from a higher-level boot router, not from this scene.
