"""Create contact sheets of details, opening work and last pages for PDF review."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output/primary-answer-key-review.json"
DEST = ROOT / "tmp/primary-answers/contact-review"


def contacts():
    DEST.mkdir(parents=True, exist_ok=True)
    rows = json.loads(REPORT.read_text(encoding="utf-8"))["papers"]
    for name, row in rows.items():
        if row.get("status") not in ("layout_checked", "published"):
            continue
        source = Path(row["preview_directory"])
        indexes = list(dict.fromkeys([1, 2, 3, row["pages"]]))
        sheet = Image.new("RGB", (1000, 1460), "#dce3e8")
        labels = ImageDraw.Draw(sheet)
        for i, number in enumerate(indexes):
            with Image.open(source / f"page-{number:03d}.png") as page:
                page.thumbnail((480, 690))
                x, y = 10 + (i % 2) * 500, 25 + (i // 2) * 730
                sheet.paste(page, (x, y))
                labels.text((x, y - 18), f"Page {number}", fill="#173645")
        sheet.save(DEST / (Path(name).stem + ".jpg"), quality=90)
    print("Contact sheets ready for visual review.")


if __name__ == "__main__":
    contacts()
