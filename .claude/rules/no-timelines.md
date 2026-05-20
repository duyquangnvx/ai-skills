# No Timeline Estimates

Don't quote calendar time (hours, days, weeks) for work scope. As an AI coding agent, my execution pace doesn't map to human developer pace, and the numbers create false confidence the user then plans around.

## Rule

Never write "1-2 days", "~1 week of work", "30 minutes", "few hours", "by Friday", or similar calendar estimates — not in proposals, plans, commit messages, or conversation.

## Why

- AI execution speed varies wildly with task shape. A "1-day human task" might be 5 minutes of actual tool calls, or 3 hours of debugging UXP runtime gaps.
- Estimates get propagated as commitments. The user remembers "1 week" even when I said "roughly".
- The user's mental model is different anyway: they care about **what blocks them** and **scope shape**, not how long it takes me.

## What to communicate instead

| Don't say | Say |
|---|---|
| "This will take 2 days" | "Small change — 3-4 file edits" |
| "~1 week of work" | "Milestone-sized — let me sketch the breakdown" |
| "30 minutes to do X" | "Quick edit" — or just do it |
| "Should be done by Friday" | (delete) |

Acceptable scope signals:

- **Effort shape**: "single edit", "multi-file refactor", "needs research first", "spike before commit"
- **Risk**: "low-risk", "uncertain — let me check X first"
- **Order**: "this blocks that" instead of calendar time
- **Build/test latency**: if a command genuinely takes ~30s, OK to mention so the user knows why I'm waiting

## Edge cases (these ARE quotable)

- **External real-world deadlines** — "EU AI Act effective 2026-08-02" is a fact, not my estimate.
- **Vendor SLA** — "OpenAI Responses returns in 2-5 minutes" is the provider's published behavior.
- **Tool latency I just measured** — "build took 1.8s" is observation, not prediction.

The line: **don't predict human-pace work durations.**
