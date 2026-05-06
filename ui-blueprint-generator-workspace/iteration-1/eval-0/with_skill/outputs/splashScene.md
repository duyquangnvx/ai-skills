---
id: splashScene
type: scene
title: "Splash"
orientation: portrait
safeArea: true
parents: []
children: []
sources:
  - "PRD.md#screens"
dataBindings:
  - app: AppState
  - i18n: I18nKeys
emits: [app.bootComplete]
listens: [app.bootProgress, app.bootError]
---

## purpose

App entry point. Shows the brand logo and a load-progress indicator while the engine warms up (asset preload, save migration, remote config). Auto-advances to [[scenes/mainMenuScene]] on `app.bootComplete`. Surfaces a retry path on boot error.

## ui

```yaml
type: ZStack
children:
  - id: bgLogo
    type: Image
    align: center
    asset: brand.logo
    fit: contain
    width: "60%sw"
    height: auto

  - id: footer
    type: VStack
    align: bottom-center
    width: fill
    height: auto
    children:
      - { id: barProgress, type: ProgressBar, bind: { value: "app.bootProgress" }, min: 0, max: 100 }
      - { id: lblStatus,   type: Text,        bind: { text: "i18n.splash.status" },  style: { text: token.caption } }
      - { id: lblVersion,  type: Text,        bind: { text: "app.version" },         style: { text: token.caption } }

  - id: errorPanel
    type: VStack
    align: center
    width: "80%sw"
    height: auto
    visible: { bind: "$mode === \"error\"" }
    children:
      - { id: lblErrorTitle, type: Text,   bind: { text: "i18n.splash.errorTitle" }, style: { text: token.h2 } }
      - { id: lblErrorBody,  type: Text,   bind: { text: "i18n.splash.errorBody" },  style: { text: token.body } }
      - { id: btnRetry,      type: Button, bind: { label: "i18n.common.retry" },     style: { variant: primary } }
```

## modes

```yaml
- id: booting
  initial: true
  description: "Boot sequence in progress; progress bar visible"
  enter: { do: [ service.call("BootService", "start") ] }
  on:
    - { event: app.bootComplete,                                                 goto: ready }
    - { event: app.bootError,                                                    goto: error }

- id: ready
  description: "Boot complete; immediately route to main menu"
  enter: { do: [ nav.replace("mainMenuScene") ] }
  final: true

- id: error
  description: "Boot failed; user can retry"
  on:
    - { widget: btnRetry, event: tap, do: [ service.call("BootService", "start") ], goto: booting }
```

## acceptance

```yaml
- id: U-splashScene-1
  given: "scene=splashScene, mode=booting, app.bootProgress=42"
  when: "render"
  then: "barProgress shows 42% filled"
  test_hint: "unit"

- id: U-splashScene-2
  given: "scene=splashScene, mode=booting"
  when: "app.bootComplete event received"
  then: "scene transitions to mainMenuScene via nav.replace"
  test_hint: "UI E2E"

- id: U-splashScene-3
  given: "scene=splashScene, mode=booting"
  when: "app.bootError event received"
  then: "mode=error, errorPanel visible, btnRetry enabled"
  test_hint: "UI E2E"

- id: U-splashScene-4
  given: "scene=splashScene, mode=error"
  when: "tap btnRetry"
  then: "BootService.start invoked, mode=booting"
  test_hint: "UI E2E"
```

## notes

- Splash has no `parents` — it is the app root, launched by the engine.
- Use `nav.replace` (not `nav.gotoScene`) so the splash is removed from the navigation stack.
- Animation contracts (logo fade-in, progress bar transitions) live in `DESIGN.md#splash-animations`.
- Open question: should there be a minimum dwell time so the splash doesn't flash on a fast device? Surface to design.
