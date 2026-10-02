"""Make source-page contact sheets for manual question and diagram review."""
import argparse
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("exam")
    parser.add_argument("pages", nargs="*", type=int)
    args = parser.parse_args()
    exam = Path(args.exam)
    doc = pymupdf.open(exam)
    pages = args.pages or list(range(1, len(doc) + 1))
    destination = Path("tmp/pdfs/source-review")
    destination.mkdir(parents=True, exist_ok=True)
    for offset in range(0, len(pages), 4):
        sheet = Image.new("RGB", (1800, 2600), "#dce3e8")
        label = ImageDraw.Draw(sheet)
        for index, number in enumerate(pages[offset:offset + 4]):
            pixmap = doc[number - 1].get_pixmap(matrix=pymupdf.Matrix(1.7, 1.7))
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            image.thumbnail((880, 1235))
            x, y = 10 + index % 2 * 900, 30 + index // 2 * 1300
            sheet.paste(image, (x, y))
            label.text((x, y - 20), f"Page {number}", fill="#173645")
        path = destination / f"{exam.stem}-sheet{offset // 4 + 1:02d}.png"
        sheet.save(path)
        print(path)


if __name__ == "__main__":
    main()
