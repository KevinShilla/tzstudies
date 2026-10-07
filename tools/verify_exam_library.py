"""Validate the checked-in import manifest and its original/section PDFs offline."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    from tzstudies.catalogue import build_catalogue
    from tzstudies.file_security import _validate_pdf

    manifest = json.loads((ROOT / "exams" / "catalogue.json").read_text(encoding="utf-8"))
    for filename, paper in manifest["papers"].items():
        if Path(filename).name != filename or len(filename) > 200 or not filename.endswith(".pdf"):
            raise ValueError("Unsafe filename")
        source = urlsplit(paper["source_url"])
        if source.scheme != "https" or source.username or source.password:
            raise ValueError("Invalid source URL")
        data = (ROOT / "exams" / filename).read_bytes()
        if len(data) != paper["bytes"] or hashlib.sha256(data).hexdigest() != paper["sha256"]:
            raise ValueError(f"Paper checksum does not match: {filename}")
        _validate_pdf(data)
    catalogue = build_catalogue(ROOT / "exams", ROOT / "answer_keys")
    counts = Counter((paper["grade"], paper["subject_group"]) for paper in catalogue if paper["year"] and int(paper["year"]) >= 2022)
    for number in range(1, 7):
        for subject in ("math", "english", "kiswahili"):
            if counts[(f"S{number}", subject)] < 7:
                raise ValueError(f"Insufficient coverage: Standard {number} {subject}")
    print(f"Validated {len(manifest['papers'])} imported PDFs. All 18 standard/subject groups have at least seven papers from 2022 onward.")


if __name__ == "__main__":
    main()
