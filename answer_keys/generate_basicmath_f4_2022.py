#!/usr/bin/env python3
"""Generate BasicMath Form 4 (CSEE) 2022 NECTA Answer Key PDF."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)
from reportlab.lib import colors

# ── Colors ──
DARK_BLUE = HexColor("#1a237e")
GREEN = HexColor("#2e7d32")
LIGHT_BLUE_BG = HexColor("#e3f2fd")
LIGHT_GREEN_BG = HexColor("#e8f5e9")
LIGHT_YELLOW_BG = HexColor("#fffde7")
LIGHT_ORANGE_BG = HexColor("#fff3e0")
LIGHT_RED_BG = HexColor("#fce4ec")
GREY_BG = HexColor("#f5f5f5")
BORDER_BLUE = HexColor("#1565c0")
BORDER_GREEN = HexColor("#2e7d32")
BORDER_ORANGE = HexColor("#e65100")
BORDER_RED = HexColor("#c62828")
MEDIUM_GREY = HexColor("#616161")
LIGHT_GREY = HexColor("#eeeeee")

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "BasicMath-F4-2022 (Answer Key).pdf")

WIDTH, HEIGHT = A4

# ── Styles ──
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kwargs):
    return ParagraphStyle(name, parent=styles[parent], **kwargs)

sTitle = make_style('CTitle', fontSize=28, leading=34, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6, fontName='Helvetica-Bold')
sSubtitle = make_style('CSubtitle', fontSize=14, leading=18, textColor=GREEN, alignment=TA_CENTER, spaceAfter=4)
sHeading1 = make_style('H1x', fontSize=18, leading=22, textColor=DARK_BLUE, fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=8)
sHeading2 = make_style('H2x', fontSize=14, leading=18, textColor=DARK_BLUE, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
sBody = make_style('Bodyx', fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=4)
sStep = make_style('Stepx', fontSize=11, leading=15, leftIndent=18, spaceAfter=3)
sMath = make_style('Mathx', fontSize=11, leading=16, leftIndent=18, fontName='Courier', spaceAfter=3)
sAnswer = make_style('Answerx', fontSize=12, leading=16, fontName='Helvetica-Bold', textColor=DARK_BLUE, leftIndent=18, spaceAfter=6)
sTip = make_style('Tipx', fontSize=10, leading=14, textColor=HexColor("#1b5e20"), leftIndent=24, rightIndent=12, spaceAfter=4)
sWarn = make_style('Warnx', fontSize=10, leading=14, textColor=HexColor("#b71c1c"), leftIndent=24, rightIndent=12, spaceAfter=4)
sFooter = make_style('Footerx', fontSize=9, leading=11, textColor=MEDIUM_GREY, alignment=TA_CENTER)
sSmall = make_style('Smallx', fontSize=10, leading=13, textColor=MEDIUM_GREY)
sCenterBody = make_style('CenterBodyx', fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=4)
sFeature = make_style('Featurex', fontSize=10, leading=14, alignment=TA_CENTER, textColor=HexColor("#333333"))
sBullet = make_style('Bulletx', fontSize=11, leading=15, leftIndent=30, bulletIndent=18, spaceAfter=3)

# ── Helpers ──
def hr():
    return HRFlowable(width="100%", thickness=1, color=LIGHT_GREY, spaceBefore=6, spaceAfter=6)

def colored_box(content_list, bg_color, border_color, title=None):
    """Create a colored box with border using a table."""
    inner = []
    if title:
        inner.append(Paragraph(title, make_style('boxtitle', fontSize=11, fontName='Helvetica-Bold', textColor=border_color, spaceAfter=4)))
    inner.extend(content_list)
    t = Table([[inner]], colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 1.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    return t

def tip_box(text):
    return colored_box([Paragraph(text, sTip)], LIGHT_GREEN_BG, BORDER_GREEN, "Study Tip")

def warn_box(text):
    return colored_box([Paragraph(text, sWarn)], LIGHT_RED_BG, BORDER_RED, "Common Mistake")

def answer_box(text):
    return colored_box([Paragraph(text, sAnswer)], LIGHT_BLUE_BG, BORDER_BLUE, "Answer")

def question_header(qnum, marks, topic):
    return Paragraph(f'<b>Question {qnum}</b>  <font color="#616161">[{marks} marks] - {topic}</font>', sHeading2)

def step(text):
    return Paragraph(text, sStep)

def math(text):
    return Paragraph(text, sMath)

def body(text):
    return Paragraph(text, sBody)

def sp(h=6):
    return Spacer(1, h)

# ── Footer ──
def footer_func(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(MEDIUM_GREY)
    canvas_obj.drawCentredString(WIDTH / 2, 20, "mytzstudies.com | Free Tanzanian Exam Resources")
    canvas_obj.drawRightString(WIDTH - 40, 20, f"Page {doc.page}")
    canvas_obj.restoreState()

# ── Build Story ──
story = []

# ════════════════════════════════════════
# COVER PAGE
# ════════════════════════════════════════
story.append(Spacer(1, 80))
story.append(Paragraph("myTZStudies", make_style('CoverTitle', fontSize=44, leading=52, textColor=DARK_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(Spacer(1, 10))
story.append(Paragraph("Your Free Exam Prep Resource", make_style('CoverSub', fontSize=16, leading=20, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(Spacer(1, 40))

# Feature boxes (2 columns x 3 rows)
features = [
    ("Complete Solutions", "Step-by-step answers\nfor every question"),
    ("Student Friendly", "Clear explanations in\nsimple language"),
    ("Exam Ready", "Formatted to match\nNECTA exam style"),
    ("Study Tips", "Helpful hints and\ncommon mistake warnings"),
    ("Free Forever", "100% free resources\nfor all students"),
    ("All Subjects", "Covering major CSEE\nand ACSEE subjects"),
]

feat_rows = []
for i in range(0, 6, 2):
    row_data = []
    for j in range(2):
        f = features[i + j]
        cell_content = [
            Paragraph(f'<b>{f[0]}</b>', make_style('ft', fontSize=12, alignment=TA_CENTER, textColor=DARK_BLUE, fontName='Helvetica-Bold', spaceAfter=4)),
            Paragraph(f[1].replace('\n', '<br/>'), make_style('fd', fontSize=9, alignment=TA_CENTER, textColor=MEDIUM_GREY, leading=13))
        ]
        row_data.append(cell_content)
    feat_rows.append(row_data)

feat_table = Table(feat_rows, colWidths=[(WIDTH - 120) / 2] * 2, rowHeights=[70] * 3)
feat_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG),
    ('BOX', (0, 0), (0, 0), 1, BORDER_BLUE),
    ('BOX', (1, 0), (1, 0), 1, BORDER_BLUE),
    ('BOX', (0, 1), (0, 1), 1, BORDER_BLUE),
    ('BOX', (1, 1), (1, 1), 1, BORDER_BLUE),
    ('BOX', (0, 2), (0, 2), 1, BORDER_BLUE),
    ('BOX', (1, 2), (1, 2), 1, BORDER_BLUE),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
]))
story.append(feat_table)

story.append(Spacer(1, 40))
story.append(Paragraph("mytzstudies.com", make_style('CoverURL', fontSize=18, leading=22, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(PageBreak())

# ════════════════════════════════════════
# TITLE PAGE
# ════════════════════════════════════════
story.append(Spacer(1, 60))
story.append(Paragraph("ANSWER KEY", sTitle))
story.append(Spacer(1, 20))

info_data = [
    ["Subject:", "Basic Mathematics"],
    ["Level:", "Form Four (CSEE)"],
    ["Year:", "2022"],
    ["Exam Board:", "NECTA"],
    ["Type:", "Answer Key"],
]
info_table = Table(info_data, colWidths=[140, 300])
info_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 13),
    ('TEXTCOLOR', (0, 0), (0, -1), DARK_BLUE),
    ('TEXTCOLOR', (1, 0), (1, -1), black),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('LINEBELOW', (0, 0), (-1, -2), 0.5, LIGHT_GREY),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ('LEFTPADDING', (1, 0), (1, -1), 20),
]))
story.append(info_table)

story.append(Spacer(1, 30))
story.append(Paragraph("Exam Structure", sHeading2))
struct_data = [
    ["Section", "Questions", "Marks Each", "Total Marks"],
    ["A", "Q1 - Q10", "6", "60"],
    ["B", "Q11 - Q14", "10", "40"],
    ["", "", "Grand Total:", "100"],
]
struct_table = Table(struct_data, colWidths=[80, 140, 100, 120])
struct_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -2), 0.5, LIGHT_GREY),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('FONTNAME', (2, 3), (3, 3), 'Helvetica-Bold'),
    ('BACKGROUND', (0, 1), (-1, 1), LIGHT_BLUE_BG),
    ('BACKGROUND', (0, 2), (-1, 2), white),
    ('LINEABOVE', (0, 3), (-1, 3), 1, DARK_BLUE),
]))
story.append(struct_table)
story.append(PageBreak())

# ════════════════════════════════════════
# SECTION A HEADER
# ════════════════════════════════════════
story.append(Paragraph("SECTION A", make_style('SecA', fontSize=22, leading=26, textColor=white, alignment=TA_CENTER, fontName='Helvetica-Bold', backColor=DARK_BLUE, spaceAfter=4, spaceBefore=0)))
story.append(Paragraph("Answer ALL questions. Each question carries 6 marks.", sCenterBody))
story.append(hr())

# ── Q1 ──
story.append(question_header("1(a)", "2", "Sets and Percentages"))
story.append(body("Find the percentage of multiples of 5 in the set {1, 2, 3, ..., 52}."))
story.append(sp())
story.append(step("<b>Step 1:</b> List multiples of 5 up to 52:"))
story.append(math("5, 10, 15, 20, 25, 30, 35, 40, 45, 50"))
story.append(step("Count = 10 multiples"))
story.append(sp())
story.append(step("<b>Step 2:</b> Calculate the percentage:"))
story.append(math("Percentage = (10 / 52) x 100 = 19.2%"))
story.append(sp())
story.append(answer_box("Percentage of multiples of 5 = <b>19.2%</b>"))
story.append(sp(10))

story.append(question_header("1(b)(i)", "2", "Fractions"))
story.append(body("Arrange in ascending order: 1/2, 2/9, 3/8, 1/12, 2/5."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the LCD of 2, 9, 8, 12, 5. LCD = 360."))
story.append(step("<b>Step 2:</b> Convert each fraction:"))
story.append(math("1/12 = 30/360"))
story.append(math("2/9  = 80/360"))
story.append(math("3/8  = 135/360"))
story.append(math("2/5  = 144/360"))
story.append(math("1/2  = 180/360"))
story.append(sp())
story.append(step("<b>Step 3:</b> Order from smallest to largest: 30, 80, 135, 144, 180"))
story.append(sp())
story.append(answer_box("Ascending order: <b>1/12, 2/9, 3/8, 2/5, 1/2</b>"))
story.append(tip_box("To compare fractions, always convert to a common denominator first. The LCD keeps the numbers manageable."))
story.append(sp(10))

story.append(question_header("1(b)(ii)", "2", "Standard Form"))
story.append(body("Simplify (7 x 10<super>4</super>) / 0.000035, giving your answer in standard form."))
story.append(sp())
story.append(step("<b>Step 1:</b> Write the numerator and denominator:"))
story.append(math("7 x 10<super>4</super> = 70,000"))
story.append(math("0.000035 = 3.5 x 10<super>-5</super>"))
story.append(sp())
story.append(step("<b>Step 2:</b> Divide:"))
story.append(math("70,000 / (3.5 x 10<super>-5</super>)"))
story.append(math("= (7 x 10<super>4</super>) / (3.5 x 10<super>-5</super>)"))
story.append(math("= 2 x 10<super>4-(-5)</super>"))
story.append(math("= 2 x 10<super>9</super>"))
story.append(sp())
story.append(answer_box("Answer = <b>2 x 10<super>9</super></b>"))
story.append(warn_box("When dividing powers of 10, subtract the exponents. Remember: subtracting a negative exponent means adding. 4 - (-5) = 9, not -1."))
story.append(PageBreak())

# ── Q2 ──
story.append(question_header("2(a)", "2", "Exponential Equations"))
story.append(body("Find x if 8<super>(x-1)</super> = 16."))
story.append(sp())
story.append(step("<b>Step 1:</b> Express both sides as powers of 2:"))
story.append(math("8 = 2<super>3</super>,  so  8<super>(x-1)</super> = (2<super>3</super>)<super>(x-1)</super> = 2<super>3(x-1)</super>"))
story.append(math("16 = 2<super>4</super>"))
story.append(sp())
story.append(step("<b>Step 2:</b> Since the bases are equal, equate exponents:"))
story.append(math("3(x - 1) = 4"))
story.append(math("3x - 3 = 4"))
story.append(math("3x = 7"))
story.append(math("x = 7/3"))
story.append(sp())
story.append(answer_box("x = <b>7/3</b>"))
story.append(tip_box("When solving exponential equations, the key strategy is to express both sides with the same base, then equate the exponents."))
story.append(sp(10))

story.append(question_header("2(b)(i)", "2", "Logarithms"))
story.append(body("Simplify log<sub>a</sub>(sqrt(a)) + log<sub>a</sub>(a<super>2</super>)."))
story.append(sp())
story.append(step("<b>Step 1:</b> Apply log rules: log<sub>a</sub>(a<super>n</super>) = n"))
story.append(math("log<sub>a</sub>(sqrt(a)) = log<sub>a</sub>(a<super>1/2</super>) = 1/2"))
story.append(math("log<sub>a</sub>(a<super>2</super>) = 2"))
story.append(sp())
story.append(step("<b>Step 2:</b> Add the results:"))
story.append(math("1/2 + 2 = 5/2"))
story.append(sp())
story.append(answer_box("Answer = <b>5/2</b>"))
story.append(sp(10))

story.append(question_header("2(b)(ii)", "2", "Rationalization"))
story.append(body("Rationalize (5 + sqrt(2)) / (sqrt(6) - sqrt(2))."))
story.append(sp())
story.append(step("<b>Step 1:</b> Multiply numerator and denominator by the conjugate (sqrt(6) + sqrt(2)):"))
story.append(math("= (5 + sqrt(2))(sqrt(6) + sqrt(2)) / ((sqrt(6))<super>2</super> - (sqrt(2))<super>2</super>)"))
story.append(sp())
story.append(step("<b>Step 2:</b> Simplify the denominator:"))
story.append(math("(sqrt(6))<super>2</super> - (sqrt(2))<super>2</super> = 6 - 2 = 4"))
story.append(sp())
story.append(step("<b>Step 3:</b> Expand the numerator:"))
story.append(math("(5)(sqrt(6)) + (5)(sqrt(2)) + (sqrt(2))(sqrt(6)) + (sqrt(2))(sqrt(2))"))
story.append(math("= 5*sqrt(6) + 5*sqrt(2) + sqrt(12) + 2"))
story.append(math("= 5*sqrt(6) + 5*sqrt(2) + 2*sqrt(3) + 2"))
story.append(sp())
story.append(answer_box("Answer = <b>(5*sqrt(6) + 5*sqrt(2) + 2*sqrt(3) + 2) / 4</b>"))
story.append(warn_box("To rationalize a denominator with (a - b), always multiply by (a + b)/(a + b). This uses the difference of squares identity."))
story.append(PageBreak())

# ── Q3 ──
story.append(question_header("3(a)(i)", "2", "Set Operations"))
story.append(body("P = {multiples of 5 less than 35}, Q = {odd numbers between 14 and 30}. Find P intersection Q."))
story.append(sp())
story.append(step("<b>Step 1:</b> List each set:"))
story.append(math("P = {5, 10, 15, 20, 25, 30}"))
story.append(math("Q = {15, 17, 19, 21, 23, 25, 27, 29}"))
story.append(sp())
story.append(step("<b>Step 2:</b> Find elements common to both sets:"))
story.append(sp())
story.append(answer_box("P intersection Q = <b>{15, 25}</b>"))
story.append(sp(10))

story.append(question_header("3(a)(ii)", "2", "Venn Diagrams"))
story.append(body("50 farmers: 25 grow cashew, 16 grow both cashew and maize, 10 grow neither. Find the number who grow maize only."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find total who grow at least one crop:"))
story.append(math("n(C union M) = 50 - 10 = 40"))
story.append(sp())
story.append(step("<b>Step 2:</b> Use the union formula to find n(M):"))
story.append(math("n(C union M) = n(C) + n(M) - n(C intersection M)"))
story.append(math("40 = 25 + n(M) - 16"))
story.append(math("n(M) = 40 - 25 + 16 = 31"))
story.append(sp())
story.append(step("<b>Step 3:</b> Maize only = n(M) - n(C intersection M):"))
story.append(math("= 31 - 16 = 15"))
story.append(sp())
story.append(answer_box("Number who grow maize only = <b>15</b>"))
story.append(tip_box("Draw a Venn diagram to visualize the problem. Label the intersection first, then work outward."))
story.append(sp(10))

story.append(question_header("3(b)", "2", "Probability"))
story.append(body("3 seeds are planted, each with probability 1/3 of germinating. Find P(at least 2 germinate)."))
story.append(sp())
story.append(step("<b>Step 1:</b> P(exactly 2 germinate):"))
story.append(step("Choose 2 of 3 seeds: C(3,2) = 3 ways"))
story.append(math("P(exactly 2) = 3 x (1/3)<super>2</super> x (2/3)<super>1</super> = 3 x 1/9 x 2/3 = 6/27"))
story.append(sp())
story.append(step("<b>Step 2:</b> P(exactly 3 germinate):"))
story.append(math("P(exactly 3) = (1/3)<super>3</super> = 1/27"))
story.append(sp())
story.append(step("<b>Step 3:</b> P(at least 2) = P(exactly 2) + P(exactly 3):"))
story.append(math("= 6/27 + 1/27 = 7/27"))
story.append(sp())
story.append(answer_box("P(at least 2 germinate) = <b>7/27</b>"))
story.append(PageBreak())

# ── Q4 ──
story.append(question_header("4(a)", "3", "Vectors"))
story.append(body("a = (4, 3), b = (-4, 1), c = (2, 5). Compare |a + 2b| and |3a + c|."))
story.append(sp())
story.append(step("<b>Step 1:</b> Calculate a + 2b:"))
story.append(math("a + 2b = (4, 3) + 2(-4, 1) = (4 - 8, 3 + 2) = (-4, 5)"))
story.append(math("|a + 2b| = sqrt((-4)<super>2</super> + 5<super>2</super>) = sqrt(16 + 25) = sqrt(41) approx 6.4"))
story.append(sp())
story.append(step("<b>Step 2:</b> Calculate 3a + c:"))
story.append(math("3a + c = 3(4, 3) + (2, 5) = (12 + 2, 9 + 5) = (14, 14)"))
story.append(math("|3a + c| = sqrt(14<super>2</super> + 14<super>2</super>) = sqrt(196 + 196) = sqrt(392) = 14*sqrt(2) approx 19.8"))
story.append(sp())
story.append(answer_box("|3a + c| > |a + 2b|, so the vector <b>3a + c is longer</b>."))
story.append(sp(10))

story.append(question_header("4(b)", "3", "Coordinate Geometry"))
story.append(body("Find the equation of the line through (4, 2) perpendicular to 2x + 3y + 14 = 0."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the slope of the given line:"))
story.append(math("2x + 3y + 14 = 0  =>  y = (-2/3)x - 14/3"))
story.append(math("Slope = -2/3"))
story.append(sp())
story.append(step("<b>Step 2:</b> Perpendicular slope = negative reciprocal:"))
story.append(math("m = 3/2"))
story.append(sp())
story.append(step("<b>Step 3:</b> Use point-slope form with (4, 2):"))
story.append(math("y - 2 = (3/2)(x - 4)"))
story.append(math("2(y - 2) = 3(x - 4)"))
story.append(math("2y - 4 = 3x - 12"))
story.append(math("3x - 2y - 8 = 0"))
story.append(sp())
story.append(answer_box("Equation: <b>3x - 2y - 8 = 0</b>"))
story.append(warn_box("Perpendicular slopes are negative reciprocals. If one slope is m, the perpendicular slope is -1/m, not just 1/m."))
story.append(PageBreak())

# ── Q5 ──
story.append(question_header("5(a)", "2", "Similar Triangles"))
story.append(body("A triangle has sides 4 cm, 5 cm, and 6 cm. A similar triangle has longest side 18 cm. Find the other sides."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the scale factor:"))
story.append(math("Scale factor = 18 / 6 = 3"))
story.append(sp())
story.append(step("<b>Step 2:</b> Multiply each side by the scale factor:"))
story.append(math("4 x 3 = 12 cm"))
story.append(math("5 x 3 = 15 cm"))
story.append(sp())
story.append(answer_box("The other two sides are <b>12 cm and 15 cm</b>."))
story.append(sp(10))

story.append(question_header("5(b)(i)", "2", "Regular Hexagon"))
story.append(body("A regular hexagon is inscribed in a circle. Its perimeter is 72 cm. Find the radius of the circle."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the side length:"))
story.append(math("Side = 72 / 6 = 12 cm"))
story.append(sp())
story.append(step("<b>Step 2:</b> In a regular hexagon inscribed in a circle, the side length equals the radius:"))
story.append(math("Radius = Side = 12 cm"))
story.append(sp())
story.append(answer_box("Radius = <b>12 cm</b>"))
story.append(tip_box("A regular hexagon inscribed in a circle can be divided into 6 equilateral triangles, each with side equal to the radius."))
story.append(sp(10))

story.append(question_header("5(b)(ii)", "2", "Area and Trigonometry"))
story.append(body("Triangle ABC has area 70 cm<super>2</super>, AB = 14 cm, AC = 20 cm. Find angle BAC."))
story.append(sp())
story.append(step("<b>Step 1:</b> Use the area formula:"))
story.append(math("Area = (1/2) x AB x AC x sin(BAC)"))
story.append(math("70 = (1/2)(14)(20) x sin(BAC)"))
story.append(math("70 = 140 x sin(BAC)"))
story.append(sp())
story.append(step("<b>Step 2:</b> Solve for sin(BAC):"))
story.append(math("sin(BAC) = 70 / 140 = 1/2"))
story.append(math("BAC = sin<super>-1</super>(1/2) = 30 degrees"))
story.append(sp())
story.append(answer_box("Angle BAC = <b>30 degrees</b>"))
story.append(PageBreak())

# ── Q6 ──
story.append(question_header("6(a)", "2", "Unit Conversion"))
story.append(body("Anna walks 24 km per day. Find the distance she walks in 2 days in metres."))
story.append(sp())
story.append(step("<b>Step 1:</b> Distance in 2 days:"))
story.append(math("24 x 2 = 48 km"))
story.append(sp())
story.append(step("<b>Step 2:</b> Convert to metres (1 km = 1000 m):"))
story.append(math("48 x 1000 = 48,000 m"))
story.append(sp())
story.append(answer_box("Distance = <b>48,000 metres</b>"))
story.append(sp(10))

story.append(question_header("6(b)", "4", "Direct Proportion"))
story.append(body("C is directly proportional to s. When s = 20,000, C = 18,000."))
story.append(sp())
story.append(step("<b>(i) Find the constant k:</b>"))
story.append(math("C = ks"))
story.append(math("18,000 = k x 20,000"))
story.append(math("k = 18,000 / 20,000 = 9/10"))
story.append(sp())
story.append(answer_box("k = <b>9/10</b> (or 0.9)"))
story.append(sp())
story.append(step("<b>(ii) Write the equation connecting C and s:</b>"))
story.append(sp())
story.append(answer_box("C = <b>(9/10)s</b>  or equivalently  C = 0.9s"))
story.append(PageBreak())

# ── Q7 ──
story.append(question_header("7(a)", "2", "Profit and Loss"))
story.append(body("A table costs 20,000 Tsh and is sold at a loss of 15%. Find the selling price."))
story.append(sp())
story.append(step("<b>Step 1:</b> Calculate the loss:"))
story.append(math("Loss = 15% x 20,000 = 0.15 x 20,000 = 3,000 Tsh"))
story.append(sp())
story.append(step("<b>Step 2:</b> Find the selling price:"))
story.append(math("Selling Price = Cost Price - Loss"))
story.append(math("= 20,000 - 3,000 = 17,000 Tsh"))
story.append(sp())
story.append(answer_box("Selling Price = <b>17,000 Tsh</b>"))
story.append(sp(10))

story.append(question_header("7(b)", "4", "Trial Balance"))
story.append(body("Prepare a Trial Balance from Mabala's cash account."))
story.append(sp())

tb_data = [
    ["Account", "Debit (Tsh)", "Credit (Tsh)"],
    ["Cash", "82,000", ""],
    ["Purchases", "80,000", ""],
    ["Telephone", "28,000", ""],
    ["Capital", "", "100,000"],
    ["Sales", "", "90,000"],
    ["", "", ""],
    ["Total", "190,000", "190,000"],
]
tb_table = Table(tb_data, colWidths=[160, 120, 120])
tb_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GREY),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
    ('LINEABOVE', (0, 7), (-1, 7), 1.5, DARK_BLUE),
    ('BACKGROUND', (0, 7), (-1, 7), LIGHT_BLUE_BG),
]))
story.append(tb_table)
story.append(sp())
story.append(answer_box("The Trial Balance balances at <b>190,000 Tsh</b> on both sides."))
story.append(tip_box("A Trial Balance must always have equal debit and credit totals. If they do not match, there is an error in the accounts."))
story.append(PageBreak())

# ── Q8 ──
story.append(question_header("8(a)", "3", "Arithmetic Progression"))
story.append(body("An AP has 5th term = 8 and 11th term = -34. Find the sum of the first 10 terms."))
story.append(sp())
story.append(step("<b>Step 1:</b> Set up equations using a<sub>n</sub> = a + (n-1)d:"))
story.append(math("a + 4d = 8   ... (i)"))
story.append(math("a + 10d = -34 ... (ii)"))
story.append(sp())
story.append(step("<b>Step 2:</b> Subtract (i) from (ii):"))
story.append(math("6d = -42"))
story.append(math("d = -7"))
story.append(sp())
story.append(step("<b>Step 3:</b> Find a from equation (i):"))
story.append(math("a = 8 - 4(-7) = 8 + 28 = 36"))
story.append(sp())
story.append(step("<b>Step 4:</b> Use the sum formula S<sub>n</sub> = (n/2)(2a + (n-1)d):"))
story.append(math("S<sub>10</sub> = (10/2)(2(36) + 9(-7))"))
story.append(math("= 5(72 - 63)"))
story.append(math("= 5(9) = 45"))
story.append(sp())
story.append(answer_box("S<sub>10</sub> = <b>45</b>"))
story.append(sp(10))

story.append(question_header("8(b)", "3", "Compound Interest"))
story.append(body("100,000,000 Tsh is invested at 2% compound interest per year."))
story.append(sp())
story.append(step("<b>(i) Amount after 2 years:</b>"))
story.append(math("A = P(1 + r)<super>n</super>"))
story.append(math("A = 100,000,000 x (1.02)<super>2</super>"))
story.append(math("A = 100,000,000 x 1.0404"))
story.append(math("A = 104,040,000 Tsh"))
story.append(sp())
story.append(answer_box("Amount after 2 years = <b>104,040,000 Tsh</b>"))
story.append(sp())
story.append(step("<b>(ii) Compound interest earned:</b>"))
story.append(math("Interest = A - P = 104,040,000 - 100,000,000"))
story.append(math("= 4,040,000 Tsh"))
story.append(sp())
story.append(answer_box("Compound interest = <b>4,040,000 Tsh</b>"))
story.append(warn_box("Do not confuse compound interest with simple interest. With compound interest, you earn interest on interest. With simple interest: I = 100,000,000 x 0.02 x 2 = 4,000,000 (less than compound)."))
story.append(PageBreak())

# ── Q9 ──
story.append(question_header("9(a)(i)", "2", "Trigonometric Ratios"))
story.append(body("Evaluate sin(690 degrees) / cos(690 degrees)."))
story.append(sp())
story.append(step("<b>Step 1:</b> Simplify the angle:"))
story.append(math("690 - 360 = 330 degrees"))
story.append(math("So sin(690)/cos(690) = tan(690) = tan(330)"))
story.append(sp())
story.append(step("<b>Step 2:</b> Evaluate tan(330 degrees):"))
story.append(math("330 = 360 - 30, so this is in the 4th quadrant"))
story.append(math("tan(330) = -tan(30) = -1/sqrt(3) = -sqrt(3)/3"))
story.append(sp())
story.append(answer_box("sin(690)/cos(690) = <b>-sqrt(3)/3</b>"))
story.append(tip_box("To simplify large angles, subtract 360 until you get an angle between 0 and 360. Then identify the quadrant and use the reference angle."))
story.append(sp(10))

story.append(question_header("9(a)(ii)", "2", "Trigonometry Application"))
story.append(body("A rectangular garden is 400 m by 300 m. Seedlings are planted at intervals of 1.25 m along the diagonal BD. How many seedlings?"))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the length of diagonal BD:"))
story.append(math("BD = sqrt(400<super>2</super> + 300<super>2</super>) = sqrt(160000 + 90000)"))
story.append(math("= sqrt(250000) = 500 m"))
story.append(sp())
story.append(step("<b>Step 2:</b> Find the number of seedlings:"))
story.append(math("Number of intervals = 500 / 1.25 = 400"))
story.append(math("Number of seedlings = 400 + 1 = 401"))
story.append(step("(We add 1 because seedlings are at both endpoints.)"))
story.append(sp())
story.append(answer_box("Number of seedlings = <b>401</b>"))
story.append(sp(10))

story.append(question_header("9(b)", "2", "Angle of Depression"))
story.append(body("A tower is 50 m high. The angle of depression of a car from the top is 30 degrees. Find the distance of the car from the base."))
story.append(sp())
story.append(step("<b>Step 1:</b> Draw a right triangle. The angle of depression from the top = angle of elevation from the car = 30 degrees."))
story.append(sp())
story.append(step("<b>Step 2:</b> Use trigonometry:"))
story.append(math("tan(30) = opposite / adjacent = 50 / d"))
story.append(math("d = 50 / tan(30) = 50 / (1/sqrt(3))"))
story.append(math("d = 50 x sqrt(3) = 50*sqrt(3) m"))
story.append(math("d approx 86.6 m"))
story.append(sp())
story.append(answer_box("Distance = <b>50*sqrt(3) m (approx 86.6 m)</b>"))
story.append(PageBreak())

# ── Q10 ──
story.append(question_header("10(a)", "2", "Substitution"))
story.append(body("Express 2t<super>-10</super> - 3t<super>-5</super> + 1 = 0 in terms of x, where x = 1/t<super>5</super>."))
story.append(sp())
story.append(step("<b>Step 1:</b> Note that t<super>-5</super> = 1/t<super>5</super> = x and t<super>-10</super> = (t<super>-5</super>)<super>2</super> = x<super>2</super>."))
story.append(sp())
story.append(step("<b>Step 2:</b> Substitute:"))
story.append(math("2x<super>2</super> - 3x + 1 = 0"))
story.append(sp())
story.append(answer_box("The equation becomes <b>2x<super>2</super> - 3x + 1 = 0</b>"))
story.append(sp(10))

story.append(question_header("10(b)", "4", "Quadratic Formula"))
story.append(body("Solve 2x<super>2</super> - 3x + 1 = 0 using the quadratic formula."))
story.append(sp())
story.append(step("<b>Step 1:</b> Identify a = 2, b = -3, c = 1."))
story.append(sp())
story.append(step("<b>Step 2:</b> Apply the quadratic formula:"))
story.append(math("x = (-b +/- sqrt(b<super>2</super> - 4ac)) / 2a"))
story.append(math("x = (3 +/- sqrt(9 - 8)) / 4"))
story.append(math("x = (3 +/- sqrt(1)) / 4"))
story.append(math("x = (3 +/- 1) / 4"))
story.append(sp())
story.append(step("<b>Step 3:</b> Find both solutions:"))
story.append(math("x = (3 + 1) / 4 = 4/4 = 1"))
story.append(math("x = (3 - 1) / 4 = 2/4 = 1/2"))
story.append(sp())
story.append(answer_box("x = <b>1</b>  or  x = <b>1/2</b>"))

# Section A Summary
story.append(sp(12))
story.append(colored_box([
    Paragraph("<b>Section A Summary</b>", make_style('sumtitle', fontSize=13, textColor=DARK_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6)),
    Paragraph("You have completed all 10 questions in Section A (60 marks total). Key topics covered: sets, fractions, standard form, exponents, logarithms, rationalization, Venn diagrams, probability, vectors, coordinate geometry, similarity, trigonometry, proportion, profit/loss, bookkeeping, arithmetic progressions, compound interest, and quadratic equations.", sBody),
], LIGHT_YELLOW_BG, HexColor("#f9a825"), None))
story.append(PageBreak())

# ════════════════════════════════════════
# SECTION B HEADER
# ════════════════════════════════════════
story.append(Paragraph("SECTION B", make_style('SecB', fontSize=22, leading=26, textColor=white, alignment=TA_CENTER, fontName='Helvetica-Bold', backColor=DARK_BLUE, spaceAfter=4)))
story.append(Paragraph("Answer ALL questions. Each question carries 10 marks.", sCenterBody))
story.append(hr())

# ── Q11 ──
story.append(question_header("11(a)", "3", "Arc Length and Central Angle"))
story.append(body("An arc has length 22 cm and the radius is 63 cm. Find the central angle in degrees."))
story.append(sp())
story.append(step("<b>Step 1:</b> Use the arc length formula:"))
story.append(math("l = r x theta  (theta in radians)"))
story.append(math("22 = 63 x theta"))
story.append(math("theta = 22/63 = 2/9 radians"))
story.append(sp())
story.append(step("<b>Step 2:</b> Convert radians to degrees:"))
story.append(math("theta = (2/9) x (180/pi)"))
story.append(math("Using pi = 22/7:"))
story.append(math("theta = (2/9) x (180 x 7/22)"))
story.append(math("= (2 x 180 x 7) / (9 x 22)"))
story.append(math("= 2520 / 198 = 20 degrees"))
story.append(sp())
story.append(answer_box("Central angle = <b>20 degrees</b>"))
story.append(sp(10))

story.append(question_header("11(b)", "4", "Circle Theorems"))
story.append(body("Prove that angles x and y (inscribed angles subtending arcs that together make the full circle) are supplementary."))
story.append(sp())
story.append(step("<b>Step 1:</b> Let the central angles subtended by the same arcs be a and b."))
story.append(step("By the inscribed angle theorem: angle at circumference = half the angle at center."))
story.append(math("a = 2x  and  b = 2y"))
story.append(sp())
story.append(step("<b>Step 2:</b> The two arcs together make a full circle:"))
story.append(math("a + b = 360 degrees"))
story.append(math("2x + 2y = 360 degrees"))
story.append(math("x + y = 180 degrees"))
story.append(sp())
story.append(answer_box("Since x + y = 180 degrees, angles x and y are <b>supplementary</b>. QED"))
story.append(sp(10))

story.append(question_header("11(c)", "3", "Intersecting Chords"))
story.append(body("Two chords intersect inside a circle at point E. AE = 8 cm, BE = 3 cm, CE = 4 cm. Find DE."))
story.append(sp())
story.append(step("<b>Step 1:</b> Apply the intersecting chords theorem:"))
story.append(math("AE x DE = BE x CE"))
story.append(sp())
story.append(step("<b>Step 2:</b> Substitute and solve:"))
story.append(math("8 x DE = 3 x 4"))
story.append(math("8 x DE = 12"))
story.append(math("DE = 12/8 = 1.5 cm"))
story.append(sp())
story.append(answer_box("DE = <b>1.5 cm</b>"))
story.append(tip_box("The intersecting chords theorem states: when two chords cross inside a circle, the products of their segments are equal. Remember: AE x DE = BE x CE."))
story.append(PageBreak())

# ── Q12 ──
story.append(question_header("12(a)", "5", "Earth as a Sphere"))
story.append(body("A bus travels from A(3 degrees S, 39 degrees E) to B(12 degrees S, 39 degrees E) at 40 km/h. Find the time taken. Use R = 6400 km, pi = 3.14."))
story.append(sp())
story.append(step("<b>Step 1:</b> Since both points share the same longitude (39 degrees E), the bus travels along a meridian (great circle)."))
story.append(sp())
story.append(step("<b>Step 2:</b> Find the angular difference:"))
story.append(math("Angle = 12 - 3 = 9 degrees"))
story.append(sp())
story.append(step("<b>Step 3:</b> Calculate the distance:"))
story.append(math("Distance = (theta/360) x 2 x pi x R"))
story.append(math("= (9/360) x 2 x 3.14 x 6400"))
story.append(math("= (1/40) x 40,192"))
story.append(math("= 1,004.8 km"))
story.append(sp())
story.append(step("<b>Step 4:</b> Calculate the time:"))
story.append(math("Time = Distance / Speed = 1,004.8 / 40"))
story.append(math("= 25.12 hours"))
story.append(math("= 25 hours and 7 minutes"))
story.append(sp())
story.append(answer_box("Time = <b>25 hours 7 minutes</b> (or 25.12 hours)"))
story.append(sp(10))

story.append(question_header("12(b)", "5", "Three-Dimensional Geometry"))
story.append(body("A rectangular box has base UVXY with UV = 4.2 cm, VX = 2 cm, and height XR = 2.5 cm."))
story.append(sp())
story.append(step("<b>(i) Find the length UR:</b>"))
story.append(sp())
story.append(step("First, find VR (diagonal on the face VXR):"))
story.append(math("VR = sqrt(VX<super>2</super> + XR<super>2</super>) = sqrt(4 + 6.25)"))
story.append(math("= sqrt(10.25) approx 3.2 cm"))
story.append(sp())
story.append(step("Then find UR (space diagonal from U to R):"))
story.append(math("UR = sqrt(UV<super>2</super> + VR<super>2</super>) = sqrt(17.64 + 10.25)"))
story.append(math("= sqrt(27.89) approx 5.3 cm"))
story.append(sp())
story.append(answer_box("UR approx <b>5.3 cm</b>"))
story.append(sp())

story.append(step("<b>(ii) Angle between UR and the base plane:</b>"))
story.append(sp())
story.append(step("The projection of R onto the base is point X. So the projection of UR onto the base is UX."))
story.append(math("UX = sqrt(UV<super>2</super> + VX<super>2</super>) = sqrt(17.64 + 4) = sqrt(21.64) approx 4.65 cm"))
story.append(sp())
story.append(step("The angle between UR and the base:"))
story.append(math("tan(angle) = XR / UX = 2.5 / 4.65 = 0.5376"))
story.append(math("angle = arctan(0.5376) approx 28 degrees"))
story.append(sp())
story.append(answer_box("Angle between UR and the base plane approx <b>28 degrees</b>"))
story.append(PageBreak())

# ── Q13 ──
story.append(question_header("13(a)", "4", "Matrix Equations"))
story.append(body("Find x, y, z, w given the matrix equation:"))
story.append(math("| x  4 |   | -5  -7 |   | 38   46 |"))
story.append(math("| 4  y | x |  2   z | = | -10   w |"))
story.append(sp())
story.append(step("<b>Step 1:</b> Multiply and compare entries:"))
story.append(sp())
story.append(step("Row 1, Column 1: x(-5) + 4(2) = 38"))
story.append(math("-5x + 8 = 38  =>  -5x = 30  =>  x = -6"))
story.append(sp())
story.append(step("Row 1, Column 2: x(-7) + 4(z) = 46"))
story.append(math("(-6)(-7) + 4z = 46  =>  42 + 4z = 46  =>  z = 1"))
story.append(sp())
story.append(step("Row 2, Column 1: 4(-5) + y(2) = -10"))
story.append(math("-20 + 2y = -10  =>  2y = 10  =>  y = 5"))
story.append(sp())
story.append(step("Row 2, Column 2: 4(-7) + y(z) = w"))
story.append(math("-28 + 5(1) = w  =>  w = -23"))
story.append(sp())
story.append(answer_box("x = <b>-6</b>,  y = <b>5</b>,  z = <b>1</b>,  w = <b>-23</b>"))
story.append(sp(10))

story.append(question_header("13(b)", "3", "Transformations - Reflections"))
story.append(body("Reflect the point (3, -2) in the line y = -x, then reflect the result in the line x = 0."))
story.append(sp())
story.append(step("<b>Step 1:</b> Reflect (3, -2) in the line y = -x."))
story.append(step("Rule: (x, y) maps to (-y, -x)."))
story.append(math("(3, -2) maps to (2, -3)"))
story.append(sp())
story.append(step("<b>Step 2:</b> Reflect (2, -3) in the line x = 0 (the y-axis)."))
story.append(step("Rule: (x, y) maps to (-x, y)."))
story.append(math("(2, -3) maps to (-2, -3)"))
story.append(sp())
story.append(answer_box("Final image = <b>(-2, -3)</b>"))
story.append(sp(10))

story.append(question_header("13(c)", "3", "Translation"))
story.append(body("A translation maps (5, 5) to (-7, -7). Find the point mapped to (-4, -4)."))
story.append(sp())
story.append(step("<b>Step 1:</b> Find the translation vector:"))
story.append(math("T = (-7 - 5, -7 - 5) = (-12, -12)"))
story.append(sp())
story.append(step("<b>Step 2:</b> If (x, y) maps to (-4, -4):"))
story.append(math("x + (-12) = -4  =>  x = 8"))
story.append(math("y + (-12) = -4  =>  y = 8"))
story.append(sp())
story.append(answer_box("The original point is <b>(8, 8)</b>"))
story.append(warn_box("When finding the original point from the image, reverse the translation: add the vector components instead of subtracting."))
story.append(PageBreak())

# ── Q14 ──
story.append(question_header("14(a)", "5", "Functions"))
story.append(body("Given f(x) = 1/(x - 2):"))
story.append(sp())
story.append(step("<b>(i) Domain and Range:</b>"))
story.append(sp())
story.append(step("Domain: f(x) is undefined when x - 2 = 0, i.e., when x = 2."))
story.append(math("Domain = {all real numbers except x = 2}"))
story.append(sp())
story.append(step("Range: f(x) = 1/(x-2) can take any value except 0 (the numerator is always 1, never 0)."))
story.append(math("Range = {all real numbers except 0}"))
story.append(sp())
story.append(answer_box("Domain: <b>all real numbers, x != 2</b><br/>Range: <b>all real numbers, y != 0</b>"))
story.append(sp())
story.append(step("<b>(ii) Find f<super>-1</super>(1/3):</b>"))
story.append(sp())
story.append(step("First, find the inverse function. Let y = 1/(x - 2):"))
story.append(math("y(x - 2) = 1"))
story.append(math("x - 2 = 1/y"))
story.append(math("x = 1/y + 2"))
story.append(math("So f<super>-1</super>(y) = 1/y + 2"))
story.append(sp())
story.append(step("Now evaluate f<super>-1</super>(1/3):"))
story.append(math("f<super>-1</super>(1/3) = 1/(1/3) + 2 = 3 + 2 = 5"))
story.append(sp())
story.append(answer_box("f<super>-1</super>(1/3) = <b>5</b>"))
story.append(sp(10))

story.append(question_header("14(b)", "5", "Linear Programming"))
story.append(body("Black shirts cost 24,000 Tsh each, white shirts cost 30,000 Tsh each. Budget is 180,000 Tsh. At most 5 black shirts. Maximize total number of shirts."))
story.append(sp())
story.append(step("<b>Step 1:</b> Define variables and constraints:"))
story.append(math("Let x = number of black shirts, y = number of white shirts"))
story.append(math("Constraints:"))
story.append(math("  24,000x + 30,000y &lt;= 180,000  =>  4x + 5y &lt;= 30"))
story.append(math("  x &lt;= 5"))
story.append(math("  x &gt;= 0,  y &gt;= 0"))
story.append(sp())
story.append(step("<b>Step 2:</b> Objective: Maximize x + y."))
story.append(sp())
story.append(step("<b>Step 3:</b> Find the corner points of the feasible region:"))
story.append(math("(0, 0): x + y = 0"))
story.append(math("(5, 0): x + y = 5"))
story.append(math("(5, 2): x + y = 7   [check: 4(5)+5(2) = 30, OK]"))
story.append(math("(0, 6): x + y = 6   [check: 4(0)+5(6) = 30, OK]"))
story.append(sp())
story.append(step("<b>Step 4:</b> The maximum value of x + y is <b>7</b>, at (5, 2)."))
story.append(sp())
story.append(answer_box("Greatest number of shirts = <b>7</b> (5 black + 2 white)"))
story.append(tip_box("In linear programming, the maximum or minimum always occurs at a corner point of the feasible region. Test all corner points and compare."))

# Section B Summary
story.append(sp(12))
story.append(colored_box([
    Paragraph("<b>Section B Summary</b>", make_style('sumbtitle', fontSize=13, textColor=DARK_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6)),
    Paragraph("You have completed all 4 questions in Section B (40 marks total). Key topics covered: circles and arcs, circle theorems, intersecting chords, earth geometry, 3D geometry, matrices, reflections, translations, functions and inverses, and linear programming.", sBody),
], LIGHT_YELLOW_BG, HexColor("#f9a825"), None))
story.append(PageBreak())

# ════════════════════════════════════════
# LAST PAGE
# ════════════════════════════════════════
story.append(Spacer(1, 100))
story.append(Paragraph("Thank you for using this Answer Key!", make_style('thanks', fontSize=20, leading=26, textColor=DARK_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(Spacer(1, 20))
story.append(Paragraph("We hope the step-by-step solutions and study tips helped you understand each topic better. Keep practising past papers to build your confidence for the exam.", sCenterBody))
story.append(Spacer(1, 30))

# Resource box
story.append(colored_box([
    Paragraph("<b>Visit mytzstudies.com for more free resources</b>", make_style('res1', fontSize=16, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=10)),
    Paragraph("Past papers and answer keys for all subjects", make_style('res2', fontSize=12, alignment=TA_CENTER, spaceAfter=4)),
    Paragraph("Form 1 to Form 6 (CSEE and ACSEE)", make_style('res3', fontSize=12, alignment=TA_CENTER, spaceAfter=4)),
    Paragraph("Always free. Always student-friendly.", make_style('res4', fontSize=12, alignment=TA_CENTER, textColor=MEDIUM_GREY)),
], LIGHT_GREEN_BG, GREEN, None))

story.append(Spacer(1, 40))
story.append(Paragraph("mytzstudies.com", make_style('lasturl', fontSize=22, leading=28, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(Spacer(1, 10))
story.append(Paragraph("Free Tanzanian Exam Resources", make_style('lastsub', fontSize=12, textColor=MEDIUM_GREY, alignment=TA_CENTER)))

# ════════════════════════════════════════
# BUILD
# ════════════════════════════════════════
doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    topMargin=40,
    bottomMargin=45,
    leftMargin=45,
    rightMargin=45,
    title="Basic Mathematics Form 4 (CSEE) 2022 - Answer Key",
    author="myTZStudies",
)

doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
print(f"PDF generated successfully: {OUTPUT_PATH}")
