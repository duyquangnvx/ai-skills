---
name: chapter-audio-pipeline
description: |
  Generate chapter-level audio files from raw novel chapters via a four-phase pipeline — polish → segment → synthesize → concat. Polish rewrites raw prose for audio readability. Segment splits the chapter into ordered {speakerId, text} blocks, attributing dialogue to characters and narration to the narrator. Synthesize fans out one TTS call per segment using a per-speaker CLI command template stored in speakers.json. Concat merges the audio chunks into one chapter audio file. Cross-chapter speaker identity is preserved in speakers.json so the same character keeps the same voice across the whole novel. Use when the user wants to turn a multi-chapter novel into audio one chapter at a time. Trigger phrases include "process chapter X audio", "make audio for chapter Y", "synthesize chapter Z", "tạo audio cho chương N", "xử lý audio chương N", "process next chapter audio", "process all chapters audio".
---

# Chapter Audio Pipeline

Turn raw novel chapters into chapter-level audio via polish → segment → synthesize → concat, one chapter at a time. Cross-chapter speaker identity preserved in `speakers.json`.

## Project layout

```
data/
└── <novel>/
    ├── speakers.json                     ← cross-chapter speaker registry
    └── chapters/
        └── <chapter-id>/
            ├── raw.txt                   ← input (user supplies, already split)
            ├── polished.txt              ← Phase 1 output
            ├── segments.json             ← Phase 2 output
            ├── audio/
            │   ├── seg-000.wav           ← Phase 3 output (one per segment)
            │   ├── seg-000.error         ← if synthesis failed
            │   ├── seg-001.wav
            │   └── ...
            └── chapter.wav               ← Phase 4 output (final)
```

## Speakers registry

`data/<novel>/speakers.json` maps each speaker id to a TTS command template:

```json
{
  "narrator": {
    "description": "Default narrator voice",
    "command": "edge-tts --voice en-US-AriaNeural --text {text} --write-media {output}"
  },
  "char-1": {
    "description": "Protagonist — calm male voice",
    "command": "edge-tts --voice en-US-GuyNeural --text {text} --write-media {output}"
  }
}
```

The `command` field uses `{text}` and `{output}` placeholders. Any TTS CLI works (edge-tts, piper, elevenlabs CLI, custom wrappers). Pick one CLI per speaker — the helper substitutes the placeholders and runs the command.

The segmenter agent adds new speakers it discovers to this file, copying the narrator's command as a default. The user edits voice mappings between runs.

## Commands

The user invokes the skill with prompts like:

- "process chapter <id> of <novel>" — run all four phases on one chapter
- "process next chapter" — find the first chapter without `chapter.wav` and process it
- "process all chapters" — iterate sequentially over chapters missing `chapter.wav`
- "resume chapter <id>" — pick up from the latest existing intermediate output
- "rerun phase N chapter <id>" — delete that phase's output and rerun

## Timeout configuration

| Layer | Setting | Notes |
|---|---|---|
| max_turns per agent | polisher 25 / segmenter 20 | Tune after first runs |
| Wall-clock per phase | polish 480s / segment 300s / synthesize 900s / concat 300s | Move on with what completed |

Bash timeout and container deadline are omitted — this skill targets interactive runs. Add them if scheduling unattended.

## Resume

If a previous run left intermediate files in `data/<novel>/chapters/<id>/`, the skill detects them and skips phases whose outputs are already present.

To force a rerun of a specific phase, delete the corresponding output:

| Phase | Delete to rerun |
|---|---|
| 1 polish | `polished.txt` |
| 2 segment | `segments.json` |
| 3 synthesize | `audio/seg-*.wav` and `audio/seg-*.error` (or just the failed ones) |
| 4 concat | `chapter.wav` |

Then re-invoke the skill on that chapter.

---

## Phase 1: Polish

**Goal:** Improve prose readability for audio narration — refine wording, smooth rhythm, add sensible atmospheric detail without changing the plot.

**Inputs:** `data/<novel>/chapters/<chapter-id>/raw.txt`

**Outputs:** `polished.txt` (success) or `polished.txt.error` (failure)

### Step 1.1: Run polisher

Single agent invocation:

```
Task(subagent_type: "polisher", prompt: "Polish chapter <chapter-id> of novel <novel>")
```

The polisher reads `raw.txt`, rewrites it, writes `polished.txt`. No fan-out.

### On failure

Log `polished.txt.error`. Skip the rest of the pipeline for this chapter and continue with the next one (if running `process all`). The user can fix `raw.txt` and rerun.

---

## Phase 2: Segment

