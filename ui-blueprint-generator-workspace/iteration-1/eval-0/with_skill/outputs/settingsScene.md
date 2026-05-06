---
id: settingsScene
type: scene
title: "Settings"
orientation: portrait
safeArea: true
parents: [mainMenuScene, pausePopup]
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - prefs: UserPrefs
  - i18n: I18nKeys
emits: [prefs.changed]
listens: []
---

## purpose

User preferences screen. Lets the player adjust sound effects volume, music volume, and language. Bindings write directly to `prefs.*` so changes are immediate; back navigation just returns to the previous scene/popup.

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.settings.title" }, style: { text: token.h2 } }

  - id: scrollArea
    type: Scroll
    axis: vertical
    flex: 1
    children:
      - id: content
        type: VStack
        width: fill
        height: auto
        children:
          - id: rowSound
            type: HStack
            height: auto
            children:
              - { id: lblSound,  type: Text,   bind: { text: "i18n.settings.sound" }, style: { text: token.body } }
              - { type: Spacer, flex: 1 }
              - { id: tglSound,  type: Toggle, bind: { value: "prefs.audio.soundEnabled" } }
              - { id: sldSound,  type: Slider, bind: { value: "prefs.audio.soundVolume" }, min: 0, max: 100, step: 1, enabled: { bind: "prefs.audio.soundEnabled === true" } }

          - id: rowMusic
            type: HStack
            height: auto
            children:
              - { id: lblMusic,  type: Text,   bind: { text: "i18n.settings.music" }, style: { text: token.body } }
              - { type: Spacer, flex: 1 }
              - { id: tglMusic,  type: Toggle, bind: { value: "prefs.audio.musicEnabled" } }
              - { id: sldMusic,  type: Slider, bind: { value: "prefs.audio.musicVolume" }, min: 0, max: 100, step: 1, enabled: { bind: "prefs.audio.musicEnabled === true" } }

          - id: rowLanguage
            type: HStack
            height: auto
            children:
              - { id: lblLanguage, type: Text, bind: { text: "i18n.settings.language" }, style: { text: token.body } }
              - { type: Spacer, flex: 1 }
              - { id: btnLanguage, type: Button, bind: { label: "prefs.language.displayName" }, style: { variant: secondary } }

          - id: rowVersion
            type: HStack
            height: auto
            children:
              - { id: lblVersionLabel, type: Text, bind: { text: "i18n.settings.version" }, style: { text: token.caption } }
              - { type: Spacer, flex: 1 }
              - { id: lblVersionValue, type: Text, bind: { text: "app.version" },           style: { text: token.caption } }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — toggles, sliders, and language picker live; values write through to prefs.*"
  on:
    - { widget: btnBack,     event: tap,    do: [ nav.back() ] }
    - { widget: tglSound,    event: change, do: [ data.set("prefs.audio.soundEnabled", "{value}"),  emit("prefs.changed", "soundEnabled") ] }
    - { widget: sldSound,    event: change, do: [ data.set("prefs.audio.soundVolume", "{value}"),   emit("prefs.changed", "soundVolume") ] }
    - { widget: tglMusic,    event: change, do: [ data.set("prefs.audio.musicEnabled", "{value}"),  emit("prefs.changed", "musicEnabled") ] }
    - { widget: sldMusic,    event: change, do: [ data.set("prefs.audio.musicVolume", "{value}"),   emit("prefs.changed", "musicVolume") ] }
    - { widget: btnLanguage, event: tap,                                                                                                  goto: pickingLanguage }

- id: pickingLanguage
  description: "Language picker open (engine-native picker / sheet); awaiting selection or cancel"
  enter: { do: [ service.call("LocaleService", "openPicker") ] }
  on:
    - { event: prefs.changed, where: "$mode === \"pickingLanguage\"", goto: idle }
```

## acceptance

```yaml
- id: U-settingsScene-1
  given: "scene=settingsScene, prefs.audio.soundEnabled=true"
  when: "tap tglSound"
  then: "prefs.audio.soundEnabled becomes false; sldSound is disabled"
  test_hint: "UI E2E"

- id: U-settingsScene-2
  given: "scene=settingsScene, prefs.audio.musicVolume=50"
  when: "drag sldMusic to 80"
  then: "prefs.audio.musicVolume=80; prefs.changed emitted with key=musicVolume"
  test_hint: "UI E2E"

- id: U-settingsScene-3
  given: "scene=settingsScene, prefs.language.displayName=\"English\""
  when: "render"
  then: "btnLanguage label shows 'English'"
  test_hint: "unit"

- id: U-settingsScene-4
  given: "scene=settingsScene, mode=idle"
  when: "tap btnLanguage"
  then: "mode=pickingLanguage, native locale picker opens"
  test_hint: "UI E2E"

- id: U-settingsScene-5
  given: "scene=settingsScene"
  when: "tap btnBack"
  then: "navigates back to caller (mainMenuScene or pausePopup parent scene)"
  test_hint: "UI E2E"
```

## notes

- Language picking is delegated to a `LocaleService` (engine-native locale list / OS picker). The blueprint stays engine-agnostic.
- Sound and music each have a toggle + slider so the player can fully mute or fine-tune. If the PRD intends single-toggle (no slider), simplify to just `Toggle`.
- Version row is inferred — useful in casual games for support / bug reports. Remove if product objects.
- Animation contracts (toggle thumb slide, slider feedback) live in `DESIGN.md#settings-animations`.
- Open question: should this be a popup overlay rather than a scene? PRD says "screen" so kept as scene; if engineering prefers an overlay (no scene swap from gameplay), promote to popup with `modal: true, dismissible: true`.
