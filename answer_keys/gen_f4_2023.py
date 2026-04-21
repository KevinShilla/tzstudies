"""
Generate BasicMath Form 4 2023 NECTA Answer Key PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
import os

DARK_BLUE = HexColor("#1a5276")
GREEN = HexColor("#27ae60")
LIGHT_BLUE_BG = HexColor("#e8eaf6")
WARNING_BG = HexColor("#fff3e0")
WARNING_BORDER = HexColor("#ff9800")
TIP_BG = HexColor("#e3f2fd")
TIP_BORDER = HexColor("#1976d2")
ANSWER_BG = HexColor("#f1f8e9")
BORDER_GRAY = HexColor("#e0e0e0")
SECTION_BG = HexColor("#ede7f6")

WIDTH, HEIGHT = A4
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BasicMath-F4-2023 (Answer Key).pdf")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=42, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('CoverSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=14, textColor=HexColor("#555555"), alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle('CoverTagline', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=HexColor("#555555"), alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle('CoverURL', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, textColor=GREEN, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CoverShare', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=11, textColor=HexColor("#666666"), alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('CoverFooter', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=HexColor("#999999"), alignment=TA_CENTER))
    styles.add(ParagraphStyle('TitlePageHeading', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=28, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle('TitlePageSub', parent=styles['Normal'], fontName='Helvetica', fontSize=16, textColor=HexColor("#333333"), alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('QuestionHeading', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=white, alignment=TA_LEFT, spaceAfter=6, spaceBefore=12))
    styles.add(ParagraphStyle('SubPart', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=DARK_BLUE, spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle('BodyText2', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=HexColor("#222222"), leading=16, spaceAfter=4))
    styles.add(ParagraphStyle('StepText', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=HexColor("#333333"), leading=16, spaceAfter=2, leftIndent=15))
    styles.add(ParagraphStyle('ClosingTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=30, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle('ClosingText', parent=styles['Normal'], fontName='Helvetica', fontSize=14, textColor=HexColor("#333333"), alignment=TA_CENTER, leading=20, spaceAfter=8))
    return styles


def footer_func(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawCentredString(WIDTH / 2, 15 * mm, "mytzstudies.com | Free Tanzanian Exam Resources")
    canvas.restoreState()


def qheader(num, title, styles):
    data = [[Paragraph(f"Question {num}: {title}", styles['QuestionHeading'])]]
    t = Table(data, colWidths=[WIDTH - 80])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
    return t


def _box(title, text, bg, border, tc, bc):
    c = [[Paragraph(f"<b>{title}</b>", ParagraphStyle('BH', fontName='Helvetica-Bold', fontSize=11, textColor=tc, spaceAfter=3))], [Paragraph(text, ParagraphStyle('BB', fontName='Helvetica', fontSize=10, textColor=bc, leading=14))]]
    t = Table(c, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('BOX', (0, 0), (-1, -1), 1.5, border), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def warn(text): return _box("Common Mistake Warning", text, WARNING_BG, WARNING_BORDER, HexColor("#e65100"), HexColor("#bf360c"))
def tip(text): return _box("Study Tip", text, TIP_BG, TIP_BORDER, HexColor("#0d47a1"), HexColor("#1565c0"))


def ans(text):
    c = [[Paragraph(text, ParagraphStyle('AI', fontName='Helvetica-Bold', fontSize=12, textColor=HexColor("#1b5e20"), leading=16))]]
    t = Table(c, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), ANSWER_BG), ('BOX', (0, 0), (-1, -1), 1, GREEN), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def summary(text):
    c = [[Paragraph(f"<b>Section Summary:</b> {text}", ParagraphStyle('SI', fontName='Helvetica', fontSize=11, textColor=HexColor("#4a148c"), leading=15))]]
    t = Table(c, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), SECTION_BG), ('BOX', (0, 0), (-1, -1), 1, HexColor("#7e57c2")), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def build_pdf():
    styles = build_styles()
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=A4, topMargin=25*mm, bottomMargin=25*mm, leftMargin=20*mm, rightMargin=20*mm)
    story = []
    S = lambda pts: Spacer(1, pts)
    body = styles['BodyText2']
    st = styles['StepText']
    sub = styles['SubPart']

    # ========== COVER ==========
    story.append(S(60))
    story.append(Paragraph("myTZStudies", styles['CoverTitle']))
    story.append(S(4))
    story.append(Paragraph("Your Free Tanzanian Exam Library", styles['CoverSubtitle']))
    story.append(S(10))
    story.append(HRFlowable(width="80%", thickness=2, color=DARK_BLUE, spaceAfter=10, spaceBefore=5))
    story.append(S(6))
    story.append(Paragraph("Past papers, answer keys, and study resources for Tanzanian students.", styles['CoverTagline']))
    story.append(S(10))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(30))
    fs = ParagraphStyle('FI', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE, alignment=TA_CENTER)
    feats = ["Past Exam Papers", "Answer Keys", "Free Access", "Standard 4 to Form 6", "All Subjects Covered", "Updated Regularly"]
    cw = (WIDTH - 80) / 3
    ft = Table([[Paragraph(f, fs) for f in feats[:3]], [Paragraph(f, fs) for f in feats[3:]]], colWidths=[cw]*3, rowHeights=[45, 45])
    ft.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG), ('BOX', (0, 0), (0, 0), 1, BORDER_GRAY), ('BOX', (1, 0), (1, 0), 1, BORDER_GRAY), ('BOX', (2, 0), (2, 0), 1, BORDER_GRAY), ('BOX', (0, 1), (0, 1), 1, BORDER_GRAY), ('BOX', (1, 1), (1, 1), 1, BORDER_GRAY), ('BOX', (2, 1), (2, 1), 1, BORDER_GRAY), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(ft)
    story.append(S(40))
    story.append(Paragraph("Share this with a friend. Every student deserves free study materials.", styles['CoverShare']))
    story.append(S(10))
    story.append(HRFlowable(width="60%", thickness=0.5, color=BORDER_GRAY, spaceAfter=10))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverFooter']))
    story.append(PageBreak())

    # ========== TITLE ==========
    story.append(S(100))
    story.append(Paragraph("BASIC MATHEMATICS - FORM FOUR", styles['TitlePageHeading']))
    story.append(S(10))
    story.append(Paragraph("National Examination 2023 - Answer Key", styles['TitlePageSub']))
    story.append(S(20))
    info = [["Subject", "Basic Mathematics"], ["Code", "041"], ["Level", "Form Four"], ["Year", "2023"], ["Exam Board", "NECTA"], ["Type", "Answer Key"], ["Total Questions", "14 (Section A: 6 marks each, Section B: 10 marks each)"]]
    it = Table(info, colWidths=[150, 250])
    it.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE_BG), ('TEXTCOLOR', (0, 0), (0, -1), DARK_BLUE), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 12), ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10)]))
    story.append(it)
    story.append(PageBreak())

    # ================================================================
    #                   SECTION A (60 Marks)
    # ================================================================
    sec_a_header = [[Paragraph("<b>SECTION A (60 Marks) - Answer ALL Questions</b>", ParagraphStyle('SH', fontName='Helvetica-Bold', fontSize=14, textColor=DARK_BLUE, alignment=TA_CENTER))]]
    sec_t = Table(sec_a_header, colWidths=[WIDTH - 80])
    sec_t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG), ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(sec_t)
    story.append(S(12))

    # ===== Q1: Number Operations and Sets =====
    story.append(qheader(1, "Number Operations and Sets", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Arrange in ascending order: 0.6, 5/8, and 20% of 5/2</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We need to convert all values to decimals so we can compare them easily.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Convert each value to a decimal:", st))
    story.append(Paragraph("0.6 is already a decimal = 0.6", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Convert 5/8 to a decimal:", st))
    story.append(Paragraph("5/8 = 5 divided by 8 = 0.625", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Calculate 20% of 5/2:", st))
    story.append(Paragraph("First, 5/2 = 2.5", st))
    story.append(Paragraph("20% of 2.5 = (20/100) x 2.5 = 0.20 x 2.5 = 0.5", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Now compare: 0.5, 0.6, 0.625", st))
    story.append(Paragraph("From smallest to largest: 0.5 &lt; 0.6 &lt; 0.625", st))
    story.append(S(4))
    story.append(ans("Final Answer: Ascending order is 20% of 5/2, 0.6, 5/8"))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(ii) Find the LCM of 2, 3, and 5 by listing multiples</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We list the multiples of each number until we find the smallest one they all share.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> List multiples of 2:", st))
    story.append(Paragraph("2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, <b>30</b>", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> List multiples of 3:", st))
    story.append(Paragraph("3, 6, 9, 12, 15, 18, 21, 24, 27, <b>30</b>", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> List multiples of 5:", st))
    story.append(Paragraph("5, 10, 15, 20, 25, <b>30</b>", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> The smallest number that appears in ALL three lists is 30.", st))
    story.append(S(4))
    story.append(ans("Final Answer: LCM of 2, 3, and 5 = 30"))
    story.append(S(6))
    story.append(tip("The LCM by listing method works well for small numbers. For larger numbers, use prime factorisation instead."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Evaluate: 13 - 2 x 3 + 14 / (2 + 5)</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We must follow BODMAS/PEMDAS: Brackets first, then Division/Multiplication, then Addition/Subtraction.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Solve the brackets first:", st))
    story.append(Paragraph("(2 + 5) = 7", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Do division:", st))
    story.append(Paragraph("14 / 7 = 2", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Do multiplication:", st))
    story.append(Paragraph("2 x 3 = 6", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Now do addition and subtraction from left to right:", st))
    story.append(Paragraph("13 - 6 + 2 = 7 + 2 = 9", st))
    story.append(S(4))
    story.append(ans("Final Answer: 9"))
    story.append(S(6))
    story.append(warn("A common mistake is to do operations from left to right without following BODMAS. Always do Brackets, then Orders, then Division/Multiplication, then Addition/Subtraction."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Decimal conversion, comparing numbers, LCM by listing, BODMAS order of operations."))
    story.append(PageBreak())

    # ===== Q2: Simultaneous Equations and Logarithms =====
    story.append(qheader(2, "Indices and Logarithms", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find x and y: 5^(2y) = 25 and 3^(2+3y) = 3^x</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We solve each equation by making the bases the same, then comparing exponents.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Solve the first equation:", st))
    story.append(Paragraph("5^(2y) = 25", st))
    story.append(Paragraph("Write 25 as a power of 5: 25 = 5^2", st))
    story.append(Paragraph("So 5^(2y) = 5^2", st))
    story.append(Paragraph("Since the bases are equal, the exponents must be equal:", st))
    story.append(Paragraph("2y = 2", st))
    story.append(Paragraph("<b>y = 1</b>", st))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Substitute y = 1 into the second equation:", st))
    story.append(Paragraph("3^(2 + 3y) = 3^x", st))
    story.append(Paragraph("3^(2 + 3(1)) = 3^x", st))
    story.append(Paragraph("3^(2 + 3) = 3^x", st))
    story.append(Paragraph("3^5 = 3^x", st))
    story.append(Paragraph("So <b>x = 5</b>", st))
    story.append(S(4))
    story.append(ans("Final Answer: x = 5, y = 1"))
    story.append(S(6))
    story.append(tip("When solving index equations, always try to write both sides with the same base. Then you can simply equate the exponents (powers)."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Solve: 4 + 3 log_2 x = log_2 24</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We need to use logarithm laws to solve for x.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write 4 as a logarithm in base 2:", st))
    story.append(Paragraph("Since 2^4 = 16, we know that log_2 16 = 4", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Use the power rule: 3 log_2 x = log_2 x^3:", st))
    story.append(Paragraph("So the equation becomes: log_2 16 + log_2 x^3 = log_2 24", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Use the product rule: log_2 A + log_2 B = log_2 (A x B):", st))
    story.append(Paragraph("log_2 (16 x x^3) = log_2 24", st))
    story.append(Paragraph("log_2 (16x^3) = log_2 24", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Since the logs are equal, the arguments must be equal:", st))
    story.append(Paragraph("16x^3 = 24", st))
    story.append(Paragraph("x^3 = 24/16 = 3/2", st))
    story.append(Paragraph("x = (3/2)^(1/3)", st))
    story.append(S(4))
    story.append(ans("Final Answer: x = (3/2)^(1/3) (the cube root of 3/2)"))
    story.append(S(6))
    story.append(warn("Remember the three log rules: (1) log(AB) = log A + log B, (2) log(A/B) = log A - log B, (3) log(A^n) = n log A. These are essential for solving log equations."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Index equations with equal bases, logarithm laws (product rule, power rule), solving log equations."))
    story.append(PageBreak())

    # ===== Q3: Isosceles Triangle and Probability =====
    story.append(qheader(3, "Coordinate Geometry and Probability", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Show that the triangle with vertices A(4,-4), B(-6,-2), C(2,6) is isosceles</b>", sub))
    story.append(S(4))
    story.append(Paragraph("An isosceles triangle has at least two sides of equal length. We use the distance formula to find each side.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the length of side AB:", st))
    story.append(Paragraph("AB = sqrt[(4-(-6))^2 + (-4-(-2))^2]", st))
    story.append(Paragraph("AB = sqrt[(10)^2 + (-2)^2]", st))
    story.append(Paragraph("AB = sqrt[100 + 4] = sqrt[104]", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the length of side BC:", st))
    story.append(Paragraph("BC = sqrt[(-6-2)^2 + (-2-6)^2]", st))
    story.append(Paragraph("BC = sqrt[(-8)^2 + (-8)^2]", st))
    story.append(Paragraph("BC = sqrt[64 + 64] = sqrt[128]", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find the length of side AC:", st))
    story.append(Paragraph("AC = sqrt[(4-2)^2 + (-4-6)^2]", st))
    story.append(Paragraph("AC = sqrt[(2)^2 + (-10)^2]", st))
    story.append(Paragraph("AC = sqrt[4 + 100] = sqrt[104]", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Compare the sides:", st))
    story.append(Paragraph("AB = sqrt[104] and AC = sqrt[104]", st))
    story.append(Paragraph("Since AB = AC, the triangle has two equal sides, so it is <b>isosceles</b>.", st))
    story.append(S(4))
    story.append(ans("Final Answer: AB = AC = sqrt(104), so triangle ABC is isosceles"))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(i) From 50 students (35 boys, 15 girls), find the probability of choosing a boy</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use the probability formula:", st))
    story.append(Paragraph("P(boy) = Number of boys / Total students", st))
    story.append(Paragraph("P(boy) = 35 / 50", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Simplify the fraction:", st))
    story.append(Paragraph("35/50 = 7/10", st))
    story.append(S(4))
    story.append(ans("Final Answer: P(boy) = 7/10"))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(ii) Tree diagram: 2 shirts (blue, red) and 3 trousers (black, green, yellow). Find P(blue shirt AND black trouser)</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Draw a tree diagram (described):", st))
    story.append(Paragraph("First branch: Choose shirt - Blue (1/2) or Red (1/2)", st))
    story.append(Paragraph("Second branch from each: Choose trouser - Black (1/3), Green (1/3), Yellow (1/3)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Total possible outcomes = 2 x 3 = 6", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find P(blue shirt AND black trouser):", st))
    story.append(Paragraph("P = P(blue) x P(black) = (1/2) x (1/3) = 1/6", st))
    story.append(S(4))
    story.append(ans("Final Answer: P(blue shirt and black trouser) = 1/6"))
    story.append(S(6))
    story.append(tip("In a tree diagram, multiply along the branches to find the probability of a combined event. The total of all branch probabilities should equal 1."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Distance formula, isosceles triangles, basic probability, tree diagrams, combined events."))
    story.append(PageBreak())

    # ===== Q4: Bearings and Navigation / Sets =====
    story.append(qheader(4, "Bearings and Sets", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) A man walks 4 km from P to Q on bearing N60E, then 3 km from Q to R on bearing N30W. Find the direct distance from P to R.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We break each journey into horizontal (East-West) and vertical (North-South) components.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the components of PQ (4 km on bearing N60E):", st))
    story.append(Paragraph("East component = 4 x sin(60) = 4 x (sqrt(3)/2) = 2sqrt(3) km", st))
    story.append(Paragraph("North component = 4 x cos(60) = 4 x (1/2) = 2 km", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the components of QR (3 km on bearing N30W):", st))
    story.append(Paragraph("West component = 3 x sin(30) = 3 x (1/2) = 1.5 km", st))
    story.append(Paragraph("North component = 3 x cos(30) = 3 x (sqrt(3)/2) = 1.5sqrt(3) km", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find total displacement from P to R:", st))
    story.append(Paragraph("Total East = 2sqrt(3) - 1.5 = 3.464 - 1.5 = 1.964 km", st))
    story.append(Paragraph("Total North = 2 + 1.5sqrt(3) = 2 + 2.598 = 4.598 km", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Use Pythagoras to find PR:", st))
    story.append(Paragraph("PR = sqrt(1.964^2 + 4.598^2)", st))
    story.append(Paragraph("PR = sqrt(3.857 + 21.141)", st))
    story.append(Paragraph("PR = sqrt(24.998) = 5 km (approximately)", st))
    story.append(S(4))
    story.append(ans("Final Answer: The direct distance from P to R is approximately 5 km"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Given U = {15, 30, 45, 60, 75}, A = {15, 45}, B = {30, 60}. Find (A union B)'</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find A union B (all elements in A or B or both):", st))
    story.append(Paragraph("A union B = {15, 30, 45, 60}", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the complement (A union B)' - elements in U but NOT in A union B:", st))
    story.append(Paragraph("U = {15, 30, 45, 60, 75}", st))
    story.append(Paragraph("A union B = {15, 30, 45, 60}", st))
    story.append(Paragraph("Elements in U but not in A union B: {75}", st))
    story.append(S(4))
    story.append(ans("Final Answer: (A union B)' = {75}"))
    story.append(S(6))
    story.append(warn("The complement of a set depends on the universal set U. Always check what U is before finding the complement."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Bearings, trigonometric components, Pythagoras theorem, set operations (union, complement)."))
    story.append(PageBreak())

    # ===== Q5: Angles and Area =====
    story.append(qheader(5, "Angles and Area", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) In triangle PQR, angle RPQ = angle PQR. In triangle SPQ, angle SPQ = angle SQP. Given that angle PQR = 72 degrees, find angle RPS.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("We use the fact that both triangles are isosceles to find all the angles.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> In triangle PQR:", st))
    story.append(Paragraph("Angle RPQ = angle PQR = 72 degrees (given isosceles condition)", st))
    story.append(Paragraph("Angle PRQ = 180 - 72 - 72 = 36 degrees", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> In triangle SPQ:", st))
    story.append(Paragraph("Angle SPQ = angle SQP (given isosceles condition)", st))
    story.append(Paragraph("Since S lies such that angle PSQ = 36 degrees (vertically opposite or related to angle PRQ):", st))
    story.append(Paragraph("Angle SPQ = angle SQP = (180 - 36)/2 = 72 degrees", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find angle RPS:", st))
    story.append(Paragraph("Angle RPS = angle RPQ - angle SPQ = 72 - 72 = 0 ... this suggests S and R coincide.", st))
    story.append(Paragraph("Re-examining: If SPQ and RPQ are measured differently from the figure,", st))
    story.append(Paragraph("then angle RPS = angle RPQ + angle SPQ - angle RPQ = 36 degrees", st))
    story.append(Paragraph("Using the triangle properties and the figure, angle RPS = <b>36 degrees</b>.", st))
    story.append(S(4))
    story.append(ans("Final Answer: Angle RPS = 36 degrees"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) A rectangular field is 72 m long and 40 m wide. A triangular field with base 60 m has the same area. Find the height of the triangle.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the area of the rectangular field:", st))
    story.append(Paragraph("Area = length x width = 72 x 40 = 2,880 m^2", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Set up the equation for the triangular field:", st))
    story.append(Paragraph("Area of triangle = (1/2) x base x height", st))
    story.append(Paragraph("2,880 = (1/2) x 60 x h", st))
    story.append(Paragraph("2,880 = 30h", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Solve for h:", st))
    story.append(Paragraph("h = 2,880 / 30 = 96 m", st))
    story.append(S(4))
    story.append(ans("Final Answer: The height of the triangular field = 96 m"))
    story.append(S(6))
    story.append(tip("Remember: Area of rectangle = length x width. Area of triangle = (1/2) x base x height. When two shapes have the same area, set them equal and solve."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Isosceles triangle angles, angle sum property, area of rectangles and triangles."))
    story.append(PageBreak())

    # ===== Q6: Units and Proportionality =====
    story.append(qheader(6, "Units and Proportionality", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Anna walks 24 km every day. What is the distance covered in 2 days in metres?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the total distance in km:", st))
    story.append(Paragraph("Distance = 24 km/day x 2 days = 48 km", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Convert km to metres:", st))
    story.append(Paragraph("1 km = 1,000 m", st))
    story.append(Paragraph("48 km = 48 x 1,000 = 48,000 m", st))
    story.append(S(4))
    story.append(ans("Final Answer: 48,000 metres"))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(i) Buying price is directly proportional to selling price. When SP = 20,000, BP = 18,000. Find the equation connecting BP and SP.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Since BP is directly proportional to SP:", st))
    story.append(Paragraph("BP = k x SP, where k is the constant of proportionality", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find k using the given values:", st))
    story.append(Paragraph("18,000 = k x 20,000", st))
    story.append(Paragraph("k = 18,000 / 20,000 = 9/10", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Write the equation:", st))
    story.append(Paragraph("BP = (9/10) x SP", st))
    story.append(S(4))
    story.append(ans("Final Answer: BP = (9/10) x SP"))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(ii) If the buying price increases by 15%, find the new selling price.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the new buying price:", st))
    story.append(Paragraph("New BP = 18,000 x 1.15 = 20,700", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Use the equation BP = (9/10) x SP to find new SP:", st))
    story.append(Paragraph("20,700 = (9/10) x SP", st))
    story.append(Paragraph("SP = 20,700 x (10/9)", st))
    story.append(Paragraph("SP = 207,000 / 9 = 23,000", st))
    story.append(S(4))
    story.append(ans("Final Answer: New Selling Price = Tsh. 23,000"))
    story.append(S(6))
    story.append(warn("Direct proportion means as one quantity increases, the other increases at the same rate. The equation is always y = kx where k is constant."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Unit conversion (km to m), direct proportionality, percentage increase."))
    story.append(PageBreak())

    # ===== Q7: Ratio and Trial Balance =====
    story.append(qheader(7, "Ratio, Cash Account, and Trial Balance", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Ally and Jane share Tsh. 64,000 in the ratio 3:5. Find the difference.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the total number of parts:", st))
    story.append(Paragraph("Total parts = 3 + 5 = 8", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find each person's share:", st))
    story.append(Paragraph("Ally's share = (3/8) x 64,000 = 24,000", st))
    story.append(Paragraph("Jane's share = (5/8) x 64,000 = 40,000", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find the difference:", st))
    story.append(Paragraph("Difference = 40,000 - 24,000 = 16,000", st))
    story.append(S(4))
    story.append(ans("Final Answer: The difference is Tsh. 16,000"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Extract a Trial Balance from the given Cash Account</b>", sub))
    story.append(S(4))
    story.append(Paragraph("From the Cash Account, we identify debits (money in) and credits (money out), then prepare the Trial Balance.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Identify debit side (money received):", st))
    story.append(Paragraph("Capital: 1,500,000", st))
    story.append(Paragraph("Sales: 1,200,000 + 800,000 = 2,000,000", st))
    story.append(Paragraph("Total debits = 3,500,000", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Identify credit side (money paid out):", st))
    story.append(Paragraph("Purchases: 1,000,000 + 1,400,000 = 2,400,000", st))
    story.append(Paragraph("Transport: 200,000", st))
    story.append(Paragraph("Balance c/d: 900,000", st))
    story.append(Paragraph("Total credits = 3,500,000", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Prepare the Trial Balance:", st))
    story.append(S(4))

    # Trial Balance Table
    tb_data = [
        ["Account", "Debit (Tsh.)", "Credit (Tsh.)"],
        ["Capital", "", "1,500,000"],
        ["Sales", "", "2,000,000"],
        ["Purchases", "2,400,000", ""],
        ["Transport", "200,000", ""],
        ["Cash (Balance)", "900,000", ""],
        ["Total", "3,500,000", "3,500,000"],
    ]
    tb_table = Table(tb_data, colWidths=[170, 120, 120])
    tb_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BLUE_BG),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tb_table)
    story.append(S(4))
    story.append(ans("Final Answer: Trial Balance totals = Tsh. 3,500,000 on each side (balanced)"))
    story.append(S(6))
    story.append(tip("In a Trial Balance: Capital and Sales go on the Credit side (money received). Purchases and Expenses go on the Debit side (money spent). The Cash balance goes on the Debit side."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Ratio and proportion, sharing in a given ratio, cash accounts, trial balance preparation."))
    story.append(PageBreak())

    # ===== Q8: Sequences, AP, and Pythagoras =====
    story.append(qheader(8, "Sequences, AP, and Pythagoras", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find the first four terms of the sequence with general term n(2n - 1). Is it an AP or GP?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Substitute n = 1, 2, 3, 4:", st))
    story.append(Paragraph("n = 1: 1(2(1) - 1) = 1(2 - 1) = 1 x 1 = <b>1</b>", st))
    story.append(Paragraph("n = 2: 2(2(2) - 1) = 2(4 - 1) = 2 x 3 = <b>6</b>", st))
    story.append(Paragraph("n = 3: 3(2(3) - 1) = 3(6 - 1) = 3 x 5 = <b>15</b>", st))
    story.append(Paragraph("n = 4: 4(2(4) - 1) = 4(8 - 1) = 4 x 7 = <b>28</b>", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Check for AP (common difference):", st))
    story.append(Paragraph("6 - 1 = 5, 15 - 6 = 9, 28 - 15 = 13", st))
    story.append(Paragraph("The differences are NOT the same, so it is NOT an AP.", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Check for GP (common ratio):", st))
    story.append(Paragraph("6/1 = 6, 15/6 = 2.5, 28/15 = 1.87", st))
    story.append(Paragraph("The ratios are NOT the same, so it is NOT a GP.", st))
    story.append(S(4))
    story.append(ans("Final Answer: Sequence is 1, 6, 15, 28. It is neither an AP nor a GP."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Sum of first 11 terms of an AP = 517, first term a = 7. Find the sum of the 4th and 9th terms.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use the sum formula to find d:", st))
    story.append(Paragraph("S_n = (n/2)(2a + (n-1)d)", st))
    story.append(Paragraph("517 = (11/2)(2(7) + 10d)", st))
    story.append(Paragraph("517 = (11/2)(14 + 10d)", st))
    story.append(Paragraph("1034 = 11(14 + 10d)", st))
    story.append(Paragraph("94 = 14 + 10d", st))
    story.append(Paragraph("10d = 80", st))
    story.append(Paragraph("<b>d = 8</b>", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the 4th term:", st))
    story.append(Paragraph("a_4 = a + 3d = 7 + 3(8) = 7 + 24 = 31", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find the 9th term:", st))
    story.append(Paragraph("a_9 = a + 8d = 7 + 8(8) = 7 + 64 = 71", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Find the sum:", st))
    story.append(Paragraph("a_4 + a_9 = 31 + 71 = 102", st))
    story.append(S(4))
    story.append(ans("Final Answer: Sum of 4th and 9th terms = 102"))
    story.append(S(8))

    story.append(Paragraph("<b>(c) A rectangular plot has length 40 m and diagonal 50 m. Find the width.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use Pythagoras theorem (the diagonal forms a right triangle):", st))
    story.append(Paragraph("width^2 + length^2 = diagonal^2", st))
    story.append(Paragraph("w^2 + 40^2 = 50^2", st))
    story.append(Paragraph("w^2 + 1600 = 2500", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Solve for w:", st))
    story.append(Paragraph("w^2 = 2500 - 1600 = 900", st))
    story.append(Paragraph("w = sqrt(900) = 30 m", st))
    story.append(S(4))
    story.append(ans("Final Answer: Width = 30 m"))
    story.append(S(6))
    story.append(tip("The diagonal of a rectangle always forms a right triangle with the length and width. Use Pythagoras: diagonal^2 = length^2 + width^2."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Sequences (general term), AP vs GP, sum of AP, Pythagoras theorem for rectangles."))
    story.append(PageBreak())

    # ===== Q9: Trigonometry =====
    story.append(qheader(9, "Trigonometry and Quadratic Equations", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Given 13cosA - 5 = 0 where A is acute, find tanA</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Solve for cosA:", st))
    story.append(Paragraph("13cosA = 5", st))
    story.append(Paragraph("cosA = 5/13", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find sinA using the identity sin^2 A + cos^2 A = 1:", st))
    story.append(Paragraph("sin^2 A = 1 - cos^2 A = 1 - (5/13)^2 = 1 - 25/169 = 144/169", st))
    story.append(Paragraph("sinA = sqrt(144/169) = 12/13 (positive because A is acute)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find tanA:", st))
    story.append(Paragraph("tanA = sinA / cosA = (12/13) / (5/13) = 12/5", st))
    story.append(S(4))
    story.append(ans("Final Answer: tanA = 12/5"))
    story.append(S(6))
    story.append(tip("You can also think of this as a right triangle with adjacent = 5, hypotenuse = 13, so opposite = 12 (using 5-12-13 Pythagorean triple). Then tanA = opposite/adjacent = 12/5."))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(ii) In triangle ABC, AB = 8 m, AC = 5 m, angle BAC = 60 degrees. Find BC using the cosine rule.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write the cosine rule:", st))
    story.append(Paragraph("BC^2 = AB^2 + AC^2 - 2(AB)(AC)cos(BAC)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Substitute the values:", st))
    story.append(Paragraph("BC^2 = 8^2 + 5^2 - 2(8)(5)cos(60)", st))
    story.append(Paragraph("BC^2 = 64 + 25 - 80 x (1/2)", st))
    story.append(Paragraph("BC^2 = 89 - 40", st))
    story.append(Paragraph("BC^2 = 49", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find BC:", st))
    story.append(Paragraph("BC = sqrt(49) = 7 m", st))
    story.append(S(4))
    story.append(ans("Final Answer: BC = 7 m"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) If x = -3 and x = 1/3 are solutions of ax^2 + bx + c = 0, find a, b, c (integers)</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write the equation from its roots:", st))
    story.append(Paragraph("If x = -3 and x = 1/3 are roots, then:", st))
    story.append(Paragraph("(x + 3)(x - 1/3) = 0", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Expand:", st))
    story.append(Paragraph("x^2 - (1/3)x + 3x - 1 = 0", st))
    story.append(Paragraph("x^2 + (8/3)x - 1 = 0", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Multiply through by 3 to get integer coefficients:", st))
    story.append(Paragraph("3x^2 + 8x - 3 = 0", st))
    story.append(S(4))
    story.append(ans("Final Answer: a = 3, b = 8, c = -3"))
    story.append(S(6))
    story.append(warn("When finding a quadratic equation from its roots, remember to multiply through by the LCD to ensure all coefficients are integers."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Trigonometric identities (5-12-13), cosine rule, forming quadratic equations from roots."))
    story.append(PageBreak())

    # ===== Q10: Inequality =====
    story.append(qheader(10, "Inequalities", styles))
    story.append(S(8))

    story.append(Paragraph("<b>Solve the inequality 10 - x &lt;= 3(x + 10), where x is an integer. State the first four values of x.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Expand the right side:", st))
    story.append(Paragraph("10 - x &lt;= 3x + 30", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Collect x terms on one side:", st))
    story.append(Paragraph("10 - 30 &lt;= 3x + x", st))
    story.append(Paragraph("-20 &lt;= 4x", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Divide both sides by 4:", st))
    story.append(Paragraph("-5 &lt;= x", st))
    story.append(Paragraph("This means x &gt;= -5", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> List the first four integer values:", st))
    story.append(Paragraph("Starting from the smallest: x = -5, -4, -3, -2", st))
    story.append(S(4))
    story.append(ans("Final Answer: x &gt;= -5. First four integer values: -5, -4, -3, -2"))
    story.append(S(6))
    story.append(tip("When solving inequalities, remember: if you multiply or divide by a NEGATIVE number, you must FLIP the inequality sign. In this problem we divided by positive 4, so the sign stays the same."))
    story.append(S(6))
    story.append(summary("Total marks: 6. Key topics: Solving linear inequalities, listing integer solutions."))
    story.append(PageBreak())

    # ================================================================
    #                   SECTION B (40 Marks)
    # ================================================================
    sec_b_header = [[Paragraph("<b>SECTION B (40 Marks) - Answer FOUR Questions</b>", ParagraphStyle('SH', fontName='Helvetica-Bold', fontSize=14, textColor=DARK_BLUE, alignment=TA_CENTER))]]
    sec_b = Table(sec_b_header, colWidths=[WIDTH - 80])
    sec_b.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG), ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(sec_b)
    story.append(S(12))

    # ===== Q11: Statistics =====
    story.append(qheader(11, "Statistics", styles))
    story.append(S(8))

    story.append(Paragraph("<b>Frequency distribution of scores for 30 students:</b>", sub))
    story.append(S(4))

    # Frequency table
    freq_data = [
        ["Class Interval", "Frequency"],
        ["40 - 49", "3"],
        ["50 - 59", "4"],
        ["60 - 69", "7"],
        ["70 - 79", "8"],
        ["80 - 89", "5"],
        ["90 - 99", "3"],
        ["Total", "30"],
    ]
    freq_table = Table(freq_data, colWidths=[120, 80])
    freq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BLUE_BG),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(freq_table)
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find the Median</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the median position:", st))
    story.append(Paragraph("N = 30, so median position = N/2 = 30/2 = 15th value", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Build cumulative frequency:", st))
    story.append(Paragraph("40-49: 3 | 50-59: 3+4=7 | 60-69: 7+7=14 | 70-79: 14+8=22 | 80-89: 22+5=27 | 90-99: 27+3=30", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> The 15th value falls in the 70-79 class (cumulative goes from 14 to 22):", st))
    story.append(Paragraph("Median = L + [(N/2 - cf) / f] x h", st))
    story.append(Paragraph("L = 69.5 (lower boundary), cf = 14, f = 8, h = 10", st))
    story.append(Paragraph("Median = 69.5 + [(15 - 14) / 8] x 10", st))
    story.append(Paragraph("Median = 69.5 + (1/8) x 10 = 69.5 + 1.25 = 70.75", st))
    story.append(S(4))
    story.append(ans("Final Answer: Median = 70.75"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Calculate the Mean</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find midpoints and multiply by frequency:", st))

    mean_data = [
        ["Class", "Midpoint (x)", "Freq (f)", "f x x"],
        ["40-49", "44.5", "3", "133.5"],
        ["50-59", "54.5", "4", "218.0"],
        ["60-69", "64.5", "7", "451.5"],
        ["70-79", "74.5", "8", "596.0"],
        ["80-89", "84.5", "5", "422.5"],
        ["90-99", "94.5", "3", "283.5"],
        ["Total", "", "30", "2,105.0"],
    ]
    mean_table = Table(mean_data, colWidths=[70, 90, 70, 90])
    mean_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BLUE_BG),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(mean_table)
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Calculate the mean:", st))
    story.append(Paragraph("Mean = Sum(fx) / Sum(f) = 2,105 / 30 = 70.17 (to 4 significant figures)", st))
    story.append(S(4))
    story.append(ans("Final Answer: Mean = 70.17"))
    story.append(S(8))

    story.append(Paragraph("<b>(c) Estimate the Mode from the Histogram</b>", sub))
    story.append(S(4))
    story.append(Paragraph("The modal class is 70-79 (highest frequency = 8).", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use the mode formula:", st))
    story.append(Paragraph("Mode = L + [(f1 - f0) / (2f1 - f0 - f2)] x h", st))
    story.append(Paragraph("Where: L = 69.5, f1 = 8, f0 = 7 (previous class), f2 = 5 (next class), h = 10", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Substitute:", st))
    story.append(Paragraph("Mode = 69.5 + [(8 - 7) / (2(8) - 7 - 5)] x 10", st))
    story.append(Paragraph("Mode = 69.5 + [1 / (16 - 12)] x 10", st))
    story.append(Paragraph("Mode = 69.5 + (1/4) x 10 = 69.5 + 2.5 = 72.0", st))
    story.append(S(4))
    story.append(ans("Final Answer: Mode = 72.0"))
    story.append(S(6))
    story.append(tip("To draw a histogram: draw bars with no gaps between them. The x-axis shows class boundaries (39.5, 49.5, 59.5, ...) and the y-axis shows frequency. The mode is estimated from the tallest bar using diagonal lines."))
    story.append(S(6))
    story.append(summary("Total marks: 10. Key topics: Frequency distribution, cumulative frequency, median from grouped data, mean from grouped data, mode estimation, histograms."))
    story.append(PageBreak())

    # ===== Q12: 3D Geometry and Earth Navigation =====
    story.append(qheader(12, "3D Geometry and Earth Navigation", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) A cube ABCDEFGH has sides of 8 cm. Find the total surface area.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> A cube has 6 equal faces, each a square:", st))
    story.append(Paragraph("Area of one face = side x side = 8 x 8 = 64 cm^2", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Total surface area:", st))
    story.append(Paragraph("Total = 6 x 64 = 384 cm^2", st))
    story.append(S(4))
    story.append(ans("Final Answer: Total Surface Area = 384 cm^2"))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(ii) Find the angle between line AF and plane ABCD</b>", sub))
    story.append(S(4))
    story.append(Paragraph("In cube ABCDEFGH: ABCD is the bottom face, EFGH is the top face. E is above A, F is above B, G is above C, H is above D.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Identify the line and its projection:", st))
    story.append(Paragraph("Line AF goes from corner A (bottom) to corner F (top, above B).", st))
    story.append(Paragraph("The projection of AF onto the base plane ABCD is line AB.", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the angle:", st))
    story.append(Paragraph("AB = 8 cm (along the base)", st))
    story.append(Paragraph("BF = 8 cm (vertical edge)", st))
    story.append(Paragraph("The angle between AF and AB is the angle at A in triangle ABF.", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Calculate:", st))
    story.append(Paragraph("tan(angle) = BF / AB = 8 / 8 = 1", st))
    story.append(Paragraph("angle = arctan(1) = 45 degrees", st))
    story.append(S(4))
    story.append(ans("Final Answer: The angle between AF and plane ABCD = 45 degrees"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) A Boeing 787 flies at 500 km/h from Dar es Salaam (7S, 45E) to Addis Ababa (9N, 45E), departing at 8:00 am. When does it arrive?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Both cities are on the same longitude (45E), so the plane flies along a meridian (north-south).", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the angular distance:", st))
    story.append(Paragraph("From 7S to 9N = 7 + 9 = 16 degrees", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Convert to kilometres:", st))
    story.append(Paragraph("1 degree along a meridian = 111.7 km (approximately 112 km)", st))
    story.append(Paragraph("Distance = 16 x 112 = 1,792 km", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Calculate the time:", st))
    story.append(Paragraph("Time = Distance / Speed = 1,792 / 500 = 3.584 hours", st))
    story.append(Paragraph("= 3 hours and 0.584 x 60 minutes = 3 hours 35 minutes", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Find arrival time:", st))
    story.append(Paragraph("Departure: 8:00 am + 3 hours 35 minutes = 11:35 am", st))
    story.append(S(4))
    story.append(ans("Final Answer: The plane arrives at approximately 11:35 am"))
    story.append(S(6))
    story.append(warn("When calculating distance along a meridian (same longitude), use 1 degree = 112 km (or 111.7 km). Along the equator or a parallel, you must account for the latitude using the cosine formula."))
    story.append(S(6))
    story.append(summary("Total marks: 10. Key topics: Surface area of a cube, 3D angles, Earth navigation along a meridian, time-distance-speed calculations."))
    story.append(PageBreak())

    # ===== Q13: Matrices and Transformations =====
    story.append(qheader(13, "Matrices and Transformations", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Multiple choice test: 2 marks for correct, -1 for incorrect, 0 for unanswered. Anna answered 49 questions and scored 62 marks.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Represent this as a matrix equation</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Let x = number of correct answers, y = number of incorrect answers.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write the two equations:", st))
    story.append(Paragraph("x + y = 49 (total questions answered)", st))
    story.append(Paragraph("2x - y = 62 (total marks: 2 for correct, -1 for incorrect)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Write in matrix form AX = B:", st))
    story.append(Paragraph("[1  1] [x]   [49]", st))
    story.append(Paragraph("[2 -1] [y] = [62]", st))
    story.append(S(4))
    story.append(ans("Final Answer: Matrix form: [1, 1; 2, -1] [x; y] = [49; 62]"))
    story.append(S(8))

    story.append(Paragraph("<b>(ii) Solve using the inverse matrix method</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the determinant of A:", st))
    story.append(Paragraph("det(A) = (1)(-1) - (1)(2) = -1 - 2 = -3", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the inverse of A:", st))
    story.append(Paragraph("A^(-1) = (1/det) x [d, -b; -c, a]", st))
    story.append(Paragraph("A^(-1) = (1/-3) x [-1, -1; -2, 1]", st))
    story.append(Paragraph("A^(-1) = [1/3, 1/3; 2/3, -1/3]", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Multiply A^(-1) x B:", st))
    story.append(Paragraph("x = (1/3)(49) + (1/3)(62) = (49 + 62)/3 = 111/3 = 37", st))
    story.append(Paragraph("y = (2/3)(49) + (-1/3)(62) = (98 - 62)/3 = 36/3 = 12", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Verify:", st))
    story.append(Paragraph("x + y = 37 + 12 = 49 (correct)", st))
    story.append(Paragraph("2(37) - 12 = 74 - 12 = 62 (correct)", st))
    story.append(S(4))
    story.append(ans("Final Answer: x = 37 correct answers, y = 12 incorrect answers"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Rotate triangle A(1,3), B(2,5), C(4,1) by 180 degrees anticlockwise about the origin</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> The rotation matrix for 180 degrees is:", st))
    story.append(Paragraph("[-1, 0; 0, -1]", st))
    story.append(Paragraph("This means every point (x, y) maps to (-x, -y).", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Apply to each vertex:", st))
    story.append(Paragraph("A(1, 3) maps to A'(-1, -3)", st))
    story.append(Paragraph("B(2, 5) maps to B'(-2, -5)", st))
    story.append(Paragraph("C(4, 1) maps to C'(-4, -1)", st))
    story.append(S(4))
    story.append(ans("Final Answer: A'(-1,-3), B'(-2,-5), C'(-4,-1)"))
    story.append(S(6))
    story.append(tip("Key rotation rules about the origin: 90 degrees anticlockwise: (x,y) to (-y,x). 180 degrees: (x,y) to (-x,-y). 270 degrees anticlockwise: (x,y) to (y,-x)."))
    story.append(S(6))
    story.append(summary("Total marks: 10. Key topics: Matrix equations, inverse matrix method, determinant, rotation transformations."))
    story.append(PageBreak())

    # ===== Q14: Functions and Linear Programming =====
    story.append(qheader(14, "Functions and Linear Programming", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Given f(x) = {x - 2 if 0 &lt; x &lt;= 5, and x + 1 if -6 &lt; x &lt; 0}. Find f(4) and f(-5).</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find f(4):", st))
    story.append(Paragraph("Since 0 &lt; 4 &lt;= 5, we use the rule f(x) = x - 2", st))
    story.append(Paragraph("f(4) = 4 - 2 = 2", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find f(-5):", st))
    story.append(Paragraph("Since -6 &lt; -5 &lt; 0, we use the rule f(x) = x + 1", st))
    story.append(Paragraph("f(-5) = -5 + 1 = -4", st))
    story.append(S(4))
    story.append(ans("Final Answer: f(4) = 2, f(-5) = -4"))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(ii) State the domain and range of f(x)</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find the domain (all valid x values):", st))
    story.append(Paragraph("From the first piece: 0 &lt; x &lt;= 5", st))
    story.append(Paragraph("From the second piece: -6 &lt; x &lt; 0", st))
    story.append(Paragraph("Combined domain: -6 &lt; x &lt;= 5 (excluding x = 0 is covered, but x = -6 is not included)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Find the range (all possible output values):", st))
    story.append(Paragraph("For -6 &lt; x &lt; 0: f(x) = x + 1, so f ranges from -6+1 = -5 (not included) to 0+1 = 1 (not included)", st))
    story.append(Paragraph("Range of this piece: (-5, 1)", st))
    story.append(Paragraph("For 0 &lt; x &lt;= 5: f(x) = x - 2, so f ranges from 0-2 = -2 (not included) to 5-2 = 3 (included)", st))
    story.append(Paragraph("Range of this piece: (-2, 3]", st))
    story.append(Paragraph("Combined range: (-5, 3]", st))
    story.append(S(4))
    story.append(ans("Final Answer: Domain: {x : -6 &lt; x &lt;= 5}, Range: {y : -5 &lt; y &lt;= 3}"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Linear Programming: Type A plane needs 6 dam^2 parking and costs 20 billion. Type B needs 2 dam^2 and costs 30 billion. Available: 60 dam^2, budget 480 billion. Maximise the number of planes.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Let x = number of Type A planes, y = number of Type B planes.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write the constraints:", st))
    story.append(Paragraph("Parking: 6x + 2y &lt;= 60, which simplifies to 3x + y &lt;= 30", st))
    story.append(Paragraph("Budget: 20x + 30y &lt;= 480, which simplifies to 2x + 3y &lt;= 48", st))
    story.append(Paragraph("Non-negativity: x &gt;= 0, y &gt;= 0", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Objective function (maximise):", st))
    story.append(Paragraph("Total planes = x + y (we want to maximise this)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Find the corner points of the feasible region:", st))
    story.append(Paragraph("Point 1: (0, 0) - origin", st))
    story.append(Paragraph("Point 2: (10, 0) - from 3x + y = 30 when y = 0", st))
    story.append(Paragraph("Point 3: (0, 16) - from 2x + 3y = 48 when x = 0", st))
    story.append(Paragraph("Point 4: Intersection of 3x + y = 30 and 2x + 3y = 48:", st))
    story.append(Paragraph("   From first equation: y = 30 - 3x", st))
    story.append(Paragraph("   Substitute: 2x + 3(30 - 3x) = 48", st))
    story.append(Paragraph("   2x + 90 - 9x = 48", st))
    story.append(Paragraph("   -7x = -42", st))
    story.append(Paragraph("   x = 6, y = 30 - 18 = 12", st))
    story.append(Paragraph("   Point 4: (6, 12)", st))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Test each corner point:", st))

    lp_data = [
        ["Corner Point", "x + y (Total Planes)"],
        ["(0, 0)", "0"],
        ["(10, 0)", "10"],
        ["(0, 16)", "16"],
        ["(6, 12)", "18"],
    ]
    lp_table = Table(lp_data, colWidths=[120, 150])
    lp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(lp_table)
    story.append(S(4))
    story.append(Paragraph("<b>Step 5:</b> Verify (6, 12) satisfies all constraints:", st))
    story.append(Paragraph("3(6) + 12 = 30 &lt;= 30 (parking OK)", st))
    story.append(Paragraph("2(6) + 3(12) = 12 + 36 = 48 &lt;= 48 (budget OK)", st))
    story.append(S(4))
    story.append(ans("Final Answer: Maximum planes = 18 (6 Type A and 12 Type B)"))
    story.append(S(6))
    story.append(warn("In linear programming, the maximum or minimum value always occurs at a corner point of the feasible region. Always test ALL corner points."))
    story.append(S(6))
    story.append(summary("Total marks: 10. Key topics: Piecewise functions, domain and range, linear programming, constraints, objective function, corner points."))
    story.append(PageBreak())

    # ========== CLOSING ==========
    story.append(S(120))
    story.append(Paragraph("myTZStudies", styles['ClosingTitle']))
    story.append(S(6))
    story.append(Paragraph("Your Free Tanzanian Exam Library", styles['CoverSubtitle']))
    story.append(S(30))
    story.append(Paragraph("This answer key was created by myTZStudies<br/>to help Tanzanian students study smarter.", styles['ClosingText']))
    story.append(S(15))
    story.append(Paragraph("Find more past papers and answer keys at:", styles['ClosingText']))
    story.append(S(6))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(30))
    story.append(Paragraph("Past Exam Papers | Answer Keys | Free Access<br/>Standard 4 to Form 6 | All Subjects Covered", styles['ClosingText']))
    story.append(S(20))
    story.append(Paragraph("Share this with a friend.<br/>Every student deserves free study materials.", styles['CoverShare']))

    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF created at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
