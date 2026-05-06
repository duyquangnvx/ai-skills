---
id: settingsScene
type: scene
title: "Settings"
orientation: portrait
safeArea: true
parents: [mainMenuScene, pausePopup]
children: []
sources:
  - "PRD#screen-7"
dataBindings:
  - save: SaveData
  - i18n: I18nKeys
emits: [settings.changed]
listens: []
---

## purpose

Player-facing preferences. Three groups: audio (sound on/off, music on/off, volume sliders), language picker, and a footer with version + back. Persists via two-way `bind.value` against `save.settings.*`. Reachable from [[scenes/mainMenuScene]] and from [[popups/pausePopup]].

## ui

```yaml
type: VStack
children:
  - id: topBar
    type: ZStack
    height: "10%sh"
    children:
      - { id: btnBack,  type: IconButton, align: center-left, icon: chevron-left }
      - { id: lblTitle, type: Text,       align: center,      bind: { text: "i18n.settings.title" } }

  - id: scrollBody
    type: Scroll
    flex: 1
    axis: vertical
    children:
      - id: content
        type: VStack
        height: auto
        children:
          - id: groupAudio
            type: VStack
            height: auto
            children:
              - { id: lblAudioHeader, type: Text, bind: { text: "i18n.settings.audio" } }

              - id: rowSound
                type: HStack
                height: auto
                children:
                  - { id: lblSound, type: Text,   bind: { text: "i18n.settings.sound" }, flex: 1 }
                  - { id: tglSound, type: Toggle, bind: { value: "save.settings.soundOn" } }

              - id: rowSoundVolume
                type: HStack
                height: auto
                children:
                  - { id: lblSoundVolume, type: Text,   bind: { text: "i18n.settings.soundVolume" }, flex: 1 }
                  - { id: sldSoundVolume, type: Slider, bind: { value: "save.settings.soundVolume" }, min: 0, max: 100, step: 1, enabled: { bind: "save.settings.soundOn === true" } }

              - id: rowMusic
                type: HStack
                height: auto
                children:
                  - { id: lblMusic, type: Text,   bind: { text: "i18n.settings.music" }, flex: 1 }
                  - { id: tglMusic, type: Toggle, bind: { value: "save.settings.musicOn" } }

              - id: rowMusicVolume
                type: HStack
                height: auto
                children:
                  - { id: lblMusicVolume, type: Text,   bind: { text: "i18n.settings.musicVolume" }, flex: 1 }
                  - { id: sldMusicVolume, type: Slider, bind: { value: "save.settings.musicVolume" }, min: 0, max: 100, step: 1, enabled: { bind: "save.settings.musicOn === true" } }

          - id: groupLanguage
            type: VStack
            height: auto
            children:
              - { id: lblLanguageHeader, type: Text, bind: { text: "i18n.settings.language" } }

              - id: lstLanguages
                type: List
                bind: { items: "save.settings.availableLanguages" }
                itemTemplate:
                  type: HStack
                  height: auto
                  children:
                    - { id: lblLangName,  type: Text,       bind: { text: "item.displayName" }, flex: 1 }
                    - { id: btnLangPick,  type: IconButton, icon: check, visible: { bind: "item.code === save.settings.language" } }

          - id: groupAbout
            type: VStack
            height: auto
            children:
              - { id: lblAboutHeader, type: Text, bind: { text: "i18n.settings.about" } }
              - { id: lblVersion,     type: Text, bind: { text: "save.app.version", fmt: "v{n}" } }
```

## modes

```yaml
- id: editing
  initial: true
  description: "Default — settings interactive; toggles/sliders write through to save"
  on:
    - { widget: btnBack,      event: tap,    do: [ nav.back() ] }
    - { widget: tglSound,     event: change, do: [ data.set("save.settings.soundOn", "{value}"), emit("settings.changed", "soundOn") ] }
    - { widget: tglMusic,     event: change, do: [ data.set("save.settings.musicOn", "{value}"), emit("settings.changed", "musicOn") ] }
    - { widget: sldSoundVolume, event: change, do: [ data.set("save.settings.soundVolume", "{value}"), emit("settings.changed", "soundVolume") ] }
    - { widget: sldMusicVolume, event: change, do: [ data.set("save.settings.musicVolume", "{value}"), emit("settings.changed", "musicVolume") ] }
    - { widget: btnLangPick,  event: tap,    do: [ data.set("save.settings.language", "{item.code}"), emit("settings.changed", "language") ] }
```

## acceptance

```yaml
- id: U-settingsScene-1
  given: "scene=settingsScene, save.settings.soundOn = true"
  when: "tap tglSound"
  then: "save.settings.soundOn becomes false, settings.changed event emitted"
  test_hint: "UI E2E"

- id: U-settingsScene-2
  given: "scene=settingsScene, save.settings.soundOn = false"
  when: "render sldSoundVolume"
  then: "slider is disabled"
  test_hint: "unit"

- id: U-settingsScene-3
  given: "scene=settingsScene, an unselected language row"
  when: "tap btnLangPick on that row"
  then: "save.settings.language is updated to that row's item.code"
  test_hint: "UI E2E"

- id: U-settingsScene-4
  given: "scene=settingsScene"
  when: "tap btnBack"
  then: "scene unwinds via nav.back to whichever parent (mainMenuScene or pausePopup)"
  test_hint: "UI E2E"

- id: U-settingsScene-5
  given: "save.settings.language = 'en'"
  when: "render lstLanguages with the 'en' row"
  then: "the check icon is visible on that row only"
  test_hint: "unit"
```

## notes

- Sound and music toggles each have their own volume slider; volume is disabled when the matching toggle is off. PRD didn't specify volume — added because every match-3 settings screen has it. Drop sliders if PRD truly only wants on/off.
- Language is a list-pick rather than a dropdown to keep blueprints engine-agnostic — universal vocabulary doesn't include `Combobox`. If the project declares `Combobox` in `_config.md`, the list can be replaced.
- `nav.back` returns to whichever scene/popup pushed this one — works correctly whether parent is `mainMenuScene` or `pausePopup`.
- Settings persist through `data.set` which writes through to `save.settings.*`. Implementation should debounce slider writes if engine has perf concerns.
