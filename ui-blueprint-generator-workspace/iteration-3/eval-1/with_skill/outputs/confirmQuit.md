---
id: confirmQuit
type: popup
title: "Confirm quit"
modal: true
dismissible: true
parents: []
sources:
  - "designer-spec#confirm-quit-popup"
emits: [quit.accepted, quit.dismissed]
listens: []
---

## purpose

Modal confirmation dialog shown before the user exits. Asks "Are you sure?" and offers Cancel / Quit. Emits `quit.accepted` so the caller routes the actual exit; emits `quit.dismissed` on Cancel or backdrop tap so the caller knows the user opted to stay.

## ui

```yaml
type: ZStack
children:
  - id: hitBackdrop
    type: HitArea
    align: center
    width: fill
    height: fill

  - id: panel
    type: VStack
    align: center
    width: 320dp
    height: 200dp
    children:
      - { type: Spacer, height: 24dp }
      - { id: lblTitle, type: Text, bind: { text: "i18n.confirmQuit.title" }, align: center, style: { text: token.h2 } }

      - { type: Spacer, flex: 1 }
      - { id: lblMessage, type: Text, bind: { text: "i18n.confirmQuit.message" }, align: center, style: { text: token.body } }
      - { type: Spacer, flex: 1 }

      - id: buttonRow
        type: HStack
        width: fill
        height: auto
        children:
          - { type: Spacer, width: 16dp }
          - { id: btnCancel, type: Button, bind: { label: "i18n.confirmQuit.cancel" }, style: { variant: secondary } }
          - { type: Spacer, flex: 1 }
          - { id: btnQuit, type: Button, bind: { label: "i18n.confirmQuit.quit" }, style: { variant: primary } }
          - { type: Spacer, width: 16dp }

      - { type: Spacer, height: 16dp }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — both buttons enabled, awaiting input"
  on:
    - { widget: btnQuit,     event: tap, do: [ ui.closePopup(), emit("quit.accepted") ],  goto: submitted }
    - { widget: btnCancel,   event: tap, do: [ ui.closePopup(), emit("quit.dismissed") ] }
    - { widget: hitBackdrop, event: tap, do: [ ui.closePopup(), emit("quit.dismissed") ] }

- id: submitted
  final: true
  description: "Quit confirmed; popup closing, caller proceeds with exit"
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
  then: "quit.dismissed event emitted, popup closes, no quit.accepted fired"
  test_hint: "UI E2E"

- id: U-confirmQuit-3
  given: "popup=confirmQuit, dismissible=true"
  when: "tap hitBackdrop (outside panel)"
  then: "quit.dismissed event emitted, popup closes"
  test_hint: "UI E2E"

- id: U-confirmQuit-4
  given: "popup=confirmQuit rendered over an existing scene"
  when: "user taps any element behind the backdrop"
  then: "input is blocked by modal=true; only popup widgets receive input"
  test_hint: "integration"
```

## notes

- The designer's spec gives pixel-precise positions (title 24dp from top, message 60dp from top, buttons 16dp from each panel edge). The blueprint expresses these as stack + `Spacer` constraints, not absolute coordinates. The exact title→message gap that produces "message at 60dp from top" is a function of `token.h2` line height and lives in `DESIGN.md` — downstream visual design tunes the inner Spacers (`flex: 1` between title and message) into fixed dp values if pixel parity is required.
- Panel is fixed `320dp × 200dp` per the designer spec. Centered via the `ZStack` root with `align: center`. If a future variant needs to grow with content, switch panel `height` to `auto` and re-anchor button row distances; the sizing is intentionally explicit here because the spec called it out.
- Cancel is `secondary` variant, Quit is `primary` — matches "primary action lives on the right" convention. If the project's convention is destructive-action-on-the-left, swap variants in `DESIGN.md`, not here.
- Title/message/button labels bind to `i18n.confirmQuit.*`. The exact strings ("Quit?", "Are you sure?", "Cancel", "Quit") are owned by the i18n catalog.
- Animation contracts (backdrop fade-in, panel scale-in/out) belong in `DESIGN.md#dialog-animations`. The blueprint only declares mode transitions.
- `parents` is empty pending an upstream spec specifying which scenes can open this popup. Add the parent screen ids when those blueprints are written.
