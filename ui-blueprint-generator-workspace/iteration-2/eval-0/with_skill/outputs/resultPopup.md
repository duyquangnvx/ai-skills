---
id: resultPopup
type: popup
title: "Result"
modal: true
dismissible: false
parents: [gameplayScene]
children: []
sources:
  - "PRD#screen-6-result"
dataBindings:
  - data: ResultData
  - state: LevelState
emits: [result.retry, result.dismissed, result.next]
listens: []
---

## purpose

Modal end-of-level overlay shown after [[scenes/gameplayScene]] reaches `level.complete` or `level.timeUp`. Communicates win-or-lose, displays stars earned (win) or zero stars (lose), and offers Retry, Next (win only), and Quit. Caller passes `data.result` ("win" | "lose") and `data.stars` (0-3) when opening.

## ui

```yaml
type: ZStack
children:
  - { id: hitBackdrop, type: HitArea, align: center, width: fill, height: fill }

  - id: panel
    type: VStack
    align: center
    width: "80%sw"
    height: auto
    children:
      - id: imgBanner
        type: Image
        asset: "result.bannerWin"
        fit: contain
        width: "60%sw"
        height: auto
        visible: { bind: "data.result === \"win\"" }

      - id: imgBannerLose
        type: Image
        asset: "result.bannerLose"
        fit: contain
        width: "60%sw"
        height: auto
        visible: { bind: "data.result === \"lose\"" }

      - id: lblTitle
        type: Text
        bind: { text: "i18n.result.title" }
        style: { text: token.h1 }

      - id: lblScore
        type: Text
        bind: { text: "state.score", fmt: "Score: {n}" }
        style: { text: token.h2 }

      - id: stars
        type: Custom
        name: StarRow
        props:
          bind: "data.stars"
          max: 3

      - id: actions
        type: HStack
        height: auto
        children:
          - { id: btnQuit,  type: Button, bind: { label: "i18n.result.quit" },  style: { variant: ghost },     flex: 1 }
          - { id: btnRetry, type: Button, bind: { label: "i18n.result.retry" }, style: { variant: secondary }, flex: 1 }
          - id: btnNext
            type: Button
            bind: { label: "i18n.result.next" }
            style: { variant: primary }
            flex: 1
            visible: { bind: "data.result === \"win\"" }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — actions awaiting input"
  on:
    - { widget: btnRetry, event: tap, do: [ ui.closePopup(), emit("result.retry"), nav.replace("gameplayScene", { levelId: "{data.levelId}" }) ], goto: closing }
    - { widget: btnNext,  event: tap, where: "data.result === \"win\"", do: [ ui.closePopup(), emit("result.next"), nav.replace("gameplayScene", { levelId: "{data.nextLevelId}" }) ], goto: closing }
    - { widget: btnQuit,  event: tap, do: [ ui.closePopup(), emit("result.dismissed"), nav.gotoScene("levelSelect") ], goto: closing }

- id: closing
  final: true
  description: "Popup closing; navigation in flight"
```

## acceptance

```yaml
- id: U-resultPopup-1
  given: "popup=resultPopup with data.result===\"win\" and data.stars===3"
  when: "popup renders"
  then: "imgBanner (win) is visible, btnNext is visible, StarRow shows 3 of 3 filled"
  test_hint: "unit"

- id: U-resultPopup-2
  given: "popup=resultPopup with data.result===\"lose\""
  when: "popup renders"
  then: "imgBannerLose is visible, btnNext is hidden, StarRow shows 0 of 3 filled"
  test_hint: "unit"

- id: U-resultPopup-3
  given: "popup=resultPopup, mode=idle"
  when: "tap btnRetry"
  then: "popup closes, result.retry emitted, gameplayScene replaces with current levelId"
  test_hint: "UI E2E"

- id: U-resultPopup-4
  given: "popup=resultPopup with data.result===\"win\""
  when: "tap btnNext"
  then: "popup closes, result.next emitted, gameplayScene replaces with nextLevelId"
  test_hint: "UI E2E"

- id: U-resultPopup-5
  given: "popup=resultPopup, mode=idle"
  when: "tap btnQuit"
  then: "popup closes, result.dismissed emitted, navigates to levelSelect"
  test_hint: "UI E2E"
```

## notes

- `data.levelId` and `data.nextLevelId` are passed by the caller (gameplayScene) when opening this popup. `data.result` and `data.stars` are required.
- `nav.replace` is used for retry/next so the new gameplayScene replaces the prior one in the navigation stack rather than stacking.
- Win/lose banner uses two separate Image widgets toggled by `visible.bind` — keeps the boolean DSL simple. An alternative would be a `Custom: ResultBanner` widget; declared as two Images here so it stays in universal vocabulary.
- Animation of stars filling in sequence is engine-side; lives in `DESIGN.md#result-animations`.
