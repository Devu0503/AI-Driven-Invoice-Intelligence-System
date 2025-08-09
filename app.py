# app.py — Invoice Intelligence (Phase 3)

import os
import pandas as pd
import streamlit as st

# Page config (set once, at top)
st.set_page_config(page_title="Invoice Intelligence — Phase 3", page_icon="📄", layout="wide")

# --- Local modules ---
from src.auth import authenticate_user, register_user
from src.eda import run_eda
from src.extract import extract_from_ocr_outputs
from src.editable_table import edit_dataframe
from src.visual_explorer import explore
from src.invoice_generator import generator
from src.ingest import process_upload

# --- Constants ---
CSV_PATH = "data/structured_csv/invoice_data.csv"

# --- Session Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# -----------------------------
# Login / Register page
# -----------------------------
def login_page():
    st.title("🔐 Login / Register")

    tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

    with tab_login:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        # <-- explicit button for login
        if st.button("Login", use_container_width=True):
            if authenticate_user(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.success(f"Welcome, {u}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_register:
        nu = st.text_input("New Username")
        npw = st.text_input("New Password", type="password")
        # <-- explicit button for register (already present)
        if st.button("Register", use_container_width=True):
            if register_user(nu, npw):
                st.success("User registered. Please login.")
            else:
                st.warning("Username already exists.")


# -----------------------------
# Main App (after login)
# -----------------------------
def main_app():
    # Sidebar header
    with st.sidebar:
        st.success(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        st.markdown("---")
        # Optional re-extraction button if OCR .txt files are in data/ocr_outputs
        if st.button("🔍 Re-run Invoice Extraction", use_container_width=True):
            extract_from_ocr_outputs("data/ocr_outputs", CSV_PATH)
            st.success("Data extracted and saved to CSV.")

    st.title("🧾 Invoice Intelligence — Phase 3")

    # Removed ML tab
    tabs = st.tabs(["📊 EDA", "✏️ Edit", "🧲 Builder", "🧾 Create Invoice", "📤 Upload"])

    # ------------------ EDA ------------------
    with tabs[0]:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            run_eda(df)
        else:
            st.warning("Invoice CSV not found. Create or upload invoices first.")

    # ------------------ Edit Table ------------------
    with tabs[1]:
        edit_dataframe(CSV_PATH)

    # ------------------ Visual Builder ------------------
    with tabs[2]:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            explore(df)
        else:
            st.warning("Invoice CSV not found.")

    # ------------------ Create Invoice -> PDF + persist ------------------
    with tabs[3]:
        generator(CSV_PATH)

    # ------------------ Upload (PDF/PNG/JPG) -> parse -> persist ------------------
    with tabs[4]:
        st.subheader("Upload Invoices (PDF/PNG/JPG) → Auto‑Extract → Save")
        st.caption("PDF text is parsed with PyPDF2; images use Tesseract OCR (with OCR fallback for scanned PDFs).")
        files = st.file_uploader(
            "Upload one or more invoices",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        if files:
            logs = []
            for f in files:
                try:
                    rec, msg = process_upload(f, CSV_PATH)
                    logs.append(msg)
                except Exception as e:
                    logs.append(f"❌ {f.name}: {e}")
            st.write("\n\n".join(logs))
            if st.button("Refresh EDA"):
                st.rerun()


# -----------------------------
# Entry
# -----------------------------
def main():
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()


if __name__ == "__main__":
    main()
