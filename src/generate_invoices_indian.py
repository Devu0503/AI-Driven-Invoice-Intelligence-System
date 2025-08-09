import os
import random
from PIL import Image, ImageDraw, ImageFont
from faker import Faker
import pandas as pd

fake = Faker("en_IN") # Faker instance for Indian context
output_dir = "data/synthetic_invoices"
os.makedirs(output_dir, exist_ok=True)

items = ["USB Cable", "Power Bank", "Mouse", "Keyboard", "Charger", "Mobile Case", "HDMI Cable", "Earphones", "Webcam", "Laptop Stand"]
structured_data = []

def generate_invoice_data():
    qty = random.randint(1, 5)
    rate = random.randint(100, 1000)
    amount = qty * rate
    cgst = amount * 0.09
    sgst = amount * 0.09
    total = amount + cgst + sgst
    item = random.choice(items)
    return {
        "Invoice_No": fake.bothify("INV/20##/0###"),
        "Date": fake.date(),
        "Time": fake.time(),
        "Buyer_Name": fake.name(),
        "Buyer_Address": fake.address().replace("\n", ", "),
        "PAN": fake.bothify("ABCDE####F"),
        "GSTIN": fake.bothify("##ABCDE####Z#1"),
        "Item": item,
        "Qty": qty,
        "Rate": rate,
        "Amount": amount,
        "CGST": round(cgst, 2),
        "SGST": round(sgst, 2),
        "Total": round(total, 2),
        "Terms": "Goods once sold will not be taken back."
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

    for key in ["Invoice_No", "Date", "Time", "Buyer_Name", "Buyer_Address", "PAN", "GSTIN"]:
        draw.text((50, y), f"{key.replace('_', ' ')}: {data[key]}", fill="black", font=font)
        y += 40

    y += 20
    draw.text((50, y), "Item Details:", font=font, fill="black")
    y += 40
    draw.text((60, y), f"Item: {data['Item']}", font=font, fill="black")
    y += 30
    draw.text((60, y), f"Quantity: {data['Qty']}  Rate: Rs.{data['Rate']}  Amount: Rs.{data['Amount']}", font=font, fill="black")
    y += 40
    draw.text((50, y), f"CGST (9%): Rs.{data['CGST']}", font=font, fill="black")
    y += 30
    draw.text((50, y), f"SGST (9%): Rs.{data['SGST']}", font=font, fill="black")
    y += 30
    draw.text((50, y), f"Total Amount Payable: Rs.{data['Total']}", font=font, fill="black")
    y += 60
    draw.text((50, y), data["Terms"], font=font, fill="black")

    img.save(os.path.join(output_dir, filename))

# Generate and save data
for i in range(1, 1001):
    data = generate_invoice_data()
    filename = f"invoice_india_{i}.jpg"
    create_invoice_image(data, filename)
    data["Source_File"] = filename
    structured_data.append(data)

df = pd.DataFrame(structured_data)
csv_output_path = "data/structured_csv/invoice_data.csv"
os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
df.to_csv(csv_output_path, index=False)
print(f" Generated 1000 invoices and saved to {csv_output_path}")
