<!--
FUNCTIONAL-SPEC TIER — AGENT INSTRUCTIONS
=========================================

PURPOSE
Produce engineer-ready GDDs focused on functional spec (data models,
algorithms, balance, edge cases). NOT a vision doc, pitch deck, or
narrative bible. Use this tier when the deliverable's primary reader
is Engineering / QA / Level Design, and the artifact must be detailed
enough that an engineer can derive types, state machines, and
acceptance tests directly from it.

PREREQUISITES — complete before writing
1. Settle: reference titles, audience, monetization stance, scope
   ceiling. Don't guess these — ask the user or use the Step 1
   batched interview from SKILL.md.
2. Research 2–3 top games in the same sub-genre. Read store reviews —
   pain points there feed §3.6 (recovery), §6.3 (anti-frustration on
   resources), §7.4 (anti-frustration on monetization). Reviews
   surface bugs the original team didn't fix; do not repeat them.
3. Confirm scope (MVP vs full) with user. Default: write for MVP and
   list the rest in §11 Out of Scope.

WRITING RULES (in addition to references/writing-rules.md)
- Functional spec means: data shapes, algorithms, state machines,
  numeric values, edge cases. If a section doesn't supply at least
  one of those, cut or shrink it.
- MUST / SHOULD / MAY / TBD language. No "we will consider".
- All numbers (time, drop rate, price, regen) are STARTING VALUES,
  flag as "needs playtest tune". Never present numbers as final
  unless user explicitly confirmed.
- Pseudo-code in TypeScript-style for shapes and algorithms. Real
  implementation language is engineering's choice.
- Tables for structured data with >3 fields. Prose for rationale only.
- No filler ("in conclusion", "as we have seen"). The reader is an
  engineer, not a stakeholder.
- Length is not a virtue. Cut sections that don't apply to the genre.

GENRE FIT
- Casual / puzzle / match: full template applies.
- RPG / sim: expand §3 (mechanics) and §4 (content); add progression
  curves and gear tiers in §8.
- Multiplayer / competitive: add netcode/sync sub-section in §3;
  expand §10 (desync, rollback); server-side anti-cheat in §10.4.
- Premium / paid: skip §7 (monetization), shrink §6 (currencies).
- Hyper-casual: §7 expands, §3 simplifies, §4 may be procedural-only.

DELIVERABLE HYGIENE
- Remove this comment block before saving the final file.
- Replace every {{PLACEHOLDER}} with real content, a `> **TBD:**`
  blockquote, or delete the line. No scaffolding leaks.
- Every TBD in the body MUST also appear in §12 Open Questions with
  an owner and deadline. Untracked TBDs become silent decisions.
-->

# {{GAME_TITLE}} — GDD

> **Status:** {{Draft v0.1 | Review v0.X | Approved v1.0}}
> **Last updated:** {{YYYY-MM-DD}}
> **Scope:** {{MVP | v1.X | Full}}
> **Target reader:** Engineering, Level Design, QA. Art/UI ref-only.

---

## 0. Document conventions

- **MUST** = required for in-scope release. Cut = block release.
- **SHOULD** = strong default; override-able with documented reason.
- **MAY** = optional; can defer.
- **TBD** = not decided. Owner + deadline tracked in §12.
- All numerical values are **starting values** unless marked "final".
- Pseudo-code is TypeScript-style for spec clarity, not implementation.

---

## 1. Overview

### 1.1 Game pillars

<!-- 3-5 testable pillars. Each = identity-defining property that drives
design tradeoffs. Anti-pattern: vague pillars like "fun", "engaging".
Test: can a feature be cut for failing a pillar? If no, sharpen it. -->

1. **{{Pillar name}}** — {{one sentence; what it implies for design tradeoffs}}
2. **{{Pillar name}}** — {{...}}
3. **{{Pillar name}}** — {{...}}

### 1.2 Reference titles

<!-- Be specific about what each ref contributes. -->

