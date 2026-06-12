# Spec Analysis Checklist

Use this to extract harness-relevant facts from any spec — PRD, design doc,
vision doc, RFC, or long-form description. The output drives the interview
(ask only what this didn't answer) and pre-populates the docs.

## How to use

Read the spec end-to-end first. Then go through the dimensions below, filling
each with **direct evidence from the spec** or marking it `[GAP]`. Do not
infer or invent — gaps surface to the user, not get filled with plausible
defaults.

## The seven dimensions

### 1. Vision and scope

- What is being built? (one sentence in user-facing terms)
- Who is it for?
- What is explicitly out of scope? (every "we will not", "later", "v2",
  "no <thing> at v1") — feeds the roadmap's Out lists and DoD
- What does success look like? (the bar for "shipped")

### 2. Decisions the spec already made

Choices the spec states explicitly — these become entries in `decisions.md`
immediately (still revisable later). Technical and product-level alike: stack
picks, vendor choices, architectural commitments, scope calls.

Look for language like: "we will", "the product is", "v1 ships with", "must
support", "is not". Each is a decision someone made, even if not framed as
one. Capture each as one line + the why (lift the spec's reasoning when
given; write `per spec` when it only asserts) + the spec section as Source.

Do NOT invent decisions the spec didn't make.

### 3. Dev-layer facts

What the harness files need directly:

- Stack, runtime, intended directory layout → CLAUDE.md / interview. Watch
  for specs that describe a runtime/output workspace tree (what the product
  *produces*) — that is not the source layout; treat the source tree as a
  separate fact, usually a `[GAP]`
- Commands for test/build/lint, if stated → CLAUDE.md Commands table
- Conventions and invariants an agent could not guess ("X is append-only",
  "never regenerate Y") → CLAUDE.md Conventions, classified advisory vs
  must-always
- System components and data flow → `architecture.md`

### 4. Implied phases

Read for phasing signals: "MVP", "v1", "phase N", "first X then Y",
dependency hints, deadlines. If the spec is non-phased, propose a phase shape
from the product's natural slices — **vertical slices**, each demoable
end-to-end — and mark the proposal clearly as a suggestion, not the spec's
words. No phasing signal and no clear direction → recommend skipping the
roadmap rather than inventing one.

### 5. External constraints

Hard deadlines, team shape (solo vs team), budget signals, compliance,
platform commitments, dependencies on other teams. Constraints often hide as
throwaway phrases — "it's for kids" can imply a compliance regime. Skip
coordination questions for a solo project.

### 6. Success bar at v1

The minimum to count as "shipped": functional bar, quality bar, content bar.
Drives the roadmap's Definition of Done. Prefer criteria checkable without
subjective judgment.

### 7. Open questions

Anything the spec leaves undefined that affects the harness. Categorize:

- **Blocking:** must be answered before generating files (ask the user)
- **TBD-acceptable:** generate with an honest `TBD` marker
- **Future:** explicitly deferred by the spec itself

## Output format

Produce a structured summary and show it to the user before generating any
file:

```
## Spec Analysis Summary

**Project:** <one-line vision>
**For:** <target user>
**Stack/dev facts:** <what the spec states; [GAP] for the rest>
**Out of scope:** <2-3 most important non-goals>

**Decisions the spec already made (→ decisions.md):**
- <decision> — why: <one line, or "per spec"> — <spec ref>

**Implied / proposed phases (→ roadmap.md, or "skip roadmap"):**
1. <phase name> — <one line>

**External constraints:** <constraint — evidence>

**v1 success bar:** <criteria>

**Blocking questions:** <questions for the user>
**TBD-acceptable gaps:** <short list>
**Deferred by spec (future):** <short list — omit if none>
```

## Anti-patterns

- **Don't fill gaps with plausible defaults.** A plausible default becomes a
  fake fact in the generated files. Mark gaps honestly.
- **Don't paraphrase the spec back as analysis.** If the summary reads like a
  shorter spec, it's compression, not analysis. Analysis means structuring,
  surfacing implicit decisions, and naming gaps.
- **Don't extract feature lists.** Features land in roadmap phases later;
  the analysis is about frame, not content.
