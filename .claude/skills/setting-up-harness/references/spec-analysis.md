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
  "no <thing> at v1") — feeds the backlog's Out lists and product DoD
- What does success look like? (the bar for "shipped")

### 2. Decisions the spec already made

Choices the spec states explicitly — these become ADRs in `docs/adr/`
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
- System components and data flow → `architecture.md` (seeded as *intended*
  design — the template's day-zero status line applies until the structure
  is built)

### 4. Implied epics, risk register & build order

Read for structure signals: the product's natural **capability areas** — these
become epics, coarse and dependency-ordered; for each, note what **usable**
would mean (the surface a person touches to exercise it). A spec's milestones
are *its* plan, not automatically the epic set: re-derive the capabilities,
then check them against the milestones.

Separately, extract the **risk register**:

- research questions that could invalidate the plan → spike candidates
- integration contracts the spec leaves unpinned → walking-skeleton candidate
  (one thin story at most)
- external lead-time items (audits, approvals, reviews) → start-early notes

Mark proposals as suggestions, not the spec's words. No structure signal and no
clear direction → recommend skipping the backlog rather than inventing epics.

### 5. External constraints

Hard deadlines, team shape (solo vs team), budget signals, compliance,
platform commitments, dependencies on other teams. Constraints often hide as
throwaway phrases — "it's for kids" can imply a compliance regime. Skip
coordination questions for a solo project.

### 6. Success bar at v1

The minimum to count as "shipped": functional bar, quality bar, content bar.
Drives the backlog's Definition of Done. Prefer criteria checkable without
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

**Decisions the spec already made (→ docs/adr/):**
- <decision> — why: <one line, or "per spec"> — <spec ref>

**Implied epics & build order (→ backlog.md, or "skip backlog"):**
- Epics: <E01 area (usable: <surface>)>, <E02 area (usable: <…>)>, … (dependency order)
- Build order: <dependency order of the capabilities>
- Risk register: <spike candidates · unpinned contracts · external lead-times>

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
- **Don't extract feature lists.** Features land in epics and stories later;
  the analysis is about frame, not content.
