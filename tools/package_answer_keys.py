"""Package the website's canonical answer keys and a complete index."""
import csv
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def package():
    from tzstudies.catalogue import build_catalogue

    catalogue = build_catalogue(ROOT / "exams", ROOT / "answer_keys")
    assert all(paper["answer_key"] for paper in catalogue), "All papers need published keys before packaging"
    report = json.loads((ROOT / "output/primary-answer-key-review.json").read_text(encoding="utf-8"))
    assert report["summary"]["published"] == report["summary"]["total_papers"]
    output = ROOT / "output"
    index = output / "answer-key-index.csv"
    rows = []
    for paper in catalogue:
        key = ROOT / "answer_keys" / paper["answer_key"]
        solution = ROOT / "answer_keys/solutions" / (Path(paper["filename"]).stem + ".json")
        data = json.loads(solution.read_text(encoding="utf-8")) if solution.exists() else {}
        rows.append({"exam": paper["filename"], "answer_key": key.name, "subject": paper["subject"],
                     "level": paper["level"], "year": paper["year"], "issuer": paper["board"],
                     "answered_parts": len(data.get("questions", [])), "bytes": key.stat().st_size})
    with index.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    readme = output / "README.txt"
    readme.write_text(
        f"MyTZStudies.com - Free Tanzania Exam Library\n\n{len(rows)} canonical worked answer keys.\n"
        f"{report['summary']['total_papers']} new Standard 1-6 Math, English and Kiswahili keys plus the existing {len(rows) - report['summary']['total_papers']} keys.\n"
        f"New keys cover {report['summary']['answered_parts']:,} printed tasks/parts, including oral-task assessment guidance.\n"
        "Missing dictation/audio, printing mistakes and ambiguous source items are explained in the affected solutions.\n"
        "The original questions and exact source pages were checked; model responses are labeled as examples.\n\n"
        "The website cover, exam metadata page, numbered steps, final answers and study notes follow the existing design.\n"
        "See answer-key-index.csv for paper-to-key matching. Visit https://mytzstudies.com for the library.\n",
        encoding="utf-8",
    )
    archive = output / "MyTZStudies-Answer-Keys.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED, compresslevel=6) as bundle:
        for row in rows:
            bundle.write(ROOT / "answer_keys" / row["answer_key"], "answer_keys/" + row["answer_key"])
        bundle.write(index, index.name)
        bundle.write(readme, readme.name)
    with ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert sum(name.endswith(".pdf") for name in bundle.namelist()) == len(rows)
    print(f"Packaged {len(rows)} answer keys; ZIP {archive.stat().st_size / 1024**2:.1f} MB.")


if __name__ == "__main__":
    package()
