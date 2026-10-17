"""Read local assignment references into private text files for analysis."""

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf


ROOT = Path(__file__).resolve().parent.parent / "ass 5ก่อนได้รับfeedback"
OUT = Path.home() / "SeminarLab" / "reports" / "reference_text"
OUT.mkdir(parents=True, exist_ok=True)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def office_text(path: Path) -> str:
    lines = []
    with zipfile.ZipFile(path) as package:
        if path.suffix.lower() == ".docx":
            members = ["word/document.xml"]
            tag = W + "p"
            text_tag = W + "t"
        else:
            members = sorted(
                (name for name in package.namelist()
                 if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=lambda name: int(re.search(r"slide(\d+)", name).group(1)),
            )
            tag = A + "p"
            text_tag = A + "t"
        for member in members:
            lines.append(f"### {member}")
            root = ET.fromstring(package.read(member))
            for para in root.iter(tag):
                value = "".join(node.text or "" for node in para.iter(text_tag)).strip()
                if value:
                    lines.append(value)
    return "\n".join(lines)


for path in ROOT.iterdir():
    if path.suffix.lower() in (".docx", ".pptx"):
        value = office_text(path)
    elif path.suffix.lower() == ".pdf":
        document = pymupdf.open(path)
        value = "\n".join(f"### page {i + 1}\n{page.get_text()}"
                          for i, page in enumerate(document))
    else:
        continue
    target = OUT / f"{path.stem}.txt"
    target.write_text(value, encoding="utf-8")
    print(path.name, "->", target.name, "chars", len(value))
