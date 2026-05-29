# Game Feel — Best Practices (General)

Engine-agnostic notes on making a game *feel* satisfying ("sướng"). Distilled
from hands-on juice work; phrased so it transfers to any minigame.

> One sentence to remember: **feeling is an energy curve, synchronized across
> channels, that tracks game state and serves readability — not a collection of
> pretty effects.**

---

## 1. Core mental model: build → detonate

Satisfaction comes from the **shape of the energy curve**, not from any single
effect. Energy must *ramp up* to a climax and *then* burst — never burst first
and taper.

- The slow / static parts (victory pose, result overlay, settle) always come
  **after** the climax, never in the middle of the rise.
- A reliable arc: *anticipation → accelerating build → detonation (the peak) →
  short resolution*.
- Smell test: if the most intense frame is at the **start** of a celebration and
  everything after is calmer, the arc is backwards. Reorder it.

## 2. The feedback ladder — work in priority order

When adding feel to a game, go cheapest-highest-ROI first:

1. **Haptics first.** Cheapest win, biggest payoff. Map each event class to a
   distinct *weight*: a light tick for routine steps, a soft bump for
   pick-up/grab, a sharper buzz for "blocked/invalid", a heavy thud for
   win/clear. The haptic vocabulary should mirror the action's weight.
2. **Per-interaction feedback.** Every meaningful action — grab, extend,
   retrace/undo, blocked — gets its own immediate signal. The player should
   never wonder whether the last input *took* or *missed*.
3. **Pacing & anticipation.** Telegraph the payoff (e.g. pulse the cells that
   would finish the board); cap durations so nothing drags.

Don't jump to particles and trophies while the foundational sensory layer
(haptics + instant per-action feedback) is missing.

## 3. Techniques that consistently pay off

- **Intensity tracks game state.** Feedback shouldn't be uniform. Scale it by
  progress with a *back-loaded* curve (e.g. `intensity = progress^1.6`) so it
  surges as the player nears completion — faint early, blazing near the end.
- **Acceleration reads as life.** A wave whose steps *shorten* over time feels
  alive; constant/linear timing feels mechanical. Use easing everywhere; almost
  never linear.
- **An impact frame = multiple channels on one beat.** A hit feels like a hit
  because *camera punch + screen flash + haptic* land on the **same frame**, not
  because one channel is loud. Synchronize, don't amplify.
- **Depth comes from cheap layers, not one expensive effect.** A single thin
  outline reads cheap; a soft bloom + two staggered, differently-tinted rings
  reads premium. Same trick for bursts (glow + stars + orbs + sparkles). Stack a
  few cheap layers with slight offsets in time, scale, and color.
- **One focal point for the climax.** Everything at the peak should radiate from
  a single point. Don't let the big moment sprawl across the screen.
- **Snappy, with a duration ceiling.** Bound total effect time regardless of
  content size (e.g. the finish wave finishes in ~0.3s whether the line is 5 or
  50 cells — long content just accelerates harder). Squeeze; don't lengthen.
- **Fire feedback on the visual climax, not before it.** If the burst happens a
  beat after the logical event, move the haptic/sound to the burst so they
  coincide.

## 4. Discipline — so juice doesn't fight the game

- **Respect readability.** Additive glow blows bright colors out to white;
  clamp peak opacity by the color's luminance. Juice serves the player's ability
  to read the board — it must never wash it out.
- **Opt-in to shared code.** Shared effect layers used by multiple games should
  only gain *default-off* parameters, so one game's juice can't regress another.
  New effects live game-side first; promote to shared only once proven.
- **Extract constants + pure functions.** Put every tuning number in one
  `*Visuals`/constants file with descriptive names — iteration drops to seconds.
  Keep the math (curves, schedules) as pure functions and unit-test those; the
  *feel* itself is verified by eye, not by assertion.

## 5. Workflow

- Tight loop: fast type/compile check (catches red) → build (confirms it runs) →
  **run it and judge the feel by eye.** Effect layers can't be meaningfully
  unit-tested; don't try. Test the pure math; eyeball the juice.
- Lock in small increments. Commit each feel layer as soon as it's verified, so a
  later change that kills the feel is easy to bisect and revert.
- "Verified" for juice means a human watched it, not that a test passed.

---

### Quick checklist for a new "feel" pass

- [ ] Does energy *build* to the climax (not peak-then-taper)?
- [ ] Haptics mapped to event weights?
- [ ] Every action has instant, distinct feedback (success vs. fail)?
- [ ] Intensity scales with game state, back-loaded?
- [ ] Climax = punch + flash + haptic on one beat, from one focal point?
- [ ] Richness from a few cheap stacked layers, not one heavy effect?
- [ ] Durations capped; nothing drags on long content?
- [ ] Bright colors clamped so the board stays readable?
- [ ] Shared-code changes default-off?
- [ ] Tuning numbers named in one place; curves unit-tested; feel eyeballed?
