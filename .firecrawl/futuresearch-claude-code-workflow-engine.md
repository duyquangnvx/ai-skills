[← Back to Blog](https://futuresearch.ai/blog/)

* * *

Our marketing pipeline scans 18 community sources, enriches threads with full content, classifies opportunities with a 20-question rubric, generates draft forum responses, and creates a pull request - every weekday at 08:00 UTC. The whole pipeline definition is not e.g. Python's functions with some workflow manager and executor like Prefect or Dagster (which are both cool), but - yeah, you guessed it - a markdown file in plain English, written by my boss.

I don't mean my boss _specified_ it and an engineer implemented it. I mean he opened `SKILL.md` in his editor and typed the pipeline in English. Or more precisely - in the light of this series - he asked Claude Code to write it together with him. It's a markdown file that says things like "spawn 18 scanners in background" and "after phase 1, do phase 2." It's not a formal task DAG and isn't specified in code. And it all runs _inside_ Claude Code, as described in our [first post from the series](https://futuresearch.ai/blog/claude-code-kubernetes-cronjob). This post is about a generic comparison of such systems, while we will see specific instances of that in the subsequent posts.

## Rough Comparison

We're not going to pretend this is better than Prefect or Dagster. For a lot of workloads, it's worse. But "a lot" isn't "all," and we think the tradeoff space is genuinely interesting. Here is a somewhat naive comparison:

|  | Prefect / Dagster | Claude Code |
| --- | --- | --- |
| Task definition | Python functions, objects, decorators, ... | Markdown files |
| DAG | Explicit dependency graph | "after scanning, enrich" |
| Workers | Containerized functions | Subagents with their own context windows |
| Retry logic | `@task(retries=3)` | "if Python enrichment fails, try WebFetch instead" |
| Adding a new integration | Install plugin, configure IO manager, write config schema | "read from BigQuery" |
| Scaffolding | Specific decorators, YAML, `definitions.py`, webserver config, user code, ... | Markdown files |
| Deployment | webserver, usercode containers, UIs, DB, ... | one (cron)job as per Part 1 of this series |
| Monitoring | Dashboards, metrics, alerts, orchestration UIs | none? |
| Who writes it | Software engineer | anyone, in English |
| Debugging | Stack traces, breakpoints | Absolutely horrendous |

I am not gonna pretend this comparison is not skewed towards Claude Code, it heavily is, as it's not a full replacement of these. Dagster is giving you stuff like sensors, queues, concurrency, work pools and what not, and if you need those, then go for it. What we are covering here is mostly the job runtime and basic orchestration (which could still be plugged into frameworks like this to benefit from both worlds).

I want to write something like "it's all markdown files", which is a little bit of an exaggeration, but not much! The whole setup is one skill (the orchestrator), a handful of subagent definitions, and some Python libraries for the mechanical stuff. Compare that to e.g. Dagster scaffolding. Dagster is pretty opinionated here and you _really_ want to do things the way it wants you to - `definitions.py`, YAML config, webserver, user code server, and if you want to read from GCS, the right IO manager plugin configured through Dagster's abstraction layer instead of just... asking Claude to use `gsutil`. It's all legitimate infrastructure for production workloads. If tomorrow we need to read from BigQuery, we write "query BigQuery for the last 7 days of page analytics" in the skill file and Claude figures out the `bq` command or the MCP tool or whatever's available (setting _those_ \+ permissions is still some annoying boilerplate though).

## How It Works

The pipeline is one skill that orchestrates six phases. Most of the heavy lifting is fanned out to subagents running in parallel. We will get into the details of the pipeline in a separate post, but just to give you an idea of what we're talking about:

```
Phase 1: Scan
  ├── Python search script → produces shards
  ├── 18 scanner subagents (one per source: reddit, hubspot, shopify, ...)
  └── N search-scanner subagents (one per shard)
       ↓ poll filesystem for .json / .error files
Phase 2: Enrich
  └── Python enrichment (fetch full thread content, WebFetch fallback)
       ↓
Phase 3: Classify
  └── N classifier subagents (one per enriched file, 20 questions, score 1-5)
       ↓ poll filesystem again
Phase 4: Propose
  └── proposer-{product} subagents (one per product with score 4-5 hits)
       ↓
Phase 5: Report
  └── markdown report with metrics, top opportunities, draft responses
       ↓
Phase 6: Git
  └── branch, commit, push, open PR
```

The orchestrator - the main Claude Code process - reads the skill, spawns the subagents via the `Task` tool, and coordinates them. The subagents write results to disk. The orchestrator polls for output files rather than collecting agent output directly (we'll get to why in the filesystem section below). The "dependency graph" is just document order: phase 2 comes after phase 1 because it's written after phase 1.

## The Accidental Resilience

Here's one aspect that the comparison table doesn't capture: Claude Code is accidentally resilient in ways that traditional orchestrators are not.

When a Python script hits an unexpected error, it crashes. By default, the state is lost, you go to some logging tool or something and try to find the bug. If you are lucky, you fix the bug, but often you're not sure if it's hard to reproduce (reddit blocks IPs from GCP), you re-run the whole thing, and hope. Orchestrators are trying to help you by giving you e.g. retries mechanisms, which are good, but far from ideal when dealing with unknown unknowns, i.e. how many retries do you need, what the backoff period is, on what type of errors should you try to retry and so on.

When Claude Code hits an error, it _reads the error message and decides what to do._ A library isn't installed in the container? It runs `apt-get install` (scary, but awesome). An API returns an unexpected format? It adapts the parsing. The enrichment script returns fewer results than expected? The pipeline instruction says "use WebFetch for the failed URLs" - and it does, for just the ones that failed, preserving everything that already worked.

This is not magic. It's just that the "retry logic" has access to the same reasoning that wrote the original attempt. It can distinguish between "the server is down, try again" and "this approach won't work, try a different one," in a way traditional retries cannot.

And the state preservation is a great feature on its own. When running locally and phase 3 of our pipeline fails, phases 1 and 2's results are still on disk _and_ in the conversation context. If we're running interactively, we can `--resume` and say "phase 2 worked fine, start from phase 3 and here's what went wrong." The agent just remembers everything - no checkpoint files, no serialization, no cache key configuration.

Prefect and Dagster have caching, and it's a real feature. But getting it right is real engineering work: hash the inputs properly for the cache key, make sure the task-level cache interacts correctly with the flow-level cache, handle the case where a cached task succeeds but the next task fails, deciding where the cache is stored... We've been through this, and sometimes it's just not worth the effort.

## What a Skill Looks Like

This is a real excerpt from our pipeline definition:

```markdown
## Phase 1: Scan

### Step 1b: Run Domain Scanners

Spawn all 18 domain scanners in background.
Track each task_id with its source name.

Each: Task (subagent_type: scanner, run_in_background: true): "Scan {source}"
```

That's the DAG basically: "Spawn 18 things. Track them." Claude Code reads this, spawns 18 subagents, and tracks the task IDs. The "dependency graph" is the document order: Phase 2 comes after Phase 1 because it's written after Phase 1, as... any human naturally works and thinks.

Running it is what we covered in the [Part 1](https://futuresearch.ai/blog/claude-code-kubernetes-cronjob). You pass `"execute scan-and-classify skill"` as a prompt and it runs. Again, you don't have to think about deployments and flags and if you should use `deploy()` or `serve()` or anything, just CLI command.

## What an Agent Looks Like

We do have specialized agents that do specific jobs. Agents are spawned with their own context, so the context of the main orchestrating agent doesn't explode. Each subagent is a markdown file with YAML frontmatter:

```yaml
---
name: scanner
description: Scan a community source for marketing opportunities.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
permissionMode: bypassPermissions
---
```

We have 23 of these agent definitions. Scanners, classifiers, proposers, graphics generators, dataset finders, SEO analyzers. Each one is a markdown file describing what the agent should do, what tools it has, and what model to use.

## Python Does Mechanics, Claude Does Judgment

One of the design principles is **putting mechanics in code and letting Claude make judgments.** Specifically, it's this separation of concerns:

```
lib/scanners/reddit.py     → Fetches posts, parses JSON, handles rate limits
.claude/agents/scanner.md  → Reads posts, decides "is this a real data problem?"
```

This is not a strict separation - it's totally fine that the agents are writing some code. But if it's something that can be reused and standardized, it's good to add it, but it's still quite wasteful resource-wise to let agents do everything like scanning API endpoints and stuff.

This is yet another part where running inside Claude Code shines - it can **develop and improve itself while running in production.** No, really, let that sink in for a second, because you cannot just gloss over it: the development and the runtime blend together. You tell it to run the scanner for a site and it tells you it can't because X, but presents you with a workaround for X that it can incorporate into the skill or lib for future runs. When it encounters that the environment has changed - like an API schema on the remote is different - it can self-correct during the runtime, and even commit that as an improvement for any further runs.

## The Filesystem Is the Message Bus

Here's where it gets ugly. In Prefect, it's the orchestrator backend that manages dependencies. Claude is of course able to get state of agents natively, and it worked fine for like 4 agents. When we scaled to 18, the orchestrator's context window filled up with all the returned output, as it seems to be a limitation that Claude cannot get the state without also parsing the output. Claude started forgetting earlier results and producing incomplete reports.

The fix: `run_in_background: true` \+ filesystem polling. The orchestrator's context went from O(n \* output\_size) to O(n \* filename). The agents write their results to disk and the orchestrator only reads file paths. Specifically, when a scanner agent finishes, it writes `data/scans/reddit/2026-02-17-run1.json`. If it fails, it writes `data/scans/reddit/2026-02-17-run1.error`. The orchestrator polls:

```bash
while [ $ELAPSED -lt $TIMEOUT ]; do
  SUCCESS=$(ls -1 data/scans/*/${TODAY}-run*.json 2>/dev/null | wc -l)
  ERRORS=$(ls -1 data/scans/*/${TODAY}-run*.error 2>/dev/null | wc -l)
  if [ "$((SUCCESS + ERRORS))" -ge "$EXPECTED" ]; then break; fi
  sleep 10
done
```

`.json` means success. `.error` means failure. `ls` is the health check. This is not elegant.

## Handling Timeouts

Agents will run forever if you let them, and given how imprecise and informal this setup is, you need to add some limits to it. There is nothing especially interesting here, but for completeness, we implemented that on four layers:

**Layer 1: `max_turns` per agent.** A hard limit on API round-trips. When a news-finder hits 30 turns, Claude Code stops it and returns whatever it has. We tuned these empirically - 30 was too few for news-finder, 20 was right for dataset-finder.

**Layer 2: Wall-clock cap per phase.** 10 minutes. If a batch of agents hasn't finished, move on with whatever completed. Mark the stragglers as "timeout" in the report.

**Layer 3: Bash `timeout 10800`.** After 3 hours, a second Claude wakes up to salvage partial results (see [Post 1](https://futuresearch.ai/blog/claude-code-kubernetes-cronjob)).

**Layer 4: activeDeadlineSeconds.** And finally the hard limit enforced by Kubernetes, set to 4 hours in our case.

## Debugging Experience Is Bad

I want to be honest about this. Debugging a Claude Code pipeline is pretty subpar. There are no breakpoints or stack traces. When a subagent fails silently, you see nothing - you just notice a `.error` file appeared, if you remembered to implement `.error` files in the first place (we didn't).

And as there's no formal verification of any of it - no tests for the pipeline, no type checking on the DAG and so on, you interact with the system through Claude Code because a human genuinely cannot handle the throughput of many parallel scanners writing enriched JSON. It's vibecoding at its finest.

Also, the `--dangerously-skip-permissions`? The flag is named that for a reason, and there's no way to guarantee that Claude Code won't - to paraphrase a famous Haskell tutorial - go outside and scratch your car with a potato. We run it in an ephemeral container with limited credentials to reduce the blast radius. But if you're someone who needs formal guarantees about what your code will do at runtime, this approach should give you hives. We do acknowledge this, and are fully aware of the associated risks and tradeoffs, and given what this does, the stakes are low.

## Three Quirks From the Skill File

And of course, writing pipelines in English produces some quirks you'd never see in a traditional codebase. Here are three picks from ours.

**The one-sentence retry policy.** This is the entire fallback logic for when enrichment fails:

```markdown
If Python enrichment returns fewer opportunities than scanned,
use WebFetch for the failed URLs.
Add successful results with "enrichment_method": "webfetch".
Log URLs that fail both methods.
```

In Prefect, that's a custom retry handler with conditional logic. Here it's a paragraph and Claude figures it out.

**The anti-coding instruction.** The classifier agent's instructions include this:

```markdown
At no point should you Write() a Python script. If you think you
need one, it's because you misunderstood these instructions.
```

We added this after a classifier tried to write a sentiment analysis script instead of just... reading the thread and thinking about it.

**The "never fully fail" rule.** The last section of the skill file:

```markdown
- Scanner fails: Log failure, continue with others
- Python enrichment fails: Try WebFetch fallback, then continue
- Classifier fails: Log failure, continue with other sources
- Proposer fails: Log failure, keep intermediate files

Never fail the entire skill due to individual component failures.
Always produce a pipeline report.
```

That last line is doing a lot of work. Even a completely botched run produces a report saying "everything broke" - which is still more useful than a silent crash.

## GitHub Is the UI

I genuinely enjoy nerding about subagent orchestration and filesystem-based message buses as much as anyone. But [FutureSearch](https://futuresearch.ai/) is a startup that needs to survive. The cool architecture means nothing if it doesn't change something out in the real world behind the boundaries of the company. Our pipeline generates mostly reports, and also needs some state like what URLs it has already seen and so on. A natural thing for this would be to use a database, define a schema, set up credentials, ... Well, we use GitHub as a store (together with LFS). Every pipeline run creates a PR with a markdown report and necessary state files like a `seen.txt` with already listed URLs. Our non-technical person opens it, reads the results, expands a draft response, tweaks a sentence, and responds to an opportunity. Or they open the news pipeline PR, pick the better graphic from two variations, downloads the PNG, and shares it. GitHub is the database, the UI, and the delivery mechanism.

This bridges the gap between what an AI can do and a human can do - neither on their own is as good as both together. The AI produces 80% of the work, the human fixes the last hardest 20% and takes action, and together they ship something neither could individually.

The flexibility matters more than the reliability here. When the classifier catches that a Reddit post is actually a competitor's marketing campaign, that's judgment no `@task(retries=3)` gives you. When news breaks about tariffs and the pipeline routes to QuantGov for regulatory data, that's not something you hard-code in a DAG. And when your boss can read the pipeline definition and say "add Snowflake to the sources" and it just works because the instruction is in English - that's the point.

_We build [FutureSearch](https://futuresearch.ai/) \- forecast, score, classify, or research every row of a dataset. This pipeline is how we find the people who need it._

* * *

_[FutureSearch](https://futuresearch.ai/) lets you run your own team of AI researchers and forecasters on any dataset. [Try it for yourself.](https://futuresearch.ai/)_