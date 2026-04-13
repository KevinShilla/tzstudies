"""
Generate Answer Key PDF for BasicMath Form 4 (CSEE) 2023 NECTA Exam
Uses reportlab to create a branded, student-friendly PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable
import os

# ── Colors ──
DARK_BLUE = HexColor("#1a237e")
GREEN = HexColor("#2e7d32")
LIGHT_GREEN = HexColor("#e8f5e9")
LIGHT_BLUE = HexColor("#e3f2fd")
LIGHT_YELLOW = HexColor("#fffde7")
LIGHT_RED = HexColor("#fce4ec")
LIGHT_ORANGE = HexColor("#fff3e0")
GRAY = HexColor("#f5f5f5")
DARK_GRAY = HexColor("#424242")
MED_GRAY = HexColor("#757575")
BORDER_GRAY = HexColor("#e0e0e0")
ANSWER_BG = HexColor("#e8f5e9")
WARNING_BG = HexColor("#fff8e1")
WARNING_BORDER = HexColor("#f9a825")
TIP_BG = HexColor("#e3f2fd")
TIP_BORDER = HexColor("#1565c0")

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BasicMath-F4-2023 (Answer Key).pdf")

PAGE_W, PAGE_H = A4


# ── Page footer ──
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MED_GRAY)
    canvas.drawCentredString(PAGE_W / 2, 18 * mm,
                             "mytzstudies.com | Free Tanzanian Exam Resources")
    canvas.restoreState()


def build_styles():
    ss = getSampleStyleSheet()

    ss.add(ParagraphStyle(
        "CoverTitle", parent=ss["Title"],
        fontName="Helvetica-Bold", fontSize=36, leading=44,
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6
    ))
    ss.add(ParagraphStyle(
        "CoverTagline", parent=ss["Normal"],
        fontName="Helvetica", fontSize=16, leading=22,
        textColor=GREEN, alignment=TA_CENTER, spaceAfter=30
    ))
    ss.add(ParagraphStyle(
        "TitlePageHeading", parent=ss["Title"],
        fontName="Helvetica-Bold", fontSize=28, leading=36,
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10
    ))
    ss.add(ParagraphStyle(
        "TitlePageSub", parent=ss["Normal"],
        fontName="Helvetica", fontSize=16, leading=22,
        textColor=DARK_GRAY, alignment=TA_CENTER, spaceAfter=6
    ))
    ss.add(ParagraphStyle(
        "QuestionHeader", parent=ss["Heading1"],
        fontName="Helvetica-Bold", fontSize=16, leading=22,
        textColor=DARK_BLUE, spaceAfter=8, spaceBefore=18,
        borderWidth=0, borderPadding=0,
    ))
    ss.add(ParagraphStyle(
        "SubQuestion", parent=ss["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=HexColor("#283593"), spaceAfter=4, spaceBefore=10,
    ))
    ss.add(ParagraphStyle(
        "BodyText2", parent=ss["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=15,
        textColor=DARK_GRAY, spaceAfter=4, alignment=TA_LEFT,
    ))
    ss.add(ParagraphStyle(
        "StepText", parent=ss["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=15,
        textColor=DARK_GRAY, spaceAfter=2, leftIndent=18,
    ))
    ss.add(ParagraphStyle(
        "AnswerText", parent=ss["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=HexColor("#1b5e20"), spaceAfter=6,
    ))
    ss.add(ParagraphStyle(
        "SectionBanner", parent=ss["Title"],
        fontName="Helvetica-Bold", fontSize=20, leading=28,
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10, spaceBefore=20,
    ))
    ss.add(ParagraphStyle(
        "FooterURL", parent=ss["Normal"],
        fontName="Helvetica-Bold", fontSize=14, leading=18,
        textColor=GREEN, alignment=TA_CENTER,
    ))
    return ss


# ── Helper functions ──
def make_warning_box(title_text, body_text, avail_w):
    data = [[Paragraph(f"<b>Common Mistake Warning:</b> {title_text}",
                        ParagraphStyle("w", fontName="Helvetica-Bold", fontSize=10,
                                       leading=14, textColor=HexColor("#e65100"))),
            ],
            [Paragraph(body_text,
                        ParagraphStyle("wb", fontName="Helvetica", fontSize=9.5,
                                       leading=13, textColor=HexColor("#bf360c")))]]
    t = Table(data, colWidths=[avail_w - 24])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WARNING_BG),
        ("BOX", (0, 0), (-1, -1), 1.5, WARNING_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def make_tip_box(body_text, avail_w):
    data = [[Paragraph(f"<b>Study Tip:</b> {body_text}",
                        ParagraphStyle("t", fontName="Helvetica", fontSize=9.5,
                                       leading=13, textColor=HexColor("#0d47a1")))]]
    t = Table(data, colWidths=[avail_w - 24])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TIP_BG),
        ("BOX", (0, 0), (-1, -1), 1.5, TIP_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def make_answer_highlight(text, avail_w):
    data = [[Paragraph(text,
                        ParagraphStyle("a", fontName="Helvetica-Bold", fontSize=11,
                                       leading=16, textColor=HexColor("#1b5e20")))]]
    t = Table(data, colWidths=[avail_w - 24])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ANSWER_BG),
        ("BOX", (0, 0), (-1, -1), 1, HexColor("#66bb6a")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def section_divider():
    return HRFlowable(width="100%", thickness=1, color=BORDER_GRAY,
                      spaceBefore=10, spaceAfter=10)


def S(text, style):
    """Shortcut for Paragraph."""
    return Paragraph(text, style)


# ── Cover Page ──
def build_cover_page(story, ss, avail_w):
    story.append(Spacer(1, 80))
    story.append(S("myTZStudies", ss["CoverTitle"]))
    story.append(S("Your Free Exam Prep Resource", ss["CoverTagline"]))
    story.append(Spacer(1, 30))

    features = [
        "Free Past Papers", "Answer Keys", "Study Guides",
        "Practice Tests", "Topic Summaries", "Exam Tips"
    ]
    colors_list = [LIGHT_BLUE, LIGHT_GREEN, LIGHT_YELLOW,
                   LIGHT_ORANGE, LIGHT_RED, GRAY]
    box_w = (avail_w - 30) / 3
    box_h = 50

    rows = []
    for r in range(2):
        row = []
        for c in range(3):
            idx = r * 3 + c
            cell_p = Paragraph(
                f'<para alignment="center"><font face="Helvetica-Bold" size="11" '
                f'color="{DARK_BLUE.hexval()}">{features[idx]}</font></para>',
                ss["BodyText2"]
            )
            row.append(cell_p)
        rows.append(row)

    t = Table(rows, colWidths=[box_w] * 3, rowHeights=[box_h] * 2)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_BLUE),
        ("BACKGROUND", (1, 0), (1, 0), LIGHT_GREEN),
        ("BACKGROUND", (2, 0), (2, 0), LIGHT_YELLOW),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT_ORANGE),
        ("BACKGROUND", (1, 1), (1, 1), LIGHT_RED),
        ("BACKGROUND", (2, 1), (2, 1), GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 60))
    story.append(S("mytzstudies.com", ss["FooterURL"]))
    story.append(PageBreak())


# ── Title Page ──
def build_title_page(story, ss):
    story.append(Spacer(1, 100))
    story.append(S("ANSWER KEY", ss["TitlePageHeading"]))
    story.append(Spacer(1, 20))
    story.append(S("Subject: Basic Mathematics", ss["TitlePageSub"]))
    story.append(S("Level: Form Four (CSEE)", ss["TitlePageSub"]))
    story.append(S("Year: 2023", ss["TitlePageSub"]))
    story.append(S("Examination: NECTA", ss["TitlePageSub"]))
    story.append(S("Type: Answer Key with Detailed Solutions", ss["TitlePageSub"]))
    story.append(Spacer(1, 40))
    story.append(S("14 Questions | Sections A &amp; B", ss["TitlePageSub"]))
    story.append(S("Complete step-by-step solutions with study tips", ss["TitlePageSub"]))
    story.append(PageBreak())


# ── Last Page ──
def build_last_page(story, ss):
    story.append(PageBreak())
    story.append(Spacer(1, 150))
    story.append(S("Thank you for using myTZStudies!", ss["TitlePageHeading"]))
    story.append(Spacer(1, 20))
    story.append(S("Visit mytzstudies.com for more free resources", ss["TitlePageSub"]))
    story.append(Spacer(1, 10))
    story.append(S("Free past papers, answer keys, and study guides for all subjects.",
                    ss["TitlePageSub"]))
    story.append(Spacer(1, 30))
    story.append(S("mytzstudies.com", ss["FooterURL"]))


# ══════════════════════════════════════════════════════════════
#  ALL 14 QUESTIONS
# ══════════════════════════════════════════════════════════════

def build_questions(story, ss, W):
    body = ss["BodyText2"]
    step = ss["StepText"]
    qh = ss["QuestionHeader"]
    sq = ss["SubQuestion"]

    # ── SECTION A BANNER ──
    story.append(S("SECTION A", ss["SectionBanner"]))
    story.append(S("<i>Answer ALL questions in this section.</i>", body))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 1
    # ═══════════════════════════════════════
    story.append(S("Question 1", qh))

    # Q1(a)(i)
    story.append(S("(a)(i) Arrange 0.6 recurring, 3/5, and 20% of 13/4 in ascending order", sq))
    story.append(S("<b>Step 1:</b> Convert each value to a decimal for easy comparison.", body))
    story.append(S("0.6 recurring = 0.6666... = 2/3", step))
    story.append(S("3/5 = 0.6", step))
    story.append(S("20% of 13/4 = 0.2 x 3.25 = 0.65", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Compare the decimals: 0.6 &lt; 0.65 &lt; 0.6666...", body))
    story.append(make_answer_highlight(
        "Answer: 3/5 (0.6), then 20% of 13/4 (0.65), then 0.6 recurring (0.667)", W))
    story.append(make_warning_box(
        "Don't confuse 0.6 recurring with 0.6!",
        "0.6 recurring (0.6666...) equals 2/3, which is larger than 0.6 or 0.65. "
        "Always convert to decimals when comparing fractions and percentages.", W))
    story.append(Spacer(1, 6))

    # Q1(a)(ii)
    story.append(S("(a)(ii) Evaluate: 13 - 2 x 3 + 14 / (2 + 5)", sq))
    story.append(S("<b>Step 1:</b> Follow BODMAS/PEMDAS. First, brackets: (2 + 5) = 7", body))
    story.append(S("<b>Step 2:</b> Division: 14 / 7 = 2", body))
    story.append(S("<b>Step 3:</b> Multiplication: 2 x 3 = 6", body))
    story.append(S("<b>Step 4:</b> Left to right: 13 - 6 + 2 = 9", body))
    story.append(make_answer_highlight("Answer: 9", W))
    story.append(make_tip_box(
        "Always remember BODMAS: Brackets, Orders, Division/Multiplication (left to right), "
        "Addition/Subtraction (left to right). This is one of the most tested concepts!", W))
    story.append(Spacer(1, 6))

    # Q1(b)
    story.append(S("(b) Find the LCM of 2, 3, and 5 by listing multiples", sq))
    story.append(S("<b>Step 1:</b> List multiples of each number:", body))
    story.append(S("Multiples of 2: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, <b>30</b>, ...", step))
    story.append(S("Multiples of 3: 3, 6, 9, 12, 15, 18, 21, 24, 27, <b>30</b>, ...", step))
    story.append(S("Multiples of 5: 5, 10, 15, 20, 25, <b>30</b>, ...", step))
    story.append(S("<b>Step 2:</b> The smallest number that appears in ALL three lists is 30.", body))
    story.append(make_answer_highlight("Answer: LCM = 30", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 2
    # ═══════════════════════════════════════
    story.append(S("Question 2", qh))

    # Q2(a)
    story.append(S("(a) Solve the simultaneous equations: 5^(x - 2y) = 25 and 3^(2x) / 3^y = 3^4", sq))
    story.append(S("<b>Step 1:</b> Rewrite using same bases.", body))
    story.append(S("Equation 1: 5^(x - 2y) = 5^2, so x - 2y = 2 ... (i)", step))
    story.append(S("Equation 2: 3^(2x - y) = 3^4, so 2x - y = 4 ... (ii)", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> From (i): x = 2 + 2y", body))
    story.append(S("<b>Step 3:</b> Substitute into (ii):", body))
    story.append(S("2(2 + 2y) - y = 4", step))
    story.append(S("4 + 4y - y = 4", step))
    story.append(S("3y = 0, so y = 0", step))
    story.append(S("<b>Step 4:</b> Back-substitute: x = 2 + 2(0) = 2", body))
    story.append(make_answer_highlight("Answer: x = 2, y = 0", W))
    story.append(make_tip_box(
        "When solving exponential equations, always rewrite both sides with the same base "
        "first. Then equate the exponents to get simple linear equations.", W))
    story.append(Spacer(1, 6))

    # Q2(b)
    story.append(S("(b) Solve: 4 + 3 log_3(x) = log_3(24)", sq))
    story.append(S("<b>Step 1:</b> Rearrange: 3 log_3(x) = log_3(24) - 4", body))
    story.append(S("<b>Step 2:</b> Note that 4 = log_3(81) since 3^4 = 81", body))
    story.append(S("<b>Step 3:</b> Use log laws: log_3(x^3) = log_3(24) - log_3(81) = log_3(24/81)", body))
    story.append(S("<b>Step 4:</b> Simplify: 24/81 = 8/27", body))
    story.append(S("<b>Step 5:</b> So x^3 = 8/27, therefore x = cube root of 8/27 = 2/3", body))
    story.append(make_answer_highlight("Answer: x = 2/3", W))
    story.append(make_warning_box(
        "Don't forget to convert constants to logarithmic form!",
        "The number 4 must be written as log_3(81) before you can combine it with other log terms. "
        "A common error is trying to subtract 4 directly from log_3(24).", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 3
    # ═══════════════════════════════════════
    story.append(S("Question 3", qh))

    # Q3(a)
    story.append(S("(a) Given the universal set U = {15, 30, 45, 60, 75}, A = {15, 45}, B = {30, 60}. "
                    "Find (A union B)'", sq))
    story.append(S("<b>Step 1:</b> Find A union B = {15, 30, 45, 60}", body))
    story.append(S("<b>Step 2:</b> The complement (A union B)' = U - (A union B) = {75}", body))
    story.append(make_answer_highlight("Answer: (A union B)' = {75}", W))
    story.append(Spacer(1, 6))

    # Q3(b)(i)
    story.append(S("(b)(i) A class has 50 students: 35 boys and 15 girls. "
                    "Find the probability of selecting a boy.", sq))
    story.append(S("<b>Step 1:</b> P(boy) = Number of boys / Total students = 35/50", body))
    story.append(S("<b>Step 2:</b> Simplify: 35/50 = 7/10", body))
    story.append(make_answer_highlight("Answer: P(boy) = 7/10 = 0.7", W))
    story.append(Spacer(1, 6))

    # Q3(b)(ii)
    story.append(S("(b)(ii) A person has 2 shirts (blue, red) and 3 trousers (black, green, yellow). "
                    "Find P(blue shirt AND black trouser).", sq))
    story.append(S("<b>Step 1:</b> P(blue shirt) = 1/2", body))
    story.append(S("<b>Step 2:</b> P(black trouser) = 1/3", body))
    story.append(S("<b>Step 3:</b> Since the events are independent: P(both) = (1/2) x (1/3) = 1/6", body))
    story.append(make_answer_highlight("Answer: P(blue shirt and black trouser) = 1/6", W))
    story.append(make_tip_box(
        "For independent events, multiply the individual probabilities. "
        "Make sure to list all possibilities if you are unsure whether events are independent.", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 4
    # ═══════════════════════════════════════
    story.append(S("Question 4", qh))

    # Q4(a)
    story.append(S("(a) Show that triangle A(4, -4), B(-6, -2), C(2, 6) is isosceles.", sq))
    story.append(S("<b>Step 1:</b> Find the length of each side using the distance formula.", body))
    story.append(S("AB = sqrt[(4-(-6))^2 + (-4-(-2))^2] = sqrt[100 + 4] = sqrt(104)", step))
    story.append(S("BC = sqrt[(-6-2)^2 + (-2-6)^2] = sqrt[64 + 64] = sqrt(128)", step))
    story.append(S("AC = sqrt[(4-2)^2 + (-4-6)^2] = sqrt[4 + 100] = sqrt(104)", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Compare: AB = AC = sqrt(104)", body))
    story.append(make_answer_highlight(
        "Answer: Since AB = AC = sqrt(104), two sides are equal. Therefore triangle ABC is isosceles.", W))
    story.append(Spacer(1, 6))

    # Q4(b)
    story.append(S("(b) A man walks 4 km from P to Q on bearing N60E, then 3 km from Q to R on bearing N30W. "
                    "Find the resultant displacement.", sq))
    story.append(S("<b>Step 1:</b> Break each leg into x (East) and y (North) components.", body))
    story.append(S("PQ: x = 4 sin 60 = 4 x (sqrt3/2) = 2sqrt3, y = 4 cos 60 = 4 x 0.5 = 2", step))
    story.append(S("QR: x = -3 sin 30 = -3 x 0.5 = -1.5, y = 3 cos 30 = 3 x (sqrt3/2) = 1.5sqrt3", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Add components:", body))
    story.append(S("Total x = 2sqrt3 - 1.5 = 3.464 - 1.5 = 1.964", step))
    story.append(S("Total y = 2 + 1.5sqrt3 = 2 + 2.598 = 4.598", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> Resultant = sqrt(1.964^2 + 4.598^2) = sqrt(3.857 + 21.142) = sqrt(25) = 5 km", body))
    story.append(make_answer_highlight("Answer: The resultant displacement is 5 km", W))
    story.append(make_tip_box(
        "For bearing problems, always resolve into North-South and East-West components. "
        "Remember: N60E means 60 degrees measured from North toward East.", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 5
    # ═══════════════════════════════════════
    story.append(S("Question 5", qh))

    # Q5(a)
    story.append(S("(a) In the figure, angle RPQ = angle PQR and angle SPQ = angle SQP. Find angle RPS.", sq))
    story.append(S("<b>Step 1:</b> In triangle PQR, since angle RPQ = angle PQR:", body))
    story.append(S("From the figure, angle PQR = 72 degrees.", step))
    story.append(S("So angle RPQ = 72 degrees (given equal).", step))
    story.append(S("Angle PRQ = 180 - 72 - 72 = 36 degrees.", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> In triangle PQS, since angle SPQ = angle SQP:", body))
    story.append(S("From the figure, angle PSQ = 112 degrees.", step))
    story.append(S("So angle SPQ = angle SQP = (180 - 112) / 2 = 34 degrees.", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> R is above PQ and S is below PQ.", body))
    story.append(S("Angle RPS = angle RPQ + angle QPS = 72 + 34 = 106 degrees.", step))
    story.append(make_answer_highlight("Answer: Angle RPS = 106 degrees", W))
    story.append(Spacer(1, 6))

    # Q5(b)
    story.append(S("(b) A rectangular field is 72 m by 40 m. A triangular field with base 60 m has the same area. "
                    "Find the height of the triangular field.", sq))
    story.append(S("<b>Step 1:</b> Area of rectangle = 72 x 40 = 2880 m squared", body))
    story.append(S("<b>Step 2:</b> Area of triangle = (1/2) x base x height = (1/2) x 60 x h", body))
    story.append(S("<b>Step 3:</b> Set equal: (1/2) x 60 x h = 2880", body))
    story.append(S("30h = 2880", step))
    story.append(S("h = 2880 / 30 = 96 m", step))
    story.append(make_answer_highlight("Answer: Height = 96 m", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 6
    # ═══════════════════════════════════════
    story.append(S("Question 6", qh))

    # Q6(a)
    story.append(S("(a) Anna walks 24 km per day. What is the distance she walks in 2 days in metres?", sq))
    story.append(S("<b>Step 1:</b> Distance in 2 days = 24 x 2 = 48 km", body))
    story.append(S("<b>Step 2:</b> Convert to metres: 48 km = 48 x 1000 = 48,000 m", body))
    story.append(make_answer_highlight("Answer: 48,000 metres", W))
    story.append(Spacer(1, 6))

    # Q6(b)
    story.append(S("(b) The buying price (C) is proportional to the selling price (s). "
                    "When s = 20,000 then C = 18,000.", sq))
    story.append(S("<b>(i) Find the equation connecting C and s:</b>", body))
    story.append(S("<b>Step 1:</b> Since C is proportional to s: C = ks (where k is a constant)", body))
    story.append(S("<b>Step 2:</b> Substitute: 18,000 = k x 20,000", body))
    story.append(S("k = 18,000 / 20,000 = 9/10", step))
    story.append(make_answer_highlight("Answer (i): C = (9/10)s", W))
    story.append(Spacer(1, 6))
    story.append(S("<b>(ii) If buying price increases by 15%, find the new selling price:</b>", body))
    story.append(S("<b>Step 1:</b> New buying price = 18,000 x 1.15 = 20,700", body))
    story.append(S("<b>Step 2:</b> Using C = (9/10)s: 20,700 = (9/10)s", body))
    story.append(S("s = 20,700 x 10/9 = 23,000", step))
    story.append(make_answer_highlight("Answer (ii): New selling price = 23,000 Tsh", W))
    story.append(make_tip_box(
        "Direct proportion means C = ks. Always find k first using the given values, "
        "then use the equation for any new calculations.", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 7
    # ═══════════════════════════════════════
    story.append(S("Question 7", qh))

    # Q7(a)
    story.append(S("(a) Ally and Jane share 64,000 Tsh in the ratio 3:5. Find the difference.", sq))
    story.append(S("<b>Step 1:</b> Total parts = 3 + 5 = 8", body))
    story.append(S("<b>Step 2:</b> Ally's share = (3/8) x 64,000 = 24,000 Tsh", body))
    story.append(S("<b>Step 3:</b> Jane's share = (5/8) x 64,000 = 40,000 Tsh", body))
    story.append(S("<b>Step 4:</b> Difference = 40,000 - 24,000 = 16,000 Tsh", body))
    story.append(make_answer_highlight("Answer: The difference is 16,000 Tsh", W))
    story.append(Spacer(1, 6))

    # Q7(b)
    story.append(S("(b) Prepare a trial balance from Mr. Mrisho's cash account.", sq))
    story.append(S("<b>Step 1:</b> Summarize all debit entries (money received):", body))
    story.append(S("Capital: 1,500,000 Tsh", step))
    story.append(S("Sales: 1,200,000 + 800,000 = 2,000,000 Tsh", step))
    story.append(S("Total Credit side: 3,500,000 Tsh", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Summarize all credit entries (money paid out):", body))
    story.append(S("Purchases: 1,000,000 + 1,400,000 = 2,400,000 Tsh", step))
    story.append(S("Transport: 200,000 Tsh", step))
    story.append(S("Total Debit side: 2,600,000 Tsh", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> Cash balance = 3,500,000 - 2,600,000 = 900,000 Tsh", body))
    story.append(Spacer(1, 4))

    # Trial balance table
    tb_data = [
        ["Account", "Debit (Tsh)", "Credit (Tsh)"],
        ["Cash", "900,000", ""],
        ["Purchases", "2,400,000", ""],
        ["Transport", "200,000", ""],
        ["Capital", "", "1,500,000"],
        ["Sales", "", "2,000,000"],
        ["Total", "3,500,000", "3,500,000"],
    ]
    tb_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GREEN),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ])
    tb = Table(tb_data, colWidths=[W * 0.4, W * 0.3, W * 0.3])
    tb.setStyle(tb_style)
    story.append(tb)
    story.append(make_answer_highlight("Answer: Trial balance totals: Debit = Credit = 3,500,000 Tsh", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 8
    # ═══════════════════════════════════════
    story.append(S("Question 8", qh))

    # Q8(a)
    story.append(S("(a) The general term is n(2n - 1). Find the first 4 terms and state whether it is AP, GP, or neither.", sq))
    story.append(S("<b>Step 1:</b> Compute the first four terms:", body))
    story.append(S("n = 1: 1(2(1) - 1) = 1 x 1 = 1", step))
    story.append(S("n = 2: 2(2(2) - 1) = 2 x 3 = 6", step))
    story.append(S("n = 3: 3(2(3) - 1) = 3 x 5 = 15", step))
    story.append(S("n = 4: 4(2(4) - 1) = 4 x 7 = 28", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Check for AP (constant difference):", body))
    story.append(S("Differences: 6-1=5, 15-6=9, 28-15=13. NOT constant, so not AP.", step))
    story.append(S("<b>Step 3:</b> Check for GP (constant ratio):", body))
    story.append(S("Ratios: 6/1=6, 15/6=2.5, 28/15=1.87. NOT constant, so not GP.", step))
    story.append(make_answer_highlight("Answer: First 4 terms are 1, 6, 15, 28. The sequence is neither AP nor GP.", W))
    story.append(Spacer(1, 6))

    # Q8(b)
    story.append(S("(b) Sum of first 11 terms of an AP is 517, first term is 7. "
                    "Find the sum of the 4th and 9th terms.", sq))
    story.append(S("<b>Step 1:</b> Use the sum formula: S_n = (n/2)(2a + (n-1)d)", body))
    story.append(S("517 = (11/2)(2(7) + 10d)", step))
    story.append(S("517 = (11/2)(14 + 10d)", step))
    story.append(S("1034 = 11(14 + 10d)", step))
    story.append(S("14 + 10d = 94", step))
    story.append(S("10d = 80, so d = 8", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Find the 4th and 9th terms:", body))
    story.append(S("a_4 = 7 + 3(8) = 7 + 24 = 31", step))
    story.append(S("a_9 = 7 + 8(8) = 7 + 64 = 71", step))
    story.append(S("<b>Step 3:</b> Sum = 31 + 71 = 102", body))
    story.append(make_answer_highlight("Answer: Sum of the 4th and 9th terms = 102", W))
    story.append(make_tip_box(
        "In an AP, the sum of terms equidistant from the ends is always the same. "
        "For example, a_4 + a_9 could also be found using a_1 + a_12 if you have 12 terms.", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 9
    # ═══════════════════════════════════════
    story.append(S("Question 9", qh))

    # Q9(a)
    story.append(S("(a) A rectangular plot is 40 m long with a diagonal of 50 m. Find the width.", sq))
    story.append(S("<b>Step 1:</b> Use Pythagoras' theorem: width^2 + 40^2 = 50^2", body))
    story.append(S("width^2 + 1600 = 2500", step))
    story.append(S("width^2 = 900", step))
    story.append(S("width = 30 m", step))
    story.append(make_answer_highlight("Answer: Width = 30 m", W))
    story.append(Spacer(1, 6))

    # Q9(b)(i)
    story.append(S("(b)(i) Given 13 cos A - 5 = 0, find tan A.", sq))
    story.append(S("<b>Step 1:</b> Solve for cos A: cos A = 5/13", body))
    story.append(S("<b>Step 2:</b> Find sin A using sin^2 A + cos^2 A = 1:", body))
    story.append(S("sin^2 A = 1 - (5/13)^2 = 1 - 25/169 = 144/169", step))
    story.append(S("sin A = 12/13", step))
    story.append(S("<b>Step 3:</b> tan A = sin A / cos A = (12/13) / (5/13) = 12/5", body))
    story.append(make_answer_highlight("Answer: tan A = 12/5", W))
    story.append(make_tip_box(
        "Remember the 5-12-13 right triangle! It is one of the most common Pythagorean triples in exams, "
        "alongside 3-4-5 and 8-15-17.", W))
    story.append(Spacer(1, 6))

    # Q9(b)(ii)
    story.append(S("(b)(ii) Triangle ABC: AB = 8, AC = 5, angle BAC = 60 degrees. Find BC.", sq))
    story.append(S("<b>Step 1:</b> Apply the cosine rule: BC^2 = AB^2 + AC^2 - 2(AB)(AC)cos(BAC)", body))
    story.append(S("BC^2 = 8^2 + 5^2 - 2(8)(5)cos 60", step))
    story.append(S("BC^2 = 64 + 25 - 80(0.5)", step))
    story.append(S("BC^2 = 89 - 40 = 49", step))
    story.append(S("BC = 7", step))
    story.append(make_answer_highlight("Answer: BC = 7 m", W))
    story.append(make_warning_box(
        "Don't forget the minus sign in the cosine rule!",
        "The formula is a^2 = b^2 + c^2 - 2bc cos A. The minus sign before 2bc cos A is crucial. "
        "Many students accidentally use a plus sign.", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 10
    # ═══════════════════════════════════════
    story.append(S("Question 10", qh))

    # Q10(a)
    story.append(S("(a) If x = -3 and x = 1/3 are roots of ax^2 + bx + c = 0, find a, b, and c.", sq))
    story.append(S("<b>Step 1:</b> Write the equation from its roots:", body))
    story.append(S("(x + 3)(x - 1/3) = 0", step))
    story.append(S("<b>Step 2:</b> Expand:", body))
    story.append(S("x^2 + 3x - x/3 - 1 = 0", step))
    story.append(S("x^2 + (9x - x)/3 - 1 = 0", step))
    story.append(S("x^2 + (8/3)x - 1 = 0", step))
    story.append(S("<b>Step 3:</b> Multiply through by 3 to clear fractions:", body))
    story.append(S("3x^2 + 8x - 3 = 0", step))
    story.append(make_answer_highlight("Answer: a = 3, b = 8, c = -3", W))
    story.append(Spacer(1, 6))

    # Q10(b)
    story.append(S("(b) Solve the inequality: 10 - x &lt;= 3(x + 10). List the first four integer values.", sq))
    story.append(S("<b>Step 1:</b> Expand the right side: 10 - x &lt;= 3x + 30", body))
    story.append(S("<b>Step 2:</b> Collect terms: -x - 3x &lt;= 30 - 10", body))
    story.append(S("-4x &lt;= 20", step))
    story.append(S("<b>Step 3:</b> Divide by -4 (flip the inequality sign!):", body))
    story.append(S("x &gt;= -5", step))
    story.append(make_answer_highlight("Answer: x >= -5. First four integer values: -5, -4, -3, -2", W))
    story.append(make_warning_box(
        "Flip the inequality sign when dividing by a negative number!",
        "This is one of the most common mistakes. When you divide (or multiply) both sides of an "
        "inequality by a negative number, you MUST reverse the inequality sign.", W))

    # ── SECTION B ──
    story.append(PageBreak())
    story.append(S("SECTION B", ss["SectionBanner"]))
    story.append(S("<i>Answer any FOUR questions from this section.</i>", body))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 11
    # ═══════════════════════════════════════
    story.append(S("Question 11 - Statistics", qh))
    story.append(S("Frequency table: 40-49 (2), 50-59 (4), 60-69 (7), 70-79 (9), 80-89 (5), 90-99 (3)", body))
    story.append(Spacer(1, 4))

    # Frequency table
    freq_data = [
        ["Class", "Frequency (f)", "Midpoint (x)", "fx", "Cumulative f"],
        ["40 - 49", "2", "44.5", "89", "2"],
        ["50 - 59", "4", "54.5", "218", "6"],
        ["60 - 69", "7", "64.5", "451.5", "13"],
        ["70 - 79", "9", "74.5", "670.5", "22"],
        ["80 - 89", "5", "84.5", "422.5", "27"],
        ["90 - 99", "3", "94.5", "283.5", "30"],
        ["Total", "30", "", "2135", ""],
    ]
    ft = Table(freq_data, colWidths=[W*0.18, W*0.18, W*0.2, W*0.2, W*0.24])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GREEN),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ft)
    story.append(Spacer(1, 8))

    # Q11(a) Median
    story.append(S("(a) Median", sq))
    story.append(S("<b>Step 1:</b> N = 30, so N/2 = 15. Find the class where cumulative frequency reaches 15.", body))
    story.append(S("Cumulative frequencies: 2, 6, 13, 22, 27, 30", step))
    story.append(S("The 15th value falls in the class 70-79 (cumulative reaches 22).", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Apply the median formula:", body))
    story.append(S("Median = L + ((N/2 - F) / f) x h", step))
    story.append(S("L = 69.5 (lower boundary), F = 13 (cumulative before), f = 9, h = 10", step))
    story.append(S("Median = 69.5 + ((15 - 13) / 9) x 10 = 69.5 + 2.22 = 71.72", step))
    story.append(make_answer_highlight("Answer: Median = 71.72", W))
    story.append(Spacer(1, 6))

    # Q11(b) Mean
    story.append(S("(b) Mean", sq))
    story.append(S("<b>Step 1:</b> Sum of fx = 89 + 218 + 451.5 + 670.5 + 422.5 + 283.5 = 2135", body))
    story.append(S("<b>Step 2:</b> Mean = Sum of fx / N = 2135 / 30 = 71.17", body))
    story.append(make_answer_highlight("Answer: Mean = 71.17", W))
    story.append(Spacer(1, 6))

    # Q11(c) Mode
    story.append(S("(c) Mode", sq))
    story.append(S("<b>Step 1:</b> Modal class = 70-79 (highest frequency = 9)", body))
    story.append(S("<b>Step 2:</b> Apply the mode formula:", body))
    story.append(S("Mode = L + ((f1 - f0) / (2f1 - f0 - f2)) x h", step))
    story.append(S("L = 69.5, f1 = 9, f0 = 7 (previous), f2 = 5 (next), h = 10", step))
    story.append(S("Mode = 69.5 + ((9 - 7) / (18 - 7 - 5)) x 10 = 69.5 + (2/6) x 10 = 69.5 + 3.33 = 72.83", step))
    story.append(make_answer_highlight("Answer: Mode = 72.83", W))
    story.append(make_tip_box(
        "For grouped data: use class boundaries (not class limits) in formulas. "
        "The lower boundary of 70-79 is 69.5, not 70. This is a common source of errors!", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 12
    # ═══════════════════════════════════════
    story.append(S("Question 12", qh))

    # Q12(a)
    story.append(S("(a) A square box (cube) ABCDEFGH has side 8 cm.", sq))

    story.append(S("<b>(i) Total surface area:</b>", body))
    story.append(S("A cube has 6 equal faces, each of area 8 x 8 = 64 cm^2", step))
    story.append(S("Total surface area = 6 x 64 = 384 cm^2", step))
    story.append(make_answer_highlight("Answer (i): Total surface area = 384 cm^2", W))
    story.append(Spacer(1, 6))

    story.append(S("<b>(ii) Length AF and its angle with the base ABCD:</b>", body))
    story.append(S("<b>Step 1:</b> In cube ABCDEFGH, A is at the bottom and F is above B.", body))
    story.append(S("The projection of F onto the base plane is B.", step))
    story.append(S("AB = 8 cm (horizontal), BF = 8 cm (vertical)", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Find AF:", body))
    story.append(S("AF = sqrt(AB^2 + BF^2) = sqrt(64 + 64) = sqrt(128) = 8sqrt(2) cm", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> Angle with base ABCD:", body))
    story.append(S("tan(theta) = BF / AB = 8/8 = 1", step))
    story.append(S("theta = arctan(1) = 45 degrees", step))
    story.append(make_answer_highlight("Answer (ii): AF = 8sqrt(2) cm, angle with base = 45 degrees", W))
    story.append(Spacer(1, 6))

    # Q12(b)
    story.append(S("(b) Boeing flies from (7 S, 45 E) to (9 N, 45 E) at 500 km/h. Departure at 8:00 am.", sq))
    story.append(S("<b>Step 1:</b> Both points are on the same longitude (45 E), so travel is along a meridian.", body))
    story.append(S("<b>Step 2:</b> Angular difference = 7 + 9 = 16 degrees (crossing the equator).", body))
    story.append(S("<b>Step 3:</b> Distance = 16 x 112 = 1792 km (using 1 degree = 112 km).", body))
    story.append(S("<b>Step 4:</b> Time = 1792 / 500 = 3.584 hours = 3 hours 35 minutes.", body))
    story.append(S("<b>Step 5:</b> Arrival time = 8:00 am + 3 hr 35 min = 11:35 am.", body))
    story.append(make_answer_highlight("Answer: Distance = 1792 km. Arrival time = 11:35 am", W))
    story.append(make_tip_box(
        "When two places share the same longitude, they are on the same meridian. "
        "The distance is simply the angular difference multiplied by 112 km (or 111 km, depending on the value given).", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 13
    # ═══════════════════════════════════════
    story.append(S("Question 13", qh))

    # Q13(a)
    story.append(S("(a) Solve for x and y in the matrix equation:", sq))
    story.append(S("[x, 4; 3, y] + [3x, 5; -3, 7] = [8, 9; 0, 9]", body))
    story.append(S("<b>Step 1:</b> Add corresponding elements:", body))
    story.append(S("x + 3x = 8  =>  4x = 8  =>  x = 2", step))
    story.append(S("4 + 5 = 9  (checks out)", step))
    story.append(S("3 + (-3) = 0  (checks out)", step))
    story.append(S("y + 7 = 9  =>  y = 2", step))
    story.append(make_answer_highlight("Answer: x = 2, y = 2", W))
    story.append(Spacer(1, 6))

    # Q13(b)
    story.append(S("(b) Multiple choice: 2 marks for correct, -1 for incorrect, 0 for unanswered. "
                    "Anna answered 49 questions and scored 62.", sq))
    story.append(S("<b>(i) Form the equations:</b>", body))
    story.append(S("Let x = correct answers, y = incorrect answers.", step))
    story.append(S("x + y = 49 ... (i)", step))
    story.append(S("2x - y = 62 ... (ii)", step))
    story.append(make_answer_highlight("Answer (i): x + y = 49 and 2x - y = 62", W))
    story.append(Spacer(1, 6))

    story.append(S("<b>(ii) Use inverse matrix to find x (correct answers):</b>", body))
    story.append(S("<b>Step 1:</b> Write in matrix form: [1, 1; 2, -1][x; y] = [49; 62]", body))
    story.append(S("<b>Step 2:</b> Find the inverse of [1, 1; 2, -1]:", body))
    story.append(S("det = (1)(-1) - (1)(2) = -1 - 2 = -3", step))
    story.append(S("Inverse = (1/-3)[-1, -1; -2, 1]", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> Multiply:", body))
    story.append(S("[x; y] = (1/-3)[-1(-1)(49) + (-1)(62); (-2)(49) + (1)(62)]", step))
    story.append(S("= (1/-3)[-49 - 62; -98 + 62]", step))
    story.append(S("= (1/-3)[-111; -36]", step))
    story.append(S("= [37; 12]", step))
    story.append(make_answer_highlight("Answer (ii): x = 37 correct answers, y = 12 incorrect answers", W))
    story.append(Spacer(1, 6))

    # Q13(c)
    story.append(S("(c) Rotate triangle A(1,3), B(2,5), C(4,1) by 180 degrees about the origin.", sq))
    story.append(S("<b>Rule:</b> For 180 degree rotation about origin: (x, y) maps to (-x, -y)", body))
    story.append(S("A(1, 3) maps to A'(-1, -3)", step))
    story.append(S("B(2, 5) maps to B'(-2, -5)", step))
    story.append(S("C(4, 1) maps to C'(-4, -1)", step))
    story.append(make_answer_highlight("Answer: A'(-1, -3), B'(-2, -5), C'(-4, -1)", W))
    story.append(make_tip_box(
        "Key rotation rules about the origin: 90 CW: (x,y) maps to (y,-x). "
        "90 CCW: (x,y) maps to (-y,x). 180: (x,y) maps to (-x,-y).", W))
    story.append(section_divider())

    # ═══════════════════════════════════════
    # QUESTION 14
    # ═══════════════════════════════════════
    story.append(S("Question 14", qh))

    # Q14(a)
    story.append(S("(a) Piecewise function: f(x) = -2 if 0 &lt; x &lt;= 5, and f(x) = x + 1 if -6 &lt;= x &lt; 0", sq))

    story.append(S("<b>(i) Find f(4) and f(-5):</b>", body))
    story.append(S("f(4): Since 0 &lt; 4 &lt;= 5, use f(x) = -2. So f(4) = -2", step))
    story.append(S("f(-5): Since -6 &lt;= -5 &lt; 0, use f(x) = x + 1. So f(-5) = -5 + 1 = -4", step))
    story.append(make_answer_highlight("Answer (i): f(4) = -2, f(-5) = -4", W))
    story.append(Spacer(1, 6))

    story.append(S("<b>(ii) State the domain and range:</b>", body))
    story.append(S("Domain: The set of all valid x values = [-6, 0) union (0, 5]", step))
    story.append(S("Note: x = 0 is not included in either piece.", step))
    story.append(Spacer(1, 4))
    story.append(S("Range: For the first piece (0 &lt; x &lt;= 5), f(x) = -2 always. Output = {-2}", step))
    story.append(S("For the second piece (-6 &lt;= x &lt; 0), f(x) = x + 1.", step))
    story.append(S("When x = -6: f(-6) = -5. When x approaches 0: f(x) approaches 1.", step))
    story.append(S("So this piece gives outputs from -5 to just below 1, i.e., [-5, 1).", step))
    story.append(make_answer_highlight("Answer (ii): Domain = [-6, 0) union (0, 5]. Range = [-5, 1) union {-2}", W))
    story.append(Spacer(1, 6))

    # Q14(b)
    story.append(S("(b) Linear programming: Air Tanzania has Type A (6 dam^2 parking, 20B cost) and "
                    "Type B (2 dam^2 parking, 30B cost). Space: 60 dam^2. Budget: 480B.", sq))
    story.append(S("<b>Step 1:</b> Define variables: Let a = number of Type A, b = number of Type B.", body))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 2:</b> Write the constraints:", body))
    story.append(S("Parking: 6a + 2b &lt;= 60, simplified to 3a + b &lt;= 30", step))
    story.append(S("Budget: 20a + 30b &lt;= 480, simplified to 2a + 3b &lt;= 48", step))
    story.append(S("Non-negativity: a &gt;= 0, b &gt;= 0", step))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 3:</b> Maximize: a + b (total number of airplanes).", body))
    story.append(Spacer(1, 4))
    story.append(S("<b>Step 4:</b> Find corner points of the feasible region:", body))
    story.append(S("Intersection of 3a + b = 30 and 2a + 3b = 48:", step))
    story.append(S("From first equation: b = 30 - 3a", step))
    story.append(S("Substitute: 2a + 3(30 - 3a) = 48  =>  2a + 90 - 9a = 48  =>  -7a = -42  =>  a = 6", step))
    story.append(S("b = 30 - 18 = 12", step))
    story.append(Spacer(1, 4))

    # Corner points table
    cp_data = [
        ["Corner Point", "a + b"],
        ["(0, 0)", "0"],
        ["(10, 0)", "10"],
        ["(6, 12)", "18"],
        ["(0, 16)", "16"],
    ]
    cpt = Table(cp_data, colWidths=[W*0.3, W*0.3])
    cpt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 3), (-1, 3), LIGHT_GREEN),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cpt)
    story.append(Spacer(1, 6))

    story.append(S("<b>Step 5:</b> Maximum value of a + b = 18, at point (6, 12).", body))
    story.append(make_answer_highlight(
        "Answer: The greatest number of airplanes = 18 (6 Type A + 12 Type B)", W))
    story.append(make_warning_box(
        "Don't forget to check ALL corner points!",
        "In linear programming, the optimal solution always occurs at a corner point of the feasible region. "
        "You must evaluate the objective function at every corner point and compare.", W))


# ══════════════════════════════════════════════════════════════
#  MAIN BUILD
# ══════════════════════════════════════════════════════════════

def main():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.5 * cm,
        title="BasicMath Form 4 (CSEE) 2023 - Answer Key",
        author="myTZStudies",
    )
    ss = build_styles()
    avail_w = PAGE_W - 4 * cm  # usable width

    story = []
    build_cover_page(story, ss, avail_w)
    build_title_page(story, ss)
    build_questions(story, ss, avail_w)
    build_last_page(story, ss)

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF generated successfully: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