| Game | Role in design |
|---|---|
| {{Title}} | {{e.g., "core loop pacing", "monetization aggressiveness", "UI patterns"}} |
| {{Title}} | {{...}} |

### 1.3 Target audience

- **Primary:** {{demographic + behavioral profile, specific}}
- **Secondary:** {{if applicable, with accessibility implications}}
- **Geo focus:** {{regions, localization scope}}

### 1.4 Platform & technical baseline

- **Platforms:** {{iOS X+ / Android Y+ / PC / Console}}
- **Orientation:** {{portrait | landscape | both}}
- **Network:** {{offline-first | always-online | hybrid — and what each requires}}
- **Save:** {{local | cloud | hybrid — and migration plan}}

---

## 2. Core gameplay loop

### 2.1 One-paragraph pitch

<!-- 3-5 sentences. What does the player do, second-by-second? An engineer
new to the project should grasp the game from this alone. No marketing tone. -->

{{Pitch.}}

### 2.2 Session flow (state diagram)

<!-- ASCII state diagram. Cover all transitions including quit, timeout,
interruption paths. -->

```
[State A] → [State B] → ...
```

### 2.3 Win / lose / quit conditions

| Condition | Trigger | Result |
|---|---|---|
| {{Win}} | {{precise condition}} | {{state change}} |
| {{Fail / lose}} | {{...}} | {{...}} |
| {{Quit}} | {{...}} | {{...}} |

### 2.4 Scoring / rating formula (if applicable)

```
{{formula in pseudo-code, with thresholds}}
```

<!-- Thresholds are starting values; verify achievable by skilled play
before locking. Level designer / QA must self-pass to validate. -->

---

## 3. Core systems spec

> **Engine spec.** This section directly informs code structure and is
> the largest in a functional-spec GDD.

### 3.1 Data model

<!-- All core types. Cover: entities, state enums, key relationships,
nullability, bounds. -->

```typescript
type {{CoreEntity}} = {
  // {{fields}}
};
```

### 3.2 Coordinate / world system

<!-- Units, origin, bounds. Include any virtual or extended space (e.g.,
off-screen pathfinding, infinite scroll, paged worlds). -->

{{Spec.}}

### 3.3 Core rule(s)

<!-- The defining mechanic(s). For each:
1. Plain-language definition
2. Numbered list of formal conditions (all of them)
3. Cases that look like they satisfy the rule but don't (negative examples) -->

**{{Rule name}}**

Plain language: {{...}}

Formal conditions:
1. {{condition}}
2. {{condition}}

