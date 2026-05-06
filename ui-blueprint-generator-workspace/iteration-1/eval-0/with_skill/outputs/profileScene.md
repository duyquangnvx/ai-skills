---
id: profileScene
type: scene
title: "Profile"
orientation: portrait
safeArea: true
parents: [mainMenuScene]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - profile: PlayerProfile
  - save: SaveData
  - i18n: I18nKeys
emits: [profile.avatarChangeRequested]
listens: []
---

## purpose

Player profile screen. Shows the avatar, display name, current player level (with XP progress), and a scrollable list of achievements (locked + unlocked). Tapping the avatar requests an avatar change (delegated to a service). Read-mostly; no destructive actions.

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
      - { id: avatar,        type: Custom, name: Avatar,                      props: { bind: "profile.avatar", size: "80dp" } }
      - { id: lblDisplayName, type: Text,  bind: { text: "profile.displayName" }, style: { text: token.h1 } }
      - { id: lblPlayerLevel, type: Text,  bind: { text: "profile.level", fmt: "Level {n}" }, style: { text: token.body } }
      - { id: barXP,          type: ProgressBar, bind: { value: "profile.xp.current" }, min: 0, max: 100 }
      - { id: lblXP,          type: Text,  bind: { text: "{profile.xp.current} / {profile.xp.next}" }, style: { text: token.caption } }

  - id: achievementsHeader
    type: HStack
    height: auto
    children:
      - { id: lblAchTitle, type: Text, bind: { text: "i18n.profile.achievements" }, style: { text: token.h2 } }
      - { type: Spacer, flex: 1 }
      - { id: lblAchCount, type: Text, bind: { text: "{profile.achievements.unlockedCount} / {profile.achievements.totalCount}" }, style: { text: token.caption } }

  - id: scrollArea
    type: Scroll
    axis: vertical
    flex: 1
    children:
      - id: lstAchievements
        type: List
        bind: { items: "profile.achievements.list" }
        axis: vertical
        itemTemplate:
          type: HStack
          width: fill
          height: auto
          children:
            - { id: imgIcon,  type: Custom, name: AchievementBadge, props: { bind: "item" }, width: "48dp", height: "48dp" }
            - id: textCol
              type: VStack
              flex: 1
              height: auto
              children:
                - { id: lblName,  type: Text, bind: { text: "item.nameKey" },        style: { text: token.body } }
                - { id: lblDesc,  type: Text, bind: { text: "item.descriptionKey" }, style: { text: token.caption }, maxLines: 2 }
            - { id: lblDate,  type: Text, bind: { text: "item.unlockedAt" }, style: { text: token.caption }, visible: { bind: "item.unlocked === true" } }
            - { id: imgLock,  type: Icon, icon: lock, visible: { bind: "item.unlocked === false" } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — read-only display; avatar tap requests change"
  on:
    - { widget: btnBack, event: tap, do: [ nav.back() ] }
    - { widget: avatar,  event: tap, do: [ emit("profile.avatarChangeRequested"), service.call("ProfileService", "openAvatarPicker") ] }
```

## acceptance

```yaml
- id: U-profileScene-1
  given: "scene=profileScene, profile.displayName=\"Alex\", profile.level=7"
  when: "render"
  then: "lblDisplayName shows 'Alex'; lblPlayerLevel shows 'Level 7'"
  test_hint: "unit"

- id: U-profileScene-2
  given: "scene=profileScene, profile.xp.current=40, profile.xp.next=100"
  when: "render"
  then: "barXP shows 40% filled; lblXP shows '40 / 100'"
  test_hint: "unit"

- id: U-profileScene-3
  given: "scene=profileScene, item.unlocked=false"
  when: "render achievement row"
  then: "lock icon visible; unlocked-date hidden"
  test_hint: "unit"

- id: U-profileScene-4
  given: "scene=profileScene, item.unlocked=true, item.unlockedAt=\"2026-04-01\""
  when: "render achievement row"
  then: "unlocked-date label visible with date; lock icon hidden"
  test_hint: "unit"

- id: U-profileScene-5
  given: "scene=profileScene"
  when: "tap avatar"
  then: "profile.avatarChangeRequested emitted; ProfileService.openAvatarPicker invoked"
  test_hint: "UI E2E"

- id: U-profileScene-6
  given: "scene=profileScene"
  when: "tap btnBack"
  then: "navigates back to mainMenuScene"
  test_hint: "UI E2E"
```

## notes

- Profile is read-mostly — only avatar tap performs an action. If product later wants name editing, add an edit button + popup; do not bind a free TextField directly to `profile.displayName` (server validation needed).
- `profile.xp.current` is bound 0..100 to the ProgressBar; if XP overflows the segment, the data source should expose a normalized value or this binding needs a wrapper field.
- Avatar tap emits an event AND invokes a service so the avatar-picker is decoupled from this screen. The picker UI itself is out of PRD scope; surface a follow-up.
- Animation contracts (achievement-row tap pulse, XP-bar fill on level up) live in `DESIGN.md#profile-animations`.
- Open question: friends / leaderboard tab — not in PRD; surface to product before adding.
