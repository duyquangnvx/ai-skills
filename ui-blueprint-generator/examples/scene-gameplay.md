---
id: gameplayScene
type: scene
title: "Gameplay scene"
orientation: portrait
safeArea: true
parents: [mainMenu, levelSelect]
children: [pausePopup, resultPopup, tutorialPopup, settingsPopup]
sources:
  - "specs/gameplay.md#layout"
  - "specs/gameplay.md#animations"
dataBindings:
  - level: LevelData
  - state: LevelState
  - save: SaveData
emits: [level.action, level.complete, level.timeUp, level.boosterUsed]
listens: [timer.tick, settle.complete, tutorial.required, tutorial.dismissed, pause.resumed]
---

## purpose

Main gameplay scene. Hosts the play area (`Custom: BoardView`), a HUD with timer / goal / lives, and a booster bar. All gameplay-mode variants reuse this scene; only the HUD goal binding and `BoardView` props differ per `level.mode`.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,     type: IconButton, align: center-left,  icon: chevron-left }
      - { id: lblLevel,    type: Text,       align: center,       bind: { text: "level.displayIndex", fmt: "Level {n}" }, style: { text: token.h2 } }
      - { id: btnSettings, type: IconButton, align: center-right, icon: gear }

  - id: hud
    type: VStack
    height: auto
    children:
      - { id: lblTimer, type: Text,   bind: { text: "state.timer", fmt: "{mm:ss}" }, style: { text: token.h1 } }
      - { id: lblGoal,  type: Text,   bind: { text: "state.goalText" },              style: { text: token.body } }
      - { id: hearts,   type: Custom, name: HeartRow, props: { bind: "save.hearts.current" } }

  - id: boardRegion
    type: ZStack
    flex: 1
    children:
      - id: board
        type: Custom
        name: BoardView
        bind: "state.board"
        props:
          mode.bind: "level.mode"
        on:
          tap.tile:
            - emit("level.action", "{cell}")

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
          tap:
            - service.call("BoosterService", "useHint")
            - emit("level.boosterUsed", "hint")
      - id: btnShuffle
        type: IconButton
        icon: shuffle
        badge: { bind: "save.boosters.shuffle" }
        enabled: { bind: "save.boosters.shuffle > 0 && state.timer > 0" }
        on:
          tap:
            - service.call("BoosterService", "useShuffle")
            - emit("level.boosterUsed", "shuffle")
      - id: btnAddTime
        type: IconButton
        icon: clock-plus
        badge: { bind: "save.boosters.addTime" }
        enabled: { bind: "save.boosters.addTime > 0 && state.timer > 0" }
        on:
          tap:
            - service.call("BoosterService", "addTime")
            - emit("level.boosterUsed", "addTime")
```

## modes

```yaml
- id: default
  initial: true
  description: "Timer running, board interactive"
  on:
    - widget: btnBack
      event: tap
      do:
        - ui.openPopup("pausePopup")
      goto: paused
    - widget: btnSettings
      event: tap
      do:
        - ui.openPopup("settingsPopup")
    - event: level.timeUp
      do:
        - 'ui.openPopup("resultPopup", { result: "lose" })'
      goto: gameOver
    - event: level.complete
      do:
        - 'ui.openPopup("resultPopup", { result: "win" })'
      goto: gameOver
    - event: tutorial.required
      goto: tutorialBlocking

- id: paused
  description: "Pause popup open, timer frozen, board input blocked"
  enter:
    do:
      - emit("timer.pause")
  exit:
    do:
      - emit("timer.resume")
  on:
    - event: pause.resumed
      goto: default

- id: tutorialBlocking
  description: "First-encounter tutorial popup shown; timer paused, board frozen"
  enter:
    do:
      - emit("timer.pause")
  exit:
    do:
      - emit("timer.resume")
  on:
    - event: tutorial.dismissed
      goto: default

- id: gameOver
  final: true
  description: "Result popup shown, board frozen but visible"
```

## acceptance

```yaml
- id: U-gameplayScene-1
  given: "scene=gameplayScene, mode=default"
  when: "tap btnBack"
  then: "pausePopup opens, timer pauses, mode=paused"
  test_hint: "UI E2E"

- id: U-gameplayScene-2
  given: "settle animation in progress"
  when: "tap btnBack"
  then: "settle completes first, then pausePopup opens"

- id: U-gameplayScene-3
  given: "save.boosters.hint === 0"
  when: "render btnHint"
  then: "btnHint is disabled (greyed out)"
  test_hint: "unit"

- id: U-gameplayScene-4
  given: "first encounter of level.mode requiring tutorial"
  when: "scene enters and tutorial.required is emitted"
  then: "tutorialPopup fires, mode=tutorialBlocking, timer paused"
  test_hint: "UI E2E"
```

## notes

- HUD `lblGoal` binding adapts per `level.mode` — see [[sources:specs/gameplay#modes]] for mode-specific goal formats.
- `BoardView` and `HeartRow` are `Custom` widgets; implementations live in `src/features/board/` and `src/features/hud/`.
- During settle animation, all input is blocked at the engine layer — see [[U-gameplayScene-2]].
- Animation contracts (tile-tap scale, match-success burst, settle tween) live in `DESIGN.md#gameplay-animations`. Blueprint declares only triggers via `emit()` actions.
- Booster buttons live on `## ui` widget-level `on:` because they are state-independent — guard via `enabled.bind` (`state.timer > 0` is false during pause). They never need a transition.
