# Knowing It Works: The Standard

Applies to every surface. Reading a prompt and finding it sensible tells you nothing about whether it changes behavior; a surface is verified when you have watched the model behave differently with and without it.

## The shared primitive

Every verification in this skill is one operation at a different scale: **ablate the line, run a scenario where it should matter, compare.** That is the same question as "does this line change what the model does next", so the budget audit, the pressure scenario, and the eval run are not three methods — they are one method applied to a word, a rule, and a catalog.

Three rules make it trustworthy:

- **Always run the no-guidance control.** If the model already does the right thing without your line, there is nothing to fix and the line is cost with no benefit. Delete it and move on. Most disputes about wording are settled by discovering the control never failed.
- **Repeat.** A single sample is noise. Run enough of each arm to see a distribution, and read the flagged outputs yourself — automated scoring counts template echoes and quoted counter-examples as hits, overstating both failure and success.
- **Treat variance as a result.** When guidance lands, runs converge on the same shape. Five different readings across five runs means the wording is not binding, and adding words rarely fixes it — the form is wrong, and `instructions.md` covers which form fits which failure.

## Per-surface instantiation

**Instructions.** Pressure scenarios: put the rule in tension with time, sunk cost, an authority telling the agent to skip it, or a long session. A rule that holds only when nothing is pushing against it has not been tested. Capture the rationalizations verbatim and answer them by name.

**Tool layer.** Realistic multi-step tasks over real data, not single-call smoke tests. "Search the logs for customer_id=9182" proves nothing; "customer 9182 says they were charged three times — find the relevant logs, determine whether other customers were affected, and summarize the likely cause" exercises selection, argument construction, response reading, and recovery.

**Context lifecycle.** The failures here are invisible in a single transcript because they are drift, so they need runs long enough to drift. Measure recall of a decision across a compaction boundary; behavior when a file read at turn 3 is edited at turn 30; whether memory is read at the moments it should be; whether the agent reports a stale conclusion as current; whether a refused stale write leads to escalation or to a clobber. Include the case where nothing changed, so you can see the cost of the machinery when it is not needed.

**Trust and safety.** Adversarial content in every channel the session ingests, and a check that a denial stays a denial rather than becoming a detour.

## The eval loop

Standard eval hygiene applies — prototype in the real runtime, change one thing at a time, hold out tasks so you are not fitting the set. Four things are specific to this material:

- **Write tasks that would fail for the reason you care about.** A task the design passes for unrelated reasons measures nothing, and it is the most common way an eval suite reads green while the interface is broken.
- **Do not pin the verifier to one correct tool-call path** when several are valid. You are measuring whether the agent got there, not whether it took your route.
- **Log observable diagnostics, never hidden reasoning.** Use the reasoning summaries the runtime exposes; do not build a design that requires private chain-of-thought. A useful visible block: goal, selected tool, one-sentence reason, parameters, expected result, uncertainty, observed issue, next action.
- **Read transcripts, not just scores.** The failures that matter here — redundant reads, oversized results, ignored errors, acting on a fact from twenty turns ago, stopping early — mostly do not change the final answer, which is exactly why they survive.

Agents can review traces and propose changes: names, schemas, response shapes, validation, error text, disambiguation, and the evals that would prove the fix. Do not accept a suggestion because it reads well; run it.

## What to measure

Final accuracy hides most failure classes. Instrument every axis on which the design can degrade without the answer changing:

- Task success, and cost per *successful* task.
- Tool-call count, invalid-call rate, retry count.
- Token consumption, latency, time to first useful action.
- Cache hit rate, and context length at turn N.
- Recall of decisions and constraints across a compaction boundary.
- Re-read rate after external change, and stale-claim rate.
- Human interventions, approval prompts, safety blocks.

High token use suggests response bloat or too many chained calls. A high invalid-call rate points at schemas, names, descriptions, or error text. Rising context length with flat task success is debris. A stale-claim that survives to the final answer is the one failure the other metrics will not show you.

## Review criteria

When judging qualitatively rather than measuring:

- **Clarity**: can an agent tell when to use this over its siblings?
- **Completeness**: does the contract carry every convention a caller needs — formats, defaults, side effects?
- **Recoverability**: does every error say what to change before retrying, and do the errors that should be terminal read as terminal?
- **Efficiency**: are responses bounded, with verbosity options where size genuinely varies?
- **Consistency**: do names, parameters, and enums follow the catalog's conventions?
- **Groundedness**: can the agent tell how old what it is reading is, and what it was derived from?

## Cross-surface checks

- [ ] No rule, field, or workflow documented in two homes.
- [ ] Untrusted input is separated from trusted instructions in every ingest channel.
- [ ] Heavy references, schemas, and examples load on demand.
- [ ] Changes are verified by ablation against a control, not by reading them.
- [ ] Long-session behavior is measured, not assumed.
- [ ] Exactly one approval gate per irreversible action.
