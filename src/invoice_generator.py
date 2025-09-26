# takes invoice inputs via a form,                               # High-level summary of module capabilities.
# renders a visual invoice with PIL,                             # 1) UI for input; 2) draw invoice as an image.
# saves PNG & PDF to disk,                                       # 3) Persist as PNG/PDF files.
# appends a row to CSV and SQLite,                               # 4) Log each invoice to CSV and DB.
# lets the user download the PDF.                                # 5) Provide a download button in Streamlit.

# src/invoice_generator.py                                       # File path (informational).

import os, io, datetime                                          # stdlib: filesystem ops, in-memory bytes, dates/times.
import pandas as pd                                              # Pandas for writing/reading tabular data (CSV).
from PIL import Image, ImageDraw, ImageFont                      # Pillow: image creation, drawing, and fonts.
import streamlit as st                                           # Streamlit: web UI framework.

try:
    # when imported as a package (recommended)
    from .db import insert_row                                   # Preferred relative import of DB insert helper.
except ImportError:
    # fallback if someone runs the file directly
    from src.db import insert_row                                # Fallback absolute import for direct script runs.

GEN_DIR = "data/generated_invoices"                              # Output directory for generated files.
os.makedirs(GEN_DIR, exist_ok=True)                              # Ensure the directory exists (no error if it does).

def _render_invoice_image(data: dict) -> Image.Image:            # Internal: render an invoice to a PIL Image.
    """Render an invoice into a PIL Image we can also export to PDF."""  # Docstring describing the function.
    img = Image.new("RGB", (900, 900), color="white")            # Create a blank 900x900 white canvas.
    draw = ImageDraw.Draw(img)                                   # Get a drawing context to place text/graphics.
    try:
        font = ImageFont.truetype("arial.ttf", 24)               # Try loading Arial regular (24pt) for body text.
        font_b = ImageFont.truetype("arial.ttf", 28)             # Try loading Arial (28pt) for headers/bold.
    except Exception:
        font = ImageFont.load_default()                          # Fallback to default bitmap font if not found.
        font_b = font                                            # Use same fallback for bold.

    y = 40                                                       # Vertical cursor for text placement.
    draw.text((300, y), "INVOICE", font=font_b, fill="black"); y += 50  # Title at near-top center-ish, then move down.

    lines = [                                                    # Key header fields to print, pulled from data dict.
        ("Invoice No", data["Invoice_No"]),
        ("Date",       data["Date"]),
        ("Time",       data["Time"]),
        ("Buyer Name", data["Buyer_Name"]),
        ("Buyer Address", data["Buyer_Address"]),
        ("PAN",        data["PAN"]),
        ("GSTIN",      data.get("GSTIN","")),                    # GSTIN may be missing → default to empty string.
    ]
    for k,v in lines:                                            # Loop over each (label, value) pair...
        draw.text((50, y), f"{k}: {v}", font=font, fill="black"); y += 36  # Print and advance vertical cursor.

    y += 12                                                      # Small spacing before item details section.
    draw.text((50, y), "Item Details:", font=font_b, fill="black"); y += 36  # Section header.
    draw.text((60, y), f"Item: {data['Item']}", font=font, fill="black"); y += 28  # Item name.
    draw.text((60, y),                                           # Quantity, Rate, Amount on one line.
              f"Quantity: {data['Qty']}   Rate: ₹{data['Rate']}   Amount: ₹{data['Amount']}",
              font=font, fill="black"); y += 36
    draw.text((50, y), f"CGST (9%): ₹{data['CGST']}", font=font, fill="black"); y += 28  # CGST line.
    draw.text((50, y), f"SGST (9%): ₹{data['SGST']}", font=font, fill="black"); y += 28  # SGST line.
    draw.text((50, y), f"Total Amount Payable: ₹{data['Total']}", font=font_b, fill="black"); y += 48  # Total.
    draw.text((50, y), data["Terms"], font=font, fill="black")   # Terms & conditions at the end.

    return img                                                   # Return the composed PIL image.

def _append_csv(csv_path: str, record: dict):                    # Internal: append a single invoice to a CSV file.
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)        # Ensure the CSV directory exists.
    if os.path.exists(csv_path):                                 # If CSV already exists...
        pd.DataFrame([record]).to_csv(csv_path, mode="a", header=False, index=False)  # append row (no header).
    else:                                                        # If no CSV yet...
        pd.DataFrame([record]).to_csv(csv_path, index=False)     # create new CSV with header.

