---
id: splashScene
type: scene
title: "Splash"
orientation: portrait
safeArea: true
parents: []
children: []
sources:
  - "PRD#screen-1-splash"
dataBindings:
  - state: LevelState
emits: [splash.bootComplete]
listens: [boot.assetsReady, boot.assetsFailed]
---

## purpose

App entry surface. Displays the brand mark and a progress indicator while bootstrap services (assets, save data, remote config) initialize. On success transitions to [[scenes/mainMenu]]; on failure shows a retry prompt.

## ui

```yaml
type: ZStack
children:
  - { id: imgBackground, type: Image, align: center,        asset: "splash.bg",   fit: cover,   width: fill, height: fill }
  - { id: imgLogo,       type: Image, align: center,        asset: "splash.logo", fit: contain, width: "60%sw", height: auto }

  - id: bottomBlock
    type: VStack
    align: bottom-center
    width: "80%sw"
    height: auto
    children:
      - { id: barBoot,    type: ProgressBar, bind: { value: "state.bootProgress" }, min: 0, max: 100 }
      - { id: lblStatus,  type: Text,        bind: { text: "i18n.splash.status" },  style: { text: token.caption } }
      - { id: btnRetry,   type: Button,      bind: { label: "i18n.splash.retry" },  visible: { bind: "$mode === \"failed\"" } }
```

## modes

```yaml
- id: loading
  initial: true
  description: "Bootstrap in progress; progress bar advancing"
  on:
    - { event: boot.assetsReady,  do: [ emit("splash.bootComplete"), nav.replace("mainMenu") ], goto: complete }
    - { event: boot.assetsFailed,                                                                goto: failed }

- id: failed
  description: "Bootstrap failed; retry button visible"
  on:
    - { widget: btnRetry, event: tap, do: [ service.call("BootService", "retry") ], goto: loading }

- id: complete
  final: true
  description: "Boot complete; navigation to main menu in flight"
```

## acceptance

```yaml
- id: U-splashScene-1
  given: "scene=splashScene, mode=loading"
  when: "boot.assetsReady event fires"
  then: "nav.replace to mainMenu, splash.bootComplete emitted, mode=complete"
  test_hint: "integration"

- id: U-splashScene-2
  given: "scene=splashScene, mode=loading"
  when: "boot.assetsFailed event fires"
  then: "btnRetry becomes visible, mode=failed"
  test_hint: "UI E2E"

- id: U-splashScene-3
  given: "scene=splashScene, mode=failed"
  when: "tap btnRetry"
  then: "BootService.retry called, mode=loading"
  test_hint: "UI E2E"
```

## notes

- Splash never receives back-navigation; `nav.replace` (not `nav.gotoScene`) ensures it cannot be returned to.
- `state.bootProgress` is exposed by the boot service as a 0-100 integer; renderer maps to ProgressBar fill.
- Branding visuals (logo size, animation) live in `DESIGN.md#splash`. Blueprint only declares structure.
