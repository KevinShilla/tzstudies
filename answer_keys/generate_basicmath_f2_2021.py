"""
Generate BasicMath Form 2 2021 NECTA Answer Key PDF
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
DARK_BLUE = HexColor("#1a5276")
GREEN = HexColor("#27ae60")
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
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "BasicMath-F2-2021 (Answer Key).pdf")


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=42, textColor=DARK_BLUE,
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14, textColor=HexColor("#555555"),
        alignment=TA_CENTER, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'CoverTagline', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, textColor=HexColor("#555555"),
        alignment=TA_CENTER, spaceAfter=10
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
        'CoverShare', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=11, textColor=HexColor("#666666"),
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'CoverFooter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, textColor=HexColor("#999999"),
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
    content = [[
        Paragraph("<b>Common Mistake Warning</b>", ParagraphStyle(
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
    content = [[
        Paragraph("<b>Study Tip</b>", ParagraphStyle(
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
    story.append(Paragraph("Your Free Tanzanian Exam Library", styles['CoverSubtitle']))
    story.append(S(10))
    story.append(HRFlowable(width="80%", thickness=2, color=DARK_BLUE, spaceAfter=10, spaceBefore=5))
    story.append(S(6))
    story.append(Paragraph(
        "Past papers, answer keys, and study resources for Tanzanian students.",
        styles['CoverTagline']
    ))
    story.append(S(10))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(30))

    # Feature boxes - 3x2 grid
    features = [
        "Past Exam Papers", "Answer Keys", "Free Access",
        "Standard 4 to Form 6", "All Subjects Covered", "Updated Regularly"
    ]
    feat_style = ParagraphStyle('FeatInner', fontName='Helvetica-Bold', fontSize=11,
                                textColor=DARK_BLUE, alignment=TA_CENTER)

    def feat_cell(text):
        return Paragraph(text, feat_style)

    row1 = [feat_cell(f) for f in features[:3]]
    row2 = [feat_cell(f) for f in features[3:]]

    col_w = (WIDTH - 80) / 3
    feat_table = Table([row1, row2], colWidths=[col_w] * 3, rowHeights=[45, 45])
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
    story.append(S(40))
    story.append(Paragraph(
        "Share this with a friend. Every student deserves free study materials.",
        styles['CoverShare']
    ))
    story.append(S(80))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverFooter']))
    story.append(PageBreak())

    # ========== TITLE PAGE ==========
    story.append(S(80))
    story.append(Paragraph("BASIC MATHEMATICS - FORM TWO", styles['TitlePageHeading']))
    story.append(S(10))
    story.append(Paragraph("National Assessment 2021 - Answer Key", styles['TitlePageSub']))
    story.append(S(30))

    info_data = [
        ["Subject:", "Basic Mathematics"],
        ["Code:", "041"],
        ["Level:", "Form Two"],
        ["Year:", "2021"],
        ["Exam Board:", "NECTA"],
        ["Type:", "Answer Key"],
        ["Total Questions:", "10 (each worth 10 marks)"],
    ]
    info_style_l = ParagraphStyle('InfoL', fontName='Helvetica-Bold', fontSize=14,
                                  textColor=DARK_BLUE, alignment=TA_LEFT)
    info_style_r = ParagraphStyle('InfoR', fontName='Helvetica', fontSize=14,
                                  textColor=HexColor("#333333"), alignment=TA_LEFT)

    info_rows = [[Paragraph(r[0], info_style_l), Paragraph(r[1], info_style_r)] for r in info_data]
    info_table = Table(info_rows, colWidths=[140, 280])
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
    story.append(make_question_header(1, "Numbers, Place Value &amp; LCM", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Write 498,030 in words.</b>", sub))
    story.append(Paragraph(
        "We need to read the number 498,030 and write it out in English words.",
        body))
    story.append(Paragraph("Step 1: Break the number into groups:", step))
    story.append(Paragraph("498 is in the thousands group, and 030 is in the ones group.", step))
    story.append(Paragraph("Step 2: Read each group:", step))
    story.append(Paragraph("498 = four hundred ninety-eight (thousands)", step))
    story.append(Paragraph("030 = thirty", step))
    story.append(make_answer_box("Four hundred ninety-eight thousand and thirty."))
    story.append(S(6))

    story.append(Paragraph("<b>(a)(ii) Express 498,030 in standard notation (standard form).</b>", sub))
    story.append(Paragraph(
        "Standard notation means writing the number as a value between 1 and 10, multiplied by a power of 10.",
        body))
    story.append(Paragraph("Step 1: Move the decimal point so the number is between 1 and 10:", step))
    story.append(Paragraph("498,030 becomes 4.98030", step))
    story.append(Paragraph("Step 2: Count how many places you moved the decimal point:", step))
    story.append(Paragraph("We moved it 5 places to the left.", step))
    story.append(Paragraph("Step 3: Write in standard form:", step))
    story.append(make_answer_box("498,030 = 4.98030 x 10<super>5</super>"))
    story.append(S(6))

    story.append(Paragraph("<b>(a)(iii) Find the Lowest Common Multiple (LCM) of 3, 10, and 15 using the listing method.</b>", sub))
    story.append(Paragraph(
        "The LCM is the smallest number that all three numbers divide into evenly. "
        "We list the multiples (the times tables) of each number and find the first one they share.",
        body))
    story.append(Paragraph("Step 1: List multiples of 3: 3, 6, 9, 12, 15, 18, 21, 24, 27, <b>30</b>, ...", step))
    story.append(Paragraph("Step 2: List multiples of 10: 10, 20, <b>30</b>, 40, ...", step))
    story.append(Paragraph("Step 3: List multiples of 15: 15, <b>30</b>, 45, ...", step))
    story.append(Paragraph("Step 4: The smallest number that appears in all three lists is 30.", step))
    story.append(make_answer_box("LCM of 3, 10, and 15 = 30"))
    story.append(S(6))

    story.append(make_tip_box(
        "When listing multiples, start from the largest number's multiples first (here, 15). "
        "Check each one against the other numbers. This saves time!"
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(i) Write in numerals: nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred and one.</b>", sub))
    story.append(Paragraph(
        "We need to convert the words back into a number.",
        body))
    story.append(Paragraph("Step 1: Nine hundred ninety-nine million = 999,000,000", step))
    story.append(Paragraph("Step 2: Nine hundred ninety-nine thousand = 999,000", step))
    story.append(Paragraph("Step 3: Nine hundred and one = 901", step))
    story.append(Paragraph("Step 4: Add them together: 999,000,000 + 999,000 + 901", step))
    story.append(make_answer_box("999,999,901"))
    story.append(S(6))

    story.append(Paragraph("<b>(b)(ii) Determine the number of significant figures in 400,780 and 0.00606, then approximate each to one significant figure.</b>", sub))
    story.append(Paragraph(
        "Significant figures are the digits that tell us how precise a number is. "
        "Zeros at the start of a decimal are NOT significant. Zeros between other digits ARE significant.",
        body))
    story.append(S(4))
    story.append(Paragraph("<b>For 400,780:</b>", step))
    story.append(Paragraph("The digits are 4, 0, 0, 7, 8, 0. The trailing zero may or may not be significant, "
                           "but as written, the significant digits are 4, 0, 0, 7, 8 = <b>5 significant figures</b>.", step))
    story.append(Paragraph("Approximated to 1 significant figure: keep only the first digit (4), "
                           "replace the rest with zeros.", step))
    story.append(make_answer_box("400,780 has 5 significant figures. Approximated to 1 sig. fig. = 400,000"))
    story.append(S(4))
    story.append(Paragraph("<b>For 0.00606:</b>", step))
    story.append(Paragraph("The leading zeros (0.00) are NOT significant. They are just placeholders.", step))
    story.append(Paragraph("The significant digits are 6, 0, 6 = <b>3 significant figures</b>.", step))
    story.append(Paragraph("Approximated to 1 significant figure: keep only the first significant digit (6).", step))
    story.append(make_answer_box("0.00606 has 3 significant figures. Approximated to 1 sig. fig. = 0.006"))
    story.append(S(6))

    story.append(make_warning_box(
        "Students often count leading zeros in decimals as significant figures. Remember: "
        "leading zeros (like the 0.00 in 0.00606) are NEVER significant. They are just placeholders!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 1 tests your understanding of place value, standard form (scientific notation), "
        "LCM by listing, and significant figures. These are core number skills for Form Two."
    ))

    # ========== QUESTION 2 ==========
    story.append(S(10))
    story.append(make_question_header(2, "Fractions, Decimals &amp; Percentages", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Write the fractions 2/3, 3/4, 5/8, and 1/2 in order of magnitude starting with the smallest.</b>", sub))
    story.append(Paragraph(
        "To compare fractions, we need to give them all the same bottom number of the fraction (denominator). "
        "This common denominator is called the Lowest Common Denominator (LCD).",
        body))
    story.append(Paragraph("Step 1: Find the LCD of 3, 4, 8, and 2. The LCD = 24.", step))
    story.append(Paragraph("Step 2: Convert each fraction to have 24 as the bottom number (denominator):", step))
    story.append(Paragraph("2/3 = (2 x 8)/(3 x 8) = 16/24", step))
    story.append(Paragraph("3/4 = (3 x 6)/(4 x 6) = 18/24", step))
    story.append(Paragraph("5/8 = (5 x 3)/(8 x 3) = 15/24", step))
    story.append(Paragraph("1/2 = (1 x 12)/(2 x 12) = 12/24", step))
    story.append(Paragraph("Step 3: Now compare the top numbers of the fractions (numerators): 12, 15, 16, 18", step))
    story.append(Paragraph("Step 4: Order from smallest to largest:", step))
    story.append(make_answer_box("1/2, 5/8, 2/3, 3/4"))
    story.append(S(6))

    story.append(Paragraph("<b>(a)(ii) Find the product of 2/3, 3/4, 5/8, and 1/2.</b>", sub))
    story.append(Paragraph(
        "The product means we multiply all the fractions together. "
        "To multiply fractions, multiply all the top numbers of the fractions (numerators) together "
        "and all the bottom numbers of the fractions (denominators) together.",
        body))
    story.append(Paragraph("Step 1: Multiply the top numbers (numerators): 2 x 3 x 5 x 1 = 30", step))
    story.append(Paragraph("Step 2: Multiply the bottom numbers (denominators): 3 x 4 x 8 x 2 = 192", step))
    story.append(Paragraph("Step 3: The result is 30/192. Now simplify by dividing top and bottom by their common factor.", step))
    story.append(Paragraph("30 and 192 are both divisible by 6: 30/6 = 5, 192/6 = 32", step))
    story.append(make_answer_box("(2/3) x (3/4) x (5/8) x (1/2) = 5/32"))
    story.append(S(6))

    story.append(make_tip_box(
        "When multiplying fractions, you can cancel (simplify) BEFORE you multiply. "
        "For example, the 3 in 2/3 cancels with the 3 in 3/4. This makes the numbers smaller and easier to work with!"
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Subtract 0.02 of Tsh. 270,000 from 36% of Tsh. 50,000.</b>", sub))
    story.append(Paragraph(
        "We need to find two amounts and then subtract one from the other.",
        body))
    story.append(Paragraph("Step 1: Find 0.02 of Tsh. 270,000:", step))
    story.append(Paragraph("0.02 x 270,000 = Tsh. 5,400", step))
    story.append(Paragraph("Step 2: Find 36% of Tsh. 50,000:", step))
    story.append(Paragraph("36/100 x 50,000 = Tsh. 18,000", step))
    story.append(Paragraph("Step 3: Subtract: 18,000 - 5,400 = 12,600", step))
    story.append(make_answer_box("Answer: Tsh. 12,600"))
    story.append(S(6))

    story.append(make_warning_box(
        "Read the question carefully! It says 'subtract 0.02 of 270,000 FROM 36% of 50,000'. "
        "This means 36% of 50,000 comes first, then we subtract. The order matters!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 2 covers ordering fractions using a common denominator, multiplying fractions, "
        "and working with decimals and percentages in real-life money problems."
    ))

    # ========== QUESTION 3 ==========
    story.append(S(10))
    story.append(make_question_header(3, "Units of Measurement &amp; Simple Interest", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find the value of 500 cm + 3150 mm + 3.5 m. Give your answer in metres.</b>", sub))
    story.append(Paragraph(
        "Since the answer must be in metres, we convert everything to metres first.",
        body))
    story.append(Paragraph("Step 1: Convert 500 cm to metres: 500 / 100 = 5 m", step))
    story.append(Paragraph("Step 2: Convert 3150 mm to metres: 3150 / 1000 = 3.15 m", step))
    story.append(Paragraph("Step 3: 3.5 m is already in metres.", step))
    story.append(Paragraph("Step 4: Add them all: 5 + 3.15 + 3.5 = 11.65", step))
    story.append(make_answer_box("500 cm + 3150 mm + 3.5 m = 11.65 m"))
    story.append(S(6))

    story.append(make_tip_box(
        "Remember: 1 m = 100 cm = 1000 mm. To convert cm to m, divide by 100. "
        "To convert mm to m, divide by 1000. Always convert to the same unit before adding!"
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Find the number of years for Tshs. 20,000 to earn interest of Tshs. 4,800 at 4% per annum.</b>", sub))
    story.append(Paragraph(
        "We use the simple interest formula: I = PRT / 100, where I = Interest, P = Principal (starting amount), "
        "R = Rate (percentage), and T = Time (in years).",
        body))
    story.append(Paragraph("Step 1: Write down what we know:", step))
    story.append(Paragraph("I = 4,800, P = 20,000, R = 4%, T = ? (what we want to find)", step))
    story.append(Paragraph("Step 2: Put the values into the formula:", step))
    story.append(Paragraph("4,800 = (20,000 x 4 x T) / 100", step))
    story.append(Paragraph("Step 3: Simplify the right side:", step))
    story.append(Paragraph("4,800 = 800T", step))
    story.append(Paragraph("Step 4: Divide both sides by 800:", step))
    story.append(Paragraph("T = 4,800 / 800 = 6", step))
    story.append(make_answer_box("T = 6 years"))
    story.append(S(6))

    story.append(make_warning_box(
        "Always check your answer makes sense. If you get a negative time or a very large number, "
        "you may have mixed up the formula. Remember: I = PRT/100."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 3 tests unit conversion (cm, mm, m) and the simple interest formula. "
        "These skills are used in everyday life when measuring and banking."
    ))

    # ========== QUESTION 4 ==========
    story.append(S(10))
    story.append(make_question_header(4, "Geometry - Polygons &amp; Area", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) Write the name of the polygon ABCD.</b>", sub))
    story.append(Paragraph(
        "A polygon is a flat shape with straight sides. The name depends on how many sides it has.",
        body))
    story.append(Paragraph("ABCD has 4 vertices (corners): A, B, C, D.", step))
    story.append(Paragraph("A shape with 4 sides is called a quadrilateral.", step))
    story.append(make_answer_box("The polygon ABCD is a quadrilateral."))
    story.append(S(6))

    story.append(Paragraph("<b>(a)(ii) Find the values of x and y.</b>", sub))
    story.append(Paragraph(
        "The angles inside any quadrilateral always add up to 360 degrees. "
        "The angles are: A = x, B = 150 degrees, C = (2x - 30) degrees, D = y.",
        body))
    story.append(Paragraph("Step 1: Write the angle sum equation:", step))
    story.append(Paragraph("x + 150 + (2x - 30) + y = 360", step))
    story.append(Paragraph("Step 2: Simplify:", step))
    story.append(Paragraph("3x + y + 120 = 360", step))
    story.append(Paragraph("3x + y = 240 ... (equation 1)", step))
    story.append(Paragraph("Step 3: From the figure, angles A and C are opposite angles and appear equal:", step))
    story.append(Paragraph("x = 2x - 30", step))
    story.append(Paragraph("-x = -30, so x = 30 degrees", step))
    story.append(Paragraph("Step 4: Substitute x = 30 into equation 1:", step))
    story.append(Paragraph("3(30) + y = 240", step))
    story.append(Paragraph("90 + y = 240", step))
    story.append(Paragraph("y = 150 degrees", step))
    story.append(make_answer_box("x = 30 degrees, y = 150 degrees"))
    story.append(S(6))

    story.append(Paragraph("<b>(b) Calculate the area of the figure where O is the centre of the circle and OABC is a square with side 7 cm.</b>", sub))
    story.append(Paragraph(
        "The figure shows a square OABC with a quarter circle arc from A to C (since O is the centre of the circle "
        "with radius 7 cm). We need to find the shaded area, which is the area of the square minus the area of the quarter circle.",
        body))
    story.append(Paragraph("Step 1: Find the area of the square:", step))
    story.append(Paragraph("Area of square = side x side = 7 x 7 = 49 cm<super>2</super>", step))
    story.append(Paragraph("Step 2: Find the area of the quarter circle (using pi = 22/7):", step))
    story.append(Paragraph("Area of quarter circle = (1/4) x pi x r<super>2</super>", step))
    story.append(Paragraph("= (1/4) x (22/7) x 7<super>2</super>", step))
    story.append(Paragraph("= (1/4) x (22/7) x 49", step))
    story.append(Paragraph("= (1/4) x 22 x 7 = (1/4) x 154 = 38.5 cm<super>2</super>", step))
    story.append(Paragraph("Step 3: Find the shaded area:", step))
    story.append(Paragraph("Shaded area = Area of square - Area of quarter circle", step))
    story.append(Paragraph("= 49 - 38.5 = 10.5 cm<super>2</super>", step))
    story.append(make_answer_box("Area of shaded region = 10.5 cm<super>2</super>"))
    story.append(S(6))

    story.append(make_tip_box(
        "When a question involves a circle inside a square (or vice versa), the shaded area is usually "
        "the difference between the two areas. Always use pi = 22/7 unless told otherwise."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 4 covers naming polygons, using the angle sum property of quadrilaterals (360 degrees), "
        "and calculating areas involving circles and squares."
    ))

    # ========== QUESTION 5 ==========
    story.append(S(10))
    story.append(make_question_header(5, "Algebra - Word Problems &amp; Quadratic Equations", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) The age of the father is three times the age of his son. If the sum of their ages is 64 years, find their ages.</b>", sub))
    story.append(Paragraph(
        "We use algebra to set up an equation. Let the son's age be a letter (variable) and express "
        "the father's age using that same letter.",
        body))
    story.append(Paragraph("Step 1: Let the son's age = x", step))
    story.append(Paragraph("Step 2: Father's age = 3x (three times the son's age)", step))
    story.append(Paragraph("Step 3: Their ages add up to 64:", step))
    story.append(Paragraph("x + 3x = 64", step))
    story.append(Paragraph("4x = 64", step))
    story.append(Paragraph("Step 4: Divide both sides by 4:", step))
    story.append(Paragraph("x = 64 / 4 = 16", step))
    story.append(Paragraph("Step 5: Son = 16, Father = 3 x 16 = 48", step))
    story.append(Paragraph("Step 6: Check: 16 + 48 = 64. Correct!", step))
    story.append(make_answer_box("Son's age = 16 years, Father's age = 48 years"))
    story.append(S(6))

    story.append(Paragraph("<b>(b) Solve x<super>2</super> + 7x + 12 = 0 by factorization.</b>", sub))
    story.append(Paragraph(
        "To factorize, we need to find two numbers that multiply to give 12 (the last number) "
        "and add up to give 7 (the middle number).",
        body))
    story.append(Paragraph("Step 1: Find two numbers that multiply to 12 and add to 7:", step))
    story.append(Paragraph("Think: 3 x 4 = 12 and 3 + 4 = 7. So the numbers are 3 and 4.", step))
    story.append(Paragraph("Step 2: Write the factorized form:", step))
    story.append(Paragraph("(x + 3)(x + 4) = 0", step))
    story.append(Paragraph("Step 3: Set each bracket equal to zero:", step))
    story.append(Paragraph("x + 3 = 0 gives x = -3", step))
    story.append(Paragraph("x + 4 = 0 gives x = -4", step))
    story.append(make_answer_box("x = -3 or x = -4"))
    story.append(S(6))

    story.append(make_warning_box(
        "When factorizing quadratics, always check by expanding your answer. "
        "(x + 3)(x + 4) = x<super>2</super> + 4x + 3x + 12 = x<super>2</super> + 7x + 12. Correct!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 5 tests translating word problems into algebraic equations and solving "
        "quadratic equations by factorization. Always check your answers by substituting back."
    ))

    # ========== QUESTION 6 ==========
    story.append(S(10))
    story.append(make_question_header(6, "Coordinate Geometry &amp; Transformations", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find the slope and equation of the line passing through A(6, 4) and B(12, 6).</b>", sub))
    story.append(Paragraph(
        "The slope (gradient) tells us how steep a line is. We use the formula: "
        "slope = (change in y) / (change in x).",
        body))
    story.append(Paragraph("Step 1: Find the slope:", step))
    story.append(Paragraph("slope = (y<sub>2</sub> - y<sub>1</sub>) / (x<sub>2</sub> - x<sub>1</sub>) = (6 - 4) / (12 - 6) = 2/6 = 1/3", step))
    story.append(Paragraph("Step 2: Use the point-slope form to find the equation:", step))
    story.append(Paragraph("y - y<sub>1</sub> = m(x - x<sub>1</sub>)", step))
    story.append(Paragraph("y - 4 = (1/3)(x - 6)", step))
    story.append(Paragraph("y - 4 = (1/3)x - 2", step))
    story.append(Paragraph("y = (1/3)x + 2", step))
    story.append(make_answer_box("Slope = 1/3, Equation: y = (1/3)x + 2"))
    story.append(S(6))

    story.append(Paragraph("<b>(b)(i) A translation takes the origin (0, 0) to (-3, -4). Find where it takes Q(1, -2).</b>", sub))
    story.append(Paragraph(
        "A translation slides every point by the same amount. "
        "The translation vector tells us how far to move in the x and y directions.",
        body))
    story.append(Paragraph("Step 1: Find the translation vector:", step))
    story.append(Paragraph("The origin (0, 0) moves to (-3, -4), so the vector is (-3, -4).", step))
    story.append(Paragraph("Step 2: Apply the same vector to Q(1, -2):", step))
    story.append(Paragraph("Q' = (1 + (-3), -2 + (-4)) = (1 - 3, -2 - 4) = (-2, -6)", step))
    story.append(make_answer_box("Q' = (-2, -6)"))
    story.append(S(6))

    story.append(Paragraph("<b>(b)(ii) Find the images of A(-5, 2) and B(4, -7) after reflection in the y-axis.</b>", sub))
    story.append(Paragraph(
        "When you reflect a point in the y-axis (the vertical line in the middle), "
        "the x-coordinate changes sign (positive becomes negative, negative becomes positive), "
        "but the y-coordinate stays the same.",
        body))
    story.append(Paragraph("Step 1: Reflection rule for y-axis: (x, y) becomes (-x, y)", step))
    story.append(Paragraph("Step 2: A(-5, 2) becomes A'(5, 2)", step))
    story.append(Paragraph("Step 3: B(4, -7) becomes B'(-4, -7)", step))
    story.append(make_answer_box("A' = (5, 2) and B' = (-4, -7)"))
    story.append(S(6))

    story.append(make_tip_box(
        "For reflections: in the y-axis, change the sign of x. In the x-axis, change the sign of y. "
        "A handy memory trick: the axis you reflect in is the one whose coordinate stays the same!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 6 covers finding slope and equation of a line, translations, and reflections. "
        "These are fundamental coordinate geometry and transformation skills."
    ))

    # ========== QUESTION 7 ==========
    story.append(S(10))
    story.append(make_question_header(7, "Exponents &amp; Logarithms", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Find x in (1/3)<super>sqrt(x)</super> = 81<super>(-x)</super></b>", sub))
    story.append(Paragraph(
        "The trick is to rewrite both sides using the same base number. Both 1/3 and 81 can be written as powers of 3.",
        body))
    story.append(Paragraph("Step 1: Rewrite the left side:", step))
    story.append(Paragraph("1/3 = 3<super>-1</super>, so (1/3)<super>sqrt(x)</super> = 3<super>-sqrt(x)</super>", step))
    story.append(Paragraph("Step 2: Rewrite the right side:", step))
    story.append(Paragraph("81 = 3<super>4</super>, so 81<super>(-x)</super> = 3<super>-4x</super>", step))
    story.append(Paragraph("Step 3: Since the bases are the same (both are 3), the powers must be equal:", step))
    story.append(Paragraph("-sqrt(x) = -4x", step))
    story.append(Paragraph("sqrt(x) = 4x", step))
    story.append(Paragraph("Step 4: Divide both sides by sqrt(x) (assuming x is not 0):", step))
    story.append(Paragraph("1 = 4 x sqrt(x)", step))
    story.append(Paragraph("sqrt(x) = 1/4", step))
    story.append(Paragraph("Step 5: Square both sides:", step))
    story.append(Paragraph("x = (1/4)<super>2</super> = 1/16", step))
    story.append(make_answer_box("x = 1/16"))
    story.append(S(6))

    story.append(make_warning_box(
        "When working with exponents, always try to express everything using the same base. "
        "Common bases to try are 2, 3, 5, and 10."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) If log<sub>10</sub>(x/5) = log<sub>10</sub>(2/x) + 1, find x.</b>", sub))
    story.append(Paragraph(
        "Remember that 1 = log<sub>10</sub>(10). We can use logarithm rules to solve this.",
        body))
    story.append(Paragraph("Step 1: Rewrite 1 as log<sub>10</sub>(10):", step))
    story.append(Paragraph("log<sub>10</sub>(x/5) = log<sub>10</sub>(2/x) + log<sub>10</sub>(10)", step))
    story.append(Paragraph("Step 2: Use the log addition rule: log(a) + log(b) = log(a x b):", step))
    story.append(Paragraph("log<sub>10</sub>(x/5) = log<sub>10</sub>((2/x) x 10) = log<sub>10</sub>(20/x)", step))
    story.append(Paragraph("Step 3: If the logs are equal, the numbers inside must be equal:", step))
    story.append(Paragraph("x/5 = 20/x", step))
    story.append(Paragraph("Step 4: Cross multiply:", step))
    story.append(Paragraph("x<super>2</super> = 100", step))
    story.append(Paragraph("Step 5: Take the square root:", step))
    story.append(Paragraph("x = 10 (we take the positive value because log requires positive numbers)", step))
    story.append(make_answer_box("x = 10"))
    story.append(S(6))

    story.append(make_tip_box(
        "Key log rules to remember: log(a) + log(b) = log(ab), log(a) - log(b) = log(a/b), "
        "and n x log(a) = log(a<super>n</super>). Also, log<sub>10</sub>(10) = 1."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 7 tests exponent laws (rewriting with same base) and logarithm rules. "
        "These topics require careful algebraic manipulation."
    ))

    # ========== QUESTION 8 ==========
    story.append(S(10))
    story.append(make_question_header(8, "Congruence &amp; Similarity of Triangles", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Show that triangles XPA and YQA are congruent.</b>", sub))
    story.append(Paragraph(
        "Two triangles are congruent if they have exactly the same shape and size. "
        "We need to show three matching parts. PX and QY are perpendicular to PQ, and PX = QY.",
        body))
    story.append(Paragraph("Step 1: Identify the matching parts:", step))
    story.append(Paragraph("PX = QY (this is given in the question)", step))
    story.append(Paragraph("Angle XPA = Angle YQA = 90 degrees (because PX and QY are perpendicular to PQ)", step))
    story.append(Paragraph("Angle XAP = Angle YAQ (these are vertically opposite angles, which are always equal)", step))
    story.append(Paragraph("Step 2: We have two angles and one side matching. This is the AAS (Angle-Angle-Side) rule.", step))
    story.append(make_answer_box("Triangle XPA is congruent to Triangle YQA by AAS (Angle-Angle-Side) rule."))
    story.append(S(6))

    story.append(make_tip_box(
        "The four ways to prove triangles are congruent: SSS (three sides equal), "
        "SAS (two sides and the angle between them), ASA (two angles and the side between them), "
        "and AAS (two angles and a side not between them)."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Triangles ABC and DEF are similar. Find the values of x, y, z, and w.</b>", sub))
    story.append(Paragraph(
        "Similar triangles have the same shape but can be different sizes. "
        "Their corresponding angles are equal. In triangle ABC: angle A = 60 degrees, angle B = 90 degrees.",
        body))
    story.append(Paragraph("Step 1: Find angle C (which is x) in triangle ABC:", step))
    story.append(Paragraph("Angles in a triangle add up to 180 degrees.", step))
    story.append(Paragraph("x = 180 - 90 - 60 = 30 degrees", step))
    story.append(S(4))
    story.append(Paragraph("Step 2: Since triangle ABC is similar to triangle DEF, corresponding angles are equal:", step))
    story.append(Paragraph("w (at E, corresponding to B) = 90 degrees", step))
    story.append(Paragraph("z (at F, corresponding to A) = 60 degrees", step))
    story.append(Paragraph("y (at D, corresponding to C) = 30 degrees", step))
    story.append(make_answer_box("x = 30 degrees, y = 30 degrees, z = 60 degrees, w = 90 degrees"))
    story.append(S(6))

    story.append(make_section_summary(
        "Question 8 covers proving triangle congruence using AAS and finding angles in similar triangles. "
        "Remember: congruent = same shape AND size; similar = same shape, possibly different size."
    ))

    # ========== QUESTION 9 ==========
    story.append(S(10))
    story.append(make_question_header(9, "Pythagoras' Theorem &amp; Trigonometry", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) In the figure, PQ = 17 cm, QS = 15 cm, RS = 6 cm. Find x (which is PR).</b>", sub))
    story.append(Paragraph(
        "The figure shows triangle PQR with point S on QR such that PS is perpendicular to QR. "
        "We use Pythagoras' Theorem, which says: in a right-angled triangle, the square of the longest side "
        "(hypotenuse) equals the sum of the squares of the other two sides.",
        body))
    story.append(Paragraph("Step 1: In right triangle PQS, find PS using Pythagoras:", step))
    story.append(Paragraph("PQ<super>2</super> = PS<super>2</super> + QS<super>2</super>", step))
    story.append(Paragraph("17<super>2</super> = PS<super>2</super> + 15<super>2</super>", step))
    story.append(Paragraph("289 = PS<super>2</super> + 225", step))
    story.append(Paragraph("PS<super>2</super> = 289 - 225 = 64", step))
    story.append(Paragraph("PS = 8 cm", step))
    story.append(S(4))
    story.append(Paragraph("Step 2: In right triangle PSR, find PR using Pythagoras:", step))
    story.append(Paragraph("PR<super>2</super> = PS<super>2</super> + RS<super>2</super>", step))
    story.append(Paragraph("PR<super>2</super> = 64 + 36 = 100", step))
    story.append(Paragraph("PR = 10 cm", step))
    story.append(make_answer_box("x = PR = 10 cm"))
    story.append(S(6))

    story.append(Paragraph("<b>(b) The angle of elevation of the top of a building from a point 80 m away is 25 degrees. Find the height of the building.</b>", sub))
    story.append(Paragraph(
        "The angle of elevation is the angle you look up from horizontal to see the top of the building. "
        "We use trigonometry: tan(angle) = opposite side / adjacent side.",
        body))
    story.append(Paragraph("Step 1: Draw the situation: the building is the vertical side (opposite), "
                           "the ground distance is the horizontal side (adjacent), and 25 degrees is the angle.", step))
    story.append(Paragraph("Step 2: Use tan:", step))
    story.append(Paragraph("tan(25 degrees) = height / 80", step))
    story.append(Paragraph("Step 3: Look up tan(25 degrees) = 0.4663 (from tables)", step))
    story.append(Paragraph("Step 4: Solve for height:", step))
    story.append(Paragraph("height = 80 x 0.4663 = 37.3 m", step))
    story.append(make_answer_box("Height of the building = 37.3 m"))
    story.append(S(6))

    story.append(make_warning_box(
        "Make sure your calculator is in DEGREE mode, not radian mode, when doing trigonometry! "
        "Also, remember SOH-CAH-TOA: Sin = Opposite/Hypotenuse, Cos = Adjacent/Hypotenuse, Tan = Opposite/Adjacent."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 9 uses Pythagoras' Theorem (for right triangles) and basic trigonometry (tan). "
        "These are essential tools for solving problems involving lengths and angles."
    ))

    # ========== QUESTION 10 ==========
    story.append(S(10))
    story.append(make_question_header(10, "Sets (Venn Diagrams) &amp; Statistics", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) In a class of 30 students, 17 participate in English debate and 12 participate in both English debate and Mathematics club. Every student participates in at least one.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) How many students participate in English debate only?</b>", sub))
    story.append(Paragraph(
        "If 17 students are in English debate total, and 12 of those are also in Mathematics club, "
        "then the rest are in English debate only.",
        body))
    story.append(Paragraph("Step 1: English debate only = Total in English debate - Both", step))
    story.append(Paragraph("= 17 - 12 = 5", step))
    story.append(make_answer_box("English debate only = 5 students"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) How many students participate in Mathematics club only?</b>", sub))
    story.append(Paragraph(
        "We know every student is in at least one activity. So: English only + Both + Maths only = Total.",
        body))
    story.append(Paragraph("Step 1: Use the total:", step))
    story.append(Paragraph("5 + 12 + Maths only = 30", step))
    story.append(Paragraph("Maths only = 30 - 5 - 12 = 13", step))
    story.append(make_answer_box("Mathematics club only = 13 students"))
    story.append(S(4))
    story.append(Paragraph("(Total in Mathematics club = 13 + 12 = 25 students)", step))
    story.append(S(6))

    story.append(make_tip_box(
        "For Venn diagram problems, always start with the overlap (both groups) first, "
        "then work outward. Use the formula: Total = A only + Both + B only."
    ))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Ages of 20 students: 13, 15, 17, 16, 15, 14, 16, 18, 17, 16, 15, 14, 13, 16, 14, 17, 15, 16, 15, 16</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Frequency table:</b>", sub))
    story.append(Paragraph(
        "A frequency table shows how many times each value appears. Count each age carefully.",
        body))

    # Frequency table
    freq_header_style = ParagraphStyle('FHdr', fontName='Helvetica-Bold', fontSize=11,
                                       textColor=white, alignment=TA_CENTER)
    freq_cell_style = ParagraphStyle('FCell', fontName='Helvetica', fontSize=11,
                                     textColor=HexColor("#222222"), alignment=TA_CENTER)

    freq_data = [
        [Paragraph("<b>Age</b>", freq_header_style),
         Paragraph("<b>Tally</b>", freq_header_style),
         Paragraph("<b>Frequency</b>", freq_header_style)],
        [Paragraph("13", freq_cell_style), Paragraph("||", freq_cell_style), Paragraph("2", freq_cell_style)],
        [Paragraph("14", freq_cell_style), Paragraph("|||", freq_cell_style), Paragraph("3", freq_cell_style)],
        [Paragraph("15", freq_cell_style), Paragraph("|||||", freq_cell_style), Paragraph("5", freq_cell_style)],
        [Paragraph("16", freq_cell_style), Paragraph("||||||", freq_cell_style), Paragraph("6", freq_cell_style)],
        [Paragraph("17", freq_cell_style), Paragraph("|||", freq_cell_style), Paragraph("3", freq_cell_style)],
        [Paragraph("18", freq_cell_style), Paragraph("|", freq_cell_style), Paragraph("1", freq_cell_style)],
        [Paragraph("<b>Total</b>", freq_cell_style), Paragraph("", freq_cell_style), Paragraph("<b>20</b>", freq_cell_style)],
    ]

    freq_table = Table(freq_data, colWidths=[80, 100, 100])
    freq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BLUE_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(freq_table)
    story.append(S(8))

    story.append(Paragraph("<b>(ii) Frequency Polygon:</b>", sub))
    story.append(Paragraph(
        "A frequency polygon is drawn by plotting the frequency of each age on a graph, "
        "then connecting the points with straight lines. The x-axis shows the ages and the y-axis shows the frequency.",
        body))
    story.append(Paragraph("Plot these points and connect them with straight lines:", step))
    story.append(Paragraph("(13, 2), (14, 3), (15, 5), (16, 6), (17, 3), (18, 1)", step))
    story.append(Paragraph("Start with a point at (12, 0) and end with a point at (19, 0) to close the polygon.", step))
    story.append(S(6))

    story.append(make_section_summary(
        "Question 10 tests Venn diagrams (set operations) and statistics (frequency tables and frequency polygons). "
        "Always verify your total frequency matches the number of items given."
    ))

    # ========== LAST PAGE - BRANDING ==========
    story.append(PageBreak())
    story.append(S(100))
    story.append(Paragraph("myTZStudies", styles['ClosingTitle']))
    story.append(S(15))
    story.append(Paragraph(
        "Your free resource for Tanzanian exam preparation.",
        styles['ClosingText']
    ))
    story.append(S(10))
    story.append(Paragraph(
        "We provide past papers, answer keys, and study materials<br/>"
        "for students from Standard 4 to Form 6.",
        styles['ClosingText']
    ))
    story.append(S(10))
    story.append(Paragraph(
        "All resources are completely free.<br/>"
        "Every Tanzanian student deserves access to quality study materials.",
        styles['ClosingText']
    ))
    story.append(S(20))
    story.append(Paragraph(
        '<b><font color="#27ae60">mytzstudies.com</font></b>',
        ParagraphStyle('ClosingURL', fontName='Helvetica-Bold', fontSize=22,
                       textColor=GREEN, alignment=TA_CENTER)
    ))
    story.append(S(30))
    story.append(Paragraph(
        "Share this with a friend. Education is the key to success.",
        ParagraphStyle('ClosingShare', fontName='Helvetica-Oblique', fontSize=12,
                       textColor=HexColor("#777777"), alignment=TA_CENTER)
    ))

    # Build
    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF created: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
