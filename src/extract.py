import os
import re
import pandas as pd

def parse_invoice_text(text):
    # Basic example using regex
    invoice_no = re.search(r"Invoice\s*No[:\-]?\s*(\w+)", text, re.IGNORECASE)
    date = re.search(r"Date[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", text)
    total = re.search(r"Total\s*Amount[:\-]?\s*₹?([\d,]+\.\d{2})", text)

    return {
        "Invoice_No": invoice_no.group(1) if invoice_no else "",
        "Date": date.group(1) if date else "",
        "Total_Amount": total.group(1) if total else "",
    }

def extract_from_ocr_outputs(input_folder, output_csv):
    records = []
    for file in os.listdir(input_folder):
        if file.endswith(".txt"):
            with open(os.path.join(input_folder, file), "r", encoding="utf-8") as f:
                text = f.read()
                record = parse_invoice_text(text)
                record["Source_File"] = file
                records.append(record)

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"✅ Extracted data saved to: {output_csv}")

if __name__ == "__main__":
    extract_from_ocr_outputs("data/ocr_outputs", "data/structured_csv/invoice_data.csv")
