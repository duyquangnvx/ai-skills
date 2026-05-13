# Conditional Sections — When to Include What

Three sections are always included:
- Pitch + Core Loop + Design Pillars
- Mechanics
- Art Direction + UI/UX

Every other section is conditional. Use the rules below to decide whether to include a section. The rule of thumb: **a section earns its place by changing how someone on the team would do their work.** If removing it loses nothing, leave it out.

---

## Story / Narrative / World

**Include if:**
- The game has named characters with motivations
- There is a plot, even a loose one (escape the dungeon, save the kingdom)
- The setting itself is a selling point (specific historical period, original IP world)
- Cutscenes, dialogue, or environmental storytelling are planned

**Skip if:**
- Abstract puzzle game (Tetris, Threes)
- Pure mechanical sandbox (most racing, fighting, sports games)
- Game-jam game where the "story" is just a one-line setup
- The user explicitly says "no story"

**Depth guide:**
- Lean tier: 1 short section combining premise + setting
- Standard: separate Story & World + Characters sections
- Comprehensive: full breakdown including themes, plot structure, narrative delivery, player agency

---

## Characters

**Include if:**
- The player controls a named, characterized protagonist (not "the player" / "the cube")
- There are recurring NPCs the player interacts with
- Character archetypes matter for class/role selection

**Skip if:**
- The player is an anonymous avatar
- No NPCs of note
- All "characters" are really enemies — describe them in the AI or Combat section instead

---

## Combat

**Include if:**
- Combat is a primary verb (anything from shooters to RPGs to fighting games)

**Skip if:**
- Pure puzzle, walking sim, narrative adventure with no combat
- Sports / racing — those have their own analogous sections (race rules, scoring) not "combat"

**Note:** For games with combat AND non-combat systems (RPGs, immersive sims), keep Combat as its own section even at Standard tier — it's almost always complex enough to deserve dedicated space.

---

## Levels / Areas / Content Inventory

**Include if:** Any game with discrete content beyond procedural generation. Even procedural games usually have biome/area definitions.

**Skip if:** Truly content-less (pure abstract puzzle with one play space).

**Note:** The "content inventory" subsection (counts of enemies/items/etc.) is almost always worth including — it forces concreteness about scope.

---

## Artificial Intelligence

**Include if:**
- Enemies have non-trivial behaviors (anything beyond "patrol then attack")
- Companion AI is a feature
- Ambient/world AI matters (immersive sim, open world)
- An adaptive/director system is planned (L4D, Resident Evil director)

**Skip if:**
- PvP only — no AI to design
- Pure puzzle — opponents don't "think"
- Turn-based abstract games (chess-like) where AI is a separate technical concern, not a design one
- Card games where AI is mostly probabilistic, not behavioral (mention briefly under Mechanics)

---

## Multiplayer / Networking

**Include if:** Any form of multi-player interaction — co-op, PvP, async, social.

**Skip entirely if:** Pure singleplayer, no leaderboards, no async social features. Don't include a "we might add multiplayer later" section — that's noise.

**Sub-section guidance when included:**
- Always: Modes, player count, social features
- Add Networking architecture for real-time multiplayer
- Add Matchmaking for player-vs-player or pickup games
- Add PvP balance if PvP exists
- Add Anti-cheat for competitive multiplayer

---

## Monetization

**Include if:**
- The game is commercial in any way (premium sale, F2P, ads, DLC, subscription)

**Skip if:**
- Game jam game, student project, portfolio piece with no commercial intent
- "We'll figure it out later" — mark as TBD instead of writing a hollow section

**Depth guide:**
- Premium-sold game: brief section, mostly price + DLC plans
- F2P: needs detailed economy interaction, monetization fairness philosophy, IAP categories
- Live service: also include the Live Operations section

---

## Live Operations

**Include only if** the game is explicitly a live service (regular content updates, seasons, events, KPI-tracked retention). Don't include for premium games with occasional patches.

---

## Audio

**Include if:**
- Music or audio identity is part of the pitch (rhythm games, atmospheric horror, music-driven titles)
- VO is planned
- The team has a dedicated audio person or contractor

**Skip / shorten if:**
- Solo dev using royalty-free assets — a short note in Art Direction is enough
- Game jam game

---

## Accessibility

**Include if:** Standard tier or above for any commercial release. This should increasingly be default — Microsoft, Sony, and Nintendo all push for accessibility features now.

**Can skip if:** Game jam or one-off prototype with no public release intent.

---

## Localization

**Include if:**
- Commercial release in multiple regions
- The game is text-heavy (RPG, narrative adventure, strategy)

**Skip if:**
- Single-language launch, no localization planned
- Visual game with minimal text (most arcade, puzzle, racing)

---

## Technical Specification

**Include if:** Any project with a team of more than 2, OR any project that will be QA'd, ported, or shipped to console.

**Depth guide:**
- Lean: skip or a one-line note ("Built in Godot 4, targeting Windows + Linux")
- Standard: engine, target hardware, performance targets, key tech risks
- Comprehensive: full hardware matrix, save system, build pipeline, third-party dependencies

---

## Production Plan / Schedule

**Include in all tiers**, but match depth:
- Lean: a few milestones + ship date + "out of scope"
- Standard: milestone table + risks + out-of-scope
- Comprehensive: phased plan, milestone table, team composition, budget, full risk register

---

## Marketing & Community

**Include if:**
- Commercial release
- Active community / live service

**Skip if:** Non-commercial, student project, internal-only.

---

## Genre-Specific Cheat Sheet

Quick reference for "what does a typical [genre] GDD include":

| Genre | Must-have (beyond mandatory 3) | Often-needed | Usually skip |
|---|---|---|---|
| Roguelike / roguelite | Progression (meta), Economy, Levels (procedural rules), AI (enemies) | Combat, Story (light), Audio | Multiplayer, Localization |
| Turn-based strategy | Combat (deep), Economy, Levels, AI (opponent), Multiplayer (often) | Story, Tech | — |
| Narrative adventure / walking sim | Story (deep), Characters, World, Audio | UI/Accessibility | Combat, AI, Multiplayer, Economy |
| FPS singleplayer | Combat, Levels, AI, Story | Audio, Tech | Multiplayer, Economy |
| FPS multiplayer | Combat, Multiplayer (deep), Levels (maps), Live Ops | Anti-cheat, Tech, Monetization | Story (light or none) |
| Puzzle game | Levels (deep), UI | Story (light), Audio | Combat, AI, Multiplayer, Economy |
| Sandbox / sim | Economy, Progression, AI (ambient), Tech | Story (light), Multiplayer | Combat (sometimes) |
| Cozy / farming sim | Progression, Economy, Story, Characters, World | Audio, Localization | Combat, complex AI |
| Mobile F2P casual | Monetization (deep), Live Ops, Economy, Onboarding, Localization | Tech (mobile-specific) | Complex story, AI |
| Fighting game | Combat (very deep), Characters (rosters), Multiplayer, Balance | Tech (netcode), Audio | Story (light), Economy |
| Racing | Tracks/Levels, Cars/Vehicles (analog of Combat), Multiplayer | Audio, Progression | Story (often), complex AI |
| Card / deckbuilder | Mechanics (deep), Progression, Economy, Levels (encounter design) | Story (light), Multiplayer | Complex AI, Tech (light) |
| MMORPG | Everything. This is comprehensive-tier territory. | — | — |
