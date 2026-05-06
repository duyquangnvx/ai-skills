---
id: pausePopup
type: popup
title: "Pause"
modal: true
dismissible: false
parents: [gameplayScene]
children: []
sources:
  - "PRD#screen-5"
dataBindings:
  - i18n: I18nKeys
emits: [pause.resumed]
listens: []
---

## purpose

Mid-round pause overlay. Freezes [[scenes/gameplayScene]] and offers three actions: resume (close + emit `pause.resumed`), settings (navigate to [[scenes/settingsScene]]), quit (return to [[scenes/mainMenuScene]]). Non-dismissible by tap-outside — players must make an explicit choice.

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
      - { id: lblTitle,    type: Text,   bind: { text: "i18n.pause.title" } }
      - { id: btnResume,   type: Button, bind: { label: "i18n.pause.resume" },   style: { variant: primary } }
      - { id: btnSettings, type: Button, bind: { label: "i18n.pause.settings" }, style: { variant: secondary } }
      - { id: btnQuit,     type: Button, bind: { label: "i18n.pause.quit" },     style: { variant: secondary } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — three buttons enabled, awaiting input"
  on:
    - { widget: btnResume,   event: tap, do: [ ui.closePopup(), emit("pause.resumed") ],                  goto: closed }
    - { widget: btnSettings, event: tap, do: [ nav.gotoScene("settingsScene") ] }
    - { widget: btnQuit,     event: tap, do: [ ui.closePopup(), nav.gotoScene("mainMenuScene") ],         goto: closed }

- id: closed
  final: true
  description: "Popup closed; gameplay either resumed or unwound to main menu"
```

## acceptance

```yaml
- id: U-pausePopup-1
  given: "popup=pausePopup, mode=idle, parent=gameplayScene"
  when: "tap btnResume"
  then: "popup closes, pause.resumed event emitted, gameplayScene mode=default"
  test_hint: "UI E2E"

- id: U-pausePopup-2
  given: "popup=pausePopup, mode=idle"
  when: "tap btnSettings"
  then: "navigates to settingsScene with gameplayScene preserved beneath"
  test_hint: "UI E2E"

- id: U-pausePopup-3
  given: "popup=pausePopup, mode=idle"
  when: "tap btnQuit"
  then: "popup closes and navigates to mainMenuScene"
  test_hint: "UI E2E"

- id: U-pausePopup-4
  given: "popup=pausePopup, dismissible=false"
  when: "tap hitBackdrop"
  then: "no action — popup remains open"
  test_hint: "unit"
```

## notes

- `dismissible: false` is intentional. Players must commit to one of the three actions — preventing accidental tap-outside resumes during heated rounds.
- Settings action navigates to a full scene rather than opening a settings popup — matches the PRD which lists settings as a screen, not a popup.
- Returning from settings via `nav.back` restores the gameplayScene with its `paused` mode intact and this popup still open. (Engine-level guarantee; not modeled here.)
- Quit currently has no confirmation — if testing reveals accidental quits, wrap with [[popups/confirmPopup]] (not yet defined in this PRD batch).
