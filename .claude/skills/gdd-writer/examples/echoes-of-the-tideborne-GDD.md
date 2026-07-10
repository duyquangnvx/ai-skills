# Echoes of the Tideborne

> **Tagline:** Sail the sound, not the sea — a rhythm-roguelike where every wave is a beat.
> **Version:** 0.1 · **Last updated:** 2026-05-12 · **Owner:** A. Tran

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Pillars](#2-design-pillars)
3. [Core Loop & Game Flow](#3-core-loop--game-flow)
4. [Gameplay Mechanics](#4-gameplay-mechanics)
5. [Progression & Economy](#5-progression--economy)
6. [Story & World](#6-story--world)
7. [Levels & Content](#7-levels--content)
8. [Art Direction](#8-art-direction)
9. [UI / UX](#9-ui--ux)
10. [Audio](#10-audio)
11. [Technical Notes](#11-technical-notes)
12. [Scope, Schedule & Risks](#12-scope-schedule--risks)
13. [Out of Scope](#13-out-of-scope)
14. [Open Questions](#14-open-questions)

---

## 1. Overview

### 1.1 Pitch (Elevator)
A rhythm-roguelike where you captain a tiny boat across a procedural ocean of music — your moves, attacks, and parries all snap to the beat of an adaptive soundtrack that gets denser as you sail deeper.

### 1.2 Concept (Detailed)
*Echoes of the Tideborne* is a top-down rhythm roguelike for solo players. Each run drops the player on a tiny boat in a procedural sea split into "stanzas" — short musical phrases that act as level segments. The player navigates by tapping to the beat: every quarter-note is an opportunity to move, attack, or parry. Missing the beat doesn't kill you, but it locks out your inputs for one bar — long enough to get hit.

The hook is that the music isn't background — it's the level. Enemies appear on specific beats, hazards spawn on bar transitions, and the soundtrack layers up as you push deeper, turning the game from a sparse percussion line at the start of a run into a full orchestral piece by the final boss.

Inspired by *Crypt of the NecroDancer* (rhythm-as-input), *Dredge* (small boat, dread of the deep), and *Hades* (run-based pacing, character voice).

### 1.3 Genre & References
- **Primary genre:** Rhythm roguelike
- **Secondary tags:** Single-player, top-down, indie, narrative-light
- **Reference games:**
  - **Crypt of the NecroDancer** — beat-locked input model
  - **Dredge** — small-boat dread, escalating creepiness as you push out
  - **Hades** — run pacing, between-run character beats, escalating soundtrack

### 1.4 Target Audience
- **Primary:** Players ages ~18–40 who like rhythm games AND roguelikes (NecroDancer, Hi-Fi Rush, Hades). Comfortable with 30–60 min play sessions, willing to fail and learn.
- **Secondary:** Music-focused players who don't normally play roguelikes — the soundtrack is the draw.

### 1.5 Platforms & Input
- **Launch platforms:** PC (Steam, Win/Mac/Linux), Switch
- **Post-launch consideration:** iOS/Android (touch-only build) at +6 months
- **Input methods:** Gamepad (primary), keyboard, touch on mobile. Mouse not supported — the game is beat-based, not point-based.

### 1.6 Unique Selling Points
1. The soundtrack IS the level — every wave, enemy, and hazard is on the beat.
2. Adaptive music layers grow with run depth: solo cello at biome 1, full orchestra at biome 5.
3. Failure isn't punishing the wrong note — it's losing one bar of inputs. Always recoverable, never frustrating.

---

## 2. Design Pillars

1. **Music is the system.** Every mechanic must be expressible in beats. If a feature breaks the rhythm-input model, it's cut.
2. **Recover, don't restart.** Missing a beat costs a bar, never a life. Death only comes from sustained mistakes, never one slip.
3. **The ocean gets louder.** Every layer of depth adds a layer of sound. Progression is audible before it's visible.

---

## 3. Core Loop & Game Flow

### 3.1 Core Loops (nested)
- **Moment-to-moment (~2s):** Listen for incoming beat → choose move/attack/parry → execute on the beat.
- **Encounter (~30s):** Spot wave or enemy → identify pattern → survive the bar → loot or move on.
- **Stanza / level (~3–5 min):** Sail a procedural musical phrase → fight the stanza's boss → choose a between-stanza upgrade.
- **Run (~25–40 min):** Pass through 5 biome stanzas → final boss → die or win → return to dock.
- **Meta (10+ hr):** Unlock new boats, new soundtracks, new captains, hard mode.

### 3.2 Game Flow

```
Boot → Title → Dock (meta hub) → Select Captain & Boat → Set Sail → [Stanza 1...5] → Final Boss
                ↑                                                                         ↓
                └─── Return with shards (currency) ←──── Death OR Win ←──────────────────┘
```

### 3.3 Player Objectives
- **Short-term:** Survive the current bar without missing a beat.
- **Mid-term:** Reach the next stanza and pick a good upgrade.
- **Long-term:** Beat the final boss with all five captains; unlock the deep-ocean ending.

---

## 4. Gameplay Mechanics

### 4.1 Player Actions

| Action | Input (gamepad) | Notes |
|---|---|---|
| Move | D-pad / left stick + on beat | One tile per beat, 8-directional |
| Attack | A button on beat | Hits adjacent tile in facing direction |
| Parry | B button on beat | One-bar window, blocks one hit, riposte if perfect |
| Special | Y button on downbeat (beat 1) | Captain-specific ability, uses 1 charge |
| Wait | Hold left stick neutral | Burns the beat safely, used for timing |

### 4.2 Core Systems

#### Beat lock-out
Missing a beat (acting off-rhythm or holding two conflicting inputs) puts the player into a "stagger" state for one bar (4 beats). During stagger, no inputs register. This is the primary failure cost — you can't be hit while staggered, but you also can't avoid hazards that arrive during stagger. Stagger is announced with a distinct sound and a visual ripple, so it's always clear.

#### Wave patterns
Each biome has a library of wave patterns — sequences of hazard tiles that arrive on specific beats. A "two-and-four" wave pattern arrives on beats 2 and 4 of every bar; a "syncopated" pattern arrives on the off-beats. Patterns are introduced one biome at a time and combined in later biomes.

#### Enemies
Enemies have a "tell" beat (they flash one beat before they act) and an "act" beat. Players who learn to listen for the tell can pre-position. Enemies don't have HP — most die in one hit, with elites taking 2–3 hits and bosses being multi-phase encounters tied to song structure.

### 4.3 Failure & Death
The boat has 3 hull points. Hit by a hazard or enemy → lose 1 hull. At 0 hull → run ends, return to dock with earned shards. No checkpoints within a run.

---

## 5. Progression & Economy

### 5.1 In-run Progression
- **Upgrades** (between stanzas): pick 1 of 3. Examples: +1 hull, parry window +50%, special charges +1, gain a passive note ability.
- **Charts** (rare drops mid-stanza): consumables that buff one stanza only.

### 5.2 Meta Progression
- **Shards** (run currency): permanent currency earned every run, win or lose. Spent at the dock.
- **Captain unlocks:** new playable captains with different abilities and starting boats.
- **Soundtrack unlocks:** new musical genres unlock new biome variants.

### 5.3 Economy
- **Resources:** Hull (in-run, capped at 5), Special charges (in-run, capped at 3), Shards (meta, uncapped)
- **Sources:** clearing stanzas (+10 shards), defeating elites (+5), defeating bosses (+50), perfect-bar bonus (+1 per perfect bar)
- **Sinks:** captain unlocks (200–500 shards), boat skins (100), soundtrack variants (300), hard mode unlock (1000)
- **Balance target:** ~150 shards per average run, full meta unlock takes ~40 runs.

---

## 6. Story & World

### 6.1 Premise
The ocean has gone silent. The Tideborne — sea-singers whose voices kept the deep tame — have all vanished, and the music of the sea is being eaten by something below. You're the last apprentice, the only one who can still hear the old songs. You sail to find what's been silencing them.

### 6.2 Setting
A stylized ocean world. No specific real-world geography — just sea, sky, and the things between. The world is "loud" near the coast (shanties, fishing villages heard from afar) and grows quieter and stranger as the player sails out.

### 6.3 Narrative Delivery
Story is told entirely through:
- Short captain dialogues at the dock (between runs)
- Environmental "echoes" — found objects that play a brief audio clip
- The soundtrack itself, which becomes more dissonant in deeper biomes

No cutscenes. No lengthy text logs.

### 6.4 Plot Outline
- **Act 1 (biomes 1–2):** Player learns the basics, meets remaining sea folk who tell of the disappearances.
- **Act 2 (biomes 3–4):** Player discovers the songs themselves are being consumed by a deep entity.
- **Act 3 (biome 5 + boss):** Confront the entity. Choice: silence it (kill it) or sing with it (alternate ending unlock).

---

## 7. Levels & Content

### 7.1 Content Inventory
- 5 biomes (musical genres): folk, jazz, electronic, classical, dissonant
- 20 enemy types (4 per biome)
- 5 bosses + 1 final
- ~40 wave patterns
- 30 upgrades (6 per category)
- 5 playable captains
- ~25 audio "echoes" for environmental story

### 7.2 Level / Area Structure
Procedural runs through 5 stanzas (one per biome), each ~3–5 minutes. Layout within a stanza is procedurally generated from a hand-authored set of pattern blocks. Boss arenas are hand-designed.

### 7.3 Sample First-time User Experience
- **Minute 0–1:** Dock tutorial — meet the mentor captain, learn move and attack on simple percussion beat.
- **Minute 1–3:** First stanza, very sparse. Two wave patterns and one enemy type. Cannot fail.
- **Minute 3–8:** Second stanza adds parry and a second enemy type. First real challenge.
- **Minute 8–15:** Stanza 3 introduces special ability. By the end of the first run, the player has touched all core mechanics.

---

## 8. Art Direction

### 8.1 Visual Style
Hand-illustrated 2D top-down with a painterly, watercolor-leaning aesthetic. Limited frame counts for animation (~8 frames per loop) to keep the hand-drawn feel.

### 8.2 Mood & Tone
Coastal melancholy near the start, gradually shifting to surreal and slightly unsettling at depth. Never horror — always wonder.

### 8.3 Color & Palette
Per-biome 24-color palette. Cool, sun-faded for biome 1. Vivid jazz neons for biome 3. Near-monochrome blues with sickly highlights for biome 5.

### 8.4 Reference Images / Moodboard
> **TBD:** Pinterest board link from art lead. Placeholders below describe intent:
- [TBD] — _Ocean tone reference: Sable's painterly horizon, muted blue/lavender_
- [TBD] — _Boat design: small, handcrafted, see Dredge's starter trawler_
- [TBD] — _Enemy silhouette: stylized, readable from one tile away, see Hyper Light Drifter sketches_

### 8.5 Animation Style
Frame-by-frame for the player boat (8 frames bob loop, 6 frame attack). Particle-driven for water and waves. UI animations are tween-based.

### 8.6 Key Asset List
- 5 captain portraits + 5 boat sprites
- 20 enemy sprites (idle, tell, attack, death = 4 states each)
- 5 biome tilesets
- 5 boss sprite sets
- ~30 hazard sprites (waves, mines, whirlpools)
- UI: panels, beat indicator, hull indicator, special charge UI

---

## 9. UI / UX

### 9.1 Camera
Fixed top-down at moderate zoom. Player boat is centered. View extends ~6 tiles in each direction.

### 9.2 Controls
Gamepad-primary, keyboard fully supported.
- **Gamepad:** D-pad/L-stick (move), A (attack), B (parry), Y (special), X (wait/burn beat), Start (pause)
- **Keyboard:** WASD/Arrows (move), J (attack), K (parry), L (special), Space (wait), Esc (pause)
- Full rebinding supported.

### 9.3 HUD
Persistent on-screen:
- Hull pips (top-left)
- Special charges (top-right)
- Beat indicator (center-bottom) — a pulsing ring that the player times inputs to
- Stanza progress bar (top-center, subtle)

### 9.4 Screens
- Title / boot
- Main menu (New Run, Continue, Captains, Soundtrack, Options, Quit)
- Dock (meta hub)
- Captain select
- Boat customization
- Options (Video, Audio, Controls, Accessibility)
- Pause
- Between-stanza upgrade screen
- Run results
- Credits

### 9.5 Player Onboarding
First run is a soft tutorial — sparse pattern density, contextual prompts (gamepad icons hovering above the boat for "press A to attack"). No text-heavy tutorial. Mentor captain dialog covers narrative framing.

---

## 10. Audio

### 10.1 Music
Adaptive, layered soundtrack composed in five biome-genres: folk, jazz, electronic, classical, dissonant. Each biome has a base loop + 3 layers that activate based on run depth and player performance. Composer brief: "Make it feel like the sea is the orchestra."

### 10.2 Sound Effects
Diegetic where possible — splash sounds for waves, creaks for the boat. Combat SFX are mixed quieter than music, with a stronger emphasis on rhythmic "click" cues for hits and parries.

### 10.3 Voice
No spoken dialogue. Captain "voices" are stylized syllabic blurts (Animal Crossing style) over text. This keeps localization cheap and the aesthetic consistent.

---

## 11. Technical Notes

### 11.1 Engine & Tools
Godot 4. Custom music-sync layer using FMOD for adaptive audio.

### 11.2 Target Hardware
PC min spec: Intel i3 2017+, integrated GPU, 4 GB RAM. Switch native. iOS/Android (post-launch) targeting 2020+ devices.

### 11.3 Performance Targets
60 FPS on min spec PC. 60 FPS docked on Switch, 30 FPS handheld acceptable for biome 5. <3s load between stanzas.

### 11.4 Key Technical Risks
- FMOD adaptive layering on Switch is the biggest unknown — needs early prototype on devkit.
- Beat-accurate input on mobile (touch latency) may force frame-skip tolerance design.

---

## 12. Scope, Schedule & Risks

### 12.1 Team
- 1 director / designer (A. Tran)
- 2 programmers (one gameplay, one audio/tech)
- 1 artist (full-time)
- 1 composer (contract)
- 1 part-time QA from month 8

### 12.2 Milestones

| Milestone | Target date | Definition |
|---|---|---|
| First playable | 2026-08 | One captain, one biome, one boss, gamepad only |
| Vertical slice | 2026-12 | Two biomes polished, all systems wired, marketing assets |
| Content complete | 2027-06 | All 5 biomes, all captains, all bosses |
| Beta | 2027-09 | Feature-complete, in playtesting |
| Ship | 2027-12 | PC + Switch launch |

### 12.3 Risks
- **Composer bandwidth** — 5 biome scores is a lot. Mitigation: contract a second composer for biomes 3–4 if behind by month 9.
- **Switch port performance** — mitigation: early devkit prototyping in month 4, performance budget set per biome.
- **Beat-input feel** — if rhythm-input doesn't feel good, the entire game fails. Mitigation: first playable focuses 100% on input feel before content.

---

## 13. Out of Scope

Considered and explicitly excluded:
- Multiplayer (co-op or PvP). The rhythm system is too tightly coupled to one player.
- A leveling/XP system. Run-to-run meta is the only progression.
- Procedurally generated music. Layers swap and combine but the underlying compositions are hand-written.
- A "free play" mode without the run structure.

---

## 14. Open Questions

> **TBD:** Should perfect-bar bonuses stack within a stanza (combo system), or reset each bar? Affects flow state design.
> **TBD:** Final ending — both endings, or commit to a single canonical ending and a "secret" variant?
> **TBD:** Switch performance — confirm 60 FPS feasibility on biome 5 by 2026-09.

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-05-12 | A. Tran | Initial draft |
