"""Small server-rendered pages with shareable, validated library filters."""
import math

from flask import abort, request, url_for

from tzstudies.catalogue import GRADE_NAMES, SUBJECT_LABELS, matches_query
from tzstudies.security import valid_text

PAGE_SIZE = 18


def library_context(exams, endpoint="papers.index", answer_keys=False):
    query = request.args.get("q", "").strip()
    grade = request.args.get("grade", "").strip().upper()
    subject = request.args.get("subject", "").strip().lower()
    year = request.args.get("year", "").strip()
    raw_page = request.args.get("page", "1")
    if len(query) > 200 or query and not valid_text(query, 200):
        abort(400)
    if grade and grade not in GRADE_NAMES or subject and subject not in SUBJECT_LABELS:
        abort(400)
    if year and (not year.isascii() or not year.isdigit() or len(year) != 4 or not 2000 <= int(year) <= 2100):
        abort(400)
    if not raw_page.isascii() or not raw_page.isdigit() or len(raw_page) > 6 or int(raw_page) < 1:
        abort(400)
    available = [exam for exam in exams if exam["answer_key"]] if answer_keys else exams
    filtered = [exam for exam in available if (not grade or exam["grade"] == grade)
                and (not subject or exam["subject_group"] == subject) and (not year or exam["year"] == year)
                and (not query or matches_query(exam, query))]
    page_count = max(1, math.ceil(len(filtered) / PAGE_SIZE))
    page = min(int(raw_page), page_count)
    filters = {"q": query, "grade": grade, "subject": subject, "year": year}

    def page_url(number):
        return url_for(endpoint, **{key: value for key, value in filters.items() if value}, page=number) + "#libraryResults"

    level_counts = {code: sum(exam["grade"] == code for exam in available) for code in GRADE_NAMES}
    grade_options = [(code, label) for code, label in GRADE_NAMES.items() if level_counts[code]]
    return {
        "exams": filtered[(page - 1) * PAGE_SIZE:page * PAGE_SIZE], "filters": filters,
        "total": len(exams), "available_count": len(available), "result_total": len(filtered),
        "key_count": sum(bool(exam["answer_key"]) for exam in exams), "level_count": len(grade_options),
        "grade_options": grade_options, "level_counts": level_counts, "subject_options": SUBJECT_LABELS,
        "years": sorted({exam["year"] for exam in available if exam["year"]}, reverse=True),
        "page": page, "page_count": page_count, "page_links": [(number, page_url(number)) for number in range(max(1, page - 2), min(page_count, page + 2) + 1)],
        "previous_url": page_url(page - 1) if page > 1 else None, "next_url": page_url(page + 1) if page < page_count else None,
        "first_result": (page - 1) * PAGE_SIZE + 1 if filtered else 0, "last_result": min(page * PAGE_SIZE, len(filtered)),
        "filter_endpoint": endpoint, "clear_url": url_for(endpoint) + "#examSection",
        "primary_levels": [(code, GRADE_NAMES[code], level_counts[code], url_for(endpoint, grade=code) + "#examSection") for code in GRADE_NAMES if code in {"S1", "S2", "S3", "S4", "S5", "S6"}],
    }
