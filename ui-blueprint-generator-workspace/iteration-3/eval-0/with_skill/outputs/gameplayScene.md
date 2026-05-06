---
id: gameplayScene
type: scene
title: "Gameplay scene"
orientation: portrait
safeArea: true
parents: [levelSelectScene]
children: [pausePopup, resultPopup]
sources:
  - "PRD#screen-4"
dataBindings:
  - level: LevelData
  - state: LevelState
  - save: SaveData
emits: [level.action, level.complete, level.timeUp, level.boosterUsed]
listens: [timer.tick, settle.complete, pause.resumed, result.dismissed]
---

## purpose

Hosts the active match-3 round. Includes a top bar (back/level/settings), a HUD showing timer / goal / hearts, the playfield (`Custom: BoardView`), and a booster bar. Drives win/lose via the state machine, surfacing [[popups/pausePopup]] and [[popups/resultPopup]] as appropriate.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnPause,    type: IconButton, align: center-left,  icon: pause }
      - { id: lblLevel,    type: Text,       align: center,       bind: { text: "level.displayIndex", fmt: "Level {n}" } }
      - { id: btnSettings, type: IconButton, align: center-right, icon: gear }

  - id: hud
    type: VStack
    height: auto
    children:
      - { id: lblTimer, type: Text, bind: { text: "state.timer", fmt: "{mm:ss}" } }
      - { id: lblGoal,  type: Text, bind: { text: "state.goalText" } }
      - { id: hearts,   type: Custom, name: HeartRow, props: { bind: "save.hearts.current" } }

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
        enabled: { bind: "save.boosters.hint > 0 && state.timer > 0" }
        on:
          tap: [ service.call("BoosterService", "useHint"), emit("level.boosterUsed", "hint") ]
      - id: btnShuffle
        type: IconButton
        icon: shuffle
        badge: { bind: "save.boosters.shuffle" }
        enabled: { bind: "save.boosters.shuffle > 0 && state.timer > 0" }
        on:
          tap: [ service.call("BoosterService", "useShuffle"), emit("level.boosterUsed", "shuffle") ]
      - id: btnAddTime
        type: IconButton
        icon: clock-plus
        badge: { bind: "save.boosters.addTime" }
        enabled: { bind: "save.boosters.addTime > 0 && state.timer > 0" }
        on:
          tap: [ service.call("BoosterService", "addTime"), emit("level.boosterUsed", "addTime") ]
```

## modes

```yaml
- id: default
  initial: true
  description: "Timer running, board interactive"
  on:
    - { widget: btnPause,    event: tap, do: [ ui.openPopup("pausePopup") ],                       goto: paused }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { event: level.timeUp,             do: [ ui.openPopup("resultPopup", { result: "lose" }) ],  goto: gameOver }
    - { event: level.complete,           do: [ ui.openPopup("resultPopup", { result: "win" }) ],   goto: gameOver }

- id: paused
  description: "Pause popup open, timer frozen, board input blocked"
  enter: { do: [ emit("timer.pause") ] }
  exit:  { do: [ emit("timer.resume") ] }
  on:
    - { event: pause.resumed, goto: default }

- id: gameOver
  final: true
  description: "Result popup shown, board frozen but visible"
```

## acceptance

```yaml
- id: U-gameplayScene-1
  given: "scene=gameplayScene, mode=default"
  when: "tap btnPause"
  then: "pausePopup opens, timer pauses, mode=paused"
  test_hint: "UI E2E"

- id: U-gameplayScene-2
  given: "scene=gameplayScene, mode=default, state.timer > 0"
  when: "level.timeUp event fires"
  then: "resultPopup opens with result=lose, mode=gameOver"
  test_hint: "UI E2E"

- id: U-gameplayScene-3
  given: "scene=gameplayScene, mode=default, all goals satisfied"
  when: "level.complete event fires"
  then: "resultPopup opens with result=win, mode=gameOver"
  test_hint: "UI E2E"

- id: U-gameplayScene-4
  given: "save.boosters.hint === 0"
  when: "render btnHint"
  then: "btnHint is disabled"
  test_hint: "unit"

- id: U-gameplayScene-5
  given: "scene=gameplayScene, mode=paused"
  when: "pause.resumed event fires"
  then: "mode=default, timer resumes"
  test_hint: "UI E2E"
```

## notes

- `BoardView` and `HeartRow` are `Custom` widgets; implementations live outside the blueprint.
- Settings is opened as a full scene (per PRD #7) — not a popup — via `nav.gotoScene("settingsScene")`. On return, `nav.back` re-enters gameplay.
- Booster buttons live on widget-level `on:` because they are state-independent — `enabled.bind` covers pause via `state.timer > 0`.
- Animation contracts (tile-tap, match-burst, settle tween) belong in `DESIGN.md` once authored.
