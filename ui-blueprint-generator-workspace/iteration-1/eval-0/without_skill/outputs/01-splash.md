# Screen Blueprint: Splash

## Overview
- **Screen ID:** `splash`
- **Type:** Boot / Loading screen
- **Orientation:** Portrait (mobile)
- **Entry point:** App launch
- **Exit:** Auto-transition to Main Menu after assets load

## Purpose
Display branding, perform initial bootstrapping (asset preload, remote config fetch, save-data load) and route the player into the main menu when ready.

## Layout
- Full-screen background art (game key visual / brand color).
- Centered game logo (≈ 60% screen width, vertical position ~ 35% from top).
- Loading progress bar near bottom (vertical position ~ 80% from top), width ≈ 70% screen.
- Loading caption text under the bar ("Loading...", "Connecting...", "Preparing your candies...").
- Studio / publisher logo small at bottom edge.
- Optional version text in bottom-right corner (small, low opacity).

## Components
| Component        | Type        | Notes                                                |
|------------------|-------------|------------------------------------------------------|
| `bg_splash`      | Image       | Full-bleed background, looped subtle particle FX     |
| `logo_game`      | Image       | Game logo, fade-in + slight bounce on enter          |
| `progress_bar`   | Progress    | 0-100, animated fill                                 |
| `lbl_status`     | Text        | Dynamic status string                                |
| `logo_studio`    | Image       | Anchored bottom-center                               |
| `lbl_version`    | Text        | Anchored bottom-right                                |

## States
- **Loading:** Progress bar animates as bootstrap tasks complete.
- **Error (network/config fail):** Show retry popup overlay with "Retry" button.
- **Maintenance:** Replace progress bar with maintenance message and disabled retry.
- **Force update:** Replace caption with "Update required" + button to store.

## Interactions / Logic
- On enter: start preloading sequence (atlases, audio, level metadata, save data, remote config).
- Update `progress_bar` value as each phase completes.
- Update `lbl_status` per phase.
- On all tasks success: fade out and `Navigate(MainMenu)`.
- On failure: show error popup, allow retry.
- Minimum display time: 1.5s (so logo is visible even on fast loads).

## Audio
- One-shot stinger / logo sound on enter.
- No music yet (music starts on Main Menu).

## Analytics
- `splash_shown`
- `splash_load_complete` (with duration ms)
- `splash_load_failed` (with reason)

## Accessibility
- Respect reduced-motion: skip particle FX.
- High-contrast text for status caption.

## Defaults / Assumptions
- No login screen; player auto-signs into anonymous account in background.
- No tap-to-continue; screen auto-advances.
