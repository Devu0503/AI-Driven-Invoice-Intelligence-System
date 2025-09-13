import streamlit as st
import os
import sys
import pandas as pd

# --- Setup path to src ---
sys.path.append(os.path.abspath("src"))

from src.auth import authenticate_user, register_user
from src.eda import run_eda
from src.extract import extract_from_ocr_outputs

# --- Constants ---
CSV_PATH = "data/structured_csv/invoice_data.csv"

# --- Session State Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Login Page ---
def login_page():
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password.")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("✅ Registration successful. Please login.")
            else:
                st.warning("⚠️ Username already exists.")

# --- Main App ---
def main_app():
    st.sidebar.success(f"👤 Logged in as: {st.session_state.username}")
    st.title("📄 AI-Driven Invoice Intelligence Dashboard")

    # # --- Re-run Extraction ---
    # if st.sidebar.button("🔍 Re-run Invoice Extraction"):
    #     extract_from_ocr_outputs("data/ocr_outputs", CSV_PATH)
    #     st.sidebar.success("✅ Data extracted and saved to CSV!")

    # --- Load and Run EDA ---
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

        # Optional message about SQLite
        st.info("ℹ️ After analysis, use the '💾 Save to Database' button to store results into SQLite.")

        run_eda(df)
    else:
        st.warning("⚠️ Invoice data not found. Please extract invoices first.")

# --- Entry Point ---
def main():
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main()
