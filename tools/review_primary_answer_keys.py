"""Track and audit worked solutions for the 148 imported primary papers.

Run without flags for a progress report. --render creates unpublished drafts;
--publish requires the recorded PDF hash from a successful layout audit and a
separate visual_reviewed approval in each solution source.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import shutil
from fractions import Fraction
from pathlib import Path

import pymupdf
from build_answer_keys import ROOT, build, validate

MANIFEST = ROOT / "exams/catalogue.json"
REPORT = ROOT / "output/primary-answer-key-review.json"


def content_digest(data):
    content = {k: v for k, v in data.items() if k not in ("visual_reviewed", "visual_review_pdf_sha256")}
    content["_image_hashes"] = {q["image"]: hashlib.sha256((ROOT / q["image"]).read_bytes()).hexdigest()
                               for q in data["questions"] if q.get("image")}
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def calculate(expression):
    """Evaluate numbers and arithmetic only, using exact fractions (never eval)."""
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Fraction(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow) and right.denominator == 1 and abs(right) <= 10:
                return left ** int(right)
        raise ValueError("Only bounded numeric arithmetic is allowed")

    return visit(tree.body)


def audit_pdf(path, data, render=False):
    errors = []
    preview = ROOT / "tmp/primary-answers/pdf-review" / path.stem
    if render:
        preview.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(path) as document:
        texts = [page.get_text() for page in document]
        if len(texts) < 3:
            errors.append("Missing cover/details/solutions pages")
        if "MyTZStudies.com" not in texts[0] or "Your Free Tanzania Exam Library" not in texts[0]:
            errors.append("Incorrect website cover")
        if "Final Answer" in texts[0] or data["year"] in texts[0]:
            errors.append("Exam/answer material on advertising cover")
        if data["board"] not in texts[1] or data["year"] not in texts[1] or data["subject"] not in texts[1]:
            errors.append("Missing exam metadata on second page")
        if "Final Answer" in texts[1]:
            errors.append("Answers on exam metadata page")
        if sum(text.count("Final Answer") for text in texts) != len(data["questions"]):
            errors.append("Final-answer count differs from source part count")
        for index, page in enumerate(document):
            spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                     for line in b["lines"] for s in line["spans"] if s["text"].strip()]
            for span in spans:
                rect = pymupdf.Rect(span["bbox"])
                if rect.x0 < 25 or rect.x1 > page.rect.width - 25 or rect.y0 < 15 or rect.y1 > page.rect.height - 15:
                    errors.append(f"Page {index + 1}: text outside safe margins")
                if "\ufffd" in span["text"] or "\x00" in span["text"]:
                    errors.append(f"Page {index + 1}: missing glyph")
            for i, span in enumerate(spans):
                a = pymupdf.Rect(span["bbox"])
                for other in spans[i + 1:]:
                    b = pymupdf.Rect(other["bbox"])
                    overlap = a & b
                    if not overlap.is_empty and overlap.width > 1 and overlap.height > min(a.height, b.height) * .3:
                        errors.append(f"Page {index + 1}: overlapping text")
            if render:
                page.get_pixmap(dpi=100).save(preview / f"page-{index + 1:03d}.png")
        return {"pages": len(document), "pdf_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "layout_errors": sorted(set(errors)), "preview_directory": str(preview)}


def review(render=False, publish=False, filenames=None):
    papers = json.loads(MANIFEST.read_text(encoding="utf-8"))["papers"]
    previous = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    results = dict(previous.get("papers", {}))
    template_sha = hashlib.sha256((ROOT / "tools/build_answer_keys.py").read_bytes()).hexdigest()
    for filename, metadata in papers.items():
        if filenames and filename not in filenames:
            continue
        source = ROOT / "answer_keys/solutions" / (Path(filename).stem + ".json")
        row = {"subject": metadata["subject"], "grade": metadata["grade"], "status": "pending"}
        if not source.exists():
            results[filename] = row
            continue
        source_bytes = source.read_bytes()
        data = json.loads(source_bytes)
        row.update(parts=len(data["questions"]), limitations=data.get("limitations", []))
        try:
            validate(data)
            assert data["exam"] == filename
            assert data["output"] == Path(filename).stem + "-AnswerKey.pdf"
            checks = 0
            for question in data["questions"]:
                for check in question.get("math_checks", []):
                    assert calculate(check["expression"]) == Fraction(str(check["expected"])), f"Arithmetic error at {question['id']}"
                    checks += 1
            row.update(status="content_checked", math_checks=checks)
            draft = ROOT / "output/pdf" / data["output"]
            old = results.get(filename, {})
            reusable = (old.get("source_sha256") == content_digest(data)
                        and old.get("template_sha256") == template_sha
                        and draft.exists()
                        and old.get("pdf_sha256") == hashlib.sha256(draft.read_bytes()).hexdigest())
            if render and not reusable:
                with contextlib.redirect_stdout(io.StringIO()):
                    build(data, publish=False)
                row.update(audit_pdf(draft, data, render=True))
                row["source_sha256"] = content_digest(data)
                row["template_sha256"] = template_sha
                row["status"] = "layout_checked" if not row["layout_errors"] else "layout_errors"
            elif filename in results:
                if old.get("source_sha256") == content_digest(data):
                    row.update({k: old[k] for k in ("pages", "pdf_sha256", "layout_errors", "preview_directory", "source_sha256", "template_sha256", "status") if k in old})
            if publish:
                assert row["status"] in ("layout_checked", "published") and not row["layout_errors"], "Missing successful layout audit"
                assert data.get("visual_reviewed") is True, "Latest rendered PNGs need visual review"
                assert data.get("visual_review_pdf_sha256") == row["pdf_sha256"], "Visual approval refers to a different PDF"
                assert hashlib.sha256(draft.read_bytes()).hexdigest() == row["pdf_sha256"], "Draft PDF changed after review"
                target = ROOT / "answer_keys" / data["output"]
                temporary = target.with_suffix(".publishing")
                shutil.copy2(draft, temporary)
                temporary.replace(target)
                row["status"] = "published"
            row["visual_reviewed"] = bool(data.get("visual_reviewed") and data.get("visual_review_pdf_sha256") == row.get("pdf_sha256"))
        except (AssertionError, ValueError) as error:
            row.update(status="needs_review", error=str(error))
        results[filename] = row
    summary = {"total_papers": len(papers), "solution_sources": sum(r["status"] != "pending" for r in results.values()),
               "published": sum(r["status"] == "published" for r in results.values()),
               "visually_approved": sum(r.get("visual_reviewed", False) for r in results.values()),
               "answered_parts": sum(r.get("parts", 0) for r in results.values()),
               "math_checks": sum(r.get("math_checks", 0) for r in results.values()),
               "remaining": [name for name in papers if results.get(name, {}).get("status") != "published"]}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT.with_suffix(".writing")
    temporary.write_text(json.dumps({"summary": summary, "papers": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(REPORT)
    print(json.dumps({k: v for k, v in summary.items() if k != "remaining"}, indent=2))
    return results


def approve_visual(filenames):
    """Record explicit approval after the caller has inspected rendered PNGs."""
    assert filenames, "List the specific papers whose rendered PNGs you inspected"
    rows = json.loads(REPORT.read_text(encoding="utf-8"))["papers"]
    for filename in filenames:
        row = rows[filename]
        assert row["status"] in ("layout_checked", "published") and not row["layout_errors"]
        source = ROOT / "answer_keys/solutions" / (Path(filename).stem + ".json")
        data = json.loads(source.read_text(encoding="utf-8"))
        assert content_digest(data) == row["source_sha256"], "Source changed since rendering"
        pdf = ROOT / "output/pdf" / data["output"]
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == row["pdf_sha256"], "PDF changed since rendering"
        data.update(visual_reviewed=True, visual_review_pdf_sha256=row["pdf_sha256"])
        temporary = source.with_suffix(".writing")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(source)
    print(f"Recorded visual review for {len(filenames)} PDFs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--approve-visual", action="store_true")
    args = parser.parse_args()
    if args.approve_visual:
        approve_visual(args.filenames)
    else:
        review(render=args.render, publish=args.publish, filenames=args.filenames)
