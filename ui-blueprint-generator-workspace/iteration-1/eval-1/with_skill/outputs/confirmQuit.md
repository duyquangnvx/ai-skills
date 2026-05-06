---
id: confirmQuit
type: popup
title: "Confirm quit"
modal: true
dismissible: false
parents: []
sources:
  - "designer-spec#confirm-quit-popup"
dataBindings: []
emits: [quit.accepted, quit.dismissed]
listens: []
---

## purpose

Modal confirmation popup that asks the user to confirm quitting before destructive navigation. Renders a centered fixed-size panel over a full-screen scrim; surfaces a `Cancel` action that returns control to the caller and a `Quit` action that emits the accepted event so the caller can perform the actual quit.

## ui

```yaml
type: ZStack
children:
  - id: backdrop
    type: HitArea
    align: center
    width: fill
    height: fill
    style: { color: token.scrim }

  - id: panel
    type: ZStack
    align: center
    width: 320dp
    height: 200dp
    style: { color: token.bg }
    children:
      - id: lblTitle
        type: Text
        align: top-center
        offset: { x: 0dp, y: 24dp }
        bind: { text: "i18n.confirmQuit.title" }
        style: { text: token.h2 }

      - id: lblMessage
        type: Text
        align: top-center
        offset: { x: 0dp, y: 60dp }
        bind: { text: "i18n.confirmQuit.message" }
        style: { text: token.body }

      - id: btnCancel
        type: Button
        align: bottom-left
        offset: { x: 16dp, y: -16dp }
        bind: { label: "i18n.confirmQuit.cancel" }
        style: { variant: secondary }

      - id: btnQuit
        type: Button
        align: bottom-right
        offset: { x: -16dp, y: -16dp }
        bind: { label: "i18n.confirmQuit.quit" }
        style: { variant: primary }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — both buttons enabled, awaiting input"
  on:
    - { widget: btnQuit,   event: tap, do: [ ui.closePopup(), emit("quit.accepted") ],   goto: submitted }
    - { widget: btnCancel, event: tap, do: [ ui.closePopup(), emit("quit.dismissed") ] }

- id: submitted
  final: true
  description: "Quit confirmed; popup closing and caller will perform the actual quit"
```

## acceptance

```yaml
- id: U-confirmQuit-1
  given: "popup=confirmQuit, mode=idle"
  when: "tap btnQuit"
  then: "quit.accepted event emitted, popup closes, mode=submitted"
  test_hint: "UI E2E"

- id: U-confirmQuit-2
  given: "popup=confirmQuit, mode=idle"
  when: "tap btnCancel"
  then: "quit.dismissed event emitted, popup closes, caller resumes"
  test_hint: "UI E2E"

- id: U-confirmQuit-3
  given: "popup=confirmQuit, dismissible=false"
  when: "tap backdrop (outside panel)"
  then: "no event emitted, popup remains open"
  test_hint: "UI E2E"

- id: U-confirmQuit-4
  given: "popup=confirmQuit is rendered"
  when: "input is dispatched at any point on screen"
  then: "input behind the panel is blocked (modal=true); only popup widgets receive events"
  test_hint: "integration"
```

## notes

- Panel size is fixed at `320dp x 200dp` per designer spec; centered via `ZStack align: center` on the root layer.
- Inside the panel, each label/button is anchored to a corner of the panel via `align` + `offset` — this preserves the designer's pixel-precise placement (24dp top inset for title, 60dp top inset for message, 16dp insets for the bottom buttons) without resorting to absolute positioning. Negative `y` on the bottom-aligned buttons reads as "16dp inward from the bottom edge."
- `dismissible: false` because quitting is destructive — backdrop taps must not silently dismiss. Back-button behavior is delegated to the engine adapter (typically mapped to `btnCancel`).
- Backdrop colour token (`token.scrim`) resolves to a semi-transparent black in `DESIGN.md`; the exact alpha is a design concern, not a blueprint concern.
- Final string content (`Quit?`, `Are you sure?`, `Cancel`, `Quit`) lives behind `i18n.confirmQuit.*` keys — this blueprint does not hard-code the natural-language copy.
- Animation contracts (panel scale-fade in/out, backdrop fade) live in `DESIGN.md#dialog-animations`.
- Open question: should this popup accept caller-provided labels via `data.*` (like the generic [[popups/confirmPopup]] pattern)? Current draft is a dedicated single-purpose popup; promote to a generic `confirmPopup` if a second confirmation site appears.
