"""Build checked answer-key source data into the site's branded PDFs.

Run with the PDF dependencies in requirements-pdf.txt. The source JSON remains
editable, and each PDF records the precise original exam it accompanies.
"""
import argparse
import hashlib
import json
import math
import shutil
import time
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = A4
BLUE = colors.HexColor("#1a5276")
GREEN = colors.HexColor("#267144")
LIGHT_BLUE = colors.HexColor("#edf4f8")
LIGHT_GREEN = colors.HexColor("#eef6ea")
GREY = colors.HexColor("#58656e")
CONTENT_WIDTH = WIDTH - 96


def font_setup():
    # DejaVu embeds the mathematical symbols used in secondary-school solutions.
    try:
        from matplotlib import get_data_path
        math_fonts = Path(get_data_path()) / "fonts" / "ttf"
        for name, filename in [("Study", "DejaVuSans.ttf"), ("Study-Bold", "DejaVuSans-Bold.ttf"), ("Study-Italic", "DejaVuSans-Oblique.ttf")]:
            pdfmetrics.registerFont(TTFont(name, math_fonts / filename))
        pdfmetrics.registerFontFamily("Study", normal="Study", bold="Study-Bold", italic="Study-Italic", boldItalic="Study-Bold")
        return "Study", "Study-Bold"
    except ImportError:
        pass
    font_root = Path("C:/Windows/Fonts")
    if (font_root / "arial.ttf").exists():
        for name, filename in [("Study", "arial.ttf"), ("Study-Bold", "arialbd.ttf"), ("Study-Italic", "ariali.ttf")]:
            pdfmetrics.registerFont(TTFont(name, font_root / filename))
        pdfmetrics.registerFontFamily("Study", normal="Study", bold="Study-Bold", italic="Study-Italic", boldItalic="Study-Bold")
        return "Study", "Study-Bold"
    return "Helvetica", "Helvetica-Bold"


NORMAL, BOLD = font_setup()
STYLES = {
    "body": ParagraphStyle("body", fontName=NORMAL, fontSize=10.3, leading=15.2, textColor=colors.HexColor("#263238"), spaceAfter=6),
    "prompt": ParagraphStyle("prompt", fontName=BOLD, fontSize=11, leading=16, textColor=BLUE, spaceBefore=12, spaceAfter=9, keepWithNext=True),
    "section": ParagraphStyle("section", fontName=BOLD, fontSize=15, leading=21, textColor=colors.white, backColor=BLUE, borderPadding=10, spaceBefore=16, spaceAfter=14, keepWithNext=True),
    "answer": ParagraphStyle("answer", fontName=BOLD, fontSize=10.8, leading=16, textColor=GREEN, backColor=LIGHT_GREEN, borderColor=colors.HexColor("#b5d2a8"), borderWidth=.6, borderPadding=9, spaceBefore=5, spaceAfter=13),
    "tip": ParagraphStyle("tip", fontName=NORMAL, fontSize=9.3, leading=14, textColor=BLUE, backColor=LIGHT_BLUE, borderPadding=9, spaceBefore=3, spaceAfter=11),
    "summary": ParagraphStyle("summary", fontName=NORMAL, fontSize=10, leading=15, textColor=GREY, spaceBefore=12, spaceAfter=14),
    "title": ParagraphStyle("title", fontName=BOLD, fontSize=26, leading=34, textColor=BLUE, alignment=TA_CENTER, spaceAfter=15),
    "subtitle": ParagraphStyle("subtitle", fontName=NORMAL, fontSize=15, leading=22, textColor=GREY, alignment=TA_CENTER, spaceAfter=22),
    "label": ParagraphStyle("label", fontName=BOLD, fontSize=10.5, leading=16, textColor=BLUE),
    "value": ParagraphStyle("value", fontName=NORMAL, fontSize=10.5, leading=16),
}


class TextBox(Flowable):
    """A padded box whose padding participates in pagination and layout."""
    def __init__(self, text, style, paragraph=None):
        super().__init__()
        self.kind = style
        self.text = text
        base = STYLES[style]
        self.spaceBefore = base.spaceBefore
        self.spaceAfter = base.spaceAfter
        self.keepWithNext = getattr(base, "keepWithNext", False)
        clean = ParagraphStyle(style + "-inner", parent=base, backColor=None, borderWidth=0, borderPadding=0, spaceBefore=0, spaceAfter=0)
        self.paragraph = paragraph or Paragraph(escape(str(text)).replace("\n", "<br/>"), clean)

    def wrap(self, avail_width, avail_height):
        self.width = avail_width
        _, height = self.paragraph.wrap(avail_width - 18, avail_height - 18)
        self.height = height + 18
        return self.width, self.height

    def split(self, avail_width, avail_height):
        if self.kind in {"tip", "section"}:
            return []
        parts = self.paragraph.split(avail_width - 18, max(0, avail_height - 18))
        if len(parts) < 2:
            return []
        return [TextBox(self.text, self.kind, paragraph=part) for part in parts]

    def draw(self):
        background = BLUE if self.kind == "section" else LIGHT_GREEN if self.kind == "answer" else LIGHT_BLUE
        self.canv.setFillColor(background)
        self.canv.setStrokeColor(colors.HexColor("#b5d2a8") if self.kind == "answer" else background)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        self.paragraph.drawOn(self.canv, 9, 9)


