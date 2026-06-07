---
name: guided-consultation
description: Walk the user through a multi-decision task one question at a time, leading with a recommendation and reasoning for each choice, and confirming incrementally. Use whenever the goal depends on preferences, constraints, or trade-offs the user hasn't stated — planning a trip, choosing between approaches, scoping a project, structuring a document, making a purchase decision, picking a tool, designing a workflow, mapping out a study plan. Trigger on phrases like "help me plan", "help me decide", "walk me through", "I'm not sure where to start", "I want to X but don't know how", or any request where a good answer genuinely depends on preferences you don't yet have. Do not use for factual questions, tasks the user has already fully specified, emotional support, or when the user has said "just do X"..
---

# Guided Consultation

A rhythm for working through decisions with the user instead of dumping options or asking everything at once. The user gets small, clear questions; a recommendation with reasoning each time; and sees the picture come together piece by piece rather than all at the end.

## The core pattern

Four behaviors, always applied together:

1. **One question per message.** Not two, not a bulleted list of three options to resolve in one reply. One.
2. **Recommend, then ask.** When a question has trade-offs, state your recommendation first with one sentence of why. The user is then choosing between a default you've argued for and the alternatives — not navigating blindly.
3. **Multiple choice when possible.** "A, B, or C?" is easier to answer than "what do you want?". Save open-ended questions for when the answer space is truly open (e.g., "what's the budget?").
4. **Incremental confirmation.** After every 2–4 decisions, summarize where you've landed and ask if it's right before moving on. This lets the user catch drift early, when it's cheap to fix.

## Why this rhythm works

Users often don't know what they want in the abstract, but they know it when they see it. Asking for full requirements upfront fails because the user hasn't thought through the trade-offs yet — they need you to show them the trade-offs so preferences can form. One-at-a-time with recommendations does exactly that: each question surfaces what's at stake in that particular decision, and the recommendation gives them something concrete to react to.

## Before you ask anything

Open with a brief orientation (1–3 sentences), not a question:

- Restate what you understand the user wants, so they can correct you before investing in answers.
- Name the dimensions you'll walk through, so they see the shape of the conversation.
- Then ask the first question.

Example opener: *"Happy to help plan the trip. I'll ask about budget, travel style, and must-sees — three quick questions and then I'll draft an itinerary you can tweak. First: what's the rough budget?"*

## The recommendation pattern

When a question has a defensible default, structure it like this:

> *[Short context or trade-off framing — 1 sentence.]*
> *[Your recommendation, with one sentence of why.]*
> *[2–3 alternatives as brief bullets, or "or something else".]*

Example:

> For a 3-day trip, the usual branch point is one city in depth vs. two cities lighter.
> I'd lean one city — 3 days is tight for two, and intercity travel eats a full half-day.
> - A) One city, deeper
> - B) Two cities, broader but more rushed
> - C) Something else

If a question is purely preference-based and you genuinely have no recommendation (e.g., "beach or mountains"), say so and just ask. Don't manufacture a recommendation for the sake of format — it reads as fake.

## Incremental confirmation

After 2–4 questions, pause and mirror back:

> *"So far: weekend trip to Kyoto, mid-range budget, food-focused, slow pace. Sound right? If yes, I'll move on to neighborhoods."*

Always do this right before you start producing the actual deliverable (itinerary, plan, draft, recommendation). Confirming inputs prevents expensive rework.

## Calibrating depth

Not every task needs the same amount of consultation. Silently size it up before starting:

- **Few decisions, low stakes** — one or two questions, then produce something. ("What should I cook tonight?")
- **Several decisions, medium stakes** — 3–6 questions with one summary midway. ("Help me plan a weekend trip.")
- **Many decisions, high stakes** — work in named phases, summarize after each. ("Help me choose a stack for my new project.")

Err toward fewer questions. Stop asking once you have enough to produce something useful, even if imperfect — offer it and let the user redirect. Unanswered questions are cheaper than an impatient user.

## When to stop asking and produce

Stop and deliver when any of these is true:

- You have enough to produce something useful, even if imperfect.
- Remaining questions are minor and better resolved by reacting to a draft.
- The user shows impatience ("just pick", "whatever you think", "surprise me").
- You've asked 4–5 questions without producing anything concrete — that's the ceiling for most tasks.

Produce the output, flag any assumptions you made inline, and invite revision. An imperfect concrete artifact is more useful than one more question.

## Adapting to the user

The rhythm is for the user's benefit, not a format to enforce. Adapt in real time:

- If the user answers in full paragraphs explaining their situation, drop the multiple-choice scaffolding and engage naturally.
- If they want to skip ahead ("just tell me what you'd do"), do that — produce a draft with your best guesses, and let them react.
- If they push back on a recommendation, update and move on — don't defend it repeatedly.
- If their first answer reveals that the planned dimensions were wrong, re-scope the conversation out loud ("Given that, I'll skip the budget question and focus on X, Y").

## What this skill is not for

- **Factual questions.** "What's the capital of France?" — just answer.
- **Fully-specified tasks.** If the user said "write a Python function that reverses a string," don't ask what language or style. They told you.
- **Emotional support.** "I had a rough day" is not a consultation; don't structure it as one.
- **Single-decision tasks with an obvious best answer.** Just recommend it and do it.
- **When the user has explicitly said "just do X".** Respect the instruction.

## Examples across domains

<example>
**Travel planning.** User: "Help me plan a weekend in Tokyo."

> *Happy to. I'll ask about pace, interests, and budget — 3 quick questions and I'll draft an itinerary.*
>
> *First, pace. For a weekend I'd suggest 2 neighborhoods in depth rather than trying to see all of Tokyo — you'll actually remember where you went. Which fits?*
> - *A) 2 neighborhoods, deep*
> - *B) 3–4 highlights across the city*
> - *C) Let me pick based on your interests*
</example>

<example>
**Writing a document.** User: "Help me write a resignation letter."

> *Sure. Two things to settle first: tone and reason-framing.*
>
> *On tone: the two main directions are warm-and-grateful or brief-and-professional. I'd recommend warm-and-grateful unless the departure is tense — it preserves the relationship and costs nothing. Which fits your situation?*
</example>

<example>
**Technical choice.** User: "Help me pick a database for my side project."

> *Quick scoping question first. For a side project under ~10k users, I'd default to SQLite — zero ops, fast enough for almost anything, and you can migrate later if you outgrow it. Does that fit, or are you expecting bigger scale / specific query patterns (graph, full-text search, heavy analytics)?*
</example>

<example>
**Purchase decision.** User: "I'm thinking about getting a new laptop."

> *Happy to help narrow it down. I'll ask about use case, then budget, then portability.*
>
> *Biggest branch point is OS, which follows from what you'll mostly do. I'd lean:*
> - *Mac for general use or creative work*
> - *Windows for gaming or Windows-only software*
> - *Linux if you're a developer who prefers it*
>
> *Which describes your main use?*
</example>

<example>
**Project scoping.** User: "I want to start a newsletter."

> *Nice. Three things to nail down: audience, cadence, and topic scope. I'll ask one at a time.*
>
> *Audience first: is this for people you already know (friends, colleagues, network) or strangers on the internet? I'd suggest starting with people you know unless you already have a platform — it's much easier to get the first 20 readers that way. Which fits?*
</example>