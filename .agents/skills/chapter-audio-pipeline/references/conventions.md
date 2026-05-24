# Conventions

## File layout

```
data/
└── <novel>/
    ├── speakers.json
    └── chapters/
        └── <chapter-id>/
            ├── raw.txt
            ├── polished.txt
            ├── segments.json
            ├── audio/
            │   ├── seg-NNN.wav
            │   └── seg-NNN.error
            └── chapter.wav
```

## Identifiers

| Identifier | Format | Example |
|---|---|---|
| `<novel>` | kebab-case slug, stable across runs | `silver-rain` |
| `<chapter-id>` | zero-padded number or kebab-case slug, sortable | `ch001`, `the-meeting` |
| Segment index | zero-padded to three digits | `seg-000`, `seg-042` |
| Speaker id | kebab-case, prefix characters with `char-` | `narrator`, `char-anna` |

## File formats

| File | Format |
|---|---|
| `raw.txt`, `polished.txt` | Plain UTF-8 text. User supplies `raw.txt`. Polisher writes `polished.txt`. |
| `segments.json` | JSON array of `{"speakerId": str, "text": str}` in reading order. |
| `speakers.json` | JSON object mapping `speakerId` → `{"description": str, "command": str}`. |
| Audio chunks and final | `.wav` by default. Change throughout (synth command + concat helper) if you want `.mp3` or another container. |

## Speaker command templates

The `command` field in `speakers.json` is a shell command template with two placeholders:

- `{text}` — replaced with the segment's text by the helper (helper handles shell-escape).
- `{output}` — replaced with the absolute output path.

Examples (pick whichever CLI is installed):

| CLI | Template |
|---|---|
| edge-tts (free, Microsoft) | `edge-tts --voice en-US-AriaNeural --text {text} --write-media {output}` |
| piper (offline) | `piper --model en_US-amy-medium.onnx --output_file {output} --text {text}` |
| elevenlabs CLI | `elevenlabs synth --voice-id <id> --text {text} -o {output}` |
| custom wrapper | `python tts_wrapper.py --voice narrator --text {text} --out {output}` |

Mix and match across speakers — the narrator can use edge-tts while a character uses elevenlabs, etc.

## Atomic write convention

Every file written by an agent or helper goes through a temp-and-rename:

```python
tmp = output.with_suffix(output.suffix + ".tmp")
tmp.write_text(payload, encoding="utf-8")
tmp.replace(output)
```

This prevents the orchestrator's polling code from observing a half-written file.

## Error files

`.error` files are plain text — error message plus any helpful context. They sit alongside the success file they would have replaced:

| Phase | Success | Error |
|---|---|---|
| 1 polish | `polished.txt` | `polished.txt.error` |
| 2 segment | `segments.json` | `segments.json.error` |
| 3 synthesize | `audio/seg-NNN.wav` | `audio/seg-NNN.error` |
| 4 concat | `chapter.wav` | `chapter.wav.error` |

The orchestrator's poll loop counts BOTH success and error files toward "task complete" — that's how a fan-out phase finishes when some segments fail.

## Cross-chapter consistency

`speakers.json` lives at `data/<novel>/speakers.json`, one per novel. It is read and updated by the segmenter, then read by the synthesizer. Voice mappings stay stable across chapters — same `char-anna` keeps the same voice in chapter 1 and chapter 50.

When the segmenter discovers a new character in chapter N:

1. Add an entry to `speakers.json` with a default `command` copied from `narrator`.
2. Emit segments referencing the new `speakerId`.
3. The user customizes the voice afterward — synthesis for that character uses whatever the user set.

If a character only appears in a later chapter, the entry will only exist from that chapter onward. The synthesizer will fail with `KeyError` if any earlier chapter references an unknown speaker — that's a signal the segmenter mis-attributed and the user needs to fix `segments.json` of the earlier chapter or add the speaker manually.

## What the helpers do NOT do

- `synthesize_segment.py` does not validate audio content, retry on rate limit, or post-process audio. Add those behaviors in the implementation if needed.
- `concat_chapter.py` does not normalize volume, apply crossfades, or insert chapter intro/outro. Add those if you want a more produced output.

Both helpers leave `NotImplementedError` for the user to fill in — the orchestration above does not depend on the exact backend chosen.
