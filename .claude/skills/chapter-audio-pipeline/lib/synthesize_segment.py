"""Synthesize one segment's audio by running the speaker's TTS command.

Usage:
    python synthesize_segment.py --segments <segments.json> \
                                  --speakers <speakers.json> \
                                  --index <N> \
                                  --output <audio/seg-NNN.wav>

Example:
    python lib/synthesize_segment.py \
        --segments data/silver-rain/chapters/ch001/segments.json \
        --speakers data/silver-rain/speakers.json \
        --index 3 \
        --output data/silver-rain/chapters/ch001/audio/seg-003.wav
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def synthesize_segment(
    segments_path: Path,
    speakers_path: Path,
    index: int,
    output: Path,
) -> None:
    """Run the TTS command for one segment and write the audio to `output`.

    Args:
        segments_path: Path to segments.json (a list of {speakerId, text}).
        speakers_path: Path to speakers.json (speakerId -> {description, command}).
        index: Zero-based segment index to synthesize.
        output: Destination audio file. Parent directory is created if missing.

    Raises:
        IndexError: If `index` is out of range for segments.json.
        KeyError: If the segment's speakerId is not present in speakers.json.
        subprocess.CalledProcessError: If the TTS command returns non-zero.
    """
    raise NotImplementedError(
        "Domain logic — implement based on: load segments[index], look up "
        "speakers[segment['speakerId']]['command'], substitute {text} and "
        "{output} placeholders, run via subprocess.run, raise on non-zero exit. "
        "Remember to shell-escape the text (or pass via stdin)."
    )


def _write_error(output: Path, message: str) -> None:
    error_path = output.with_suffix(output.suffix + ".error")
    error_path.parent.mkdir(parents=True, exist_ok=True)
    error_path.write_text(message, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--segments", type=Path, required=True)
    parser.add_argument("--speakers", type=Path, required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        synthesize_segment(args.segments, args.speakers, args.index, args.output)
    except Exception as exc:
        _write_error(args.output, f"{type(exc).__name__}: {exc}\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
