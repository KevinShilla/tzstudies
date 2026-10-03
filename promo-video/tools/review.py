"""Decode each finished frame; produce chronological review sheets and media checks."""

import json
import math
import re
import struct
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / "output" / "video"
QA = ROOT / "qa" / "full-review"
QA.mkdir(parents=True, exist_ok=True)
FONT = ImageFont.truetype(str(ROOT / "public" / "fonts" / "DM-Sans.ttf"), 18)


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def atoms(path):
    result = []
    with path.open("rb") as file:
        offset = 0
        while offset < path.stat().st_size:
            file.seek(offset)
            header = file.read(8)
            if len(header) < 8:
                break
            length, kind = struct.unpack(">I4s", header)
            if length == 1:
                length = struct.unpack(">Q", file.read(8))[0]
            if length == 0:
                length = path.stat().st_size - offset
            result.append({"kind": kind.decode("ascii", "replace"), "offset": offset, "size": length})
            offset += length
    return result


def review(name, width, height, seconds):
    path = OUTPUT / name
    info = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]).stdout)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (video["width"], video["height"]) == (width, height)
    assert video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p"
    assert video["r_frame_rate"] == "30/1"
    assert abs(float(info["format"]["duration"]) - seconds) < 0.05
    assert audio["codec_name"] == "aac" and audio["channels"] == 2 and audio["sample_rate"] == "48000"
    structure = atoms(path)
    assert next(a["offset"] for a in structure if a["kind"] == "moov") < next(
        a["offset"] for a in structure if a["kind"] == "mdat"
    ), "MP4 must start streaming before the complete download"

    # Decode all frames, including every transition, to rule out missing or corrupt frames.
    raw = run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=160:90", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    ).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160)
    assert len(frames) == seconds * 30
    dark = np.mean(frames < 12, axis=(1, 2)) > 0.98
    assert not dark.any(), "Unexpected black frame"
    change = np.mean(np.abs(np.diff(frames.astype(np.int16), axis=0)), axis=(1, 2))

    # Inspect text, product framing and edit pacing over the complete timeline.
    frame_dir = QA / path.stem
    frame_dir.mkdir(exist_ok=True)
    if width > height:
        w, h, cols, per_sheet = 480, 270, 4, 24
    else:
        w, h, cols, per_sheet = 270, 480, 5, 15
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(path),
            "-vf",
            rf"select=not(mod(n\,15)),scale={w}:{h}",
            "-fps_mode",
            "vfr",
            str(frame_dir / "frame-%03d.png"),
        ]
    )
    images = sorted(frame_dir.glob("frame-*.png"))
    sheets = []
    for page in range(math.ceil(len(images) / per_sheet)):
        chunk = images[page * per_sheet : (page + 1) * per_sheet]
        rows = math.ceil(len(chunk) / cols)
        sheet = Image.new("RGB", (cols * w, rows * (h + 32)), "#dfe8da")
        draw = ImageDraw.Draw(sheet)
        for i, file in enumerate(chunk):
            x = i % cols * w
            y = i // cols * (h + 32)
            time = (page * per_sheet + i) / 2
            draw.text((x + 12, y + 5), f"{time:05.1f}s", font=FONT, fill="#123c3b")
            sheet.paste(Image.open(file).convert("RGB"), (x, y + 32))
        target = QA / f"{path.stem}-timeline-{page + 1}.png"
        sheet.save(target)
        sheets.append(str(target))
    loud = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(path),
            "-vn",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json",
            "-f",
            "null",
            "-",
        ]
    ).stderr.decode("utf-8", "replace")
    match = re.search(r'\{\s*"input_i"[\s\S]+?\}', loud)
    loudness = json.loads(match.group())
    assert -18 < float(loudness["input_i"]) < -14
    assert float(loudness["input_tp"]) < -0.5
    return {
        "file": str(path),
        "duration": info["format"]["duration"],
        "bytes": path.stat().st_size,
        "video": video,
        "audio": audio,
        "decodedFrames": len(frames),
        "blackFrames": int(dark.sum()),
        "averageFrameChange": float(change.mean()),
        "integratedLoudnessLUFS": float(loudness["input_i"]),
        "truePeakDBTP": float(loudness["input_tp"]),
        "loudnessRangeLU": float(loudness["input_lra"]),
        "streamingReady": True,
        "timelineSheets": sheets,
    }


reports = []
for target in [("MyTZStudies-Launch-1080p.mp4", 1920, 1080, 72), ("MyTZStudies-Social-Vertical.mp4", 1080, 1920, 26)]:
    report = review(*target)
    reports.append(report)
    print(
        target[0],
        report["decodedFrames"],
        "frames decoded,",
        report["integratedLoudnessLUFS"],
        "LUFS,",
        report["truePeakDBTP"],
        "dBTP",
    )
(QA / "media-checks.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
print("Review sheets and media checks complete.")
