# app.py — Invoice Intelligence (Phase 3)
# devu_05 gets the big dummy dataset (copied once) but can still add/create.
# All other users get an empty personal CSV + personal SQLite DB.

import os
import re
import sqlite3
import pandas as pd
import streamlit as st

# ---- Session state (must exist before use)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_csv" not in st.session_state:
    st.session_state.user_csv = ""

# ---- Page config
st.set_page_config(page_title="Intelligence - Invoice - System",
                   page_icon="📄", layout="wide")

# ---- Local modules
from src.auth import authenticate_user, register_user
from src.eda import run_eda
from src.extract import extract_from_ocr_outputs
from src.editable_table import edit_dataframe
from src.visual_builder import builder
from src.invoice_generator import generator
from src.ingest import process_upload

# Per-user DB helpers
from src.db import set_db_path, current_db_path, insert_row

# ---------- Paths & constants ----------
USERS_DIR  = "data/users"
DUMMY_CSV  = "data/structured_csv/invoice_data.csv"   # master dummy with ~1000 rows
REQUIRED_COLS = [
    "Invoice_No","Date","Time","Buyer_Name","Buyer_Address","PAN","GSTIN",
    "Item","Qty","Rate","Amount","CGST","SGST","Total","Terms","Source_File"
]

# ---------- path helpers ----------
def _safe_username(u: str) -> str:
    u = (u or "").strip().lower()
    return re.sub(r"[^a-z0-9_-]+", "", u)

def _user_dir(username: str) -> str:
    return os.path.join(USERS_DIR, _safe_username(username))

def _user_csv(username: str) -> str:
    return os.path.join(_user_dir(username), "invoice_data.csv")

def _user_db(username: str) -> str:
    return os.path.join(_user_dir(username), "invoices.db")

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

# ---------- seeding / data utilities ----------
def _seed_db_from_csv(csv_path: str):
    """Seed currently selected DB (current_db_path()) from csv if table exists and is empty."""
    dbp = current_db_path()
    os.makedirs(os.path.dirname(dbp), exist_ok=True)
    with sqlite3.connect(dbp) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='invoices'")
        has_table = cur.fetchone()[0] == 1
        if not has_table:
            return
        cur.execute("SELECT COUNT(*) FROM invoices")
        if cur.fetchone()[0] > 0:
            return  # already has rows → skip

    try:
        df = pd.read_csv(csv_path)
        if not df.empty:
            for _, row in df.fillna("").iterrows():
                insert_row(row.to_dict())
    except Exception as e:
        st.warning(f"DB seed from CSV skipped: {e}")

def _copy_dummy_into_user_csv(csv_path: str) -> bool:
    """Overwrite user's CSV with the master dummy CSV."""
    if not os.path.exists(DUMMY_CSV):
        st.error(f"Dummy CSV not found at {DUMMY_CSV}")
        return False
    df = pd.read_csv(DUMMY_CSV).reindex(columns=REQUIRED_COLS).fillna("")
    _ensure_dir(os.path.dirname(csv_path))
    df.to_csv(csv_path, index=False)
    return True

def _clear_table_and_seed_from_csv(csv_path: str):
    """Wipe the invoices table in the current user DB and reseed from CSV."""
    dbp = current_db_path()
    _ensure_dir(os.path.dirname(dbp))
    with sqlite3.connect(dbp) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM invoices")
        conn.commit()
    try:
        df = pd.read_csv(csv_path).fillna("")
        for _, row in df.iterrows():
            insert_row(row.to_dict())
    except Exception as e:
        st.warning(f"DB reseed skipped: {e}")

def init_user_storage(username: str) -> str:
    """
    - devu_05: on first login copy DUMMY_CSV -> data/users/devu_05/invoice_data.csv
    - others : create empty CSV with required headers
    For ALL: set per-user DB path; for devu_05 seed DB from CSV if DB is empty/new.
    """
    userdir  = _user_dir(username)
    _ensure_dir(userdir)  # <-- create folder first

    csv_path = _user_csv(username)

    if not os.path.exists(csv_path):
        if _safe_username(username) == "devu_05" and os.path.exists(DUMMY_CSV):
            _copy_dummy_into_user_csv(csv_path)
        else:
            pd.DataFrame(columns=REQUIRED_COLS).to_csv(csv_path, index=False)

    # Always point DB to this user (so they can add/create)
    _ensure_dir(os.path.dirname(_user_db(username)))
    set_db_path(_user_db(username))

    # Seed devu_05 DB once from CSV if empty
    if _safe_username(username) == "devu_05":
        _seed_db_from_csv(csv_path)

    return csv_path