Negative examples (look correct but aren't): {{...}}

### 3.4 Algorithm specs

<!-- For each non-trivial algorithm: approach, pseudo-code, complexity,
edge cases. Don't hand-wave with algorithm names — show the specific
variant for THIS game. -->

```typescript
function {{algorithmName}}(/* ... */) {
  // {{...}}
}
```

**Complexity:** {{O(...)}}
**Edge cases:** {{enumerate}}

### 3.5 State transitions

<!-- If entities have states, spec all valid transitions. Use a transition
table or state diagram. List forbidden transitions explicitly — they
become assertions in code. -->

| From | To | Trigger | Forbidden? |
|---|---|---|---|
| {{state}} | {{state}} | {{event}} | no |

### 3.6 Failure / recovery states

<!-- Deadlock detection, soft-lock prevention, invalid-state recovery.
For each: detection trigger, recovery action, cost to player.
Default rule: recovery from system-caused failure costs the player ZERO.
This is frequently violated. -->

| Failure | Detection | Recovery | Cost to player |
|---|---|---|---|
| {{...}} | {{trigger}} | {{action}} | 0 |

### 3.7 Edge cases

<!-- "What if X happens during Y" cases. Each unspecified row is a real bug. -->

| Edge case | Spec |
|---|---|
| {{e.g., simultaneous input during animation}} | {{behavior}} |

---

## 4. Content structure

<!-- Adapt naming: levels / missions / zones / chapters / runs / quests. -->

### 4.1 Content data schema

```typescript
type {{ContentUnit}} = {
  id: number;
  // {{...}}
};
```

### 4.2 Difficulty / size tiers

| Tier | Parameters | Used in {{range}} |
|---|---|---|
| {{Easy}} | {{...}} | {{1–10}} |

### 4.3 Difficulty curve

<!-- Avoid linear curves. Plateau-then-jump retains better. Document
where jumps happen and why. Anti-frustration rule: difficulty SHOULD
NOT increase immediately after a fail. -->

{{Description + chart sketch if useful.}}

### 4.4 Balance formulas

```
{{formula}}
```

<!-- Mark all values as starting; needs playtest. -->

### 4.5 Content generation / authoring

<!-- Procedural rules OR hand-crafting workflow.
- Procedural: MUST guarantee solvability/completeness. Spec the algorithm.
- Hand-crafted: MUST have an auto-validation gate (auto-solver, balance
  checker). Spec the gate. -->

{{Approach + gate.}}

---

## 5. Player tools (boosters / abilities / items / spells)

### 5.X Per-tool spec

<!-- One subsection per tool. Each MUST cover:
- Effect (precise; no "helps the player")
- Activation flow (taps, gestures, targeting)
- Cooldown / charges / limits
- Cost (free count per unit, soft currency, hard currency, ad alternative)
- Edge cases — at minimum the no-op case (refund or not?)
-->

#### 5.X.1 {{Tool name}}

**Effect:** {{precise}}
**Activation:** {{flow}}
**Limits:** {{cooldown / charges / per-unit cap}}
**Cost:** {{free count, soft-currency price, hard-currency price, ad alternative}}
**Edge cases:** {{enumerate; minimum the no-op case}}

### 5.Z Tool economy summary

| Tool | Free/{{unit}} | Soft price | Hard price | Rewarded ad? |
|---|---|---|---|---|

---

## 6. Currencies & resources

<!-- Skip if premium / paid game. -->

### 6.1 Soft currency

- **Earned via:** {{enumerate sources}}
- **Spent on:** {{enumerate sinks}}
- **Cap:** {{if any}}

### 6.2 Hard currency

- **Earned via:** {{small in-game amounts; primarily IAP-driven}}
- **Spent on:** {{enumerate; this defines IAP value perception}}
- **Starting balance:** {{welcome bonus, if any}}

### 6.3 Lives / energy / stamina (if used)

- **Cap, regen rate, refill options.**
- **MUST NOT decrement on:** {{enumerate scenarios that are not the player's fault — crash, OS-kill, network drop, system-forced state change}}

| Scenario | Resource action |
|---|---|
| {{OS-killed mid-level}} | {{no decrement}} |

---

## 7. Monetization

<!-- Skip if premium / paid game. -->

### 7.1 Ads placement matrix

<!-- Every placement, including the slots intentionally NOT used (those
are commitments too). -->

| Placement | Type | Frequency | Cap | Skip-able |
|---|---|---|---|---|

### 7.2 Rewarded video opportunities

| Trigger | Reward | Cooldown | Daily limit |
|---|---|---|---|

### 7.3 IAP catalog

| SKU | Price (USD ref) | Contents | MVP? |
|---|---|---|---|

### 7.4 Anti-frustration rules (MUST / MUST NOT)

<!-- Players never see this section, but it determines whether they
uninstall. Common rules:
- MUST NOT show ads during active gameplay
- MUST NOT charge resources for system-caused state changes
- MUST NOT show interstitial within X hours of an IAP
- MUST honor "remove ads" purchase across all surfaces
- SHOULD reduce ad cadence for high-retention users -->

- **MUST** {{commitment}}
- **MUST NOT** {{prohibition}}

---

## 8. Meta progression

### 8.1 Progression structure

<!-- Map / tree / linear / open. Unlock conditions. -->

{{Spec.}}

### 8.2 Daily systems

<!-- Check-in, daily challenge, daily quest. Reset timing — local time vs
server time matters; pick one and document. -->

{{Spec + reset timezone decision.}}

### 8.3 Achievements

<!-- 10-20 achievements is plenty for MVP. Defer 100+ achievement bloat. -->

| Achievement | Condition | Reward |
|---|---|---|

### 8.X Events / seasons / battle pass (optional)

<!-- Default: defer past MVP. If included, spec lifecycle and reset rules. -->

---

## 9. UI flow

### 9.1 Screen map

<!-- ASCII tree showing all screens and primary navigation. -->

```
{{MainMenu}}
├── {{Play}}
│   └── ...
└── {{Settings}}
```

### 9.2 In-game HUD

<!-- Top / center / bottom regions. Enumerate elements per region. Note
minimum touch sizes and font sizes if accessibility is in scope. -->

| Region | Elements |
|---|---|
| Top | {{...}} |
| Center | {{...}} |
| Bottom | {{...}} |

### 9.3 Result / outcome screens

<!-- Win, fail, abandon. Each: layout, primary CTA, secondary options.
Default-focused button matters. -->

{{Spec each outcome screen.}}

### 9.4 Accessibility (if in scope)

<!-- Touch sizes, contrast modes, font scaling, color-blind support,
reduced-motion option. Senior-targeted games: larger minimums. -->

{{Spec or "out of scope for MVP".}}

---

## 10. Edge cases & failure modes

### 10.1 Mid-session interruption

| Event | Behavior |
|---|---|
| {{home button}} | {{save + resume}} |
| {{incoming call}} | {{...}} |
| {{OS-killed app}} | {{...}} |
| {{crash}} | {{...}} |
| {{network drop}} | {{...}} |

### 10.2 Save state spec

```typescript
type SavedSession = {
  version: number;  // schema version, MUST exist for migration
  // {{...}}
};
```

<!-- Trigger events for save: enumerate. Storage location: spec. -->

**Save triggers:** {{enumerate}}
**Storage:** {{location, encryption, size cap}}

### 10.3 Network handling

<!-- For each network-dependent feature: offline behavior. Hide silently?
Disable with state? Show retry? -->

| Feature | Offline behavior |
|---|---|
| {{...}} | {{...}} |

### 10.4 Anti-cheat

<!-- Right-size to game type. Single-player casual: minimal (monotonic
clock, hash check, encrypted prefs). Competitive / leaderboard:
server-side validation. Don't over-invest in MVP. -->

{{Right-sized spec.}}

---

## 11. Out of scope

<!-- Explicit list of "not in this version". Group by deferred milestone.
Without this list, scope creep is silent and unowned. -->

- {{Feature}} (planned: {{version | future}})
- {{Feature}} (planned: {{...}})

---

## 12. Open questions

<!-- Every TBD from above gets a row. Without owner + deadline, TBDs
become silent decisions made by the implementer. Don't allow that. -->

| # | Question | Owner | Deadline |
|---|---|---|---|
| Q1 | {{question}} | {{role/person}} | {{milestone}} |
| Q2 | {{...}} | {{...}} | {{...}} |

---

## 13. Acceptance criteria

<!-- Concrete verification checklist. Each item must be objectively
testable (no "feels right"). -->

**Gameplay:**
- [ ] {{verifiable item}}
- [ ] {{...}}

**Technical:**
- [ ] FPS target on reference device
- [ ] App / build size cap
- [ ] Cold start time
- [ ] Crash-free rate target
- [ ] Save/restore correct on interruption scenarios

**Monetization (if applicable):**
- [ ] All IAP SKUs configured and sandbox-tested
- [ ] Restore Purchase works
- [ ] Ad SDK integrated; fill rate verified in target geo
- [ ] "Remove ads" fully removes all banner + interstitial surfaces

**Compliance:**
- [ ] Privacy policy + ToS URLs live
- [ ] Age rating set
- [ ] Region-specific consent (GDPR / ATT / etc.) if applicable
- [ ] No unlicensed third-party assets

---

*End of GDD.*