def generator(csv_path: str):                                    # Public Streamlit UI entry: build form + persist flows.
    """Streamlit UI: create invoice → download PDF → auto-save to CSV & DB."""  # Docstring for UX flow.
    st.subheader("🧾 Create & Download Invoice (auto-saves to DB/CSV)")  # Section header in the app.

    with st.form("make_invoice"):                                # Start a form block (group inputs + one submit).
        col1, col2 = st.columns(2)                               # Two-column layout for cleaner UI.
        with col1:                                               # Left column inputs:
            invoice_no   = st.text_input("Invoice No", value="INV/2025/089019")  # Invoice number text field.
            date         = st.date_input("Date", value=datetime.date.today())    # Date picker (defaults to today).
            time         = st.time_input("Time", value=datetime.datetime.now().time())  # Time picker (defaults now).
            buyer_name   = st.text_input("Buyer Name")           # Buyer’s name.
            pan          = st.text_input("PAN", value="ABCDE1234F")  # PAN with sample default.
        with col2:                                               # Right column inputs:
            buyer_addr   = st.text_area("Buyer Address", height=90)   # Multiline address field.
            gstin        = st.text_input("GSTIN", value="16ABCDE8273Z01")  # GSTIN with sample default.
            item         = st.text_input("Item", value="Power Bank")       # Item name.
            qty          = st.number_input("Quantity", min_value=1, value=1)  # Integer quantity (min 1).
            rate         = st.number_input("Rate (₹)", min_value=0, value=500)  # Unit price (non-negative).

        terms = st.text_input("Terms", value="Goods once sold will not be taken back.")  # Terms string.
        submitted = st.form_submit_button("Create Invoice")       # Submit button for the form.

    if not submitted:                                            # If the user hasn’t submitted yet...
        return                                                   # stop here (don’t render or save anything).

    amount = qty * rate                                          # Raw amount = qty × rate.
    cgst = round(amount * 0.09, 2)                               # CGST at 9%, rounded to 2 decimals.
    sgst = round(amount * 0.09, 2)                               # SGST at 9%, rounded to 2 decimals.
    total = round(amount + cgst + sgst, 2)                       # Grand total = amount + both taxes.

    record = {                                                   # Build a normalized record dict for persistence.
        "Invoice_No": invoice_no,                                # Invoice identifier.
        "Date": str(date),                                       # Coerce date object to string for CSV/DB.
        "Time": str(time),                                       # Coerce time object to string for CSV/DB.
        "Buyer_Name": buyer_name,                                # Buyer’s name.
        "Buyer_Address": buyer_addr,                             # Buyer’s address.
        "PAN": pan,                                              # PAN.
        "GSTIN": gstin,                                          # GSTIN.
        "Item": item,                                            # Item description.
        "Qty": int(qty),                                         # Quantity as int.
        "Rate": float(rate),                                     # Rate as float.
        "Amount": float(amount),                                 # Subtotal as float.
        "CGST": float(cgst),                                     # CGST as float.
        "SGST": float(sgst),                                     # SGST as float.
        "Total": float(total),                                   # Total as float.
        "Terms": terms,                                          # Terms string.
        "Source_File": f"{invoice_no}.pdf"                       # Logical filename reference (not sanitized).
    }

    # Render preview image
    img = _render_invoice_image(record)                          # Create a PIL image from the record.
    st.image(img, caption="Preview", use_container_width=True)   # Show preview in the UI.

    # Save PNG + PDF on disk and offer PDF download
    safe_invoice_no = invoice_no.replace("/", "_")               # Sanitize invoice_no for filesystem paths.
    png_path = os.path.join(GEN_DIR, f"{safe_invoice_no}.png")   # Full PNG output path.
    pdf_path = os.path.join(GEN_DIR, f"{safe_invoice_no}.pdf")   # Full PDF output path.
    img.save(png_path, "PNG")                                    # Write PNG to disk.

    pdf_bytes = io.BytesIO()                                     # In-memory buffer for PDF export.
    img.save(pdf_bytes, "PDF", resolution=100.0)                 # Export the image as PDF into buffer.
    pdf_bytes.seek(0)                                            # Rewind buffer to the beginning.
    with open(pdf_path, "wb") as f:                              # Open the output PDF path for writing...
        f.write(pdf_bytes.getbuffer())                           # ...and write the in-memory bytes to disk.

    # Persist to CSV + DB
    _append_csv(csv_path, record)                                # Append the record to the CSV log.
    try:
        insert_row(record)    # into SQLite                         # Attempt DB insert via helper.
    except Exception as e:
        st.warning(f"DB insert warning: {e}")                     # Non-fatal warning if DB insert fails.

    st.success(f"✅ Saved invoice as PNG & PDF in {GEN_DIR} and appended to DB/CSV.")  # Success toast.
    st.download_button("⬇️ Download PDF",                        # Download button in the UI...
                       data=pdf_bytes,                            # ...serving the in-memory PDF bytes,
                       file_name=f"{invoice_no}.pdf",             # ...with this filename,
                       mime="application/pdf")                    # ...and correct MIME type.
