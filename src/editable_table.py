# src/editable_table.py
import streamlit as st
import pandas as pd
import os

def edit_dataframe(csv_path: str):
    st.markdown("### 📤 Editable Data Table")
    if not os.path.exists(csv_path):
        st.error("CSV not found. Upload or extract first.")
        return

    df = pd.read_csv(csv_path)
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if st.button("💾 Save edits back to CSV"):
        edited.to_csv(csv_path, index=False)
        st.success("Saved!")
