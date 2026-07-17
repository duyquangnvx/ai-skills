# Architecture

> **Status: intended — seeded from the spec; nothing is built yet.**
<!-- Day-zero repos only; omit when code exists. Rewrite covered parts to
as-built as stories land; delete this line when the whole file describes
what exists. -->

<2-4 lines: what kind of product this is, for whom.>

How the system is **now**. Overwrite when it changes — the diagram too; do not
keep history.

## Containers

<!-- Runnable parts, how they connect, external systems they touch. ~3+ runnable
parts or ~4+ boxes → one mermaid flowchart owns this and replaces the prose lines
below; fewer → keep the prose, no diagram. Never draw C4 L3/L4 — code is the
source of truth. A container diagram is a plain mermaid flowchart (not the
formal C4Container syntax), e.g.:
flowchart LR
  user([User]) --> web[Web app · React]
  web --> api[API · Node]
  api --> db[(Postgres)]
  api --> mail{{SendGrid}}
-->

<a mermaid flowchart, OR — for a simple system — these prose lines:>

- Components: <the runnable parts / modules>
- Data flow: <how a request or action moves through them>
- External dependencies: <the services, APIs, libraries that matter>

## Notes

<!-- Only what the diagram can't carry: constraints, invariants, and why a
structure is the way it is — link the decision, don't restate it. -->
