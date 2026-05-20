<!--
WRITING RULES FOR THE COMPREHENSIVE TEMPLATE — REMOVE THIS BLOCK BEFORE SHIPPING

- Target length: 3–5 printed pages (~1,500–3,000 words). If you're over 3,000, you are writing a strategy memo, not a brief — cut.
- Mandatory sections: Executive summary, Problem, Why now, Market & target user, Value proposition, Shape of solution, Non-goals, Success metrics, Business model, Competitive landscape, Risks, Stakeholders, Phase shape.
- The Phase shape section describes the *strategic* phasing (validate → build → scale → expand) WITHOUT dates. The dated roadmap is a separate document — if the user asks for both, deliver them as separate files.
- DO NOT include feature lists with acceptance criteria. The Shape section and the Phase shape section describe the *kind* of solution and the *strategic* phasing — feature-level detail belongs in the PRD.
- DO NOT include milestone tables with dates or sprint plans. Phase gates without dates are OK ("Phase 1 ends when we have 10 paying customers" is a strategic gate; "Phase 1 ends Apr 30" is a project-plan milestone — keep it out).
- Use TBD blockquotes for anything the user did not provide: `> **TBD:** [question]`
- Translate every header and label below to match the user's language.
- This template is for board-level / steering-committee / investor-facing briefs. The Executive Summary at the top must be self-contained — assume some readers will only read it.
- After filling in, delete this entire comment block.
-->

# <Product name> — Product Brief

| | |
|---|---|
| **Owner** | <name> |
| **Status** | Draft v0.1 |
| **Date** | <YYYY-MM-DD> |
| **Audience** | <e.g. Steering committee, Board, Leadership team> |
| **Decision requested** | <what you want from this audience — go/no-go, funding, headcount, etc.> |

## Executive summary

> 5–8 sentences. Stands alone. Covers: what we're proposing, who it's for, why now, what the opportunity is sized at, what kind of solution we'll build (shape, not features), what success looks like, and what we need from this audience.

---

## 1. Problem / Opportunity

What pain or opportunity exists today, in concrete terms.

- **The pain:** describe the user's current friction.
- **Cost of doing nothing:** quantify — lost time, lost revenue, churn, opportunity cost, competitive risk.
- **Evidence:** interviews, support data, analytics, observed workarounds. If the case is partly hypothesized, mark TBD with the validation plan.

## 2. Why now

What has changed that makes this the right moment? Be specific.

- **Technology shift:** <e.g. LLMs cheap enough, mobile bandwidth, regulation>
- **Market shift:** <e.g. competitor pulled out, category accelerating, customer urgency rising>
- **Internal capability:** <e.g. new platform, new data, new team>
- **Strategic alignment:** <how this connects to broader company strategy>

## 3. Market & target user

### 3.1 Market sizing *(if relevant to the decision)*

- **TAM** (total addressable market): <number + how derived> or `> **TBD**`
- **SAM** (serviceable addressable): <number + how derived> or `> **TBD**`
- **SOM** (serviceable obtainable, realistic 3-year): <number + how derived> or `> **TBD**`
- Source: <data source, methodology>. If bottoms-up, show the calculation.

### 3.2 Target segments

- **Wedge segment (year 1):** detailed persona — role, behavior, current workaround, willingness to pay (if commercial).
- **Adjacent segments (later):** who we expand to next, and what we'd need to add to serve them.
- **Non-target segments:** who this is explicitly *not* for, and why we're choosing to ignore them.

## 4. Competitive landscape

Who solves this today? What do they get right, what do they miss?

| Competitor | What they do well | Where they fall short | Our edge |
|---|---|---|---|
| <Competitor 1> | <strength> | <weakness> | <differentiator> |
| <Competitor 2> | <strength> | <weakness> | <differentiator> |
| Status quo (do nothing / workaround) | <why people stay> | <what makes them switch> | <our pull> |

**Our defensible position:** one paragraph on why we win — and stay winning — vs. each of these. If we don't have a defensible position, say so explicitly. That is itself a strategic finding.

## 5. Value proposition

What changes for the target user when they have this.

- **Headline value (to the wedge user):** one sentence the user would agree with.
- **Headline value (to the business):** one sentence on how this creates company value.
- **Before / after:** the most measurable single shift this enables for the user.

## 6. Shape of the solution

The *kind* of solution we're betting on — enough to make the value prop credible. Not a feature list.

- 4–6 bullets describing the defining mechanics, surfaces, or opinionated choices.
- Reference any prior art, prototypes, sketches, or competitor analogs.
- Detailed feature-level scope, user flows, and acceptance criteria belong in the downstream PRD.

*Test: if you find yourself writing "the system shall ..." or enumerating fields/screens/edge cases, you've drifted into PRD territory. Pull back to shape.*

## 7. Non-goals

Specific things that people will reflexively ask for that we are choosing NOT to pursue — each with a reason. This is half the strategic value of the brief.

