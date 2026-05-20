# No Timeline Estimates

Don't quote calendar time (hours, days, weeks) for work scope. AI execution pace doesn't map to human pace, and the numbers create false confidence the user then plans around.

## Rule

Never write "1-2 days", "~1 week of work", "30 minutes", "few hours", "by Friday", or similar calendar estimates — not in proposals, plans, commit messages, or conversation.

## Why

- AI execution speed varies wildly with task shape. A "1-day human task" might be a few minutes of actual tool calls, or hours of debugging an unexpected edge case.
- Estimates get propagated as commitments. The user remembers "1 week" even when I said "roughly".
- The user's mental model is different anyway: they care about **what blocks them** and **scope shape**, not how long it takes me.

## What to communicate instead

| Don't say | Say |
|---|---|
| "This will take 2 days" | "Small change — a few focused edits" |
| "~1 week of work" | "Milestone-sized — let me sketch the breakdown" |
| "30 minutes to do X" | "Quick edit" — or just do it |
| "Should be done by Friday" | (delete) |

Acceptable scope signals:

- **Effort shape**: "single edit", "multi-file refactor", "needs research first", "spike before commit"
- **Risk**: "low-risk", "uncertain — let me check X first"
- **Order**: "this blocks that" instead of calendar time
- **Build/test latency**: if a command genuinely takes a noticeable amount of time, OK to mention so the user knows why I'm waiting

## Edge cases (these ARE quotable)

- **External real-world deadlines** — a published regulation date or external due date is a fact, not my estimate.
- **Vendor SLA** — a provider's documented response time is their published behavior.
- **Latency I just measured** — "build took 1.8s" is observation, not prediction.

The line: **don't predict human-pace work durations.**
