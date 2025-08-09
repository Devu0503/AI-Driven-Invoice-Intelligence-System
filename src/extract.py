import os
import re
import pandas as pd
from datetime import datetime

def parse_invoice_text(text):
    def extract(pattern, default=""):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    return {
        "Invoice_No": extract(r"Invoice\s*No[:\-]?\s*([\w\/-]+)", "INV"),
        "Date": extract(r"Date[:\-]?\s*([\d\-\/]+)", datetime.today().strftime("%Y-%m-%d")),
        "Time": extract(r"Time[:\-]?\s*([\d:APMapm\s]+)", datetime.now().strftime("%H:%M:%S")),
        "Buyer_Name": extract(r"Buyer\s*Name[:\-]?\s*(.+)"),
        "Buyer_Address": extract(r"Buyer\s*Address[:\-]?\s*(.+)"),
        "PAN": extract(r"PAN\s*No[:\-]?\s*(\w{10})"),
        "GSTIN": extract(r"GSTIN[:\-]?\s*([\dA-Z]{15})"),
        "Item": extract(r"Item[:\-]?\s*(.+)"),
        "Qty": extract(r"Quantity[:\-]?\s*(\d+)"),
        "Rate": extract(r"Rate[:\-]?\s*Rs\.?(\d+)"),
        "Amount": extract(r"Amount[:\-]?\s*Rs\.?([\d,.]+)"),
        "CGST": extract(r"CGST.*Rs\.?([\d,.]+)"),
        "SGST": extract(r"SGST.*Rs\.?([\d,.]+)"),
        "Total": extract(r"Total\s*Amount\s*Payable[:\-]?\s*Rs\.?([\d,.]+)"),
        "Terms": extract(r"Terms[:\-]?\s*(.+)"),
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
    print(f" Extracted structured data saved to: {output_csv}")

if __name__ == "__main__":
    extract_from_ocr_outputs("data/ocr_outputs", "data/structured_csv/invoice_data.csv")
