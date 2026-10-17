"""OCR metrics with explicit denominators and retained failure rows."""
import unicodedata
from cer_wer_calculator import levenshtein


def normalize(text):
    return "\n".join(" ".join(line.split()) for line in unicodedata.normalize("NFC", text).replace("\r\n", "\n").splitlines()).strip()


def ocr_metric(reference, hypothesis, status="ok"):
    ref, hyp = normalize(reference), normalize(hypothesis or "")
    edits = levenshtein(ref, hyp)
    return {"reference_characters": len(ref), "edit_distance": edits,
            "cer": edits / len(ref) if ref else None, "status": status,
            "empty_reference": not bool(ref), "failed": status != "ok"}


def summarize(rows):
    applicable = [r for r in rows if r["reference_characters"] > 0]
    chars = sum(r["reference_characters"] for r in applicable)
    return {"attempts": len(rows), "failures": sum(r["failed"] for r in rows),
            "scorable_documents": len(applicable), "empty_reference_documents": len(rows)-len(applicable),
            "reference_characters": chars,
            "micro_cer": sum(r["edit_distance"] for r in applicable)/chars if chars else None,
            "macro_cer": sum(r["cer"] for r in applicable)/len(applicable) if applicable else None}
