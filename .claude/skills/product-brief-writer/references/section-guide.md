# Section Guide — How to Fill Each Section Well

This reference is for use *while drafting*. When you're unsure how to fill a section concretely, open the relevant subsection here and use the good/bad examples as a calibration target.

## Table of contents

1. [Pitch / Executive summary](#1-pitch--executive-summary)
2. [Problem / Opportunity](#2-problem--opportunity)
3. [Why now](#3-why-now)
4. [Target user](#4-target-user)
5. [Value proposition](#5-value-proposition)
6. [Shape of the solution](#6-shape-of-the-solution)
7. [Non-goals](#7-non-goals)
8. [Success metrics](#8-success-metrics)
9. [Business model](#9-business-model)
10. [Competitive landscape](#10-competitive-landscape)
11. [Risks & assumptions](#11-risks--assumptions)
12. [Constraints](#12-constraints)
13. [Stakeholders / team](#13-stakeholders--team)
14. [Timing intent](#14-timing-intent)
15. [Phase shape (comprehensive tier only)](#15-phase-shape-comprehensive-tier-only)
16. [Open questions](#16-open-questions)

---

## 1. Pitch / Executive summary

**Job of this section:** make the reader want to keep reading, or — if they stop here — give them the thesis.

**Test it passes if:** a colleague who only reads this paragraph can repeat the thesis back accurately to a third party.

**Bad:**
> "We are building a revolutionary new platform that will transform how teams collaborate, providing best-in-class user experience and unparalleled value."

Why bad: zero specifics. Could be any product. No user, no problem, no measurable change.

**Good:**
> "We're proposing a self-serve onboarding flow for new SMB customers on our platform. Today, 38% of trial signups drop off before activating their first integration — most can't figure out which integration to set up first. The new flow uses 3 setup questions to pick a recommended starter integration and guides them through in under 10 minutes. We expect this to lift trial-to-paid conversion from 11% to 16% within one quarter."

Why good: named user (SMB trialers), specific pain (38% drop-off), specific solution shape (3 questions + guided setup), measurable target (11% → 16%).

---

## 2. Problem / Opportunity

**Job of this section:** make the pain feel real and worth solving.

**Test it passes if:** the reader can describe the user's current workaround in their own words.

**Bad:**
> "Users find our onboarding confusing and difficult to navigate."

Why bad: vague, no evidence, no cost quantified, no specific friction named.

**Good:**
> "First-time SMB owners signing up for a trial face 14 possible integrations on the setup screen. In user testing, 7 of 10 said 'I don't know which one to pick first'. 38% of trial accounts never connect any integration — and accounts that don't connect an integration in week 1 convert to paid at 2%, vs. 19% for accounts that do. Today, users either ask in our Slack community (38 questions last month tagged 'first integration'), search docs (4,200 searches/mo for 'which integration'), or churn silently."

Why good: specific friction (14 integrations, choice paralysis), evidence (user tests, analytics, support data), quantified cost (2% vs. 19% conversion), describes the workaround (Slack, docs, churn).

**Templates for evidence types:**
- Quotes from interviews: "X people we talked to said variants of: '<quote>'"
- Support data: "<N> tickets / month tagged <topic>" or "<N> searches / month for <query>"
- Analytics: "<X%> of users do <action>", "<Y%> drop off at <step>"
- Observed workarounds: "Users currently <thing> in <other tool>, then <next thing>"

If you have no evidence yet, that's a critical TBD — flag it explicitly.

---

## 3. Why now

**Job of this section:** answer "why didn't we / shouldn't we do this 6 months ago, and why not in 6 months?"

**Strong "why now" categories:**
- Technology unlocked something (e.g. "LLM inference is now cheap enough to run on every page load")
- Customer urgency increased (e.g. "post-acquisition, 3 of our top 10 accounts asked for this in QBRs")
- Competitor moved (e.g. "<competitor> launched a similar feature in March; we are at risk of being seen as second-rate")
- Internal capability matured (e.g. "the new auth platform shipped in Q1, so we can finally build this without a 6-month auth rewrite")
- Regulatory deadline (e.g. "EU AI Act compliance requirements kick in Aug 2026")

**Bad:**
> "The market is growing and now is the right time to invest."

**Good:**
> "Two things changed in Q1: (1) we shipped the unified billing layer, which makes per-customer pricing tiers actually possible without a 3-month migration; and (2) our top three logo-prospects in the pipeline cited 'no usage-based pricing' as a blocker in their evaluations. Six months ago, neither was true."

---

## 4. Target user

**Job of this section:** narrow the audience to people we could actually build for and learn from.

**Test it passes if:** the build team could describe one specific real or representative person without re-reading.

**Bad:**
> "Small and medium businesses who want to grow."

Why bad: this is "everyone with a business". No behavior, no context, no specificity.

**Good:**
> "**Wedge user:** Solo or 2–10 person SaaS startups, post-revenue but pre-Series A, that already use Stripe for payments and HubSpot for CRM. They have ad-hoc reporting spreadsheets pulling from both, updated weekly by the founder. Founder spends ~2 hours/week maintaining these. They have tried tools like X and Y but found setup too complex. They will pay for this themselves with no procurement review."

Why good: role (founder), team size, tech stack (Stripe + HubSpot), current behavior (manual spreadsheet), pain frequency (~2hrs/wk), tried alternatives (X, Y), buying power (founder budget, no procurement).

**Pitfall to avoid:** demographic targeting ("millennials", "Gen Z", "high-income earners"). Demographics don't predict product behavior. Use roles, behaviors, contexts, and current workarounds instead.

**The "non-user" list:** for each brief, name 1–2 adjacent groups we are explicitly *not* serving. Sharpens scope. Example: "Not for: enterprise sales orgs with procurement-driven buying — they need SSO, audit logs, custom contracts which are out of scope for v1."

---

## 5. Value proposition

**Job of this section:** name the *outcome change*, not the feature.

**Test it passes if:** the user themselves would agree with the sentence ("yes, that's what I want").

**Bad:**
> "A better, faster, more delightful way to manage your tasks."

Why bad: "better, faster, more delightful" relative to what? Outcome unmeasurable, not specific to any user.

**Good:**
> "Solo SaaS founders close their weekly metrics review in 15 minutes instead of 2 hours, with the same level of confidence they get from their hand-built spreadsheet."

Why good: specific user, measurable shift (2h → 15min), preserves what they value today (confidence), comparable to their current alternative.

**Pattern:** *<user> can now <do desired outcome> in <new way / time / effort>, instead of <current state>.*

**Counter-test:** could this value prop be used to *reject* a feature in the future? If yes, it's a real value prop. If "does this feature serve our value prop?" doesn't answer "yes / no" cleanly, the value prop is too vague.

---

## 6. Shape of the solution

**Job of this section:** make the value prop credible without crossing into PRD territory.

**The line:** the shape section describes the *kind* of thing we're betting on (3–5 bullets, comprehensive tier 4–6). The PRD describes the *thing itself* (features, flows, fields, edge cases). If a reader of the brief would re-read your shape section while writing the PRD and find it useful as *framing*, you got it right. If they'd re-read it and find feature specs they need to copy out, you wrote a PRD inside the brief.

**Bad — feature list disguised as shape:**
> "- Dashboard with chart widgets users can resize and rearrange.
> - Filter bar with date range, metric type, and source filters.
> - Export menu supporting PNG, PDF, and CSV.
> - Settings page with theme, notification, and account preferences."

Why bad: enumerates UI affordances, not the strategic shape. Tells you what to build, not what kind of bet this is. Belongs in the PRD.

**Bad — too abstract to be credible:**
> "- A powerful, intuitive analytics experience for SaaS founders."

Why bad: no shape, no opinionated choice. Could be anything.

**Good:**
> "- A single unified metrics view that auto-pulls from Stripe + HubSpot (no per-metric config) — explicit choice to be opinionated, not configurable.
> - 5 pre-built metric cards matching the top spreadsheet patterns we observed in interviews (MRR, churn, CAC, new logos, pipeline).
> - One-click weekly snapshot designed for the existing 'investor update' habit — captures the view, adds founder commentary, exports as a single image.
> - Founder-only product in v1: no team accounts, no permissions, no multi-currency."

Why good: shape is clear (opinionated, pre-built, snapshot-centric), every bullet ties to either user behavior we observed or a deliberate non-choice. Not a feature spec — a thesis about what kind of product this is.

**Pattern check:** if a bullet starts with "the system shall support …" or describes UI mechanics (resize, rearrange, filter, export options) — pull back. Rewrite as "what kind of thing is this", not "how does it work in detail".

---

## 7. Non-goals

**Non-goals are the strategic core of the brief.** Anyone can write what they'll build; the discipline — and the value to the reader — is naming what we'll deliberately *not* build, with reasons.

**Job of this section:** sharpen the bet by listing the things people will reflexively ask for that we are choosing to defer or refuse.

**Test it passes if:** a senior reviewer reads the non-goals and thinks "good — I was going to ask about exactly that, glad it's been considered."

**Bad — too vague:**
> "Out of scope: enterprise features, advanced customization, integrations beyond MVP."

Why bad: doesn't name the *specific* asks people will have. Doesn't include a reason. Provides no information beyond "we won't build everything".

**Bad — non-goal without a reason:**
> "Out of scope:
> - Multi-user accounts
> - Custom metric definitions
> - Salesforce integration"

Why bad: each item is specific, but with no reasoning the reader can't tell whether you've considered them or just forgotten them.

**Good:**
> "- **Custom metric definitions** — *we will guess wrong; the whole bet is that an opinionated 5-card view is better than a flexible builder. Customization is the v3 conversation, after we know which 5 are actually right.*
> - **Multi-user / team accounts** — *adds auth, permissions, billing-seat complexity. Defer until we have evidence solo founders want to share access (rather than just snapshots).*
> - **Other integrations (Salesforce, QuickBooks, Notion)** — *we'll add these once we know which the wedge user actually wants, not before. Pre-emptively building integrations is the single biggest scope killer for tools like this.*
> - **Slack / email scheduling of snapshots** — *manual sharing first. Automation if usage justifies — current evidence is founders prefer reviewing before sending.*"

Why good: each item is a *specific* ask the team will hear, with a *strategic reason* for the deferral. The reasons distinguish "deliberately deferred" from "haven't thought about it yet".

**Patterns for good non-goal reasons:**
- "Because we'd be guessing — need <evidence X> before committing."
- "Because it conflicts with <core value Y> we just declared."
- "Because it's a 10× build for 1.5× value at our current scale."
- "Because it's a different segment (<segment Z>) — would dilute the wedge."
- "Because it pre-commits us to <expensive infrastructure> we don't yet know we need."

**Anti-pattern to watch for:** non-goals that are really *features deferred to a later phase with a date*. That's roadmap content, not non-goal content. A non-goal is a *strategic refusal*, not a "we'll get to it in Q3". If you find yourself writing "v2 will include …", that's a roadmap line — move it out of the brief or restate it as "not committing to this until <gate>".

---

## 8. Success metrics

**Each metric must answer all four:**
1. What are we measuring? (clear name, ideally already-instrumented)
2. Where are we today? (baseline)
3. Where do we want to be? (target)
4. By when? (timeframe)

**Bad:**
> "Increase engagement and improve retention."

Why bad: not measurable, no baseline, no target, no timeframe.

**Good:**

| Metric | Baseline | Target | Timeframe |
|---|---|---|---|
| % of trial accounts that connect an integration in week 1 | 62% | 80% | 8 weeks post-launch |
| Trial-to-paid conversion | 11% | 16% | 1 quarter post-launch |
| Self-reported NPS for new SMB cohort | TBD (instrument first) | ≥ 30 | 1 quarter post-launch |

**Counter-metric (guardrail) examples:**
- "Increasing signups, but not at the cost of activation rate dropping below 50%."
- "Increasing weekly active users, but not at the cost of support ticket volume rising >20%."
- "Lifting conversion, but not at the cost of refund rate exceeding 5%."

The counter-metric exists because optimization without guardrails leads to gaming the headline metric in ways that hurt the business.

**Common pitfalls:**
- Vanity metrics (page views, signups in isolation) without an activation / outcome metric.
- Metrics tied to inputs (features shipped, lines of code) rather than user outcomes.
- "All up" metrics (total revenue, total users) that obscure whether the new thing is working.

---

## 9. Business model

Include only if commercial.

**Bad:**
> "We'll monetize through subscriptions."

**Good:**
> "**Model:** SaaS subscription, single-user tier.
> **Price hypothesis:** $19 / month or $190 / year. Anchor: roughly half of what we see solo founders paying for their current spreadsheet-replacement stack (Geckoboard + Zapier ≈ $50/mo combined for our target persona).
> **Unit economics (rough):** CAC ~$60 (organic-led growth, content + community), 12-month LTV ~$180 expected, 18-month payback. We'd revisit if CAC exceeds $90.
> **Why this works at scale:** at 5k subscribers we hit ~$1M ARR. Achievable in year 1 if 4% of our existing trial cohort upgrades (today ~10k trials/year)."

Why good: specific price + anchor reasoning, unit economics with thresholds, a viability check.

---

## 10. Competitive landscape

Skip this section unless positioning vs. competitors is part of the reader's decision.

**Bad:**
> "We have many competitors but we're better than all of them."

**Good:**

| Competitor | What they do well | Where they fall short | Our edge |
|---|---|---|---|
| Geckoboard | Polished dashboards, many integrations | Generic — requires manual setup per metric; not SaaS-founder-shaped | Opinionated defaults for the SaaS founder workflow; <2 min setup |
| ChartMogul | Deep Stripe analytics, trusted brand | Stripe-only; expensive ($199/mo) for solo founders | Stripe + HubSpot in one view, 10× cheaper |
| Spreadsheet (status quo) | Free, infinitely flexible, founder is in control | Manual to maintain, error-prone, no historical snapshot | Same view but auto-updating, with the snapshot they already share with investors |

**Always include "status quo" as a competitor.** Most users don't switch from a competitor — they switch from doing it themselves, doing nothing, or living with the pain. Naming the status quo competitor honestly is more important than naming the funded startup competitor.

**Our defensible position:** one paragraph on what keeps us winning. If we have no defensible position, *say so* — that's a strategic finding worth surfacing, not a problem to hide.

---

## 11. Risks & assumptions

**Job of this section:** name what could be wrong, before someone else does.

A risk we surface ourselves with a de-risk plan is credibility. A risk found by the reviewer is a credibility hit.

**Bad:**
> "Risk: users may not adopt the product. Mitigation: marketing."

Why bad: identifies the most obvious failure mode with the least useful mitigation.

**Good:**

| Assumption | Why it might be wrong | Impact if wrong | De-risk plan |
|---|---|---|---|
| Solo SaaS founders will pay $19/mo from their own card | Many use company cards with low limits or expense review even at small scale | Kills LTV math; need higher price or different segment | Price-test landing page with 5 founder communities before any build; minimum 30 LOIs from the wedge persona before commit |
| HubSpot's free-tier API rate limits will support our query volume | We've assumed 1 req/min per account; HubSpot may throttle harder on free plans | Forces all customers onto paid HubSpot tiers, shrinks TAM materially | 2-week spike: build a stub ingestion path against 3 real free-tier HubSpot accounts and measure throttling |
| Founders trust auto-pulled metrics enough to share with investors | They may distrust an opaque calculation and want to see the raw query | Adoption stalls at "interesting tool" rather than "weekly habit" | First 10 design-partner interviews include the question: "would you send this snapshot to your investors as-is?" |

**Pattern for each row:** the specific belief, the specific failure mode, the specific consequence, and the specific *cheap* experiment to test it before committing more capacity.

**Risk ordering:** put the most likely × most damaging risk first. Don't bury the scariest one.

---

## 12. Constraints

Only constraints that actually *constrain* a decision. Skip if there are none.

**Bad:**
> "We have limited resources and need to be efficient."

Every team has limited resources. This is filler.

**Good:**
> - **Deadline:** must be GA by Aug 31 to capture the back-to-work Q3 buying cycle (per Sales).
> - **Headcount:** 1 PM, 2 engineers, 0.5 designer for 12 weeks. No flex.
> - **Technical:** must run on existing single-tenant infra; no new database, no new auth.
> - **Brand:** product must read as "founder-friendly" — no enterprise UI cues, no SSO/compliance language in marketing.

---

## 13. Stakeholders / team

**Use the DACI or RACI pattern.** Be specific by name *or* role.

**Good:**
> - **Accountable (DRI):** <PM name> — owns the brief, the PRD, the launch.
> - **Executive sponsor:** <VP Product> — owns prioritization vs. other Q3 bets.
> - **Build team:** 1 PM, 2 backend engineers, 1 frontend engineer, 0.5 designer (shared with the platform team).
> - **Consulted:** Sales (account exec lead), Support (lead), Data (instrumentation owner).
> - **Informed:** GTM, Customer Success, Finance.

If you're asking for headcount, *say so explicitly*. Don't bury asks in fine print.

---

## 14. Timing intent

**Job of this section:** capture timing if — and only if — it is a *constraint on the decision* the reader is making. Otherwise skip the section entirely.

**The crucial distinction.** A dated milestone table belongs in a project plan, not a brief. The brief sits above the plan; if the plan slips by 2 weeks the brief should not need to be rewritten. So the brief carries *strategic timing* (why this window matters), and the plan carries *operational timing* (when which milestone hits).

**Bad — milestone table inside the brief:**

| Phase | Deliverable | Date |
|---|---|---|
| Discovery | 10 interviews | Apr 30 |
| Prototype | Clickable demo | May 31 |
| MVP build | Closed beta | Jul 31 |
| GA Launch | Public release | Aug 31 |

Why bad: this is project-plan content. It dates the brief (literally — it becomes wrong the moment any milestone slips), and creates two sources of truth for the schedule. The brief now needs to be edited every time the plan changes.

**Bad — vague timing platitudes:**
> "We want to ship soon and iterate quickly."

Why bad: doesn't constrain anything, doesn't tell the reader why the timing matters.

**Good — when timing is a real constraint:**
> "**Timing intent.** Need to validate before the Q3 SMB buying cycle starts in August — that's the window where churn-prevention pitches land best, and we want our value prop in front of trial accounts before they churn. Detailed milestones live in the linked project plan."

Why good: 2 sentences, names the timing constraint, gives the *reason* the constraint exists, and explicitly defers dated milestones to the project plan.

**Good — when timing isn't a constraint:**
> *(no section at all)*

Skipping the section is the right answer if timing isn't part of the go/no-go question.

**The test:** if a reviewer asks "when will this ship?" they're asking about the project plan, not the brief. If a reviewer asks "why does this need to ship now rather than later or sooner?" — that's a brief question, and that's the answer this section gives.

---

## 15. Phase shape (comprehensive tier only)

**Job of this section:** describe the *strategic phasing* of the bet — what we'd validate first, what we'd build, what we'd scale to — without committing to dates.

**The crucial distinction.** A dated roadmap belongs in a separate roadmap document. The brief's phase shape uses **gates** (outcomes that must be true to advance), not dates. This is so the brief survives schedule changes without being rewritten.

**Bad — dated roadmap inside the brief:**

| Phase | Deliverable | Date |
|---|---|---|
| Phase 1 | Validation | Apr–May 2026 |
| Phase 2 | MVP build | Jun–Jul 2026 |
| Phase 3 | GA + Phase 2 features | Aug–Oct 2026 |
| Phase 4 | Scale | Q4 2026 |

Why bad: this is roadmap content. It collapses the moment Phase 1 takes 6 weeks instead of 8.

**Good — gate-based phasing:**

> **Phase 1 — Validate.** Goal: prove SaaS founders will pay $19/mo for an opinionated 5-card view. Approach: 10 founder interviews + landing-page price test + design-partner LOIs. Gate to Phase 2: ≥30 LOIs from the wedge persona, ≥40% landing-page CTR on $19/mo pricing.
>
> **Phase 2 — Build & launch MVP.** Goal: 20 design partners using the product weekly within 8 weeks of beta open. Approach: closed beta with the LOI cohort, ship the 5-card view + Stripe + HubSpot ingestion + weekly snapshot. Gate to Phase 3: ≥15 of the 20 partners use it weekly without prompting; trial-to-paid conversion ≥15% in beta.
>
> **Phase 3 — Scale.** Goal: $1M ARR within 12 months of GA. Approach: organic + community-led growth, no paid acquisition until CAC <$90 is proven. Gate to declare-victory: 5,000 paying subscribers, churn <5%/mo, NPS ≥30.

Why good: each phase has a goal, a shape (kind of activity), and a *gate* — a specific outcome that says "yes, advance" or "no, kill / iterate". No dates means the brief survives schedule slippage; the roadmap doc carries the operational dates.

**Pattern for each phase:** *Goal* (what becomes true) → *Approach* (kind of activity, 2–4 bullets, not a feature list) → *Gate* (the outcome that gates the next phase).

---

## 16. Open questions

**Every TBD that doesn't have an owner and a deadline becomes a silent commitment.** That's how briefs leak — the team builds the thing under an assumed default that no one explicitly chose.

**Bad:**
> "TBD: pricing, integrations, timeline."

**Good:**

| Question | Owner | Decide by |
|---|---|---|
| Do we charge $19/mo or $29/mo at launch? | PM | Apr 30 (after price-test landing page) |
| Do we ship with HubSpot day 1, or Stripe-only? | PM + Design | May 15 (after design-partner interviews) |
| Who owns the in-app activation copy? | Design DRI | May 1 |

Every row: a specific question, a named owner, a deadline by which the answer must exist. If you don't have an owner yet, write `> **TBD: assign owner**` — and that itself becomes the first open question.
