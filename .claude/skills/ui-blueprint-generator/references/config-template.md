# `_config.yaml` Template

Each project keeps one `ui-blueprints/_config.yaml` declaring its bind namespaces, action verbs, style tokens, and project-specific widget extensions. Loaded at the start of every blueprint generation session; subsequent blueprints conform to its declarations.

This file shows two canonical templates — game and mobile-app. Copy the closest match into the project, then adjust.

## Minimal structure

```yaml
domain: game | mobile | desktop
version: <semver>      # bump on breaking changes (verb removed, namespace renamed, etc.)
project: <name>

bindNamespaces:
  <namespace>: { source: <TypeName>, scope: <description> }
  ...

actionVerbs:
  <verb>: { args: [...], maps_to?: <impl-hint> }
  ...

styleTokens: ./DESIGN.md#tokens   # or inline tokens object

projectWidgets:                    # optional
  <WidgetName>: { props: [...] }
  ...

naming:                            # optional, overrides defaults in conventions.md
  screen_id_case: camelCase
  widget_id_case: camelCase
  acceptance_id_scheme: scoped     # or "sequential"

layout:                            # optional, overrides default file layout
  scenes: ui-blueprints/scenes/
  popups: ui-blueprints/popups/
  shared: ui-blueprints/shared/
```

---

## Canonical: game (Cocos2d / Unity / Godot)

```yaml
domain: game
version: 1.0.0
project: TileMatchPro

bindNamespaces:
  level: { source: LevelData,  scope: per-level config (loaded from JSON) }
  state: { source: LevelState, scope: per-session runtime }
  save:  { source: SaveData,   scope: persistent device storage }
  i18n:  { source: I18nKeys,   scope: localized strings }

actionVerbs:
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

styleTokens: ./DESIGN.md#tokens

projectWidgets:
  HeartRow:     { props: [bind] }
  BoosterBadge: { props: [icon, bind, count.bind] }
  Minimap:      { props: [bind, scale] }

naming:
  screen_id_case: camelCase
  widget_id_case: camelCase
  acceptance_id_scheme: scoped     # U-<screen>-<n>

layout:
  scenes: ui-blueprints/scenes/
  popups: ui-blueprints/popups/
  shared: ui-blueprints/shared/
```

---

## Canonical: mobile-app (React Native / SwiftUI / Flutter)

```yaml
domain: mobile
version: 1.0.0
project: SocialFeed

bindNamespaces:
  user:   { source: UserProfile,   scope: per-account }
  feed:   { source: FeedState,     scope: per-session feed cache }
  prefs:  { source: UserPrefs,     scope: device-local prefs }
  flags:  { source: FeatureFlags,  scope: remote-config flags }
  i18n:   { source: I18nKeys,      scope: localized strings }
  device: { source: DeviceInfo,    scope: platform/runtime }

actionVerbs:
  nav.push:      { args: [route, params?], maps_to: "router.push" }
  nav.replace:   { args: [route, params?], maps_to: "router.replace" }
  nav.back:      { args: [],                maps_to: "router.back" }
  ui.openSheet:  { args: [sheetId, data?] }
  ui.closeSheet: { args: [sheetId?] }
  ui.showToast:  { args: [textKey, durationMs?] }
  emit:          { args: [eventName, payload?] }
  api.call:      { args: [endpoint, method, body?] }
  data.set:      { args: [path, value] }
  noop:          { args: [] }

styleTokens: ./DESIGN.md#tokens

projectWidgets:
  Avatar:      { props: [bind, size] }
  Chip:        { props: [label, variant] }
  BottomSheet: { props: [bind.open, snapPoints] }
  SearchField: { props: [bind.value, placeholder] }

naming:
  screen_id_case: camelCase
  widget_id_case: camelCase
  acceptance_id_scheme: scoped

layout:
  scenes: ui-blueprints/screens/
  popups: ui-blueprints/sheets/
  shared: ui-blueprints/shared/
```

---

## Loading rules

1. `_config.yaml` is read at the start of every blueprint generation session.
2. The `bindNamespaces`, `actionVerbs`, and `projectWidgets` keys extend the universal vocabulary in `vocabulary.md` — blueprints may use any verb, namespace, or widget that is universal **or** declared here.
3. The `naming` key, if present, takes precedence over the defaults in `conventions.md`.
4. Changes to `_config.yaml` bump `version`. Blueprints may declare `configVersion` in `frontmatter`; mismatch is a validator error so stale blueprints surface explicitly.
5. Changes to `_config.yaml` should trigger re-validation of all blueprints in the project.
