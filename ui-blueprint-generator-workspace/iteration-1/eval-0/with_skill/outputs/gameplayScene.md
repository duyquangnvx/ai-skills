---
id: gameplayScene
type: scene
title: "Gameplay"
orientation: portrait
safeArea: true
parents: [levelSelectScene]
children: [pausePopup, resultPopup]
sources:
  - "PRD.md#screens"
dataBindings:
  - level: LevelData
  - state: LevelState
  - save: SaveData
  - i18n: I18nKeys
emits: [level.action, level.complete, level.timeUp, level.boosterUsed]
listens: [timer.tick, settle.complete, pause.resumed, level.exitRequested, level.retryRequested, level.nextRequested]
---

## purpose

Main play scene. Hosts the match-3 board (`Custom: BoardView`), a HUD (level label, moves/timer, goal, score), and a booster bar. Routes to [[popups/pausePopup]] on pause and to [[popups/resultPopup]] on win or lose.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnPause, type: IconButton, align: center-left,  icon: pause }
      - { id: lblLevel, type: Text,       align: center,       bind: { text: "level.displayIndex", fmt: "Level {n}" }, style: { text: token.h2 } }
      - { id: lblScore, type: Text,       align: center-right, bind: { text: "state.score" },                          style: { text: token.body } }

  - id: hud
    type: HStack
    height: auto
    children:
      - id: movesPanel
        type: VStack
        flex: 1
        children:
          - { id: lblMovesValue, type: Text, bind: { text: "state.movesLeft" },          style: { text: token.h1 } }
          - { id: lblMovesLabel, type: Text, bind: { text: "i18n.gameplay.movesLabel" }, style: { text: token.caption } }
      - id: goalPanel
        type: VStack
        flex: 1
        children:
          - { id: lblGoalValue, type: Text, bind: { text: "state.goalProgress" },       style: { text: token.h1 } }
          - { id: lblGoalLabel, type: Text, bind: { text: "state.goalLabel" },          style: { text: token.caption } }
      - id: heartsPanel
        type: VStack
        flex: 1
        children:
          - { id: hearts, type: Custom, name: HeartRow, props: { bind: "save.hearts.current" } }

  - id: boardRegion
    type: ZStack
    flex: 1
    children:
      - id: board
        type: Custom
        name: BoardView
        props:
          bind: "state.board"
          mode.bind: "level.mode"
        on:
          tap.tile: [ emit("level.action", "{cell}") ]

  - id: boosters
    type: HStack
    height: "max(70dp, 10%sh)"
    children:
      - id: btnHint
        type: IconButton
        icon: lightbulb
        badge: { bind: "save.boosters.hint" }
        enabled: { bind: "save.boosters.hint > 0 && state.movesLeft > 0" }
        on:
          tap: [ service.call("BoosterService", "useHint"), emit("level.boosterUsed", "hint") ]
      - id: btnShuffle
        type: IconButton
        icon: shuffle
        badge: { bind: "save.boosters.shuffle" }
        enabled: { bind: "save.boosters.shuffle > 0 && state.movesLeft > 0" }
        on:
          tap: [ service.call("BoosterService", "useShuffle"), emit("level.boosterUsed", "shuffle") ]
      - id: btnBomb
        type: IconButton
        icon: bomb
        badge: { bind: "save.boosters.bomb" }
        enabled: { bind: "save.boosters.bomb > 0 && state.movesLeft > 0" }
        on:
          tap: [ service.call("BoosterService", "useBomb"), emit("level.boosterUsed", "bomb") ]
```

## modes

```yaml
- id: playing
  initial: true
  description: "Board interactive, moves/timer counting down"
  on:
    - { widget: btnPause, event: tap, do: [ ui.openPopup("pausePopup") ],                              goto: paused }
    - { event: level.complete,        do: [ ui.openPopup("resultPopup", { result: "win" }) ],         goto: gameOver }
    - { event: level.timeUp,          do: [ ui.openPopup("resultPopup", { result: "lose" }) ],        goto: gameOver }

- id: paused
  description: "Pause popup open; board input blocked"
  enter: { do: [ emit("timer.pause") ] }
  exit:  { do: [ emit("timer.resume") ] }
  on:
    - { event: pause.resumed,        goto: playing }
    - { event: level.exitRequested,  do: [ ui.closePopup("pausePopup"), nav.replace("levelSelectScene") ] }
    - { event: level.retryRequested, do: [ ui.closePopup("pausePopup"), service.call("LevelService", "restart") ], goto: playing }

- id: gameOver
  description: "Result popup shown; board frozen"
  on:
    - { event: level.exitRequested,  do: [ ui.closePopup("resultPopup"), nav.replace("levelSelectScene") ] }
    - { event: level.retryRequested, do: [ ui.closePopup("resultPopup"), service.call("LevelService", "restart") ], goto: playing }
    - { event: level.nextRequested,  do: [ ui.closePopup("resultPopup"), service.call("LevelService", "loadNext") ], goto: playing }
```

## acceptance

```yaml
- id: U-gameplayScene-1
  given: "scene=gameplayScene, mode=playing"
  when: "tap btnPause"
  then: "pausePopup opens, mode=paused, timer paused via emit(timer.pause)"
  test_hint: "UI E2E"

- id: U-gameplayScene-2
  given: "scene=gameplayScene, mode=playing, save.boosters.hint=0"
  when: "render"
  then: "btnHint is disabled (greyed out)"
  test_hint: "unit"

- id: U-gameplayScene-3
  given: "scene=gameplayScene, mode=playing"
  when: "level.complete event received"
  then: "resultPopup opens with result=win, mode=gameOver"
  test_hint: "UI E2E"

- id: U-gameplayScene-4
  given: "scene=gameplayScene, mode=playing"
  when: "level.timeUp event received"
  then: "resultPopup opens with result=lose, mode=gameOver"
  test_hint: "UI E2E"

- id: U-gameplayScene-5
  given: "scene=gameplayScene, mode=paused"
  when: "level.retryRequested event received"
  then: "pausePopup closes, LevelService.restart invoked, mode=playing"
  test_hint: "UI E2E"

- id: U-gameplayScene-6
  given: "scene=gameplayScene, mode=gameOver"
  when: "level.exitRequested event received"
  then: "resultPopup closes, navigation replaces with levelSelectScene"
  test_hint: "UI E2E"
```

## notes

- HUD goal binding is generic (`state.goalProgress`, `state.goalLabel`) so the same blueprint covers any match-3 goal type (clear-X, score-target, drop-Y) without per-type variants.
- Both moves-based and timer-based variants are supported by a single `state.movesLeft`/`state.timer` source; pick which is shown by binding to whichever is non-null. Surface to engineering if both must be visible simultaneously.
- `BoardView` is a `Custom` widget; implementation lives in `src/features/board/`. Animation contracts (tile-tap scale, match burst, settle tween) live in `DESIGN.md#gameplay-animations`.
- Pause popup and result popup own their own button sets and emit `level.exitRequested` / `level.retryRequested` so this scene doesn't need to know which button was pressed.
- Open question: cascading-failure mode (no moves left but board still settling) — confirm whether `level.timeUp` covers the "out of moves" case or a separate event is needed.
