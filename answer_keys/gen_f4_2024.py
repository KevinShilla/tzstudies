"""
Generate BasicMath Form 4 2024 NECTA Answer Key PDF
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
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BasicMath-F4-2024 (Answer Key).pdf")


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


def warn(text):
    return _box("Common Mistake Warning", text, WARNING_BG, WARNING_BORDER, HexColor("#e65100"), HexColor("#bf360c"))


def tip(text):
    return _box("Study Tip", text, TIP_BG, TIP_BORDER, HexColor("#0d47a1"), HexColor("#1565c0"))


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


S = Spacer


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        topMargin=30, bottomMargin=40, leftMargin=40, rightMargin=40
    )
    styles = build_styles()
    story = []

    # ── COVER PAGE ──
    story.append(S(1, 60))
    story.append(Paragraph("myTZStudies", styles['CoverTitle']))
    story.append(S(1, 4))
    story.append(Paragraph("Your Free Tanzanian Exam Library", styles['CoverSubtitle']))
    story.append(S(1, 10))
    story.append(HRFlowable(width="80%", thickness=2, color=DARK_BLUE, spaceAfter=10, spaceBefore=5))
    story.append(S(1, 6))
    story.append(Paragraph("Past papers, answer keys, and study resources for Tanzanian students.", styles['CoverTagline']))
    story.append(S(1, 10))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(1, 30))
    fs = ParagraphStyle('FI', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE, alignment=TA_CENTER)
    feats = ["Past Exam Papers", "Answer Keys", "Free Access", "Standard 4 to Form 6", "All Subjects Covered", "Updated Regularly"]
    cw = (WIDTH - 80) / 3
    ft = Table([[Paragraph(f, fs) for f in feats[:3]], [Paragraph(f, fs) for f in feats[3:]]], colWidths=[cw] * 3, rowHeights=[45, 45])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG),
        ('BOX', (0, 0), (0, 0), 1, BORDER_GRAY), ('BOX', (1, 0), (1, 0), 1, BORDER_GRAY), ('BOX', (2, 0), (2, 0), 1, BORDER_GRAY),
        ('BOX', (0, 1), (0, 1), 1, BORDER_GRAY), ('BOX', (1, 1), (1, 1), 1, BORDER_GRAY), ('BOX', (2, 1), (2, 1), 1, BORDER_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
    ]))
    story.append(ft)
    story.append(S(1, 40))
    story.append(Paragraph("Share this with a friend. Every student deserves free study materials.", styles['CoverShare']))
    story.append(S(1, 10))
    story.append(HRFlowable(width="60%", thickness=0.5, color=BORDER_GRAY, spaceAfter=10))
    story.append(Paragraph("Made with mytzstudies.com", styles['CoverFooter']))
    story.append(PageBreak())

    # ── TITLE PAGE ──
    story.append(S(1, 60))
    story.append(Paragraph("BASIC MATHEMATICS - FORM FOUR", styles['TitlePageHeading']))
    story.append(S(1, 6))
    story.append(Paragraph("National Examination 2024 - Answer Key", styles['TitlePageSub']))
    story.append(S(1, 20))
    story.append(HRFlowable(width="60%", thickness=1, color=DARK_BLUE, spaceAfter=20, spaceBefore=5))
    info_style = ParagraphStyle('Info', fontName='Helvetica', fontSize=11, textColor=HexColor("#333333"), leading=15)
    info_bold = ParagraphStyle('InfoB', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE, leading=15)
    info_data = [
        ["Subject", "Basic Mathematics"],
        ["Code", "041"],
        ["Level", "Form Four"],
        ["Year", "2024"],
        ["Exam Board", "NECTA"],
        ["Type", "Answer Key"],
        ["Total Questions", "14 (Section A: 6 marks each, Section B: 10 marks each)"],
    ]
    info_table_data = [[Paragraph(r[0], info_bold), Paragraph(r[1], info_style)] for r in info_data]
    it = Table(info_table_data, colWidths=[150, 320])
    it.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(it)
    story.append(S(1, 30))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(PageBreak())

    # ── SECTION A HEADER ──
    sec_a_data = [[Paragraph("<b>SECTION A (60 Marks)</b><br/>Answer ALL questions. Each question carries 6 marks.", ParagraphStyle('SA', fontName='Helvetica-Bold', fontSize=14, textColor=white, alignment=TA_CENTER, leading=20))]]
    sec_a = Table(sec_a_data, colWidths=[WIDTH - 80])
    sec_a.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
    story.append(sec_a)
    story.append(S(1, 10))

    # ────────────────────────────────────────────────────────────────
    # QUESTION 1: GCF and Percentages
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(1, "GCF and Percentages", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) Find the size of the largest square that can be drawn on a rectangular board measuring 54 cm by 78 cm.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("To find the largest square, we need the Greatest Common Factor (GCF) of 54 and 78.", styles['BodyText2']))
    story.append(Paragraph("<b>Step 1:</b> Find the prime factorisation of each number.", styles['StepText']))
    story.append(Paragraph("54 = 2 x 3 x 3 x 3 = 2 x 3<super>3</super>", styles['StepText']))
    story.append(Paragraph("78 = 2 x 3 x 13", styles['StepText']))
    story.append(Paragraph("<b>Step 2:</b> Pick the common prime factors with the smallest powers.", styles['StepText']))
    story.append(Paragraph("Common factors: 2 and 3", styles['StepText']))
    story.append(Paragraph("GCF = 2 x 3 = 6", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Each square is 6 cm x 6 cm"))
    story.append(S(1, 6))
    story.append(tip("The GCF tells us the largest size that divides both dimensions exactly. The board can be covered by (54/6) x (78/6) = 9 x 13 = 117 squares."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) A class has 40 students, 17 are boys and the rest are girls.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Number of girls = 40 - 17 = 23", styles['StepText']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Express the number of boys in decimal:</b>", styles['StepText']))
    story.append(Paragraph("Boys as a fraction = 17/40", styles['StepText']))
    story.append(Paragraph("17 / 40 = 0.425", styles['StepText']))
    story.append(ans("Number of boys in decimal = 0.425"))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(ii) What percentage are girls? What percentage are boys?</b>", styles['StepText']))
    story.append(Paragraph("Percentage of girls = (23/40) x 100 = 57.5%", styles['StepText']))
    story.append(Paragraph("Percentage of boys = (17/40) x 100 = 42.5%", styles['StepText']))
    story.append(ans("Percentage of girls = 57.5%<br/>Percentage of boys = 42.5%"))
    story.append(S(1, 6))
    story.append(warn("Always check that percentages add up to 100%. Here 57.5% + 42.5% = 100%. If they do not add up, go back and check your working."))
    story.append(S(1, 6))
    story.append(summary("GCF is found by taking the product of common prime factors with the smallest powers. To convert a fraction to a decimal, divide the numerator by the denominator. To convert to a percentage, multiply by 100."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 2: Surds and Logarithms
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(2, "Surds and Logarithms", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) Express (3 + &#x221A;7) / (5 + &#x221A;7) in a simplified surd form.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Rationalise the denominator by multiplying top and bottom by the conjugate (5 - &#x221A;7).", styles['StepText']))
    story.append(Paragraph("= (3 + &#x221A;7)(5 - &#x221A;7) / (5 + &#x221A;7)(5 - &#x221A;7)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Expand the numerator.", styles['StepText']))
    story.append(Paragraph("= (3)(5) + (3)(-&#x221A;7) + (&#x221A;7)(5) + (&#x221A;7)(-&#x221A;7)", styles['StepText']))
    story.append(Paragraph("= 15 - 3&#x221A;7 + 5&#x221A;7 - 7", styles['StepText']))
    story.append(Paragraph("= 8 + 2&#x221A;7", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Expand the denominator using the difference of squares.", styles['StepText']))
    story.append(Paragraph("= 5<super>2</super> - (&#x221A;7)<super>2</super> = 25 - 7 = 18", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 4:</b> Simplify the fraction.", styles['StepText']))
    story.append(Paragraph("= (8 + 2&#x221A;7) / 18 = 2(4 + &#x221A;7) / 18 = (4 + &#x221A;7) / 9", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("(4 + &#x221A;7) / 9 &nbsp; or equivalently &nbsp; 4/9 + (&#x221A;7)/9"))
    story.append(S(1, 6))
    story.append(tip("To rationalise a denominator of the form (a + &#x221A;b), multiply top and bottom by (a - &#x221A;b). This uses the difference of squares: (a + &#x221A;b)(a - &#x221A;b) = a<super>2</super> - b."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Solve: 4 + log<sub>3</sub> x = log<sub>3</sub> 24. Find x without using a calculator.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Isolate the logarithm with x.", styles['StepText']))
    story.append(Paragraph("log<sub>3</sub> x = log<sub>3</sub> 24 - 4", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Write 4 as a logarithm in base 3.", styles['StepText']))
    story.append(Paragraph("4 = log<sub>3</sub> 3<super>4</super> = log<sub>3</sub> 81", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Combine using the subtraction rule.", styles['StepText']))
    story.append(Paragraph("log<sub>3</sub> x = log<sub>3</sub> 24 - log<sub>3</sub> 81 = log<sub>3</sub> (24/81)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 4:</b> Simplify the fraction.", styles['StepText']))
    story.append(Paragraph("24/81 = 8/27", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 5:</b> Since log<sub>3</sub> x = log<sub>3</sub> (8/27), we get:", styles['StepText']))
    story.append(Paragraph("x = 8/27", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("x = 8/27"))
    story.append(S(1, 6))
    story.append(warn("Remember: log<sub>a</sub> M - log<sub>a</sub> N = log<sub>a</sub> (M/N). Also, any constant c can be written as log<sub>a</sub>(a<super>c</super>). Do not mix up these rules."))
    story.append(S(1, 6))
    story.append(summary("Rationalise surds by multiplying by the conjugate. For logarithm equations, convert constants to log form and use subtraction/addition rules to combine."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 3: Sets and Probability
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(3, "Sets and Probability", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) A school has 100 students. 45 prefer Music, 40 prefer Theatre Arts, and 5 prefer both. How many prefer none?</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Use the union formula.", styles['StepText']))
    story.append(Paragraph("n(M &#x222A; T) = n(M) + n(T) - n(M &#x2229; T)", styles['StepText']))
    story.append(Paragraph("n(M &#x222A; T) = 45 + 40 - 5 = 80", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Students who prefer none = Total - n(M &#x222A; T).", styles['StepText']))
    story.append(Paragraph("= 100 - 80 = 20", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("20 students prefer neither Music nor Theatre Arts"))
    story.append(S(1, 6))
    story.append(warn("Always subtract the intersection to avoid double counting students who like both."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Offices have tables as shown:</b>", styles['SubPart']))
    story.append(S(1, 4))
    # Frequency table
    hdr_s = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)
    cell_s = ParagraphStyle('TC', fontName='Helvetica', fontSize=10, textColor=HexColor("#222222"), alignment=TA_CENTER)
    freq_data = [
        [Paragraph("No. of Tables", hdr_s), Paragraph("1", hdr_s), Paragraph("2", hdr_s), Paragraph("3", hdr_s), Paragraph("4", hdr_s), Paragraph("5", hdr_s), Paragraph("6", hdr_s)],
        [Paragraph("No. of Offices", cell_s), Paragraph("2", cell_s), Paragraph("5", cell_s), Paragraph("6", cell_s), Paragraph("3", cell_s), Paragraph("2", cell_s), Paragraph("2", cell_s)],
    ]
    freq_t = Table(freq_data, colWidths=[100] + [55] * 6)
    freq_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(freq_t)
    story.append(S(1, 4))
    story.append(Paragraph("Total offices = 2 + 5 + 6 + 3 + 2 + 2 = 20", styles['StepText']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Probability that an office has 2 tables:</b>", styles['StepText']))
    story.append(Paragraph("P(2 tables) = 5/20 = 1/4", styles['StepText']))
    story.append(ans("P(2 tables) = 1/4 = 0.25"))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(ii) Probability that an office has at least 5 tables:</b>", styles['StepText']))
    story.append(Paragraph("Offices with 5 tables = 2, offices with 6 tables = 2", styles['StepText']))
    story.append(Paragraph("P(at least 5) = (2 + 2)/20 = 4/20 = 1/5", styles['StepText']))
    story.append(ans("P(at least 5 tables) = 1/5 = 0.2"))
    story.append(S(1, 6))
    story.append(tip("'At least 5' means 5 or more. Add up the frequencies for 5 and 6."))
    story.append(S(1, 6))
    story.append(summary("For sets, use n(A &#x222A; B) = n(A) + n(B) - n(A &#x2229; B). For probability, P(event) = favourable outcomes / total outcomes."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 4: Vectors
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(4, "Vectors and Parallel Lines", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) Given A(6, -4), B(8, 4), P(6, 1), Q(7, 5). Determine if AB is parallel to PQ.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Find vector AB.", styles['StepText']))
    story.append(Paragraph("AB = B - A = (8 - 6, 4 - (-4)) = (2, 8)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Find vector PQ.", styles['StepText']))
    story.append(Paragraph("PQ = Q - P = (7 - 6, 5 - 1) = (1, 4)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Check if one is a scalar multiple of the other.", styles['StepText']))
    story.append(Paragraph("AB = (2, 8) = 2 x (1, 4) = 2 x PQ", styles['StepText']))
    story.append(Paragraph("Since AB = 2PQ, the vectors are scalar multiples of each other.", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("AB is parallel to PQ (AB = 2PQ)"))
    story.append(S(1, 6))
    story.append(tip("Two vectors are parallel if one is a scalar multiple of the other, i.e., (a, b) = k(c, d) for some constant k. Check that a/c = b/d."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Given a = 2i - 7j and 2a + 3b = 13i - 2j. Find b.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Substitute a into the equation.", styles['StepText']))
    story.append(Paragraph("2(2i - 7j) + 3b = 13i - 2j", styles['StepText']))
    story.append(Paragraph("4i - 14j + 3b = 13i - 2j", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Isolate 3b.", styles['StepText']))
    story.append(Paragraph("3b = (13i - 2j) - (4i - 14j)", styles['StepText']))
    story.append(Paragraph("3b = (13 - 4)i + (-2 + 14)j", styles['StepText']))
    story.append(Paragraph("3b = 9i + 12j", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Divide by 3.", styles['StepText']))
    story.append(Paragraph("b = 3i + 4j", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("b = 3i + 4j"))
    story.append(S(1, 6))
    story.append(warn("When subtracting vectors, be careful with signs. Subtracting a negative gives a positive: -2 - (-14) = -2 + 14 = 12."))
    story.append(S(1, 6))
    story.append(summary("Vectors are parallel if one is a scalar multiple of the other. To solve vector equations, substitute known vectors and solve for each component (i and j) separately."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 5: Hexagon Area and Similar Triangles
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(5, "Regular Hexagon and Similar Triangles", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) A regular hexagon inscribed in a circle of radius r has area 720 m<super>2</super>. Find r, rounded to the nearest (i) tenth (ii) ten.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Use the formula for the area of a regular hexagon.", styles['StepText']))
    story.append(Paragraph("Area = (3&#x221A;3 / 2) x r<super>2</super>", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Set up the equation.", styles['StepText']))
    story.append(Paragraph("(3&#x221A;3 / 2) x r<super>2</super> = 720", styles['StepText']))
    story.append(Paragraph("r<super>2</super> = 720 x 2 / (3&#x221A;3) = 1440 / (3&#x221A;3)", styles['StepText']))
    story.append(Paragraph("r<super>2</super> = 480 / &#x221A;3 = 480&#x221A;3 / 3 = 160&#x221A;3", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Calculate.", styles['StepText']))
    story.append(Paragraph("r<super>2</super> = 160 x 1.7321 = 277.13", styles['StepText']))
    story.append(Paragraph("r = &#x221A;277.13 = 16.647...", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("(i) To the nearest tenth: r = 16.6 m<br/>(ii) To the nearest ten: r = 20 m"))
    story.append(S(1, 6))
    story.append(tip("A regular hexagon with circumradius r is made of 6 equilateral triangles, each with side r. Area of one equilateral triangle = (&#x221A;3/4)r<super>2</super>, so total = 6 x (&#x221A;3/4)r<super>2</super> = (3&#x221A;3/2)r<super>2</super>."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Triangles AEB and CDE share vertex E. AE = 36 m, BE = 24 m, AB = 36 m.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Prove that triangles AEB and CDE are similar:</b>", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("1. Angle AEB = Angle CED (vertically opposite angles at E).", styles['StepText']))
    story.append(Paragraph("2. The sides of the two triangles are in the same ratio (proportional).", styles['StepText']))
    story.append(Paragraph("3. By the AA (Angle-Angle) similarity criterion, triangle AEB is similar to triangle CDE.", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Triangles AEB and CDE are similar (AA similarity: vertically opposite angles at E and proportional sides)."))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) Find CD.</b>", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("From the similar triangles: AE/CE = BE/DE = AB/CD", styles['StepText']))
    story.append(Paragraph("Given: AE = 36, BE = 24, CE = 24, DE = 16 (from figure).", styles['StepText']))
    story.append(Paragraph("Scale factor = CE/AE = 24/36 = 2/3", styles['StepText']))
    story.append(Paragraph("CD/AB = 2/3, so CD = (2/3) x 36 = 24 m", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("CD = 24 m"))
    story.append(S(1, 6))
    story.append(summary("For regular hexagons, Area = (3&#x221A;3/2)r<super>2</super>. For similar triangles, corresponding sides are proportional and corresponding angles are equal."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 6: Variation and Volume
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(6, "Inverse Variation and Volume", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) Time t varies inversely with speed v. She takes 30 minutes at 10 m/s.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Write the equation connecting t and v.</b>", styles['StepText']))
    story.append(Paragraph("Since t varies inversely with v: t = k/v", styles['StepText']))
    story.append(Paragraph("Convert 30 minutes to seconds: 30 x 60 = 1800 s", styles['StepText']))
    story.append(Paragraph("Substitute: 1800 = k/10", styles['StepText']))
    story.append(Paragraph("k = 1800 x 10 = 18,000", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Equation: t = 18,000/v (where t is in seconds and v is in m/s)"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) Find the speed needed to get home in 15 minutes.</b>", styles['StepText']))
    story.append(Paragraph("Convert 15 minutes to seconds: 15 x 60 = 900 s", styles['StepText']))
    story.append(Paragraph("900 = 18,000/v", styles['StepText']))
    story.append(Paragraph("v = 18,000/900 = 20 m/s", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Speed = 20 m/s"))
    story.append(S(1, 6))
    story.append(tip("Inverse variation means when one quantity increases, the other decreases. The product t x v is always constant (= k). So doubling the speed halves the time."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) A container collects 850 ml of rain per minute. Rain falls from 8:10 am to 11:52 am. Find the total water collected in litres.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Find the duration of rain.", styles['StepText']))
    story.append(Paragraph("From 8:10 am to 11:52 am = 3 hours 42 minutes = 222 minutes", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Calculate total volume.", styles['StepText']))
    story.append(Paragraph("Total = 222 x 850 ml = 188,700 ml", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Convert to litres.", styles['StepText']))
    story.append(Paragraph("188,700 ml / 1000 = 188.7 litres", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Total water collected = 188.7 litres"))
    story.append(S(1, 6))
    story.append(warn("Be careful when calculating the time difference. From 8:10 to 11:10 is 3 hours (180 min), then from 11:10 to 11:52 is 42 more minutes. Total = 222 minutes."))
    story.append(S(1, 6))
    story.append(summary("For inverse variation, t = k/v. To find k, substitute known values. Remember: 1 litre = 1000 ml."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 7: Ratio of Ages
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(7, "Ratio of Ages", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>The ratio of the sum of ages to the difference of ages of Amina and Bakari is 5:4. Find the ratio of their ages.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Let the ages of Amina and Bakari be <b>a</b> and <b>b</b> (where a &gt; b).", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 1:</b> Set up the equation from the ratio.", styles['StepText']))
    story.append(Paragraph("(a + b) / (a - b) = 5/4", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Cross-multiply.", styles['StepText']))
    story.append(Paragraph("4(a + b) = 5(a - b)", styles['StepText']))
    story.append(Paragraph("4a + 4b = 5a - 5b", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Solve for the ratio a/b.", styles['StepText']))
    story.append(Paragraph("4b + 5b = 5a - 4a", styles['StepText']))
    story.append(Paragraph("9b = a", styles['StepText']))
    story.append(Paragraph("a/b = 9/1", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("The ratio of Amina's age to Bakari's age is 9 : 1"))
    story.append(S(1, 6))
    story.append(tip("When the ratio of (sum) to (difference) is given, cross-multiply and rearrange to find the ratio of the individual quantities."))
    story.append(S(1, 6))
    story.append(summary("If (a+b):(a-b) = m:n, then cross-multiply to get n(a+b) = m(a-b), and solve for a:b."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 8: Cash Account and Trial Balance
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(8, "Cash Account and Trial Balance", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>From the following transactions, prepare a Cash Account and Trial Balance.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Transactions:<br/>"
                            "July 1: Started business with capital Tsh 1,000,000<br/>"
                            "July 2: Cash sales Tsh 500,000<br/>"
                            "July 2: Cash purchases Tsh 300,000<br/>"
                            "July 10: Cash sales Tsh 310,000<br/>"
                            "July 15: Cash purchases Tsh 700,000<br/>"
                            "July 20: Paid wages Tsh 55,000<br/>"
                            "July 25: Paid rent Tsh 10,000", styles['BodyText2']))
    story.append(S(1, 6))

    # Cash Account Table
    story.append(Paragraph("<b>Cash Account (Tsh)</b>", styles['SubPart']))
    story.append(S(1, 4))
    ca_hdr = ParagraphStyle('CAH', fontName='Helvetica-Bold', fontSize=9, textColor=white, alignment=TA_CENTER)
    ca_cell = ParagraphStyle('CAC', fontName='Helvetica', fontSize=9, textColor=HexColor("#222222"), alignment=TA_CENTER)
    ca_cellb = ParagraphStyle('CACB', fontName='Helvetica-Bold', fontSize=9, textColor=HexColor("#222222"), alignment=TA_CENTER)
    ca_data = [
        [Paragraph("Date", ca_hdr), Paragraph("Details", ca_hdr), Paragraph("Amount", ca_hdr),
         Paragraph("Date", ca_hdr), Paragraph("Details", ca_hdr), Paragraph("Amount", ca_hdr)],
        [Paragraph("July 1", ca_cell), Paragraph("Capital", ca_cell), Paragraph("1,000,000", ca_cell),
         Paragraph("July 2", ca_cell), Paragraph("Purchases", ca_cell), Paragraph("300,000", ca_cell)],
        [Paragraph("July 2", ca_cell), Paragraph("Sales", ca_cell), Paragraph("500,000", ca_cell),
         Paragraph("July 15", ca_cell), Paragraph("Purchases", ca_cell), Paragraph("700,000", ca_cell)],
        [Paragraph("July 10", ca_cell), Paragraph("Sales", ca_cell), Paragraph("310,000", ca_cell),
         Paragraph("July 20", ca_cell), Paragraph("Wages", ca_cell), Paragraph("55,000", ca_cell)],
        [Paragraph("", ca_cell), Paragraph("", ca_cell), Paragraph("", ca_cell),
         Paragraph("July 25", ca_cell), Paragraph("Rent", ca_cell), Paragraph("10,000", ca_cell)],
        [Paragraph("", ca_cell), Paragraph("", ca_cell), Paragraph("", ca_cell),
         Paragraph("July 31", ca_cell), Paragraph("Balance c/d", ca_cell), Paragraph("745,000", ca_cell)],
        [Paragraph("", ca_cellb), Paragraph("Total", ca_cellb), Paragraph("1,810,000", ca_cellb),
         Paragraph("", ca_cellb), Paragraph("Total", ca_cellb), Paragraph("1,810,000", ca_cellb)],
        [Paragraph("Aug 1", ca_cell), Paragraph("Balance b/d", ca_cell), Paragraph("745,000", ca_cell),
         Paragraph("", ca_cell), Paragraph("", ca_cell), Paragraph("", ca_cell)],
    ]
    ca_t = Table(ca_data, colWidths=[55, 70, 80, 55, 70, 80])
    ca_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('BACKGROUND', (0, 6), (-1, 6), LIGHT_BLUE_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 6), (-1, 6), 1.5, black),
        ('LINEBELOW', (0, 6), (-1, 6), 1.5, black),
    ]))
    story.append(ca_t)
    story.append(S(1, 4))
    story.append(Paragraph("Balance c/d = 1,810,000 - (300,000 + 700,000 + 55,000 + 10,000) = 1,810,000 - 1,065,000 = 745,000", styles['StepText']))
    story.append(S(1, 8))

    # Trial Balance
    story.append(Paragraph("<b>Trial Balance as at 31 July (Tsh)</b>", styles['SubPart']))
    story.append(S(1, 4))
    tb_data = [
        [Paragraph("Account", ca_hdr), Paragraph("Debit (Tsh)", ca_hdr), Paragraph("Credit (Tsh)", ca_hdr)],
        [Paragraph("Cash", ca_cell), Paragraph("745,000", ca_cell), Paragraph("", ca_cell)],
        [Paragraph("Capital", ca_cell), Paragraph("", ca_cell), Paragraph("1,000,000", ca_cell)],
        [Paragraph("Sales", ca_cell), Paragraph("", ca_cell), Paragraph("810,000", ca_cell)],
        [Paragraph("Purchases", ca_cell), Paragraph("1,000,000", ca_cell), Paragraph("", ca_cell)],
        [Paragraph("Wages", ca_cell), Paragraph("55,000", ca_cell), Paragraph("", ca_cell)],
        [Paragraph("Rent", ca_cell), Paragraph("10,000", ca_cell), Paragraph("", ca_cell)],
        [Paragraph("Total", ca_cellb), Paragraph("1,810,000", ca_cellb), Paragraph("1,810,000", ca_cellb)],
    ]
    tb_t = Table(tb_data, colWidths=[140, 120, 120])
    tb_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('BACKGROUND', (0, 7), (-1, 7), LIGHT_BLUE_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 7), (-1, 7), 1.5, black),
        ('LINEBELOW', (0, 7), (-1, 7), 1.5, black),
    ]))
    story.append(tb_t)
    story.append(S(1, 6))
    story.append(ans("Trial Balance totals: Debit = Tsh 1,810,000, Credit = Tsh 1,810,000 (balanced)"))
    story.append(S(1, 6))
    story.append(warn("In a trial balance, the total debits must equal the total credits. If they do not, there is an error in your entries."))
    story.append(S(1, 6))
    story.append(summary("Cash account records all cash receipts (debit side) and cash payments (credit side). The trial balance checks that total debits equal total credits."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 9: Arithmetic Progression (Loan)
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(9, "Arithmetic Progression - Loan Repayment", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>An entrepreneur repays a loan monthly: Tsh 20,000 in the first month, Tsh 22,000 in the second, Tsh 24,000 in the third, and so on. The final installment is Tsh 114,000.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("This is an Arithmetic Progression (AP) with:", styles['BodyText2']))
    story.append(Paragraph("First term (a) = 20,000", styles['StepText']))
    story.append(Paragraph("Common difference (d) = 22,000 - 20,000 = 2,000", styles['StepText']))
    story.append(Paragraph("Last term (l) = 114,000", styles['StepText']))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(i) Find the number of months (n).</b>", styles['StepText']))
    story.append(Paragraph("Using: l = a + (n - 1)d", styles['StepText']))
    story.append(Paragraph("114,000 = 20,000 + (n - 1)(2,000)", styles['StepText']))
    story.append(Paragraph("114,000 - 20,000 = (n - 1)(2,000)", styles['StepText']))
    story.append(Paragraph("94,000 = (n - 1)(2,000)", styles['StepText']))
    story.append(Paragraph("n - 1 = 94,000 / 2,000 = 47", styles['StepText']))
    story.append(Paragraph("n = 48", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Number of months = 48"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) Find the total loan amount.</b>", styles['StepText']))
    story.append(Paragraph("Sum of AP: S = (n/2)(first + last)", styles['StepText']))
    story.append(Paragraph("S = (48/2)(20,000 + 114,000)", styles['StepText']))
    story.append(Paragraph("S = 24 x 134,000", styles['StepText']))
    story.append(Paragraph("S = 3,216,000", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Total loan repaid = Tsh 3,216,000"))
    story.append(S(1, 6))
    story.append(tip("For AP problems: use l = a + (n-1)d to find n, and S = (n/2)(a + l) to find the total sum. These two formulas solve most AP questions."))
    story.append(S(1, 6))
    story.append(summary("An arithmetic progression has a constant difference between consecutive terms. Key formulas: nth term = a + (n-1)d, Sum = (n/2)(first + last)."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 10: Trigonometry and Inequality
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(10, "Trigonometry and Inequality", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) An electricity post AB is 6 m tall. A wire AC = 10 m goes from the top A to the ground at C. Point D is on the ground, 4 m from C (CD = 4 m). Find AD in surd form.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Find BC using Pythagoras in triangle ABC (right angle at B).", styles['StepText']))
    story.append(Paragraph("BC<super>2</super> = AC<super>2</super> - AB<super>2</super> = 10<super>2</super> - 6<super>2</super> = 100 - 36 = 64", styles['StepText']))
    story.append(Paragraph("BC = 8 m", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Find BD.", styles['StepText']))
    story.append(Paragraph("D is between B and C, so BD = BC - CD = 8 - 4 = 4 m", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Find AD using Pythagoras in triangle ABD (right angle at B).", styles['StepText']))
    story.append(Paragraph("AD<super>2</super> = AB<super>2</super> + BD<super>2</super> = 6<super>2</super> + 4<super>2</super> = 36 + 16 = 52", styles['StepText']))
    story.append(Paragraph("AD = &#x221A;52 = &#x221A;(4 x 13) = 2&#x221A;13", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("AD = 2&#x221A;13 m"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Show that 4 sin 75&#176; = &#x221A;6 + &#x221A;2</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Write 75&#176; as a sum of known angles.", styles['StepText']))
    story.append(Paragraph("75&#176; = 45&#176; + 30&#176;", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Apply the compound angle formula.", styles['StepText']))
    story.append(Paragraph("sin(45&#176; + 30&#176;) = sin 45&#176; cos 30&#176; + cos 45&#176; sin 30&#176;", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Substitute the exact values.", styles['StepText']))
    story.append(Paragraph("= (&#x221A;2/2)(&#x221A;3/2) + (&#x221A;2/2)(1/2)", styles['StepText']))
    story.append(Paragraph("= &#x221A;6/4 + &#x221A;2/4", styles['StepText']))
    story.append(Paragraph("= (&#x221A;6 + &#x221A;2) / 4", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 4:</b> Multiply both sides by 4.", styles['StepText']))
    story.append(Paragraph("4 sin 75&#176; = &#x221A;6 + &#x221A;2 &nbsp; &#x2713; (proved)", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("4 sin 75&#176; = &#x221A;6 + &#x221A;2 (shown)"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(c) A student needs a minimum average of 53 in two tests. She scored 54 in the first test. Find the least possible mark in the second test.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Let x = mark in the second test.", styles['StepText']))
    story.append(Paragraph("Average = (54 + x) / 2", styles['StepText']))
    story.append(Paragraph("We need: (54 + x) / 2 &#x2265; 53", styles['StepText']))
    story.append(Paragraph("54 + x &#x2265; 106", styles['StepText']))
    story.append(Paragraph("x &#x2265; 52", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("The least possible mark in the second test is 52."))
    story.append(S(1, 6))
    story.append(warn("An inequality uses &#x2265; (greater than or equal to), not just &gt;. The minimum value satisfying x &#x2265; 52 is exactly 52."))
    story.append(S(1, 6))
    story.append(summary("Use Pythagoras to find distances in right triangles. The compound angle formula sin(A+B) = sinA cosB + cosA sinB is essential for exact values. For inequalities, solve like equations but keep the direction of the inequality."))
    story.append(PageBreak())

    # ── SECTION B HEADER ──
    sec_b_data = [[Paragraph("<b>SECTION B (40 Marks)</b><br/>Answer FOUR questions from this section. Each question carries 10 marks.", ParagraphStyle('SB', fontName='Helvetica-Bold', fontSize=14, textColor=white, alignment=TA_CENTER, leading=20))]]
    sec_b = Table(sec_b_data, colWidths=[WIDTH - 80])
    sec_b.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), HexColor("#1a5276")), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
    story.append(sec_b)
    story.append(S(1, 10))

    # ────────────────────────────────────────────────────────────────
    # QUESTION 11: Statistics
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(11, "Statistics", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>The cumulative frequency table of students' scores is given below:</b>", styles['SubPart']))
    story.append(S(1, 4))

    # Cumulative frequency table
    hdr_s2 = ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)
    cell_s2 = ParagraphStyle('TC2', fontName='Helvetica', fontSize=10, textColor=HexColor("#222222"), alignment=TA_CENTER)
    cf_data = [
        [Paragraph("Scores", hdr_s2), Paragraph("65-69", hdr_s2), Paragraph("70-74", hdr_s2), Paragraph("75-79", hdr_s2), Paragraph("80-84", hdr_s2), Paragraph("85-89", hdr_s2), Paragraph("90-94", hdr_s2), Paragraph("95-99", hdr_s2)],
        [Paragraph("Cum. Freq.", cell_s2), Paragraph("10", cell_s2), Paragraph("22", cell_s2), Paragraph("43", cell_s2), Paragraph("49", cell_s2), Paragraph("58", cell_s2), Paragraph("62", cell_s2), Paragraph("66", cell_s2)],
    ]
    cf_t = Table(cf_data, colWidths=[80] + [58] * 7)
    cf_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(cf_t)
    story.append(S(1, 4))

    # Frequency table
    story.append(Paragraph("<b>Step 1:</b> Extract the individual frequencies from the cumulative frequencies.", styles['StepText']))
    freq_table_data = [
        [Paragraph("Scores", hdr_s2), Paragraph("65-69", hdr_s2), Paragraph("70-74", hdr_s2), Paragraph("75-79", hdr_s2), Paragraph("80-84", hdr_s2), Paragraph("85-89", hdr_s2), Paragraph("90-94", hdr_s2), Paragraph("95-99", hdr_s2)],
        [Paragraph("Frequency", cell_s2), Paragraph("10", cell_s2), Paragraph("12", cell_s2), Paragraph("21", cell_s2), Paragraph("6", cell_s2), Paragraph("9", cell_s2), Paragraph("4", cell_s2), Paragraph("4", cell_s2)],
        [Paragraph("Midpoint", cell_s2), Paragraph("67", cell_s2), Paragraph("72", cell_s2), Paragraph("77", cell_s2), Paragraph("82", cell_s2), Paragraph("87", cell_s2), Paragraph("92", cell_s2), Paragraph("97", cell_s2)],
    ]
    freq_table = Table(freq_table_data, colWidths=[80] + [58] * 7)
    freq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(freq_table)
    story.append(S(1, 4))
    story.append(Paragraph("Total students (N) = 10 + 12 + 21 + 6 + 9 + 4 + 4 = 66", styles['StepText']))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a)(i) Mean using assumed mean A = 77:</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Deviations (d = midpoint - 77): -10, -5, 0, 5, 10, 15, 20", styles['StepText']))
    story.append(Paragraph("&#x2211;fd = 10(-10) + 12(-5) + 21(0) + 6(5) + 9(10) + 4(15) + 4(20)", styles['StepText']))
    story.append(Paragraph("= -100 + (-60) + 0 + 30 + 90 + 60 + 80 = 100", styles['StepText']))
    story.append(Paragraph("Mean = A + &#x2211;fd / N = 77 + 100/66 = 77 + 1.52 = 78.52", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Mean = 78.52 (to 2 decimal places)"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a)(ii) Ogive (cumulative frequency curve):</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Plot cumulative frequencies against upper class boundaries:", styles['StepText']))
    story.append(Paragraph("(69.5, 10), (74.5, 22), (79.5, 43), (84.5, 49), (89.5, 58), (94.5, 62), (99.5, 66)", styles['StepText']))
    story.append(Paragraph("Join the points with a smooth curve. Start from (64.5, 0).", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Plot the points above on graph paper and draw a smooth S-shaped curve (ogive)."))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a)(iii) Mode:</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("The modal class is 75-79 (highest frequency = 21).", styles['StepText']))
    story.append(Paragraph("Mode = L + [(f<sub>1</sub> - f<sub>0</sub>) / (2f<sub>1</sub> - f<sub>0</sub> - f<sub>2</sub>)] x h", styles['StepText']))
    story.append(Paragraph("Where: L = 74.5, f<sub>1</sub> = 21, f<sub>0</sub> = 12, f<sub>2</sub> = 6, h = 5", styles['StepText']))
    story.append(Paragraph("Mode = 74.5 + [(21 - 12) / (2(21) - 12 - 6)] x 5", styles['StepText']))
    story.append(Paragraph("= 74.5 + [9 / (42 - 18)] x 5", styles['StepText']))
    story.append(Paragraph("= 74.5 + (9/24) x 5", styles['StepText']))
    story.append(Paragraph("= 74.5 + 1.875 = 76.375", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Mode = 76.375"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(b) PT is a tangent to a circle with centre O and radius 5 cm. A secant from P passes through the centre, hitting the circle at C (nearer) and the far side. If PC = 8 cm, find PT.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Find PA (the far intersection of the secant with the circle).", styles['StepText']))
    story.append(Paragraph("The secant passes through the centre. Diameter = 2 x 5 = 10 cm.", styles['StepText']))
    story.append(Paragraph("PA = PC + diameter = 8 + 10 = 18 cm", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Use the tangent-secant theorem.", styles['StepText']))
    story.append(Paragraph("PT<super>2</super> = PC x PA = 8 x 18 = 144", styles['StepText']))
    story.append(Paragraph("PT = &#x221A;144 = 12 cm", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("PT = 12 cm"))
    story.append(S(1, 6))
    story.append(tip("The tangent-secant theorem states: PT<super>2</super> = PC x PA, where PT is the tangent and PCA is the secant from external point P."))
    story.append(S(1, 6))
    story.append(summary("For grouped data: Mean = A + &#x2211;fd/N. Mode uses the modal class formula. The ogive plots cumulative frequencies against upper class boundaries. For circles, the tangent-secant theorem is PT<super>2</super> = PC x PA."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 12: 3D Shapes and Volume
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(12, "3D Shapes and Dimensions", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a)(i) The surface area of a sphere is 113.04 cm<super>2</super>. Find the diameter. (Use &#x03C0; = 3.14)</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Use the surface area formula.", styles['StepText']))
    story.append(Paragraph("Surface area = 4&#x03C0;r<super>2</super>", styles['StepText']))
    story.append(Paragraph("113.04 = 4 x 3.14 x r<super>2</super>", styles['StepText']))
    story.append(Paragraph("113.04 = 12.56 x r<super>2</super>", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Solve for r.", styles['StepText']))
    story.append(Paragraph("r<super>2</super> = 113.04 / 12.56 = 9", styles['StepText']))
    story.append(Paragraph("r = 3 cm", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Find the diameter.", styles['StepText']))
    story.append(Paragraph("Diameter = 2r = 2 x 3 = 6 cm", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Diameter = 6 cm"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(a)(ii) 75.360 litres of water is poured into a cylindrical tank with diameter 40 cm. Find the height of water. (Use &#x03C0; = 3.14)</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Convert litres to cm<super>3</super>.", styles['StepText']))
    story.append(Paragraph("75.360 litres = 75,360 cm<super>3</super> (since 1 litre = 1000 cm<super>3</super>)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Use the volume formula for a cylinder.", styles['StepText']))
    story.append(Paragraph("V = &#x03C0;r<super>2</super>h", styles['StepText']))
    story.append(Paragraph("Radius = 40/2 = 20 cm", styles['StepText']))
    story.append(Paragraph("75,360 = 3.14 x 20<super>2</super> x h", styles['StepText']))
    story.append(Paragraph("75,360 = 3.14 x 400 x h", styles['StepText']))
    story.append(Paragraph("75,360 = 1,256 x h", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Solve for h.", styles['StepText']))
    story.append(Paragraph("h = 75,360 / 1,256 = 60 cm", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Height of water = 60 cm"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) A farmer has 56 m of wire to fence a rectangular plot with area 171 m<super>2</super>. Find the dimensions.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Step 1:</b> Set up equations.", styles['StepText']))
    story.append(Paragraph("Perimeter: 2(l + w) = 56, so l + w = 28", styles['StepText']))
    story.append(Paragraph("Area: l x w = 171", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Form a quadratic equation.", styles['StepText']))
    story.append(Paragraph("Since l + w = 28 and l x w = 171, l and w are roots of:", styles['StepText']))
    story.append(Paragraph("x<super>2</super> - 28x + 171 = 0", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 3:</b> Solve the quadratic.", styles['StepText']))
    story.append(Paragraph("x = (28 &#xB1; &#x221A;(784 - 684)) / 2 = (28 &#xB1; &#x221A;100) / 2 = (28 &#xB1; 10) / 2", styles['StepText']))
    story.append(Paragraph("x = 38/2 = 19 &nbsp; or &nbsp; x = 18/2 = 9", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Dimensions: 19 m x 9 m"))
    story.append(S(1, 6))
    story.append(tip("When you know both the sum and product of two numbers, they are the roots of x<super>2</super> - (sum)x + (product) = 0."))
    story.append(S(1, 6))
    story.append(summary("Surface area of sphere = 4&#x03C0;r<super>2</super>. Volume of cylinder = &#x03C0;r<super>2</super>h. If perimeter and area of a rectangle are known, use the quadratic formula to find the dimensions."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 13: Navigation, Matrices, Enlargement
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(13, "Navigation, Matrices, and Enlargement", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) Find the distance in nautical miles along a meridian:</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) A(18&#176;N, 12&#176;E) and B(65&#176;N, 12&#176;E):</b>", styles['StepText']))
    story.append(Paragraph("Both points are on the same longitude (12&#176;E), so we travel along a meridian.", styles['StepText']))
    story.append(Paragraph("Difference in latitude = 65&#176; - 18&#176; = 47&#176;", styles['StepText']))
    story.append(Paragraph("Distance = 47 x 60 = 2,820 nautical miles", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Distance AB = 2,820 nautical miles"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) C(31&#176;S, 76&#176;W) and D(22&#176;N, 76&#176;W):</b>", styles['StepText']))
    story.append(Paragraph("Both points are on the same longitude (76&#176;W). One is South, one is North.", styles['StepText']))
    story.append(Paragraph("Total difference in latitude = 31&#176; + 22&#176; = 53&#176;", styles['StepText']))
    story.append(Paragraph("Distance = 53 x 60 = 3,180 nautical miles", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Distance CD = 3,180 nautical miles"))
    story.append(S(1, 6))
    story.append(warn("When two places are on opposite sides of the equator (one N, one S), ADD the latitudes. When on the same side, SUBTRACT."))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Roza and Juma wrote 2x2 matrices:</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("Let R = [4, -6; 5, 3] (Roza's matrix) and J = [2, -6; 5, 3] (Juma's matrix).", styles['BodyText2']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Find 2R + 3J:</b>", styles['StepText']))
    story.append(Paragraph("2R = 2[4, -6; 5, 3] = [8, -12; 10, 6]", styles['StepText']))
    story.append(Paragraph("3J = 3[2, -6; 5, 3] = [6, -18; 15, 9]", styles['StepText']))
    story.append(Paragraph("2R + 3J = [8+6, -12+(-18); 10+15, 6+9] = [14, -30; 25, 15]", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("2R + 3J = [14, -30; 25, 15]"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) Find the difference of the determinants:</b>", styles['StepText']))
    story.append(Paragraph("det(R) = (4)(3) - (-6)(5) = 12 + 30 = 42", styles['StepText']))
    story.append(Paragraph("det(J) = (2)(3) - (-6)(5) = 6 + 30 = 36", styles['StepText']))
    story.append(Paragraph("Difference = 42 - 36 = 6", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Difference of determinants = 6"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(c) A farm measuring 72 m x 88 m is enlarged by a scale factor of 4.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) Find the area of the enlarged farm.</b>", styles['StepText']))
    story.append(Paragraph("Original area = 72 x 88 = 6,336 m<super>2</super>", styles['StepText']))
    story.append(Paragraph("Area scale factor = 4<super>2</super> = 16", styles['StepText']))
    story.append(Paragraph("New area = 6,336 x 16 = 101,376 m<super>2</super>", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Area of enlarged farm = 101,376 m<super>2</super>"))
    story.append(S(1, 6))
    story.append(tip("When a shape is enlarged by scale factor k, lengths multiply by k but areas multiply by k<super>2</super> and volumes by k<super>3</super>."))
    story.append(S(1, 6))
    story.append(summary("Meridian distance = difference in latitude x 60 nm. For matrices, det[a,b;c,d] = ad - bc. Enlargement: area scale factor = (linear scale factor)<super>2</super>."))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────────
    # QUESTION 14: Functions and Linear Programming
    # ────────────────────────────────────────────────────────────────
    story.append(qheader(14, "Functions and Linear Programming", styles))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(a) A quiz awards points by y = 3x, where x = number of correct answers.</b>", styles['SubPart']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>(i) How many points for 8 correct answers?</b>", styles['StepText']))
    story.append(Paragraph("y = 3x = 3(8) = 24 points", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("24 points"))
    story.append(S(1, 6))

    story.append(Paragraph("<b>(ii) Find the inverse function. State the domain and range of the inverse.</b>", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 1:</b> Find the inverse.", styles['StepText']))
    story.append(Paragraph("y = 3x", styles['StepText']))
    story.append(Paragraph("Swap x and y: x = 3y", styles['StepText']))
    story.append(Paragraph("Solve for y: y = x/3", styles['StepText']))
    story.append(Paragraph("So f<super>-1</super>(x) = x/3", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Step 2:</b> Domain and range of the inverse.", styles['StepText']))
    story.append(Paragraph("Domain of f<super>-1</super> = Range of f = {3, 6, 9, 12, ...} (multiples of 3, i.e., the points awarded)", styles['StepText']))
    story.append(Paragraph("Range of f<super>-1</super> = Domain of f = {1, 2, 3, 4, ...} (positive integers, i.e., the number of correct answers)", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("f<super>-1</super>(x) = x/3<br/>Domain of inverse: {3, 6, 9, 12, ...}<br/>Range of inverse: {1, 2, 3, 4, ...}"))
    story.append(S(1, 8))

    story.append(Paragraph("<b>(b) Linear Programming: Minimise cost of a food mixture.</b>", styles['SubPart']))
    story.append(S(1, 4))

    # Vitamin table
    lp_hdr = ParagraphStyle('LPH', fontName='Helvetica-Bold', fontSize=10, textColor=white, alignment=TA_CENTER)
    lp_cell = ParagraphStyle('LPC', fontName='Helvetica', fontSize=10, textColor=HexColor("#222222"), alignment=TA_CENTER)
    lp_data = [
        [Paragraph("Vitamin", lp_hdr), Paragraph("Food I (per kg)", lp_hdr), Paragraph("Food II (per kg)", lp_hdr), Paragraph("Min. Required", lp_hdr)],
        [Paragraph("A", lp_cell), Paragraph("2", lp_cell), Paragraph("1", lp_cell), Paragraph("10", lp_cell)],
        [Paragraph("B", lp_cell), Paragraph("1", lp_cell), Paragraph("2", lp_cell), Paragraph("12", lp_cell)],
        [Paragraph("C", lp_cell), Paragraph("1", lp_cell), Paragraph("3", lp_cell), Paragraph("8", lp_cell)],
        [Paragraph("Cost (Tsh/kg)", lp_cell), Paragraph("6,000", lp_cell), Paragraph("10,000", lp_cell), Paragraph("", lp_cell)],
    ]
    lp_t = Table(lp_data, colWidths=[100, 100, 100, 100])
    lp_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(lp_t)
    story.append(S(1, 6))

    story.append(Paragraph("Let x = kg of Food I, y = kg of Food II.", styles['StepText']))
    story.append(S(1, 4))
    story.append(Paragraph("<b>Constraints:</b>", styles['StepText']))
    story.append(Paragraph("2x + y &#x2265; 10 &nbsp; (Vitamin A)", styles['StepText']))
    story.append(Paragraph("x + 2y &#x2265; 12 &nbsp; (Vitamin B)", styles['StepText']))
    story.append(Paragraph("x + 3y &#x2265; 8 &nbsp; (Vitamin C)", styles['StepText']))
    story.append(Paragraph("x &#x2265; 0, y &#x2265; 0", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Objective:</b> Minimise C = 6,000x + 10,000y", styles['StepText']))
    story.append(S(1, 4))

    story.append(Paragraph("<b>Step 1:</b> Find the corner points of the feasible region.", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Intersection of 2x + y = 10 and x + 2y = 12:</b>", styles['StepText']))
    story.append(Paragraph("From first equation: y = 10 - 2x", styles['StepText']))
    story.append(Paragraph("Substitute into second: x + 2(10 - 2x) = 12", styles['StepText']))
    story.append(Paragraph("x + 20 - 4x = 12 &nbsp; &#x2192; &nbsp; -3x = -8 &nbsp; &#x2192; &nbsp; x = 8/3", styles['StepText']))
    story.append(Paragraph("y = 10 - 2(8/3) = 10 - 16/3 = 14/3", styles['StepText']))
    story.append(Paragraph("Point: (8/3, 14/3) &#x2248; (2.67, 4.67)", styles['StepText']))
    story.append(S(1, 2))
    story.append(Paragraph("<b>Other feasible corners:</b>", styles['StepText']))
    story.append(Paragraph("y-axis: (0, 10) - satisfies all constraints", styles['StepText']))
    story.append(Paragraph("x-axis: (12, 0) - satisfies all constraints", styles['StepText']))
    story.append(S(1, 4))

    story.append(Paragraph("<b>Step 2:</b> Evaluate the cost at each corner point.", styles['StepText']))
    story.append(Paragraph("At (8/3, 14/3): C = 6,000(8/3) + 10,000(14/3) = 16,000 + 46,667 = 62,667", styles['StepText']))
    story.append(Paragraph("At (0, 10): C = 6,000(0) + 10,000(10) = 100,000", styles['StepText']))
    story.append(Paragraph("At (12, 0): C = 6,000(12) + 10,000(0) = 72,000", styles['StepText']))
    story.append(S(1, 4))

    story.append(Paragraph("<b>Step 3:</b> The minimum cost is at the intersection point.", styles['StepText']))
    story.append(S(1, 4))
    story.append(ans("Minimum cost = Tsh 62,667 (approximately)<br/>at x = 8/3 kg of Food I and y = 14/3 kg of Food II"))
    story.append(S(1, 6))
    story.append(warn("Always check that your corner points satisfy ALL the constraints before evaluating the objective function."))
    story.append(S(1, 6))
    story.append(tip("In linear programming, the optimal solution always occurs at a corner point (vertex) of the feasible region. Test all corners and pick the minimum (or maximum)."))
    story.append(S(1, 6))
    story.append(summary("For linear programming: (1) Define variables. (2) Write constraints as inequalities. (3) Graph the feasible region. (4) Find corner points. (5) Evaluate the objective function at each corner. (6) Pick the optimal value."))
    story.append(PageBreak())

    # ── CLOSING PAGE ──
    story.append(S(1, 120))
    story.append(Paragraph("myTZStudies", styles['ClosingTitle']))
    story.append(S(1, 6))
    story.append(Paragraph("Your Free Tanzanian Exam Library", styles['CoverSubtitle']))
    story.append(S(1, 30))
    story.append(Paragraph("This answer key was created by myTZStudies<br/>to help Tanzanian students study smarter.", styles['ClosingText']))
    story.append(S(1, 15))
    story.append(Paragraph("Find more past papers and answer keys at:", styles['ClosingText']))
    story.append(S(1, 6))
    story.append(Paragraph("mytzstudies.com", styles['CoverURL']))
    story.append(S(1, 30))
    story.append(Paragraph("Past Exam Papers | Answer Keys | Free Access<br/>Standard 4 to Form 6 | All Subjects Covered", styles['ClosingText']))
    story.append(S(1, 20))
    story.append(Paragraph("Share this with a friend.<br/>Every student deserves free study materials.", styles['CoverShare']))

    # Build
    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF created: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
