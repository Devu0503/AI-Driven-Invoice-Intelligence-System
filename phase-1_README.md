# 🧠 AI Invoice Extraction Project – Phase 1

This project is designed to automate the extraction of structured data from invoice images using OCR (Optical Character Recognition). In **Phase 1**, we focus on generating synthetic invoices, performing OCR on them, and extracting key invoice fields into a structured CSV format.

---

## 🚀 Phase 1 Goals

1. ✅ Generate synthetic invoice images with realistic fields.
2. ✅ Perform OCR on invoice images to extract raw text.
3. ✅ Parse the text to extract structured data (Invoice No, Date, Buyer Name, etc.).
4. ✅ Save the structured data into a unified CSV file: `data/structured_csv/invoice_data.csv`.

---

## 📁 Project Structure

AI_Invoice_Project/
│
├── data/
│ ├── raw_invoices/ # Uploaded invoice images (user or synthetic)
│ ├── ocr_outputs/ # Raw OCR .txt files (optional stage)
│ ├── structured_csv/
│ │ └── invoice_data.csv # Final structured output from OCR
│ └── synthetic_invoices/ # (Optional) folder for storing synthetic invoices
│
├── src/
│ ├── extract.py # Parses OCR text and extracts fields into structured format
│ ├── generate_invoices_indian.py # Generates synthetic invoices using PIL
│ ├── ocr.py # Performs OCR on invoice images using pytesseract



---

## 🛠️ How It Works

### 1. 🧾 Generate Synthetic Invoices

- `generate_invoices_indian.py` creates dummy invoice images with fields like:
  - Invoice No
  - Date
  - Buyer Name and Address
  - PAN, GSTIN
  - Items with Quantity, Rate, Amount
  - CGST, SGST, Total Amount
  - Terms

### 2. 🔍 OCR on Invoice

- `ocr.py` uses `pytesseract` to extract text from the image and optionally stores it in `data/ocr_outputs`.

### 3. 🧠 Extract Fields

- `extract.py` applies regex and parsing logic to extract key fields from raw OCR text.
- Output is structured as a dictionary with consistent field names.

### 4. 💾 Save Structured Data

- The extracted records are saved in: invoice_data.csv

---

## ✅ Extracted Fields

- `Invoice_No`
- `Date`
- `Buyer_Name`
- `Buyer_Address`
- `PAN_No`
- `GSTIN`
- `Item`
- `Quantity`
- `Rate`
- `Amount`
- `CGST`
- `SGST`
- `Total_Amount_Payable`
- `Terms`

---
