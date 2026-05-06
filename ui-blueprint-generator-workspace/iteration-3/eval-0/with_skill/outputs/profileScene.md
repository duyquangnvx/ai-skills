---
id: profileScene
type: scene
title: "Profile"
orientation: portrait
safeArea: true
parents: [mainMenuScene]
children: []
sources:
  - "PRD#screen-8"
dataBindings:
  - save: SaveData
  - i18n: I18nKeys
emits: []
listens: []
---

## purpose

Player profile dashboard. Shows avatar, display name, current player level (experience-driven, not match-3 level), and a list of achievements with locked/unlocked state. Read-only view; profile editing not in scope per PRD.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.profile.title" } }

  - id: identity
    type: VStack
    height: auto
    children:
      - { id: avatar,        type: Custom, name: Avatar, props: { bind: "save.profile.avatar", size: "30%sw" } }
      - { id: lblDisplayName, type: Text,  bind: { text: "save.profile.displayName" } }
      - { id: lblPlayerLevel, type: Text,  bind: { text: "save.profile.playerLevel", fmt: "Level {n}" } }
      - { id: barXp,         type: ProgressBar, bind: { value: "save.profile.xpProgress" }, min: 0, max: 100 }
      - { id: lblXpDetail,   type: Text,  bind: { text: "{save.profile.xpCurrent} / {save.profile.xpNext}" } }

  - id: achievementsHeader
    type: HStack
    height: auto
    children:
      - { id: lblAchievementsTitle, type: Text, bind: { text: "i18n.profile.achievements" }, flex: 1 }
      - { id: lblAchievementsCount, type: Text, bind: { text: "{save.profile.achievementsUnlocked} / {save.profile.achievementsTotal}" } }

  - id: scrollAchievements
    type: Scroll
    flex: 1
    axis: vertical
    children:
      - id: lstAchievements
        type: List
        bind: { items: "save.profile.achievements" }
        itemTemplate:
          type: HStack
          height: auto
          children:
            - id: imgAchievementIcon
              type: Image
              bind: { asset: "item.icon" }
              tint: token.muted
              width: 48dp
              height: 48dp
              fit: contain
            - id: achievementTextStack
              type: VStack
              flex: 1
              height: auto
              children:
                - { id: lblAchievementName, type: Text, bind: { text: "item.name" } }
                - { id: lblAchievementDesc, type: Text, bind: { text: "item.description" } }
            - id: imgAchievementUnlocked
              type: Icon
              icon: check-circle
              visible: { bind: "item.unlocked === true" }
              size: 24dp
```

## modes

```yaml
- id: viewing
  initial: true
  description: "Default — read-only profile view"
  on:
    - { widget: btnBack, event: tap, do: [ nav.back() ] }
```

## acceptance

```yaml
- id: U-profileScene-1
  given: "scene=profileScene, save.profile.displayName = 'Alice'"
  when: "render lblDisplayName"
  then: "displays 'Alice'"
  test_hint: "unit"

- id: U-profileScene-2
  given: "scene=profileScene, save.profile.playerLevel = 12, save.profile.xpProgress = 40"
  when: "render lblPlayerLevel and barXp"
  then: "level shows 'Level 12', barXp at 40%"
  test_hint: "unit"

- id: U-profileScene-3
  given: "scene=profileScene, an achievement with item.unlocked === true"
  when: "render that achievement row"
  then: "the check-circle icon is visible on that row"
  test_hint: "unit"

- id: U-profileScene-4
  given: "scene=profileScene, an achievement with item.unlocked === false"
  when: "render that achievement row"
  then: "the check-circle icon is hidden"
  test_hint: "unit"

- id: U-profileScene-5
  given: "scene=profileScene"
  when: "tap btnBack"
  then: "navigates back to mainMenuScene"
  test_hint: "UI E2E"
```

## notes

- "Player level" here is account-XP level (e.g. social progression), distinct from "match-3 level" used in [[scenes/levelSelectScene]] / [[scenes/gameplayScene]]. Bound from `save.profile.playerLevel` to keep the namespaces clean.
- Avatar is a `Custom` widget (declared in `_config.md`) — implementation likely renders an image with a frame ring or fallback initials.
- Achievement rows use a `tint` on the icon to grey out locked items visually; the unlock check icon is the explicit indicator. Final visual treatment lives in `DESIGN.md`.
- No edit-profile flow specified in PRD. If added later, push it as a new popup (e.g. `editProfilePopup`) rather than mode-switching this scene.
- Tapping an achievement row could open a detail popup in a future iteration; not in scope here.
