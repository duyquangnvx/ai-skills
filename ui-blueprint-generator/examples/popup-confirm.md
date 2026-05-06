---
id: confirmPopup
type: popup
title: "Confirm action"
modal: true
dismissible: true
parents: [pausePopup, settingsPopup, resultPopup]
sources:
  - "specs/ux/dialogs.md#confirmation"
dataBindings:
  - data: ConfirmDialogData
emits: [confirm.accepted, confirm.dismissed]
listens: []
---

## purpose

Reusable confirmation dialog. Accepts a title, body message, and labels for confirm/cancel buttons via popup data. Emits `confirm.accepted` or `confirm.dismissed` so callers don't need to track which popup answered — they listen on the bus and route by payload.

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
      - { id: lblTitle,   type: Text,   bind: { text: "data.title" },         style: { text: token.h2 } }
      - { id: lblMessage, type: Text,   bind: { text: "data.message" },       style: { text: token.body } }
      - { id: btnConfirm, type: Button, bind: { label: "data.confirmLabel" }, style: { variant: primary } }
      - { id: btnCancel,  type: Button, bind: { label: "data.cancelLabel" },  style: { variant: secondary } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — both buttons enabled, awaiting input"
  on:
    - widget: btnConfirm
      event: tap
      do:
        - ui.closePopup()
        - emit("confirm.accepted")
      goto: submitted
    - widget: btnCancel
      event: tap
      do:
        - ui.closePopup()
        - emit("confirm.dismissed")
    - widget: hitBackdrop
      event: tap
      do:
        - ui.closePopup()
        - emit("confirm.dismissed")

- id: submitted
  final: true
  description: "Confirm tapped; popup closing"
```

## acceptance

```yaml
- id: U-confirmPopup-1
  given: "popup=confirmPopup, mode=idle"
  when: "tap btnConfirm"
  then: "confirm.accepted event emitted, popup closes, mode=submitted"
  test_hint: "UI E2E"

- id: U-confirmPopup-2
  given: "popup=confirmPopup, dismissible=true"
  when: "tap hitBackdrop (outside panel)"
  then: "confirm.dismissed event emitted, popup closes"

- id: U-confirmPopup-3
  given: "popup=confirmPopup, mode=idle"
  when: "tap btnCancel"
  then: "confirm.dismissed event emitted, popup closes"

- id: U-confirmPopup-4
  given: "another popup is already open above this one"
  when: "render confirmPopup"
  then: "input behind this popup is blocked (modal=true) but the lower popup remains visible"
```

## notes

- The confirm/cancel labels are bound from `data.*` so callers control wording (e.g. "Quit" vs "Restart" vs "Delete"). Default labels live in i18n, not in this blueprint.
- `dismissible: true` means tap-outside (`hitBackdrop`) closes — back-button behavior is handled by the engine adapter per platform conventions.
- Animation contracts (panel scale-fade in/out, backdrop fade) live in `DESIGN.md#dialog-animations`.
- This popup intentionally has no internal pre-process flow — the caller handles work on `confirm.accepted`. Keeps it reusable.
- Buttons stack vertically because `panel` is a `VStack`. For side-by-side button layouts, replace `panel` with a `VStack` containing a header sub-area and an `HStack` button row, or use a `Custom: ButtonRow` widget.
