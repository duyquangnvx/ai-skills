---
name: gdd-writer
description: Use when the user wants to write, draft, generate, scaffold, or structure any game design document — GDD, design doc, game pitch doc, game concept doc, design spec, functional spec, engineering spec, or implementation-ready GDD — for any genre (mobile, PC, console, indie, AAA, multiplayer, F2P, narrative, puzzle, match-3, hyper-casual, etc.) or scope (one-pager, standard, comprehensive, MVP). Also use when the user describes a game idea and asks to turn it into a structured document, asks to "document the design" of a game concept, or asks for an engineer-ready spec with data models, algorithms, balance numbers, and edge cases.
---

# GDD Writer

A skill for producing Game Design Documents in Markdown that follow industry best practices. The output is a single `.md` file that is version-control friendly, easy to read in any text editor, and renders nicely on GitHub, GitLab, Notion, and similar tools.

## Core philosophy

A GDD is a **living blueprint**, not a contract. The goal is a document the team will actually read and update — not a 50-page spec that goes stale on day two. Three principles drive every choice:

1. **Right-size to the project.** A weekend prototype needs a one-pager. A 12-month indie project needs ~10–15 sections. An AAA pitch needs the full structure. Pick the tier that matches reality.
2. **Conditional sections only.** Don't include a "Multiplayer" section for a singleplayer game, don't include "Monetization" for a free portfolio piece. Empty headers are noise.
3. **Concrete beats abstract.** Every section should give the reader something they can act on — a number, a reference image link, a named mechanic, a specific verb. Vague aspiration ("immersive experience") is worse than nothing.

## Workflow

### Step 1: Gather enough information to write something useful

Before writing, you need to know enough to fill in the **mandatory** sections concretely. If the user's initial message doesn't cover these, ask 3–6 focused questions in a single batch (prefer one batched message over a slow back-and-forth):

**Always need to know:**
- Working title (or placeholder)
- Genre + closest 2–3 reference games ("like X meets Y")
- Core loop in one sentence ("Explore → fight → loot → upgrade → repeat")
- Target platform(s)
- Scope/tier intent — solo prototype? indie team? full studio production?

**Ask only if relevant to the game:**
- Story/narrative — only if the game has one
- Multiplayer details — only if multiplayer
- Monetization model — only if commercial / F2P
- Art direction references — always nice to have, but don't block on it

If the user has already given a rich brief, **skip the interview** and go straight to drafting. Don't ask redundant questions when the answer is already in context.

