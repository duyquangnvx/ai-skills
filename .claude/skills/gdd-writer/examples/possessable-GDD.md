# Possessable

> **Tagline:** A tiny ghost. A locked room. A lot of furniture.
> **Version:** 0.1 · **Last updated:** 2026-05-12 · **Owner:** J. Park

---

## 1. Pitch

A 48-hour-jam puzzle platformer where you play a small, sad ghost trying to escape a locked house by possessing furniture. Each object you possess gives you a different verb — chairs can stack, lamps can illuminate, books can be thrown — and the puzzle is figuring out which sequence of possessions unlocks the next room.

**Genre:** Puzzle platformer
**Platform(s):** Browser (itch.io)
**Reference games:** _Patrick's Parabox_ (single-mechanic depth) meets _Baba Is You_ (object-swap logic), with the cozy melancholy of _A Short Hike_.

---

## 2. Design Pillars

1. **One verb at a time.** Every puzzle should be readable as "which object do I need to be right now?" Anything that requires juggling two possessions simultaneously is cut.
2. **Sad, not scary.** This is a ghost story about loneliness, not horror. No jump-scares, no threats.
3. **Five-minute rooms.** Every puzzle should be solvable in under five minutes by a fresh player. A jam game is a short game.

---

## 3. Core Loop

**30-second loop:** Look at the room → pick an object to possess → use that object's verb → look again.
**5-minute loop:** Enter a room → solve the possession puzzle → exit through the unlocked door.
**Session loop:** ~6 rooms, ~30 minutes to complete the whole game.

---

## 4. Mechanics

### Player actions
- **Float** (move ghost form, slow, ignores gravity)
- **Possess** (press E on an object to become it)
- **Release** (press E again to leave the object and return to ghost form)
- **Object-specific verb** (each object has one — see below)

### Possessable objects (jam scope)
- **Chair** — can be stacked on other furniture
- **Lamp** — illuminates dark areas, revealing platforms
- **Book** — can be picked up by other possessions, thrown for weight
- **Clock** — pauses moving hazards while possessed
- **Painting** — opens a hidden passage when possessed (one-time)
- **Door** — final puzzle. Possess to unlock.

### Progression
No upgrades, no meta-progression. Linear room sequence. Each room introduces one new possessable.

---

## 5. Art Direction

**Visual style:** 2D pixel art, 32×32 tiles, hand-animated.

**Mood/tone:** Soft, twilight, melancholic. A house at dusk, dust in the light beams.

**Reference images:**
- [TBD] — _Lighting reference: the warm-window aesthetic of A Short Hike interiors_
- [TBD] — _Ghost design: small, droopy, expressive face, see Spirit City: Lofi Sessions_
- [TBD] — _Room composition: cluttered but readable, see Owlboy interiors_

**Color palette:** 16-color limited palette — dusty pinks, warm browns, soft purples. Two accent colors: lamp yellow for hints, ghost cyan for the player.

---

## 6. UI / UX

**Camera:** Fixed per room, no scrolling. One screen = one puzzle.

**Controls:**
- Arrow keys / WASD — move
- E — possess / release
- Space — object verb (varies per possession)
- R — reset room

**HUD elements:** None during gameplay. A small icon top-left shows which object is currently possessed.

**Key screens:** Title, room (the game), pause, end card.

---

## 7. Scope & Schedule

**Target playtime:** 30 minutes for completion.
**Content targets:** 6 rooms, 6 possessable types.

**Schedule (48 hours):**
- Hour 0–6: Core ghost + possession mechanic working, one test room
- Hour 6–18: Rooms 1–3, all object verbs prototyped
- Hour 18–30: Rooms 4–6, art pass on rooms 1–3
- Hour 30–42: Art pass remaining rooms, audio, polish
- Hour 42–48: Bug fix, build, submit

**Out of scope** (explicitly NOT building):
- Cutscenes or text-heavy story
- Multiple endings
- Settings menu beyond default audio
- A reset-all-progress option
- Achievements

---

## 8. Open questions / TBDs

> **TBD:** Decide whether the player can possess the same object twice in one room or it's locked after release.
> **TBD:** Final room — is the "Door" puzzle a mechanical climax or an emotional one? Lean emotional, but needs a moment.
