"""Extract the imported primary exams for offline solution writing and review.

Public exam text and rendered pages stay in tmp/. No credentials or student
information are used. OCR is only an aid; diagrams and scans need page review.
"""
import hashlib
import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "tmp" / "primary-answers"


def prepare():
    manifest = json.loads((ROOT / "exams/catalogue.json").read_text(encoding="utf-8"))
    jobs, inventory = [], []
    for filename, metadata in manifest["papers"].items():
        source = ROOT / "exams" / filename
        assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"]
        folder = DEST / source.stem
        folder.mkdir(parents=True, exist_ok=True)
        with pymupdf.open(source) as document:
            pages = []
            for index, page in enumerate(document):
                text = page.get_text(sort=True)
                useful = text.replace("Downloaded", "").replace("Darasa Huru", "")
                scanned = len(useful.strip()) < 220
                image = folder / f"page-{index + 1:02d}.png"
                # Retain a sharp reference for picture questions and arithmetic.
                if not image.exists():
                    page.get_pixmap(dpi=150).save(image)
                pages.append({"page": index + 1, "text": text, "scanned": scanned,
                              "image": str(image)})
                if scanned:
                    jobs.append({"image": str(image), "output": str(image.with_suffix(".txt"))})
        record = {"exam": filename, "metadata": metadata, "pages": pages}
        (folder / "source.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        (folder / "source.txt").write_text("\n\n".join(f"PAGE {p['page']}\n{p['text']}" for p in pages), encoding="utf-8")
        inventory.append({"exam": filename, "pages": len(pages), "scanned_pages": sum(p["scanned"] for p in pages),
                          "characters": sum(len(p["text"]) for p in pages)})
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    (DEST / "ocr-jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    print(f"Prepared {len(inventory)} papers, {sum(p['pages'] for p in inventory)} pages; {len(jobs)} pages need OCR.")


if __name__ == "__main__":
    prepare()
