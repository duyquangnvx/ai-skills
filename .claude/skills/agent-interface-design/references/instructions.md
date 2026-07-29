# Writing Instructions: The Standard

Applies to system prompts, agent configs, skill bodies, and prompt templates.

## Make important rules observable

Each important rule should affect a transcript-visible behavior: output shape, tool choice, file edit, refusal, escalation. If you cannot point to the behavior a rule should produce, the model cannot either — and you have no way to tell whether the line is working, which makes it permanently unfalsifiable and permanently unremovable.

## Match the form to the failure

Classify the failure you actually observed before choosing wording. The form that fixes one class measurably worsens another.

| What the model does | Right form | Wrong form |
| --- | --- | --- |
| Knows the rule and skips it under pressure | Prohibition, with the specific rationalizations named and answered | Soft guidance — "prefer", "consider" |
| Complies, but the output has the wrong shape | Positive recipe: state what the output *is*, its parts, in order | A list of prohibitions |
| Omits a required element from output it already produces | A required slot in the structure it fills in | A reminder in prose near the structure |
| Should behave differently under some condition | A conditional keyed to an observable predicate | An unconditional rule plus exemptions |

Prohibitions backfire on shaping problems because a "don't" is something the model negotiates with when a competing incentive pushes the other way — under one, a prohibition can produce more of the unwanted content than saying nothing at all. A recipe leaves nothing to negotiate: the output matches the stated shape or it does not.

Two properties of wording that hold whichever form you pick. **Nuance clauses reopen what the rule closed** — "don't X unless it matters" invites the exception to swallow the rule, so express a real exception as its own conditional. And **exemption clauses do not scope**: "this limit doesn't apply to code blocks" still suppresses code blocks. If part of the output must be exempt, restructure so the rule cannot reach it.

Give the model a constructive default path, and reserve explicit prohibitions for safety, privacy, destructive actions, data exfiltration, and legal boundaries — costly failures need hard edges.

## Remove contradictions

When two same-level rules disagree, the model picks one arbitrarily, and no priority ladder fixes that — delete or reconcile first. Contradictions are not merely unresolved; they cost effort even when they resolve correctly, because the model spends reasoning trying to reconcile them.

Ranking across levels is a question about source authority and belongs in one place: `trust-and-safety.md`. State the ranking your system uses explicitly, put it where compaction cannot drop it, and instruct the agent to ask when a conflict cannot be resolved safely.

Know where each artifact lands in your runtime, because that determines what may override it — an instruction file injected at user-message level is not an enforcement layer, whatever it says. Verify the layering rather than assuming it; it is a harness implementation detail and it changes. Deterministic guarantees belong in hooks or runtime policy, never in instruction text.

## Explain the why for judgment rules

Models generalize from clear intent better than from brittle rule lists. A bare rule covers the cases you spelled out; the reason covers the ones you didn't — and gives the model the grounds to recognize when a case falls outside the rule entirely, which no amount of enumeration provides.

## Calibrate force

MUST, NEVER, and CRITICAL work by contrast with the text around them, which means force is a signal with a fixed budget: its meaning is set entirely by how often you spend it. Miscalibration fails in both directions. Spend it on style preferences and the marker stops carrying information, so the genuinely critical rules lose their edge. Withhold it from safety and data-loss boundaries and they read as suggestions.

**The correction direction is a measurement, not a default.** If a behavior fires too often, dial the language down to plain phrasing; if it fires too rarely, the usual cause is that the rule is not observable enough or is buried, not that it needs more force. You find out by running the scenario, never by assuming which way the current generation of models leans.

Escalate to MUST or NEVER only for a specific observed failure, never prophylactically.

## Give hard requirements an escape hatch

An absolute rule the model cannot always satisfy produces fabricated compliance — hallucinated arguments, invented facts:

```text
Risky: You must call a tool before responding to the user.
Safer: Call a tool before responding. If you lack the information to
       construct a valid call, ask the user instead.
```

Pair every MUST with its conditional exit, and give the exit a threshold. "Ask the user" with no threshold produces an agent that asks constantly; `architecture.md` covers when asking is the right move.

## Examples are behavioral tests

Add examples only for non-obvious formats or observed failure modes — when prose is ambiguous or formatting matters. An example carries at least as much steering weight as a prose rule, so one that demonstrates a violation teaches the violation. Every example must comply with every rule in the document.

Good examples are realistic, compact, and current. Remove examples showing forbidden behavior, outdated APIs, unsafe tool use, or a different output format than the one requested.

## Metadata and routing

Metadata fields are routing surfaces: they describe triggers, symptoms, and scope, never the workflow. A workflow summary in a description becomes a shortcut the model follows instead of reading the body — the body then becomes documentation the model skips.

Bad:

```yaml
description: Use for skill review - checks metadata, tests scenarios, then rewrites weak sections
```

Better:

```yaml
description: Use when creating, editing, or reviewing SKILL.md files
```

Write descriptions in the third person and lead with the triggering condition. Include the symptoms someone would notice before they know what the thing is called.

## Budget audit

Every token competes. The test is the same one that decides whether a rule belongs at all: **remove the line, run a scenario where it should matter, and see whether the output changes.** Anything that survives removal is cost without benefit, however true it reads.

That test finds what a checklist of smells misses — three examples all teaching the same rule, a glossary of forty terms of which three are used, a preamble of background, a correct-but-inert sentence nobody acts on. `verification.md` covers how to run it against a control.

Instructions also rot in a way that is invisible on a read-through: rules for scenarios that no longer exist, caveats about behavior that changed, examples using an API that moved. Review them in the same change that touches the system they describe.

## Review checklist

- [ ] Required behaviors are observable in realistic transcripts.
- [ ] The form of each rule matches the failure it was written for.
- [ ] No two rules contradict; cross-source ranking is stated and lives somewhere durable.
- [ ] Strong language is reserved for costly or observed failure modes.
- [ ] Every hard requirement has a conditional exit with a threshold.
- [ ] Every example complies with every prose rule and uses current APIs.
- [ ] Descriptions say when, not how; no workflow summaries in metadata.
- [ ] Every surviving line changed behavior when ablated.
