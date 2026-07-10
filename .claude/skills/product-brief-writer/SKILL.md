---
name: product-brief-writer
description: Use when the user wants to write, draft, generate, scaffold, or structure a product brief, product one-pager, product pitch doc, product concept doc, product summary, product vision doc, MVP brief, Amazon-style PR/FAQ, opportunity assessment, or any short strategic document that frames a product before a PRD or detailed spec is written. Also use when the user describes a product idea and asks to "turn it into a brief", "document the concept", "write the pitch", "draft a one-pager", or asks for a short stakeholder-facing doc that captures problem, target user, value proposition, scope, and success metrics. Works for SaaS, mobile apps, web apps, hardware, internal tools, B2B/B2C, consumer, AI features, or any product domain.
---

# Product Brief Writer

A skill for producing **Product Briefs** in Markdown — short strategic documents (1–5 pages) that frame *what we're building, for whom, why, and how we'll know it's working* before any PRD, GDD, or detailed spec is written. Output is a single `.md` file, version-control friendly, readable in any text editor, and renders nicely on GitHub, Notion, Confluence, etc.

## What a product brief is — and is not

A product brief sits **above** detailed implementation docs and **below** company-level vision docs.

| Document | Detail level | Primary question |
|---|---|---|
| Vision doc / strategy memo | Highest abstraction, longest | *Where is the company / product going in 1–5 years?* |
| **Product brief** (this skill) | Concise, 1–5 pages | *Why and what is this product, at a glance?* |
| PRD (Product Requirements Doc) | Detailed, 5–30 pages | *What features, in what shape, with what acceptance criteria?* |
| GDD / Functional Spec / Tech Spec | Very detailed | *How is it built, with what data models and algorithms?* |

**If the user asks for a PRD, full requirements doc, GDD, or engineering spec → this is the wrong skill.** Suggest `gdd-writer` for games or recommend writing a PRD instead. This skill is specifically for the upstream "frame the opportunity" document.

A product brief is **the cheapest way to pressure-test an idea before committing engineering capacity.** Its job is to force clarity on four strategic questions:

1. **Problem** — what real pain or opportunity exists?
2. **Audience** — who specifically has it (not "everyone")?
3. **Value** — why will they care, and why now?
4. **Success** — how will we know it worked?

