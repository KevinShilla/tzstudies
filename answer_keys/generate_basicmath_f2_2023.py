"""
Generate BasicMath Form 2 2023 NECTA Answer Key PDF
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
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "BasicMath-F2-2023 (Answer Key).pdf")


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
        'CoverDesc', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, textColor=HexColor("#555555"),
        alignment=TA_CENTER, leading=18, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'CoverSmall', parent=styles['Normal'],
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
    story.append(HRFlowable(width="60%", thickness=2, color=DARK_BLUE, spaceAfter=15))
    story.append(Paragraph(
        "Past papers, answer keys, and study resources for Tanzanian students.",
        styles['CoverDesc']
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
    story.append(S(30))
    story.append(Paragraph(
        "Share this with a friend. Every student deserves free study materials.",
        styles['CoverDesc']
    ))
    story.append(S(60))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverSmall']))
    story.append(PageBreak())

    # ========== TITLE PAGE ==========
    story.append(S(80))
    story.append(Paragraph("BASIC MATHEMATICS - FORM TWO", styles['TitlePageHeading']))
    story.append(S(10))
    story.append(Paragraph("National Assessment 2023 - Answer Key", styles['TitlePageSub']))
    story.append(S(30))

    info_data = [
        ["Subject:", "Basic Mathematics"],
        ["Level:", "Form Two"],
        ["Year:", "2023"],
        ["Code:", "041"],
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
    story.append(S(10))
    story.append(Paragraph(
        "Total: 10 questions, each worth 10 marks.",
        ParagraphStyle('IntroMarks', fontName='Helvetica-Bold', fontSize=12,
                       textColor=DARK_BLUE, alignment=TA_CENTER)
    ))
    story.append(PageBreak())

    # ========== QUESTION 1: Multiples &amp; Significant Figures ==========
    story.append(make_question_header(1, "Multiples &amp; Significant Figures", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph("<b>(a) List the first twelve multiples of 4 and 5 and identify common multiples.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> List the first 12 multiples of 4.", step))
    story.append(Paragraph("Multiples of 4: 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48", step))
    story.append(Paragraph("(We get these by multiplying 4 by 1, 2, 3, ... up to 12.)", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> List the first 12 multiples of 5.", step))
    story.append(Paragraph("Multiples of 5: 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Identify common multiples (numbers that appear in both lists).", step))
    story.append(Paragraph("Looking at both lists, we see that <b>20</b> and <b>40</b> appear in both.", step))
    story.append(S(6))
    story.append(make_answer_box("Common multiples of 4 and 5 (within the first 12 multiples): 20, 40"))
    story.append(S(6))

    story.append(make_tip_box(
        "Common multiples are numbers that appear in the multiplication tables of both numbers. "
        "The smallest common multiple is called the Least Common Multiple (LCM). Here, LCM of 4 and 5 is 20."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph("<b>(b) Evaluate (2/25) x 0.737 correct to:</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Convert the fraction to a decimal.", step))
    story.append(Paragraph("2/25 = 2 divided by 25 = 0.08", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Multiply the two decimals.", step))
    story.append(Paragraph("0.08 x 0.737 = 0.05896", step))
    story.append(S(4))

    # (i)
    story.append(Paragraph("<b>(i) One significant figure:</b>", step))
    story.append(Paragraph(
        "The first significant figure is the first non-zero digit. In 0.05896, "
        "the first non-zero digit is 5 (in the hundredths place). "
        "We look at the next digit (8) which is 5 or more, so we round up.",
        step
    ))
    story.append(make_answer_box("0.05896 rounded to 1 significant figure = <b>0.06</b>"))
    story.append(S(6))

    # (ii)
    story.append(Paragraph("<b>(ii) Three decimal places:</b>", step))
    story.append(Paragraph(
        "Three decimal places means we keep three digits after the decimal point. "
        "0.05896 has digits 0, 5, 8 in the first three decimal places. "
        "The fourth decimal digit is 9 (5 or more), so we round up the 8 to 9.",
        step
    ))
    story.append(make_answer_box("0.05896 rounded to 3 decimal places = <b>0.059</b>"))
    story.append(S(6))

    story.append(make_warning_box(
        "Do not confuse significant figures with decimal places! In 0.05896, the leading zeros "
        "are NOT significant. The first significant figure is the 5. "
        "But for decimal places, we count all digits after the decimal point."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 1 tested multiples and rounding. Always list multiples carefully and "
        "remember the difference between significant figures and decimal places."
    ))
    story.append(PageBreak())

    # ========== QUESTION 2: Fractions &amp; Percentages ==========
    story.append(make_question_header(2, "Fractions &amp; Percentages", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph("<b>(a) Arrange 2/3, 4/7, 3/8, and 5/9 in ascending order.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find a common denominator (the bottom number of the fraction).", step))
    story.append(Paragraph(
        "We need the Least Common Denominator (LCD) of 3, 7, 8, and 9. The LCD = 504.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Convert each fraction to have the same denominator.", step))
    story.append(Paragraph("2/3 = (2 x 168)/(3 x 168) = 336/504", step))
    story.append(Paragraph("4/7 = (4 x 72)/(7 x 72) = 288/504", step))
    story.append(Paragraph("3/8 = (3 x 63)/(8 x 63) = 189/504", step))
    story.append(Paragraph("5/9 = (5 x 56)/(9 x 56) = 280/504", step))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 3:</b> Now compare the top numbers of the fractions (numerators): "
        "189, 280, 288, 336.",
        step
    ))
    story.append(Paragraph("Smallest to largest: 189, 280, 288, 336", step))
    story.append(S(6))
    story.append(make_answer_box("Ascending order: 3/8, 5/9, 4/7, 2/3"))
    story.append(S(6))

    story.append(make_tip_box(
        "To compare fractions, convert them all to the same denominator (the bottom number of the fraction). "
        "Then simply compare the numerators (the top numbers). The bigger the numerator, the bigger the fraction."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) In 2016 the population of Mericho village was 2,800. "
        "In 2017 the population increased by 8%. What was the population in 2017?</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Calculate the increase.", step))
    story.append(Paragraph("Increase = 8% of 2,800", step))
    story.append(Paragraph("= (8/100) x 2,800", step))
    story.append(Paragraph("= 0.08 x 2,800", step))
    story.append(Paragraph("= 224 people", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Add the increase to the original population.", step))
    story.append(Paragraph("Population in 2017 = 2,800 + 224 = 3,024", step))
    story.append(S(6))
    story.append(make_answer_box("The population in 2017 was <b>3,024</b> people."))
    story.append(S(6))

    story.append(make_warning_box(
        "A common mistake is to forget to add the increase to the original amount. "
        "When a value increases by a percentage, the new value = original + increase."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 2 covered comparing fractions using a common denominator and calculating "
        "percentage increase. Always convert fractions to the same denominator before comparing."
    ))
    story.append(PageBreak())

    # ========== QUESTION 3: Units of Measurement &amp; Profit ==========
    story.append(make_question_header(3, "Units of Measurement &amp; Profit", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) If 1,000 tonnes of maize were shared equally among 25 schools, "
        "how many kilograms did each school get?</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Convert tonnes to kilograms.", step))
    story.append(Paragraph("1 tonne = 1,000 kg", step))
    story.append(Paragraph("So 1,000 tonnes = 1,000 x 1,000 = 1,000,000 kg", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Divide equally among 25 schools.", step))
    story.append(Paragraph("Each school gets = 1,000,000 / 25 = 40,000 kg", step))
    story.append(S(6))
    story.append(make_answer_box("Each school received <b>40,000 kg</b> of maize."))
    story.append(S(6))

    story.append(make_tip_box(
        "Always convert units first before doing division or other calculations. "
        "Remember: 1 tonne = 1,000 kg, 1 kg = 1,000 g."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) A shopkeeper bought a radio for sh. 80,000 and sold it at a profit of 20%. "
        "Find the profit and selling price.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Calculate the profit.", step))
    story.append(Paragraph("Profit = 20% of the buying price (cost price)", step))
    story.append(Paragraph("Profit = (20/100) x 80,000", step))
    story.append(Paragraph("Profit = 0.20 x 80,000", step))
    story.append(Paragraph("Profit = 16,000 shillings", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Calculate the selling price.", step))
    story.append(Paragraph("Selling price = Cost price + Profit", step))
    story.append(Paragraph("Selling price = 80,000 + 16,000 = 96,000 shillings", step))
    story.append(S(6))
    story.append(make_answer_box("Profit = <b>sh. 16,000</b>. Selling price = <b>sh. 96,000</b>."))
    story.append(S(6))

    story.append(make_warning_box(
        "Remember: Profit is calculated on the cost price (buying price), not the selling price. "
        "Selling price = Cost price + Profit."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 3 tested unit conversion (tonnes to kilograms) and profit calculations. "
        "Always convert to the required unit first, and remember that profit percentage is based on cost price."
    ))
    story.append(PageBreak())

    # ========== QUESTION 4: Geometry - Trapezium &amp; Square ==========
    story.append(make_question_header(4, "Geometry - Trapezium &amp; Square", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) ABCD is a trapezium with AD parallel to BC. "
        "Angle A = 60 degrees, Angle D = 40 degrees. Find angles a, b, and c.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Understand the figure. ABCD is a trapezium where AD is parallel to BC "
        "(shown by arrows). A is bottom-left (60 degrees), D is bottom-right (40 degrees), "
        "B is top-left, C is top-right.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 2:</b> Use the property of co-interior angles (also called same-side interior angles). "
        "When two parallel lines are cut by a transversal, co-interior angles add up to 180 degrees.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Finding angle b:</b>", step))
    story.append(Paragraph(
        "AB is a transversal cutting the parallel lines AD and BC.",
        step
    ))
    story.append(Paragraph(
        "Angle A and angle b are co-interior angles, so: angle A + b = 180 degrees",
        step
    ))
    story.append(Paragraph("60 + b = 180", step))
    story.append(Paragraph("b = 180 - 60 = 120 degrees", step))
    story.append(S(4))
    story.append(Paragraph("<b>Finding angle c:</b>", step))
    story.append(Paragraph(
        "DC is a transversal cutting the parallel lines AD and BC.",
        step
    ))
    story.append(Paragraph(
        "Angle D and angle c are co-interior angles, so: angle D + c = 180 degrees",
        step
    ))
    story.append(Paragraph("40 + c = 180", step))
    story.append(Paragraph("c = 180 - 40 = 140 degrees", step))
    story.append(S(4))
    story.append(Paragraph("<b>Finding angle a:</b>", step))
    story.append(Paragraph(
        "Angle a is the exterior angle at vertex C (between BC extended and DC). "
        "Angles a and c are on a straight line, so they add up to 180 degrees.",
        step
    ))
    story.append(Paragraph("a + c = 180", step))
    story.append(Paragraph("a = 180 - 140 = 40 degrees", step))
    story.append(S(6))
    story.append(make_answer_box("a = <b>40 degrees</b>, b = <b>120 degrees</b>, c = <b>140 degrees</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "Co-interior angles (between parallel lines on the same side of a transversal) always add up to 180 degrees. "
        "Angles on a straight line also add up to 180 degrees."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) A square room has a floor with side = 5 m. Find the perimeter and area.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Calculate the perimeter.", step))
    story.append(Paragraph("A square has 4 equal sides.", step))
    story.append(Paragraph("Perimeter = 4 x side = 4 x 5 = 20 m", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Calculate the area.", step))
    story.append(Paragraph("Area of a square = side x side = 5 x 5 = 25 m<super>2</super>", step))
    story.append(S(6))
    story.append(make_answer_box("Perimeter = <b>20 m</b>. Area = <b>25 m<super>2</super></b>."))
    story.append(S(6))

    story.append(make_warning_box(
        "Do not confuse perimeter (the total distance around the shape) with area (the space inside). "
        "Perimeter is measured in metres (m), while area is in square metres (m<super>2</super>)."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 4 covered properties of parallel lines in a trapezium and basic measurements of a square. "
        "Remember co-interior angles add to 180 degrees."
    ))
    story.append(PageBreak())

    # ========== QUESTION 5: Algebra - Linear &amp; Quadratic Equations ==========
    story.append(make_question_header(5, "Algebra - Linear &amp; Quadratic Equations", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) If (6y + 1)/4 = 5(y + 5)/6, find y correct to three significant figures.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Cross multiply to remove the fractions.", step))
    story.append(Paragraph(
        "Multiply both sides: 6 x (6y + 1) = 4 x 5(y + 5)",
        step
    ))
    story.append(Paragraph("6(6y + 1) = 20(y + 5)", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Expand both sides.", step))
    story.append(Paragraph("36y + 6 = 20y + 100", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Collect like terms (move y terms to one side, numbers to the other).", step))
    story.append(Paragraph("36y - 20y = 100 - 6", step))
    story.append(Paragraph("16y = 94", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 4:</b> Solve for y.", step))
    story.append(Paragraph("y = 94/16 = 5.875", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 5:</b> Round to 3 significant figures.", step))
    story.append(Paragraph(
        "5.875 has 4 significant figures. To round to 3, we look at the 4th digit (5). "
        "Since it is 5 or more, we round up the 7 to 8.",
        step
    ))
    story.append(S(6))
    story.append(make_answer_box("y = <b>5.88</b> (to 3 significant figures)"))
    story.append(S(6))

    story.append(make_tip_box(
        "When cross-multiplying, multiply the top number of the left fraction (numerator) by the "
        "bottom number of the right fraction (denominator), and vice versa."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) Solve 3x<super>2</super> - 7x - 6 = 0 by completing the square.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Divide the entire equation by 3 (the number in front of x<super>2</super>).",
        step
    ))
    story.append(Paragraph("x<super>2</super> - (7/3)x - 2 = 0", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Move the constant to the right side.", step))
    story.append(Paragraph("x<super>2</super> - (7/3)x = 2", step))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 3:</b> Complete the square. Take half of the coefficient of x, then square it.",
        step
    ))
    story.append(Paragraph(
        "Half of 7/3 is 7/6. Squaring it: (7/6)<super>2</super> = 49/36.",
        step
    ))
    story.append(Paragraph("Add 49/36 to both sides:", step))
    story.append(Paragraph(
        "x<super>2</super> - (7/3)x + 49/36 = 2 + 49/36",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 4:</b> Simplify the right side.", step))
    story.append(Paragraph("2 + 49/36 = 72/36 + 49/36 = 121/36", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 5:</b> Write the left side as a perfect square.", step))
    story.append(Paragraph("(x - 7/6)<super>2</super> = 121/36", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 6:</b> Take the square root of both sides.", step))
    story.append(Paragraph("x - 7/6 = +/- 11/6", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 7:</b> Solve for x.", step))
    story.append(Paragraph("x = 7/6 + 11/6 = 18/6 = 3", step))
    story.append(Paragraph("or x = 7/6 - 11/6 = -4/6 = -2/3", step))
    story.append(S(6))
    story.append(make_answer_box("x = <b>3</b> or x = <b>-2/3</b>"))
    story.append(S(6))

    story.append(make_warning_box(
        "When completing the square, do not forget to divide the entire equation by the coefficient "
        "of x<super>2</super> first. Also remember the +/- when taking square roots."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 5 tested solving linear equations by cross-multiplication and quadratic equations "
        "by completing the square. Always show all steps clearly for full marks."
    ))
    story.append(PageBreak())

    # ========== QUESTION 6: Coordinate Geometry &amp; Reflections ==========
    story.append(make_question_header(6, "Coordinate Geometry &amp; Reflections", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) Find the gradient of the straight line joining points (-1, 2) and (3, -5).</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Write down the formula for gradient.", step))
    story.append(Paragraph(
        "Gradient (m) = (y<sub>2</sub> - y<sub>1</sub>) / (x<sub>2</sub> - x<sub>1</sub>)",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Substitute the coordinates.", step))
    story.append(Paragraph(
        "Let (x<sub>1</sub>, y<sub>1</sub>) = (-1, 2) and (x<sub>2</sub>, y<sub>2</sub>) = (3, -5).",
        step
    ))
    story.append(Paragraph("m = (-5 - 2) / (3 - (-1))", step))
    story.append(Paragraph("m = -7 / 4", step))
    story.append(S(6))
    story.append(make_answer_box("Gradient = <b>-7/4</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "The gradient tells you how steep a line is. A negative gradient means the line slopes downward "
        "from left to right. Be careful with negative signs when subtracting coordinates!"
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) Find the image of point P(-3, 7) after reflection in the x-axis and y-axis.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Reflection in the x-axis:</b>", step))
    story.append(Paragraph(
        "When we reflect in the x-axis, the x-coordinate stays the same but the y-coordinate "
        "changes sign (positive becomes negative and vice versa).",
        step
    ))
    story.append(Paragraph("Rule: (x, y) becomes (x, -y)", step))
    story.append(Paragraph("P(-3, 7) becomes P'(-3, -7)", step))
    story.append(S(6))
    story.append(make_answer_box("Image after reflection in x-axis: <b>P'(-3, -7)</b>"))
    story.append(S(6))

    story.append(Paragraph("<b>Reflection in the y-axis:</b>", step))
    story.append(Paragraph(
        "When we reflect in the y-axis, the y-coordinate stays the same but the x-coordinate "
        "changes sign.",
        step
    ))
    story.append(Paragraph("Rule: (x, y) becomes (-x, y)", step))
    story.append(Paragraph("P(-3, 7) becomes P''(3, 7)", step))
    story.append(S(6))
    story.append(make_answer_box("Image after reflection in y-axis: <b>P''(3, 7)</b>"))
    story.append(S(6))

    story.append(make_warning_box(
        "Do not mix up x-axis and y-axis reflections! For x-axis reflection, the y-value changes sign. "
        "For y-axis reflection, the x-value changes sign. A helpful way to remember: "
        "the axis you reflect in is the one that stays the same."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 6 covered the gradient formula and reflections. The gradient is rise over run, "
        "and reflections flip coordinates across the specified axis."
    ))
    story.append(PageBreak())

    # ========== QUESTION 7: Indices &amp; Logarithms ==========
    story.append(make_question_header(7, "Indices &amp; Logarithms", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) Solve for n in the equation 16<super>(1-n)</super> x 2<super>(1+n)</super> = 1/2.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Express all terms as powers of the same base (base 2).",
        step
    ))
    story.append(Paragraph("16 = 2<super>4</super>, so 16<super>(1-n)</super> = (2<super>4</super>)<super>(1-n)</super> = 2<super>4(1-n)</super> = 2<super>(4-4n)</super>", step))
    story.append(Paragraph("Also, 1/2 = 2<super>-1</super>", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Combine the left side using the law of indices (when multiplying, add the powers).", step))
    story.append(Paragraph("2<super>(4-4n)</super> x 2<super>(1+n)</super> = 2<super>-1</super>", step))
    story.append(Paragraph("2<super>(4-4n+1+n)</super> = 2<super>-1</super>", step))
    story.append(Paragraph("2<super>(5-3n)</super> = 2<super>-1</super>", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Since the bases are equal, the powers must be equal.", step))
    story.append(Paragraph("5 - 3n = -1", step))
    story.append(Paragraph("-3n = -1 - 5", step))
    story.append(Paragraph("-3n = -6", step))
    story.append(Paragraph("n = -6 / -3 = 2", step))
    story.append(S(6))
    story.append(make_answer_box("n = <b>2</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "When solving equations with indices (powers), the key strategy is to express everything "
        "with the same base. Then you can equate the powers. Remember: "
        "a<super>m</super> x a<super>n</super> = a<super>(m+n)</super>."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) Find x in log(2x<super>2</super> + 1) + log 4 = log(7x<super>2</super> + 8).</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Use the logarithm law: log A + log B = log(A x B).",
        step
    ))
    story.append(Paragraph("log(4(2x<super>2</super> + 1)) = log(7x<super>2</super> + 8)", step))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 2:</b> Since both sides have log, the expressions inside must be equal.",
        step
    ))
    story.append(Paragraph("4(2x<super>2</super> + 1) = 7x<super>2</super> + 8", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Expand and simplify.", step))
    story.append(Paragraph("8x<super>2</super> + 4 = 7x<super>2</super> + 8", step))
    story.append(Paragraph("8x<super>2</super> - 7x<super>2</super> = 8 - 4", step))
    story.append(Paragraph("x<super>2</super> = 4", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 4:</b> Take the square root of both sides.", step))
    story.append(Paragraph("x = +/- 2", step))
    story.append(S(6))
    story.append(make_answer_box("x = <b>2</b> or x = <b>-2</b>"))
    story.append(S(6))

    story.append(make_warning_box(
        "When using log A + log B = log(AB), make sure both sides of the equation have logarithms "
        "before applying this rule. Also check that your answers make the expressions inside the "
        "logarithms positive (you cannot take the log of a negative number)."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 7 tested laws of indices and logarithms. Express everything in the same base for "
        "index equations, and use log laws to combine or separate logarithms."
    ))
    story.append(PageBreak())

    # ========== QUESTION 8: Similar Triangles &amp; Congruence ==========
    story.append(make_question_header(8, "Similar Triangles &amp; Congruence", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) In triangle ABC, DE is parallel to BC. AD:BD = 3:5 and AC = 9.6 cm. Find AE.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Identify the theorem to use. Since DE is parallel to BC, we use the "
        "Basic Proportionality Theorem (also called the Intercept Theorem).",
        step
    ))
    story.append(Paragraph(
        "This says: If a line is drawn parallel to one side of a triangle, it divides the other "
        "two sides proportionally.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Find the ratio AD:AB.", step))
    story.append(Paragraph("AD:BD = 3:5, so AD:AB = AD:(AD + BD) = 3:(3 + 5) = 3:8", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Apply the proportion.", step))
    story.append(Paragraph("AD/AB = AE/AC (by the Basic Proportionality Theorem)", step))
    story.append(Paragraph("3/8 = AE/9.6", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 4:</b> Solve for AE.", step))
    story.append(Paragraph("AE = 9.6 x (3/8)", step))
    story.append(Paragraph("AE = 9.6 x 0.375", step))
    story.append(Paragraph("AE = 3.6 cm", step))
    story.append(S(6))
    story.append(make_answer_box("AE = <b>3.6 cm</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "The Basic Proportionality Theorem is very useful. When a line is parallel to one side "
        "of a triangle, it creates proportional segments. Make sure to use the correct ratio: "
        "AD/AB (not AD/BD) when comparing with AE/AC."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) ABC is a triangle with AB = AC and D is the midpoint of BC. "
        "Prove that angle ABD = angle ACD.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Proof:</b>", step))
    story.append(S(4))
    story.append(Paragraph("Consider triangles ABD and ACD:", step))
    story.append(S(4))
    story.append(Paragraph("<b>Statement 1:</b> AB = AC (given - the triangle is isosceles)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Statement 2:</b> BD = DC (given - D is the midpoint of BC)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Statement 3:</b> AD = AD (common side - shared by both triangles)", step))
    story.append(S(4))
    story.append(Paragraph(
        "Since all three sides of triangle ABD are equal to the corresponding three sides of "
        "triangle ACD, the two triangles are congruent by the <b>SSS (Side-Side-Side)</b> rule.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph(
        "Therefore, angle ABD = angle ACD (corresponding angles of congruent triangles are equal).",
        step
    ))
    story.append(S(6))
    story.append(make_answer_box(
        "Triangle ABD is congruent to triangle ACD (SSS). "
        "Therefore angle ABD = angle ACD. <b>Q.E.D.</b>"
    ))
    story.append(S(6))

    story.append(make_warning_box(
        "In proofs, always state the reason for each step. The three conditions for SSS congruence "
        "must all be clearly stated. Do not skip any of the three pairs of equal sides."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 8 tested the Basic Proportionality Theorem and triangle congruence proofs. "
        "Know the conditions for congruence: SSS, SAS, ASA, and AAS."
    ))
    story.append(PageBreak())

    # ========== QUESTION 9: Trigonometry &amp; Pythagoras ==========
    story.append(make_question_header(9, "Trigonometry &amp; Pythagoras", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) The angle of elevation of the top of a building from a point on the ground is 25 degrees. "
        "The point is 80 m from the base. Find the height of the building.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Draw a right triangle. The height of the building is the opposite side, "
        "the distance from the base is the adjacent side, and the angle of elevation is 25 degrees.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 2:</b> Choose the correct trigonometric ratio. We have the adjacent side (80 m) "
        "and want the opposite side (height). Use tangent.",
        step
    ))
    story.append(Paragraph("tan(angle) = opposite / adjacent", step))
    story.append(Paragraph("tan(25 degrees) = height / 80", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Solve for the height.", step))
    story.append(Paragraph("height = 80 x tan(25 degrees)", step))
    story.append(Paragraph("height = 80 x 0.4663", step))
    story.append(Paragraph("height = 37.3 m (to one decimal place)", step))
    story.append(S(6))
    story.append(make_answer_box("Height of the building = <b>37.3 m</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "Remember SOH-CAH-TOA: Sin = Opposite/Hypotenuse, Cos = Adjacent/Hypotenuse, "
        "Tan = Opposite/Adjacent. Choose the ratio based on what you know and what you need to find."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) In a right triangle, BA = 6 m, AC = 8 m, and angle A = 90 degrees. Calculate BC.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph(
        "<b>Step 1:</b> Since angle A = 90 degrees, BC is the hypotenuse (the longest side, "
        "opposite the right angle).",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Apply the Pythagorean theorem.", step))
    story.append(Paragraph(
        "BC<super>2</super> = BA<super>2</super> + AC<super>2</super> (Pythagoras' theorem: hypotenuse squared = sum of other two sides squared)",
        step
    ))
    story.append(Paragraph("BC<super>2</super> = 6<super>2</super> + 8<super>2</super>", step))
    story.append(Paragraph("BC<super>2</super> = 36 + 64", step))
    story.append(Paragraph("BC<super>2</super> = 100", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Take the square root.", step))
    story.append(Paragraph("BC = square root of 100 = 10 m", step))
    story.append(S(6))
    story.append(make_answer_box("BC = <b>10 m</b>"))
    story.append(S(6))

    story.append(make_warning_box(
        "The Pythagorean theorem only works for right-angled triangles! The hypotenuse is always "
        "the side opposite the right angle and is always the longest side. "
        "3-4-5, 5-12-13, and 6-8-10 are common Pythagorean triples to memorize."
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 9 tested trigonometry (angle of elevation with tangent) and the Pythagorean theorem. "
        "Always identify which sides you have before choosing your formula."
    ))
    story.append(PageBreak())

    # ========== QUESTION 10: Sets &amp; Statistics ==========
    story.append(make_question_header(10, "Sets &amp; Statistics", styles))
    story.append(S(8))

    # Part (a)
    story.append(Paragraph(
        "<b>(a) 250 students attended Day 1, 350 attended Day 2, 150 attended both days, "
        "and 10 were absent both days. Find the total number of students.</b>",
        sub
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use the addition formula for sets.", step))
    story.append(Paragraph(
        "n(Day 1 union Day 2) = n(Day 1) + n(Day 2) - n(Day 1 intersection Day 2)",
        step
    ))
    story.append(Paragraph(
        "This formula avoids counting the students who attended both days twice.",
        step
    ))
    story.append(S(4))
    story.append(Paragraph("<b>Step 2:</b> Substitute the values.", step))
    story.append(Paragraph("n(Day 1 union Day 2) = 250 + 350 - 150 = 450", step))
    story.append(Paragraph("This means 450 students attended at least one of the two days.", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 3:</b> Add those who were absent both days.", step))
    story.append(Paragraph("Total students = 450 + 10 = 460", step))
    story.append(S(6))
    story.append(make_answer_box("Total number of students = <b>460</b>"))
    story.append(S(6))

    story.append(make_tip_box(
        "The addition formula n(A union B) = n(A) + n(B) - n(A intersection B) prevents double counting. "
        "Do not forget to add back any elements that are outside both sets (like students absent both days)."
    ))
    story.append(S(8))

    # Part (b)
    story.append(Paragraph(
        "<b>(b) A pie chart shows: Kiswahili = 210 degrees, Mathematics = 120 degrees, "
        "Chemistry = 30 degrees.</b>",
        sub
    ))
    story.append(S(4))

    # (i)
    story.append(Paragraph("<b>(i) What fraction of students passed Kiswahili?</b>", step))
    story.append(Paragraph(
        "The total angle in a pie chart is 360 degrees. The fraction is found by dividing "
        "the angle for Kiswahili by the total angle.",
        step
    ))
    story.append(Paragraph("Fraction = 210/360", step))
    story.append(Paragraph(
        "Simplify by dividing both the top number (numerator) and the bottom number (denominator) by 30:",
        step
    ))
    story.append(Paragraph("210/360 = 7/12", step))
    story.append(S(6))
    story.append(make_answer_box("Fraction who passed Kiswahili = <b>7/12</b>"))
    story.append(S(6))

    # (ii)
    story.append(Paragraph("<b>(ii) What percentage of students passed Mathematics?</b>", step))
    story.append(Paragraph("Percentage = (angle for Maths / total angle) x 100%", step))
    story.append(Paragraph("= (120/360) x 100%", step))
    story.append(Paragraph("= (1/3) x 100%", step))
    story.append(Paragraph("= 33.33% (or 33 and 1/3 percent)", step))
    story.append(S(6))
    story.append(make_answer_box("Percentage who passed Mathematics = <b>33.33%</b> (or 33 1/3 %)"))
    story.append(S(6))

    # (iii)
    story.append(Paragraph(
        "<b>(iii) What percentage of students passed Mathematics and Chemistry combined?</b>",
        step
    ))
    story.append(Paragraph("Combined angle = 120 + 30 = 150 degrees", step))
    story.append(Paragraph("Percentage = (150/360) x 100%", step))
    story.append(Paragraph("= (5/12) x 100%", step))
    story.append(Paragraph("= 41.67% (or 41 and 2/3 percent)", step))
    story.append(S(6))
    story.append(make_answer_box(
        "Percentage who passed Mathematics and Chemistry = <b>41.67%</b> (or 41 2/3 %)"
    ))
    story.append(S(6))

    story.append(make_warning_box(
        "In pie charts, the total angle is always 360 degrees. To find a fraction, divide the "
        "sector angle by 360. To find a percentage, multiply the fraction by 100. "
        "Always simplify your fractions!"
    ))
    story.append(S(6))
    story.append(make_section_summary(
        "Question 10 tested set operations (addition formula) and interpreting pie charts. "
        "Remember the total in a pie chart is 360 degrees, and always account for elements outside all sets."
    ))
    story.append(PageBreak())

    # ========== CLOSING / BRANDING PAGE ==========
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
        "Resources from Standard 4 to Form 6",
    ]
    res_style = ParagraphStyle('ResItem', fontName='Helvetica', fontSize=13,
                                textColor=HexColor("#333333"), alignment=TA_CENTER, leading=20)
    for r in resources:
        story.append(Paragraph(f"&bull; {r}", res_style))

    story.append(S(30))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(10))
    story.append(Paragraph(
        "Your Free Tanzanian Exam Library",
        styles['CoverTagline']
    ))
    story.append(S(30))
    story.append(Paragraph(
        "Share this with a friend. Every student deserves free study materials.",
        styles['CoverDesc']
    ))
    story.append(S(40))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverSmall']))

    # Build
    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF created successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
