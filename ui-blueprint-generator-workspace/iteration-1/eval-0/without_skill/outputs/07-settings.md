# Screen Blueprint: Settings

## Overview
- **Screen ID:** `settings`
- **Type:** Configuration screen (also reusable as overlay from Pause popup)
- **Orientation:** Portrait
- **Entry from:** Main Menu, Pause popup
- **Exit to:** Caller (Main Menu or Pause popup)

## Purpose
Let the player toggle audio, change language, manage account, and view legal/support information.

## Layout
- Top bar:
  - Back button (left).
  - Title "Settings" (center).
- Scrollable content (vertical list of grouped rows):
  - **Audio**
    - Sound effects: toggle + slider.
    - Music: toggle + slider.
  - **Language**
    - Row with current language; tap → language picker popup.
  - **Notifications** (optional)
    - Toggle for push notifications.
  - **Account**
    - Player ID (read-only, copyable).
    - Sign in / Link account button (Google / Apple) — optional.
    - Restore purchases.
  - **Support**
    - Help / FAQ
    - Contact support
  - **Legal**
    - Terms of service
    - Privacy policy
  - **About**
    - Version number, build hash.
- Optional footer: small "Reset progress" link for dev builds.

## Components
| Component         | Type      | Notes                                              |
|-------------------|-----------|----------------------------------------------------|
| `btn_back`        | Button    | Returns to caller                                  |
| `lbl_title`       | Text      | "Settings"                                         |
| `toggle_sfx`      | Toggle    | Sound effects on/off                               |
| `slider_sfx`      | Slider    | 0-100, disabled when toggle off                    |
| `toggle_music`    | Toggle    | Music on/off                                       |
| `slider_music`    | Slider    | 0-100, disabled when toggle off                    |
| `row_language`    | Row       | Shows current language, opens picker               |
| `toggle_notif`    | Toggle    | Push notifications                                 |
| `lbl_player_id`   | Text+Copy | Player id with copy icon                           |
| `btn_link_account`| Button    | Optional, only if not linked                       |
| `btn_restore`     | Button    | iOS / Android restore purchases                    |
| `btn_help`        | Button    | Opens help                                         |
| `btn_contact`     | Button    | Opens email / form                                 |
| `btn_tos`         | Button    | Opens external link / webview                      |
| `btn_privacy`     | Button    | Opens external link / webview                      |
| `lbl_version`     | Text      | App version + build                                |

## States
- **Default:** Reflects current persisted settings.
- **Audio off:** Slider disabled and greyed.
- **Language picker open:** Sub-popup overlays.
- **Account linked:** "Link account" replaced with "Signed in as ..." + sign-out button.

## Interactions / Logic
- Each toggle / slider persists immediately to local storage and applies live (mute audio, change volume).
- Language change → reload localization, soft-refresh visible text. May require restart for some languages with large font deltas; show toast "Language updated".
- Back button → `Navigate(back)`.
- Hardware back / swipe-back → equivalent to Back button.

## Data
- Persisted: sfxEnabled, sfxVolume, musicEnabled, musicVolume, language, notificationsEnabled, accountLink.
- Sources: local prefs / cloud profile.

## Audio
- Adjusting sliders: play sample SFX as the slider moves.
- Button SFX on toggles.

## Analytics
- `settings_shown`
- `settings_audio_changed` (channel, value)
- `settings_language_changed` (from, to)
- `settings_account_linked` (provider)

## Accessibility
- Sliders operable by tap-and-step buttons in addition to drag.
- Labels read via screen reader with current values.
- Color-independent toggle indicator (text "On"/"Off").

## Defaults / Assumptions
- Default sfx + music ON, volumes 80%.
- Default language = device locale, fallback English.
- Languages list: en, vi, es, pt-BR, fr, de, ja, ko, zh-CN, zh-TW (configurable list).
