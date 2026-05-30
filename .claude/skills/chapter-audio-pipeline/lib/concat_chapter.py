"""Concatenate per-segment audio files into one chapter audio file.

Walks segments.json in order. For each segment, locates `seg-<NNN>.<ext>` in
the audio directory. If that file is missing or a matching `.error` marker
exists, substitutes a short silence clip and continues.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SILENCE_SECONDS = 0.5
AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".ogg", ".opus", ".flac")


def _find_segment_audio(audio_dir: Path, index: int) -> Path | None:
    stem = f"seg-{index:03d}"
    if (audio_dir / f"{stem}.error").exists():
        return None
    for ext in AUDIO_EXTS:
        candidate = audio_dir / f"{stem}{ext}"
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    return None


def _make_silence(path: Path, duration: float, sample_rate: int) -> None:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate={sample_rate}",
        "-t", str(duration),
        "-c:a", "pcm_s16le",
        str(path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _probe_sample_rate(path: Path) -> int:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate",
        "-of", "default=nw=1:nk=1",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return int(res.stdout.strip() or 24000)


def concat_chapter(
    audio_dir: Path,
    segments_path: Path,
    output: Path,
) -> None:
    segments = json.loads(segments_path.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)

    real_files = [
        p for i in range(len(segments))
        if (p := _find_segment_audio(audio_dir, i)) is not None
    ]
    if not real_files:
        raise FileNotFoundError(
            f"No segment audio files found under {audio_dir}; every segment failed"
        )

    sample_rate = _probe_sample_rate(real_files[0])

    with tempfile.TemporaryDirectory(prefix="concat_chapter_") as tmpdir:
        tmp = Path(tmpdir)
        silence_path = tmp / "silence.wav"
        _make_silence(silence_path, SILENCE_SECONDS, sample_rate)

        # Re-encode every input to a uniform PCM WAV so the concat demuxer
        # (which requires identical codec params) is happy regardless of what
        # the upstream TTS produced.
        list_path = tmp / "concat.txt"
        with list_path.open("w", encoding="utf-8") as fh:
            for i in range(len(segments)):
                src = _find_segment_audio(audio_dir, i)
                if src is None:
                    fh.write(f"file '{silence_path.as_posix()}'\n")
                    continue
                normalized = tmp / f"seg-{i:03d}.wav"
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(src),
                        "-ar", str(sample_rate),
                        "-ac", "1",
                        "-c:a", "pcm_s16le",
                        str(normalized),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                fh.write(f"file '{normalized.as_posix()}'\n")

        tmp_output = output.with_suffix(output.suffix + ".tmp")
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c:a", "pcm_s16le",
                "-f", "wav",
                str(tmp_output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        tmp_output.replace(output)


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
    except subprocess.CalledProcessError as exc:
        _write_error(
            args.output,
            f"CalledProcessError exit={exc.returncode}\n"
            f"stdout: {exc.stdout}\nstderr: {exc.stderr}\n",
        )
        raise SystemExit(1) from exc
    except Exception as exc:
        _write_error(args.output, f"{type(exc).__name__}: {exc}\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
