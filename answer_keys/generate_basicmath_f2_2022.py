"""
Generate BasicMath Form 2 2022 NECTA Answer Key PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors
import os

# Colors
DARK_BLUE = HexColor("#1a237e")
GREEN = HexColor("#2e7d32")
LIGHT_BLUE_BG = HexColor("#e8eaf6")
LIGHT_GREEN_BG = HexColor("#e8f5e9")
WARNING_BG = HexColor("#fff3e0")
WARNING_BORDER = HexColor("#ff9800")
TIP_BG = HexColor("#e3f2fd")
TIP_BORDER = HexColor("#1976d2")
ANSWER_BG = HexColor("#f1f8e9")
LIGHT_GRAY = HexColor("#f5f5f5")
BORDER_GRAY = HexColor("#e0e0e0")
SECTION_BG = HexColor("#ede7f6")

WIDTH, HEIGHT = A4
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "BasicMath-F2-2022 (Answer Key).pdf")

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=42, textColor=DARK_BLUE,
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'CoverTagline', parent=styles['Normal'],
        fontName='Helvetica', fontSize=16, textColor=GREEN,
        alignment=TA_CENTER, spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        'FeatureBox', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'CoverURL', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, textColor=GREEN,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'TitlePageHeading', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=28, textColor=DARK_BLUE,
        alignment=TA_CENTER, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'TitlePageSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=16, textColor=HexColor("#333333"),
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'QuestionHeading', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=16, textColor=white,
        alignment=TA_LEFT, spaceAfter=6, spaceBefore=12
    ))
    styles.add(ParagraphStyle(
        'SubPart', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, textColor=DARK_BLUE,
        spaceBefore=10, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        'BodyText2', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, textColor=HexColor("#222222"),
        leading=16, spaceAfter=4, alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        'StepText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, textColor=HexColor("#333333"),
        leading=16, spaceAfter=2, leftIndent=15
    ))
    styles.add(ParagraphStyle(
        'AnswerText', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, textColor=HexColor("#1b5e20"),
        leading=16, spaceAfter=6, leftIndent=15
    ))
    styles.add(ParagraphStyle(
        'WarningTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, textColor=HexColor("#e65100"),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        'WarningText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=HexColor("#bf360c"),
        leading=14
    ))
    styles.add(ParagraphStyle(
        'TipTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, textColor=HexColor("#0d47a1"),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        'TipText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=HexColor("#1565c0"),
        leading=14
    ))
    styles.add(ParagraphStyle(
        'SectionSummary', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=11, textColor=HexColor("#4a148c"),
        leading=15, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, textColor=HexColor("#666666"),
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'ClosingTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=30, textColor=DARK_BLUE,
        alignment=TA_CENTER, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'ClosingText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14, textColor=HexColor("#333333"),
        alignment=TA_CENTER, leading=20, spaceAfter=8
    ))
    return styles


def footer_func(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawCentredString(WIDTH / 2, 15 * mm, "mytzstudies.com | Free Tanzanian Exam Resources")
    canvas.restoreState()


def make_question_header(num, title, styles):
    """Create a colored banner for each question."""
    header_data = [[Paragraph(f"Question {num}: {title}", styles['QuestionHeading'])]]
    header_table = Table(header_data, colWidths=[WIDTH - 80])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    return header_table


def make_warning_box(text):
    """Common Mistake Warning box."""
    content = [[
        Paragraph("<b>&#9888; Common Mistake Warning</b>", ParagraphStyle(
            'WarnHead', fontName='Helvetica-Bold', fontSize=11,
            textColor=HexColor("#e65100"), spaceAfter=3
        )),
    ], [
        Paragraph(text, ParagraphStyle(
            'WarnBody', fontName='Helvetica', fontSize=10,
            textColor=HexColor("#bf360c"), leading=14
        ))
    ]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), WARNING_BG),
        ('BOX', (0, 0), (-1, -1), 1.5, WARNING_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def make_tip_box(text):
    """Study Tip box."""
    content = [[
        Paragraph("<b>&#128161; Study Tip</b>", ParagraphStyle(
            'TipHead', fontName='Helvetica-Bold', fontSize=11,
            textColor=HexColor("#0d47a1"), spaceAfter=3
        )),
    ], [
        Paragraph(text, ParagraphStyle(
            'TipBody', fontName='Helvetica', fontSize=10,
            textColor=HexColor("#1565c0"), leading=14
        ))
    ]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TIP_BG),
        ('BOX', (0, 0), (-1, -1), 1.5, TIP_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def make_answer_box(text):
    """Highlighted answer box."""
    content = [[
        Paragraph(text, ParagraphStyle(
            'AnsInner', fontName='Helvetica-Bold', fontSize=12,
            textColor=HexColor("#1b5e20"), leading=16
        ))
    ]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ANSWER_BG),
        ('BOX', (0, 0), (-1, -1), 1, GREEN),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def make_section_summary(text):
    """Section summary box."""
    content = [[
        Paragraph(f"<b>Section Summary:</b> {text}", ParagraphStyle(
            'SumInner', fontName='Helvetica', fontSize=11,
            textColor=HexColor("#4a148c"), leading=15
        ))
    ]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('BOX', (0, 0), (-1, -1), 1, HexColor("#7e57c2")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def build_pdf():
    styles = build_styles()

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    story = []
    S = lambda pts: Spacer(1, pts)
    body = styles['BodyText2']
    step = styles['StepText']
    sub = styles['SubPart']

    # ========== COVER PAGE ==========
    story.append(S(60))
    story.append(Paragraph("myTZStudies", styles['CoverTitle']))
    story.append(S(4))
    story.append(Paragraph("Your Free Exam Prep Resource", styles['CoverTagline']))
    story.append(S(30))

    # Feature boxes - 2 rows of 3
    features = ["Free Past Papers", "Answer Keys", "Study Guides",
                 "Practice Tests", "Topic Summaries", "Exam Tips"]

    feat_style = ParagraphStyle('FeatInner', fontName='Helvetica-Bold', fontSize=11,
                                 textColor=DARK_BLUE, alignment=TA_CENTER)

    def feat_cell(text):
        return Paragraph(text, feat_style)

    row1 = [feat_cell(f) for f in features[:3]]
    row2 = [feat_cell(f) for f in features[3:]]

    col_w = (WIDTH - 80) / 3
    feat_table = Table([row1, row2], colWidths=[col_w]*3, rowHeights=[45, 45])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG),
        ('BOX', (0, 0), (0, 0), 1, BORDER_GRAY),
        ('BOX', (1, 0), (1, 0), 1, BORDER_GRAY),
        ('BOX', (2, 0), (2, 0), 1, BORDER_GRAY),
        ('BOX', (0, 1), (0, 1), 1, BORDER_GRAY),
        ('BOX', (1, 1), (1, 1), 1, BORDER_GRAY),
        ('BOX', (2, 1), (2, 1), 1, BORDER_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(feat_table)
    story.append(S(50))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(PageBreak())

    # ========== TITLE PAGE ==========
    story.append(S(80))
    story.append(Paragraph("ANSWER KEY", styles['TitlePageHeading']))
    story.append(S(20))

    info_data = [
        ["Subject:", "Basic Mathematics"],
        ["Level:", "Form Two"],
        ["Year:", "2022"],
        ["Exam Board:", "NECTA"],
        ["Type:", "Answer Key"],
    ]
    info_style_l = ParagraphStyle('InfoL', fontName='Helvetica-Bold', fontSize=14,
                                   textColor=DARK_BLUE, alignment=TA_LEFT)
    info_style_r = ParagraphStyle('InfoR', fontName='Helvetica', fontSize=14,
                                   textColor=HexColor("#333333"), alignment=TA_LEFT)

    info_rows = [[Paragraph(r[0], info_style_l), Paragraph(r[1], info_style_r)] for r in info_data]
    info_table = Table(info_rows, colWidths=[120, 250])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG),
        ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(S(30))
    story.append(Paragraph(
        "This answer key provides detailed, step-by-step solutions to help you "
        "understand how to solve each problem. Use it to check your work and learn from any mistakes.",
        ParagraphStyle('Intro', fontName='Helvetica', fontSize=12,
                       textColor=HexColor("#555555"), alignment=TA_CENTER, leading=18)
    ))
    story.append(PageBreak())

    # ========== QUESTION 1 ==========
    story.append(make_question_header(1, "Banking & Repeating Decimals", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Mwajuma's Bank Account</b>", sub))
    story.append(Paragraph(
        "Mwajuma deposited <b>Tsh. 360,000</b> in a bank. The bank charges <b>Tsh. 1,000</b> for each withdrawal.",
        body))
    story.append(S(4))

    story.append(Paragraph("<b>(i) After withdrawing Tsh. 106,000:</b>", sub))
    story.append(Paragraph("Step 1: Calculate the total amount deducted (withdrawal + bank charge):", step))
    story.append(Paragraph("Total deducted = 106,000 + 1,000 = <b>107,000</b>", step))
    story.append(Paragraph("Step 2: Subtract from the balance:", step))
    story.append(Paragraph("Remaining = 360,000 - 107,000", step))
    story.append(make_answer_box("Remaining balance = Tsh. 253,000"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) After a further withdrawal of Tsh. 50,000:</b>", sub))
    story.append(Paragraph("Step 1: Total deducted = 50,000 + 1,000 = <b>51,000</b>", step))
    story.append(Paragraph("Step 2: Remaining = 253,000 - 51,000", step))
    story.append(make_answer_box("Remaining balance = Tsh. 202,000"))
    story.append(S(6))

    story.append(make_warning_box(
        "Don't forget to add the bank charge of Tsh. 1,000 to EACH withdrawal! "
        "Many students lose marks by only subtracting the withdrawal amount."
    ))
    story.append(S(10))

    story.append(Paragraph("<b>(b) Convert 2.434343... (repeating) to a mixed fraction</b>", sub))
    story.append(Paragraph("Step 1: Let x = 2.434343...", step))
    story.append(Paragraph("Step 2: Multiply both sides by 100 (because 2 digits repeat):", step))
    story.append(Paragraph("100x = 243.434343...", step))
    story.append(Paragraph("Step 3: Subtract the original equation:", step))
    story.append(Paragraph("100x - x = 243.4343... - 2.4343...", step))
    story.append(Paragraph("99x = 241", step))
    story.append(Paragraph("Step 4: Solve for x:", step))
    story.append(Paragraph("x = 241/99", step))
    story.append(Paragraph("Step 5: Convert to mixed fraction: 241 &divide; 99 = 2 remainder 43", step))
    story.append(make_answer_box("2.434343... = 2  43/99"))
    story.append(S(6))

    story.append(make_tip_box(
        "To convert a repeating decimal to a fraction: multiply by 10^n where n = number of repeating digits, "
        "then subtract the original to cancel out the repeating part."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "This question tests basic arithmetic with real-life banking, and converting repeating decimals to fractions."
    ))

    # ========== QUESTION 2 ==========
    story.append(S(10))
    story.append(make_question_header(2, "Decimals, Rounding & Unit Conversion", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Total mass to the nearest whole number</b>", sub))
    story.append(Paragraph("Dog = 30.7 kg, Cat = 13.44 kg, Goat = 18.26 kg", body))
    story.append(Paragraph("Step 1: Add all masses: 30.7 + 13.44 + 18.26 = <b>62.40 kg</b>", step))
    story.append(Paragraph("Step 2: Round to nearest whole number:", step))
    story.append(make_answer_box("Total mass &asymp; 62 kg"))
    story.append(S(4))

    story.append(Paragraph("<b>(a)(ii) Rounding each animal's mass</b>", sub))
    story.append(Paragraph("Dog (nearest ones): 30.7 &rarr; look at the digit after ones (7 &ge; 5, round up)", step))
    story.append(make_answer_box("Dog = 31 kg"))
    story.append(Paragraph("Cat (1 decimal place): 13.44 &rarr; look at 2nd decimal (4 &lt; 5, round down)", step))
    story.append(make_answer_box("Cat = 13.4 kg"))
    story.append(Paragraph("Goat (3 significant figures): 18.26 &rarr; first 3 sig figs are 1, 8, 2; "
                            "next digit is 6 &ge; 5, so round up", step))
    story.append(make_answer_box("Goat = 18.3 kg"))
    story.append(S(6))

    story.append(make_warning_box(
        "Significant figures vs decimal places: '3 significant figures' counts ALL digits starting from the first "
        "non-zero digit. '1 decimal place' counts digits after the decimal point."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(i) Add: 8 km 799 m 400 mm + 5 km 300 m 609 mm</b>", sub))
    story.append(Paragraph("Step 1: Add millimetres: 400 + 609 = 1009 mm = 1 m and 9 mm", step))
    story.append(Paragraph("Step 2: Add metres (with carry): 799 + 300 + 1 = 1100 m = 1 km and 100 m", step))
    story.append(Paragraph("Step 3: Add kilometres (with carry): 8 + 5 + 1 = 14 km", step))
    story.append(make_answer_box("Total = 14 km 100 m 9 mm"))
    story.append(S(4))

    story.append(Paragraph("<b>(b)(ii) Convert to metres</b>", sub))
    story.append(Paragraph("14 km = 14,000 m; 100 m = 100 m; 9 mm = 0.009 m", step))
    story.append(make_answer_box("Total = 14,100.009 m"))
    story.append(S(6))
    story.append(make_section_summary(
        "This question covers decimal operations, rounding rules, and metric unit conversions. "
        "Always carry over when smaller units exceed their limit (1000 mm = 1 m, 1000 m = 1 km)."
    ))

    # ========== QUESTION 3 ==========
    story.append(S(10))
    story.append(make_question_header(3, "Circles & Area", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Parts of a Circle</b>", sub))
    story.append(Paragraph("Draw a circle with center O and label the following:", body))
    story.append(S(4))

    parts = [
        ["<b>Term</b>", "<b>Definition</b>"],
        ["Radius AO", "A straight line from the center O to any point A on the circle"],
        ["Arc AB", "The curved part of the circle between points A and B"],
        ["Chord CD", "A straight line joining two points C and D on the circle (does not pass through center)"],
        ["Sector AOB", 'A "pizza slice" shape enclosed by two radii OA and OB and the arc AB between them'],
    ]
    parts_rows = [[Paragraph(c, ParagraphStyle('TC', fontName='Helvetica', fontSize=10,
                                                textColor=HexColor("#222222"), leading=13)) for c in r] for r in parts]
    parts_table = Table(parts_rows, colWidths=[120, WIDTH - 200])
    parts_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BLUE_BG),
        ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(parts_table)
    story.append(S(8))

    story.append(Paragraph("<b>(b) Square carpet of side 14 m with largest circular carpet inside</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>(i) Area of circular carpet:</b>", sub))
    story.append(Paragraph("The largest circle that fits inside a square has diameter = side of square", step))
    story.append(Paragraph("Diameter = 14 m, so radius = 14/2 = <b>7 m</b>", step))
    story.append(Paragraph("Area = &pi;r&sup2; = (22/7) &times; 7&sup2; = (22/7) &times; 49", step))
    story.append(make_answer_box("Area of circular carpet = 154 m&sup2;"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Remaining area (area not covered by circle):</b>", sub))
    story.append(Paragraph("Square area = 14 &times; 14 = 196 m&sup2;", step))
    story.append(Paragraph("Remaining = 196 - 154", step))
    story.append(make_answer_box("Remaining area = 42 m&sup2;"))
    story.append(S(6))
    story.append(make_tip_box(
        "When the question says 'use &pi; = 22/7', it usually means the numbers will cancel nicely. "
        "If the radius is a multiple of 7, the fraction simplifies perfectly!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Know the key parts of a circle (radius, diameter, chord, arc, sector, segment). "
        "For area problems, identify what shape fits inside what and subtract."
    ))

    # ========== QUESTION 4 ==========
    story.append(S(10))
    story.append(make_question_header(4, "Simultaneous Equations & Quadratics", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Solve by elimination: a/2 - b/5 = 1 and 3b = 24 + a</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Step 1: Clear fractions in equation 1 by multiplying by 10:", step))
    story.append(Paragraph("10(a/2) - 10(b/5) = 10(1) &rarr; 5a - 2b = 10  ... (i)", step))
    story.append(Paragraph("Step 2: Rearrange equation 2:", step))
    story.append(Paragraph("3b = 24 + a &rarr; a = 3b - 24  ... (ii)", step))
    story.append(Paragraph("Step 3: Substitute (ii) into (i):", step))
    story.append(Paragraph("5(3b - 24) - 2b = 10", step))
    story.append(Paragraph("15b - 120 - 2b = 10", step))
    story.append(Paragraph("13b = 130", step))
    story.append(Paragraph("b = 10", step))
    story.append(Paragraph("Step 4: Find a: a = 3(10) - 24 = 30 - 24 = 6", step))
    story.append(make_answer_box("a = 6, b = 10"))
    story.append(S(6))

    story.append(make_warning_box(
        "When clearing fractions, multiply EVERY term on BOTH sides. A common mistake is forgetting to "
        "multiply the right side or missing a term."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Rectangle: length exceeds width by 5 cm. Area = 50 cm&sup2;. Find dimensions.</b>", sub))
    story.append(Paragraph("Step 1: Let width = w, then length = w + 5", step))
    story.append(Paragraph("Step 2: Area = length &times; width:", step))
    story.append(Paragraph("w(w + 5) = 50", step))
    story.append(Paragraph("w&sup2; + 5w - 50 = 0", step))
    story.append(Paragraph("Step 3: Factorise:", step))
    story.append(Paragraph("(w + 10)(w - 5) = 0", step))
    story.append(Paragraph("w = -10 or w = 5", step))
    story.append(Paragraph("Step 4: Reject w = -10 (width cannot be negative)", step))
    story.append(make_answer_box("Width = 5 cm, Length = 10 cm"))
    story.append(S(6))
    story.append(make_tip_box(
        "Always reject negative answers when dealing with physical measurements like length, width, or time. "
        "State why you reject it to earn full marks."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Simultaneous equations can be solved by substitution or elimination. Quadratic word problems: "
        "set up the equation, factorise, solve, and reject impossible answers."
    ))

    # ========== QUESTION 5 ==========
    story.append(S(10))
    story.append(make_question_header(5, "Ratio & Simple Interest", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Asha and Juma share Tsh. 630,000. Asha gets twice Juma's share.</b>", sub))
    story.append(Paragraph("Step 1: Let Juma's share = x, then Asha's share = 2x", step))
    story.append(Paragraph("Step 2: Total = x + 2x = 3x", step))
    story.append(Paragraph("3x = 630,000", step))
    story.append(Paragraph("x = 210,000", step))
    story.append(Paragraph("Step 3: Asha's share = 2 &times; 210,000", step))
    story.append(make_answer_box("Asha received Tsh. 420,000"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Simple Interest: rate = 3% per year, after 4 years interest = Tsh. 900,000</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>(i) Find the initial deposit (Principal):</b>", sub))
    story.append(Paragraph("Formula: I = PRT/100", step))
    story.append(Paragraph("900,000 = P &times; 3 &times; 4 / 100", step))
    story.append(Paragraph("900,000 = 12P / 100", step))
    story.append(Paragraph("P = 900,000 &times; 100 / 12", step))
    story.append(make_answer_box("Initial deposit (P) = Tsh. 7,500,000"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Total amount after 4 years:</b>", sub))
    story.append(Paragraph("Amount = Principal + Interest", step))
    story.append(Paragraph("Amount = 7,500,000 + 900,000", step))
    story.append(make_answer_box("Total amount = Tsh. 8,400,000"))
    story.append(S(6))

    story.append(make_warning_box(
        "In the simple interest formula I = PRT/100, make sure you identify which value you're solving for. "
        "Don't confuse Interest (I) with the total Amount (A = P + I)."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Ratio problems: express shares in terms of one variable. Simple interest: "
        "memorise I = PRT/100 and A = P + I."
    ))

    # ========== QUESTION 6 ==========
    story.append(S(10))
    story.append(make_question_header(6, "Linear Equations & Scale Drawing", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Line y = 3x - p passes through (6, 10) and (q, 22). Find p and q.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Step 1: Substitute point (6, 10) into y = 3x - p:", step))
    story.append(Paragraph("10 = 3(6) - p", step))
    story.append(Paragraph("10 = 18 - p", step))
    story.append(Paragraph("p = 18 - 10", step))
    story.append(make_answer_box("p = 8"))
    story.append(S(4))
    story.append(Paragraph("Step 2: Now the equation is y = 3x - 8. Substitute point (q, 22):", step))
    story.append(Paragraph("22 = 3q - 8", step))
    story.append(Paragraph("3q = 30", step))
    story.append(make_answer_box("q = 10"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Room is 500 cm by 200 cm. Scale = 1:100</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>(i) Drawing dimensions:</b>", sub))
    story.append(Paragraph("Scale 1:100 means 1 cm on drawing = 100 cm in real life", step))
    story.append(Paragraph("Length on drawing = 500 / 100 = 5 cm", step))
    story.append(Paragraph("Width on drawing = 200 / 100 = 2 cm", step))
    story.append(make_answer_box("Drawing dimensions = 5 cm by 2 cm"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Actual area of the room:</b>", sub))
    story.append(Paragraph("Area = 500 &times; 200 = 100,000 cm&sup2;", step))
    story.append(Paragraph("Convert: 100,000 cm&sup2; &divide; 10,000 = 10 m&sup2;", step))
    story.append(make_answer_box("Area of room = 10 m&sup2;"))
    story.append(S(6))
    story.append(make_tip_box(
        "Scale 1:n means divide real measurements by n to get drawing measurements. "
        "For area, the scale factor is squared: 1:n means area scale is 1:n&sup2;."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "To find unknowns in a line equation, substitute known points. "
        "For scale drawings, divide real dimensions by the scale factor."
    ))

    # ========== QUESTION 7 ==========
    story.append(S(10))
    story.append(make_question_header(7, "Surds & Subject of Formula", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) P = &radic;2 - 3,  Q = &radic;2 + 1</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>(i) Show that PQ = -1 - 2&radic;2</b>", sub))
    story.append(Paragraph("PQ = (&radic;2 - 3)(&radic;2 + 1)", step))
    story.append(Paragraph("Use FOIL method (First, Outer, Inner, Last):", step))
    story.append(Paragraph("= (&radic;2)(&radic;2) + (&radic;2)(1) + (-3)(&radic;2) + (-3)(1)", step))
    story.append(Paragraph("= 2 + &radic;2 - 3&radic;2 - 3", step))
    story.append(Paragraph("= (2 - 3) + (&radic;2 - 3&radic;2)", step))
    story.append(make_answer_box("PQ = -1 - 2&radic;2  (shown)"))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) Show that P/Q = 5 - 4&radic;2</b>", sub))
    story.append(Paragraph("P/Q = (&radic;2 - 3) / (&radic;2 + 1)", step))
    story.append(Paragraph("Step 1: Rationalise by multiplying top and bottom by the conjugate (&radic;2 - 1):", step))
    story.append(Paragraph("= (&radic;2 - 3)(&radic;2 - 1) / (&radic;2 + 1)(&radic;2 - 1)", step))
    story.append(Paragraph("Step 2: Expand the denominator: (&radic;2)&sup2; - 1&sup2; = 2 - 1 = <b>1</b>", step))
    story.append(Paragraph("Step 3: Expand the numerator:", step))
    story.append(Paragraph("= (&radic;2)(&radic;2) - (&radic;2)(1) - (3)(&radic;2) + (3)(1)", step))
    story.append(Paragraph("= 2 - &radic;2 - 3&radic;2 + 3", step))
    story.append(Paragraph("= 5 - 4&radic;2", step))
    story.append(make_answer_box("P/Q = (5 - 4&radic;2) / 1 = 5 - 4&radic;2  (shown)"))
    story.append(S(6))

    story.append(make_warning_box(
        "To rationalise a denominator with &radic;a + b, multiply top and bottom by &radic;a - b (the conjugate). "
        "This uses the difference of squares: (x+y)(x-y) = x&sup2; - y&sup2;."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Make x the subject: p = &radic;(q + x). Find x when p = 3, q = -1.</b>", sub))
    story.append(Paragraph("Step 1: Square both sides: p&sup2; = q + x", step))
    story.append(Paragraph("Step 2: Solve for x: x = p&sup2; - q", step))
    story.append(Paragraph("Step 3: Substitute p = 3, q = -1:", step))
    story.append(Paragraph("x = (3)&sup2; - (-1) = 9 + 1", step))
    story.append(make_answer_box("x = p&sup2; - q;  when p = 3, q = -1: x = 10"))
    story.append(S(6))
    story.append(make_section_summary(
        "Surds: use FOIL to multiply, and rationalise denominators using the conjugate. "
        "For change of subject: isolate the variable step by step, undoing operations in reverse order."
    ))

    # ========== QUESTION 8 ==========
    story.append(S(10))
    story.append(make_question_header(8, "Similar Triangles & Congruence", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Building side view: EN = 6 cm, NG = 18 cm, height = 12 cm</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>(i) Show that the two triangles are similar:</b>", sub))
    story.append(Paragraph("The figure shows triangle FME (small) and triangle FNG (large) sharing vertex F.", step))
    story.append(Paragraph("Angle F is common to both triangles (shared angle).", step))
    story.append(Paragraph("Angle FME = Angle FNG = 90&deg; (both are right angles, shown by the square mark).", step))
    story.append(Paragraph("By AA Similarity (two pairs of equal angles), the triangles are similar.", step))
    story.append(make_answer_box("Triangle FME is similar to Triangle FNG (by AA Similarity)"))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) Determine FE:</b>", sub))
    story.append(Paragraph("Since FME ~ FNG, and angle M = 90&deg;:", step))
    story.append(Paragraph("In right triangle FME: FM = 12 cm (height), ME = 6 cm", step))
    story.append(Paragraph("Using Pythagoras' theorem: FE&sup2; = FM&sup2; + ME&sup2;", step))
    story.append(Paragraph("FE&sup2; = 12&sup2; + 6&sup2; = 144 + 36 = 180", step))
    story.append(Paragraph("FE = &radic;180 = &radic;(36 &times; 5) = 6&radic;5", step))
    story.append(make_answer_box("FE = 6&radic;5 &asymp; 13.4 cm"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Congruent triangles ABC and PQR</b>", sub))
    story.append(Paragraph("Given: Angle C = 48&deg;, Angle R = 72&deg;, with equal sides marked.", body))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Conditions for congruence:</b>", sub))
    story.append(Paragraph("From the figure, equal sides are marked with tick marks (showing corresponding sides are equal).", step))
    story.append(Paragraph("Angle C in triangle ABC = Angle P in triangle PQR = 48&deg;.", step))
    story.append(Paragraph("With two pairs of equal sides and the included angle equal, the triangles are "
                            "congruent by the <b>SAS (Side-Angle-Side)</b> condition.", step))
    story.append(make_answer_box("Triangles ABC and PQR are congruent by SAS"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Find angle RQP:</b>", sub))
    story.append(Paragraph("Sum of angles in a triangle = 180&deg;", step))
    story.append(Paragraph("Angle RQP = 180&deg; - 48&deg; - 72&deg;", step))
    story.append(make_answer_box("Angle RQP = 60&deg;"))
    story.append(S(6))
    story.append(make_section_summary(
        "Similar triangles have equal angles but different sizes (AA, SAS, SSS similarity tests). "
        "Congruent triangles are identical in shape AND size (SSS, SAS, ASA, RHS tests)."
    ))

    # ========== QUESTION 9 ==========
    story.append(S(10))
    story.append(make_question_header(9, "Pythagoras' Theorem", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Photo diagonal = 7.8 cm. Frame = 6 cm &times; 5 cm. Will it fit?</b>", sub))
    story.append(Paragraph("Step 1: Find the diagonal of the frame using Pythagoras:", step))
    story.append(Paragraph("Frame diagonal = &radic;(6&sup2; + 5&sup2;) = &radic;(36 + 25) = &radic;61", step))
    story.append(Paragraph("&radic;61 &asymp; 7.81 cm", step))
    story.append(Paragraph("Step 2: Compare: frame diagonal (7.81 cm) &gt; photo diagonal (7.8 cm)", step))
    story.append(make_answer_box("Yes, the photograph WILL fit in the frame (7.81 &gt; 7.8)"))
    story.append(S(6))

    story.append(make_warning_box(
        "The photo fits because its diagonal (7.8 cm) is LESS than the frame's diagonal (7.81 cm). "
        "If they were equal or the photo was bigger, it would NOT fit."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Square tile: diagonal = 8 cm, angle between diagonal and side = 45&deg;. "
                            "Find the side length.</b>", sub))
    story.append(Paragraph("In a square, the diagonal always makes a 45&deg; angle with the side.", step))
    story.append(Paragraph("The relationship between diagonal (d) and side (s) of a square:", step))
    story.append(Paragraph("d = s &times; &radic;2", step))
    story.append(Paragraph("8 = s &times; &radic;2", step))
    story.append(Paragraph("s = 8 / &radic;2", step))
    story.append(Paragraph("Rationalise: s = 8/&radic;2 &times; &radic;2/&radic;2 = 8&radic;2 / 2", step))
    story.append(make_answer_box("Side length = 4&radic;2 &asymp; 5.66 cm"))
    story.append(S(6))
    story.append(make_tip_box(
        "Key facts about squares: diagonal = side &times; &radic;2, and the diagonal bisects the corner angles into two 45&deg; angles."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Pythagoras' theorem: a&sup2; + b&sup2; = c&sup2;. Use it to find diagonals, check if shapes fit, "
        "and solve right-triangle problems."
    ))

    # ========== QUESTION 10 ==========
    story.append(S(10))
    story.append(make_question_header(10, "Sets & Statistics", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Village of 1500 people: 600 keep goats, 700 keep cows, 300 keep neither</b>", sub))
    story.append(S(4))

    story.append(Paragraph("Step 1: Find how many keep at least one animal:", step))
    story.append(Paragraph("People who keep at least one = 1500 - 300 = <b>1200</b>", step))
    story.append(S(4))

    story.append(Paragraph("<b>(i) How many keep both?</b>", sub))
    story.append(Paragraph("Using the addition rule: n(G &cup; C) = n(G) + n(C) - n(G &cap; C)", step))
    story.append(Paragraph("1200 = 600 + 700 - n(Both)", step))
    story.append(Paragraph("n(Both) = 1300 - 1200", step))
    story.append(make_answer_box("Both goats and cows = 100 people"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Goats only:</b>", sub))
    story.append(Paragraph("Goats only = Total goats - Both = 600 - 100", step))
    story.append(make_answer_box("Goats only = 500 people"))
    story.append(S(4))

    story.append(Paragraph("<b>(iii) Cows only:</b>", sub))
    story.append(Paragraph("Cows only = Total cows - Both = 700 - 100", step))
    story.append(make_answer_box("Cows only = 600 people"))
    story.append(S(4))

    story.append(Paragraph("<b>(iv) Goats or cows (at least one):</b>", sub))
    story.append(make_answer_box("Goats or cows = 1200 people"))
    story.append(S(6))

    story.append(make_warning_box(
        "In set problems, 'or' means UNION (at least one), 'and' means INTERSECTION (both). "
        "Always account for the 'neither' group first!"
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Maths test marks: 50-59 (3), 60-69 (21), 70-79 (32), 80-89 (27), 90-99 (17)</b>", sub))
    story.append(Paragraph("Total students = 3 + 21 + 32 + 27 + 17 = <b>100</b>", step))
    story.append(S(4))

    # Frequency table
    freq_header = ["Class Interval", "Frequency", "Class Mark"]
    freq_data = [
        ["50 - 59", "3", "54.5"],
        ["60 - 69", "21", "64.5"],
        ["70 - 79", "32", "74.5"],
        ["80 - 89", "27", "84.5"],
        ["90 - 99", "17", "94.5"],
    ]
    tc = ParagraphStyle('TableC', fontName='Helvetica', fontSize=10,
                         textColor=HexColor("#222222"), alignment=TA_CENTER)
    th = ParagraphStyle('TableH', fontName='Helvetica-Bold', fontSize=10,
                         textColor=white, alignment=TA_CENTER)

    freq_rows = [[Paragraph(c, th) for c in freq_header]]
    freq_rows += [[Paragraph(c, tc) for c in r] for r in freq_data]

    freq_table = Table(freq_rows, colWidths=[130, 100, 100])
    freq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BLUE_BG),
        ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(freq_table)
    story.append(S(6))

    story.append(Paragraph("<b>(i) Class interval size:</b>", sub))
    story.append(Paragraph("Size = Upper boundary - Lower boundary = 59 - 50 + 1 (or 69 - 60 + 1)", step))
    story.append(make_answer_box("Class interval size = 10"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Class with highest frequency:</b>", sub))
    story.append(Paragraph("Looking at the frequency column, the highest frequency is 32.", step))
    story.append(make_answer_box("Highest frequency class = 70 - 79"))
    story.append(S(4))

    story.append(Paragraph("<b>(iii) Class mark of the highest class interval (90-99):</b>", sub))
    story.append(Paragraph("Class mark = (Lower + Upper) / 2 = (90 + 99) / 2", step))
    story.append(make_answer_box("Class mark = 94.5"))
    story.append(S(4))

    story.append(Paragraph("<b>(iv) Students who passed (scored 70 or above):</b>", sub))
    story.append(Paragraph("Passed = 32 + 27 + 17 (classes 70-79, 80-89, 90-99)", step))
    story.append(make_answer_box("Students who passed = 76"))
    story.append(S(4))

    story.append(Paragraph("<b>(v) Students who failed:</b>", sub))
    story.append(Paragraph("Failed = Total - Passed = 100 - 76", step))
    story.append(make_answer_box("Students who failed = 24"))
    story.append(S(6))

    story.append(make_tip_box(
        "Class mark (midpoint) = (lower limit + upper limit) / 2. This is used when calculating the mean "
        "from grouped data."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Sets: draw a Venn diagram to organise information. Statistics: know how to read frequency tables, "
        "find class marks, and interpret grouped data."
    ))

    # ========== CLOSING PAGE ==========
    story.append(PageBreak())
    story.append(S(100))
    story.append(Paragraph("myTZStudies", styles['CoverTitle']))
    story.append(S(10))
    story.append(Paragraph("Thank you for using this Answer Key!", styles['ClosingText']))
    story.append(S(10))
    story.append(Paragraph(
        "Visit <b>mytzstudies.com</b> for more free resources:",
        styles['ClosingText']
    ))
    story.append(S(10))

    resources = [
        "Past exam papers with detailed answer keys",
        "Study guides and topic summaries",
        "Practice tests to boost your confidence",
        "Exam tips and preparation strategies",
    ]
    res_style = ParagraphStyle('ResItem', fontName='Helvetica', fontSize=13,
                                textColor=HexColor("#333333"), alignment=TA_CENTER, leading=20)
    for r in resources:
        story.append(Paragraph(f"&bull; {r}", res_style))

    story.append(S(30))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(10))
    story.append(Paragraph(
        "Your Free Exam Prep Resource",
        styles['CoverTagline']
    ))

    # Build
    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF created successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
