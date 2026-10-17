"""Private review sheets for unique itemized-purchase candidate images."""

import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


LAB = Path.home() / "SeminarLab"
OUT = LAB / "reports" / "itemized_59_contact"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader((LAB / "reports" / "manifest.csv").open(encoding="utf-8-sig", newline=""))
            if not r["duplicate_of"] and r["doc_type"] == "itemized_purchase"]
    assert len(rows) == 59
    upright = "--upright" in sys.argv
    files = ({r["filename"]: LAB / "reports" / "orientation_skew_59" / f"{r['doc_id']}_upright_crop.jpg" for r in rows}
             if upright else {p.name: p for p in (LAB / "incoming").rglob("*") if p.is_file()})
    font = ImageFont.truetype("arial.ttf", 22)
    cell_w, cell_h = 430, 555
    for page, start in enumerate(range(0, len(rows), 12), 1):
        sheet = Image.new("RGB", (cell_w * 4, cell_h * 3), "white")
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(rows[start:start+12]):
            x, y = (index % 4) * cell_w, (index // 4) * cell_h
            src = files[row["filename"]]
            with Image.open(src) as original:
                thumb = ImageOps.contain(ImageOps.exif_transpose(original).convert("RGB"),
                                         (cell_w - 20, cell_h - 70))
            sheet.paste(thumb, (x + (cell_w - thumb.width)//2, y + 48))
            draw.text((x+10, y+10), f"{start+index+1:02d} {row['doc_id']}", fill="black", font=font)
            draw.rectangle((x,y,x+cell_w-1,y+cell_h-1), outline="#bbbbbb", width=2)
        prefix = "upright_sheet" if upright else "sheet"
        sheet.save(OUT / f"{prefix}_{page}.jpg", quality=88)
    print(len(rows), "images in", page, "private sheets")


if __name__ == "__main__":
    main()