- <Non-goal 1> — *because <reason / what we'd need to know first / strategic priority>*
- <Non-goal 2> — *because <reason>*
- <Non-goal 3> — *because <reason>*

## 8. Business model *(conditional — include if commercial)*

- **Pricing model:** subscription, usage-based, one-time, free + paid tier, marketplace cut, etc.
- **Price point hypothesis:** <number + reasoning>
- **Unit economics:** CAC, LTV, gross margin assumptions. Mark TBD if not yet known and call out which are highest-leverage to validate.
- **Revenue projection (rough):** 3 scenarios — conservative / expected / optimistic. Show assumptions, not just numbers.

## 9. Go-to-market *(conditional — include for new products or major launches)*

- **Launch motion:** product-led, sales-led, channel partner, community, paid acquisition, etc.
- **First-100 plan:** how we get the first 100 users / customers / accounts.
- **Distribution channels:** primary and secondary.
- **Positioning statement:** "For <target user>, who <has problem>, <product> is <category> that <key benefit>, unlike <competitor or alternative>, which <weakness>."

## 10. Phase shape

The *strategic* phasing of the bet — not a dated roadmap. Each phase has a **gate** (an outcome that must be true before the next phase begins), not a date.

### 10.1 Phase 1 — Validate

- **Goal:** what we're trying to learn or prove.
- **Approach (shape):** 2–4 bullets on the kind of activity (research, prototype, design partners), not a feature list.
- **Gate to Phase 2:** the specific outcome that says "yes, keep going" (e.g. "10 design partners using it weekly", "trial-to-paid uplift ≥ X%", "5 LOIs from the wedge segment").

### 10.2 Phase 2 — Build & launch

- **Goal:** what becomes true at the end of this phase.
- **Approach (shape):** 2–4 bullets on the kind of solution we'd ship.
- **Gate to Phase 3:** the outcome that says "ready to scale".

### 10.3 Phase 3 — Scale / expand

- **Goal:** what scale or expansion looks like.
- **Approach (shape):** 2–4 bullets.
- **Gate:** when we'd declare this bet won (or kill it).

*This is intentionally undated. A dated roadmap belongs in a separate document that can change without rewriting the brief.*

## 11. Success metrics

Each metric: measurable, time-bound (relative to phase, not calendar), tied to the phase gate.

### 11.1 Phase 1 (validate) metrics

| Metric | Baseline | Target | When measured |
|---|---|---|---|
| <Metric> | <baseline> | <target> | <e.g. end of validation> |
| <Metric> | <baseline> | <target> | <when> |

### 11.2 Phase 2+ (scale) metrics

| Metric | Baseline | Target | When measured |
|---|---|---|---|
| <Metric> | <baseline> | <target> | <when> |

**Counter-metrics (guardrails):** what we watch to make sure we aren't winning on the headline by hurting trust, retention, support load, or brand.

## 12. Risks & assumptions

Ordered by likelihood × impact. Surface the assumptions that, if wrong, change the answer.

| Assumption | Why it might be wrong | Impact if wrong | De-risk plan |
|---|---|---|---|
| <Top assumption> | <failure mode> | <consequence> | <experiment / interview / prototype> |
| <Assumption 2> | <failure mode> | <consequence> | <de-risk plan> |
| <Assumption 3> | <failure mode> | <consequence> | <de-risk plan> |

## 13. Constraints

- **Budget / headcount:** <approved or requested>
- **Technical:** <platform, integration, performance>
- **Regulatory / compliance:** <if any>
- **Strategic:** <conflicts with existing roadmap, brand, partnerships>

## 14. Timing intent *(conditional)*

1–2 sentences only, and only if timing constrains the strategic decision — e.g. "Need to be in market before competitor X's Aug launch" or "Tied to EU AI Act Aug 2026 deadline". This is *not* a milestone table; dated milestones belong in the separate project plan / roadmap.

## 15. Stakeholders & team

- **Accountable (DRI):** <name / role>
- **Executive sponsor:** <name / role>
- **Build team:** <roles + counts>
- **Consulted:** <names / roles>
- **Informed:** <names / roles>

If headcount is being requested, list the asks explicitly here.

## 16. Open questions

Decisions explicitly deferred. Each has an owner and a deadline — untracked TBDs become silent commitments.

| Question | Owner | Decide by |
|---|---|---|
| <Open question 1> | <name> | <date> |
| <Open question 2> | <name> | <date> |

## 17. Appendix *(optional)*

Supporting material — interview notes, data snapshots, competitive teardowns, prototype links, prior strategy docs. Keep the main body short by pushing detail here.

---

*This brief defines the strategic opportunity, shape, and phasing. Downstream documents:*
- *PRD — feature-level spec for the build phase*
- *Project plan / roadmap — dated milestones, sprint sequencing, resource allocation*
- *Detailed financial model — full unit economics & scenarios*
