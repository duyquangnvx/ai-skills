# Spec Analysis Checklist (PM Layer)

Use this to extract PM-relevant info from any spec — PRD, vision doc, design brief, RFC, or long-form description. The output drives every later phase.

## How to use

Read the spec end-to-end first. Then go through the dimensions below, filling each with **direct evidence from the spec** or marking it `[GAP]`. Do not infer or invent. Gaps surface to the user in phase 2.

This is a PM-layer analysis. Anything purely implementation lives at the dev layer, not here.

## The six dimensions

### 1. Vision and scope

- **What is being built?** (one sentence in user-facing terms)
- **Who is it for?** (target user, persona, or context)
- **Why does it need to exist?** (problem or opportunity the spec articulates)
- **What is explicitly out of scope?** (every "we will not", "later", "v2", "no <thing> at v1")
- **What does success look like?** (metrics, qualitative goals, "shippable when X")

### 2. Locked decisions (the spec already made)

Things in the spec that are not negotiable — these become rows in `decisions.md` immediately.

Look for language like: "we will", "the product is", "v1 ships with", "must support", "is not". Each is a decision someone made, even if not framed as one.

Capture each as: `<one-line decision>` + `<spec section reference>`. These pre-populate the decisions log.

### 3. Implied phases

Read the spec for phasing signals:

- "MVP", "v1", "alpha", "beta", "phase N"
- "First we'll do X, then Y" sequences
- Dependency hints
- Any deadlines or timeframes mentioned

If the spec is non-phased, propose a phase shape based on the natural slices of the product. **The shape must be vertical** — each phase ships something demoable end-to-end, not "build the data layer first, then the surface layer." Mark phase proposals clearly as a suggestion, not the spec's words.

### 4. External constraints

What's pushing on the project from outside the team?

- **Hard deadlines** (launch event, regulatory cutoff, contractual milestone)
- **Team shape** (solo, pair, team of N, distributed)
- **Budget signals** (cost ceilings, "must be free to operate")
- **Compliance / regulatory** requirements
- **Vendor / platform commitments** ("must work on platform X", "must integrate with system Y")
- **Dependency on other teams** (waiting on a shared library, waiting on legal review)

Constraints often hide as throwaway phrases. A short remark like "it's for kids" can imply an entire compliance regime.

### 5. Success bar at v1

What's the minimum the project must hit to count as "shipped v1"?

- Functional bar (which features work end-to-end)
- Quality bar (performance, reliability, polish)
- Content bar (how much content / data the launch needs)
- Compliance bar (certifications, audits, accessibility)

This drives the Definition of Done section in `roadmap.md`.

### 6. Open questions

Anything the spec leaves undefined that affects PM-layer decisions. Categorize as:

- **Blocking:** must be answered before bootstrap (e.g., a fundamental shape question)
- **TBD-acceptable:** can ship the planning docs with a placeholder
- **Future:** explicitly deferred by the spec itself

## What to NOT extract (dev layer, not here)

The skill must not pull these into the PM analysis, even if the spec mentions them:

- Programming language, framework, database, queue, cache, or any specific dependency
- Code patterns or architectural styles at the system level
- Source-tree structure
- Build, test, lint, or deployment commands
- Specific libraries or third-party packages

If the spec mentions these, note their existence (the dev layer will care) but do not include them in the PM analysis.

The exception: when a spec entry has product-level implications, capture the implication, not the technical expression. For example, a spec line locking the project to a browser surface means "no install required" — that's a product fact. The technical choice of browser framework is not.

The PM layer should be re-implementable in any tech stack without changing.

## Output format

After running the checklist, produce a structured summary like this and show it to the user before phase 2:

```
## Spec Analysis Summary

**Project:** <one-line vision>
**For:** <target user>
**Out of scope:** <2-3 most important non-goals>

**Locked decisions (will pre-populate decisions.md):**
- <decision 1> — <spec ref>
- <decision 2> — <spec ref>
... (typically several of these)

**Implied / proposed phases:**
1. <phase name> — <one-line>
2. <phase name> — <one-line>
... (typically a handful)

**External constraints:**
- <constraint> — <evidence>

**v1 success bar:**
- <criterion 1>
- <criterion 2>

**Blocking questions:**
- <question 1>
- <question 2>

**TBD-acceptable gaps:** <short list>

Ready to proceed once we resolve the blocking questions above.
```

This summary is the deliverable of phase 1. Do not generate any project files until the user has confirmed (or corrected) it.

## Anti-patterns

- **Don't fill gaps with plausible defaults.** A plausible default becomes a fake fact in the generated artifacts. Mark gaps honestly.
- **Don't extract feature lists.** Features go into roadmap phases later. Analysis is about *frame*, not *content*.
- **Don't paraphrase the spec back as analysis.** If the summary reads like a shorter version of the spec, it's not analysis — it's compression. Analysis means structuring, identifying gaps, and surfacing implicit decisions.
- **Don't copy implementation details from the spec into the PM analysis.** The spec may mix layers; the analysis must not.
