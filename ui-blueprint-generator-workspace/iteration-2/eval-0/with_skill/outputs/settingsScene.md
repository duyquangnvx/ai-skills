---
id: settingsScene
type: scene
title: "Settings"
orientation: portrait
safeArea: true
parents: [mainMenu, pausePopup]
children: []
sources:
  - "PRD#screen-7-settings"
dataBindings:
  - prefs: UserPrefs
emits: [settings.changed]
listens: []
---

## purpose

User preferences screen. Lets the player adjust sound effects, background music, and language. Reads and writes the `prefs.*` namespace; emits `settings.changed` so audio/i18n services pick up updates immediately. Returns to caller via `nav.back()` (works from both [[scenes/mainMenu]] and [[popups/pausePopup]]).

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

  - id: content
    type: VStack
    flex: 1
    children:
      - id: rowSound
        type: HStack
        height: 64dp
        children:
          - { id: lblSound, type: Text, flex: 1, bind: { text: "i18n.settings.sound" }, style: { text: token.body } }
          - id: tglSound
            type: Toggle
            bind: { value: "prefs.sound.enabled" }
            on:
              change: [ data.set("prefs.sound.enabled", "{value}"), emit("settings.changed", "sound") ]

      - id: rowSoundVolume
        type: HStack
        height: 56dp
        children:
          - { id: lblSoundVol, type: Text, flex: 1, bind: { text: "i18n.settings.soundVolume" }, style: { text: token.caption } }
          - id: sldSound
            type: Slider
            bind: { value: "prefs.sound.volume" }
            min: 0
            max: 100
            step: 1
            enabled: { bind: "prefs.sound.enabled === true" }
            on:
              change: [ data.set("prefs.sound.volume", "{value}"), emit("settings.changed", "soundVolume") ]

      - id: rowMusic
        type: HStack
        height: 64dp
        children:
          - { id: lblMusic, type: Text, flex: 1, bind: { text: "i18n.settings.music" }, style: { text: token.body } }
          - id: tglMusic
            type: Toggle
            bind: { value: "prefs.music.enabled" }
            on:
              change: [ data.set("prefs.music.enabled", "{value}"), emit("settings.changed", "music") ]

      - id: rowMusicVolume
        type: HStack
        height: 56dp
        children:
          - { id: lblMusicVol, type: Text, flex: 1, bind: { text: "i18n.settings.musicVolume" }, style: { text: token.caption } }
          - id: sldMusic
            type: Slider
            bind: { value: "prefs.music.volume" }
            min: 0
            max: 100
            step: 1
            enabled: { bind: "prefs.music.enabled === true" }
            on:
              change: [ data.set("prefs.music.volume", "{value}"), emit("settings.changed", "musicVolume") ]

      - id: rowLanguage
        type: HStack
        height: 64dp
        children:
          - { id: lblLanguage, type: Text, flex: 1, bind: { text: "i18n.settings.language" }, style: { text: token.body } }
          - id: btnLanguage
            type: Button
            bind: { label: "prefs.language.displayName" }
            style: { variant: secondary }

      - { type: Spacer, flex: 1 }
```

## modes

```yaml
- id: idle
  initial: true
  description: "Default — settings editable"
  on:
    - { widget: btnBack,     event: tap, do: [ nav.back() ] }
    - { widget: btnLanguage, event: tap, do: [ ui.openPopup("languagePopup") ] }
```

## acceptance

```yaml
- id: U-settingsScene-1
  given: "scene=settingsScene, prefs.sound.enabled===true"
  when: "tap tglSound"
  then: "prefs.sound.enabled is set to false, settings.changed emitted with payload \"sound\""
  test_hint: "UI E2E"

- id: U-settingsScene-2
  given: "scene=settingsScene, prefs.music.enabled===false"
  when: "render rowMusicVolume"
  then: "sldMusic is disabled"
  test_hint: "unit"

- id: U-settingsScene-3
  given: "scene=settingsScene, mode=idle"
  when: "tap btnBack"
  then: "navigates back to caller (mainMenu or pausePopup parent)"
  test_hint: "UI E2E"

- id: U-settingsScene-4
  given: "scene=settingsScene, prefs.sound.volume===50"
  when: "drag sldSound to 80"
  then: "prefs.sound.volume is set to 80, settings.changed emitted with payload \"soundVolume\""
  test_hint: "UI E2E"

- id: U-settingsScene-5
  given: "scene=settingsScene, mode=idle"
  when: "tap btnLanguage"
  then: "languagePopup opens"
  test_hint: "UI E2E"
```

## notes

- A `languagePopup` (list of available locales) is referenced as a child opened from `btnLanguage`. It is NOT specified in this PRD batch — flagged as an open dependency. Either add a separate blueprint for it, or replace `ui.openPopup` with a navigation to a dedicated language scene.
- Sound and music volume sliders are gated by their enable toggles — disabled when the toggle is off.
- `data.set` plus `emit("settings.changed", ...)` is the canonical write pattern; the audio service listens on the bus and re-applies volume/mute without polling.
