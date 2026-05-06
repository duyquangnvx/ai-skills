---
id: pausePopup
type: popup
title: "Pause"
modal: true
dismissible: false
parents: [gameplayScene]
children: []
sources:
  - "PRD#screen-5-pause"
dataBindings: []
emits: [pause.resumed, pause.quit]
listens: []
---

## purpose

Modal pause overlay opened from [[scenes/gameplayScene]]. Offers Resume (returns to play), Settings (opens [[scenes/settingsScene]]), and Quit (returns to [[scenes/mainMenu]]). Blocks input behind so the gameplay timer stays paused. Not dismissible by tap-outside — players must explicitly choose.

## ui

```yaml
type: ZStack
children:
  - { id: hitBackdrop, type: HitArea, align: center, width: fill, height: fill }

  - id: panel
    type: VStack
    align: center
    width: "70%sw"
    height: auto
    children:
      - { id: lblTitle,    type: Text,   bind: { text: "i18n.pause.title" },    style: { text: token.h1 } }
      - { id: btnResume,   type: Button, bind: { label: "i18n.pause.resume" },  style: { variant: primary } }
      - { id: btnSettings, type: Button, bind: { label: "i18n.pause.settings" }, style: { variant: secondary } }
      - { id: btnQuit,     type: Button, bind: { label: "i18n.pause.quit" },     style: { variant: ghost } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — all actions enabled"
  on:
    - { widget: btnResume,   event: tap, do: [ ui.closePopup(), emit("pause.resumed") ],                       goto: closing }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { widget: btnQuit,     event: tap, do: [ ui.closePopup(), emit("pause.quit"), nav.gotoScene("mainMenu") ], goto: closing }

- id: closing
  final: true
  description: "Popup closing; awaiting teardown"
```

## acceptance

```yaml
- id: U-pausePopup-1
  given: "popup=pausePopup, mode=idle"
  when: "tap btnResume"
  then: "popup closes, pause.resumed emitted, gameplay timer resumes"
  test_hint: "UI E2E"

- id: U-pausePopup-2
  given: "popup=pausePopup, mode=idle"
  when: "tap btnQuit"
  then: "popup closes, pause.quit emitted, navigates to mainMenu"
  test_hint: "UI E2E"

- id: U-pausePopup-3
  given: "popup=pausePopup, mode=idle"
  when: "tap btnSettings"
  then: "navigates to settingsScene"
  test_hint: "UI E2E"

- id: U-pausePopup-4
  given: "popup=pausePopup, dismissible=false"
  when: "tap hitBackdrop"
  then: "popup remains open; no event emitted"
  test_hint: "UI E2E"
```

## notes

- `dismissible: false` is intentional — accidental tap-outside should not silently resume play. Players confirm via Resume.
- Settings button navigates to `settingsScene` rather than opening a settings popup, matching the PRD's "Settings screen" terminology. Returning from settingsScene back to gameplayScene re-opens this pause popup is handled at the gameplayScene level (out of scope here).
- `hitBackdrop` exists to block input behind the panel; it has no tap action because `dismissible: false`.
