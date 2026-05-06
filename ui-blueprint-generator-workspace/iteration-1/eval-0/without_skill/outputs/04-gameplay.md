# Screen Blueprint: Gameplay

## Overview
- **Screen ID:** `gameplay`
- **Type:** Core gameplay scene
- **Orientation:** Portrait
- **Entry from:** Level Select (via Level Start popup), Result popup (Retry)
- **Exit to:** Result popup (win/lose), Pause popup (overlay), Level Select (after Result)

## Purpose
The main playable scene where the player matches gems on a board, uses boosters, and tries to reach level objectives within a turn or time limit.

## Layout (top → bottom)
- **HUD (top, ~ 18% of screen height):**
  - Pause button (top-left).
  - Level number / objective summary (top-center): icons of target gems with required count and remaining count, or score target.
  - Score / Star progress bar (centered horizontally, below objective).
  - Moves / time remaining counter (top-right).
- **Board (center, ~ 60% of screen height):**
  - Square match-3 grid (default 8x8, configurable per level).
  - Themed border / frame.
  - Particle / FX layer above board for matches and special pieces.
- **Booster bar (bottom, ~ 18% of screen height):**
  - Up to 4 booster slots (e.g. Hammer, Swap, Bomb, Shuffle).
  - Each slot shows icon + count owned.
  - Tap booster → enter targeting mode.
- **Optional:** Combo / streak feedback floats over the board.

## Components
| Component             | Type        | Notes                                              |
|-----------------------|-------------|----------------------------------------------------|
| `btn_pause`           | Button      | Opens Pause popup                                  |
| `widget_objective`    | Widget      | Shows goal icons + remaining counts                |
| `widget_score`        | Widget      | Score number + 3-star progress bar                 |
| `widget_moves`        | Widget      | Moves left or time left, depending on level type   |
| `board`               | GridGameView| Match-3 grid, accepts swipe/tap input              |
| `booster_slot[0..3]`  | Button      | Booster icon + count + tap-to-arm                  |
| `fx_layer`            | Effects     | Match explosions, screen shake, combo text         |
| `lbl_combo`           | Text        | Animated combo / streak text                       |

## States
- **Playing:** Normal input, HUD updating.
- **Booster armed:** Booster icon highlighted, board cursor changed, tap on board applies booster (or cancel by tapping booster again).
- **Resolving cascade:** Input disabled while cascades animate.
- **Out of moves / time, goal not met:** Trigger "lose" flow → Result popup (lose).
- **Goal met:** Lock input, play "win" flourish, count down remaining moves into bonus score, then Result popup (win).
- **Paused:** Show Pause popup overlay; gameplay frozen.

## Interactions / Logic
- Swap by swipe or tap-tap of two adjacent gems.
- Match 3+ → clear, drop, refill, cascade.
- Match 4/5/L/T → spawn special piece (line bomb, color bomb, etc.).
- Booster tap → enter targeting mode; second tap on board applies; consumes 1 charge.
- If no possible moves → auto-shuffle.
- Pause button → pause timers, dim background, show Pause popup.
- Win condition met → start win sequence (described above).
- Lose condition met → option to use "+5 moves" (rewarded ad / coins) before showing lose Result popup (configurable).

## Data In
- `levelId`, level config (board size, blockers, goal type, goal target, move/time limit, available boosters).
- Player inventory (booster counts).

## Data Out (to Result popup)
- Outcome: win or lose.
- Score, stars earned (0-3).
- Goal completion details.
- Moves/time used.
- Currency earned.

## Audio
- BGM: `bgm_gameplay` (loop, ducks during big FX).
- SFX: match, cascade, combo, special spawn, booster activate, low-moves warning, win, lose.

## Analytics
- `level_started` (levelId)
- `level_completed` (levelId, stars, score, movesUsed)
- `level_failed` (levelId, reason)
- `booster_used` (boosterId, levelId)
- `pause_opened` (levelId)

## Accessibility
- Color-blind safe gem palette (shape + color).
- Reduced-motion: dampen screen shake and particle volume.
- Larger-tap-target option for board cells.

## Defaults / Assumptions
- 8x8 default board, swap-based input, move-limited levels with collect-N goal type by default.
- 3-star scoring tied to score thresholds in level config.
- 4 booster slots; missing boosters can be purchased via "+" tap.
