# Context Anti-Patterns

Common context engineering failures, how to recognize them, and how to fix them.

---

## 1. Context stuffing

**Symptom**: Agent outputs become vague, generic, or miss important details despite having "all the information."

**Cause**: Too much information crammed into context. The model's attention is spread thin across thousands of tokens, diluting focus on what matters.

**Fix**:
- Audit every item in context: does removing it degrade output?
- Move large reference data to external files, load just-in-time
- Replace full documents with summaries + retrieval option
- Rule of thumb: if context exceeds 50% of window capacity and performance is degrading, start cutting

**Example**:
```
❌ Pre-load entire 200-page API documentation into context
✅ Pre-load API summary (endpoints list + one-line descriptions)
   Agent reads specific endpoint docs just-in-time when needed
```

---

## 2. Lost-in-the-middle

**Symptom**: Agent follows instructions at the beginning and end of the prompt but ignores rules stated in the middle.

**Cause**: Transformer attention is U-shaped — beginning and end of context receive stronger attention than the middle. Information placed in the middle is more likely to be under-attended.

**Fix**:
- Place critical instructions at the **beginning** (system prompt opening)
- Place current task data at the **end** (closest to generation point)
- Use structural markers (XML tags, markdown headers) to make middle content scannable
- For very long contexts, repeat critical rules at the end as a reminder

---

## 3. Instruction-context clash

**Symptom**: Agent behaves inconsistently — sometimes follows instructions, sometimes contradicts them.

**Cause**: Retrieved context or message history contains information that conflicts with system instructions. The model can't reconcile contradictory signals.

**Fix**:
- Audit retrieved content for contradictions with system prompt
- Add explicit priority: "When retrieved data conflicts with these instructions, follow these instructions."
- Filter retrieved content before injection — remove items that contradict established rules
- In few-shot examples, ensure examples never demonstrate behavior you've forbidden in instructions

---

## 4. Tool set confusion

**Symptom**: Agent calls the wrong tool, calls tools unnecessarily, or fails to call tools when it should.

**Cause**: Tool definitions overlap in functionality, have ambiguous descriptions, or the tool set is too large for the agent to reason about effectively.

**Fix**:
- **Reduce tool count**: merge overlapping tools, remove rarely used ones
- **Clarify descriptions**: each tool description should make its purpose unambiguous
- **Add "when to use" and "when NOT to use"** to each tool description
- **Test**: if a human engineer can't instantly say which tool fits a scenario, simplify the tool set
- Consider: 3-5 well-designed tools usually outperform 15+ narrow tools

**Example**:
```
❌ Tools: search_web, search_docs, search_knowledge_base, find_info, lookup_data
   (Agent can't distinguish between these)

✅ Tools: search(query, source=["web"|"docs"|"kb"])
   (Single tool, clear parameter for source selection)
```

---

## 5. Stale context

**Symptom**: Agent acts on outdated information, makes decisions based on old state, or repeats already-completed work.

**Cause**: Context contains old data that hasn't been updated or cleared. Common in long-running sessions or multi-session systems without proper state management.

**Fix**:
- Implement compaction to clear old tool results and superseded messages
- Use structured note-taking: agent updates a status file at checkpoints, reads fresh status at session start
- Add timestamps to all persisted data — agent can prioritize recent over old
- Clear or summarize old tool outputs after acting on them

---

## 6. Memory amnesia

**Symptom**: Agent loses all context between sessions. Asks the same questions again, re-discovers same information, makes contradictory decisions.

**Cause**: No external memory system. Everything lives only in the context window, which resets between sessions.

**Fix**:
- Design external memory files (decision log, entity registry, progress tracker)
- Define explicit update triggers (agent must update files at defined checkpoints)
- At session start, pre-load memory files or provide them as accessible references
- See strategies.md → Structured note-taking and Cross-session state patterns

---

## 7. Noise injection via RAG

**Symptom**: Agent's outputs become less focused or occasionally hallucinate facts after RAG retrieval is added.

**Cause**: Retrieved documents contain irrelevant passages that the model tries to incorporate. Semantic similarity doesn't guarantee task relevance — a document can be "about" the right topic but contain information that distracts from the specific question.

**Fix**:
- Reduce chunk size for more precise retrieval
- Add a relevance filter between retrieval and injection: have the model (or a lightweight classifier) assess whether retrieved chunks actually help answer the current question
- Limit number of retrieved chunks (3-5 focused chunks > 10 noisy chunks)
- Include retrieval source metadata so the agent can assess credibility

---

## 8. Prompt archaeology

**Symptom**: System prompt has grown to thousands of tokens through accumulated patches, edge case handlers, and "just add another rule" fixes. Agent behavior is brittle and unpredictable.

**Cause**: Treating the system prompt as a catch-all for every behavioral issue. Each fix adds tokens but also adds potential contradictions and dilutes attention from core instructions.

**Fix**:
- Rewrite the system prompt from scratch based on actual failure modes
- Extract edge case handling into conditional context (loaded only when relevant)
- Use FPL to structure complex logic instead of prose paragraphs
- Track every instruction addition with a reason — if the reason is no longer valid, remove it
- Target: system prompt should be readable by a human in under 2 minutes

---

## 9. Example overload

**Symptom**: Agent outputs are correct but overly rigid, or agent fails on inputs that don't match examples closely.

**Cause**: Too many few-shot examples that cover edge cases. Agent pattern-matches to examples instead of following instructions.

**Fix**:
- Curate 2-3 diverse, canonical examples that show the core pattern
- Remove edge case examples — handle those with clear instructions instead
- Examples are "pictures worth a thousand words" — use them to show shape of desired output, not to encode every rule

---

## 10. Invisible context pollution

**Symptom**: Agent performance degrades gradually over a long session with no obvious cause.

**Cause**: Accumulated tool outputs, error messages, and conversational debris silently consume the attention budget. No single item is problematic, but the aggregate noise drowns out signal.

**Fix**:
- Implement regular compaction (not just at window limit — schedule it)
- Clear tool outputs after they've been acted on
- Monitor context size over time — if it grows linearly, you need compaction
- Use observation masking: replace verbose outputs with summaries, store full data externally

---

## Diagnostic checklist

When an agent is underperforming, check these in order:

1. **Is the context too large?** → Audit and trim, implement compaction
2. **Is critical info in the middle?** → Move to beginning/end
3. **Are tools overlapping or ambiguous?** → Simplify tool set
4. **Is retrieved context relevant?** → Add filtering, reduce chunks
5. **Is old data polluting new decisions?** → Implement state management
6. **Is the system prompt trying to do too much?** → Rewrite at right altitude
7. **Are there contradictions between layers?** → Audit for clashes
8. **Is there memory across sessions?** → Add external memory files