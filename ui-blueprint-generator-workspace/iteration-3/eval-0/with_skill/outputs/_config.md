---
domain: game
---

# Project: Match3Casual

## Bind namespaces

```yaml
namespaces:
  level: { source: LevelData,  scope: per-level config (loaded from JSON) }
  state: { source: LevelState, scope: per-session runtime }
  save:  { source: SaveData,   scope: persistent device storage (profile, settings, progress) }
  i18n:  { source: I18nKeys,   scope: localized strings }
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
  data.increment: { args: [path, by?] }
  noop:           { args: [] }
```

## Style tokens

```yaml
style: ./DESIGN.md#tokens
```

(Not yet authored — blueprints omit `style:` blocks. Downstream picks defaults.)

## Project widget types

```yaml
widgets:
  HeartRow:     { props: [bind] }
  BoosterBadge: { props: [icon, bind, count.bind] }
  StarRow:      { props: [bind, max] }
  Avatar:       { props: [bind, size] }
  Minimap:      { props: [bind, scale] }
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
