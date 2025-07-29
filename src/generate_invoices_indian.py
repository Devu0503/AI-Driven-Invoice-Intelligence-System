# src/generate_invoices_indian.py

import os
import random
from PIL import Image, ImageDraw, ImageFont
from faker import Faker

fake = Faker("en_IN")
output_dir = "data/synthetic_invoices"
os.makedirs(output_dir, exist_ok=True)

def generate_invoice_data():
    items = ["USB Cable", "Power Bank", "Mouse", "Keyboard", "Charger", "Mobile Case"]
    qty = random.randint(1, 5)
    rate = random.randint(100, 1000)
    amount = qty * rate
    cgst = amount * 0.09
    sgst = amount * 0.09
    total = amount + cgst + sgst

    return {
        "Invoice No": fake.bothify("INV/20##/0###"),
        "Date": fake.date(),
        "Buyer Name": fake.name(),
        "Buyer Address": fake.address().replace("\n", ", "),
        "PAN No": fake.bothify("ABCDE####F"),
        "GSTIN": fake.bothify("##ABCDE####Z#1"),
        "Item": random.choice(items),
        "Qty": qty,
        "Rate": rate,
        "Amount": amount,
        "CGST (9%)": round(cgst, 2),
        "SGST (9%)": round(sgst, 2),
        "Total": round(total, 2)
    }

def create_invoice_image(data, filename):
    img = Image.new("RGB", (900, 700), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    y = 40
    draw.text((300, y), "INVOICE", font=font, fill="black")
    y += 40

    for key in ["Invoice No", "Date", "Buyer Name", "Buyer Address", "PAN No", "GSTIN"]:
        draw.text((50, y), f"{key}: {data[key]}", fill="black", font=font)
        y += 40

    y += 20
    draw.text((50, y), "Item Details:", font=font, fill="black")
    y += 40
    draw.text((60, y), f"Item: {data['Item']}", font=font, fill="black")
    y += 30
    draw.text((60, y), f"Quantity: {data['Qty']}  Rate: ₹{data['Rate']}  Amount: ₹{data['Amount']}", font=font, fill="black")
    y += 40

    draw.text((50, y), f"CGST (9%): ₹{data['CGST (9%)']}", font=font, fill="black")
    y += 30
    draw.text((50, y), f"SGST (9%): ₹{data['SGST (9%)']}", font=font, fill="black")
    y += 30
    draw.text((50, y), f"Total Amount Payable: ₹{data['Total']}", font=font, fill="black")

    y += 60
    draw.text((50, y), "Terms: Goods once sold will not be taken back.", font=font, fill="black")

    img.save(os.path.join(output_dir, filename))

# Generate 20 Indian-style invoices
for i in range(1, 1001):
    data = generate_invoice_data()
    filename = f"invoice_india_{i}.jpg"
    create_invoice_image(data, filename)

print(f"✅ Generated 1000 synthetic Indian invoices in: {output_dir}")