def para(text, style="body"):
    if style in {"answer", "tip", "section"}:
        return TextBox(text, style)
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), STYLES[style])


def triangle(equilateral=False):
    drawing = Drawing(260, 190 if equilateral else 160)
    drawing.add(Polygon([40, 15, 220, 15, 130, 170.884572681 if equilateral else 125], fillColor=None, strokeColor=BLUE, strokeWidth=1.5))
    if equilateral:
        for x, y in [(83, 88), (165, 88), (112, 0)]:
            drawing.add(String(x, y, "3 cm", fontName=NORMAL, fontSize=10, fillColor=BLUE))
    return drawing


def make_drawing(spec):
    if isinstance(spec, str):
        return triangle(spec == "equilateral")
    if spec["type"] == "clock":
        drawing = Drawing(240, 230)
        cx, cy, radius = 120, 125, 85
        drawing.add(Circle(cx, cy, radius, fillColor=colors.white, strokeColor=BLUE, strokeWidth=1.5))
        for number in range(1, 13):
            angle = math.radians(90 - number * 30)
            drawing.add(String(cx + 69 * math.cos(angle), cy + 69 * math.sin(angle) - 4, str(number), textAnchor="middle", fontName=NORMAL, fontSize=12, fillColor=BLUE))
        for angle, length, width in [(90 - spec["minute"] * 6, 61, 2), (90 - ((spec["hour"] % 12) + spec["minute"] / 60) * 30, 43, 4)]:
            angle = math.radians(angle)
            drawing.add(Line(cx, cy, cx + length * math.cos(angle), cy + length * math.sin(angle), strokeColor=BLUE, strokeWidth=width))
        drawing.add(Circle(cx, cy, 3, fillColor=BLUE, strokeColor=BLUE))
        drawing.add(String(cx, 15, spec.get("caption", ""), textAnchor="middle", fontName=NORMAL, fontSize=9, fillColor=BLUE))
        return drawing
    raise ValueError(f"Unknown drawing: {spec}")


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.setFont(BOLD, 34)
    canvas.drawCentredString(WIDTH / 2, 650, "MyTZStudies.com")
    canvas.setFillColor(GREY)
    canvas.setFont(NORMAL, 15)
    canvas.drawCentredString(WIDTH / 2, 612, "Your Free Tanzania Exam Library")
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1.2)
    canvas.line(85, 587, WIDTH - 85, 587)
    text = para("Past papers, answer keys, and study resources\nfor Tanzanian students.", "subtitle")
    text.wrap(CONTENT_WIDTH, 60)
    text.drawOn(canvas, 48, 520)
    canvas.setFillColor(GREEN)
    canvas.setFont(BOLD, 19)
    canvas.drawCentredString(WIDTH / 2, 490, "MyTZStudies.com")
    canvas.linkURL("https://mytzstudies.com", (160, 483, WIDTH - 160, 509), relative=0)
    labels = [["Past Exam Papers", "Worked Answer Keys", "Free Access"], ["Choose Your Level", "Study Step by Step", "Learn at Your Pace"]]
    table = Table([[Paragraph(escape(x), ParagraphStyle("feature", fontName=BOLD, fontSize=10, leading=16, textColor=BLUE, alignment=TA_CENTER)) for x in row] for row in labels], colWidths=[CONTENT_WIDTH / 3] * 3, rowHeights=[43, 43])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#d4dde4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    table.wrap(CONTENT_WIDTH, 100)
    table.drawOn(canvas, 48, 364)
    canvas.setFont(NORMAL, 11)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(WIDTH / 2, 321, getattr(doc, "study_levels", "Standard 4  |  Standard 7  |  Form 2  |  Form 4"))
    canvas.setFont(NORMAL, 10)
    canvas.drawCentredString(WIDTH / 2, 264, "Share this with a friend.")
    canvas.drawCentredString(WIDTH / 2, 246, "Every student deserves free study materials.")
    canvas.setFont(NORMAL, 8)
    canvas.drawCentredString(WIDTH / 2, 46, "Made with MyTZStudies.com")
    canvas.restoreState()


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9e1e6"))
    canvas.line(48, 49, WIDTH - 48, 49)
    canvas.setFillColor(GREY)
    canvas.setFont(NORMAL, 8)
    canvas.drawString(48, 34, "MyTZStudies.com | Free Tanzania Exam Library")
    canvas.drawRightString(WIDTH - 48, 34, f"Page {doc.page}")
    if doc.page > 2:
        canvas.setFillColor(BLUE)
        canvas.setFont(BOLD, 8)
        canvas.drawString(48, HEIGHT - 35, doc.study_title)
    canvas.restoreState()


