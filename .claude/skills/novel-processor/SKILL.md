---
name: novel-processor
description: Process Chinese novels chapter-by-chapter through a 4-step pipeline (translate → refine → enhance visual → enhance audio) while maintaining consistent terminology, character names, honorifics, and style across the entire novel. Use when user mentions novel translation, chapter processing, story translation from Chinese, or any multi-chapter text processing that requires cross-chapter consistency. Also triggers when user uploads a .txt file containing a Chinese novel or asks about processing chapters.
---

# Novel Processor

Process long novels chapter-by-chapter through a 4-step pipeline while maintaining cross-chapter consistency via shared context files.

## Project structure

```
<project>/
├── source/novel.txt                    ← original file
├── guides/
│   ├── 01-translate.md                 ← user-provided
│   ├── 02-refine.md
│   ├── 03-enhance-visual.md
│   └── 04-enhance-audio.md
├── context/                            ← grows across chapters
│   ├── glossary.md
│   ├── characters.md
│   └── style.md
├── chapters/
│   ├── raw/chapter-001.txt ...
│   └── processed/chapter-001/
│       ├── 01-translated.txt
│       ├── 02-refined.txt
│       ├── 03-enhanced-visual.txt
│       └── 04-enhanced-audio.txt
└── project.md                          ← progress tracker
```

## Commands

The user can say things like:
- "init project" / "khởi tạo dự án" → Phase 0
- "process chapter 5" / "xử lý chương 5" → Process single chapter
- "process chapters 5-10" / "xử lý chương 5 đến 10" → Batch
- "process next" / "xử lý tiếp" → Next unprocessed chapter
- "process all" → All remaining chapters
- "update glossary" / "cập nhật thuật ngữ" → Manual context edit
- "change preset" / "đổi preset" → Re-select preset, regenerate style.md defaults
- "status" / "tiến độ" → Show progress
- "rerun step 2 chapter 3" → Reprocess a specific step

Interpret flexibly. The user may speak Vietnamese or English.

---

## Phase 0: Project initialization

Run once when user provides a novel file.

### Step 0.1 — Setup

Create the project structure above. Copy novel.txt to source/. Confirm guide files exist in guides/ (user must provide these). If guides are missing, ask the user to provide them before proceeding.

### Step 0.2 — Detect chapters

Chapter markers vary wildly across novels. Read the first ~5000 characters of the file and look for patterns.

Common patterns (check in order):
- `第X章` / `第X節` (Chinese chapter markers)
- `Chapter X` / `CHAPTER X`
- Lines matching: number + period/colon + title (e.g., `1. 风起云涌`)
- Lines that are short (<30 chars), preceded by blank line, followed by body text
- Consistent separator patterns (e.g., `---`, `***`, `===`)
- `卷X` (volume markers — these group chapters, not replace them)

Process:
1. Scan full file for candidate pattern
2. Count matches — if reasonable (>3 chapters), present to user:
   ```
   Detected pattern: 第X章
   Found 127 chapters
   First 3: 第一章 风起云涌 / 第二章 初入江湖 / 第三章 血战
   Last: 第一百二十七章 终局
   ```
3. Ask user to confirm or provide custom pattern
4. If no pattern found, show first ~2000 chars and ask user to identify the delimiter

### Step 0.3 — Split chapters

Split novel.txt by confirmed pattern. Save as:
- `chapters/raw/chapter-001.txt` (zero-padded to 3 digits)
- Each file includes the chapter heading as first line

Write `project.md`:
```markdown
# Project: <novel name>
Preset: <preset_name>
Total chapters: N
Processed: 0/N

| Chapter | Status | Last step | Updated |
|---------|--------|-----------|---------|
| 001     | pending | -        | -       |
| 002     | pending | -        | -       |
...
```

### Step 0.4 — Select translation preset

Before building context, determine the translation style. See `references/presets.md` for all available presets.

1. Auto-detect genre from first 3 chapters:
   - Cultivation terms (修炼, 灵力, 丹田...) → suggest tu_tien presets
   - Martial arts terms (江湖, 武功, 内功...) → suggest kiem_hiep
   - Modern setting (公司, 手机, 咖啡...) → suggest do_thi presets
   - Mixed or unclear → ask user

2. Present preset options with pronoun examples so user can see the difference:
   ```
   Detected: cultivation novel (修仙)

   Presets available:
   1. Tu tiên — Cổ phong
      (ta/ngươi, hắn/nàng, full Hán Việt, trang trọng)
      Example: "Ngươi dám xúc phạm ta? Hắn lạnh lùng nhìn đối phương."

   2. Tu tiên — Hiện đại hóa
      (ta/anh, hắn/anh ta, pha trộn, dễ đọc)
      Example: "Anh dám xúc phạm ta sao? Anh ta lạnh lùng nhìn đối phương."

   3. Custom (tự cấu hình)

   Choose [1/2/3]:
   ```

