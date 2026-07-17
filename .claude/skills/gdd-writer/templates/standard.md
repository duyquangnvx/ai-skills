# {{GAME_TITLE}}

> **Tagline:** {{TAGLINE — one memorable phrase that brands the game}}
> **Version:** 0.1 · **Last updated:** {{DATE}} · **Owner:** {{AUTHOR}}

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Pillars](#2-design-pillars)
3. [Core Loop & Game Flow](#3-core-loop--game-flow)
4. [Gameplay Mechanics](#4-gameplay-mechanics)
5. [Progression & Economy](#5-progression--economy)
6. [Story & World](#6-story--world) <!-- conditional -->
7. [Characters](#7-characters) <!-- conditional -->
8. [Levels & Content](#8-levels--content)
9. [Art Direction](#9-art-direction)
10. [UI / UX](#10-ui--ux)
11. [Audio](#11-audio) <!-- conditional -->
12. [Multiplayer](#12-multiplayer) <!-- conditional -->
13. [Monetization](#13-monetization) <!-- conditional -->
14. [Technical Notes](#14-technical-notes)
15. [Scope, Schedule & Risks](#15-scope-schedule--risks)
16. [Out of Scope](#16-out-of-scope)
17. [Open Questions](#17-open-questions)

---

## 1. Overview

### 1.1 Pitch (Elevator)
{{Two sentences max. What is the game and why play it?}}

### 1.2 Concept (Detailed)
{{2–3 paragraphs. The expanded vision: what the player experiences, what makes this different, what emotional space it occupies.}}

### 1.3 Genre & References
- **Primary genre:** {{e.g. Roguelike deckbuilder}}
- **Secondary tags:** {{e.g. Single-player, turn-based, fantasy}}
- **Reference games:**
  - **{{Game 1}}** — {{what we take from it}}
  - **{{Game 2}}** — {{what we take from it}}
  - **{{Game 3}}** — {{what we take from it but do differently}}

### 1.4 Target Audience
- **Primary:** {{Demographic and play-pattern, e.g. "Players who enjoy 1–3 hour sessions of strategic games (Slay the Spire, Inscryption audience), ages ~18–40"}}
- **Secondary:** {{Optional secondary audience}}

### 1.5 Platforms & Input
- **Launch platforms:** {{e.g. PC (Steam, Win/Mac/Linux)}}
- **Post-launch consideration:** {{e.g. Switch port at +6 months}}
- **Input methods:** {{Mouse+KB, gamepad, touch — and which is primary}}

### 1.6 Unique Selling Points (USPs)
1. {{USP 1 — what makes this stand out on a store page}}
2. {{USP 2}}
3. {{USP 3}}

---

## 2. Design Pillars

3–4 principles every decision must support. Cut anything that doesn't reinforce a pillar.

1. **{{Pillar name}}** — {{What it means in practice. Give an example of a decision this pillar resolves.}}
2. **{{Pillar name}}** — {{...}}
3. **{{Pillar name}}** — {{...}}

---

## 3. Core Loop & Game Flow

### 3.1 Core Loops (nested)
- **Moment-to-moment (~10s):** {{...}}
- **Encounter (~1–2 min):** {{...}}
- **Run / level (~10–30 min):** {{...}}
- **Meta / session (1+ hour):** {{...}}

### 3.2 Game Flow

How the player moves through the game from cold launch to deep play:

```
Boot → Title Screen → Main Menu → New Run → [Core Loop] → Run Result → Meta Upgrade Screen → New Run
                                  ↘ Continue ↗
```

{{Replace the diagram with a description that matches your game.}}

### 3.3 Player Objectives
- **Short-term:** {{What's the player chasing in the next 5 minutes?}}
- **Mid-term:** {{In the next session?}}
- **Long-term:** {{What does "completing" the game look like?}}

---

## 4. Gameplay Mechanics

### 4.1 Player Actions
List the verbs available to the player. Be specific about inputs.

| Action | Input | Notes |
|---|---|---|
| {{e.g. Move}} | {{WASD / left stick}} | {{e.g. 8-directional, grid-snapped}} |
| {{Action 2}} | {{Input}} | {{Notes}} |
| {{Action 3}} | {{Input}} | {{Notes}} |

### 4.2 Core Systems
For each major system, describe what it is, how it works, and what decisions it creates for the player.

#### {{System 1 name, e.g. "Card-draw combat"}}
{{1–3 paragraphs. Mechanics, edge cases, key numbers if known.}}

#### {{System 2 name}}
{{...}}

#### {{System 3 name}}
{{...}}

### 4.3 Failure & Death
{{What happens when the player loses? Permadeath? Checkpoint? Lose currency?}}

---

## 5. Progression & Economy

### 5.1 In-run Progression
{{How the player gets stronger / unlocks more options during a single play session.}}

### 5.2 Meta Progression
{{What persists between sessions? Unlocks, currency, lore, character roster?}}

### 5.3 Economy
- **Resources:** {{e.g. Gold (in-run), Souls (meta), Keys (rare in-run)}}
- **Sources** (how the player earns each): {{...}}
- **Sinks** (where they spend it): {{...}}
- **Balance target:** {{rough ratios — e.g. "expect ~200 gold per run, full upgrade costs 1000 gold spread across 3 runs"}}

---

## 6. Story & World

<!-- Delete this section if the game has no narrative -->

### 6.1 Premise
{{One paragraph. The setup: who, where, what's wrong.}}

### 6.2 Setting
{{Where and when does this take place? What are the rules of this world?}}

### 6.3 Narrative Delivery
{{How does story reach the player? Cutscenes, environmental, dialogue, lore drops, found-text? Pick what matches scope.}}

### 6.4 Plot Outline
{{Bullet outline of major beats. Don't write the full script here.}}
- {{Beat 1}}
- {{Beat 2}}
- {{Beat 3}}

---

## 7. Characters

<!-- Delete this section if the game has no named characters -->

### 7.1 Player Character(s)
| Name | Role | Key trait |
|---|---|---|
| {{...}} | {{...}} | {{...}} |

### 7.2 NPCs / Cast
{{For each major NPC: name, role in the game, role in the story, what they do mechanically.}}

---

## 8. Levels & Content

### 8.1 Content Inventory
- {{e.g. 30 enemy types · 60 cards · 8 boss encounters · 5 biomes}}

### 8.2 Level / Area Structure
{{How levels are organized — linear chapters? Procedural runs? Open world zones? Hub-and-spoke?}}

### 8.3 Sample Level / First-time User Experience
{{Walk through the first 10–15 minutes of play. What does the player see, learn, do, and feel?}}

---

## 9. Art Direction

### 9.1 Visual Style
{{e.g. Hand-painted 2D · Low-poly stylized 3D · Pixel art at specific resolution}}

### 9.2 Mood & Tone
{{e.g. Melancholic, twilight palette · Bright cozy · Industrial oppressive}}

### 9.3 Color & Palette
{{Limited palette? Mood-driven shifts? Per-biome palette swap?}}

### 9.4 Reference Images / Moodboard
- {{Link or descriptor 1}}
- {{Link or descriptor 2}}
- {{Link or descriptor 3}}

### 9.5 Animation Style
{{Frame-by-frame? Skeletal? Limited-frame to suit the look?}}

### 9.6 Key Asset List
- {{e.g. Player character (idle, walk, attack, hit, death)}}
- {{Enemy sprites (×30)}}
- {{Tilesets (×5 biomes)}}
- {{UI: icons, panels, fonts}}

---

## 10. UI / UX

### 10.1 Camera
{{e.g. Fixed top-down · Side-scrolling · Third-person 3D · Free orbit}}

### 10.2 Controls
{{Detailed input mapping. Include controller AND keyboard if both supported.}}

### 10.3 HUD
{{What's persistently on screen? Health, currency, ability cooldowns, minimap?}}

### 10.4 Screens
List all screens the game needs:
- Main menu
- {{Pause / settings / options / video / audio / controls}}
- {{Inventory / loadout / deck}}
- {{Map / world view}}
- {{Run results / death screen}}
- {{Meta upgrade screen}}
- {{Credits}}

### 10.5 Player Onboarding
{{How does the player learn the game? Explicit tutorial? Discovery? Tooltips? "Show, don't tell" intro level?}}

---

## 11. Audio

<!-- Delete or shorten if audio is minimal -->

### 11.1 Music
{{Style, instrumentation references. Dynamic/adaptive or linear loops?}}

### 11.2 Sound Effects
{{Tone — punchy and arcadey? Subtle and naturalistic? Stylized?}}

### 11.3 Voice
{{Full VO? Grunts-and-text? None? Localization implications?}}

---

## 12. Multiplayer

<!-- Delete this section if singleplayer -->

### 12.1 Mode(s)
{{Co-op? PvP? Asynchronous? Player count?}}

### 12.2 Networking model
{{Peer-to-peer? Dedicated servers? Listen server? Authoritative model?}}

### 12.3 Matchmaking
{{Skill-based? Lobby browser? Invite-only?}}

### 12.4 Social features
{{Friends, voice chat, emotes, spectator?}}

---

## 13. Monetization

<!-- Delete this section if no commercial plan -->

### 13.1 Model
{{Premium / Free-to-play / Premium + DLC / Subscription / Ad-supported}}

### 13.2 Price point
{{Target launch price (and region differences if known)}}

### 13.3 Post-launch content
{{Free updates? Paid DLC? Cosmetics? Battle pass?}}

---

## 14. Technical Notes

### 14.1 Engine & Tools
{{e.g. Unity 6, Unreal 5, Godot 4, custom}}

### 14.2 Target Hardware
{{Min/recommended specs. Mobile chipsets if applicable.}}

### 14.3 Performance Targets
{{Target framerate, resolution, load times.}}

### 14.4 Key Technical Risks
- {{e.g. Procedural generation needs to fit in <2s load on min spec}}
- {{...}}

---

## 15. Scope, Schedule & Risks

### 15.1 Team
{{Roles and who covers them.}}

### 15.2 Milestones
| Milestone | Target date | Definition |
|---|---|---|
| First playable | {{date}} | {{what "playable" means here}} |
| Vertical slice | {{date}} | {{...}} |
| Content complete | {{date}} | {{...}} |
| Ship | {{date}} | {{...}} |

### 15.3 Risks
- **{{Risk 1}}** — {{Mitigation}}
- **{{Risk 2}}** — {{Mitigation}}

---

## 16. Out of Scope

Features we have considered and explicitly chosen NOT to build. Revisit only with strong justification.

- {{Tempting feature 1}}
- {{Tempting feature 2}}
- {{Tempting feature 3}}

---

## 17. Open Questions

> **TBD:** {{Specific question to resolve}}
> **TBD:** {{Another}}

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | {{DATE}} | {{AUTHOR}} | Initial draft |
