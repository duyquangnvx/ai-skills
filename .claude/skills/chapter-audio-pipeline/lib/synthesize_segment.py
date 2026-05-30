"""Synthesize one segment's audio by running the speaker's TTS command.

Usage:
    python synthesize_segment.py --segments <segments.json> \
                                  --speakers <speakers.json> \
                                  --index <N> \
                                  --output <audio/seg-NNN.wav>
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


def synthesize_segment(
    segments_path: Path,
    speakers_path: Path,
    index: int,
    output: Path,
) -> None:
    segments = json.loads(segments_path.read_text(encoding="utf-8"))
    speakers = json.loads(speakers_path.read_text(encoding="utf-8"))

    segment = segments[index]
    speaker_id = segment["speakerId"]
    text = segment["text"]

    if speaker_id not in speakers:
        raise KeyError(f"speakerId {speaker_id!r} missing from speakers.json")

    template = speakers[speaker_id]["command"]
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_output = output.with_suffix(output.suffix + ".tmp")

    # Tokenize template, then substitute placeholders per token so quoting is preserved
    # and the text/path are passed as single argv entries (not re-parsed by the shell).
    tokens = shlex.split(template, posix=True)
    argv: list[str] = []
    for tok in tokens:
        if tok == "{text}":
            argv.append(text)
        elif tok == "{output}":
            argv.append(str(tmp_output))
        else:
            argv.append(
                tok.replace("{text}", text).replace("{output}", str(tmp_output))
            )

    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            argv,
            output=result.stdout,
            stderr=result.stderr,
        )

    if not tmp_output.exists() or tmp_output.stat().st_size == 0:
        raise RuntimeError(
            f"TTS command exited 0 but produced no audio at {tmp_output}. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    tmp_output.replace(output)


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

    # Skip if audio already exists (resume support).
    if args.output.exists() and args.output.stat().st_size > 0:
        return

    try:
        synthesize_segment(args.segments, args.speakers, args.index, args.output)
    except subprocess.CalledProcessError as exc:
        _write_error(
            args.output,
            f"CalledProcessError exit={exc.returncode}\n"
            f"stdout: {exc.output}\nstderr: {exc.stderr}\n",
        )
        raise SystemExit(1) from exc
    except Exception as exc:
        _write_error(args.output, f"{type(exc).__name__}: {exc}\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
