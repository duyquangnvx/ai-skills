---
id: confirmPopup
type: popup
title: "Confirm action"
zIndex: 100
modal: true
dismissible: true
parents: [pausePopup, settingsPopup, resultPopup]
gdd:
  - "specs/ux/dialogs.md#confirmation"
dataBindings:
  - data: ConfirmDialogData
emits: [confirm.accepted, confirm.dismissed]
listens: []
---

## purpose

Reusable confirmation dialog. Accepts a title, body message, and labels for confirm/cancel buttons via popup data. Emits `confirm.accepted` or `confirm.dismissed` so callers don't need to track which popup answered — they listen on the bus and route by payload.

## layout

```yaml
root: { type: ZStack }
regions:
  - id: backdrop
    type: ZStack
    width: fill
    height: fill
  - id: panel
    type: VStack
    width: "80%sw"
    height: auto
    align: center
```

## widgets

```yaml
- id: hitBackdrop
  type: HitArea
  region: backdrop
  on:
    tap: [ ui.closePopup(), emit("confirm.dismissed") ]

- id: lblTitle
  type: Text
  region: panel
  bind: { text: "data.title" }
  style: { text: token.h2 }

- id: lblMessage
  type: Text
  region: panel
  bind: { text: "data.message" }
  style: { text: token.body }

- id: btnConfirm
  type: Button
  region: panel
  bind: { label: "data.confirmLabel" }
  style: { variant: primary }
  on:
    tap: [ ui.closePopup(), emit("confirm.accepted") ]

- id: btnCancel
  type: Button
  region: panel
  bind: { label: "data.cancelLabel" }
  style: { variant: secondary }
  on:
    tap: [ ui.closePopup(), emit("confirm.dismissed") ]
```

## states

```yaml
states:
  - id: idle
    description: "Default — both buttons enabled, awaiting input"
    initial: true
  - id: submitted
    description: "Confirm tapped; brief disabled-state until popup closes"
    final: true
```

## actions

```yaml
- on: { widget: btnConfirm, event: tap }
  do: [ state.set("submitted") ]
```

## animations

```yaml
- id: enter
  trigger: "scene.appear"
  spec: "backdrop fade in 150ms; panel scale 0.9 → 1.0 + fade"
  duration: 200ms
  blocksInput: true

- id: exit
  trigger: "scene.disappear"
  spec: "panel scale 1.0 → 0.95 + fade; backdrop fade out"
  duration: 150ms
  blocksInput: true
```

## acceptance

```yaml
- id: U1
  given: "popup=confirmPopup, $state=idle"
  when: "tap btnConfirm"
  then: "confirm.accepted event emitted, popup closes"
  test_hint: "UI E2E"

- id: U2
  given: "popup=confirmPopup, dismissible=true"
  when: "tap hitBackdrop (outside panel)"
  then: "confirm.dismissed event emitted, popup closes"

- id: U3
  given: "popup=confirmPopup, $state=idle"
  when: "tap btnCancel"
  then: "confirm.dismissed event emitted, popup closes"

- id: U4
  given: "another popup is already open above this one"
  when: "render confirmPopup"
  then: "input behind this popup is blocked (modal=true) but the lower popup remains visible"
```

## notes

- Buttons stack vertically because the `panel` region is a `VStack`. For side-by-side button layouts, replace `panel` with a `VStack` containing a header sub-area and a buttons sub-area — or use a `Custom: ButtonRow` widget. Sub-regions are not supported in the universal format; project may extend.
- The confirm/cancel labels are bound from `data.*` so callers control wording (e.g. "Quit" vs "Restart" vs "Delete"). Default labels live in i18n, not in this blueprint.
- `dismissible: true` means tap-outside (`hitBackdrop`) closes — but back-button behavior is handled by the engine adapter per platform conventions.
- This popup intentionally has no internal state machine for confirm-and-process flows — the caller handles processing on `confirm.accepted`. Keeps this popup reusable.
