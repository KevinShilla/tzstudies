"""Shared, filename-aware catalogue for papers and their worked solutions."""
import copy
import json
import re
import threading
import time
from pathlib import Path

GRADE_NAMES = {**{f"S{number}": f"Standard {number}" for number in range(1, 8)}, "F2": "Form 2", "F4": "Form 4", "F6": "Form 6"}
SUBJECT_NAMES = {"basicmath": "Basic Mathematics", "mathematics": "Mathematics", "hisabati": "Hisabati", "english": "English", "kiswahili": "Kiswahili"}
SUBJECT_GROUPS = {"Mathematics": "math", "Basic Mathematics": "math", "Hisabati": "math", "English": "english", "Kiswahili": "kiswahili"}
SUBJECT_LABELS = {"math": "Math", "english": "English", "kiswahili": "Kiswahili"}
_CACHE = {}
_CACHE_LOCK = threading.Lock()


def matches_query(exam, query):
    text = exam["search_text"]
    words = re.findall(r"\w+", text)
    return all(term in words if term.isdigit() else term in text for term in query.lower().split())


def identity(filename):
    stem = Path(filename).stem
    stem = re.sub(r"\s*\(\d+\)$", "", stem)
    stem = re.sub(r"\s*\(?answer[\s_-]*key\)?$", "", stem, flags=re.I)
    stem = re.sub(r"-English$", "", stem, flags=re.I)
    return re.sub(r"[\s_-]+", "-", stem.strip(" -_")).lower()


def metadata(filename):
    parts = identity(filename).split("-")
    subject = SUBJECT_NAMES.get(parts[0], parts[0].replace("_", " ").title())
    grade = next((p.upper() for p in parts if p.upper() in GRADE_NAMES), "")
    year = next((p for p in parts if re.fullmatch(r"\d{4}", p)), "")
    sample = identity(filename) == "english-s7-2024"
    return {"filename": filename, "subject": subject, "subject_group": SUBJECT_GROUPS.get(subject, subject.lower()), "grade": grade,
            "level": GRADE_NAMES.get(grade, "Exam paper"), "year": year, "board": "NECTA", "sample": sample,
            "assessment": "Sample paper" if sample else "National assessment" if grade in ("S4", "F2") else "National exam",
            "title": "", "source_url": "", "source_name": "", "language": "", "pages": None, "bytes": None, "section_note": ""}


def build_catalogue(exams_folder, keys_folder):
    """Cache only public file metadata, never rendered HTML or account/session state."""
    folders = (str(Path(exams_folder).resolve()), str(Path(keys_folder).resolve()))
    manifest = Path(exams_folder) / "catalogue.json"
    stamp = tuple(Path(folder).stat().st_mtime_ns if Path(folder).exists() else 0 for folder in folders)
    stamp += (manifest.stat().st_mtime_ns if manifest.exists() else 0,)
    now = time.monotonic()
    with _CACHE_LOCK:
        cached = _CACHE.get(folders)
        if cached and cached[0] == stamp and now - cached[1] < 60:
            return copy.deepcopy(cached[2])
        exams = _build_catalogue(exams_folder, keys_folder, manifest)
        if len(_CACHE) >= 16:
            _CACHE.clear()
        _CACHE[folders] = (stamp, now, exams)
        return copy.deepcopy(exams)


def _build_catalogue(exams_folder, keys_folder, manifest):
    entries = {}
    if manifest.exists():
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("papers", {})
    keys = {}
    for path in sorted(Path(keys_folder).glob("*.pdf"), key=lambda p: ("-AnswerKey" not in p.name, p.name.lower())):
        keys.setdefault(identity(path.name), path.name)
    groups = {}
    for path in Path(exams_folder).glob("*.*"):
        if path.suffix.lower() == ".pdf":
            groups.setdefault(identity(path.name), []).append(path.name)
    exams = []
    for key, aliases in groups.items():
        filename = min(aliases, key=lambda name: (bool(re.search(r"\(\d+\)", name)), "-English" in name, len(name), name.lower()))
        exam = metadata(filename)
        source = entries.get(filename, {})
        # The checked-in manifest supplies verified metadata for school and regional papers.
        for field in ("subject", "grade", "year", "board", "assessment", "title", "source_url", "source_name", "language", "pages", "bytes", "section_note"):
            if field in source:
                exam[field] = source[field]
        exam["level"] = GRADE_NAMES.get(exam["grade"], "Exam paper")
        exam["subject_group"] = SUBJECT_GROUPS.get(exam["subject"], exam["subject"].lower())
        exam.update(aliases=sorted(aliases), answer_key=keys.get(key))
        if exam["bytes"] is None:
            exam["bytes"] = (Path(exams_folder) / filename).stat().st_size
        exam["search_text"] = " ".join([exam["subject"], exam["subject_group"], "hisabati" if exam["subject_group"] == "math" else "", exam["grade"],
                                         exam["level"], exam["year"], exam["board"], exam["assessment"], exam["title"], filename]).lower()
        exams.append(exam)
    return sorted(exams, key=lambda e: (-int(e["year"] or 0), e["subject"], e["grade"]))
