# Popup Blueprint: Result (Win / Lose)

## Overview
- **Popup ID:** `popup_result`
- **Type:** Modal overlay (covers gameplay)
- **Parent screen:** Gameplay
- **Trigger:** Level outcome resolved (win or lose)
- **Dismiss to:** Gameplay (Retry), Level Select (Map / Next)

## Purpose
Communicate level outcome, show stars earned (win) or failure reason (lose), grant rewards, and offer Retry / Next / Quit actions.

## Layout
- Full-screen dim overlay.
- Centered result card.

### Win variant
- Top: animated banner "Level Complete!".
- Stars row: 3 star slots filled in sequence with stagger animation according to score thresholds.
- Score block: final score, best score, level number.
- Reward block: coins earned, optional booster reward.
- Button row (bottom):
  - **Map** (return to Level Select)
  - **Next** (primary, go to next level)
- Optional: share button.

### Lose variant
- Top: banner "Out of moves!" / "Out of time!" / "Failed!" depending on reason.
- Sub-message: e.g. "You needed 5 more candies".
- Lives indicator (-1 life).
- Button row:
  - **Quit** (return to Level Select)
  - **Retry** (primary, costs 1 life)
- Optional: "Continue" offer (use coins / rewarded ad to gain extra moves) shown BEFORE the lose state in many match-3 games; in this blueprint it lives in Gameplay layer, not here.

## Components
| Component        | Type      | Notes                                              |
|------------------|-----------|----------------------------------------------------|
| `bg_dim`         | Overlay   | Non-tappable                                        |
| `card_result`    | Panel     | Variant: win / lose                                 |
| `banner_title`   | Text+FX   | "Level Complete!" / "Failed!"                       |
| `row_stars`      | Widget    | 3 star icons, animated fill                         |
| `block_score`    | Widget    | Score, best, level                                  |
| `block_reward`   | Widget    | Coins / booster reward (win only)                   |
| `lbl_reason`     | Text      | Lose reason (lose only)                             |
| `btn_map`        | Button    | Return to Level Select                              |
| `btn_next`       | Button    | Win only, primary                                   |
| `btn_quit`       | Button    | Lose only, secondary                                |
| `btn_retry`      | Button    | Lose only, primary                                  |

## States
- **Win 1-star / 2-star / 3-star:** Differs in star animation and possibly reward amount.
- **Win, last level in chapter:** "Next" navigates to chapter complete screen instead.
- **Lose, no lives left:** Retry disabled or prompts to refill lives.

## Interactions / Logic
- On open (win): play win stinger, animate stars in sequence, count up score, count up coin reward, persist progress (stars, best score), grant rewards.
- On open (lose): play lose stinger, decrement lives, persist no progress.
- `btn_next` → reload Gameplay with `levelId + 1`.
- `btn_retry` → reload Gameplay with same `levelId`, consume 1 life.
- `btn_map` / `btn_quit` → `Navigate(LevelSelect)`.

## Audio
- Win: `sfx_win_stinger` + bgm fade.
- Lose: `sfx_lose_stinger`.
- Star ding per star.
- Button taps.

## Analytics
- `result_shown` (outcome, levelId, stars, score)
- `result_next_tapped`
- `result_retry_tapped`
- `result_map_tapped`

## Accessibility
- Stars communicated via count text in addition to icons.
- Animations respect reduced-motion (skip-able by tap).
- Focus moves to primary button on open.

## Defaults / Assumptions
- Stars: 1 = goal met, 2 = goal met + score threshold A, 3 = goal met + score threshold B.
- Retry costs 1 life. New best score persists.
- Win rewards: small coin grant (e.g. 50 coins) by default; configurable per level.
