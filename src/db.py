# src/db.py
# Per-user SQLite handling: app sets the DB file with set_db_path().
# insert_row() always writes into the currently selected DB.

import os
import sqlite3

# Current DB path (app will override via set_db_path)
_DB_PATH = os.environ.get("INVOICE_DB_PATH", os.path.join("data", "invoices.db"))

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS invoices (
    Invoice_No    TEXT,
    Date          TEXT,
    Time          TEXT,
    Buyer_Name    TEXT,
    Buyer_Address TEXT,
    Item          TEXT,
    Qty           REAL,
    Rate          REAL,
    Amount        REAL,
    CGST          REAL,
    SGST          REAL,
    Total         REAL,
    Terms         TEXT,
    Source_File   TEXT
)
"""

def set_db_path(path: str) -> None:
    """
    Point the DB layer to a specific SQLite file (e.g., data/users/<user>/invoices.db).
    Ensures folder exists and schema is initialized.
    """
    global _DB_PATH
    _DB_PATH = path
    init_db()

def current_db_path() -> str:
    """Return the absolute/relative path of the DB currently in use."""
    return _DB_PATH

def _connect():
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    return sqlite3.connect(_DB_PATH, check_same_thread=False)

def init_db() -> None:
    """Create invoices table if it doesn't exist."""
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(_SCHEMA_SQL)
        conn.commit()

def insert_row(row: dict) -> None:
    """
    Insert a single invoice record into the current DB.
    Expects keys aligned with CSV headers used by the app.
    """
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO invoices (
                Invoice_No, Date, Time, Buyer_Name, Buyer_Address,
                Item, Qty, Rate, Amount, CGST, SGST, Total, Terms, Source_File
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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
                row.get("Source_File", "manual_entry_html"),
            ),
        )
        conn.commit()

# Initialize a default DB so module always works (app will override per-user)
init_db()