**Extra prerequisite for the Functional Spec tier.** Before drafting, also do a quick prior-art pass:
- Identify 2–3 top games in the same sub-genre (use the user's reference titles if given).
- Skim store reviews for those games and surface 3–5 recurring complaints (resource decrement on crash, predatory ads, soft-locks, save-loss, opaque difficulty). These complaints feed §3.6 (failure/recovery), §6.3 (resource anti-frustration), and §7.4 (monetization anti-frustration) — they are the bugs your team should not repeat.
- If you cannot do this research in-session, mark it as the first row of §12 Open Questions with the user as owner.

### Step 2: Pick the tier

Choose one of four tiers based on the project's stated scope, the primary reader of the deliverable, and the depth of input you have. Read the corresponding template file from `templates/` — it is the source of truth for structure and section order.

| Tier | When to use | Template file |
|---|---|---|
| **Lean** | Solo dev, game jam, prototype, early pitch, "one-pager" requested, or input is minimal | `templates/lean.md` |
| **Standard** | Default for most indie/small-team projects. ~10–15 sections, covers gameplay, art, UI, scope, but skips deep technical/AI breakdowns | `templates/standard.md` |
| **Comprehensive** | Full production, multi-team, publisher pitch, AAA-style, or user explicitly asks for "complete/full/detailed GDD" — broad coverage across design, narrative, art, audio, business, live ops | `templates/comprehensive.md` |
| **Functional Spec** | Engineer-ready spec. Primary reader is Engineering / QA / Level Design. User asks for "functional spec", "engineering spec", "implementation-ready GDD", "MVP spec", or describes a mobile/casual/F2P/multiplayer game where data models, algorithms, balance numbers, and edge cases matter more than vision/narrative. Output uses MUST/SHOULD/MAY/TBD, TypeScript pseudo-code, and an explicit acceptance-criteria checklist | `templates/functional-spec.md` |

If unsure between two tiers, **pick the smaller one** and offer to expand later. Bloat is the more common failure mode.

Functional Spec is orthogonal to the other three: it can replace Standard/Comprehensive when the primary deliverable is implementation guidance rather than a pitch / vision doc. Use it when the user emphasizes engineering rigor; use Comprehensive when they emphasize breadth (story, art direction, marketing, live ops).

### Step 3: Apply conditional sections

**For Lean / Standard / Comprehensive tiers**, three sections are mandatory:
- **Pitch + Core Loop + Design Pillars** (the "what and why")
- **Mechanics** (detailed enough that an engineer could start prototyping)
- **Art Direction + UI/UX** (enough that an artist understands the visual target)

**For the Functional Spec tier**, the mandatory backbone is different — Art/UI are reference-only, and the engineering structure replaces them:
- **§0 Document conventions** (the MUST/SHOULD/MAY/TBD legend)
- **§1 Overview** (pillars + references + audience + platform)
- **§2 Core gameplay loop** (pitch + state diagram + win/lose/quit)
- **§3 Core systems spec** (data model + rules + algorithms + state transitions + failure/recovery + edge cases)
- **§10 Edge cases & failure modes** (interruption, save state, network)
- **§12 Open questions** (every TBD with owner + deadline)
- **§13 Acceptance criteria** (objective verification checklist)

All other sections are conditional. Add a section only if you have real input or the genre demands it. Consult `references/conditional-sections.md` for the decision rules per genre (when to add Story, Multiplayer, Monetization, Levels, AI, Audio, Tech, Accessibility, Localization, etc.).

### Step 4: Write the document

Open the chosen template, then fill it in. Follow the writing rules in `references/writing-rules.md` — these cover tone, length per section, how to handle placeholders, how to format reference images, version-history conventions, and common anti-patterns to avoid.

For prose voice and the level of concreteness expected, look at the filled-in examples in `examples/` — `possessable-GDD.md` shows a Lean-tier game-jam doc, and `echoes-of-the-tideborne-GDD.md` shows a Standard-tier indie production doc. Match their tone, density, and use of specific numbers / named systems / TBD blockquotes.

The Functional Spec template has its own embedded writing rules at the top of the file (under "WRITING RULES" in the leading HTML comment). Follow those in addition to `references/writing-rules.md` — they cover MUST/SHOULD/MAY ontology, TypeScript pseudo-code style, "numbers are starting values", and the tracked Open Questions register.

Critically:
- **Never leave the template's placeholder text** (e.g. `{{describe X here}}`, `<Influence #1>`) in the final output. Either fill it with real content from the user, fill it with a clearly-marked TBD with a follow-up question, or remove the line entirely.
- **Remove the leading instruction comment block** from any template that has one (Functional Spec ships with one). It's scaffolding for you, not for the reader.
- **Mark TBDs explicitly.** Use `> **TBD:** [specific question to resolve this]` as a blockquote so they're easy to grep for later. For Functional Spec, also add a row to the §12 Open Questions table with owner + deadline — an untracked TBD becomes a silent decision.
- **Keep prose tight.** A bullet beats a paragraph. A concrete example beats abstract description.

### Step 5: Save and present

Save the final document to the current working directory as `<game-name>-GDD.md` (slugify the game name — lowercase, hyphens, no special chars). If the user has indicated a specific directory (e.g. an existing `docs/` folder in the project), save there instead. If the `present_files` tool is available, use it to surface the file; otherwise just report the absolute path in your reply.

In your reply, give a brief summary: which tier was used, which conditional sections were included, and a short list of TBDs the user should resolve next. Keep this to 4–8 lines — the document itself is the deliverable, not the chat reply.

## Examples of tier selection

**Example 1:**
User: "I'm making a 48-hour game jam game, a tiny puzzle platformer about a ghost who can possess objects. Help me write a quick GDD."
→ **Lean tier.** Time-boxed, solo, "quick" signals one-pager. Skip Story (it's vibes-based), skip Monetization (jam game), skip Tech (engine handles it). Include Pitch, Core Loop, Pillars, Mechanics, Art, UI, Scope/Schedule.

**Example 2:**
User: "We're a 6-person indie studio kicking off a year-long roguelike deckbuilder for Steam. Need a GDD we can hand to the team."
→ **Standard tier.** Multi-person team + year-long timeline + commercial release = needs gameplay, mechanics, art, UI, levels/content, scope, monetization (commercial), maybe brief tech notes. Skip deep AI section (deckbuilders don't need it), skip multiplayer.

**Example 3:**
User: "I'm pitching a AAA open-world RPG to a publisher. I need the full design document."
→ **Comprehensive tier.** Explicit "full" + publisher pitch + AAA = include everything: overview, mechanics, story, world, characters, levels, AI, multiplayer if applicable, UI, audio, tech, art, monetization, accessibility, localization, scope, risks, team, schedule.

**Example 4:**
User: "I'm leading the engineering team for a new mobile match-3 game. I need a functional spec the engineers can implement against — data models, the match-detection algorithm, lives regen rules, ad placements, edge cases. Skip the marketing fluff."
→ **Functional Spec tier.** "Functional spec", "implement against", explicit data-model / algorithm / edge-case request, plus engineering team as primary reader. Use `templates/functional-spec.md`. Include §3 data model + match algorithm pseudo-code with complexity, §6.3 lives rules (MUST NOT decrement on crash/OS-kill/network drop), §7 monetization with anti-frustration rules, §10 edge cases, §13 acceptance criteria. Skip §9 story/narrative, §10.4 anti-cheat (single-player casual → minimal).

## What not to do

- **Don't invent specifics the user didn't give.** If they didn't say what the protagonist's name is, don't make one up — mark it as TBD. (You may suggest options in a TBD note, but don't silently commit to one.)
- **Don't pad with filler.** "This game will be fun and engaging" is not a design pillar. Cut anything that doesn't actually constrain a decision.
- **Don't copy template placeholder text into the final doc.** The templates have things like `<Influence #1>` and `[Two sentences: what is the game]` — these are scaffolding, not output.
- **Don't ignore the conditional rules.** A turn-based singleplayer puzzle game does not need a "Networking" section. Singleplayer narrative games do not need "PvP Balance". Check `references/conditional-sections.md` before adding anything beyond the mandatory three.
- **Don't write a 30-page document for a 48-hour jam game.** Match the document to the project, not to the maximum the template allows.

## Red flags — common rationalizations

If you catch yourself thinking any of these while drafting, stop and apply the counter:

| Temptation | Reality |
|---|---|
| "User didn't name the protagonist — I'll just pick 'Alex' so the doc reads better." | Inventing specifics betrays the user's intent. Use a `> **TBD:**` blockquote; optionally list 2–3 name candidates inside it. |
| "It's only a game jam but I'll write Standard tier to be thorough." | Bloat is the most common failure mode. When in doubt between two tiers, pick the smaller one and offer to expand later. |
| "I'll leave the `[describe X here]` placeholder so the user can fill it in." | Placeholders leak scaffolding into the deliverable. Either fill with real content, replace with an explicit TBD blockquote, or delete the line. |
| "The genre usually has multiplayer/monetization, so I'll add those sections to be safe." | Empty or speculative sections are noise. Only include a section if the user gave real input or `references/conditional-sections.md` requires it for the stated genre. |
| "The user wrote a one-line idea, I'll just expand it into a 5-page GDD." | Density without input = fabrication. Either ask the 3–6 batched questions in Step 1, or stay at Lean tier with TBDs marking the gaps. |
| "Design pillar: 'fun and immersive experience'." | Pillars must constrain a decision. If a pillar can't be used to reject a feature, it's filler — rewrite it as something specific ("readable at a glance, even on a 6" mobile screen"). |
| "Following the letter of the conditional rules feels too rigid here." | Violating the letter is violating the spirit. The rules exist because empty/speculative sections degrade every GDD that includes them. |
