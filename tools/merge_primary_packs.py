"""Include separately solved subject excerpts in retained complete source packs.

An import sometimes retains a full multi-subject PDF. Its answer key must also
cover those extra sections; match excerpts by original PDF hash, then translate
their page references back to the complete PDF. The operation is idempotent.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "answer_keys/solutions"


def merge():
    papers = json.loads((ROOT / "exams/catalogue.json").read_text(encoding="utf-8"))["papers"]
    changed = []
    for filename, metadata in papers.items():
        if metadata.get("source_pages"):
            continue
        excerpts = [(name, info) for name, info in papers.items() if name != filename
                    and info.get("source_pages") and info.get("original_sha256") == metadata["sha256"]]
        target = SOURCES / (Path(filename).stem + ".json")
        if not excerpts or not target.exists():
            continue
        data = json.loads(target.read_text(encoding="utf-8"))
        if any(not (SOURCES / (Path(name).stem + ".json")).exists() for name, _ in excerpts):
            continue
        # Refresh copied excerpts when their content or figures have been reviewed.
        prefixes = tuple(info["subject"] + "-" for _, info in excerpts)
        section_prefixes = tuple(info["subject"] + " - " for _, info in excerpts)
        data["questions"] = [q for q in data["questions"] if not q["id"].startswith(prefixes)]
        data["summaries"] = {section: summary for section, summary in data.get("summaries", {}).items()
                             if not section.startswith(section_prefixes)}
        added = []
        for name, info in excerpts:
            extra = json.loads((SOURCES / (Path(name).stem + ".json")).read_text(encoding="utf-8"))
            if not extra.get("reviewed"):
                break
            prefix = info["subject"] + "-"
            for question in extra["questions"]:
                question = copy.deepcopy(question)
                question["id"] = prefix + question["id"]
                question["section"] = info["subject"] + " - " + question["section"]
                question["language"] = extra["language"]
                question["source_page"] = info["source_pages"][question["source_page"] - 1]
                data["questions"].append(question)
            for section, summary in extra.get("summaries", {}).items():
                data.setdefault("summaries", {})[info["subject"] + " - " + section] = summary
            for limitation in extra.get("limitations", []):
                if isinstance(limitation, dict):
                    limitation = copy.deepcopy(limitation)
                    if "id" in limitation:
                        limitation["id"] = prefix + limitation["id"]
                if limitation not in data.setdefault("limitations", []):
                    data["limitations"].append(limitation)
            added.append(name)
        else:
            data["related_sections"] = added
            data["expected_parts"] = [q["id"] for q in data["questions"]]
            data["question_count"] = f"{len(data['questions'])} tasks/parts, including all retained subject sections"
            data["labelling_note"] = "This source PDF retains more than one subject. The additional printed sections are answered after the main subject, with their original page references."
            data.pop("visual_reviewed", None)
            temporary = target.with_suffix(".writing")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(target)
            changed.append({"exam": filename, "included": added, "parts": len(data["questions"])})
    print(json.dumps(changed, indent=2))


if __name__ == "__main__":
    merge()
