---
id: gameplayScene
type: scene
title: "Gameplay scene"
zIndex: 0
orientation: portrait
safeArea: true
parents: [mainMenu, levelSelect]
children: [pausePopup, resultPopup, tutorialPopup, settingsPopup]
gdd:
  - "specs/gameplay.md#layout"
  - "specs/gameplay.md#animations"
dataBindings:
  - level: LevelData
  - state: LevelState
  - save: SaveData
emits: [level.action, level.complete, level.timeUp, level.boosterUsed]
listens: [timer.tick, settle.complete, tutorial.dismissed]
---

## purpose

Main gameplay scene. Hosts the play area (`Custom: BoardView`), a HUD with timer / goal / lives, and a booster bar. All gameplay-mode variants reuse this scene; only HUD goal binding and `BoardView` props differ per `level.mode`.

## layout

```yaml
root: { type: VStack }
regions:
  - { id: topBar, type: ZStack, height: "10%sh" }
  - { id: hud, type: VStack, height: auto }
  - { id: board, type: ZStack, flex: 1 }
  - { id: boosters, type: HStack, height: "max(70dp, 10%sh)" }
```

## widgets

```yaml
- id: btnBack
  type: IconButton
  region: topBar
  align: center-left
  icon: chevron-left
  on:
    tap: [ ui.openPopup("pausePopup"), state.set("paused") ]

- id: lblLevel
  type: Text
  region: topBar
  align: center
  bind: { text: "level.displayIndex", fmt: "Level {n}" }
  style: { text: token.h2 }

- id: btnSettings
  type: IconButton
  region: topBar
  align: center-right
  icon: gear
  on:
    tap: [ ui.openPopup("settingsPopup") ]

- id: lblTimer
  type: Text
  region: hud
  bind: { text: "state.timer", fmt: "{mm:ss}" }
  style: { text: token.h1 }

- id: lblGoal
  type: Text
  region: hud
  bind: { text: "state.goalText" }
  style: { text: token.body }

- id: hearts
  type: Custom
  name: HeartRow
  region: hud
  props:
    bind: "save.hearts.current"

- id: board
  type: Custom
  name: BoardView
  region: board
  props:
    bind: "state.board"
    mode.bind: "level.mode"
  on:
    tap.tile: [ emit("level.action", "{cell}") ]

- id: btnHint
  type: IconButton
  region: boosters
  icon: lightbulb
  badge: { bind: "save.boosters.hint" }
  enabled: { bind: "save.boosters.hint > 0 && state.timer > 0" }
  on:
    tap: [ service.call("BoosterService", "useHint"), emit("level.boosterUsed", "hint") ]

- id: btnShuffle
  type: IconButton
  region: boosters
  icon: shuffle
  badge: { bind: "save.boosters.shuffle" }
  enabled: { bind: "save.boosters.shuffle > 0 && state.timer > 0" }
  on:
    tap: [ service.call("BoosterService", "useShuffle"), emit("level.boosterUsed", "shuffle") ]

- id: btnAddTime
  type: IconButton
  region: boosters
  icon: clock-plus
  badge: { bind: "save.boosters.addTime" }
  enabled: { bind: "save.boosters.addTime > 0 && state.timer > 0" }
  on:
    tap: [ service.call("BoosterService", "addTime"), emit("level.boosterUsed", "addTime") ]
```

## states

```yaml
states:
  - id: default
    description: "Timer running, board interactive"
    initial: true
  - id: paused
    description: "Pause popup open, timer frozen, board input blocked"
    enter: { do: [ emit("timer.pause") ] }
    exit:  { do: [ emit("timer.resume") ] }
  - id: tutorialBlocking
    description: "First-encounter tutorial popup shown; timer paused, board frozen"
    enter: { do: [ emit("timer.pause") ] }
    exit:  { do: [ emit("timer.resume") ] }
  - id: gameOver
    description: "Result popup shown, board frozen but visible"
    final: true
```

## actions

```yaml
- on: { event: timer.tick }
  do: [ noop() ]

- on: { event: level.timeUp }
  do: [ ui.openPopup("resultPopup", { result: "lose" }), state.set("gameOver") ]

- on: { event: level.complete }
  do: [ ui.openPopup("resultPopup", { result: "win" }), state.set("gameOver") ]

- on: { event: tutorial.dismissed, where: "$state === \"tutorialBlocking\"" }
  do: [ state.set("default") ]
```

## animations

```yaml
- id: tileTap
  trigger: "widget.tap on board cell"
  spec: "scale 1.05 + glow"
  duration: 80ms
  blocksInput: false

- id: matchSuccess
  trigger: "event: level.action where match"
  spec: "particle burst then tile pop"
  duration: 450ms
  blocksInput: false

- id: settle
  trigger: "event: settle.start"
  spec: "linear move per tile"
  duration: 150ms
  blocksInput: false
```

## acceptance

```yaml
- id: U1
  given: "scene=gameplayScene, $state=default"
  when: "tap btnBack"
  then: "pausePopup opens, timer pauses"
  test_hint: "UI E2E"

- id: U2
  given: "settle animation in progress"
  when: "tap btnBack"
  then: "settle completes first, then pausePopup opens"

- id: U3
  given: "save.boosters.hint === 0"
  when: "render btnHint"
  then: "btnHint is disabled (greyed out)"
  test_hint: "unit"

- id: U4
  given: "first encounter of level.mode requiring tutorial"
  when: "scene enters"
  then: "tutorialPopup fires before timer starts; $state=tutorialBlocking"
  test_hint: "UI E2E"
```

## notes

- HUD `lblGoal` binding adapts per `level.mode` — see [[gdd:specs/gameplay#modes]] for mode-specific goal formats.
- `BoardView` is a `Custom` widget; implementation lives in `src/features/board/`. Same applies to `HeartRow`.
- During settle animation, all input is blocked at the engine layer — see U2 for the back-button interaction.
- Z-layer convention: scene children stay below 100 so popup z=100 overlays cleanly.
