"""Concatenate per-segment audio files into one chapter audio file.

Walks segments.json in order. For each segment, locates `seg-<NNN>.<ext>` in
the audio directory. If that file is missing or a matching `.error` marker
exists, substitutes a short silence clip and continues.

Usage:
    python concat_chapter.py --audio-dir <audio/> \
                              --segments <segments.json> \
                              --output <chapter.wav>

Example:
    python lib/concat_chapter.py \
        --audio-dir data/silver-rain/chapters/ch001/audio \
        --segments data/silver-rain/chapters/ch001/segments.json \
        --output data/silver-rain/chapters/ch001/chapter.wav
"""

from __future__ import annotations

import argparse
from pathlib import Path


def concat_chapter(
    audio_dir: Path,
    segments_path: Path,
    output: Path,
) -> None:
    """Merge segment audio files in `segments.json` order into one file.

    Args:
        audio_dir: Directory containing seg-<NNN>.<ext> and optional .error markers.
        segments_path: Path to segments.json — drives expected count and ordering.
        output: Destination merged audio file. Parent directory is created if missing.

    Raises:
        FileNotFoundError: If no segment audio files exist at all (every segment failed).
        subprocess.CalledProcessError: If the merge tool (ffmpeg, sox, pydub backend) fails.
    """
    raise NotImplementedError(
        "Domain logic — implement based on: walk segments.json in order, for each "
        "index look up audio_dir / f'seg-{i:03d}.<ext>'. If that file is missing or "
        "an .error marker exists, substitute a 0.5s silence clip. Concatenate the "
        "resulting list via ffmpeg's concat demuxer, sox, or pydub. Write to `output`."
    )


def _write_error(output: Path, message: str) -> None:
    error_path = output.with_suffix(output.suffix + ".error")
    error_path.parent.mkdir(parents=True, exist_ok=True)
    error_path.write_text(message, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--segments", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        concat_chapter(args.audio_dir, args.segments, args.output)
    except Exception as exc:
        _write_error(args.output, f"{type(exc).__name__}: {exc}\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