**Goal:** Split the polished chapter into ordered `{speakerId, text}` segments. Narrator narration is one speaker, each character is another.

**Inputs:** `polished.txt`, `data/<novel>/speakers.json`

**Outputs:** `segments.json` (success) or `segments.json.error` (failure). May also update `speakers.json` if new characters appear.

### Step 2.1: Run segmenter

Single agent invocation:

```
Task(subagent_type: "segmenter", prompt: "Segment chapter <chapter-id> of novel <novel>")
```

The segmenter reads the polished text, attributes dialogue to speakers using context, and adds any new speakers it discovers to `speakers.json` (copying the narrator's command as a default).

### On failure

Log `segments.json.error`. Skip the rest of the pipeline for this chapter. The user can fix `polished.txt` or `speakers.json` and rerun.

---

## Phase 3: Synthesize

**Goal:** Generate one audio file per segment by invoking the TTS command for that segment's speaker.

**Inputs:** `segments.json`, `speakers.json`

**Outputs:** `audio/seg-<NNN>.wav` (success) or `audio/seg-<NNN>.error` (failure) — one per segment.

### Step 3.1: Fan out per segment

Read `segments.json` to determine N. Spawn N synthesizer tasks in background — each calls the helper:

```bash
python lib/synthesize_segment.py \
  --segments data/<novel>/chapters/<chapter-id>/segments.json \
  --speakers data/<novel>/speakers.json \
  --index <N> \
  --output data/<novel>/chapters/<chapter-id>/audio/seg-<NNN>.wav
```

Synthesis is mechanical — no subagent, just a Python helper invoked many times in parallel from the orchestrator (or via `xargs -P` if you prefer raw shell parallelism).

After spawning, poll the filesystem:

```bash
EXPECTED=$(python -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" \
  data/<novel>/chapters/<chapter-id>/segments.json)
TIMEOUT=900
ELAPSED=0
START=$(date +%s)

while [ $ELAPSED -lt $TIMEOUT ]; do
  SUCCESS=$(ls -1 data/<novel>/chapters/<chapter-id>/audio/seg-*.wav 2>/dev/null | wc -l)
  ERRORS=$(ls -1 data/<novel>/chapters/<chapter-id>/audio/seg-*.error 2>/dev/null | wc -l)
  if [ "$((SUCCESS + ERRORS))" -ge "$EXPECTED" ]; then break; fi
  sleep 5
  ELAPSED=$(( $(date +%s) - START ))
done

echo "Phase 3 complete: $SUCCESS ok, $ERRORS failed (of $EXPECTED)"
```

### On failure

Each segment fails independently. A `seg-NNN.error` marker keeps the rest of the chapter intact. Phase 4 substitutes a short silence for missing segments and continues.

To retry only the failed segments: delete their `.error` files and re-invoke the skill — the helper detects which segments are missing and only synthesizes those.

---

## Phase 4: Concat

**Goal:** Merge `audio/seg-*.wav` into a single `chapter.wav` in segment order. Substitute a short silence for any segment that has a `.error` marker or missing file.

**Inputs:** `audio/seg-*.wav`, `segments.json` (for ordering and count)

**Outputs:** `chapter.wav` (success) or `chapter.wav.error` (failure)

### Step 4.1: Run concat helper

```bash
python lib/concat_chapter.py \
  --audio-dir data/<novel>/chapters/<chapter-id>/audio \
  --segments data/<novel>/chapters/<chapter-id>/segments.json \
  --output data/<novel>/chapters/<chapter-id>/chapter.wav
```

### On failure

Log `chapter.wav.error`. Per-segment audio chunks remain on disk for manual concat or re-run after fixing the helper.

---

## Failure handling

- Polish fails: log failure, skip chapter, continue with next chapter (if batch).
- Segment fails: log failure, skip chapter, continue with next chapter.
- Synthesize fails on segment X: log `.error`, concat substitutes silence and continues.
- Concat fails: log failure, keep per-segment audio chunks intact.

Never fail the entire skill due to individual chapter or segment failures. Always produce a report listing which chapters produced `chapter.wav`, which segments failed inside any chapter, and where every artifact lives on disk.

## Output delivery

This is an interactive skill — output lands on disk under `data/<novel>/chapters/<chapter-id>/chapter.wav`. The skill ends by printing absolute paths of produced audio files and a per-chapter summary (segments synthesized vs. failed).

## Self-improvement note

If you discover that an instruction in this skill was wrong, ambiguous, or incomplete during execution, fix it inline and continue. The fix is part of the run — commit it back with the report.
