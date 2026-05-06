# Confirm Quit Popup — UI Blueprint

## Overview
- **Component**: `ConfirmQuitPopup`
- **Type**: Modal / Popup dialog
- **Purpose**: Ask the user to confirm before quitting the application.
- **Units**: All measurements use density-independent pixels (`dp`).

## Hierarchy
```
ConfirmQuitPopup (root)
├── Backdrop                (full-screen overlay)
└── Panel                   (320 x 200 dp, centered)
    ├── TitleText           ("Quit?")
    ├── MessageText         ("Are you sure?")
    ├── CancelButton        (bottom-left)
    └── QuitButton          (bottom-right)
```

## Layout Specification

### 1. Root: `ConfirmQuitPopup`
| Property | Value |
|---|---|
| Width  | match parent (full screen) |
| Height | match parent (full screen) |
| Anchor | screen origin (0,0) |
| z-index | overlay layer (above all gameplay UI) |

### 2. `Backdrop`
| Property | Value |
|---|---|
| Width  | match parent |
| Height | match parent |
| Position | (0, 0) — covers full screen |
| Background | `#000000` at 50% opacity (semi-transparent black) |
| Interaction | Blocks input to underlying scene; tap is consumed (no dismiss) |

### 3. `Panel`
| Property | Value |
|---|---|
| Width  | 320 dp |
| Height | 200 dp |
| Anchor | screen center |
| Pivot  | (0.5, 0.5) — centered on its own origin |
| Position | center of screen, i.e. offset (0, 0) from parent center |
| Background | opaque panel surface (color per design tokens) |
| Children coordinate space | local — origin at panel top-left |

### 4. `TitleText` — "Quit?"
| Property | Value |
|---|---|
| Parent | `Panel` |
| Text   | `"Quit?"` |
| Anchor | top-center of panel |
| Pivot  | (0.5, 0.0) — horizontally centered, top-aligned |
| Position | x = panel center (160 dp from panel left), y = 24 dp from panel top |
| Alignment | horizontal center |

### 5. `MessageText` — "Are you sure?"
| Property | Value |
|---|---|
| Parent | `Panel` |
| Text   | `"Are you sure?"` |
| Anchor | top-center of panel |
| Pivot  | (0.5, 0.0) — horizontally centered, top-aligned |
| Position | x = panel center (160 dp from panel left), y = 60 dp from panel top |
| Alignment | horizontal center |

### 6. `CancelButton`
| Property | Value |
|---|---|
| Parent | `Panel` |
| Label  | `"Cancel"` |
| Anchor | bottom-left of panel |
| Pivot  | (0.0, 1.0) — left-aligned, bottom-aligned |
| Position | x = 16 dp from panel left edge, y = 16 dp from panel bottom edge |
| Action | dismiss popup, return to previous screen state |

### 7. `QuitButton`
| Property | Value |
|---|---|
| Parent | `Panel` |
| Label  | `"Quit"` |
| Anchor | bottom-right of panel |
| Pivot  | (1.0, 1.0) — right-aligned, bottom-aligned |
| Position | x = 16 dp from panel right edge, y = 16 dp from panel bottom edge |
| Action | confirm quit, exit / return to main menu |

## ASCII Layout Reference
```
+----------------------------------------------------+   <- full-screen Backdrop (50% black)
|                                                    |
|                                                    |
|         +------------------------------+           |
|         |          [ Quit? ]           |  <- 24dp from panel top
|         |                              |
|         |       Are you sure?          |  <- 60dp from panel top
|         |                              |
|         |                              |
|         |                              |
|         | [Cancel]            [Quit]   |  <- 16dp from bottom; 16dp inset L/R
|         +------------------------------+
|                  (320 x 200 dp)                     |
|                                                    |
+----------------------------------------------------+
```

## Notes
- The `Panel` is centered on the screen; all child coordinates are expressed
  relative to the panel's local coordinate space (origin at panel top-left).
- "24 dp from top" and "60 dp from top" are interpreted as the y-offset of
  each text element's top edge from the panel's top edge.
- Buttons use bottom-anchored pivots so the 16 dp inset is measured from
  the panel's bottom edge to the button's bottom edge (and similarly for
  the side insets).
- Backdrop captures all input below the panel to prevent stray taps from
  reaching the underlying scene.