A brief also names the **shape of the bet** (rough direction of the solution) and the **non-goals** (what we're choosing NOT to do). These are strategic framing, not planning detail — they're in the brief because they constrain the *decision* the reader is about to make, not because they're the implementation plan.

Anything that doesn't serve those questions is filler.

## What belongs in the brief vs. somewhere else

This is the most common failure mode: briefs that drift into PRD or project-plan territory and become slow, stale, and hard to update.

| Topic | Brief | PRD | Project plan / roadmap |
|---|---|---|---|
| Problem, target user, value prop, success metrics | ✅ | recap only | — |
| Why now, market context, competitive position | ✅ | — | — |
| **Shape of the solution** (what *kind* of thing this is, 3–5 bullets) | ✅ | expanded into features | — |
| **Non-goals** (what we are explicitly NOT doing, and why) | ✅ | recap only | — |
| MVP feature list with acceptance criteria | — | ✅ | — |
| Detailed user flows, screens, edge cases | — | ✅ | — |
| Sprints, milestones with dates, gantt | — | — | ✅ |
| Multi-quarter roadmap with dates | — | — | ✅ |
| Timing intent ("must ship before Q3 buying cycle") | ✅ *if it's a constraint on the decision* | — | expanded into dates |
| Phase shape ("Phase 1 = validate, Phase 2 = scale", no dates) | ✅ *comprehensive tier only* | — | expanded into roadmap |

**The test:** if a section's content would be re-written from scratch in the PRD or project plan, it doesn't belong in the brief. Strategic framing belongs here; implementation detail belongs downstream.

## Core philosophy

Three principles drive every choice:

1. **Right-size to the audience.** A solo founder validating an idea needs a one-pager. A team kicking off quarterly planning needs a standard brief. A pitch to leadership / investors / a steering committee needs a comprehensive brief. Pick the tier that matches the actual decision being made.
2. **Concrete beats abstract.** Every section should give the reader something they can challenge — a number, a named persona, a specific pain quote, a measurable success metric. "Delightful UX" is worse than no value prop. "Reduce onboarding time from 45 min to under 10 min for first-time SMB owners" is a value prop.
3. **Conditional sections only.** Don't include a "Monetization" section for an internal tool. Don't include "Competitive Landscape" for a feature inside an existing product. Empty headers are noise that hides the signal.

## Workflow

### Step 1: Gather enough information to write something useful

Before writing, you need to know enough to fill in the **mandatory** sections concretely. If the user's initial message doesn't cover these, ask 3–6 focused questions in a single batched message (one batch beats slow back-and-forth):

**Always need to know:**
- Working name / title (or placeholder)
- **Problem in one sentence** — what pain or opportunity is this addressing?
- **Target user in one sentence** — who specifically (role + context, not demographics)?
- **Why now** — what makes this worth doing right now vs. 6 months ago or later?
- **Scope intent** — is this a feature, an MVP of a new product, a full new product, a strategic initiative? Solo builder, team, or company-level effort?
- **Primary reader of the brief** — yourself, your team, your manager, a steering committee, investors, customers?

**Ask only if relevant:**
- Existing product context — is this a new feature inside an existing product, or a greenfield product?
- Business model / monetization — only if commercial
- Competitive landscape — only if this matters to the reader's decision
- Hard constraints — deadline, budget, headcount, regulatory, integration requirements
- Success metrics — if the user has KPIs in mind already, capture them; otherwise propose 2–3 in the draft as TBD

If the user has already given a rich brief, **skip the interview** and go straight to drafting. Don't ask redundant questions when the answer is already in context.

**Output language.** Match the language the user is writing in. If the user writes in Vietnamese, the brief is in Vietnamese; if English, English. Section headers and template scaffolding translate too — don't ship English headers inside a Vietnamese brief.

### Step 2: Pick the tier

Choose one of three tiers based on the project's scope, the primary reader, and the depth of input you have. Read the corresponding template file from `templates/` — it is the source of truth for structure and section order.

| Tier | When to use | Template file |
|---|---|---|
| **One-pager** | Solo founder, early idea validation, feature pitch inside an existing product, "quick brief" requested, internal-team idea, or input is minimal. Fits on 1 page printed. | `templates/one-pager.md` |
| **Standard** | Default for most cases. New product MVP, cross-team initiative, quarterly planning kickoff, hand-off from product to design/engineering. 2–3 pages. Covers all five mandatory questions plus risks, constraints, timeline. | `templates/standard.md` |
| **Comprehensive** | Pitch to leadership / steering committee / investors / board. New business line, large strategic bet, multi-quarter initiative. 3–5 pages. Adds market context, competitive landscape, GTM, deeper risk and stakeholder analysis. | `templates/comprehensive.md` |

If unsure between two tiers, **pick the smaller one** and offer to expand later. Bloat is the more common failure mode — comprehensive briefs that read as filler kill credibility faster than concise briefs that defer detail.

### Step 3: Apply mandatory and conditional sections

**Mandatory in every tier** (these frame the strategic decision):
- **Problem / Opportunity** — what and why does it matter
- **Target user** — who, with enough specificity to picture them
- **Value proposition** — what changes for them
- **Shape of the solution** — what *kind* of thing this is (3–5 bullets, not a feature list)
- **Non-goals** — what we are explicitly NOT doing, and why
- **Success metrics** — how we'll know

**Conditional — include only if real input exists or the reader needs it:**

| Section | Include when |
|---|---|
| Why now | Comprehensive tier always; Standard if the timing case is non-obvious |
| Market / Audience sizing | Comprehensive tier; Standard if quantified TAM/SAM/SOM is part of the decision |
| Competitive landscape | Comprehensive tier; Standard if positioning vs. competitors is the crux |
| Business model / Monetization | Any tier if commercial; skip for internal tools and free-to-use side projects |
| Go-to-market | Comprehensive tier; rarely in Standard |
| Risks & assumptions | Standard and Comprehensive always; one-pager only if there's a critical risk |
| Constraints | Any tier with hard deadlines, budgets, or regulatory requirements |
| Stakeholders / Team | Standard if cross-functional; Comprehensive always |
| Timing intent | Any tier where timing is a *constraint on the decision* (e.g. "must ship before Q3 buying cycle"). 1–2 sentences, no date table. Detailed milestones belong in the project plan, not the brief. |
| Phase shape | Comprehensive tier only — describes the *strategic* phasing (Phase 1 validate / Phase 2 scale) without dates. The dated roadmap is a separate document. |
| Open questions / TBDs | Any tier with unresolved decisions — track them explicitly so they don't become silent commitments |

Consult `references/section-guide.md` for what each section should contain, with good vs. bad examples for every section.

### Step 4: Write the document

Open the chosen template and fill it in. Follow the writing rules below, plus the per-section guidance in `references/section-guide.md`.

**Writing rules — the things that separate a good brief from a bad one:**

1. **Lead with the problem, not the solution.** The first paragraph should make the reader feel the pain. Solutions feel arbitrary until the problem is real.
2. **Name the user with a verb, not a demographic.** Not "millennials who like fitness" — "people who already exercise 3x/week and want to track progressive overload across multiple gyms". Roles and behaviors beat demographics.
3. **Every metric must be measurable and time-bound.** "Improve engagement" is not a metric. "Increase D7 retention from 12% to 20% within 8 weeks of launch" is.
4. **Shape, not features.** The brief describes the *kind* of solution we're betting on (3–5 bullets), not the feature list. The moment you find yourself writing feature names with acceptance criteria, stop — that's the PRD's job. The shape should make the value prop credible, not enumerate everything that will ship.
5. **Non-goals do half the work.** The thing that separates a brief that ships from a brief that drifts is an explicit list of what we're choosing *not* to do, with a *reason* for each deferral. Anyone can write "what we'll build"; the discipline is naming what we won't.
6. **No project plan inside the brief.** If you're writing milestone dates, sprint plans, or gantt-style timelines, you've crossed into project-plan territory. Use a 1–2 sentence "timing intent" if (and only if) timing is a constraint on the decision. Real dates live in the project plan.
7. **Use TBDs, never invent.** If the user didn't give you a number, a name, a metric, or a stakeholder — use `> **TBD:** [specific question to resolve]` as a blockquote. Inventing specifics betrays the user's intent and creates silent commitments. Briefs are easier to update than to retract.
8. **One concrete example beats a paragraph of abstract description.** A real user story or a real customer quote (or a hypothetical clearly marked as such) anchors the abstract.
9. **Cut anything that doesn't constrain a decision.** If a section can be removed without changing what the team will do, it's filler. Cut it.
10. **Bullets beat paragraphs for scanability — but paragraphs beat bullets for argument.** Use bullets for lists of facts; use prose for the "why now" and the value prop, which are arguments and need to flow.
11. **Never leave template placeholder text** (e.g. `{{describe X}}`, `[fill in here]`) in the final output. Either fill with real content, replace with a TBD blockquote, or delete the line.
12. **Remove any leading instruction comment block** from the template. It's scaffolding for you, not for the reader.

### Step 5: Save and present

Save the final document to the current working directory as `<product-name>-brief.md` (slugify the product name — lowercase, hyphens, no special chars). If the user has indicated a specific directory (e.g. an existing `docs/` folder in the project), save there instead. If the `present_files` tool is available, use it to surface the file; otherwise just report the absolute path in your reply.

In your reply, give a brief summary: which tier was used, which conditional sections were included, and a short list of TBDs the user should resolve next (highest-leverage first). Keep this to 4–8 lines — the document itself is the deliverable, not the chat reply.

## Examples of tier selection

**Example 1:**
User: "Tôi đang nghĩ idea làm app track gym progressive overload, viết giúp tôi một brief ngắn để gửi co-founder review."
→ **One-pager.** Solo founder, early validation, internal audience (co-founder), explicit "ngắn". Include Problem, Target user, Value prop, Shape, Non-goals, Success metric, key risk. Output in Vietnamese.

**Example 2:**
User: "We're kicking off Q2 planning and I need a product brief for a new self-serve onboarding flow we want to ship. Audience is design + eng + PM leadership."
→ **Standard.** Quarterly planning + cross-functional audience + ongoing product = Problem, Target user, Why now, Value prop, Shape of solution, Non-goals, Success metrics, Risks, Constraints. Skip Market sizing (existing product), skip GTM (no launch). Add a 1–2 sentence Timing intent only if Q2 ship is a hard constraint — otherwise no timeline section, let the project plan own that.

**Example 3:**
User: "I'm pitching a new B2B SaaS product line to our board next month. Need a comprehensive brief with market sizing, competitive analysis, and a 12-month roadmap sketch."
→ **Comprehensive.** Board pitch + new business line + explicit "comprehensive" + market/competitive = Problem, Why now, Market sizing, Target segments, Competitive landscape, Value prop, Shape of solution, Non-goals, Business model, GTM, Phase shape (validate → scale, no dates), Success metrics by phase, Risks/assumptions, Stakeholders/team, Open questions. If the user explicitly wants a *dated* 12-month roadmap, deliver that as a *separate roadmap doc* alongside the brief — don't merge them. Mention this trade-off in the reply.

**Example 4:**
User: "Help me write a brief for adding AI-powered search to our existing docs site."
→ **One-pager** (feature inside an existing product, scope is bounded) — *unless* the user signals that this is a larger strategic bet, in which case escalate to Standard. When in doubt, ask: "Is this a feature inside the existing product, or a strategic shift in how the product positions itself?" Then pick accordingly.

## What not to do

- **Don't invent specifics the user didn't give.** No fake metrics, no fake personas, no fake competitive claims. Mark as TBD and optionally suggest 2–3 candidates inside the TBD blockquote.
- **Don't drift into PRD territory.** If you're writing feature lists with acceptance criteria, user flows with edge cases, or detailed UI specs, you've gone too deep — stop and recommend the user write a PRD next. The brief defines the *opportunity and shape*, not the *features*.
- **Don't drift into project-plan territory.** Milestone tables with dates, gantt-style sequencing, sprint planning — these are project-plan content. The brief can carry a 1–2 sentence "timing intent" if timing constrains the decision; everything else belongs in a separate project plan or roadmap doc.
- **Don't merge the brief with a roadmap.** If the user asks for both, deliver them as separate files — briefs stay small and stable, roadmaps change. Merging produces a doc that's stale on both axes.
- **Don't include marketing speak.** "Revolutionary", "best-in-class", "delightful", "seamless", "synergy" — these are red flags. Replace with what the thing actually does or measurably enables.
- **Don't pad with conditional sections.** If the user didn't give you competitive data, don't fabricate a competitive section. Either ask (in the initial batch) or leave it out.
- **Don't bury the lede.** The first 3–5 lines must communicate what this is and why it matters. Reader fatigue is real; assume the steering committee will only read the first paragraph.
- **Don't use English section headers in a Vietnamese brief (or vice versa).** Translate the scaffolding to match the user's language.

## Red flags — common rationalizations

If you catch yourself thinking any of these while drafting, stop and apply the counter:

| Temptation | Reality |
|---|---|
| "User didn't give me a success metric — I'll just put 'increase engagement' so the section isn't empty." | Vague metrics are worse than missing metrics; they create the illusion of measurability. Use a `> **TBD:**` blockquote and propose 2–3 specific candidates ("D7 retention", "tasks completed per active user per week", "conversion from trial to paid"). |
| "User said the product is 'for everyone' — I'll just write that." | "Everyone" means nobody. Push back gently: ask for the *first* user, the wedge persona, the beachhead segment. If the user resists, write the brief but mark "Target user" as `> **TBD: who is the wedge user — the first 100 paying customers will look like ___?**`. |
| "It's only a quick brief, but I'll write Comprehensive tier to be thorough." | Bloat kills brief credibility faster than missing detail. When in doubt between tiers, pick smaller and offer to expand. |
| "I'll leave the `[fill in market size here]` placeholder so the user can fix it later." | Placeholders leak scaffolding into the deliverable and read as careless. Either fill with real content, replace with an explicit TBD blockquote, or delete the line. |
| "The user wrote a one-line idea, I'll just expand it into a 3-page Standard brief." | Density without input = fabrication. Either ask the 3–6 batched questions in Step 1, or stay at One-pager tier with TBDs marking the gaps. |
| "Value prop: 'better, faster, more delightful experience'." | Value props must say *what changes for the user*. If the value prop can't be used to reject a feature ("does this make onboarding measurably shorter? if no, cut it"), it's filler. Rewrite as something specific. |
| "I'll add a Competitive Landscape section because Standard usually has one." | Standard tier marks Competitive as *conditional*. Only include if positioning vs. competitors is part of the reader's decision. Empty/speculative sections degrade the whole document. |
| "Following the letter of the conditional rules feels too rigid here." | Violating the letter is violating the spirit. The rules exist because empty/speculative sections degrade every brief that includes them. |
| "Shape: 'MVP includes 5 core features with acceptance criteria...'" | That's a PRD, not a brief. The Shape section says *what kind of solution this is* in 3–5 bullets — enough to make the value prop credible, not enough to start building. Move feature-level detail to the PRD. |
| "Non-goals: 'we won't build everything at once.'" | Non-goals are specific things people will reflexively ask for that we are deliberately deferring or refusing — each with a *reason*. Vague non-goals do no work. Pattern: "Not doing X *because* Y." |
| "I'll add a Timeline table with milestone dates so the team knows when to ship." | Dated milestones are project-plan content, not brief content. The brief belongs above the project plan. If timing is a *constraint on the go/no-go decision*, use a 1–2 sentence "Timing intent" instead — e.g. "Must reach beta before the Q3 buying cycle starts in Aug." Dates and milestone tables live in the project plan. |
| "The user asked for a 'roadmap inside the brief' — I'll just embed it." | Offer the trade-off: a brief stays small and updateable; a dated roadmap is a separate doc that changes faster. Deliver both side-by-side if needed, but don't merge — merged docs become stale and the brief loses credibility. |

## Reference files

- `references/section-guide.md` — per-section deep guidance: what makes a great problem statement, target user, value prop, success metric, scope, risk, etc. Includes good vs. bad examples for every section. Read this *while drafting* whenever you're unsure how to fill a section concretely.
- `templates/one-pager.md` — the lean template (1 page)
- `templates/standard.md` — the default template (2–3 pages)
- `templates/comprehensive.md` — the strategic / board-level template (3–5 pages)
