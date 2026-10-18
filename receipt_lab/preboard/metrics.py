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


def box_iou(reference,prediction):
    if prediction is None or len(prediction)!=4:return 0.0
    ax0,ay0,ax1,ay1=reference;bx0,by0,bx1,by1=prediction
    intersection=max(0,min(ax1,bx1)-max(ax0,bx0))*max(0,min(ay1,by1)-max(ay0,by0))
    union=max(0,ax1-ax0)*max(0,ay1-ay0)+max(0,bx1-bx0)*max(0,by1-by0)-intersection
    return intersection/union if union>0 else 0.0
