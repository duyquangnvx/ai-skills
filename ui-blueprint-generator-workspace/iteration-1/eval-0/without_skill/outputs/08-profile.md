# Screen Blueprint: Profile

## Overview
- **Screen ID:** `profile`
- **Type:** Player info screen
- **Orientation:** Portrait
- **Entry from:** Main Menu
- **Exit to:** Main Menu

## Purpose
Show the player's identity (avatar, display name), progression (player level / XP), and earned achievements. Allow basic edits like changing avatar / name.

## Layout
- Top bar:
  - Back button (left).
  - Title "Profile" (center).
  - Edit (pencil) icon (right) — toggles edit mode.
- Header card:
  - Circular avatar (tappable in edit mode → avatar picker popup).
  - Display name below avatar (tappable in edit mode → name input popup).
  - Player level badge + XP progress bar to next level.
  - Player ID (small, copyable).
- Stats row (3 columns):
  - Levels completed.
  - Total stars earned.
  - Highest streak / win rate (configurable).
- Achievements section:
  - Section header "Achievements" + counter (e.g. "12 / 40").
  - Grid of achievement tiles (3 per row).
    - Each tile: icon, name, progress bar, unlocked vs locked visual.
    - Tap → achievement detail popup with description and reward.
- Optional sections:
  - Friends list / leaderboard preview.
  - Trophy / collection cabinet.

## Components
| Component             | Type      | Notes                                              |
|-----------------------|-----------|----------------------------------------------------|
| `btn_back`            | Button    | Returns to Main Menu                               |
| `btn_edit`            | Button    | Toggles edit mode                                  |
| `widget_avatar`       | Widget    | Avatar image, tappable in edit mode                |
| `lbl_name`            | Text      | Display name                                       |
| `widget_level`        | Widget    | Level number + XP bar + XP text                    |
| `lbl_player_id`       | Text+Copy | Player id row                                      |
| `stat_levels`         | StatTile  | Number + label                                     |
| `stat_stars`          | StatTile  | Number + label                                     |
| `stat_streak`         | StatTile  | Number + label                                     |
| `grid_achievements`   | Grid      | Virtualised, 3 columns                             |
| `tile_achievement`    | Item      | Icon, name, progress, unlocked state               |

## States
- **View (default):** Read-only fields.
- **Edit:** Avatar and name become tappable; Edit icon swaps to "Done" check.
- **Achievement locked:** Greyscale + lock icon; progress shown if partial.
- **Achievement unlocked:** Coloured + checkmark; tap shows reward + grant button if unclaimed.
- **Achievement claimable:** Highlighted with badge dot.

## Interactions / Logic
- `btn_edit` → toggle edit mode; persist on Done.
- Avatar tap (edit) → avatar picker popup (preset list, possibly unlock-gated).
- Name tap (edit) → text-input popup with profanity / length validation.
- `tile_achievement` tap → achievement detail popup.
- On enter: load profile + achievements progress (local first, cloud sync if available).

## Data
- Profile: avatarId, displayName, playerLevel, xp, xpToNext, playerId, stats (levelsCompleted, starsTotal, etc.).
- Achievements: list of { id, name, desc, iconRef, target, progress, unlocked, claimed, reward }.

## Audio
- Background: ambient or main menu BGM continues.
- Achievement unlock SFX when popping detail.

## Analytics
- `profile_shown`
- `profile_avatar_changed`
- `profile_name_changed`
- `achievement_detail_opened` (id)
- `achievement_reward_claimed` (id)

## Accessibility
- Avatar / name editable via dedicated buttons too (not just tap).
- Achievement state communicated by icon + text, not only color.
- Long names truncated with ellipsis but full name read by screen reader.

## Defaults / Assumptions
- Avatars: 12 preset avatars unlocked from start; more unlock via achievements.
- Display name: 3-16 chars, profanity-filtered.
- Achievements: ~40 entries, mix of progression / collection / streak based.
- Player level / XP system: gain XP per level completed (e.g. base + stars * bonus).
