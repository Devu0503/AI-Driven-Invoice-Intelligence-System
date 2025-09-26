# app.py — Invoice Intelligence (Phase 3)
# devu_05 gets the big dummy dataset  but can still add/create.
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

# ---- Page config:Section header
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

# def _copy_dummy_into_user_csv(csv_path: str) -> bool:
#     """Overwrite user's CSV with the master dummy CSV."""
#     if not os.path.exists(DUMMY_CSV):
#         st.error(f"Dummy CSV not found at {DUMMY_CSV}")
#         return False
#     df = pd.read_csv(DUMMY_CSV).reindex(columns=REQUIRED_COLS).fillna("")
#     _ensure_dir(os.path.dirname(csv_path))
#     df.to_csv(csv_path, index=False)
#     return True

# def _clear_table_and_seed_from_csv(csv_path: str):
#     """Wipe the invoices table in the current user DB and reseed from CSV."""
#     dbp = current_db_path()
#     _ensure_dir(os.path.dirname(dbp))
#     with sqlite3.connect(dbp) as conn:
#         cur = conn.cursor()
#         cur.execute("DELETE FROM invoices")
#         conn.commit()
#     try:
#         df = pd.read_csv(csv_path).fillna("")
#         for _, row in df.iterrows():
#             insert_row(row.to_dict())
#     except Exception as e:
#         st.warning(f"DB reseed skipped: {e}")

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
    # center the card
    left, mid, right = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">🔐 Login / Register</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Sign in to continue, or create a new account.</div>', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

        # --- LOGIN ---
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Username", placeholder="e.g., devu_05")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Login")
            if submit_login:
                if not u or not p:
                    st.warning("Please enter both username and password.")
                elif authenticate_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.user_csv = init_user_storage(u)
                    st.success(f"Welcome, {u}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        # --- REGISTER ---
        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                nu  = st.text_input("New Username", placeholder="letters, numbers, _ or -")
                npw = st.text_input("New Password", type="password", placeholder="min 6 characters")
                submit_reg = st.form_submit_button("Create account")
            if submit_reg:
                if len(nu.strip()) < 3 or len(npw) < 6:
                    st.warning("Username must be ≥ 3 chars and password ≥ 6 chars.")
                elif register_user(nu, npw):
                    st.success("User registered. Please login.")
                else:
                    st.warning("Username already exists.")

        st.markdown('</div>', unsafe_allow_html=True)


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
        # if _safe_username(u) == "devu_05":
        #     st.markdown("---")
        #     st.caption("Admin actions (demo user)")
        #     if st.button("Replace CSV with 1000‑row dummy", use_container_width=True):
        #         if _copy_dummy_into_user_csv(csv_path):
        #             _clear_table_and_seed_from_csv(csv_path)
        #             st.success("Replaced CSV and reseeded DB from dummy dataset.")
        #             st.rerun()
        #     if st.button("Reseed DB from current CSV (overwrite)", use_container_width=True):
        #         _clear_table_and_seed_from_csv(csv_path)
        #         st.success("DB reseeded from your current CSV.")

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







# # app.py — Invoice Intelligence (Phase 3)                     # App entry script with multi-user features.
# # devu_05 gets the big dummy dataset  but can still add/create. # Special-cased demo user gets seeded data.
# # All other users get an empty personal CSV + personal SQLite DB. # Everyone else starts empty per user.

# import os                                                     # stdlib for filesystem ops.
# import re                                                     # regex for username sanitization.
# import sqlite3                                                # direct SQLite access (seeding, checks).
# import pandas as pd                                           # CSV read/write and data handling.
# import streamlit as st                                        # Streamlit UI framework.

# # ---- Session state (must exist before use)
# if "logged_in" not in st.session_state:                       # Initialize login flag in session.
#     st.session_state.logged_in = False
# if "username" not in st.session_state:                        # Initialize username in session.
#     st.session_state.username = ""
# if "user_csv" not in st.session_state:                        # Initialize per-user CSV path holder.
#     st.session_state.user_csv = ""

# # ---- Page config:Section header
# st.set_page_config(page_title="Intelligence - Invoice - System", # Configure page title, favicon, layout.
#                    page_icon="📄", layout="wide")

# # ---- Local modules
# from src.auth import authenticate_user, register_user          # Auth helpers.
# from src.eda import run_eda                                   # EDA page logic.
# from src.extract import extract_from_ocr_outputs              # Batch extraction from OCR folder.
# from src.editable_table import edit_dataframe                 # Editable table UI.
# from src.visual_builder import builder                        # Plotly visual builder UI.
# from src.invoice_generator import generator                   # Invoice creation UI.
# # from src.ingest import process_upload                        # (COMMENTED) Upload handler; used later -> will break if not imported.

# # Per-user DB helpers
# from src.db import set_db_path, current_db_path, insert_row   # DB path switcher, inspector, and insert.

# # ---------- Paths & constants ----------
# USERS_DIR  = "data/users"                                     # Root folder for per-user storage.
# DUMMY_CSV  = "data/structured_csv/invoice_data.csv"           # Demo dataset (~1000 rows) for devu_05.
# REQUIRED_COLS = [                                              # Canonical CSV schema (column order).
#     "Invoice_No","Date","Time","Buyer_Name","Buyer_Address","PAN","GSTIN",
#     "Item","Qty","Rate","Amount","CGST","SGST","Total","Terms","Source_File"
# ]

# # ---------- path helpers ----------
# def _safe_username(u: str) -> str:                            # Sanitize usernames to safe filesystem tokens.
#     u = (u or "").strip().lower()
#     return re.sub(r"[^a-z0-9_-]+", "", u)                     # Keep only a–z, 0–9, underscore, hyphen.

# def _user_dir(username: str) -> str:                          # Build per-user folder.
#     return os.path.join(USERS_DIR, _safe_username(username))

# def _user_csv(username: str) -> str:                          # Path to user’s CSV file.
#     return os.path.join(_user_dir(username), "invoice_data.csv")

# def _user_db(username: str) -> str:                           # Path to user’s SQLite DB file.
#     return os.path.join(_user_dir(username), "invoices.db")

# def _ensure_dir(path: str) -> None:                           # Ensure a directory exists.
#     os.makedirs(path, exist_ok=True)

# # ---------- seeding / data utilities ----------
# def _seed_db_from_csv(csv_path: str):                         # Seed current DB from CSV if table exists and is empty.
#     """Seed currently selected DB (current_db_path()) from csv if table exists and is empty."""
#     dbp = current_db_path()                                   # Resolve DB path currently set in db layer.
#     os.makedirs(os.path.dirname(dbp), exist_ok=True)          # Ensure DB dir exists.
#     with sqlite3.connect(dbp) as conn:                        # Open direct SQLite connection.
#         cur = conn.cursor()
#         cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='invoices'")  # Table present?
#         has_table = cur.fetchone()[0] == 1
#         if not has_table:                                     # If no table, do nothing (db.init handles schema elsewhere).
#             return
#         cur.execute("SELECT COUNT(*) FROM invoices")          # Count rows to avoid reseeding.
#         if cur.fetchone()[0] > 0:
#             return  # already has rows → skip

#     try:
#         df = pd.read_csv(csv_path)                            # Load seed CSV.
#         if not df.empty:
#             for _, row in df.fillna("").iterrows():           # Iterate rows, fill NaNs with empty strings.
#                 insert_row(row.to_dict())                     # Insert via db.insert_row (respects current db path).
#     except Exception as e:
#         st.warning(f"DB seed from CSV skipped: {e}")          # Non-fatal: show warning in UI.

# # def _copy_dummy_into_user_csv(csv_path: str) -> bool:        # (COMMENTED) helper to copy demo CSV into user’s CSV.
# #     """Overwrite user's CSV with the master dummy CSV."""
# #     if not os.path.exists(DUMMY_CSV):
# #         st.error(f"Dummy CSV not found at {DUMMY_CSV}")
# #         return False
# #     df = pd.read_csv(DUMMY_CSV).reindex(columns=REQUIRED_COLS).fillna("")
# #     _ensure_dir(os.path.dirname(csv_path))
# #     df.to_csv(csv_path, index=False)
# #     return True

# # def _clear_table_and_seed_from_csv(csv_path: str):           # (COMMENTED) wipe DB table and reseed from given CSV.
# #     """Wipe the invoices table in the current user DB and reseed from CSV."""
# #     dbp = current_db_path()
# #     _ensure_dir(os.path.dirname(dbp))
# #     with sqlite3.connect(dbp) as conn:
# #         cur = conn.cursor()
# #         cur.execute("DELETE FROM invoices")
# #         conn.commit()
# #     try:
# #         df = pd.read_csv(csv_path).fillna("")
# #         for _, row in df.iterrows():
# #             insert_row(row.to_dict())
# #     except Exception as e:
# #         st.warning(f"DB reseed skipped: {e}")

# def init_user_storage(username: str) -> str:                  # Prepare per-user storage (CSV/DB), seed if needed.
#     """
#     - devu_05: on first login copy DUMMY_CSV -> data/users/devu_05/invoice_data.csv
#     - others : create empty CSV with required headers
#     For ALL: set per-user DB path; for devu_05 seed DB from CSV if DB is empty/new.
#     """
#     userdir  = _user_dir(username)                            # Compute user directory.
#     _ensure_dir(userdir)  # <-- create folder first           # Ensure it exists on disk.

#     csv_path = _user_csv(username)                            # Path to user CSV.

#     if not os.path.exists(csv_path):                          # If first time (no CSV yet)…
#         if _safe_username(username) == "devu_05" and os.path.exists(DUMMY_CSV):  # If demo user and dummy available…
#             _copy_dummy_into_user_csv(csv_path)               # (CALLS COMMENTED FUNC) Copy dummy → user CSV (bug if left commented).
#         else:
#             pd.DataFrame(columns=REQUIRED_COLS).to_csv(csv_path, index=False)  # Create empty CSV with headers.

#     # Always point DB to this user (so they can add/create)
#     _ensure_dir(os.path.dirname(_user_db(username)))          # Ensure DB folder exists.
#     set_db_path(_user_db(username))                           # Tell DB layer to use this user’s DB file.

#     # Seed devu_05 DB once from CSV if empty
#     if _safe_username(username) == "devu_05":                 # Special seeding for demo user.
#         _seed_db_from_csv(csv_path)

#     return csv_path                                           # Hand back user CSV path for session.

# def _has_data(path: str) -> bool:                             # Utility guard to check if CSV has data.
#     try:
#         return os.path.exists(path) and os.path.getsize(path) > 0 and not pd.read_csv(path).empty
#     except Exception:
#         return False

# # ----------------------------- Auth pages -----------------------------
# def login_page():                                             # Render login/register UI.
#     st.title("🔐 Login / Register")
#     tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])  # Two tabs.

#     with tab_login:                                           # Login tab contents.
#         u = st.text_input("Username")                         # Username field.
#         p = st.text_input("Password", type="password")        # Password field (masked).
#         if st.button("Login", use_container_width=True):      # Login submit button.
#             if authenticate_user(u, p):                       # Verify credentials.
#                 st.session_state.logged_in = True             # Mark as logged in.
#                 st.session_state.username = u                 # Persist username.
#                 st.session_state.user_csv = init_user_storage(u)  # Set up per-user CSV/DB (and seed for devu_05).
#                 st.success(f"Welcome, {u}!")                  # Feedback.
#                 st.rerun()                                    # Restart app flow into main_app.
#             else:
#                 st.error("Invalid username or password.")     # Auth failure message.

#     with tab_register:                                        # Register tab contents.
#         nu = st.text_input("New Username")                    # New username.
#         npw = st.text_input("New Password", type="password")  # New password.
#         if st.button("Register", use_container_width=True):   # Register submit button.
#             if register_user(nu, npw):                        # Attempt registration.
#                 st.success("User registered. Please login.")  # Success message.
#             else:
#                 st.warning("Username already exists.")        # Duplicate user warning.

# # ----------------------------- Main App -----------------------------
# def main_app():                                               # Main application after login.
#     u = st.session_state.username                             # Current user.
#     csv_path = st.session_state.user_csv or init_user_storage(u)  # Ensure CSV path in session; init if missing.
#     # ensure DB path is always set
#     set_db_path(_user_db(u))                                  # Reassert DB path (defensive).

#     # Sidebar
#     with st.sidebar:                                          # Build sidebar UI.
#         st.success(f"👤 Logged in as: **{u}**")               # Show current user.
#         if st.button("Logout", type="secondary", use_container_width=True):  # Logout button.
#             st.session_state.clear(); st.rerun()              # Clear session and restart to login.

#         st.caption(f"CSV: `{csv_path}`")                      # Show CSV path.
#         st.caption(f"DB:  `{current_db_path()}`")             # Show DB path (from db layer).
#         st.markdown("---")                                    # Separator line.

#         if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:  # If CSV exists and non-empty…
#             with open(csv_path, "rb") as f:
#                 st.download_button("⬇️ Download CSV", f.read(),         # Offer CSV download.
#                                    file_name=f"{_safe_username(u)}_invoice_data.csv",
#                                    mime="text/csv", use_container_width=True)
#         dbp = _user_db(u)                                     # Resolve user DB path.
#         if os.path.exists(dbp) and os.path.getsize(dbp) > 0:  # If DB file exists and non-empty…
#             with open(dbp, "rb") as f:
#                 st.download_button("⬇️ Download SQLite DB", f.read(),   # Offer DB download.
#                                    file_name=f"{_safe_username(u)}_invoices.db",
#                                    mime="application/octet-stream", use_container_width=True)

#         # admin tools for demo user to recover dummy quickly    # (COMMENTED) Admin actions for demo reset flows.
#         # if _safe_username(u) == "devu_05":
#         #     st.markdown("---")
#         #     st.caption("Admin actions (demo user)")
#         #     if st.button("Replace CSV with 1000-row dummy", use_container_width=True):
#         #         if _copy_dummy_into_user_csv(csv_path):
#         #             _clear_table_and_seed_from_csv(csv_path)
#         #             st.success("Replaced CSV and reseeded DB from dummy dataset.")
#         #             st.rerun()
#         #     if st.button("Reseed DB from current CSV (overwrite)", use_container_width=True):
#         #         _clear_table_and_seed_from_csv(csv_path)
#         #         st.success("DB reseeded from your current CSV.")

#         st.markdown("---")                                    # Separator line.
#         if st.button("🔍 Re-run Invoice Extraction", use_container_width=True):  # Trigger batch extraction.
#             try:
#                 extract_from_ocr_outputs("data/ocr_outputs", csv_path)  # Re-parse OCR dumps into CSV.
#                 st.success("Data extracted and saved to your CSV.")
#             except Exception as e:
#                 st.warning(f"Extraction skipped: {e}")        # Non-fatal extraction issues.

#     st.title("🧾 Invoice Intelligence — Phase 3")              # Main page header.

#     tabs = st.tabs(["📊 EDA", "✏️ Edit", "🧲 Builder", "🧾 Create Invoice", "📤 Upload"])  # App sections.

#     # ------------------ EDA ------------------
#     with tabs[0]:                                             # Tab 1: EDA.
#         if _has_data(csv_path):                                # Only run if CSV has data.
#             df = pd.read_csv(csv_path)                         # Load dataset.
#             run_eda(df)                                       # Render EDA view.
#         else:
#             st.info("Your dataset is empty. Create or upload invoices first.")  # Guidance.

#     # ------------------ Edit Table ------------------
#     with tabs[1]:                                             # Tab 2: Editable table.
#         edit_dataframe(csv_path)                               # Show/edit DataFrame and persist back.

#     # ------------------ Visual Builder ------------------
#     with tabs[2]:                                             # Tab 3: Visual builder.
#         if _has_data(csv_path):                                # Guard for data presence.
#             df = pd.read_csv(csv_path)                         # Load dataset.
#             builder(df)                                       # Launch Plotly builder UI.
#         else:
#             st.info("Your dataset is empty.")                  # Guidance.

#     # ------------------ Create Invoice -> PDF + persist ------------------
#     with tabs[3]:                                             # Tab 4: Create invoice.
#         generator(csv_path)  # writes to user CSV + inserts into user DB  # Invoke generator UI.

#     # ------------------ Upload (PDF/PNG/JPG) -> parse -> persist ------------------
#     with tabs[4]:                                             # Tab 5: Upload files for parsing.
#         st.subheader("Upload Invoices (PDF/PNG/JPG) → Auto-Extract → Save")     # Section title.
#         st.caption("PDF text is parsed with PyPDF2; images use Tesseract OCR (scanned PDFs fallback to OCR).")  # Info note.
#         files = st.file_uploader(                              # Multi-file uploader.
#             "Upload one or more invoices",
#             type=["pdf", "png", "jpg", "jpeg"],
#             accept_multiple_files=True,
#         )
#         if files:                                              # If any files selected…
#             logs = []                                          # Collect status messages.
#             for f in files:
#                 try:
#                     rec, msg = process_upload(f, csv_path)  # writes to user CSV + DB  # (WILL ERROR if import is commented!)
#                     logs.append(msg)                          # Append success message.
#                 except Exception as e:
#                     logs.append(f"❌ {f.name}: {e}")          # Capture and log error per file.
#             st.write("\n\n".join(logs))                       # Show all statuses in UI.
#             st.button("Refresh EDA", on_click=st.rerun)       # Quick refresh button.

# # ----------------------------- Entry -----------------------------
# def main():                                                   # App entry switcher.
#     if st.session_state.logged_in:                            # If authenticated…
#         main_app()                                            # Show main app.
#     else:
#         login_page()                                          # Else show auth page.

# if __name__ == "__main__":                                    # Script execution entrypoint.
#     main()                                                    # Run app.
