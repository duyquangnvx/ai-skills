---
id: resultPopup
type: popup
title: "Round result"
modal: true
dismissible: false
parents: [gameplayScene]
children: []
sources:
  - "PRD#screen-6"
dataBindings:
  - data: ResultPopupData
  - state: LevelState
  - i18n: I18nKeys
emits: [result.dismissed, result.retryRequested, result.nextRequested]
listens: []
---

## purpose

End-of-round popup shown after [[scenes/gameplayScene]] settles into win or lose. Displays earned stars (0–3), a localized title (win/lose), and offers retry and home actions. On a win, also offers "next level". Caller passes `data.result` (`"win"` or `"lose"`) and `data.starsEarned` (int 0–3).

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
      - id: lblTitle
        type: Text
        bind: { text: "i18n.result.title" }
        visible: { bind: "data.result === \"win\" || data.result === \"lose\"" }

      - id: stars
        type: Custom
        name: StarRow
        props:
          bind: "data.starsEarned"
          max: 3
        visible: { bind: "data.result === \"win\"" }

      - id: lblStarsCount
        type: Text
        bind: { text: "data.starsEarned", fmt: "★ {n} / 3" }
        visible: { bind: "data.result === \"win\"" }

      - id: lblLoseMessage
        type: Text
        bind: { text: "i18n.result.loseMessage" }
        visible: { bind: "data.result === \"lose\"" }

      - id: btnRetry
        type: Button
        bind: { label: "i18n.result.retry" }
        style: { variant: secondary }

      - id: btnNext
        type: Button
        bind: { label: "i18n.result.next" }
        style: { variant: primary }
        visible: { bind: "data.result === \"win\"" }

      - id: btnHome
        type: Button
        bind: { label: "i18n.result.home" }
        style: { variant: secondary }
```

## modes

```yaml
- id: showing
  initial: true
  description: "Result displayed; awaiting user choice"
  on:
    - { widget: btnRetry, event: tap, do: [ ui.closePopup(), emit("result.retryRequested"), nav.gotoScene("gameplayScene", { levelId: "{state.currentLevelId}" }) ], goto: dismissed }
    - { widget: btnNext,  event: tap, where: "data.result === \"win\"", do: [ ui.closePopup(), emit("result.nextRequested"), nav.gotoScene("gameplayScene", { levelId: "{state.nextLevelId}" }) ], goto: dismissed }
    - { widget: btnHome,  event: tap, do: [ ui.closePopup(), emit("result.dismissed"), nav.gotoScene("mainMenuScene") ], goto: dismissed }

- id: dismissed
  final: true
  description: "Popup closed; navigation handed off"
```

## acceptance

```yaml
- id: U-resultPopup-1
  given: "popup=resultPopup, data.result === \"win\", data.starsEarned = 2"
  when: "render panel"
  then: "stars widget shows 2/3, btnNext is visible, lblLoseMessage is hidden"
  test_hint: "unit"

- id: U-resultPopup-2
  given: "popup=resultPopup, data.result === \"lose\""
  when: "render panel"
  then: "lblLoseMessage is visible, stars widget hidden, btnNext hidden"
  test_hint: "unit"

- id: U-resultPopup-3
  given: "popup=resultPopup, mode=showing"
  when: "tap btnRetry"
  then: "popup closes, navigates to gameplayScene with same levelId, mode=dismissed"
  test_hint: "UI E2E"

- id: U-resultPopup-4
  given: "popup=resultPopup, data.result === \"win\", mode=showing"
  when: "tap btnNext"
  then: "popup closes, navigates to gameplayScene with state.nextLevelId, mode=dismissed"
  test_hint: "UI E2E"

- id: U-resultPopup-5
  given: "popup=resultPopup, mode=showing"
  when: "tap btnHome"
  then: "popup closes, navigates to mainMenuScene, mode=dismissed"
  test_hint: "UI E2E"
```

## notes

- Win and lose share one popup — switched by `data.result`. Visibility-bound widgets handle the variant rather than two separate popups.
- `StarRow` is a declared project widget; for the lose state it's hidden. Implementations may animate star fill-in on win-entry — animation contract belongs in `DESIGN.md`.
- Retry and next route through `nav.gotoScene("gameplayScene", ...)` — engine adapter is responsible for tearing down/re-initing the gameplay session.
- `state.currentLevelId` and `state.nextLevelId` are read from level state so the popup itself doesn't need to receive them as data — keeps caller payload minimal.
- A "ResultPopupData" type is declared in `dataBindings` so type checkers can validate `data.result` ∈ {"win", "lose"} and `data.starsEarned` ∈ [0, 3].
