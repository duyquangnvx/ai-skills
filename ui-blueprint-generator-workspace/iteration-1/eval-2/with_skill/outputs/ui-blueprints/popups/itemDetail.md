---
id: itemDetailPopup
type: popup
title: "Item detail"
modal: true
dismissible: true
parents: [inventoryScene]
sources:
  - "specs/gdd.md#inventory-screen"
dataBindings:
  - data: ItemDetailData
  - i18n: I18nKeys
emits: [itemDetail.closed]
listens: []
---

## purpose

Shows the description of an item the player tapped on [[scenes/inventory]]. Receives the item id via popup data; renders icon, name, quantity, and description text. Dismissible by tap-outside or close button.

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
      - id: header
        type: HStack
        height: auto
        children:
          - { id: imgIcon,  type: Image,       bind: { asset: "data.icon" }, fit: contain, width: "64dp", height: "64dp" }
          - { id: lblName,  type: Text,        bind: { text: "data.name" },  flex: 1,  style: { text: token.h2 } }
          - { id: btnClose, type: IconButton,  icon: x, width: "32dp", height: "32dp" }
      - { id: lblQuantity,    type: Text, bind: { text: "data.quantity" }, fmt: "x{n}", style: { text: token.caption } }
      - { id: lblDescription, type: Text, bind: { text: "data.description" }, style: { text: token.body } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Description visible, awaiting dismiss"
  on:
    - { widget: btnClose,    event: tap, do: [ ui.closePopup(), emit("itemDetail.closed") ], goto: closed }
    - { widget: hitBackdrop, event: tap, do: [ ui.closePopup(), emit("itemDetail.closed") ], goto: closed }

- id: closed
  final: true
  description: "Popup closing"
```

## acceptance

```yaml
- id: U-itemDetailPopup-1
  given: "popup=itemDetailPopup opened with data for a known item"
  when: "render panel"
  then: "icon, name, quantity (x{n}), and description are displayed"
  test_hint: "UI E2E"

- id: U-itemDetailPopup-2
  given: "popup=itemDetailPopup, mode=idle"
  when: "tap btnClose"
  then: "popup closes, itemDetail.closed emitted, mode=closed"
  test_hint: "UI E2E"

- id: U-itemDetailPopup-3
  given: "popup=itemDetailPopup, dismissible=true, mode=idle"
  when: "tap hitBackdrop (outside panel)"
  then: "popup closes, itemDetail.closed emitted, mode=closed"
  test_hint: "UI E2E"
```

## notes

- The GDD only specifies "description popup" — name, icon, and quantity are inferred as natural fields any item-detail surface needs. If the data contract differs, the bindings (`data.name`, `data.icon`, `data.quantity`, `data.description`) should be revised to match the resolved item record.
- Caller passes `{ itemId }` on open; the popup's data layer is expected to resolve `itemId` into the `data.*` fields shown here. Alternative: bind directly via `save.inventory.byId.<itemId>` — but indexed paths are forbidden by `conventions.md`, so a resolved `data` namespace is preferred.
- Dismiss animation contracts live in `DESIGN.md`.
