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
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BasicMath-F2-2022 (Answer Key).pdf")


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
    styles.add(ParagraphStyle('BodyText2', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=HexColor("#222222"), leading=16, spaceAfter=4, alignment=TA_LEFT))
    styles.add(ParagraphStyle('StepText', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=HexColor("#333333"), leading=16, spaceAfter=2, leftIndent=15))
    styles.add(ParagraphStyle('AnswerText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=HexColor("#1b5e20"), leading=16, spaceAfter=6, leftIndent=15))
    styles.add(ParagraphStyle('ClosingTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=30, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle('ClosingText', parent=styles['Normal'], fontName='Helvetica', fontSize=14, textColor=HexColor("#333333"), alignment=TA_CENTER, leading=20, spaceAfter=8))
    return styles


def footer_func(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawCentredString(WIDTH / 2, 15 * mm, "mytzstudies.com | Free Tanzanian Exam Resources")
    canvas.restoreState()


def make_question_header(num, title, styles):
    data = [[Paragraph(f"Question {num}: {title}", styles['QuestionHeading'])]]
    t = Table(data, colWidths=[WIDTH - 80])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
    return t


def make_box(title, text, bg, border, title_color, text_color):
    content = [[Paragraph(f"<b>{title}</b>", ParagraphStyle('BH', fontName='Helvetica-Bold', fontSize=11, textColor=title_color, spaceAfter=3))], [Paragraph(text, ParagraphStyle('BB', fontName='Helvetica', fontSize=10, textColor=text_color, leading=14))]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('BOX', (0, 0), (-1, -1), 1.5, border), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def warning_box(text):
    return make_box("Common Mistake Warning", text, WARNING_BG, WARNING_BORDER, HexColor("#e65100"), HexColor("#bf360c"))


def tip_box(text):
    return make_box("Study Tip", text, TIP_BG, TIP_BORDER, HexColor("#0d47a1"), HexColor("#1565c0"))


def answer_box(text):
    content = [[Paragraph(text, ParagraphStyle('AI', fontName='Helvetica-Bold', fontSize=12, textColor=HexColor("#1b5e20"), leading=16))]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), ANSWER_BG), ('BOX', (0, 0), (-1, -1), 1, GREEN), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def section_summary(text):
    content = [[Paragraph(f"<b>Section Summary:</b> {text}", ParagraphStyle('SI', fontName='Helvetica', fontSize=11, textColor=HexColor("#4a148c"), leading=15))]]
    t = Table(content, colWidths=[WIDTH - 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), SECTION_BG), ('BOX', (0, 0), (-1, -1), 1, HexColor("#7e57c2")), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


def build_pdf():
    styles = build_styles()
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=A4, topMargin=25*mm, bottomMargin=25*mm, leftMargin=20*mm, rightMargin=20*mm)
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
    story.append(Paragraph("Past papers, answer keys, and study resources for Tanzanian students.", styles['CoverTagline']))
    story.append(S(10))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(30))

    feat_style = ParagraphStyle('FI', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE, alignment=TA_CENTER)
    features = ["Past Exam Papers", "Answer Keys", "Free Access", "Standard 4 to Form 6", "All Subjects Covered", "Updated Regularly"]
    row1 = [Paragraph(f, feat_style) for f in features[:3]]
    row2 = [Paragraph(f, feat_style) for f in features[3:]]
    col_w = (WIDTH - 80) / 3
    ft = Table([row1, row2], colWidths=[col_w]*3, rowHeights=[45, 45])
    ft.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG), ('BOX', (0, 0), (0, 0), 1, BORDER_GRAY), ('BOX', (1, 0), (1, 0), 1, BORDER_GRAY), ('BOX', (2, 0), (2, 0), 1, BORDER_GRAY), ('BOX', (0, 1), (0, 1), 1, BORDER_GRAY), ('BOX', (1, 1), (1, 1), 1, BORDER_GRAY), ('BOX', (2, 1), (2, 1), 1, BORDER_GRAY), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(ft)
    story.append(S(40))
    story.append(Paragraph("Share this with a friend. Every student deserves free study materials.", styles['CoverShare']))
    story.append(S(10))
    story.append(HRFlowable(width="60%", thickness=0.5, color=BORDER_GRAY, spaceAfter=10))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverFooter']))
    story.append(PageBreak())

    # ========== TITLE PAGE ==========
    story.append(S(100))
    story.append(Paragraph("BASIC MATHEMATICS - FORM TWO", styles['TitlePageHeading']))
    story.append(S(10))
    story.append(Paragraph("National Assessment 2022 - Answer Key", styles['TitlePageSub']))
    story.append(S(20))
    info = [["Subject", "Basic Mathematics"], ["Code", "041"], ["Level", "Form Two"], ["Year", "2022"], ["Exam Board", "NECTA"], ["Type", "Answer Key"], ["Total Questions", "10 (10 marks each)"]]
    info_table = Table(info, colWidths=[150, 250])
    info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE_BG), ('TEXTCOLOR', (0, 0), (0, -1), DARK_BLUE), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 12), ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10)]))
    story.append(info_table)
    story.append(PageBreak())

    # ========== QUESTION 1 ==========
    story.append(make_question_header(1, "Bank Withdrawals and Recurring Decimals", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Mwajuma deposited Tsh. 360,000 in her bank account. The bank charges Tsh. 1,000 for every withdrawal.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) She withdrew Tsh. 106,000. How much remained?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("First, let us understand what the question is asking:", body))
    story.append(Paragraph("Mwajuma has Tsh. 360,000 in the bank. She wants to take out Tsh. 106,000. But the bank also takes Tsh. 1,000 as a fee every time she takes money out.", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Calculate the total amount taken from her account.", step))
    story.append(Paragraph("Total deducted = Amount withdrawn + Bank charge", step))
    story.append(Paragraph("Total deducted = 106,000 + 1,000 = Tsh. 107,000", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Subtract from the original deposit.", step))
    story.append(Paragraph("Remaining = 360,000 - 107,000 = Tsh. 253,000", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Tsh. 253,000 remained in her account."))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) She makes a further withdrawal of Tsh. 50,000.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Again, add the bank charge to the withdrawal.", step))
    story.append(Paragraph("Total deducted = 50,000 + 1,000 = Tsh. 51,000", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Subtract from what was left.", step))
    story.append(Paragraph("Remaining = 253,000 - 51,000 = Tsh. 202,000", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Tsh. 202,000 remained after the second withdrawal."))
    story.append(S(6))

    story.append(warning_box("Do not forget the bank charge! Many students calculate 360,000 - 106,000 = 254,000 and forget to subtract the extra Tsh. 1,000 fee. The bank takes a fee EVERY time you withdraw."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Rewrite 2.4 recurring 3 as a mixed fraction.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("The number 2.43333... means the digit 3 repeats forever. Let us convert it step by step.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Let x = 2.43333...", step))
    story.append(Paragraph("<b>Step 2:</b> Multiply by 10 to move the non-repeating decimal:", step))
    story.append(Paragraph("10x = 24.3333...", step))
    story.append(Paragraph("<b>Step 3:</b> Multiply by 100:", step))
    story.append(Paragraph("100x = 243.3333...", step))
    story.append(Paragraph("<b>Step 4:</b> Subtract 10x from 100x to remove the repeating part:", step))
    story.append(Paragraph("100x - 10x = 243.3333... - 24.3333...", step))
    story.append(Paragraph("90x = 219", step))
    story.append(Paragraph("<b>Step 5:</b> Solve for x:", step))
    story.append(Paragraph("x = 219/90 = 73/30", step))
    story.append(Paragraph("<b>Step 6:</b> Convert to mixed fraction:", step))
    story.append(Paragraph("73 / 30 = 2 whole and 13/30", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: 2  13/30"))
    story.append(S(6))
    story.append(tip_box("To convert a recurring decimal to a fraction: (1) Let x = the number, (2) Multiply by powers of 10 to line up the repeating parts, (3) Subtract to eliminate the repeating digits."))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Bank transactions, recurring decimals, fractions. Study tip: Practice converting different types of recurring decimals to fractions."))
    story.append(PageBreak())

    # ========== QUESTION 2 ==========
    story.append(make_question_header(2, "Decimals, Rounding, and Unit Conversion", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a)(i) A dog, cat, and goat have masses 30.7 kg, 13.44 kg, and 18.26 kg. Calculate the total mass to the nearest whole number.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Add all three masses together:", step))
    story.append(Paragraph("30.7 + 13.44 + 18.26", step))
    story.append(Paragraph("= 30.70 + 13.44 + 18.26  (line up the decimal points)", step))
    story.append(Paragraph("= 62.40 kg", step))
    story.append(Paragraph("<b>Step 2:</b> Round to nearest whole number:", step))
    story.append(Paragraph("62.40 - look at the digit after the decimal point: 4. Since 4 is less than 5, we round down.", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: 62 kg"))
    story.append(S(6))

    story.append(Paragraph("<b>(a)(ii) Round off: dog to nearest ones, cat to one decimal place, goat to 3 significant figures.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Dog (30.7 kg to nearest ones):</b> Look at .7 - since 7 is 5 or more, round up: 31 kg", step))
    story.append(Paragraph("<b>Cat (13.44 kg to 1 decimal place):</b> Look at second decimal digit (4) - since 4 is less than 5, round down: 13.4 kg", step))
    story.append(Paragraph("<b>Goat (18.26 kg to 3 significant figures):</b> The first 3 significant figures are 1, 8, 2. Look at next digit (6) - since 6 is 5 or more, round up: 18.3 kg", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Dog = 31 kg, Cat = 13.4 kg, Goat = 18.3 kg"))
    story.append(S(6))

    story.append(warning_box("Significant figures are different from decimal places! Significant figures count from the first non-zero digit. For 18.26, the digits 1, 8, 2, 6 are all significant."))
    story.append(S(8))

    story.append(Paragraph("<b>(b)(i) Add the following units:</b>", sub))
    story.append(Paragraph("  km    m     mm", step))
    story.append(Paragraph("   8   799   400", step))
    story.append(Paragraph("+ 5   300   609", step))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Add millimetres: 400 + 609 = 1009 mm. Since 1000 mm = 1 m, we get 1 m and 9 mm. Carry 1 m.", step))
    story.append(Paragraph("<b>Step 2:</b> Add metres: 799 + 300 + 1 (carried) = 1100 m. Since 1000 m = 1 km, we get 1 km and 100 m. Carry 1 km.", step))
    story.append(Paragraph("<b>Step 3:</b> Add kilometres: 8 + 5 + 1 (carried) = 14 km.", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: 14 km  100 m  9 mm"))
    story.append(S(6))

    story.append(Paragraph("<b>(b)(ii) Convert the answer to metres.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("14 km = 14 x 1000 = 14,000 m", step))
    story.append(Paragraph("100 m = 100 m", step))
    story.append(Paragraph("9 mm = 9 / 1000 = 0.009 m", step))
    story.append(Paragraph("Total = 14,000 + 100 + 0.009 = 14,100.009 m", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: 14,100.009 metres"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Decimal addition, rounding, significant figures, unit conversion. Study tip: Always line up decimal points when adding and remember the conversion factors: 1 km = 1000 m, 1 m = 1000 mm."))
    story.append(PageBreak())

    # ========== QUESTION 3 ==========
    story.append(make_question_header(3, "Circle Properties and Area", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Draw a circle with center O and indicate: Arc AB, Chord CD, Sector AOB, Radius AO.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("Here are the definitions of each part of a circle:", body))
    story.append(S(4))
    story.append(Paragraph("<b>Arc AB:</b> An arc is a curved part of the circumference (the outside edge of the circle) between two points A and B. Think of it like a piece of string bent into a curve.", step))
    story.append(Paragraph("<b>Chord CD:</b> A chord is a straight line that connects two points on the circumference. It goes INSIDE the circle but does not pass through the center (unless it is a diameter).", step))
    story.append(Paragraph("<b>Sector AOB:</b> A sector is the 'pie slice' shape formed between two radii (OA and OB) and the arc AB. It looks like a slice of pizza!", step))
    story.append(Paragraph("<b>Radius AO:</b> The radius is a straight line from the center O to any point A on the circumference. All radii of the same circle are equal in length.", step))
    story.append(S(4))
    story.append(tip_box("Remember: Diameter = 2 x Radius. A chord that passes through the center is called a diameter. A sector is like a pizza slice, while a segment is like a piece cut by a chord."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Square carpet side = 14 m. Largest possible circular carpet is cut from it.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Area of the circular carpet:</b>", sub))
    story.append(Paragraph("The largest circle that fits inside a square has a diameter equal to the side of the square.", step))
    story.append(Paragraph("<b>Step 1:</b> Diameter = 14 m, so radius = 14/2 = 7 m.", step))
    story.append(Paragraph("<b>Step 2:</b> Use the formula for area of a circle:", step))
    story.append(Paragraph("Area = pi x r<super>2</super> = 22/7 x 7<super>2</super> = 22/7 x 49 = 22 x 7 = 154 m<super>2</super>", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Area of circular carpet = 154 m<super>2</super>"))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) Area of the remaining part:</b>", sub))
    story.append(Paragraph("<b>Step 1:</b> Area of square carpet = side x side = 14 x 14 = 196 m<super>2</super>", step))
    story.append(Paragraph("<b>Step 2:</b> Remaining area = Area of square - Area of circle = 196 - 154 = 42 m<super>2</super>", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Remaining area = 42 m<super>2</super>"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Circle properties (arc, chord, sector, radius), area of circle and square. Study tip: Use pi = 22/7 in NECTA exams unless told otherwise."))
    story.append(PageBreak())

    # ========== QUESTION 4 ==========
    story.append(make_question_header(4, "Simultaneous Equations and Quadratic Problems", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Solve by elimination: a/2 - b/5 = 1 and 3b = 24 + a</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Rewrite the first equation by removing fractions.", step))
    story.append(Paragraph("Multiply everything in a/2 - b/5 = 1 by 10 (the common denominator):", step))
    story.append(Paragraph("10 x a/2 - 10 x b/5 = 10 x 1", step))
    story.append(Paragraph("5a - 2b = 10 ... (equation 1)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Rewrite the second equation:", step))
    story.append(Paragraph("3b = 24 + a becomes: a - 3b = -24 ... (equation 2)", step))
    story.append(Paragraph("Or: a = 3b - 24", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Substitute a = 3b - 24 into equation 1:", step))
    story.append(Paragraph("5(3b - 24) - 2b = 10", step))
    story.append(Paragraph("15b - 120 - 2b = 10", step))
    story.append(Paragraph("13b = 130", step))
    story.append(Paragraph("b = 10", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Find a:", step))
    story.append(Paragraph("a = 3(10) - 24 = 30 - 24 = 6", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: a = 6, b = 10"))
    story.append(S(6))

    story.append(Paragraph("<b>(b) Length of book exceeds width by 5 cm. Area = 50 cm<super>2</super>. Find dimensions.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Let the width = w cm. Then length = (w + 5) cm.", step))
    story.append(Paragraph("<b>Step 2:</b> Area = length x width:", step))
    story.append(Paragraph("w(w + 5) = 50", step))
    story.append(Paragraph("w<super>2</super> + 5w = 50", step))
    story.append(Paragraph("w<super>2</super> + 5w - 50 = 0", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Factorize - find two numbers that multiply to give -50 and add to give 5:", step))
    story.append(Paragraph("Those numbers are +10 and -5.", step))
    story.append(Paragraph("(w + 10)(w - 5) = 0", step))
    story.append(Paragraph("w = -10 or w = 5", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> Width cannot be negative, so w = 5 cm.", step))
    story.append(Paragraph("Length = 5 + 5 = 10 cm.", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Width = 5 cm, Length = 10 cm"))
    story.append(S(6))
    story.append(warning_box("Always reject negative answers when solving for physical measurements like length, width, or age. A book cannot have a negative width!"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Simultaneous equations (elimination/substitution), quadratic equations from word problems. Study tip: When given fractions in equations, multiply through by the LCD first to remove fractions."))
    story.append(PageBreak())

    # ========== QUESTION 5 ==========
    story.append(make_question_header(5, "Ratio Problems and Simple Interest", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Asha and Juma received 630,000 shillings. Asha gets twice as much as Juma. How much did Asha receive?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Let Juma's share = x shillings.", step))
    story.append(Paragraph("Then Asha's share = 2x shillings (twice Juma's amount).", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Their total = 630,000:", step))
    story.append(Paragraph("x + 2x = 630,000", step))
    story.append(Paragraph("3x = 630,000", step))
    story.append(Paragraph("x = 210,000", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Asha received 2x = 2 x 210,000 = 420,000 shillings.", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Asha received Tsh. 420,000"))
    story.append(S(6))
    story.append(Paragraph("Quick check: 420,000 + 210,000 = 630,000. Correct!", step))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Mr. and Mrs. Juma deposited money at 3% simple interest. After 4 years, interest = 900,000 shillings.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Find the principal (amount deposited initially).</b>", sub))
    story.append(Paragraph("The formula for Simple Interest is:", step))
    story.append(Paragraph("Interest = (Principal x Rate x Time) / 100", step))
    story.append(Paragraph("900,000 = (P x 3 x 4) / 100", step))
    story.append(Paragraph("900,000 = 12P / 100", step))
    story.append(Paragraph("900,000 x 100 = 12P", step))
    story.append(Paragraph("90,000,000 = 12P", step))
    story.append(Paragraph("P = 90,000,000 / 12 = 7,500,000", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Principal = Tsh. 7,500,000"))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) Amount accumulated after 4 years:</b>", sub))
    story.append(Paragraph("Amount = Principal + Interest = 7,500,000 + 900,000 = 8,400,000", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Total amount = Tsh. 8,400,000"))
    story.append(S(6))
    story.append(tip_box("Simple Interest formula: I = PRT/100. Remember: P = Principal (starting money), R = Rate (percentage per year), T = Time (in years). Amount = Principal + Interest."))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Ratio and proportion, simple interest. Study tip: For ratio problems, let the smaller share be x and express everything in terms of x."))
    story.append(PageBreak())

    # ========== QUESTION 6 ==========
    story.append(make_question_header(6, "Linear Equations and Scale Drawing", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Line y = 3x - p passes through (6, 10) and (q, 22). Find p and q.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Substitute point (6, 10) into y = 3x - p:", step))
    story.append(Paragraph("10 = 3(6) - p", step))
    story.append(Paragraph("10 = 18 - p", step))
    story.append(Paragraph("p = 18 - 10 = 8", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Now the equation is y = 3x - 8. Substitute point (q, 22):", step))
    story.append(Paragraph("22 = 3q - 8", step))
    story.append(Paragraph("3q = 22 + 8 = 30", step))
    story.append(Paragraph("q = 10", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: p = 8, q = 10"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) A mason designs a room 500 cm by 200 cm.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Draw at scale 1:100.</b>", sub))
    story.append(Paragraph("Scale 1:100 means every 1 cm on paper = 100 cm in real life.", step))
    story.append(Paragraph("Length on paper = 500/100 = 5 cm", step))
    story.append(Paragraph("Width on paper = 200/100 = 2 cm", step))
    story.append(Paragraph("Draw a rectangle 5 cm by 2 cm on your paper.", step))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Calculate the actual area of the room:</b>", sub))
    story.append(Paragraph("Actual length = 500 cm = 5 m", step))
    story.append(Paragraph("Actual width = 200 cm = 2 m", step))
    story.append(Paragraph("Area = 5 x 2 = 10 m<super>2</super>", step))
    story.append(Paragraph("Or: 500 x 200 = 100,000 cm<super>2</super> = 10 m<super>2</super>", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Area of room = 10 m<super>2</super>"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Linear equations, substitution, scale drawing, area. Study tip: For scale drawings, divide actual measurements by the scale factor."))
    story.append(PageBreak())

    # ========== QUESTION 7 ==========
    story.append(make_question_header(7, "Surds and Change of Subject", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) P = sqrt(2) - 3 and Q = sqrt(2) + 1. Show that:</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) PQ = -1 - 2 sqrt(2)</b>", sub))
    story.append(Paragraph("<b>Step 1:</b> Multiply P and Q using FOIL (First, Outer, Inner, Last):", step))
    story.append(Paragraph("PQ = (sqrt(2) - 3)(sqrt(2) + 1)", step))
    story.append(Paragraph("= sqrt(2) x sqrt(2) + sqrt(2) x 1 + (-3) x sqrt(2) + (-3) x 1", step))
    story.append(Paragraph("= 2 + sqrt(2) - 3 sqrt(2) - 3", step))
    story.append(Paragraph("= (2 - 3) + (1 - 3) sqrt(2)", step))
    story.append(Paragraph("= -1 - 2 sqrt(2)  (as required)", step))
    story.append(S(4))
    story.append(answer_box("Shown: PQ = -1 - 2 sqrt(2)"))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) P/Q = 5 - 4 sqrt(2)</b>", sub))
    story.append(Paragraph("<b>Step 1:</b> Rationalize the denominator by multiplying top and bottom by (sqrt(2) - 1):", step))
    story.append(Paragraph("P/Q = (sqrt(2) - 3) / (sqrt(2) + 1) x (sqrt(2) - 1) / (sqrt(2) - 1)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Bottom: (sqrt(2) + 1)(sqrt(2) - 1) = 2 - 1 = 1", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Top: (sqrt(2) - 3)(sqrt(2) - 1)", step))
    story.append(Paragraph("= 2 - sqrt(2) - 3 sqrt(2) + 3", step))
    story.append(Paragraph("= 5 - 4 sqrt(2)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 4:</b> P/Q = (5 - 4 sqrt(2)) / 1 = 5 - 4 sqrt(2)", step))
    story.append(S(4))
    story.append(answer_box("Shown: P/Q = 5 - 4 sqrt(2)"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Express x in terms of p and q from p = sqrt(q + x). Find x when p = 3 and q = -1.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Square both sides to remove the square root:", step))
    story.append(Paragraph("p<super>2</super> = q + x", step))
    story.append(Paragraph("<b>Step 2:</b> Solve for x:", step))
    story.append(Paragraph("x = p<super>2</super> - q", step))
    story.append(Paragraph("<b>Step 3:</b> Substitute p = 3 and q = -1:", step))
    story.append(Paragraph("x = 3<super>2</super> - (-1) = 9 + 1 = 10", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: x = p<super>2</super> - q. When p = 3, q = -1: x = 10"))
    story.append(S(6))
    story.append(tip_box("When rationalizing a denominator with surds, multiply by the conjugate. If the denominator is (a + b), multiply by (a - b). This uses the difference of squares: (a+b)(a-b) = a<super>2</super> - b<super>2</super>."))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Surds, rationalization, change of subject. Study tip: FOIL method helps with multiplying two brackets."))
    story.append(PageBreak())

    # ========== QUESTION 8 ==========
    story.append(make_question_header(8, "Similar Triangles and Congruence", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) Building side view with similar triangles. FE (vertical wall), EN = 6 cm, NG = 18 cm, MN = 12 cm (perpendicular). Find FE.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Identify the similar triangles.", step))
    story.append(Paragraph("Triangle MNG and Triangle FEG are similar (AA similarity - both have right angles and share angle G).", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Set up the proportion using corresponding sides:", step))
    story.append(Paragraph("MN / FE = NG / EG", step))
    story.append(Paragraph("EG = EN + NG = 6 + 18 = 24 cm", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Substitute:", step))
    story.append(Paragraph("12 / FE = 18 / 24", step))
    story.append(Paragraph("12 / FE = 3/4", step))
    story.append(Paragraph("FE = 12 x 4/3 = 16 cm", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: FE = 16 cm"))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Triangles ABC and PQR. Angle C = 48 degrees, angle P = 48 degrees, angle R = 72 degrees.</b>", sub))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Why are triangles ABC and PQR congruent?</b>", sub))
    story.append(Paragraph("The triangles are congruent by the ASA (Angle-Side-Angle) condition:", step))
    story.append(Paragraph("- Angle C = Angle P = 48 degrees (corresponding angles are equal)", step))
    story.append(Paragraph("- The included sides are equal (given from the figure)", step))
    story.append(Paragraph("- The other corresponding angles are also equal", step))
    story.append(Paragraph("Therefore Triangle ABC is congruent to Triangle PQR.", step))
    story.append(S(6))

    story.append(Paragraph("<b>(ii) Calculate angle RQP:</b>", sub))
    story.append(Paragraph("In any triangle, the sum of all angles = 180 degrees.", step))
    story.append(Paragraph("In triangle PQR:", step))
    story.append(Paragraph("Angle P + Angle Q + Angle R = 180 degrees", step))
    story.append(Paragraph("48 + Angle Q + 72 = 180", step))
    story.append(Paragraph("Angle Q = 180 - 48 - 72 = 60 degrees", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Angle RQP = 60 degrees"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Similar triangles, congruent triangles, ASA/SAS/SSS. Study tip: For similar triangles, corresponding sides are in proportion. For congruent triangles, corresponding sides and angles are equal."))
    story.append(PageBreak())

    # ========== QUESTION 9 ==========
    story.append(make_question_header(9, "Pythagoras Theorem and Diagonal", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) A photograph with diagonal 7.8 cm. Frame is 6 cm x 5 cm. Will the photo fit?</b>", sub))
    story.append(S(4))
    story.append(Paragraph("To check if the photo fits, we need to find the diagonal of the frame and compare.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Use Pythagoras theorem to find the frame's diagonal:", step))
    story.append(Paragraph("The formula is: diagonal<super>2</super> = length<super>2</super> + width<super>2</super>", step))
    story.append(Paragraph("diagonal<super>2</super> = 6<super>2</super> + 5<super>2</super> = 36 + 25 = 61", step))
    story.append(Paragraph("diagonal = sqrt(61) = 7.81 cm (approximately)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Compare:", step))
    story.append(Paragraph("Photo diagonal = 7.8 cm", step))
    story.append(Paragraph("Frame diagonal = 7.81 cm", step))
    story.append(Paragraph("Since 7.8 &lt; 7.81, the photograph WILL fit in the frame (just barely).", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Yes, the photograph will fit in the frame. Frame diagonal (7.81 cm) is greater than photo diagonal (7.8 cm)."))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Square tile with diagonal 8 cm, angle 45 degrees. Find the side length.</b>", sub))
    story.append(S(4))
    story.append(Paragraph("In a square, the diagonal divides it into two right-angled triangles with 45-45-90 angles.", body))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> The formula relating diagonal and side of a square is:", step))
    story.append(Paragraph("diagonal = side x sqrt(2)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Solve for side:", step))
    story.append(Paragraph("side = diagonal / sqrt(2) = 8 / sqrt(2)", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 3:</b> Rationalize:", step))
    story.append(Paragraph("side = 8 / sqrt(2) x sqrt(2) / sqrt(2) = 8 sqrt(2) / 2 = 4 sqrt(2)", step))
    story.append(Paragraph("side = 4 x 1.414 = 5.66 cm (approximately)", step))
    story.append(S(4))
    story.append(answer_box("Final Answer: Side of tile = 4 sqrt(2) cm (approximately 5.66 cm)"))
    story.append(S(6))
    story.append(tip_box("In a 45-45-90 triangle: if each leg = a, then hypotenuse = a x sqrt(2). This comes from Pythagoras: a<super>2</super> + a<super>2</super> = c<super>2</super>, so c = a x sqrt(2)."))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Pythagoras theorem, diagonals, square properties. Study tip: For squares, diagonal = side x sqrt(2). For rectangles, diagonal<super>2</super> = length<super>2</super> + width<super>2</super>."))
    story.append(PageBreak())

    # ========== QUESTION 10 ==========
    story.append(make_question_header(10, "Venn Diagrams and Statistics", styles))
    story.append(S(8))

    story.append(Paragraph("<b>(a) In a village of 1500 villagers, 600 keep goats, 700 keep cows, 300 keep neither. Use Venn diagram to find:</b>", sub))
    story.append(S(4))
    story.append(Paragraph("<b>Step 1:</b> Find how many keep at least one animal:", step))
    story.append(Paragraph("Total - Neither = 1500 - 300 = 1200 villagers keep at least one animal.", step))
    story.append(S(2))
    story.append(Paragraph("<b>Step 2:</b> Use the Venn diagram formula:", step))
    story.append(Paragraph("n(Goats or Cows) = n(Goats) + n(Cows) - n(Both)", step))
    story.append(Paragraph("1200 = 600 + 700 - n(Both)", step))
    story.append(Paragraph("n(Both) = 1300 - 1200 = 100", step))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Both goats and cows = 100</b>", step))
    story.append(Paragraph("<b>(ii) Goats only = 600 - 100 = 500</b>", step))
    story.append(Paragraph("<b>(iii) Cows only = 700 - 100 = 600</b>", step))
    story.append(Paragraph("<b>(iv) Goats or cows = 1200</b>", step))
    story.append(S(4))
    story.append(answer_box("Final Answers: (i) Both = 100, (ii) Goats only = 500, (iii) Cows only = 600, (iv) Goats or cows = 1200"))
    story.append(S(6))
    story.append(Paragraph("Quick check: 500 + 100 + 600 + 300 = 1500. This matches the total! Correct!", step))
    story.append(S(8))

    story.append(Paragraph("<b>(b) Math test grades for 100 students:</b>", sub))
    story.append(Paragraph("Marks: 50-59 (3 students), 60-69 (21), 70-79 (32), 80-89 (27), 90-99 (17)", step))
    story.append(S(4))

    story.append(Paragraph("<b>(i) Class interval size:</b>", sub))
    story.append(Paragraph("Class interval = Upper boundary - Lower boundary + 1 = 59 - 50 + 1 = 10", step))
    story.append(answer_box("Answer: Class interval size = 10"))
    story.append(S(4))

    story.append(Paragraph("<b>(ii) Highest frequency class:</b>", sub))
    story.append(Paragraph("The class 70-79 has 32 students, which is the highest number.", step))
    story.append(answer_box("Answer: 70 - 79 (with 32 students)"))
    story.append(S(4))

    story.append(Paragraph("<b>(iii) Class mark of highest class interval:</b>", sub))
    story.append(Paragraph("Class mark = (Lower + Upper) / 2 = (70 + 79) / 2 = 149 / 2 = 74.5", step))
    story.append(answer_box("Answer: Class mark = 74.5"))
    story.append(S(4))

    story.append(Paragraph("<b>(iv) Number who passed (pass mark = 70):</b>", sub))
    story.append(Paragraph("Students who scored 70 or above: 32 + 27 + 17 = 76 students", step))
    story.append(answer_box("Answer: 76 students passed"))
    story.append(S(4))

    story.append(Paragraph("<b>(v) Number who failed:</b>", sub))
    story.append(Paragraph("Failed = Total - Passed = 100 - 76 = 24 students", step))
    story.append(answer_box("Answer: 24 students failed"))
    story.append(S(6))
    story.append(section_summary("Total marks: 10. Key topics: Venn diagrams, frequency distribution, class intervals. Study tip: Always check your Venn diagram totals add up to the given total. Class mark = (lower + upper boundaries) / 2."))
    story.append(PageBreak())

    # ========== CLOSING PAGE ==========
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
