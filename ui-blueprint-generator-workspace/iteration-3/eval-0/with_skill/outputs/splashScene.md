---
id: splashScene
type: scene
title: "Splash"
orientation: portrait
safeArea: false
parents: []
children: []
sources:
  - "PRD#screen-1"
dataBindings:
  - state: LevelState
  - i18n: I18nKeys
emits: [bootstrap.start]
listens: [bootstrap.ready, bootstrap.failed]
---

## purpose

App entry point. Displays the brand logo while the bootstrap pipeline (asset preload, save load, remote-config sync) runs. Auto-advances to [[scenes/mainMenuScene]] once `bootstrap.ready` fires, or shows a retry path on `bootstrap.failed`.

## ui

```yaml
type: ZStack
children:
  - id: bg
    type: Image
    align: center
    width: fill
    height: fill
    asset: img.splash.bg
    fit: cover

  - id: centerStack
    type: VStack
    align: center
    width: auto
    height: auto
    children:
      - { id: imgLogo,    type: Image, asset: img.brand.logo, width: "60%sw", height: auto, fit: contain }
      - { id: lblTagline, type: Text,  bind: { text: "i18n.splash.tagline" } }

  - id: footerStack
    type: VStack
    align: bottom-center
    width: fill
    height: auto
    children:
      - { id: barProgress, type: ProgressBar, bind: { value: "state.bootstrapProgress" }, min: 0, max: 100 }
      - { id: lblStatus,   type: Text,        bind: { text: "i18n.splash.loading" } }
      - { id: lblVersion,  type: Text,        bind: { text: "state.appVersion", fmt: "v{n}" } }
```

## modes

```yaml
- id: loading
  initial: true
  description: "Bootstrap running; progress bar updating"
  enter: { do: [ emit("bootstrap.start") ] }
  on:
    - { event: bootstrap.ready,  do: [ nav.gotoScene("mainMenuScene") ], goto: done }
    - { event: bootstrap.failed,                                          goto: error }

- id: error
  description: "Bootstrap failed; toast shown, will retry on tap"
  enter: { do: [ ui.showToast("i18n.splash.error", 3000) ] }
  on:
    - { event: bootstrap.ready, do: [ nav.gotoScene("mainMenuScene") ], goto: done }

- id: done
  final: true
  description: "Navigation handed off to mainMenuScene"
```

## acceptance

```yaml
- id: U-splashScene-1
  given: "app cold start, scene=splashScene, mode=loading"
  when: "bootstrap.ready event fires"
  then: "scene navigates to mainMenuScene, mode=done"
  test_hint: "UI E2E"

- id: U-splashScene-2
  given: "scene=splashScene, mode=loading"
  when: "bootstrap.failed event fires"
  then: "error toast displayed, mode=error"
  test_hint: "UI E2E"

- id: U-splashScene-3
  given: "state.bootstrapProgress = 50"
  when: "render barProgress"
  then: "progress bar shows half-filled"
  test_hint: "unit"
```

## notes

- Splash duration is bootstrap-driven, not timer-driven. A minimum on-screen time (typically 800ms) is an engine-level concern, not a blueprint concern.
- `safeArea: false` because the brand splash typically fills the full screen including notch/home-indicator area.
- Retry behavior on `bootstrap.failed` is intentionally simple — bootstrap service should be retrying internally; UI just shows a toast.
