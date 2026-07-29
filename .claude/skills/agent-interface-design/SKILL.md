---
name: agent-interface-design
description: "Use when designing, writing, or reviewing anything an LLM agent reads to decide behavior — system prompts, skills, tool schemas and descriptions, MCP servers, tool responses — and how its context is assembled and ages at runtime: what loads when, what stays true, memory, compaction, prompt caching, and when to escalate from workflow to agent to multi-agent. Symptoms: wrong tool calls, ignored instructions, oversized responses, prompt injection, the agent acting on a fact that has since changed, forgotten or repeated work, degrading long sessions, poor cache hits."
---

# Agent Interface Design

Everything the model reads is one interface: instructions, routing metadata, tool contracts, tool responses, and the context assembled around them at runtime. Write each surface as a small, testable behavior contract — the fewest high-signal words that reliably change model behavior in realistic scenarios.

The reader is a non-deterministic caller with limited attention, imperfect tool choice, and imperfect argument construction, and it cannot ask clarifying questions before acting on what you wrote. Design every surface for that reader.

## Four questions generate the rules

Every piece of context has the same four properties. Ask them of anything you put in front of the model and the specific rule follows, including for cases no standard here enumerates.

| Property | Ask |
| --- | --- |
| **Authority** | Who could have written this, can the user see it, and what may it override? |
| **Freshness** | When did this become true, is it still, and would the agent find out if it weren't? |
| **Cost** | What does carrying this cost on every turn from here on — tokens, latency, and attention taken from the current task? |
| **Actionability** | Does it change the next decision? |

Freshness is the one most often skipped. Context is a copy of state taken at a known time, and nothing in the window announces that a copy has gone wrong: stale context looks exactly like fresh context. A surface with no answer to the freshness question is a surface whose failures are invisible in any single transcript.

## This file is the map, not the standard

The standards live in the reference files, and each fact lives in exactly one of them. Whatever the task — writing a new surface, reviewing one, fixing a symptom — read the standard for every surface you are touching before producing output.

| Surface you are touching | Standard to read |
| --- | --- |
| Instructions: system prompts, agent configs, skill bodies, prompt templates | `references/instructions.md` |
| Tool layer: scoping, names, schemas, descriptions, responses, errors | `references/tool-patterns.md` |
| Context lifecycle: what enters, how long it stays true, compaction, memory, request layout | `references/context-lifecycle.md` |
| Authority and safety: source ranking, untrusted content, destructive actions, approval | `references/trust-and-safety.md` |
| Knowing it works: ablation, pressure scenarios, evals, metrics | `references/verification.md` |
| Architecture: workflow vs agent, multi-agent, stop conditions, tool reduction | `references/architecture.md` |

A single design question usually needs two or three of these, not one: the standard for the surface you are changing, plus `instructions.md` when the fix is a matter of wording, plus `verification.md` when you need to prove it worked. Only an audit of a whole interface touches all six.

## Principles

Each is elaborated in exactly one reference file. Here they are claims, not standards.

1. **Contracts, not documentation.** A line earns its place only if it changes what the model does next.
2. **Metadata routes; the body instructs.** Descriptions say when to load or call, never how the work goes.
3. **One home per fact.** Duplication costs tokens now and drifts into contradiction later.
4. **Authority is a property of the source, not of the position.** Rank by who wrote it and whether the user can see it.
5. **Context ages.** Every copy has a horizon; design for what happens when it expires.
6. **Enforce in software what software can enforce.** Prompts are for judgment.
7. **Every token competes.** Prefer the smallest high-signal context, and bound everything that can grow.
8. **Test, don't assume.** If you didn't watch the model fail without the line and comply with it, you don't know the words work.

## Routing a symptom

Two rules place most symptoms:

- **Behavioral symptoms** route to the surface the model read immediately before the bad decision — `instructions.md` if it ignored a rule, `tool-patterns.md` if it chose or called wrong, response shaping if it mis-reasoned from output.
- **Cost, drift, and degradation symptoms** route to whatever assembles context: `context-lifecycle.md`.

Four that route non-obviously:

| Symptom | Where |
| --- | --- |
| Agent obeys instructions found inside retrieved content | `trust-and-safety.md` — source ranking, untrusted content |
| User asked to approve the same action twice | `trust-and-safety.md` — one approval gate |
| Agent confidently reports something that was true earlier and is not now | `context-lifecycle.md` — freshness, detection |
| Loop never terminates, or retries a failure that will never succeed | `architecture.md` — stop conditions |

## One home per fact

Collisions in this skill happen along one seam: a **static contract** and its **runtime behavior** are the same fact seen from two sides. The rule that resolves them:

**The artifact file owns what to write down. The lifecycle file owns what happens to it during a session.**

| Content | Its one home |
| --- | --- |
| When to load a skill / call a tool | `description` metadata (skill frontmatter, tool description) |
| Process and workflow steps | Skill body or system prompt — never a description |
| Field names, types, required/optional, enums, return shape | Tool schema |
| Input conventions, side effects, sibling disambiguation | Tool description |
| Cross-tool workflow order, approval choreography, tone | System/developer prompt |
| Which actions require approval, and what may override what | Runtime gate; source ranking in `trust-and-safety.md` |
| Deterministic constraints (IDs, permissions, transitions) | Server-side validation |
| What a tool catalog offers and in what shape | `tool-patterns.md` |
| What a sub-agent returns, and in what shape | Its registered description where one exists; the brief itself where the spawn is ad-hoc — never left to the sub-agent |
| What happens to a loaded fact as the session runs | `context-lifecycle.md` |
| Heavy reference, long examples, API docs | On-demand reference files |

## Output pattern

For reviews:

```text
Symptom:
Likely cause:
Recommended change (surface + exact wording, signature, or error):
How to verify it (ablation, scenario, or eval):
```

For new designs: propose the smallest viable surface set, state each surface's authority and freshness horizon, explain the boundaries between tools and between prompt and schema, and list the first tasks that would prove the design works.
