---
id: gameplayScene
type: scene
title: "Gameplay scene"
orientation: portrait
safeArea: true
parents: [levelSelect]
children: [pausePopup, resultPopup]
sources:
  - "PRD#screen-4-gameplay"
dataBindings:
  - level: LevelData
  - state: LevelState
  - save: SaveData
emits: [level.action, level.complete, level.timeUp, level.boosterUsed, timer.pause, timer.resume]
listens: [timer.tick, settle.complete, pause.resumed, result.dismissed]
---

## purpose

Main match-3 gameplay surface. Hosts the HUD (level label, timer, score, lives), the play area as a `Custom: BoardView`, and a booster bar. Drives state transitions for pause / win / lose and forwards player input to gameplay services. Entered from [[scenes/levelSelect]] and opens [[popups/pausePopup]] or [[popups/resultPopup]] as children.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnPause,   type: IconButton, align: center-left,  icon: pause }
      - { id: lblLevel,   type: Text,       align: center,       bind: { text: "level.displayIndex", fmt: "Level {n}" }, style: { text: token.h2 } }
      - { id: lblScore,   type: Text,       align: center-right, bind: { text: "state.score" },                          style: { text: token.h2 } }

  - id: hud
    type: HStack
    height: auto
    children:
      - { id: lblTimer, type: Text,   flex: 1, bind: { text: "state.timer", fmt: "{mm:ss}" }, style: { text: token.h1 } }
      - { id: lblGoal,  type: Text,   flex: 2, bind: { text: "state.goalText" },              style: { text: token.body } }
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
      - id: btnBomb
        type: IconButton
        icon: bomb
        badge: { bind: "save.boosters.bomb" }
        enabled: { bind: "save.boosters.bomb > 0 && state.timer > 0" }
        on:
          tap: [ service.call("BoosterService", "useBomb"), emit("level.boosterUsed", "bomb") ]
```

## modes

```yaml
- id: default
  initial: true
  description: "Timer running, board interactive, boosters tappable"
  on:
    - { widget: btnPause, event: tap, do: [ ui.openPopup("pausePopup") ],                       goto: paused }
    - { event: level.timeUp,          do: [ ui.openPopup("resultPopup", { result: "lose" }) ],  goto: gameOver }
    - { event: level.complete,        do: [ ui.openPopup("resultPopup", { result: "win" }) ],   goto: gameOver }

- id: paused
  description: "Pause popup open; timer frozen, board input blocked"
  enter: { do: [ emit("timer.pause") ] }
  exit:  { do: [ emit("timer.resume") ] }
  on:
    - { event: pause.resumed, goto: default }

- id: gameOver
  final: true
  description: "Result popup shown; board frozen but visible behind popup"
```

## acceptance

```yaml
- id: U-gameplayScene-1
  given: "scene=gameplayScene, mode=default"
  when: "tap btnPause"
  then: "pausePopup opens, timer pauses, mode=paused"
  test_hint: "UI E2E"

- id: U-gameplayScene-2
  given: "level objectives are met"
  when: "level.complete event fires"
  then: "resultPopup opens with result=win, mode=gameOver"
  test_hint: "integration"

- id: U-gameplayScene-3
  given: "state.timer reaches 0"
  when: "level.timeUp event fires"
  then: "resultPopup opens with result=lose, mode=gameOver"
  test_hint: "integration"

- id: U-gameplayScene-4
  given: "save.boosters.hint === 0"
  when: "render btnHint"
  then: "btnHint is disabled (greyed out)"
  test_hint: "unit"

- id: U-gameplayScene-5
  given: "mode=paused"
  when: "pause.resumed event fires"
  then: "timer resumes, mode=default"
  test_hint: "UI E2E"
```

## notes

- **Confirmation gate override (Skill Step 2/4/5):** The user requested "no need to confirm" with a deadline. Per skill guidance, this would normally pause once for re-confirmation, but the user pre-emptively declined gates in their request and the test-session framing forbids clarifying questions. The override is recorded here per the skill rule. Sensible defaults applied: portrait orientation, scoped acceptance IDs, game domain config based on the canonical template, three boosters (hint/shuffle/bomb) inferred from "boosters" plural.
- HUD `lblGoal` text is bound to `state.goalText` so it adapts per level mode (collect / clear / score). Per-mode goal copy lives in i18n.
- `BoardView` and `HeartRow` are `Custom` widgets — engine implementations referenced by name only.
- Booster buttons live on `## ui` widget-level `on:` because they are state-independent — `enabled.bind` already gates them during `paused` (timer === 0 isn't the gate; the popup blocks input above board, but the bind `state.timer > 0` is true; rely on popup modality to block taps).
- Animation contracts (tile-tap, match-burst, settle) live in `DESIGN.md#gameplay-animations`. Blueprint declares only triggers via `emit()` actions.
