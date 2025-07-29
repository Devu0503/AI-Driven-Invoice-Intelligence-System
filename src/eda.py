import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

def run_eda(df):
    st.subheader("📄 Raw Data")
    st.dataframe(df)
  # 🔻 Drop all rows with any missing values
    columns_to_drop = ['GSTIN', 'PAN', 'Terms']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # 🔻 Drop rows with any nulls
    df = df.dropna()

    # --- Save to SQLite ---
    st.subheader("🗄️ Save Raw Data to SQLite")
    if st.button("💾 Save to Database"):
        try:
            conn = sqlite3.connect("invoice_data.db")
            df.to_sql("invoices", conn, if_exists="replace", index=False)
            conn.close()
            st.success("✅ Data saved to SQLite database: `invoice_data.db`")
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")

    # --- Optional: Filter by Source File ---
    if 'Source_File' in df.columns:
        selected_file = st.selectbox("📂 Filter by Source File", options=["All"] + sorted(df['Source_File'].unique().tolist()))
        if selected_file != "All":
            df = df[df["Source_File"] == selected_file]

    st.subheader("📊 Basic Info:")
    st.dataframe(df.describe(include='all'))

    st.subheader("📌 Column Types with Null Count:")
    st.write(df.dtypes.astype(str) + " | Nulls: " + df.isnull().sum().astype(str))

    st.subheader("📉 Missing Values:")
    st.write(df.isnull().sum())
   

    st.subheader("📌 Value Counts (Top 3):")
    for col in df.columns:
        if df[col].dtype == "object":
            st.write(f"🔸 {col}")
            st.write(df[col].value_counts().head(3))

    # 📦 Top 10 Items by Quantity
    st.subheader("📦 Top 10 Buyer_Name by Quantity")
    if 'Buyer_Name' in df.columns and 'Qty' in df.columns:
        try:
            qty_df = df.groupby('Buyer_Name')['Qty'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots()
            sns.barplot(x=qty_df.values, y=qty_df.index, ax=ax)
            ax.set_title("Top 10 Items by Quantity")
            ax.set_xlabel("Total Quantity")
            ax.set_ylabel("Buyer_Name")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Couldn't generate quantity chart: {e}")

    # 📈 Distribution of Amount / Total
    st.subheader("📈 Distribution of Amount / Total")
    num_col = 'Amount' if 'Amount' in df.columns else 'Total'
    if num_col in df.columns:
        try:
            fig, ax = plt.subplots()
            sns.histplot(df[num_col].dropna(), kde=True, ax=ax, bins=30)
            ax.set_title(f"Distribution of {num_col}")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Histogram failed: {e}")

    # 📉 Boxplot of Rates
    st.subheader("📉 Boxplot of Rates")
    if 'Rate' in df.columns:
        try:
            fig, ax = plt.subplots()
            sns.boxplot(x=df['Rate'].dropna(), ax=ax)
            ax.set_title("Boxplot of Item Rates")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Boxplot failed: {e}")

    # 🧩 Correlation Heatmap
    st.subheader("🧩 Correlation Heatmap (Numerical Columns)")
    numeric_cols = df.select_dtypes(include=['int64', 'float64'])
    if not numeric_cols.empty:
        fig, ax = plt.subplots()
        corr = numeric_cols.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # 🥧 Terms Distribution
    st.subheader("🥧 Terms Distribution (Pie Chart)")
    if 'Terms' in df.columns:
        try:
            terms_counts = df['Terms'].value_counts().head(5)
            fig, ax = plt.subplots()
            ax.pie(terms_counts, labels=terms_counts.index, autopct='%1.1f%%', startangle=90)
            ax.set_title("Top Terms Distribution")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Pie chart error: {e}")

    # 📅 Daily Total Trend
    st.subheader("📅 Daily Invoice Total Trend")
    if 'Date' in df.columns and 'Total' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            if df['Date'].isnull().all():
                st.warning("Date conversion failed.")
            else:
                daily_total = df.groupby(df['Date'].dt.date)['Total'].sum()
                fig, ax = plt.subplots()
                daily_total.plot(kind='line', ax=ax)
                ax.set_title("Total Amount Over Time")
                ax.set_ylabel("Total ₹")
                st.pyplot(fig)
        except Exception as e:
            st.warning(f"Date trend failed: {e}")

    # 🕓 Hourly Invoice Time Distribution
    st.subheader("🕓 Invoice Time Distribution")
    if 'Time' in df.columns:
        try:
            df['Hour'] = pd.to_datetime(df['Time'], format="%H:%M:%S", errors='coerce').dt.hour
            if df['Hour'].isnull().all():
                st.warning("Time format parsing failed.")
            else:
                fig, ax = plt.subplots()
                sns.countplot(x='Hour', data=df, ax=ax)
                ax.set_title("Invoices by Hour of Day")
                st.pyplot(fig)
        except Exception as e:
            st.warning(f"Hour-wise chart failed: {e}")
