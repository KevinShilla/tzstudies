"""Render every built answer key and audit basic page and text geometry."""
import json
import math
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def contact_sheet(images, output):
    sheet = Image.new("RGB", (1000, 1460), "#dce3e8")
    label = ImageDraw.Draw(sheet)
    for i, path in enumerate(images):
        page = Image.open(path).convert("RGB")
        page.thumbnail((480, 690))
        x, y = 10 + (i % 2) * 500, 25 + (i // 2) * 730
        sheet.paste(page, (x, y))
        label.text((x, y - 18), path.name, fill="#173645")
    sheet.save(output)


def review():
    directory = ROOT / "tmp" / "pdfs" / "review"
    directory.mkdir(parents=True, exist_ok=True)
    audit = []
    for source in sorted((ROOT / "answer_keys" / "solutions").glob("*.json")):
        data = json.loads(source.read_text(encoding="utf-8"))
        path = ROOT / "output" / "pdf" / data["output"]
        doc = pymupdf.open(path)
        texts = [page.get_text() for page in doc]
        assert "MyTZStudies.com" in texts[0] and "Your Free Tanzania Exam Library" in texts[0], path
        assert "Final Answer" not in texts[0] and data["year"] not in texts[0], path
        assert "NECTA" in texts[1] and data["year"] in texts[1] and data["subject"] in texts[1], path
        assert "Final Answer" not in texts[1], path
        assert sum(text.count("Final Answer") for text in texts) == len(data["questions"]), path
        assert all(len(text.strip()) > 80 for text in texts), path
        errors = []
        page_images = []
        for index, page in enumerate(doc):
            spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block for line in block["lines"] for span in line["spans"] if span["text"].strip()]
            for span in spans:
                rect = pymupdf.Rect(span["bbox"])
                if rect.x0 < 25 or rect.x1 > page.rect.width - 25 or rect.y0 < 15 or rect.y1 > page.rect.height - 15:
                    errors.append({"page": index + 1, "type": "page boundary", "text": span["text"]})
                if "\ufffd" in span["text"] or "\x00" in span["text"]:
                    errors.append({"page": index + 1, "type": "missing glyph", "text": span["text"]})
            for i, span in enumerate(spans):
                a = pymupdf.Rect(span["bbox"])
                for other in spans[i + 1:]:
                    b = pymupdf.Rect(other["bbox"])
                    intersection = a & b
                    if not intersection.is_empty and intersection.width > 1 and intersection.height > min(a.height, b.height) * .3:
                        errors.append({"page": index + 1, "type": "text overlap", "a": span["text"], "b": other["text"]})
            image_path = directory / f"{path.stem}-p{index + 1:02d}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(str(image_path))
            page_images.append(image_path)
        for group in range(math.ceil(len(page_images) / 4)):
            contact_sheet(page_images[group * 4:(group + 1) * 4], directory / f"{path.stem}-sheet{group + 1:02d}.png")
        audit.append({"file": path.name, "pages": len(doc), "answered_parts": len(data["questions"]), "geometry_errors": errors})
    (directory / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps({"pdfs": len(audit), "pages": sum(row["pages"] for row in audit), "geometry_errors": sum(len(row["geometry_errors"]) for row in audit)}, indent=2))
    assert not any(row["geometry_errors"] for row in audit), "Inspect tmp/pdfs/review/audit.json"


if __name__ == "__main__":
    review()
