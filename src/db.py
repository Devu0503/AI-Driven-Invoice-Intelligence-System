# src/db.py
import sqlite3
import os

DB_PATH = "data/invoices.db"

def init_db():
    """Initialize the database and create table if not exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            Invoice_No TEXT,
            Date TEXT,
            Time TEXT,
            Buyer_Name TEXT,
            Buyer_Address TEXT,
            Item TEXT,
            Qty REAL,
            Rate REAL,
            Amount REAL,
            CGST REAL,
            SGST REAL,
            Total REAL,
            Terms TEXT,
            Source_File TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_row(row: dict):
    """Insert one invoice row into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices (
            Invoice_No, Date, Time, Buyer_Name, Buyer_Address,
            Item, Qty, Rate, Amount, CGST, SGST, Total, Terms, Source_File
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("Invoice_No"),
        row.get("Date"),
        row.get("Time"),
        row.get("Buyer_Name"),
        row.get("Buyer_Address"),
        row.get("Item"),
        row.get("Qty"),
        row.get("Rate"),
        row.get("Amount"),
        row.get("CGST"),
        row.get("SGST"),
        row.get("Total"),
        row.get("Terms"),
        row.get("Source_File", "manual_entry_html")
    ))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
