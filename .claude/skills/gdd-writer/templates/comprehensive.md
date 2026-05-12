# {{GAME_TITLE}}

> **Tagline:** {{TAGLINE}}
> **Working Title:** {{If different from final title}}
> **Version:** 0.1 · **Last updated:** {{DATE}} · **Document Owner:** {{AUTHOR}}
> **Status:** Draft / Pre-production / Production / Live

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Design Pillars & Vision](#2-design-pillars--vision)
3. [Game Overview](#3-game-overview)
4. [Core Loop & Game Flow](#4-core-loop--game-flow)
5. [Gameplay Mechanics](#5-gameplay-mechanics)
6. [Progression Systems](#6-progression-systems)
7. [Economy & Resources](#7-economy--resources)
8. [Combat](#8-combat) <!-- conditional -->
9. [Story, Setting & World](#9-story-setting--world) <!-- conditional -->
10. [Characters](#10-characters) <!-- conditional -->
11. [Levels, Areas & Content](#11-levels-areas--content)
12. [Artificial Intelligence](#12-artificial-intelligence) <!-- conditional -->
13. [Multiplayer & Networking](#13-multiplayer--networking) <!-- conditional -->
14. [Art Direction](#14-art-direction)
15. [Audio Direction](#15-audio-direction)
16. [User Interface](#16-user-interface)
17. [User Experience & Onboarding](#17-user-experience--onboarding)
18. [Accessibility](#18-accessibility)
19. [Localization](#19-localization)
20. [Technical Specification](#20-technical-specification)
21. [Monetization](#21-monetization) <!-- conditional -->
22. [Live Operations](#22-live-operations) <!-- conditional, live service -->
23. [Marketing & Community](#23-marketing--community)
24. [Production Plan](#24-production-plan)
25. [Risks & Mitigations](#25-risks--mitigations)
26. [Out of Scope](#26-out-of-scope)
27. [Open Questions](#27-open-questions)
28. [Appendices](#28-appendices)

---

## 1. Executive Summary

### 1.1 Elevator Pitch
{{Two sentences. Memorable.}}

### 1.2 Hook / High Concept
{{One paragraph. The "why this exists" — the creative thesis that justifies the project.}}

### 1.3 Unique Selling Points
1. {{USP 1}}
2. {{USP 2}}
3. {{USP 3}}
4. {{USP 4}}

### 1.4 Genre, Platforms, Audience
- **Genre:** {{...}}
- **Sub-genres / tags:** {{...}}
- **Launch platforms:** {{...}}
- **Post-launch platforms:** {{...}}
- **Target audience:** {{primary + secondary}}
- **Age rating target:** {{ESRB / PEGI / CERO}}

### 1.5 Comparable Titles
| Game | Year | Why it's relevant |
|---|---|---|
| {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | {{...}} |

### 1.6 Business Goals
{{Launch revenue target, player count target, critical reception target — whatever makes this a "success" for the business.}}

---

## 2. Design Pillars & Vision

### 2.1 Design Pillars
The 3–5 principles every design decision must serve. If a proposed feature doesn't reinforce a pillar, it's cut or revised.

1. **{{Pillar name}}** — {{Definition + an example decision this pillar resolves}}
2. **{{Pillar}}** — {{...}}
3. **{{Pillar}}** — {{...}}

### 2.2 Player Fantasy
{{What does the player get to be / feel / do? Articulate the fantasy in 1–2 paragraphs.}}

### 2.3 Emotional Arc
{{What emotions do we want the player to feel across a session? Across the full game?}}

### 2.4 Non-Goals
{{Things this game explicitly is not trying to be. Useful for resisting scope drift.}}

---

## 3. Game Overview

### 3.1 Concept (Detailed)
{{3–5 paragraphs. The full expanded vision.}}

### 3.2 Look & Feel Summary
{{One paragraph snapshot of visual + tonal identity. Details live in §14.}}

### 3.3 Player Experience Goals
- {{e.g. "Within the first 5 minutes, the player should have killed something and gotten a permanent unlock."}}
- {{...}}

---

## 4. Core Loop & Game Flow

### 4.1 Nested Loops
- **Moment-to-moment (~10s):** {{...}}
- **Encounter (~1–3 min):** {{...}}
- **Mission / run (~15–60 min):** {{...}}
- **Session (~1–3 hr):** {{...}}
- **Meta / long-term (10+ hr):** {{...}}

### 4.2 Game Flow Diagram
{{ASCII or described flow from cold launch through deep play.}}

### 4.3 Objectives
- **Primary:** {{...}}
- **Secondary:** {{...}}
- **Optional / completionist:** {{...}}

---

## 5. Gameplay Mechanics

### 5.1 Player Actions / Verbs
{{Full table of inputs and their effects, including modifiers.}}

### 5.2 Movement
{{Locomotion details: walk speed, run, jump, dodge, climb, swim, vehicles. Numbers if known.}}

### 5.3 Core Systems
For each major system, write a sub-section. Cover: what it is, how it works, what choices it gives the player, edge cases, key tunable parameters.

#### 5.3.1 {{System name}}
{{...}}

#### 5.3.2 {{System name}}
{{...}}

#### 5.3.3 {{System name}}
{{...}}

### 5.4 Interactions
{{How players interact with objects (pick up, drop, use, throw), NPCs (talk, trade, fight), and environment (open, push, break).}}

### 5.5 Failure States
{{Death? Game over? Soft fail with retry? Permadeath?}}

---

## 6. Progression Systems

### 6.1 Player Character Progression
{{XP? Skill tree? Equipment? Class change?}}

### 6.2 Meta Progression
{{What persists between runs / sessions / deaths?}}

### 6.3 Unlocks
{{What is locked at start? What's the unlock pacing?}}

### 6.4 Mastery
{{What does "getting good" look like for an expert player?}}

---

## 7. Economy & Resources

### 7.1 Resource Types
| Resource | Scarcity | Source | Sink | Cap? |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

### 7.2 Currency Flow
{{How money moves through the game. Inflation control. Sink design.}}

### 7.3 Crafting / Trading
<!-- Delete if not applicable -->
{{...}}

---

## 8. Combat

<!-- Delete this entire section if the game has no combat -->

### 8.1 Combat Pillars
{{What kind of combat? Tactical? Twitchy? Methodical?}}

### 8.2 Damage & Defense Model
{{HP? Armor? Damage types? Resistances? Critical hits?}}

### 8.3 Weapons / Attacks
{{Categories, archetypes, balance philosophy.}}

### 8.4 Enemy Archetypes
{{Tank / glass cannon / support / boss patterns.}}

### 8.5 Player Power Curve
{{How player strength scales over the campaign.}}

---

## 9. Story, Setting & World

<!-- Delete if the game has no narrative -->

### 9.1 Premise & Logline
{{...}}

### 9.2 Setting
{{Where, when, what are the rules of the world?}}

### 9.3 Backstory
{{Historical context the player learns OR that informs the world even if never stated.}}

### 9.4 Themes
{{What is this game about, beneath the surface?}}

### 9.5 Plot Structure
{{Three-act? Hero's journey? Episodic? Branching?}}

### 9.6 Major Story Beats
- {{Beat 1}}
- {{Beat 2}}
- {{...}}

### 9.7 Narrative Delivery
{{Cinematics, environmental, dialogue, found-text, codex, radio chatter?}}

### 9.8 Player Agency
{{Linear story? Branching dialogue? Multiple endings?}}

---

## 10. Characters

<!-- Delete if no named characters -->

### 10.1 Player Character(s)
{{Profile each playable character: appearance, backstory, motivation, gameplay role.}}

### 10.2 Major NPCs
{{Profile each: role in story, role in gameplay, dialogue voice.}}

### 10.3 Antagonists
{{Profile primary and notable secondary antagonists.}}

### 10.4 Faction Map
<!-- Delete if no factions -->
{{Groups, their goals, their relationships.}}

---

## 11. Levels, Areas & Content

### 11.1 Content Inventory
{{Hard counts: number of levels, enemies, weapons, items, quests, lines of dialogue, cinematics, biomes, etc.}}

### 11.2 Level / Area Structure
{{Linear chapters? Open world zones? Procedural? Hub-and-spoke?}}

### 11.3 Area Briefs
For each area / level:
- Name
- Theme
- Player level expected
- Critical path
- Notable encounters / set-pieces
- Required new assets

### 11.4 First-Time User Experience
{{The first 30 minutes, beat-by-beat. What does the player learn, when, and how?}}

---

## 12. Artificial Intelligence

<!-- Delete if the game has no meaningful AI (e.g. pure PvP, abstract puzzle) -->

### 12.1 Opponent / Enemy AI
{{Behavior trees, decision-making, difficulty scaling, group behavior.}}

### 12.2 Companion / Friendly AI
{{Pathing, response to player commands, situational awareness.}}

### 12.3 Ambient / World AI
{{Crowds, wildlife, schedules, day-night behavior.}}

### 12.4 Director / Adaptive AI
<!-- Delete if not used -->
{{e.g. Left 4 Dead style director, dynamic difficulty.}}

---

## 13. Multiplayer & Networking

<!-- Delete this section entirely if singleplayer -->

### 13.1 Modes
{{Co-op, competitive, async, MMO, social.}}

### 13.2 Player Count
{{Per-mode player counts.}}

### 13.3 Networking Architecture
{{Authoritative server? Peer-to-peer? Listen server? Lockstep?}}

### 13.4 Matchmaking
{{Skill-based? Region-based? Party support?}}

### 13.5 Anti-cheat
{{Approach and tooling.}}

### 13.6 Social Features
{{Friends, parties, voice, text chat, clans/guilds.}}

### 13.7 PvP Balance
<!-- Delete if no PvP -->
{{Balance philosophy, patching cadence.}}

---

## 14. Art Direction

### 14.1 Visual Style
{{Detailed style description.}}

### 14.2 Mood, Tone, Atmosphere
{{...}}

### 14.3 Color Theory
{{Palette, contrast philosophy, how color is used to communicate gameplay.}}

### 14.4 Reference Boards
- {{Link or description 1}}
- {{Link or description 2}}
- {{Link or description 3}}

### 14.5 Character Design
{{Silhouette philosophy, proportions, costume language.}}

### 14.6 Environment Design
{{Scale, density, landmark strategy, biome differentiation.}}

### 14.7 VFX
{{Stylized vs. naturalistic. Readability targets.}}

### 14.8 Animation
{{Style — frame-by-frame? Skeletal? Mocap? Specific frame counts? Animation principles to follow.}}

### 14.9 Asset Pipeline
{{Authoring tools, source formats, export pipeline, naming conventions.}}

---

## 15. Audio Direction

### 15.1 Music
{{Style references, instrumentation, dynamic vs. linear, layering approach.}}

### 15.2 Sound Effects
{{Tone, libraries vs. custom, foley needs.}}

### 15.3 Voice
{{Full VO? Localized VO? Performance direction. Number of VO lines (rough).}}

### 15.4 Audio Mix Philosophy
{{Diegetic vs. non-diegetic balance, ducking, accessibility considerations.}}

---

## 16. User Interface

### 16.1 Camera
{{First-person, third-person, top-down, isometric. FOV. Camera behavior in combat / cutscenes.}}

### 16.2 Controls / Input
{{Full mapping for each supported input device. Rebinding support.}}

### 16.3 HUD
{{What's persistently visible during gameplay. Diegetic vs. overlay.}}

### 16.4 Menus & Screens
{{Full list of screens with purpose:}}
- Title / Boot
- Main menu
- Options (video, audio, controls, accessibility)
- Save / Load
- Pause
- Inventory
- Map
- Skill tree
- Codex / Lore
- Quest log
- Settings
- Results / End-of-mission
- Credits

### 16.5 Help System
{{Tooltips, contextual hints, manual / codex, in-game tutorial.}}

---

## 17. User Experience & Onboarding

### 17.1 Onboarding Approach
{{Explicit tutorial? Discovery? Mentor character? "Show, don't tell"?}}

### 17.2 First-Time User Experience (FTUE)
{{First 5, 15, 30 minutes — what the player learns at each beat.}}

### 17.3 Critical UX Flows
{{Map out the most important multi-screen flows: start a new game, save, quit, configure controls, change difficulty.}}

### 17.4 Difficulty
{{Difficulty levels? Adaptive? Assists / accessibility settings tied to difficulty?}}

---

## 18. Accessibility

### 18.1 Visual
{{Subtitles, colorblind modes, text size, high-contrast UI.}}

### 18.2 Audio
{{Visual cues for audio info, separate volume sliders, mono audio.}}

### 18.3 Motor
{{Remappable controls, hold-vs.-toggle options, auto-aim assists, QTE alternatives.}}

### 18.4 Cognitive
{{Difficulty toggles, slow-down mode, simplified UI, save-anywhere.}}

---

## 19. Localization

### 19.1 Target Languages
{{Launch languages, post-launch additions.}}

### 19.2 Scope per Language
{{Text only? Full VO? Subtitled VO?}}

### 19.3 Localization-Sensitive Content
{{Currency, dates, gore levels per region, religious/political content review.}}

---

## 20. Technical Specification

### 20.1 Engine
{{Engine + version, key plugins, custom tech.}}

### 20.2 Target Hardware
| Tier | CPU | GPU | RAM | Storage |
|---|---|---|---|---|
| Minimum | {{...}} | {{...}} | {{...}} | {{...}} |
| Recommended | {{...}} | {{...}} | {{...}} | {{...}} |

### 20.3 Performance Targets
{{FPS, resolution, load times, memory budget.}}

### 20.4 Save System
{{Save points? Save anywhere? Cloud sync? Save corruption recovery?}}

### 20.5 Build Pipeline & QA
{{Daily builds? Automated testing? Cert process?}}

### 20.6 Third-party Dependencies
{{SDKs, middleware, services.}}

---

## 21. Monetization

<!-- Delete if non-commercial -->

### 21.1 Model
{{Premium / F2P / Premium+DLC / Subscription / Hybrid}}

### 21.2 Pricing
{{Launch price, regional pricing, planned discounts.}}

### 21.3 In-game Purchases
<!-- Delete if no IAP -->
{{Categories, price points, fairness philosophy.}}

### 21.4 DLC / Expansion Plan
{{Roadmap of paid content.}}

---

## 22. Live Operations

<!-- Delete if not a live service -->

### 22.1 Content Cadence
{{Patches, seasons, events.}}

### 22.2 Season Structure
{{Length, pass design, themes.}}

### 22.3 KPIs
{{DAU, retention curves (D1/D7/D30), ARPDAU, session length.}}

---

## 23. Marketing & Community

### 23.1 Positioning
{{One-line positioning statement.}}

### 23.2 Key Beats
{{Reveal, demo, beta, launch, post-launch.}}

### 23.3 Community Strategy
{{Discord, social channels, content creator program.}}

---

## 24. Production Plan

### 24.1 Team Composition
{{Roles, sizes, key hires needed.}}

### 24.2 Phases
| Phase | Duration | Definition of done |
|---|---|---|
| Concept | {{...}} | {{...}} |
| Pre-production | {{...}} | {{...}} |
| Production | {{...}} | {{...}} |
| Alpha | {{...}} | {{...}} |
| Beta | {{...}} | {{...}} |
| Cert / Ship | {{...}} | {{...}} |
| Post-launch | {{...}} | {{...}} |

### 24.3 Major Milestones
{{Specific dates and deliverables.}}

### 24.4 Budget
{{Top-line budget or budget ranges by category.}}

---

## 25. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| {{...}} | {{H/M/L}} | {{H/M/L}} | {{...}} | {{...}} |
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

---

## 26. Out of Scope

Features explicitly chosen NOT to build. Revisit only with strong justification.

- {{...}}
- {{...}}
- {{...}}

---

## 27. Open Questions

> **TBD:** {{...}}
> **TBD:** {{...}}

---

## 28. Appendices

### A. Glossary
{{Project-specific terms.}}

### B. Reference Materials
{{Links to external research, competitive analysis, market data.}}

### C. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | {{DATE}} | {{AUTHOR}} | Initial draft |
