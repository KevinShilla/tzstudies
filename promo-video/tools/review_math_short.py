"""Check the finished Short and render its entire timeline for visual review."""

import json
import struct
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / "output" / "shorts"
QA = ROOT / "qa" / "math-short"
VIDEO = OUTPUT / "TZStudies-Math-Short.mp4"


def run(args):
    return subprocess.run(args, capture_output=True, check=True)


info = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(VIDEO)]).stdout)
video = next(s for s in info["streams"] if s["codec_type"] == "video")
audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
assert (video["width"], video["height"]) == (1080, 1920)
assert video["r_frame_rate"] == "30/1"
assert video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p"
assert video["color_space"] == "bt709"
assert abs(float(info["format"]["duration"]) - 52) < .05 and float(info["format"]["duration"]) < 60
assert abs(float(video["duration"]) - 52) < .001
assert audio["codec_name"] == "aac" and audio["sample_rate"] == "48000" and audio["channels"] == 2

atoms = []
with VIDEO.open("rb") as file:
    offset = 0
    while offset < VIDEO.stat().st_size:
        file.seek(offset)
        size, kind = struct.unpack(">I4s", file.read(8))
        if size == 1:
            size = struct.unpack(">Q", file.read(8))[0]
        if size == 0:
            size = VIDEO.stat().st_size - offset
        atoms.append((kind.decode("ascii"), offset))
        offset += size
assert dict(atoms)["moov"] < dict(atoms)["mdat"]

raw = run(["ffmpeg", "-v", "error", "-i", str(VIDEO), "-vf", "scale=90:160", "-f", "rawvideo", "-pix_fmt", "gray", "-"]).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90)
assert len(frames) == 1560
black = np.mean(frames < 12, axis=(1, 2)) > .98
assert not black.any(), "Unexpected black frame"
change = np.mean(np.abs(np.diff(frames.astype(np.int16), axis=0)), axis=(1, 2))

frame_dir = QA / "timeline"
frame_dir.mkdir(exist_ok=True)
run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEO), "-vf", r"select=not(mod(n\,15)),scale=270:480", "-fps_mode", "vfr", str(frame_dir / "frame-%03d.png")])
images = sorted(frame_dir.glob("frame-*.png"))
font = ImageFont.truetype(str(ROOT / "public/fonts/DM-Sans.ttf"), 19)
sheets = []
for page in range((len(images) + 19) // 20):
    group = images[page * 20:(page + 1) * 20]
    sheet = Image.new("RGB", (270 * 5, 510 * 4), "#d7ded5")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(group):
        x, y = (i % 5) * 270, (i // 5) * 510
        sheet.paste(Image.open(path), (x, y))
        draw.text((x + 8, y + 483), f"{(page * 20 + i) / 2:.1f}s", fill="#123c3b", font=font)
    name = QA / f"timeline-{page + 1}.jpg"
    sheet.save(name, quality=94)
    sheets.append(str(name))

loud = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-vn", "-af", "loudnorm=I=-15.5:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"]).stderr.decode("utf-8", "replace")
loudness, _ = json.JSONDecoder().raw_decode(loud[loud.rfind("{"):])
assert -17 < float(loudness["input_i"]) < -14
assert float(loudness["input_tp"]) < -1

report = {
    "file": str(VIDEO), "duration_seconds": float(info["format"]["duration"]), "video_duration_seconds": 52, "width": 1080, "height": 1920,
    "fps": 30, "video_codec": "h264", "color_space": "bt709", "audio_codec": "aac",
    "audio_channels": 2, "sample_rate": 48000, "decoded_frames": len(frames),
    "unexpected_black_frames": int(black.sum()), "streaming_ready": True,
    "integrated_loudness_LUFS": float(loudness["input_i"]),
    "true_peak_dBTP": float(loudness["input_tp"]),
    "loudness_range_LU": float(loudness["input_lra"]),
    "average_frame_change": float(change.mean()), "timeline_review_sheets": sheets,
    "file_bytes": VIDEO.stat().st_size,
    "math": json.loads((QA / "math-checks.json").read_text(encoding="utf-8")),
}
OUTPUT.mkdir(exist_ok=True)
(OUTPUT / "media-checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k not in ["math", "timeline_review_sheets"]}, indent=2))
