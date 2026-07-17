<!--
WRITING RULES FOR THE STANDARD TEMPLATE — REMOVE THIS BLOCK BEFORE SHIPPING

- Target length: 2–3 printed pages (~800–1,500 words). If you're over 1,500, you are drifting into PRD territory — cut.
- Mandatory sections: Pitch, Problem, Target user, Value proposition, Shape of solution, Non-goals, Success metrics, Risks & assumptions.
- Conditional sections (include only with real input or clear reader need): Why now, Business model, Constraints, Stakeholders, Timing intent (1–2 sentences only), Open questions.
- DO NOT include a dated milestone table, sprint plan, or gantt. Those belong in the project plan, not the brief. If timing constrains the decision, use a 1–2 sentence "Timing intent" section.
- DO NOT write feature lists with acceptance criteria. The Shape section is 3–5 bullets describing the *kind* of solution — anything deeper belongs in the PRD.
- Use TBD blockquotes for anything the user did not provide: `> **TBD:** [question]`
- Translate every header and label below to match the user's language.
- Replace placeholders like `<...>` and `{{...}}` with real content or delete the line.
- After filling in, delete this entire comment block.
-->

# <Product name> — Product Brief

| | |
|---|---|
| **Owner** | <name> |
| **Status** | Draft v0.1 |
| **Date** | <YYYY-MM-DD> |
| **Reviewers** | <names or roles> |

## 1. Pitch

> 3–5 sentences. What is it, who is it for, what changes for them, and why now. If the reader stops here, they should still know the core thesis.

## 2. Problem / Opportunity

What pain or opportunity exists today, and why it's worth solving now.

- **The pain:** describe the user's current friction concretely. What do they do today? What goes wrong?
- **The cost of doing nothing:** quantify if possible — lost time, lost revenue, churn risk, opportunity cost.
- **What we've heard:** evidence — interview quotes, support tickets, analytics, observed workarounds. If we have no evidence yet, mark as `> **TBD:** how we'll validate this is a real pain (n interviews, support ticket review, analytics dive).`

## 3. Why now *(optional)*

What has changed in the world, the company, or the user base that makes this the right moment? Tech enabler? New regulation? Competitor move? Customer signal? Internal capability unlocked?

Skip this section if the timing case is obvious from the Problem section.

## 4. Target user

Who specifically is this for, in enough detail that the team can picture them.

- **Wedge user (primary persona):** one paragraph describing the *first* user — role, behavior, context, current workaround.
- **Secondary segments (optional):** other groups who may benefit later, but are NOT the launch target.
- **Non-users — who this is explicitly NOT for:** name 1–2 adjacent groups we are *not* trying to serve. This sharpens scope.

## 5. Value proposition

What changes for the target user when they have this. Frame as outcomes, not features.

- **Headline value:** one sentence the user themselves would agree with.
- **Before / after:** the most measurable single shift this enables. Example: "First-time SMB owners complete onboarding in <10 minutes (today: ~45 minutes, 38% drop-off)."
- **Why us / why now (optional):** what makes us the right team / company / moment to deliver this.

## 6. Shape of the solution

The *kind* of solution we're betting on — enough to make the value prop credible. **Not a feature list.**

- 3–5 bullets describing the defining mechanics, surfaces, or opinionated choices of the solution.
- One reference to prior art / prototype / sketch if available.
- The detailed feature-level scope, user flows, and acceptance criteria belong in the downstream PRD — this section intentionally stops short of that.

*Test: if a bullet reads "the system shall support X with options A/B/C", you've drifted into PRD territory. Rewrite to describe the shape, not the spec.*

## 7. Non-goals

The things people will reflexively ask for that we are choosing to defer or refuse — each with a *reason*. This is half the value of the brief: anyone can list what we'll build; the discipline is naming what we won't.

- <Non-goal 1> — *because <reason / what we'd need to validate first / why it's lower priority>*
- <Non-goal 2> — *because <reason>*
- <Non-goal 3> — *because <reason>*

## 8. Success metrics

How we'll know if this is working. Each metric must be measurable, time-bound, and tied to the value prop.

| Metric | Baseline | Target | Timeframe |
|---|---|---|---|
| <Metric 1> | <today's number or TBD> | <target> | <e.g. 8 weeks post-launch> |
| <Metric 2> | <today's number or TBD> | <target> | <timeframe> |
| <Metric 3> | <today's number or TBD> | <target> | <timeframe> |

**Counter-metric (guardrail):** what we'll watch to make sure we're not winning on the headline metric by hurting something else (e.g. growing signups but tanking activation, growing engagement but tanking trust scores).

## 9. Business model / Monetization *(conditional — include if commercial)*

- How this makes money (or doesn't, for a feature that supports another revenue path).
- Pricing hypothesis if applicable.
- Unit economics if known. Mark TBD otherwise.

## 10. Risks & assumptions

The things we believe that, if wrong, change the answer. Order from most-likely-to-kill-the-project to least.

| Assumption | Why it might be wrong | How we'll de-risk it |
|---|---|---|
| <Assumption 1> | <failure mode> | <experiment, interview, prototype, etc.> |
| <Assumption 2> | <failure mode> | <de-risk plan> |
| <Assumption 3> | <failure mode> | <de-risk plan> |

## 11. Constraints *(conditional)*

Hard limits the team must work within:
- **Budget / headcount:** <if any>
- **Technical:** <integration, platform, performance>
- **Regulatory / compliance:** <if any>
- **Other:** <e.g. existing brand, contractual obligations>

*Note: deadlines are usually a "Timing intent" issue, not a constraint — put them in §12 below if they constrain the go/no-go decision.*

## 12. Timing intent *(conditional)*

1–2 sentences only, and only if timing is a *constraint on the decision* — e.g. "Need to validate before Q3 buying cycle starts in August" or "Must ship before the Aug 2026 EU AI Act deadline."

**This section does NOT carry milestone tables, sprint plans, or gantts.** Dated milestones, phase dates, and project sequencing belong in a separate project plan or roadmap doc. The brief stays small precisely so it can be updated independently of the plan.

## 13. Stakeholders & team *(conditional — include if cross-functional)*

- **Accountable (DRI):** <name / role>
- **Responsible (build team):** <names / roles>
- **Consulted:** <names / roles>
- **Informed:** <names / roles>

## 14. Open questions

Decisions not yet made. Each one needs an owner and a deadline — an untracked TBD becomes a silent commitment.

| Question | Owner | Decide by |
|---|---|---|
| <Open question 1> | <name> | <date> |
| <Open question 2> | <name> | <date> |

---

*Next documents: PRD (feature-level spec) and project plan (dated milestones). This brief defines the opportunity and shape; downstream docs define the build.*
