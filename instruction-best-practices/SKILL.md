---
name: instruction-best-practices
description: Best practices for writing high-quality instructions, system prompts, skills, and agent configurations for LLMs. Use this skill whenever writing or reviewing a SKILL.md, system prompt, agent instructions, tool descriptions, or any structured guidance meant to shape LLM behavior. Also trigger when the user says things like "write a prompt for", "create instructions for", "design an agent", "make a skill", "review my prompt", "improve this system prompt", or is working on any document that will be consumed by an LLM as instructions — even if they don't explicitly mention "best practices."
---

# Instruction Best Practices

A reference guide for writing high-quality instructions that shape LLM behavior — whether it's a skill, system prompt, agent configuration, or tool description. The principles here apply universally to anything an LLM reads as guidance.

This skill is meant to be loaded alongside task-specific skills (like skill-creator) or used standalone when crafting any LLM-facing instructions.

---

## Core Philosophy

Two ideas underpin everything in this guide:

1. **Clarity over control.** LLMs are smart. They respond better to well-explained reasoning than to rigid rules. Instead of micromanaging with ALWAYS/NEVER/MUST, explain *why* a behavior matters. The model will generalize from understanding to novel situations — brittle rules won't.

2. **Context is finite.** Every token competes for the model's attention. More instructions isn't better — more *signal* is better. Treat your instruction budget the way you'd treat a tight slide deck: every line must earn its place.

---

## Writing Clear Instructions

### Be specific and direct

Think of the LLM as a brilliant new team member who has no context on your norms. The more precisely you explain what you want, the better the result.

- State the desired output format and constraints explicitly.
- When order matters, use numbered steps.
- If you want thoroughness, say so — don't rely on the model to infer "above and beyond" from vague prompts.

**Test:** Show your instructions to a colleague with no context. If they'd be confused, the model will be too.

### Explain the why

Providing motivation behind your instructions helps the model generalize correctly. Instead of bare rules, add a sentence of reasoning:

```
# Weak
Always use TypeScript for new files.

# Strong
Use TypeScript for new files — the codebase is migrating from JS to TS,
and mixed files create confusing type boundaries at import points.
```

The model is smart enough to extrapolate from the explanation. If it encounters an edge case you didn't cover, understanding the *reason* lets it make the right call.

### Tell the model what to do, not what to avoid

Negative instructions ("don't use markdown", "never be verbose") give the model a constraint without a direction. Positive instructions are more effective:

```
# Weak
Do not use bullet points or markdown formatting.

# Strong
Write in flowing prose paragraphs. Use plain sentences to connect ideas naturally.
```

### Use examples

Examples are one of the most reliable ways to steer output. A few well-crafted examples (3-5) dramatically improve consistency and accuracy.

Make examples:
- **Relevant** — mirror real use cases, not toy scenarios.
- **Diverse** — cover different situations so the model doesn't overfit to one pattern.
- **Clearly marked** — wrap in `<example>` tags so the model distinguishes them from instructions.

When an instruction is hard to articulate in words, a single good example is often worth a paragraph of explanation.

---

## Structuring Instructions

### Use XML tags or markdown headers for sections

Structure helps the model parse complex instructions without ambiguity. Each type of content gets its own section:

```xml
<role>You are a senior code reviewer...</role>
<instructions>When reviewing pull requests...</instructions>
<output_format>Structure your review as...</output_format>
<examples>...</examples>
```

Best practices:
- Use consistent, descriptive tag names.
- Nest tags when content has natural hierarchy.
- For variable inputs that change per-request, use dedicated tags (e.g., `<user_input>`) so the model clearly separates instructions from data.

### Progressive disclosure

Not everything belongs in the top-level instructions. Use a layered approach:

1. **Always in context** — core behavior, role, key constraints (~100-300 words).
2. **Loaded on trigger** — detailed instructions for specific tasks (the body of a skill or prompt section).
3. **On demand** — reference files, large examples, data schemas — pointed to with clear "read this when you need it" guidance.

This mirrors how humans work: you don't memorize the entire manual, you know where to look. For skills specifically, keep SKILL.md under 500 lines and offload large references to separate files with clear pointers.

### Put long-form data before instructions

