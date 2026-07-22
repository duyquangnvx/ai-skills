---
name: changelog
description: Human-facing CHANGELOG.md in Keep a Changelog form, rotated by period as it grows. Set up a project, cut a release, backfill from git history, or audit on request.
disable-model-invocation: true
---

A changelog answers one question for a person who already has a copy of the project: what changed for me since then. Git already answers "what commits landed", so anything that only answers that belongs in git and nowhere here. The user's request carries the verb — set up, cut a release, backfill, rotate, audit — apply it so the project ends in the shape below.

## The shape of a set-up project

1. `CHANGELOG.md` at the repo root — the canonical header below, then `## [Unreleased]`, then released versions newest first.
2. `docs/changelog/<period>.md` — older releases, one file per period, once the root file outgrows a single read.
3. The project's agent instructions — `CLAUDE.md`, `AGENTS.md`, whichever the project already keeps — carry the obligation as one line: *when a change lands that a user of this project would notice, add it under `## [Unreleased]` in `CHANGELOG.md`.*

That line is the load-bearing piece, and it is a pointer rather than an `@` import on purpose: the file grows without bound, so importing it would park the whole release history in every turn of every session. The obligation is what has to be ambient; the format rules can wait in the file's header until an agent actually opens it.

## Canonical header

Install verbatim at the top of `CHANGELOG.md`, dropping the Semantic Versioning clause if the project versions some other way. It is the single source of the daily rules — agents in the project follow it with no skill loaded:

```markdown
# Changelog

Notable changes to this project, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- Write each entry for someone who uses this project, in their vocabulary
  rather than the implementer's, self-contained enough to make sense without
  the PR beside it. Group under `Added`, `Changed`, `Deprecated`, `Removed`,
  `Fixed`, or `Security`.
- Unreleased work accumulates under `## [Unreleased]`. Cutting a release
  renames that heading to `## [x.y.z] - YYYY-MM-DD` and opens a fresh empty
  `## [Unreleased]` above it.
- Older releases live in `docs/changelog/`, linked at the bottom of this file.

## [Unreleased]
```

## What earns an entry

The whole value of the file rests on this filter, so hold each candidate to a single test: could someone using the project notice this without reading the diff? A new flag, a changed default, a fixed crash, a dropped runtime version all pass. A refactor, a new test, a dependency bump nothing observable rides on all fail — and letting them in is how a changelog dies, because a file that reads as implementation trivia trains people to stop opening it.

Transcribed commit subjects are the usual way that happens. A commit is written from the author's vantage, mid-work; an entry is written from the reader's, after the fact. Restate it as what they can now do, what will break on them, or what stopped hurting.

## Cutting a release

Rename `## [Unreleased]` to `## [x.y.z] - YYYY-MM-DD` with today's date and open a fresh empty `## [Unreleased]` above it. Where the project has a remote worth linking to, version headings resolve through compare-link refs collected at the bottom of the file, so the new version gets a ref and `[Unreleased]` re-points at it; a project with no remote keeps plain headings rather than a fabricated host. A version pulled after publication keeps its section and gains `[YANKED]` on the heading — deleting it strands anyone still running that version with no way to find out what they have.

Cutting a release here means writing the changelog and nothing else — the version bump in the project's manifest and the tag itself belong to whatever release process the project already runs.

An empty `## [Unreleased]` at release time is a finding, not a formality. Either nothing user-visible shipped, or entries went unwritten when the work landed; say which before cutting.

## Rotation

Once `CHANGELOG.md` passes roughly 200 lines, move the oldest complete releases into `docs/changelog/<period>.md` and link it from the bottom of the root file, newest period first. The period is whatever slices the project's release cadence into files of readable size — `2026.md` for a few releases a year, `2026-Q3.md` for a busy project. Root keeps `Unreleased` plus the current period.

Rotation moves text, it does not summarise it: entries and their link refs travel unchanged, so a reader who follows a version link into an archive finds exactly what shipped.

## Boundaries

- A project that has already shipped versions still starts at an empty `## [Unreleased]`. Name the missing history as a gap the user can choose to fill; inventing entries for versions already out in the world is worse than having none.
- Backfill only as far as the oldest version people still run, and only from what the user points at. Attribute a change to the release that shipped it — the tag it landed under, dated when that version went out rather than when the commit was written.
- One line per change here, with a link out to upgrade steps, migration guides, or an ADR. A changelog that absorbs those becomes a document nobody finishes.
- Cutting or backfilling never edits an archived period file.
