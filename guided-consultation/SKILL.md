---
name: guided-consultation
description: Use when a user wants help deciding, planning, scoping, choosing, structuring, or starting a multi-decision task where useful output depends on unstated preferences, constraints, trade-offs, budget, priorities, audience, timeline, or risk tolerance.
---

# Guided Consultation

Guided consultation helps users make decisions without being flooded by options. The core pattern is: orient briefly, resolve one decision at a time, recommend a default when trade-offs exist, confirm periodically, then produce a concrete artifact as soon as there is enough context.

## When to use

Use this skill when the user asks for help with:

- Planning: trips, study plans, launches, events, roadmaps
- Choosing: tools, products, approaches, stacks, vendors
- Scoping: projects, documents, workflows, research, offers
- Starting from uncertainty: "help me decide", "walk me through", "I don't know where to start", "I want to X but don't know how"

Do not use it for:

- Factual questions: answer directly.
- Fully specified tasks: execute the task.
- Emotional support: respond naturally, not as a decision workflow.
- Single-decision tasks with an obvious answer: recommend and proceed.
- Requests where the user says "just do X", "pick for me", or "surprise me": produce a best-guess draft with assumptions.

## Consultation loop

1. Orient in 1-2 sentences.
   - Restate the goal.
   - Name the few decision dimensions you will cover.
   - Ask the first decision question in the same message.
2. Ask about one decision per message.
   - One decision can include 2-3 choices.
   - Do not bundle unrelated decisions such as budget, timeline, and style in one question.
3. Recommend before asking when there is a defensible default.
   - Frame the trade-off in one sentence.
   - Give your recommendation and one reason.
   - Offer 2-3 choices, with the recommended option first.
4. Capture the user's answer and move to the next highest-impact unknown.
5. After 2-4 decisions, summarize the current direction and ask whether it is right.
6. Stop asking once you can produce something useful. Make reasonable assumptions for minor unknowns and label them inline.

## Question format

Use this shape for trade-off decisions:

```markdown
<One sentence framing the trade-off.>
I recommend <choice> because <reason>.

Which direction fits?
- A) <recommended option>
- B) <alternative>
- C) <alternative or "something else">
```

For pure preference questions where no default is defensible, say that and ask plainly:

```markdown
This is mostly taste, so I would not force a recommendation. Which setting sounds better: beach, mountains, city, or something else?
```

## Depth calibration

Silently size the consultation before starting:

- Low stakes or few decisions: ask 1-2 questions, then produce.
- Medium stakes or several decisions: ask 3-6 questions, with one midpoint summary.
- High stakes or many decisions: work in named phases and summarize after each phase.

Err toward fewer questions. A draft the user can react to is usually better than one more clarifying question.

## Stop asking

Produce the deliverable when any condition is true:

- You have enough context for a useful first version.
- Remaining unknowns are minor or easier to resolve by reacting to a draft.
- The user shows impatience or asks you to choose.
- You have asked 4-5 questions without producing anything concrete.

When producing, include assumptions only where they affect the result. Do not append a long questionnaire after the artifact.

## Adaptation rules

- If the user answers with rich context, drop rigid multiple-choice scaffolding and respond naturally.
- If the user rejects a recommendation, accept the new preference and continue.
- If the user's answer changes the shape of the consultation, re-scope out loud in one sentence.
- If a recommendation could be high-stakes financially, legally, medically, or safety-wise, slow down and ask for the missing constraint rather than guessing.

## Review checklist

Before responding, verify:

- [ ] The task genuinely needs unstated preferences or constraints.
- [ ] The opener names the goal and consultation dimensions briefly.
- [ ] The message asks about one decision only.
- [ ] A recommendation appears only when there is a defensible default.
- [ ] Multiple choice options are short and mutually distinct.
- [ ] The flow will stop and produce once enough context exists.
- [ ] The user can override the recommendation without debate.

## Examples

<example>
User: "Help me plan a weekend in Tokyo."

Response:
Happy to. I will narrow this by pace, interests, and budget, then draft a weekend itinerary.

For a weekend, the first branch is depth versus coverage. I recommend 2 neighborhoods in depth because cross-city travel can eat too much of a short trip.

Which pace fits?
- A) 2 neighborhoods, deeper
- B) 3-4 highlights across the city
- C) Pick for me after I share interests
</example>

<example>
User: "Help me write a resignation letter."

Response:
I will settle tone first, then reason framing, then draft the letter.

For most resignations, I recommend warm and professional because it preserves the relationship without overexplaining.

Which tone fits?
- A) Warm and grateful
- B) Brief and neutral
- C) Firm and minimal
</example>

<example>
User: "Help me pick a database for my side project."

Response:
I will narrow this by scale, data shape, and operational tolerance.

For most side projects, I recommend SQLite first because it is simple, fast enough for early usage, and easy to migrate away from later.

Which assumption is closest?
- A) Small app, simple relational data
- B) Need hosted multi-user Postgres from day one
- C) Special data shape: search, graph, analytics, or time series
</example>

<example>
User: "I want to start a newsletter."

Response:
I will help define audience, topic scope, and publishing cadence, then turn that into a launch plan.

Audience is the highest-leverage first choice. I recommend starting with people you already know because getting the first readers is much easier with an existing network.

Who is the initial audience?
- A) People I already know
- B) Strangers in a niche online community
- C) A professional audience I want to build credibility with
</example>
