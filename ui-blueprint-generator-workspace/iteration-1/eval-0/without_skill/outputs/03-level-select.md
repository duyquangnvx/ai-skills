# Screen Blueprint: Level Select

## Overview
- **Screen ID:** `level_select`
- **Type:** Navigation / progression screen
- **Orientation:** Portrait
- **Entry from:** Main Menu (Play), Result popup (Map)
- **Exit to:** Gameplay (selected level), Main Menu (back)

## Purpose
Show the player's progression as a scrollable map / grid, indicate which levels are unlocked and what star score has been achieved, and let them launch any unlocked level.

## Layout
- Themed scrolling background (vertical scroll, parallax).
- Top bar:
  - Back button (left).
  - Coins widget (right).
  - Lives widget (right of back).
- Scrollable content area: vertical list of level nodes laid out on a winding path or grid.
  - Each node = circular badge with level number.
  - Stars earned displayed under or around the node (0-3).
  - Locked levels: greyscale + padlock icon.
  - Current level: highlighted with glow / pulse.
- Bottom anchor:
  - Auto-scroll-to-current button (small floating button) appears if user scrolls away from current level.

## Components
| Component         | Type      | Notes                                              |
|-------------------|-----------|----------------------------------------------------|
| `btn_back`        | Button    | Returns to Main Menu                               |
| `widget_coins`    | Widget    | Same as main menu                                  |
| `widget_lives`    | Widget    | Same as main menu                                  |
| `list_levels`     | ScrollList| Virtualised, vertical                              |
| `node_level`      | Item      | level number, stars, locked/unlocked state         |
| `btn_jump_current`| Button    | Floating, optional                                 |

## Level node states
- **Locked:** Grey, padlock icon, not interactive.
- **Unlocked unplayed:** Coloured, no stars, pulse animation.
- **Completed:** Coloured, star count (1-3) shown.
- **Current (next to play):** Highlighted with glow.

## Interactions / Logic
- Tap unlocked node → open `LevelStartPopup` (shows level objectives, best score, stars, lives cost, Play button).
  - Play in popup → `Navigate(Gameplay, levelId)`.
- Tap locked node → small toast "Complete previous level to unlock".
- Pull-to-refresh: re-fetch progress (optional).
- On enter: scroll to current level automatically.

## Data
- Source: local save + (optional) cloud sync.
- For each level: id, status (locked/unlocked/completed), stars, best score.

## Audio
- BGM: same as main menu or dedicated `bgm_map`.
- SFX: `sfx_node_tap`, `sfx_node_locked`.

## Analytics
- `level_select_shown`
- `level_node_tapped` (levelId, status)
- `level_select_back`

## Accessibility
- Scroll inertia respects reduced motion settings.
- Locked-state communicated via icon, not just color.

## Defaults / Assumptions
- Linear unlock progression: level N unlocked when level N-1 is completed.
- 3-star scoring per level.
- No world/chapter grouping in v1 (flat list); easy to extend to chapters later.