When your prompt includes large documents or data alongside instructions, place the data at the top and your query/instructions at the bottom. This ordering can improve response quality significantly (up to 30% in Anthropic's tests) because the model attends most strongly to the end of context.

---

## Context Engineering

### Treat context as a finite resource

LLMs have an "attention budget" — every token attends to every other token (n² relationships). As context grows:
- Model accuracy tends to decrease.
- Earlier content gets less attention.
- Redundant or low-signal content actively hurts performance by diluting attention on what matters.

**The goal:** find the smallest set of high-signal tokens that maximizes the likelihood of your desired outcome.

### Avoid context rot

In long interactions or complex instruction sets, context quality degrades over time. Watch for:
- **Redundancy** — saying the same thing in different sections.
- **Stale content** — instructions for scenarios that no longer apply.
- **Low-signal filler** — hedging language, excessive caveats, ceremonial text that adds words without adding information.

Periodically audit your instructions: for each paragraph, ask "if I removed this, would the model behave worse?" If the answer is no, remove it.

### Signal-to-noise ratio

Every line in your instructions either increases signal (helps the model do the right thing) or adds noise (dilutes attention without benefit). Common noise sources:

- Restating obvious things the model already knows how to do.
- Listing exhaustive edge cases instead of explaining the underlying principle.
- Heavy-handed formatting (excessive caps, bold, exclamation marks) that creates visual noise.
- Motivational language ("You're an amazing assistant!") that doesn't affect behavior.

Rewrite noisy sections as concise, principle-based guidance. A single clear sentence often outperforms a paragraph of examples-as-rules.

---

## Calibrating Instruction Intensity

### Match instructions to model capability

Modern models (Claude 4.6, etc.) are significantly more capable than their predecessors. Instructions that were necessary for older models may now cause problems:

- **Anti-laziness prompting** ("Be thorough! Don't skip steps!") can cause overtriggering and overthinking in newer models. Dial it back or remove it.
- **Aggressive tool-use language** ("CRITICAL: You MUST use this tool when...") was needed when models undertriggered tools. Current models respond to normal language ("Use this tool when...") and may overtrigger on aggressive prompts.
- **Excessive guardrails** against hallucination or laziness can make the model overly cautious or verbose. Trust the model more and add constraints only where you observe actual failure modes.

### The Goldilocks principle for system prompts

**Too prescriptive** — Hardcoded if-else logic, brittle rules for every scenario, heavy MUST/NEVER language. Breaks on edge cases, high maintenance.

**Too vague** — High-level platitudes without concrete signals. "Be helpful and accurate" tells the model nothing it doesn't already know.

**Just right** — Specific enough to guide behavior effectively, flexible enough to handle novel situations. Provides strong heuristics rather than rigid rules.

### Start minimal, add from failure modes

The most effective approach to calibration:

1. Start with the minimum viable instructions.
2. Test against realistic scenarios.
3. When something fails, add targeted guidance for that failure mode.
4. Re-test to make sure the fix didn't break other cases.

This avoids the common trap of front-loading every possible rule and creating bloated, contradictory instructions. It also means every line in your final instructions exists because it solved an observed problem.

---

## Designing Tools and Agent Capabilities

### Tool descriptions

If a human engineer can't definitively say which tool to use in a given situation, an AI agent can't be expected to do better. Each tool should be:

- **Self-contained** — single, clear purpose.
- **Unambiguous** — no overlap with other tools in when to use it.
- **Token-efficient** — returns relevant information without bloat.
- **Descriptive in parameters** — use `user_id` not `user`, `start_date` not `date`.

Common failure: bloated tool sets with overlapping purposes. If you're adding a tool and can't clearly explain when to use it vs. existing tools, merge or restructure.

### Balancing autonomy and safety

For agentic systems, define clear boundaries around:
- **Actions the agent should take freely** — local, reversible operations (reading files, running tests, editing drafts).
- **Actions that need confirmation** — destructive, hard-to-reverse, or externally visible operations (deleting data, pushing code, sending messages).

Frame this as a principle with examples, not an exhaustive list. The model will generalize correctly if it understands the reasoning (reversibility and impact).

### Long-horizon state management

For tasks spanning many steps or multiple context windows:
- Encourage structured note-taking — the agent writes progress notes to files that persist outside the context window.
- Use git or version control as a state tracking mechanism.
- Design for compaction — when context gets long, the most important information should be extractable and resumable.
- Consider sub-agent patterns for complex tasks — specialized agents with clean context windows that return condensed results.

---

## Retrieval and Context Strategies

### Just-In-Time context (recommended for agents)

Rather than front-loading all possible information, maintain lightweight references (file paths, search queries, links) and load data dynamically when needed.

Benefits:
- Avoids context pollution.
- Mirrors how humans work — you don't memorize everything, you know where to look.
- Keeps the active context window focused on the current task.

Trade-off: slightly slower than pre-loaded context, and requires good tool guidance so the agent doesn't get stuck.

### Hybrid approach

Load essential, stable context upfront (role, core rules, key references) and enable dynamic retrieval for everything else. This is the pattern most skills and agent systems should follow — small core prompt + tools for deeper exploration.

---

## Anti-Patterns

Avoid these common mistakes when writing LLM instructions:

1. **Wall of MUST/NEVER** — Using aggressive capitalized commands for everything. Reserve strong language for genuine safety constraints. For everything else, explain the reasoning.

2. **Exhaustive edge case listing** — Trying to enumerate every scenario instead of teaching the underlying principle. A diverse set of 3-5 examples teaches better than 20 rules.

3. **Copy-paste redundancy** — Saying the same thing in the role section, the instructions section, and the examples. The model reads all of it and redundancy wastes attention budget.

4. **Assuming bigger context = better** — Larger context windows don't solve the attention problem. A focused 2,000-token prompt often outperforms a sprawling 10,000-token one.

5. **Over-engineering for hypotheticals** — Adding instructions for scenarios that haven't happened and may never happen. This adds noise and can create unintended interactions with real instructions.

6. **Ignoring the model's baseline** — Modern models are already helpful, accurate, and follow instructions well. Don't waste tokens re-stating behaviors the model already exhibits. Focus instructions on where you need the model to differ from its defaults.

7. **Rigid output templates** — Forcing exact structures for every response. Provide a template when format truly matters (reports, structured data), but for general interaction, describe the *qualities* you want (concise, technical, narrative) and let the model adapt.

---

## Quick Reference Checklist

When reviewing any set of LLM instructions, verify:

- [ ] Each section has a clear purpose — nothing redundant.
- [ ] Instructions explain *why*, not just *what*.
- [ ] Positive framing ("do this") over negative framing ("don't do that").
- [ ] 3-5 diverse examples for any non-obvious behavior.
- [ ] Structured with XML tags or clear headers.
- [ ] Long-form data placed before instructions/queries.
- [ ] No aggressive language (MUST/NEVER/CRITICAL) unless genuinely safety-critical.
- [ ] Tested against realistic scenarios, not just ideal ones.
- [ ] Tools have non-overlapping purposes with clear descriptions.
- [ ] Total instruction length is justified — every paragraph earns its place.
