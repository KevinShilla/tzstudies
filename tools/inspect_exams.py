"""Prepare local PDF text and page images for the answer-key review."""
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "tmp" / "pdfs"
DEST.mkdir(parents=True, exist_ok=True)
groups = {}
for path in sorted((ROOT / "exams").glob("*.pdf")):
    groups.setdefault(hashlib.sha256(path.read_bytes()).hexdigest(), []).append(path)
jobs = []
inventory = []
for digest, files in groups.items():
    source = min(files, key=lambda p: (" (1)" in p.name, "-English" in p.name, len(p.name)))
    doc = fitz.open(source)
    pages = []
    for index, page in enumerate(doc):
        text = page.get_text(sort=True)
        useful = text.replace("Downloaded from", "").replace("www.maktaba.tetea.org", "")
        # A scanned page can have an extractable watermark but no exam text.
        scanned = len(useful.strip()) < 220
        image = DEST / "scans" / source.stem / f"{index + 1:02d}.png"
        if scanned:
            image.parent.mkdir(parents=True, exist_ok=True)
            if not image.exists():
                page.get_pixmap(dpi=180).save(image)
            jobs.append({"image": str(image), "output": str(image.with_suffix(".txt"))})
        pages.append({"page": index + 1, "text": text, "scanned": scanned, "image": str(image)})
    entry = {"file": source.name, "aliases": [p.name for p in files], "sha256": digest, "pages": pages}
    inventory.append(entry)
    (DEST / f"{source.stem}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    (DEST / f"{source.stem}.txt").write_text("\n\n".join(f"PAGE {p['page']}\n{p['text']}" for p in pages), encoding="utf-8")
(DEST / "review-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
(DEST / "ocr-jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
print(f"{len(inventory)} distinct PDFs; {len(jobs)} pages need OCR.")