def validate(data):
    source = ROOT / "exams" / data["exam"]
    if not source.is_file():
        raise ValueError(f"Missing exam: {data['exam']}")
    if data.get("sha256") and hashlib.sha256(source.read_bytes()).hexdigest() != data["sha256"]:
        raise ValueError(f"Source exam changed: {data['exam']}")
    ids = [q["id"] for q in data["questions"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate question labels: {data['exam']}")
    if set(ids) != set(data["expected_parts"]):
        raise ValueError(f"Missing/extra question parts: {data['exam']}")
    if len(data["expected_parts"]) != len(set(data["expected_parts"])):
        raise ValueError(f"Duplicate expected question labels: {data['exam']}")
    if not isinstance(data.get("summaries", {}), dict):
        raise ValueError(f"Section summaries must be a dictionary: {data['exam']}")
    for question in data["questions"]:
        if not isinstance(question.get("prompt"), str) or not isinstance(question.get("answer"), str) or not isinstance(question.get("section"), str):
            raise ValueError(f"Question text must be strings: {data['exam']} {question['id']}")
        if not question["prompt"] or not question["steps"] or not question["answer"]:
            raise ValueError(f"Incomplete solution: {data['exam']} {question['id']}")
        if not isinstance(question["steps"], list) or any(not isinstance(step, str) or not step.strip() for step in question["steps"]):
            raise ValueError(f"Invalid worked steps: {data['exam']} {question['id']}")
        if question.get("image"):
            image = (ROOT / question["image"]).resolve()
            if not image.is_relative_to(ROOT) or not image.is_file():
                raise ValueError(f"Missing/unsafe source figure: {data['exam']} {question['id']}")
    if not data.get("reviewed"):
        raise ValueError(f"Solution has not been reviewed: {data['exam']}")
    manifest = ROOT / "exams" / "catalogue.json"
    imported = json.loads(manifest.read_text(encoding="utf-8")).get("papers", {}) if manifest.exists() else {}
    if source.name in imported:
        verified = imported[source.name]
        if data.get("board") != verified["board"] or str(data["year"]) != str(verified["year"]) or data.get("sha256") != verified["sha256"]:
            raise ValueError(f"Incorrect source metadata: {data['exam']}")
        for question in data["questions"]:
            if type(question.get("source_page")) is not int or not 1 <= question["source_page"] <= verified["pages"]:
                raise ValueError(f"Missing source-page reference: {data['exam']} {question['id']}")
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)
    used = {ord(char) for value in strings(data) for char in value if not char.isspace()}
    for name in (NORMAL, BOLD):
        glyphs = getattr(pdfmetrics.getFont(name).face, "charToGlyph", None)
        if glyphs is not None and (missing := used - glyphs.keys()):
            codes = ", ".join(f"U+{code:04X}" for code in sorted(missing))
            raise ValueError(f"Unsupported glyphs in {data['exam']} ({name}): {codes}")


def build(data, publish=True):
    validate(data)
    out = ROOT / "output" / "pdf" / data["output"]
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(out), pagesize=A4, leftMargin=48, rightMargin=48, topMargin=64, bottomMargin=68, title=f"{data['subject']} {data['level']} {data['year']} - Answer Key", author="MyTZStudies.com", allowSplitting=True)
    doc.study_title = f"{data['subject']} | {data['level']} | {data['year']} | Answer Key"
    if data.get("board"):
        doc.study_levels = "Standards 1-7  |  Form 2  |  Form 4"
    frame = Frame(48, 68, CONTENT_WIDTH, HEIGHT - 132, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="Cover", frames=[frame], onPage=cover), PageTemplate(id="Body", frames=[frame], onPage=footer)])
    story = [NextPageTemplate("Body"), PageBreak(), Spacer(1, 30), para(f"{data['subject'].upper()}\n{data['level'].upper()}", "title"), para(f"{data['exam_type']} {data['year']}\nAnswer Key and Worked Solutions", "subtitle")]
    rows = [("Subject", data["subject"]), ("Code", data["code"]), ("Level", data["level"]), ("Year", data["year"]), ("Exam Board / Issuer", data.get("board", "NECTA")), ("Exam", data["exam_type"]), ("Type", "Answer key and worked solutions"), ("Questions", data["question_count"])]
    table = Table([[para(k, "label"), para(v, "value")] for k, v in rows], colWidths=[145, CONTENT_WIDTH - 145], hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#d4dde4")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
    story.extend([table, Spacer(1, 23), para("Try each question before checking the solution. Follow the steps, compare your working, and practise the parts you find difficult.", "tip"), para("Source paper: " + data["exam"], "summary")])
    if data.get("labelling_note"):
        story.append(para(data["labelling_note"], "summary"))
    story.append(PageBreak())
    if data.get("limitations"):
        swahili_note = data.get("language") == "sw"
        story.extend([para("Maelezo kuhusu karatasi asilia" if swahili_note else "Notes about the source paper", "section"),
                      para("Maswali yenye taarifa zinazokosekana au makosa ya uchapaji yameelezwa wazi kwenye majibu yake. Jibu la mfano si jibu rasmi la lazima." if swahili_note else "Items with missing information or printing errors are explained in their solutions. A model response is an example, rather than a prescribed official answer.", "body")])
    sections = defaultdict(list)
    for question in data["questions"]:
        sections[question["section"]].append(question)
    swahili = data.get("language") == "sw"
    for section, questions in sections.items():
        for question_index, question in enumerate(questions):
            question_swahili = question.get("language", data.get("language")) == "sw"
            label = "Jibu la mwisho / Final Answer" if question_swahili else "Final Answer"
            answer_box = para(label + ": " + question["answer"], "answer")
            # Long model essays must start below their steps and fill the page.
            # Binding the last step to a whole essay creates nearly empty pages.
            _, answer_height = answer_box.wrap(CONTENT_WIDTH, HEIGHT - 132)
            part_story = [para(section, "section")] if question_index == 0 else []
            part_story.append(para(question["id"] + ". " + question["prompt"], "prompt"))
            if question.get("drawing"):
                part_story.extend([make_drawing(question["drawing"]), Spacer(1, 12)])
            if question.get("image"):
                image_path = ROOT / question["image"]
                img = Image(str(image_path))
                ratio = min(CONTENT_WIDTH / img.imageWidth, 210 / img.imageHeight)
                img.drawWidth = img.imageWidth * ratio
                img.drawHeight = img.imageHeight * ratio
                part_story.extend([img, Spacer(1, 9)])
            for index, step in enumerate(question["steps"], 1):
                label = "Hatua" if question_swahili else "Step"
                style = ParagraphStyle("last-step", parent=STYLES["body"], keepWithNext=True) if index == len(question["steps"]) and answer_height < 280 else STYLES["body"]
                part_story.append(Paragraph(f"<b>{label} {index}:</b> {escape(step).replace(chr(10), '<br/>')}", style))
            part_story.append(answer_box)
            if question.get("tip"):
                part_story.append(para(("Kidokezo cha kujifunza: " if question_swahili else "Study Tip: ") + question["tip"], "tip"))
            summary = data.get("summaries", {}).get(section)
            if question_index == len(questions) - 1 and summary:
                part_story.extend([HRFlowable(width="100%", color=colors.HexColor("#d9e1e6")), para(("Muhtasari wa sehemu: " if question_swahili else "Section Summary: ") + summary, "summary")])
            question_height = sum(item.wrap(CONTENT_WIDTH, HEIGHT)[1] + item.getSpaceBefore() + item.getSpaceAfter() for item in part_story)
            if question_height > HEIGHT - 132:
                answer_position = part_story.index(answer_box)
                story.append(KeepTogether(part_story[:answer_position]))
                story.extend(part_story[answer_position:])
            else:
                story.append(KeepTogether(part_story))
    if data.get("references"):
        reference_story = [para("Marejeo ya uhakiki" if swahili else "Source Checks", "prompt")]
        for reference in data["references"]:
            title, url = escape(reference["title"]), escape(reference["url"], {'"': '&quot;'})
            reference_story.append(Paragraph(f'<link href="{url}" color="#1a5276">{title}</link>', STYLES["body"]))
        story.append(KeepTogether(reference_story))
    doc.build(story)
    if not publish:
        print(f"Rendered draft {data['output']} ({len(data['questions'])} answered parts)")
        return out
    target = ROOT / "answer_keys" / data["output"]
    temporary = target.with_suffix(".publishing")
    shutil.copy2(out, temporary)
    try:
        for attempt in range(3):
            try:
                temporary.replace(target)
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(.2)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Built {data['output']} ({len(data['questions'])} answered parts)")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="*")
    parser.add_argument("--draft", action="store_true", help="Render to output/pdf without publishing to the website")
    args = parser.parse_args()
    sources = [Path(p) for p in args.sources] if args.sources else sorted((ROOT / "answer_keys" / "solutions").glob("*.json"))
    for source in sources:
        build(json.loads(source.read_text(encoding="utf-8")), publish=not args.draft)
