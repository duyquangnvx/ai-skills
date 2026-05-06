---
id: resultPopup
type: popup
title: "Level result"
modal: true
dismissible: false
parents: [gameplayScene]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - data: ResultData
  - state: LevelState
  - i18n: I18nKeys
emits: [level.exitRequested, level.retryRequested, level.nextRequested]
listens: []
---

## purpose

End-of-level popup. Shows whether the player won or lost via a single popup with two visual modes (win / lose). On win, displays earned stars and offers Retry and Next. On lose, offers Retry and Quit. Caller (the [[scenes/gameplayScene]]) routes the data via `data.result` ("win" | "lose").

## ui

```yaml
type: ZStack
children:
  - { id: hitBackdrop, type: HitArea, align: center, width: fill, height: fill }

  - id: panel
    type: VStack
    align: center
    width: "85%sw"
    height: auto
    children:
      - id: lblTitle
        type: Text
        bind: { text: "data.titleKey" }
        style: { text: token.h1 }

      - id: stars
        type: Custom
        name: StarRow
        visible: { bind: "$mode === \"win\"" }
        props: { bind: "state.starsEarned" }

      - id: lblScore
        type: Text
        bind: { text: "state.score", fmt: "{n}" }
        style: { text: token.h2 }

      - id: lblBody
        type: Text
        bind: { text: "data.bodyKey" }
        style: { text: token.body }

      - id: actionsRow
        type: HStack
        height: auto
        children:
          - id: btnQuit
            type: Button
            bind: { label: "i18n.result.quit" }
            style: { variant: secondary }
            visible: { bind: "$mode === \"lose\"" }
          - id: btnRetry
            type: Button
            bind: { label: "i18n.result.retry" }
            style: { variant: secondary }
          - id: btnNext
            type: Button
            bind: { label: "i18n.result.next" }
            style: { variant: primary }
            visible: { bind: "$mode === \"win\"" }
```

## modes

```yaml
- id: win
  initial: true
  description: "Win state — stars earned, retry + next visible"
  enter: { do: [ service.call("ProgressService", "saveResult", { result: "win" }) ] }
  on:
    - { widget: btnRetry, event: tap, do: [ ui.closePopup(), emit("level.retryRequested") ],                       goto: closing }
    - { widget: btnNext,  event: tap, do: [ ui.closePopup(), emit("level.nextRequested") ],                        goto: closing }

- id: lose
  description: "Lose state — retry + quit visible, no stars"
  enter: { do: [ service.call("ProgressService", "saveResult", { result: "lose" }) ] }
  on:
    - { widget: btnRetry, event: tap, do: [ ui.closePopup(), emit("level.retryRequested") ],                       goto: closing }
    - { widget: btnQuit,  event: tap, do: [ ui.closePopup(), emit("level.exitRequested") ],                        goto: closing }

- id: closing
  final: true
  description: "Popup closing; parent scene routes"
```

## acceptance

```yaml
- id: U-resultPopup-1
  given: "popup=resultPopup, data.result=\"win\", state.starsEarned=2"
  when: "render"
  then: "mode=win, lblTitle shows win-key, StarRow shows 2 filled stars, btnNext visible, btnQuit hidden"
  test_hint: "unit"

- id: U-resultPopup-2
  given: "popup=resultPopup, data.result=\"lose\""
  when: "render"
  then: "mode=lose, lblTitle shows lose-key, StarRow hidden, btnQuit visible, btnNext hidden"
  test_hint: "unit"

- id: U-resultPopup-3
  given: "popup=resultPopup, mode=win"
  when: "tap btnRetry"
  then: "popup closes, level.retryRequested emitted"
  test_hint: "UI E2E"

- id: U-resultPopup-4
  given: "popup=resultPopup, mode=win"
  when: "tap btnNext"
  then: "popup closes, level.nextRequested emitted"
  test_hint: "UI E2E"

- id: U-resultPopup-5
  given: "popup=resultPopup, mode=lose"
  when: "tap btnQuit"
  then: "popup closes, level.exitRequested emitted"
  test_hint: "UI E2E"

- id: U-resultPopup-6
  given: "popup=resultPopup, dismissible=false"
  when: "tap hitBackdrop or back-button"
  then: "popup does not close"
  test_hint: "UI E2E"
```

## notes

- Single-popup with two FSM modes (`win` / `lose`) is preferred over two separate popups: same widget tree, divergent visibility flags, single owner of the save-result side-effect.
- `data.result` is the caller's input ("win" | "lose"); the popup picks `initial` mode based on it. Implementation: the popup-host treats incoming popup data as the seed for its FSM (engine adapter detail). If your popup runtime can't seed the initial mode this way, replace with two visibility-bound branches.
- `dismissible: false` is intentional — the result is a decision point. Player must pick Retry / Next / Quit.
- Animation contracts (star pop sequence, backdrop fade, panel scale) live in `DESIGN.md#result-animations`.
- Open question: leaderboard / share-score row — not in PRD; surface to product before adding.
