# Screen Blueprint: Main Menu

## Overview
- **Screen ID:** `main_menu`
- **Type:** Hub screen
- **Orientation:** Portrait
- **Entry from:** Splash, Settings (back), Profile (back), Level Select (back), Result popup (Home)
- **Exit to:** Level Select, Settings, Profile

## Purpose
Primary hub. Lets the player start playing, tweak settings, and view their profile. Surfaces soft currencies, daily rewards, and hooks for live-ops events.

## Layout
- Full-screen themed background with subtle parallax / animated candies.
- Top bar:
  - Coins indicator (icon + amount) top-right.
  - Lives indicator (heart icon + count) top-left.
  - Settings cog icon top-right corner (alternative entry point).
- Center stack:
  - Game logo (top-center, ~ 25% from top).
  - **Play** button (large, primary CTA, ~ 55% from top).
  - **Profile** button (medium, below Play).
  - **Settings** button (medium, below Profile).
- Bottom bar:
  - Daily reward icon / badge.
  - Shop icon (if monetization is enabled).
  - Social / leaderboard icon.
- Optional event banner above Play button (live-ops promo).

## Components
| Component         | Type      | Notes                                              |
|-------------------|-----------|----------------------------------------------------|
| `btn_play`        | Button    | Primary, pulse animation                           |
| `btn_profile`     | Button    | Secondary                                          |
| `btn_settings`    | Button    | Secondary                                          |
| `widget_coins`    | Widget    | Icon + count + "+" tap to open shop                |
| `widget_lives`    | Widget    | Icon + count + timer to next life                  |
| `banner_event`    | Widget    | Optional, hidden when no live event                |
| `btn_daily`       | Button    | Shows red dot if claim available                   |
| `lbl_logo`        | Image     | Animated logo                                      |

## States
- **Default:** All buttons enabled, currencies updated.
- **No lives:** Play button still enabled but warns when tapped (popup to refill).
- **Event active:** Event banner visible.
- **First-time user:** Tutorial pointer on Play button.

## Interactions / Logic
- `btn_play` tap → `Navigate(LevelSelect)` or directly to last unfinished level (configurable; default = LevelSelect).
- `btn_profile` tap → `Navigate(Profile)`.
- `btn_settings` tap → `Navigate(Settings)`.
- `widget_coins` tap → open Shop popup (if available).
- `widget_lives` tap → open Lives popup.
- `btn_daily` tap → open Daily Reward popup, claim if eligible.
- On enter: refresh currencies, refresh lives timer, check for unread notifications.

## Audio
- Background music: `bgm_main_menu` (loop).
- Button SFX: `sfx_button_tap`.

## Analytics
- `menu_shown`
- `menu_play_tapped`
- `menu_profile_tapped`
- `menu_settings_tapped`
- `menu_daily_tapped`

## Accessibility
- Buttons min 44pt tap target.
- Color-blind safe currency icons (shape + color).
- Localised labels.

## Defaults / Assumptions
- 3 buttons as PRD requires (Play, Profile, Settings) are mandatory; coins/lives/event/daily are optional but recommended.
- No login wall; profile is local until linked.