3. Save choice to `project.md`:
   ```
   Preset: tu_tien_co_phong
   ```

4. Preset fills default values into style.md and provides the pronoun template for characters.md. These are starting points — user can edit any field after.

### Step 0.5 — Bootstrap context

Read chapters 1-3 raw text. Use the selected preset as baseline. Extract initial:

**glossary.md** — see `references/context-format.md` for format
- Character names (Chinese → Vietnamese transliteration/translation)
- Place names
- Cultivation terms / martial arts terms / domain-specific vocabulary
- Recurring phrases or titles

**characters.md** — see `references/context-format.md` for format
- Each character: name, role, key traits
- Relationships and how they address each other (xưng hô)
- Honorifics and titles used

**style.md** — see `references/context-format.md` for format
- Genre and tone detected
- Translation style decisions (e.g., keep Chinese terms? translate all?)
- Prose register (formal/classical/modern/casual)

Present all context to user for review. This is critical — mistakes here propagate to every chapter. Wait for user confirmation before proceeding.

---

## Phase 1: Chapter processing

### Pipeline for one chapter

Each step reads: guide file + context files + input text.
Each step outputs: one .txt file.

```
Step 1: TRANSLATE
  Read:  guides/01-translate.md + context/* + chapters/raw/chapter-N.txt
  Write: chapters/processed/chapter-N/01-translated.txt
  Then:  UPDATE CONTEXT (see below)

Step 2: REFINE
  Read:  guides/02-refine.md + context/* + 01-translated.txt
  Write: chapters/processed/chapter-N/02-refined.txt

Step 3: ENHANCE VISUAL
  Read:  guides/03-enhance-visual.md + context/* + 02-refined.txt
  Write: chapters/processed/chapter-N/03-enhanced-visual.txt

Step 4: ENHANCE AUDIO
  Read:  guides/04-enhance-audio.md + context/* + 03-enhanced-visual.txt
  Write: chapters/processed/chapter-N/04-enhanced-audio.txt
```

After all 4 steps: update project.md status for this chapter.

### Context update (after Step 1 only)

After translation, scan the translated text for:
1. **New terms** not in glossary.md → append with source chapter reference
2. **New characters** not in characters.md → add entry with relationship info if available
3. **Xưng hô changes** — new relationship dynamics that affect how characters address each other
4. **Style observations** — any new patterns worth noting

Format updates as diffs and show to user:
```
📝 Context updates from Chapter N:

GLOSSARY (+3 new):
  元婴期 → Nguyên Anh kỳ (cultivation stage, first seen ch.N)
  天火 → Thiên Hỏa (artifact name)
  灵石 → linh thạch (currency)

CHARACTERS (+1 new, 1 updated):
  [NEW] 苏瑶 → Tô Dao | Female | Disciple of sect leader
    - MC calls her: sư muội
    - She calls MC: sư huynh
  [UPDATED] 林峰: now revealed as elder's son

Confirm? (y/edit/skip)
```

If user confirms → write to context files.
If user edits → apply edits then write.
If user skips → don't update (user will handle manually).

In batch mode, accumulate updates and present at the end of each chapter's step 1, not at the end of the whole batch.

### Processing modes

**Single chapter**: "process chapter 5"
- Run pipeline for chapter 5 only
- Show context updates after step 1, wait for confirm
- Proceed through steps 2-4

**Batch**: "process chapters 5-10"
- For each chapter 5→10:
  - Run step 1, show context updates, auto-continue after brief pause
  - Run steps 2-4
  - Move to next chapter
- If user says "process all" → batch all remaining pending chapters

**Rerun**: "rerun step 2 chapter 3"
- Re-execute only that step using current context
- Useful when user updates context/guide and wants to regenerate

**Next**: "process next"
- Look at project.md, find first pending chapter, process it

### Handling long chapters

If a chapter exceeds ~3000 Chinese characters (roughly the limit for quality processing in one pass):
1. Split into segments at natural paragraph breaks
2. Process each segment through the current step
3. Concatenate segments for the output file
4. Maintain segment continuity — end of segment N is context for segment N+1

### Error handling

- If a guide file is missing → stop and tell user which guide is needed
- If chapter raw file not found → check project.md for valid range
- If context files don't exist → run Phase 0.4 first
- If processing fails mid-chapter → save whatever completed, mark chapter as "partial: step N" in project.md so user can resume

---

## Context file management

See `references/context-format.md` for detailed format specifications.

Key principles:
- Context files are append-only during processing (never delete existing entries)
- Every entry has a source chapter reference so user can trace decisions
- User can manually edit context files at any time — the skill respects manual edits
- Before processing any chapter, always read fresh context (don't cache)

---

## Progress reporting

When user asks for status, read project.md and report:
```
📖 <Novel Name>
Progress: 23/127 chapters (18%)
Last processed: Chapter 23 (all 4 steps complete)
Context: 156 glossary terms, 34 characters tracked

Next pending: Chapter 24
```