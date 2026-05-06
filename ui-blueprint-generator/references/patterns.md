# UI Patterns — canonical recipes

Recipes for common UI patterns expressed in the blueprint vocabulary. Each recipe shows only the relevant fragments (frontmatter / `## ui` / `## modes` / `## acceptance`) — copy and adapt.

When in doubt about how to model something, check this file before reaching for `Custom`.

## 1. Form with field-level errors

A signup-style form: each field has its own error binding, the submit button is disabled while pending or while any required field is empty.

```yaml
type: VStack
padding: 16dp
children:
  - id: emailField
    type: Custom
    name: TextField
    bind: { value: "form.email" }
    props:
      errorText.bind: "form.errors.email"
      placeholder: "i18n.signup.emailPlaceholder"
  - id: passwordField
    type: Custom
    name: TextField
    bind: { value: "form.password" }
    props:
      errorText.bind: "form.errors.password"
      secure: true
  - id: btnSubmit
    type: Button
    bind: { label: "i18n.signup.submit" }
    enabled: { bind: "form.isValid === true && form.pending === false" }
    on:
      tap:
        - service.call("AuthService", "signup", "{form}")
```

`form.errors.<field>` is `null` when valid; `form.isValid` is a derived boolean exposed by the data source. Do NOT compute validity in boolean DSL — bind to a named field.

## 2. Multi-step wizard

Rule of thumb: ≤ 3 steps → model as N modes of a single screen. > 3 steps OR per-step different layout → N screens with shared frontmatter parents.

### Same-screen wizard (≤ 3 steps)

```yaml
- id: step1
  initial: true
  on:
    - widget: btnNext
      event: tap
      where: "wizard.step1Valid === true"
      goto: step2
- id: step2
  on:
    - widget: btnBack
      event: tap
      goto: step1
    - widget: btnNext
      event: tap
      where: "wizard.step2Valid === true"
      goto: step3
- id: step3
  final: true
  enter:
    do:
      - service.call("WizardService", "submit", "{wizard.data}")
```

`## ui` toggles step content via `visible: { bind: "$mode === \"step1\"" }`. `$mode` is a renderer-provided pseudo-namespace.

## 3. Paged list with cursor

Models loading / empty / end-of-list / retry as modes — no separate screens.

```yaml
- id: loading
  initial: true
  enter: { do: [ service.call("FeedService", "fetchPage", "{feed.cursor}") ] }
  on:
    - event: feed.pageLoaded
      goto: idle
    - event: feed.pageError
      goto: error
- id: idle
  on:
    - widget: lstFeed
      event: scrollToEnd
      where: "feed.hasMore === true"
      goto: loadingMore
- id: loadingMore
  on:
    - event: feed.pageLoaded
      goto: idle
    - event: feed.pageError
      goto: error
- id: empty
  description: "Reached after first page returns 0 items"
- id: error
  on:
    - widget: btnRetry
      event: tap
      goto: loading
```

`## ui` switches sub-regions on `$mode`. List binding stays `bind.items: feed.items` across modes.

## 4. Pull-to-refresh

```yaml
- id: lstFeed
  type: List
  bind: { items: "feed.items" }
  itemTemplate: { ... }
  on:
    pullToRefresh:
      - service.call("FeedService", "refresh")
      - emit("feed.refreshTriggered")
```

The renderer adapts to platform conventions (iOS rubber-band, Android material indicator). Acceptance asserts the event, not the gesture mechanics.

## 5. Tabs

Two valid models:

- **Mode-driven** (≤ 4 tabs, same data namespace): each tab is a mode, content sub-region toggles via `visible: { bind: "$mode === \"tabA\"" }`.
- **Sub-blueprint** (≥ 5 tabs, distinct data needs): each tab is a `type: scene` with its own frontmatter; a parent host scene includes a `Tabs` widget that switches via `nav.replace`.

Default to mode-driven unless tabs have very different data shapes.

## 6. Search field with debounced results

```yaml
- id: search
  initial: true
  on:
    - widget: searchField
      event: input
      do:
        - data.set("search.queryRaw", "{value}")
    - event: search.debouncedQueryChanged
      where: "search.queryRaw.length > 0"
      do:
        - service.call("SearchService", "query", "{search.queryRaw}")
      goto: searching
- id: searching
  on:
    - event: search.resultsLoaded
      goto: results
    - event: search.resultsLoaded
      where: "search.results.length === 0"
      goto: empty
- id: results
- id: empty
```

Debouncing is a service concern — `search.debouncedQueryChanged` is emitted by the search service after its debounce window. The blueprint declares the response, not the timing.

## 7. Empty / error / loading triad

For any screen that fetches data: model these as modes of the same screen, not separate screens.

```yaml
- id: loading
  initial: true
- id: ready
- id: empty
- id: error
  on:
    - widget: btnRetry
      event: tap
      goto: loading
```

Sub-regions in `## ui` toggle visibility on `$mode`. Acceptance covers all 4 reachable modes.

## 8. Inline banner / notification

A persistent banner inside a scene (e.g. "Your profile is incomplete"):

```yaml
- id: banner
  type: HStack
  visible: { bind: "user.profile.incomplete === true" }
  padding: 12dp
  children:
    - { id: lblBanner, type: Text, bind: { text: "i18n.profile.incomplete" }, flex: 1 }
    - { id: btnDismiss, type: IconButton, icon: x, on: { tap: [ data.set("user.prefs.bannerDismissed", true) ] } }
```

For ephemeral notifications use `type: popup, behavior: toast` instead.

## 9. Bottom sheet (drag handle, snap points)

```yaml
---
id: filterSheet
type: popup
behavior: sheet
snapPoints: [40%sh, 90%sh]
swipeToDismiss: true
modal: true
dismissible: true
parents: [feedScene]
---
```

`snapPoints` are heights the sheet rests at; `swipeToDismiss: true` allows drag-down to close. Blueprint declares the contract; renderer handles the gesture.

## 10. Toast / snackbar

```yaml
---
id: undoToast
type: popup
behavior: toast
autoDismissMs: 4000
modal: false
dismissible: true
parents: [feedScene]
emits: [toast.actionTapped]
---
```

Toast does not take input focus. `autoDismissMs` is the auto-close timer. If the toast has an action (Undo, Retry), declare it as a button in `## ui` and wire `tap → emit("toast.actionTapped") + ui.closePopup()`.
