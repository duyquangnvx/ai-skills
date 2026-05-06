---
domain: game
---

# Project: InventoryProject

## Bind namespaces

```yaml
namespaces:
  state: { source: GameState,    scope: per-session runtime }
  save:  { source: SaveData,     scope: persistent device storage }
  i18n:  { source: I18nKeys,     scope: localized strings }
```

## Action verbs

```yaml
verbs:
  nav.gotoScene:  { args: [sceneId, data?], maps_to: "Director.runScene" }
  nav.back:       { args: [],                maps_to: "Director.popScene" }
  ui.openPopup:   { args: [popupId, data?], maps_to: "PopupManager.open" }
  ui.closePopup:  { args: [popupId?],        maps_to: "PopupManager.close" }
  ui.showToast:   { args: [textKey, durationMs?] }
  emit:           { args: [eventName, payload?] }
  service.call:   { args: [serviceKey, method, args?] }
  data.set:       { args: [path, value] }
  noop:           { args: [] }
```

## Style tokens

```yaml
style: ./DESIGN.md#tokens
```

## Project widget types

```yaml
widgets: {}
```

## Naming

```yaml
naming:
  screen_id_case: camelCase
  widget_id_case: camelCase
  acceptance_id_scheme: scoped
```

## File layout

```yaml
layout:
  scenes:  ui-blueprints/scenes/
  popups:  ui-blueprints/popups/
  shared:  ui-blueprints/shared/
```
