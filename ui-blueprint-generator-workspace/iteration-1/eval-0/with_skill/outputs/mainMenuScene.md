---
id: mainMenuScene
type: scene
title: "Main menu"
orientation: portrait
safeArea: true
parents: [splashScene]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - profile: PlayerProfile
  - save: SaveData
  - i18n: I18nKeys
emits: []
listens: []
---

## purpose

Root menu of the game. Presents brand identity and the three primary entry points: Play (routes to [[scenes/levelSelectScene]]), Settings (routes to [[scenes/settingsScene]]), and Profile (routes to [[scenes/profileScene]]). Also surfaces a small status row (current level, hearts) so the player has at-a-glance context.

## ui

```yaml
type: VStack
children:
  - id: header
    type: ZStack
    height: "30%sh"
    children:
      - { id: imgLogo,   type: Image, align: center,         asset: brand.logo,                        fit: contain, width: "70%sw", height: auto }
      - { id: hearts,    type: Custom, name: HeartRow,       align: top-right,    props: { bind: "save.hearts.current" } }
      - { id: lblLevel,  type: Text,  align: top-left,       bind: { text: "save.progress.lastLevel", fmt: "Level {n}" }, style: { text: token.caption } }

  - id: spacerTop
    type: Spacer
    flex: 1

  - id: actions
    type: VStack
    width: "60%sw"
    height: auto
    children:
      - id: btnPlay
        type: Button
        bind: { label: "i18n.mainMenu.play" }
        style: { variant: primary }
      - id: btnSettings
        type: Button
        bind: { label: "i18n.mainMenu.settings" }
        style: { variant: secondary }
      - id: btnProfile
        type: Button
        bind: { label: "i18n.mainMenu.profile" }
        style: { variant: secondary }

  - id: spacerBottom
    type: Spacer
    flex: 1

  - id: footer
    type: HStack
    height: auto
    children:
      - { id: lblVersion, type: Text, bind: { text: "app.version" }, style: { text: token.caption } }
      - { type: Spacer, flex: 1 }
      - { id: lblCredits, type: Text, bind: { text: "i18n.mainMenu.credits" }, style: { text: token.caption } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — three menu buttons enabled"
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
  given: "scene=mainMenuScene, save.hearts.current=3"
  when: "render"
  then: "HeartRow shows 3 filled hearts"
  test_hint: "unit"

- id: U-mainMenuScene-5
  given: "scene=mainMenuScene, save.progress.lastLevel=12"
  when: "render"
  then: "lblLevel shows 'Level 12'"
  test_hint: "unit"
```

## notes

- Three primary CTAs explicitly per PRD. Order: Play (primary), Settings, Profile.
- HeartRow and level label give the player progress context without an extra HUD scene.
- Animation contracts (logo idle bounce, button press scale) belong in `DESIGN.md#mainMenu-animations`.
- Open question: should there be a daily-reward / shop / friends entry? Not in PRD; surface to product before adding.
