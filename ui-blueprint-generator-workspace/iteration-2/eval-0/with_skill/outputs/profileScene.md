---
id: profileScene
type: scene
title: "Profile"
orientation: portrait
safeArea: true
parents: [mainMenu]
children: []
sources:
  - "PRD#screen-8-profile"
dataBindings:
  - user: UserProfile
  - save: SaveData
emits: []
listens: []
---

## purpose

Player profile dashboard. Displays the avatar, display name, current player level + XP progress, and an achievements grid. Read-only summary view; deep edits (avatar change, display name) are deferred to future screens not in this PRD batch.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.profile.title" }, style: { text: token.h2 } }

  - id: header
    type: VStack
    height: auto
    children:
      - { id: avatar,        type: Custom, name: Avatar, props: { bind: "user.avatar", size: 96 } }
      - { id: lblDisplayName, type: Text, bind: { text: "user.displayName" }, style: { text: token.h1 } }

      - id: levelRow
        type: HStack
        height: auto
        children:
          - { id: lblLevel, type: Text, bind: { text: "user.level", fmt: "Lvl {n}" }, style: { text: token.h2 } }
          - { id: barXp,    type: ProgressBar, flex: 1, bind: { value: "user.xp" }, min: 0, max: 100 }
          - { id: lblXp,    type: Text, bind: { text: "{user.xp}/{user.xpNext}" }, style: { text: token.caption } }

  - id: achievementsHeader
    type: HStack
    height: 48dp
    children:
      - { id: lblAchievements, type: Text, flex: 1, bind: { text: "i18n.profile.achievements" }, style: { text: token.h2 } }
      - { id: lblAchievementCount, type: Text, bind: { text: "{user.achievementsUnlocked}/{user.achievementsTotal}" }, style: { text: token.caption } }

  - id: scrollAchievements
    type: Scroll
    flex: 1
    axis: vertical
    children:
      - id: lstAchievements
        type: List
        bind: { items: "user.achievements" }
        itemTemplate:
          type: HStack
          height: 72dp
          children:
            - id: imgIcon
              type: Image
              width: 56dp
              height: 56dp
              fit: contain
              bind: { asset: "item.iconAsset" }
            - id: textCol
              type: VStack
              flex: 1
              children:
                - { id: lblName, type: Text, bind: { text: "item.name" }, style: { text: token.body } }
                - { id: lblDesc, type: Text, bind: { text: "item.description" }, style: { text: token.caption }, maxLines: 2 }
            - id: imgStatus
              type: Icon
              icon: check-circle
              visible: { bind: "item.unlocked === true" }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — profile data shown"
  on:
    - { widget: btnBack, event: tap, do: [ nav.back() ] }
```

## acceptance

```yaml
- id: U-profileScene-1
  given: "user.displayName, user.level, user.xp, user.xpNext are bound"
  when: "scene renders"
  then: "lblDisplayName, lblLevel, barXp, lblXp display the bound values"
  test_hint: "unit"

- id: U-profileScene-2
  given: "user.achievements contains items with unlocked field"
  when: "scene renders"
  then: "lstAchievements renders one row per item; imgStatus check icon shown only on unlocked items"
  test_hint: "unit"

- id: U-profileScene-3
  given: "scene=profileScene, mode=idle"
  when: "tap btnBack"
  then: "navigates back to mainMenu"
  test_hint: "UI E2E"

- id: U-profileScene-4
  given: "user.achievements is an empty list"
  when: "scene renders"
  then: "lstAchievements renders zero rows; achievement count shows 0/<total>"
  test_hint: "unit"
```

## notes

- Avatar is read-only here. An avatar editor was not in the PRD; flagged for future scope.
- `user.achievements` items expose `id`, `name`, `description`, `iconAsset`, `unlocked` as named fields — keeps boolean DSL clean (no array indexing).
- XP bar uses absolute min/max 0/100 because `user.xp` is normalized by the data layer; `user.xpNext` is shown as text only.
