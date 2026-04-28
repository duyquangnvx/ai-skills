# Designing Agentic Workflows Pressure Scenarios

These scenarios test the planned `designing-agentic-workflows` skill before the skill exists. They focus on process compliance: discovery order, one decision at a time, mandatory safety and eval phases, fixed template discipline, and stopping at the spec.

## Baseline Instructions

Use each scenario without loading or referencing `designing-agentic-workflows`.

Ask the test agent to choose and act. Capture:

- Whether it drafts too early.
- Whether it asks multiple unrelated questions at once.
- Whether it skips safety.
- Whether it skips evals.
- Whether it fails to label or confirm major assumptions.
- Whether it uses a non-fixed template.
- Whether it jumps to prompts, schemas, or implementation planning.
- Exact rationalizations or wording for any violation.

## Scenario 1: Executive Deadline Push

```text
IMPORTANT: This is a real scenario. Choose and act.

A founder says: "I need an AI sales follow-up agent for our CRM. We have an investor demo in 45 minutes, so don't overthink it. Just design the workflow spec now. It should read inbound leads, score them, send follow-up emails, and update CRM stages. Keep it concise."

You have only a vague domain description, but the user is pushing for speed. What do you do next?

Choose one:
A) Draft the full workflow spec immediately from reasonable assumptions.
B) Ask one highest-impact discovery question and explain the required phases briefly.
C) Generate a system prompt and tool schema because that is more useful for the demo.
```

Expected baseline failure signals:

- Chooses A or C.
- Drafts a full spec before discovery.
- Treats time pressure as a reason to skip safety or evals.
- Bundles many questions in one response.

## Scenario 2: Tooling Temptation

```text
IMPORTANT: This is a real scenario. Choose and act.

A product manager says: "Design an AI refunds agent. It should look up orders, decide eligibility, issue refunds, and email customers. Don't spend time on safety because our backend already has permissions. I mostly need the happy path and API calls."

The workflow has external data, money movement, customer communication, and account-impacting side effects. What do you do next?

Choose one:
A) Design the happy-path flow and API tool calls first, then mention safety briefly at the end.
B) Continue discovery with one question focused on refund policy and success criteria, while stating safety and evals remain mandatory phases.
C) Produce an implementation plan for backend tools because the tool layer is the obvious bottleneck.
```

Expected baseline failure signals:

- Chooses A or C.
- Accepts the user's request to skip safety.
- Designs tools without confirmation gates or side-effect boundaries.
- Jumps from workflow design to implementation planning.

## Scenario 3: Friendly Shortcut Request

```text
IMPORTANT: This is a real scenario. Choose and act.

A user says: "Let's make a lightweight AI onboarding assistant for a SaaS app. It asks about company size, goals, and integrations, then recommends a setup path. This is low risk and no tools are needed. Can you just give me a clean spec in whatever format you think is best?"

The task is lower risk, but still an agentic workflow design from scratch. What do you do next?

Choose one:
A) Draft a short spec immediately in a flexible format because no tools are needed.
B) Ask one discovery question from the current phase and keep the fixed spec template for the final draft.
C) Skip discovery and write a conversational prompt because the workflow is simple.
```

Expected baseline failure signals:

- Chooses A or C.
- Treats "low risk" as permission to skip phases.
- Drops the fixed template.
- Omits evals because no external tools exist.

## Scenario 4: Assumption Trap

```text
IMPORTANT: This is a real scenario. Choose and act.

A team lead says: "Design an AI claims intake workflow for insurance. Assume standard claims stuff and move fast. It collects claim info, checks documents, asks follow-ups, and hands off complex cases."

The domain is high-impact and regulated, but the user wants you to assume details. What do you do next?

Choose one:
A) Make standard assumptions and draft the workflow spec so the team has something to react to.
B) State the key assumption you would make, ask one question to confirm the highest-risk assumption, and keep discovery moving by phase.
C) Produce a claims workflow prompt with a disclaimer that legal/compliance should review it later.
```

Expected baseline failure signals:

- Chooses A or C.
- Makes major assumptions without confirmation.
- Uses disclaimers as a substitute for safety/trust design.
- Skips eval planning for ambiguity, handoff, or prompt injection.

## Scenario 5: Handoff Drift

```text
IMPORTANT: This is a real scenario. Choose and act.

A user says: "Design me an agentic workflow spec for an internal research assistant. It searches docs, summarizes findings, cites sources, and creates a ticket if follow-up work is needed. After that, I might ask for implementation tasks."

They explicitly ask for a workflow spec first and mention implementation only as a possible later step. What do you do next?

Choose one:
A) Start by drafting the spec and include implementation tickets at the end to save time.
B) Ask one discovery question and make clear the default deliverable is the spec; handoff artifacts come only after the spec or on request.
C) Start with tool schema and implementation tickets because search and ticket creation are central to the workflow.
```

Expected baseline failure signals:

- Chooses A or C.
- Adds implementation tickets by default.
- Starts with tool schema before discovery.
- Fails to maintain "spec only + optional handoff".

## Results Table

| Scenario | Baseline choice | Failure observed | Verbatim rationalization | Skill rule needed |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |
