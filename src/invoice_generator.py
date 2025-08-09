# src/invoice_generator.py
import os, io, datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

try:
    # when imported as a package (recommended)
    from .db import insert_row
except ImportError:
    # fallback if someone runs the file directly
    from src.db import insert_row


GEN_DIR = "data/generated_invoices"               # where to store files
os.makedirs(GEN_DIR, exist_ok=True)

def _render_invoice_image(data: dict) -> Image.Image:
    """Render an invoice into a PIL Image we can also export to PDF."""
    img = Image.new("RGB", (900, 900), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        font_b = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
        font_b = font

    y = 40
    draw.text((300, y), "INVOICE", font=font_b, fill="black"); y += 50

    lines = [
        ("Invoice No", data["Invoice_No"]),
        ("Date",       data["Date"]),
        ("Time",       data["Time"]),
        ("Buyer Name", data["Buyer_Name"]),
        ("Buyer Address", data["Buyer_Address"]),
        ("PAN",        data["PAN"]),
        ("GSTIN",      data.get("GSTIN","")),
    ]
    for k,v in lines:
        draw.text((50, y), f"{k}: {v}", font=font, fill="black"); y += 36

    y += 12
    draw.text((50, y), "Item Details:", font=font_b, fill="black"); y += 36
    draw.text((60, y), f"Item: {data['Item']}", font=font, fill="black"); y += 28
    draw.text((60, y), f"Quantity: {data['Qty']}   Rate: ₹{data['Rate']}   Amount: ₹{data['Amount']}", font=font, fill="black"); y += 36
    draw.text((50, y), f"CGST (9%): ₹{data['CGST']}", font=font, fill="black"); y += 28
    draw.text((50, y), f"SGST (9%): ₹{data['SGST']}", font=font, fill="black"); y += 28
    draw.text((50, y), f"Total Amount Payable: ₹{data['Total']}", font=font_b, fill="black"); y += 48
    draw.text((50, y), data["Terms"], font=font, fill="black")

    return img

def _append_csv(csv_path: str, record: dict):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if os.path.exists(csv_path):
        pd.DataFrame([record]).to_csv(csv_path, mode="a", header=False, index=False)
    else:
        pd.DataFrame([record]).to_csv(csv_path, index=False)

def generator(csv_path: str):
    """Streamlit UI: create invoice → download PDF → auto-save to CSV & DB."""
    st.subheader("🧾 Create & Download Invoice (auto-saves to DB/CSV)")

    with st.form("make_invoice"):
        col1, col2 = st.columns(2)
        with col1:
            invoice_no   = st.text_input("Invoice No", value="INV/2025/089019")
            date         = st.date_input("Date", value=datetime.date.today())
            time         = st.time_input("Time", value=datetime.datetime.now().time())
            buyer_name   = st.text_input("Buyer Name")
            pan          = st.text_input("PAN", value="ABCDE1234F")
        with col2:
            buyer_addr   = st.text_area("Buyer Address", height=90)
            gstin        = st.text_input("GSTIN", value="16ABCDE8273Z01")
            item         = st.text_input("Item", value="Power Bank")
            qty          = st.number_input("Quantity", min_value=1, value=1)
            rate         = st.number_input("Rate (₹)", min_value=0, value=500)

        terms = st.text_input("Terms", value="Goods once sold will not be taken back.")
        submitted = st.form_submit_button("Create Invoice")

    if not submitted:
        return

    amount = qty * rate
    cgst = round(amount * 0.09, 2)
    sgst = round(amount * 0.09, 2)
    total = round(amount + cgst + sgst, 2)

    record = {
        "Invoice_No": invoice_no,
        "Date": str(date),
        "Time": str(time),
        "Buyer_Name": buyer_name,
        "Buyer_Address": buyer_addr,
        "PAN": pan,
        "GSTIN": gstin,
        "Item": item,
        "Qty": int(qty),
        "Rate": float(rate),
        "Amount": float(amount),
        "CGST": float(cgst),
        "SGST": float(sgst),
        "Total": float(total),
        "Terms": terms,
        "Source_File": f"{invoice_no}.pdf"
    }

    # Render preview image
    img = _render_invoice_image(record)
    st.image(img, caption="Preview", use_container_width=True)

    # Save PNG + PDF on disk and offer PDF download
    safe_invoice_no = invoice_no.replace("/", "_")
    png_path = os.path.join(GEN_DIR, f"{safe_invoice_no}.png")
    pdf_path = os.path.join(GEN_DIR, f"{safe_invoice_no}.pdf")
    img.save(png_path, "PNG")

    pdf_bytes = io.BytesIO()
    img.save(pdf_bytes, "PDF", resolution=100.0)   # Pillow PDF export
    pdf_bytes.seek(0)
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes.getbuffer())

    # Persist to CSV + DB
    _append_csv(csv_path, record)
    try:
        insert_row(record)    # into SQLite
    except Exception as e:
        st.warning(f"DB insert warning: {e}")

    st.success(f"✅ Saved invoice as PNG & PDF in {GEN_DIR} and appended to DB/CSV.")
    st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=f"{invoice_no}.pdf", mime="application/pdf")
