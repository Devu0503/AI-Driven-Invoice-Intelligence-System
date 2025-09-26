# src/ingest.py
import os, io
from typing import Dict, Tuple
import pandas as pd
from PIL import Image
import pytesseract

try:
    # preferred (package imports)
    from .extract import parse_invoice_text
    from .db import insert_row
except ImportError:
    # fallback if run directly
    from src.extract import parse_invoice_text
    from src.db import insert_row

def _text_from_pdf(file_bytes: bytes, lang: str = "eng") -> str:
    """
    Try native text via PyPDF2. If empty (scanned PDF), render with pypdfium2
    and OCR using Tesseract. Returns a single cleaned string.
    """
    import io, re
    from PyPDF2 import PdfReader

    # 1) Selectable text path
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        txt = "\n".join([(p.extract_text() or "") for p in reader.pages]).strip()
        # collapse excessive whitespace
        txt = re.sub(r"[ \t]+", " ", re.sub(r"\n{2,}", "\n\n", txt)).strip()
        if txt:
            return txt
    except Exception:
        pass

    # 2) OCR fallback
    try:
        import pypdfium2 as pdfium
        from PIL import Image, ImageOps
        import pytesseract

        pdf = pdfium.PdfDocument(io.BytesIO(file_bytes))
        parts = []

        # render ~200 DPI (scale≈ dpi/72)
        scale = 200 / 72.0

        for i in range(len(pdf)):
            page = pdf[i]
            pil = page.render(scale=scale).to_pil()

            # light preprocessing helps OCR on scans
            gray = ImageOps.grayscale(pil)
            # optional binarization
            bw = gray.point(lambda x: 255 if x > 200 else 0, mode="1")

            # OCR config: preserve layout a bit and assume single column
            config = "--psm 6"
            text_i = pytesseract.image_to_string(bw, lang=lang, config=config)
            parts.append(text_i)

        txt = "\n".join(parts)
        txt = re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", txt)).strip()
        return txt
    except Exception:
        return ""


def _text_from_image(file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return pytesseract.image_to_string(img)

def _append_csv(csv_path: str, rec: dict):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if os.path.exists(csv_path):
        pd.DataFrame([rec]).to_csv(csv_path, mode="a", header=False, index=False)
    else:
        pd.DataFrame([rec]).to_csv(csv_path, index=False)

def structure_and_save(text: str, source_name: str, csv_path: str) -> Dict:
    rec = parse_invoice_text(text)
    rec["Source_File"] = source_name
    _append_csv(csv_path, rec)
    try:
        insert_row(rec)
    except Exception:
        pass
    return rec

def process_upload(file, csv_path: str) -> Tuple[Dict, str]:
    name = file.name.lower()
    content = file.read()

    if name.endswith(".pdf"):
        text = _text_from_pdf(content)
        if not text:
            return {}, f"⚠️ Could not read text from {file.name} (likely a scanned PDF). Convert to image and re-upload."
        rec = structure_and_save(text, file.name, csv_path)
        return rec, f"✅ Parsed and saved: {file.name}"

    elif any(name.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
        text = _text_from_image(content)
        if not text.strip():
            return {}, f"⚠️ OCR returned empty text for {file.name}"
        rec = structure_and_save(text, file.name, csv_path)
        return rec, f"✅ OCR’d and saved: {file.name}"

    else:
        return {}, f"❌ Unsupported file type: {file.name}"



# # Purpose: Ingest uploaded invoices (PDF/JPG/PNG), extract text, parse structured fields, and persist them (CSV + SQLite). Returns the parsed record + a status message for the UI.

# Text extraction logic:

# PDFs: Try direct text with PyPDF2. If empty (scanned PDFs), render pages via pypdfium2 (~200 DPI) → light preprocess (grayscale + threshold) → Tesseract OCR (--psm 6).

# Images: Open with PIL and run Tesseract OCR.

# Parsing & persistence:

# Raw text → parse_invoice_text(...) → a dict of invoice fields.

# Adds Source_File (original filename).

# Appends one row to CSV and attempts SQLite insert (insert_row).

# Entry point for the app:
# process_upload(file, csv_path) → (record_dict, message_str)

# Routes by file extension (.pdf, .png/.jpg/.jpeg).

# Handles failures gracefully (empty OCR, unsupported type) with informative messages.

# Utilities inside:

# _text_from_pdf(...) – dual path (native text → OCR fallback).

# _text_from_image(...) – simple OCR for images.

# _append_csv(...) – creates/extends the CSV.

# structure_and_save(...) – parse → persist → return record.

# Design choices: Lightweight, stateless per call, safe fallbacks, and UI-friendly messages; silent DB errors don’t break the flow.

# Typical flow: Upload file → extract text → parse fields → save (CSV/DB) → return record + “✅ Parsed and saved: <name>”.