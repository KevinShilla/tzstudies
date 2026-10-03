from pathlib import Path
import urllib.request
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / 'public' / 'fonts'
FONT_DIR.mkdir(parents=True, exist_ok=True)
for family, filename, target in [('dmsans', 'DMSans%5Bopsz,wght%5D.ttf', 'DM-Sans.ttf'), ('manrope', 'Manrope%5Bwght%5D.ttf', 'Manrope.ttf')]:
    base = f'https://raw.githubusercontent.com/google/fonts/main/ofl/{family}/'
    urllib.request.urlretrieve(base + filename, FONT_DIR / target)
    urllib.request.urlretrieve(base + 'OFL.txt', FONT_DIR / f'{family}-OFL.txt')

captures = ROOT / 'public' / 'captures'
captures.mkdir(parents=True, exist_ok=True)
source = ROOT.parent / 'answer_keys' / 'BasicMath-F2-2024-AnswerKey.pdf'
pdf = pymupdf.open(source)
pdf[2].get_pixmap(matrix=pymupdf.Matrix(2,2), clip=pymupdf.Rect(40,59,555,241)).save(str(captures / 'answer-question.png'))
for i, name in [(0, 'answer-cover'), (1, 'answer-title'), (2, 'answer-page'), (3, 'answer-steps')]:
    page = pdf[i]
    page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(str(captures / f'{name}.png'))
    (captures / f'{name}.txt').write_text(page.get_text(),encoding='utf-8')
print('Local fonts with OFL licenses and four real answer-key pages prepared.')
