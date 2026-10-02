"""Shared, filename-aware catalogue for papers and their worked solutions."""
import re
from pathlib import Path

GRADE_NAMES = {"S4": "Standard 4", "S7": "Standard 7", "F2": "Form 2", "F4": "Form 4", "F6": "Form 6"}
SUBJECT_NAMES = {"basicmath": "Basic Mathematics", "mathematics": "Mathematics", "hisabati": "Hisabati", "english": "English", "kiswahili": "Kiswahili"}


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
    return {"filename": filename, "subject": subject, "grade": grade, "level": GRADE_NAMES.get(grade, "Exam paper"), "year": year, "board": "NECTA", "sample": identity(filename) == "english-s7-2024"}


def build_catalogue(exams_folder, keys_folder):
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
        exam.update(aliases=sorted(aliases), answer_key=keys.get(key))
        exam["search_text"] = " ".join([exam["subject"], exam["grade"], exam["level"], exam["year"], exam["board"], filename]).lower()
        exams.append(exam)
    return sorted(exams, key=lambda e: (-int(e["year"] or 0), e["subject"], e["grade"]))
