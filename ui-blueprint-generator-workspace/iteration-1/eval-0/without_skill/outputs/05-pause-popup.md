# Popup Blueprint: Pause

## Overview
- **Popup ID:** `popup_pause`
- **Type:** Modal overlay
- **Parent screen:** Gameplay
- **Trigger:** Pause button on Gameplay HUD
- **Dismiss to:** Gameplay (Resume), Settings (overlay), Main Menu (Quit, with confirm)

## Purpose
Pause the active level, allow the player to resume, tweak settings, or abandon the level.

## Layout
- Full-screen dim overlay (black, ~60% alpha) behind the popup.
- Centered card panel:
  - Title "Paused" at top.
  - Vertical button stack:
    - **Resume** (primary, large)
    - **Settings**
    - **Quit**
  - Optional: small "How to play" link at bottom.
- Close (X) icon top-right of card → same as Resume.

## Components
| Component        | Type      | Notes                                            |
|------------------|-----------|--------------------------------------------------|
| `bg_dim`         | Overlay   | Tappable? No (force button choice)               |
| `card_pause`     | Panel     | Slide-down or scale-in                           |
| `lbl_title`      | Text      | "Paused"                                         |
| `btn_resume`     | Button    | Primary CTA                                      |
| `btn_settings`   | Button    | Opens Settings as overlay (preserves game state) |
| `btn_quit`       | Button    | Confirms before quitting                         |
| `btn_close`      | Button    | Equivalent to Resume                             |

## States
- **Default:** Buttons enabled.
- **Confirm-quit:** After tapping Quit, swap card content to "Are you sure? You will lose this attempt." with `Yes` / `No` buttons.

## Interactions / Logic
- On open: pause game timers, mute or duck BGM (configurable), disable board input.
- `btn_resume` → close popup, resume timers, restore audio.
- `btn_settings` → open Settings as a sub-overlay (do NOT navigate away from gameplay).
  - When Settings closes, return to Pause popup.
- `btn_quit` → show confirm view.
  - `Yes` → consume a life (configurable), `Navigate(LevelSelect)`.
  - `No` → return to default Pause view.
- `btn_close` → same as `btn_resume`.
- Hardware back / swipe-back → same as `btn_resume`.

## Audio
- SFX: `sfx_popup_open`, `sfx_popup_close`, `sfx_button_tap`.
- BGM: ducked while paused.

## Analytics
- `pause_resumed`
- `pause_quit_confirmed`
- `pause_settings_opened`

## Accessibility
- Focus trap within popup.
- ESC / hardware back closes (resume).
- Buttons localised.

## Defaults / Assumptions
- Quitting a level in-progress costs 1 life by default (configurable).
- Settings opened from Pause is a lightweight overlay; full Settings screen reused.
