---
id: confirmQuit
type: popup
title: "Confirm quit"
modal: true
dismissible: false
parents: []
sources:
  - "specs/ux/dialogs.md#confirm-quit"
emits: [quit.confirmed, quit.cancelled]
listens: []
---

## purpose

Modal popup that asks the user to confirm before quitting. Presents a centered panel over a dimmed backdrop with a title, a short message, and two actions (Cancel, Quit). Emits `quit.confirmed` or `quit.cancelled` so the caller can decide what to do next without coupling to this popup.

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
    type: VStack
    align: center
    width: 320dp
    height: 200dp
    style: { color: token.surface }
    children:
      - { type: Spacer, height: 24dp }
      - id: lblTitle
        type: Text
        width: fill
        height: auto
        align: center
        bind: { text: "i18n.popup.confirmQuit.title" }
        style: { text: token.h2 }
      - { type: Spacer, flex: 1 }
      - id: lblMessage
        type: Text
        width: fill
        height: auto
        align: center
        bind: { text: "i18n.popup.confirmQuit.message" }
        style: { text: token.body }
      - { type: Spacer, flex: 1 }
      - id: footer
        type: HStack
        width: fill
        height: auto
        children:
          - { type: Spacer, width: 16dp }
          - id: btnCancel
            type: Button
            width: auto
            height: auto
            bind: { label: "i18n.popup.confirmQuit.cancel" }
            style: { variant: secondary }
          - { type: Spacer, flex: 1 }
          - id: btnQuit
            type: Button
            width: auto
            height: auto
            bind: { label: "i18n.popup.confirmQuit.quit" }
            style: { variant: primary }
          - { type: Spacer, width: 16dp }
      - { type: Spacer, height: 16dp }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Awaiting user choice — both buttons enabled."
  on:
    - { widget: btnCancel, event: tap, do: [ ui.closePopup(), emit("quit.cancelled") ], goto: closed }
    - { widget: btnQuit,   event: tap, do: [ ui.closePopup(), emit("quit.confirmed") ], goto: closed }

- id: closed
  final: true
  description: "User answered; popup closing."
```

## acceptance

```yaml
- id: U-confirmQuit-1
  given: "popup=confirmQuit, mode=idle"
  when: "tap btnQuit"
  then: "quit.confirmed event emitted, popup closes, mode=closed"
  test_hint: "UI E2E"

- id: U-confirmQuit-2
  given: "popup=confirmQuit, mode=idle"
  when: "tap btnCancel"
  then: "quit.cancelled event emitted, popup closes, mode=closed"
  test_hint: "UI E2E"

- id: U-confirmQuit-3
  given: "popup=confirmQuit is rendered"
  when: "tap backdrop"
  then: "popup remains open and no event is emitted (dismissible=false)"
  test_hint: "UI E2E"

- id: U-confirmQuit-4
  given: "popup=confirmQuit is rendered"
  when: "render"
  then: "panel is 320dp x 200dp and centered on screen; backdrop fills the screen and blocks input behind"
  test_hint: "UI E2E"
```

## notes

- Layout follows the designer's spacing spec without absolute positioning: a `VStack` inside the panel uses fixed-height `Spacer`s for the 24dp top inset and 16dp bottom inset, and `flex: 1` `Spacer`s to push the message to the visual center while keeping the title at the top and the footer at the bottom. The title sits 24dp from the top of the panel; the footer row sits 16dp from the bottom. The exact "message at 60dp from top" from the spec is approximated by the elastic centering: with title height ~24-32dp and the upper 24dp gap, the message lands near the vertical center as drawn — if pixel parity matters, replace the upper `Spacer flex: 1` with a fixed-height `Spacer` once final type metrics are locked in `DESIGN.md`.
- The footer is an `HStack` with `Spacer width: 16dp` on each end (left/right insets) and a `flex: 1` `Spacer` between the two buttons, so Cancel hugs the bottom-left and Quit hugs the bottom-right at exactly 16dp from each edge regardless of label width.
- `dismissible: false` because quitting is destructive — taps on `backdrop` are absorbed by the `HitArea` but do not close the popup. Back-button behavior is engine/platform-specific; the engine adapter should route it to `btnCancel.tap` to keep parity.
- The backdrop color (`token.scrim`) and panel color (`token.surface`) are referenced by token only; concrete RGBA / opacity values live in `DESIGN.md`.
- Title and message text bind to `i18n.popup.confirmQuit.*`. The literal "Quit?" / "Are you sure?" strings from the brief are localizable copy, not part of the blueprint.
- Open question: should pressing the platform back button equal Cancel or be ignored? Defaulting to Cancel here; flag for designer review.
