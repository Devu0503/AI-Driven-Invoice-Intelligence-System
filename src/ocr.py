import numpy as np
import pandas as pd
import os
from PIL import Image
import pytesseract

# ✅ Set path to Tesseract (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(img_path):
    try:
        img = Image.open(img_path).convert("L")  # Grayscale
        # img = img.point(lambda x: 0 if x < 140 else 255, '1')  # Optional binarization
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"❌ Error processing {img_path}: {e}")
        return ""

def run_ocr_on_folder(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"❌ Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not files:
        print("⚠️ No image files found in the input folder.")
        return

    for file in files:
        image_path = os.path.join(input_folder, file)
        text = extract_text_from_image(image_path)

        if len(text.strip()) < 30:
            print(f"⚠️ OCR result too short for {file}, skipping.")
            continue

        output_file = os.path.splitext(file)[0] + ".txt"
        output_path = os.path.join(output_folder, output_file)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ OCR done: {file}")
        except Exception as e:
            print(f"❌ Failed to save OCR for {file}: {e}")

if __name__ == "__main__":
    run_ocr_on_folder("data/synthetic_invoices", "data/ocr_outputs")
