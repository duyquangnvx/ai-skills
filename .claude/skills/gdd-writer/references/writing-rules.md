# Writing Rules for GDDs

Rules that make a GDD readable, useful, and survive contact with a team.

---

## 1. Tone

- **Direct and concrete.** "Player has 3 lives" beats "Player will be granted a number of opportunities to retry."
- **No marketing speak.** "Immersive next-gen experience" is content-free. Cut it.
- **Active voice.** "The boss fires three projectiles" not "Three projectiles are fired by the boss."
- **Present tense.** Describe the game as if it exists: "The player moves." Not "The player will move."
- **Plain English.** GDDs are read by artists, programmers, marketers, and external partners. Don't gate-keep with jargon. If a term needs explaining, put it in a Glossary appendix.

---

## 2. Section length targets

These are guides, not rules. Going long is fine when the content earns it.

| Section | Lean | Standard | Comprehensive |
|---|---|---|---|
| Pitch | 2 sentences | 2 sentences + 2 paragraphs | + USPs, hook, business goals |
| Pillars | 3 bullets, 1 line each | 3–4 bullets, 2 lines each | 3–5 bullets with examples |
| Core Loop | 2–3 bullets | nested loops (4 tiers) | nested loops + flow diagram |
| Mechanics | 5–10 bullets total | sub-sections per system | full breakdown per system |
| Art | 1 paragraph + refs | sub-sections + asset list | full art direction document |

---

## 3. Placeholder handling

Templates contain placeholders like `{{GAME_TITLE}}`, `<Influence #1>`, `[describe X here]`. **Never leave any placeholder in the final document.** For each one, do exactly one of these:

1. **Fill with real content** from the user's input.
2. **Replace with a TBD blockquote**:
   ```
   > **TBD:** What is the player's starting weapon?
   ```
3. **Delete the line entirely** if the section/bullet isn't relevant to this game.

TBDs are valuable — they make gaps grep-able and resolvable. Empty placeholders are not.

---

## 4. Lists vs. prose

- Use **prose** for: pitch, design pillars (1–2 lines each), narrative summaries, system descriptions where flow matters.
- Use **bullets** for: player verbs, content inventories, milestones, risks, screen lists.
- Use **tables** for: tabular data (input mappings, resources, hardware specs, milestones with multiple columns).

Don't bullet things that should flow. Don't paragraph things that should scan.

---

## 5. Concreteness ladder

Push every claim toward the most concrete form you can support:

| Less useful | More useful |
|---|---|
| "Fast-paced combat" | "Combat encounters resolve in 10–30 seconds" |
| "Lots of weapons" | "~20 weapons across 4 archetypes" |
| "Beautiful art" | "Hand-painted 2D, ~32-color palette per biome, ref: Hollow Knight + Hyper Light Drifter" |
| "Engaging story" | "5-hour critical path, branching at acts 2 and 3, two endings" |
| "Smart AI" | "Enemies use a 3-state behavior tree: patrol → alert → engage; flee at <20% HP" |

When the user hasn't given you numbers, mark a TBD rather than inventing one or hand-waving.

---

## 6. Reference images / moodboards

Until the user provides actual links, use this format:

```
**Reference images:**
- [TBD: link here] — _Tone reference: cool twilight palette, see Hyper Light Drifter sunset zones_
- [TBD: link here] — _Character silhouette: bulky cloak, see Journey traveler_
- [TBD: link here] — _UI feel: chunky bordered panels, see Into the Breach_
```

This way the doc captures the intent even before the user has uploaded refs, and the TBDs are grep-able.

---

## 7. Versioning

Every GDD starts at version 0.1. Conventions:
- **0.x** — pre-production / draft / not yet feature-locked
- **1.0** — production-ready GDD, all critical sections filled
- **1.x** — production iterations
- **2.x** — major redesign / re-pitch

Include a Version History table in Standard and Comprehensive tiers. Skip it in Lean.

---

## 8. Anti-patterns to avoid

These come up constantly and make GDDs less useful:

### "We'll figure it out later" sections
If a section is genuinely TBD, mark it as TBD with specific questions. Don't write a hollow section full of placeholders pretending to be content.

### Feature list bloat
A GDD is not a wish list. Every feature in the doc is a feature someone has committed to building. If it's optional, it goes in "Out of Scope" or a "Considered" appendix.

### Story tail wagging gameplay dog
A common failure: half the doc is lore and characters, the gameplay sections are thin. Unless the game is narrative-first, gameplay sections should be the largest part of the doc.

### Numbers without sourcing
"Each level takes 8 minutes" — based on what? Playtesting? Designer estimate? Comparable game? Either say "(estimated)" or just give a range.

### Copy-pasted boilerplate
"This game will feature engaging gameplay and beautiful graphics." Cut it. Every sentence should be specific to THIS game.

### Treating the GDD as a contract
Frame the doc as a living document. The first page should imply: this changes when the game changes. A GDD that hasn't been updated in 6 months is a liability.

### Over-formatting
Don't use bold and italic everywhere. Reserve **bold** for section labels and critical terms, _italic_ for occasional emphasis. Overuse = no use.

---

## 9. File naming

Output file: `<slugified-title>-GDD.md`

Slugify rules:
- Lowercase
- Spaces → hyphens
- Strip apostrophes, colons, special chars
- Keep version history in the document itself, not the filename — don't make `game-GDD-v2-final-FINAL.md`

Examples:
- "Hades of the Deep" → `hades-of-the-deep-GDD.md`
- "Project: Echo" → `project-echo-GDD.md`
- "Untitled Roguelike" → `untitled-roguelike-GDD.md`

---

## 10. The smell test

Before saving, scan the document and ask:
1. Could a new team member read this and start working on a piece of it today?
2. Did I invent anything the user didn't tell me?
3. Are any placeholders still unfilled?
4. Are TBDs specific (real questions to answer) rather than vague ("define this later")?
5. Is the document length proportional to the project's scope?

If any answer is "no", revise before saving.
