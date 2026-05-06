---
id: pausePopup
type: popup
title: "Pause"
modal: true
dismissible: true
parents: [gameplayScene]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - i18n: I18nKeys
emits: [pause.resumed, level.exitRequested, level.retryRequested]
listens: []
---

## purpose

In-level pause overlay. Freezes gameplay (the parent [[scenes/gameplayScene]] enters its `paused` mode and pauses its timer). Offers three actions: Resume (closes and resumes play), Settings (opens settings), Quit (exits to level select). Tap-outside also resumes.

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
      - { id: lblTitle,    type: Text,   bind: { text: "i18n.pause.title" },     style: { text: token.h1 } }
      - { id: btnResume,   type: Button, bind: { label: "i18n.pause.resume" },   style: { variant: primary } }
      - { id: btnSettings, type: Button, bind: { label: "i18n.pause.settings" }, style: { variant: secondary } }
      - { id: btnQuit,     type: Button, bind: { label: "i18n.pause.quit" },     style: { variant: ghost } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — three buttons enabled, awaiting input"
  on:
    - { widget: btnResume,   event: tap, do: [ ui.closePopup(), emit("pause.resumed") ],                                 goto: closing }
    - { widget: hitBackdrop, event: tap, do: [ ui.closePopup(), emit("pause.resumed") ],                                 goto: closing }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { widget: btnQuit,     event: tap, do: [ ui.closePopup(), emit("level.exitRequested") ],                            goto: closing }

- id: closing
  final: true
  description: "Popup closing; parent scene resumes or routes"
```

## acceptance

```yaml
- id: U-pausePopup-1
  given: "popup=pausePopup, mode=idle"
  when: "tap btnResume"
  then: "popup closes, pause.resumed emitted, parent scene returns to playing"
  test_hint: "UI E2E"

- id: U-pausePopup-2
  given: "popup=pausePopup, dismissible=true"
  when: "tap hitBackdrop"
  then: "popup closes, pause.resumed emitted (same as Resume)"
  test_hint: "UI E2E"

- id: U-pausePopup-3
  given: "popup=pausePopup, mode=idle"
  when: "tap btnSettings"
  then: "navigates to settingsScene (popup remains open beneath until settings closes)"
  test_hint: "UI E2E"

- id: U-pausePopup-4
  given: "popup=pausePopup, mode=idle"
  when: "tap btnQuit"
  then: "popup closes, level.exitRequested emitted, parent navigates to levelSelectScene"
  test_hint: "UI E2E"
```

## notes

- Tap-outside maps to Resume (the safe default). If product wants tap-outside to be a no-op, set `dismissible: false`.
- Settings is opened as a scene navigation rather than a nested popup — keeps the navigation stack simple. Pause popup remains in the stack and resumes when settings is dismissed.
- The pause popup does not own a confirm-quit step; tap on Quit is final. If accidental-quit becomes a complaint, wrap with a confirm popup or change `btnQuit` to open one.
- Animation contracts (panel scale-fade, backdrop fade) live in `DESIGN.md#popup-animations`.
