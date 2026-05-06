---
id: mainMenu
type: scene
title: "Main menu"
orientation: portrait
safeArea: true
parents: [splashScene]
children: []
sources:
  - "PRD#screen-2-main-menu"
dataBindings:
  - save: SaveData
  - user: UserProfile
emits: []
listens: []
---

## purpose

Top-level hub the player lands on after [[scenes/splashScene]]. Provides three primary affordances — Play (continues to [[scenes/levelSelect]]), Settings (opens [[scenes/settingsScene]]), and Profile (opens [[scenes/profileScene]]) — plus a hearts/coins status strip. Exposes brand and persistent identity context.

## ui

```yaml
type: ZStack
children:
  - { id: imgBackground, type: Image, align: center,    asset: "menu.bg", fit: cover, width: fill, height: fill }

  - id: content
    type: VStack
    align: center
    width: fill
    height: fill
    children:
      - id: header
        type: HStack
        height: "10%sh"
        children:
          - { id: avatar,    type: Custom, name: Avatar, props: { bind: "user.avatar", size: 48 } }
          - { id: lblName,   type: Text,   flex: 1,      bind: { text: "user.displayName" }, style: { text: token.h2 } }
          - { id: hearts,    type: Custom, name: HeartRow, props: { bind: "save.hearts.current" } }
          - { id: lblCoins,  type: Text,   bind: { text: "save.coins", fmt: "{n}" }, style: { text: token.body } }

      - { type: Spacer, flex: 1 }

      - { id: imgLogo, type: Image, asset: "menu.logo", fit: contain, width: "70%sw", height: auto }

      - { type: Spacer, flex: 1 }

      - id: actions
        type: VStack
        width: "70%sw"
        height: auto
        children:
          - { id: btnPlay,     type: Button, bind: { label: "i18n.menu.play" },     style: { variant: primary } }
          - { id: btnSettings, type: Button, bind: { label: "i18n.menu.settings" }, style: { variant: secondary } }
          - { id: btnProfile,  type: Button, bind: { label: "i18n.menu.profile" },  style: { variant: secondary } }

      - { type: Spacer, height: "8%sh" }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — all primary actions available"
  on:
    - { widget: btnPlay,     event: tap, do: [ nav.gotoScene("levelSelect") ] }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { widget: btnProfile,  event: tap, do: [ nav.gotoScene("profileScene") ] }
```

## acceptance

```yaml
- id: U-mainMenu-1
  given: "scene=mainMenu, mode=idle"
  when: "tap btnPlay"
  then: "navigates to levelSelect scene"
  test_hint: "UI E2E"

- id: U-mainMenu-2
  given: "scene=mainMenu, mode=idle"
  when: "tap btnSettings"
  then: "navigates to settingsScene"
  test_hint: "UI E2E"

- id: U-mainMenu-3
  given: "scene=mainMenu, mode=idle"
  when: "tap btnProfile"
  then: "navigates to profileScene"
  test_hint: "UI E2E"

- id: U-mainMenu-4
  given: "user.displayName binds to a value"
  when: "scene renders"
  then: "lblName displays the user display name and avatar binds the user.avatar asset"
  test_hint: "unit"
```

## notes

- Hearts/coins strip is a passive status indicator; tapping is not an interaction in this blueprint (deferred to monetization screen, out of PRD scope).
- Music and ambient audio start when this scene becomes active; controlled by audio service per `prefs.music.enabled`.
- Background art and exact button styles live in `DESIGN.md#main-menu`.