def _has_data(path: str) -> bool:
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0 and not pd.read_csv(path).empty
    except Exception:
        return False

# ----------------------------- Auth pages -----------------------------
def login_page():
    st.title("🔐 Login / Register")
    tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

    with tab_login:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if authenticate_user(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.user_csv = init_user_storage(u)  # sets per-user CSV+DB (and seeds for devu_05)
                st.success(f"Welcome, {u}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_register:
        nu = st.text_input("New Username")
        npw = st.text_input("New Password", type="password")
        if st.button("Register", use_container_width=True):
            if register_user(nu, npw):
                st.success("User registered. Please login.")
            else:
                st.warning("Username already exists.")

# ----------------------------- Main App -----------------------------
def main_app():
    u = st.session_state.username
    csv_path = st.session_state.user_csv or init_user_storage(u)
    # ensure DB path is always set
    set_db_path(_user_db(u))

    # Sidebar
    with st.sidebar:
        st.success(f"👤 Logged in as: **{u}**")
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.clear(); st.rerun()

        st.caption(f"CSV: `{csv_path}`")
        st.caption(f"DB:  `{current_db_path()}`")
        st.markdown("---")
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            with open(csv_path, "rb") as f:
                st.download_button("⬇️ Download CSV", f.read(),
                                   file_name=f"{_safe_username(u)}_invoice_data.csv",
                                   mime="text/csv", use_container_width=True)
        dbp = _user_db(u)
        if os.path.exists(dbp) and os.path.getsize(dbp) > 0:
            with open(dbp, "rb") as f:
                st.download_button("⬇️ Download SQLite DB", f.read(),
                                   file_name=f"{_safe_username(u)}_invoices.db",
                                   mime="application/octet-stream", use_container_width=True)

        # admin tools for demo user to recover dummy quickly
        if _safe_username(u) == "devu_05":
            st.markdown("---")
            st.caption("Admin actions (demo user)")
            if st.button("Replace CSV with 1000‑row dummy", use_container_width=True):
                if _copy_dummy_into_user_csv(csv_path):
                    _clear_table_and_seed_from_csv(csv_path)
                    st.success("Replaced CSV and reseeded DB from dummy dataset.")
                    st.rerun()
            if st.button("Reseed DB from current CSV (overwrite)", use_container_width=True):
                _clear_table_and_seed_from_csv(csv_path)
                st.success("DB reseeded from your current CSV.")

        st.markdown("---")
        if st.button("🔍 Re-run Invoice Extraction", use_container_width=True):
            try:
                extract_from_ocr_outputs("data/ocr_outputs", csv_path)
                st.success("Data extracted and saved to your CSV.")
            except Exception as e:
                st.warning(f"Extraction skipped: {e}")

    st.title("🧾 Invoice Intelligence — Phase 3")

    tabs = st.tabs(["📊 EDA", "✏️ Edit", "🧲 Builder", "🧾 Create Invoice", "📤 Upload"])

    # ------------------ EDA ------------------
    with tabs[0]:
        if _has_data(csv_path):
            df = pd.read_csv(csv_path)
            run_eda(df)
        else:
            st.info("Your dataset is empty. Create or upload invoices first.")

    # ------------------ Edit Table ------------------
    with tabs[1]:
        edit_dataframe(csv_path)

    # ------------------ Visual Builder ------------------
    with tabs[2]:
        if _has_data(csv_path):
            df = pd.read_csv(csv_path)
            builder(df)
        else:
            st.info("Your dataset is empty.")

    # ------------------ Create Invoice -> PDF + persist ------------------
    with tabs[3]:
        generator(csv_path)  # writes to user CSV + inserts into user DB

    # ------------------ Upload (PDF/PNG/JPG) -> parse -> persist ------------------
    with tabs[4]:
        st.subheader("Upload Invoices (PDF/PNG/JPG) → Auto‑Extract → Save")
        st.caption("PDF text is parsed with PyPDF2; images use Tesseract OCR (scanned PDFs fallback to OCR).")
        files = st.file_uploader(
            "Upload one or more invoices",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        if files:
            logs = []
            for f in files:
                try:
                    rec, msg = process_upload(f, csv_path)  # writes to user CSV + DB
                    logs.append(msg)
                except Exception as e:
                    logs.append(f"❌ {f.name}: {e}")
            st.write("\n\n".join(logs))
            st.button("Refresh EDA", on_click=st.rerun)

# ----------------------------- Entry -----------------------------
def main():
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main()
