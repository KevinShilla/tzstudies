"""Prepare actual source-question crops for picture-dependent Math solutions.

Only unique, left-margin integer question labels are used. Ambiguous locations
are skipped. Crops need visual review before --apply adds them to solution JSON.
"""
import argparse
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "answer_keys/figures/primary-math"
REVIEW = ROOT / "tmp/primary-answers/math-figure-crops.json"
CUES = re.compile(r"\b(?:shown|pictured|picture|diagram|clock|shaded|shade|triangles|circles|abacus|symbols|arrows|graph)\b", re.I)


def prepare():
    manifest = json.loads((ROOT / "exams/catalogue.json").read_text(encoding="utf-8"))["papers"]
    DEST.mkdir(parents=True, exist_ok=True)
    candidates = []
    for filename, meta in manifest.items():
        if meta["subject"] != "Mathematics":
            continue
        source = ROOT / "answer_keys/solutions" / (Path(filename).stem + ".json")
        if not source.exists():
            continue
        data = json.loads(source.read_text(encoding="utf-8"))
        with pymupdf.open(ROOT / "exams" / filename) as document:
            for question in data["questions"]:
                if question.get("image") or not question["id"].isdigit() or not CUES.search(question["prompt"]):
                    continue
                page = document[question["source_page"] - 1]
                words = page.get_text("words")
                labels = [w for w in words if (re.fullmatch(r"\d+[.)]", w[4]) and w[0] < page.rect.width / 3)
                          or (w[4].isdigit() and w[0] < page.rect.width * .09)]
                matches = [w for w in labels if w[4].rstrip(".)") == question["id"]]
                if len(matches) != 1:
                    continue
                match = matches[0]
                following = [w[1] for w in labels if w[1] > match[1] + 8 and abs(w[0] - match[0]) < 25]
                bottom = min(following, default=page.rect.height - 25)
                if not 25 <= bottom - match[1] <= 300:
                    continue
                clip = pymupdf.Rect(0, max(0, match[1] - 3), page.rect.width - 15, bottom - 2)
                image = DEST / (Path(filename).stem + "-Q" + question["id"] + ".png")
                page.get_pixmap(dpi=140, clip=clip).save(image)
                candidates.append({"exam": filename, "id": question["id"], "source_page": question["source_page"],
                                   "image": image.relative_to(ROOT).as_posix(), "clip": list(clip), "visual_reviewed": False})
    REVIEW.write_text(json.dumps(candidates, indent=2), encoding="utf-8")
    print(f"Prepared {len(candidates)} source-question crops for visual review.")


def apply():
    rows = json.loads(REVIEW.read_text(encoding="utf-8"))
    count = 0
    for filename in {row["exam"] for row in rows if row["visual_reviewed"]}:
        source = ROOT / "answer_keys/solutions" / (Path(filename).stem + ".json")
        data = json.loads(source.read_text(encoding="utf-8"))
        selected = {row["id"]: row["image"] for row in rows if row["exam"] == filename and row["visual_reviewed"]}
        for question in data["questions"]:
            if question["id"] in selected:
                question["image"] = selected[question["id"]]
                count += 1
        data.pop("visual_reviewed", None)
        data.pop("visual_review_pdf_sha256", None)
        temporary = source.with_suffix(".writing")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(source)
    print(f"Added {count} visually checked source figures.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply() if args.apply else prepare()
