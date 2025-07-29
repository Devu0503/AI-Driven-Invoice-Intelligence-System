
# 📄 AI-Driven Invoice Intelligence System – Phase 2

This project is built to extract, structure, analyze, and manage invoice data using OCR, NLP, and visualization tools. The project follows a phased development approach. **Phase 2 introduces Streamlit-based visualization and SQLite integration**, extending the basic CSV extraction done in Phase 1.

---

## 🔄 Phase Comparison

| Feature                         | Phase 1                      | Phase 2                        |
|---------------------------------|------------------------------|--------------------------------|
| OCR Extraction                  | ✅ Yes                       | ✅ Improved                    |
| CSV Structuring                | ✅ Yes                       | ✅ Yes                         |
| Streamlit Dashboard            | ❌ **Not included**          | ✅ **Introduced**             |
| EDA Visualizations              | ❌ No                        | ✅ Barplot, Pie, Heatmap, etc. |
| SQLite Storage                  | ❌ No                        | ✅ `invoice_data.db`           |
| Data Cleaning & Filtering       | ❌ No                        | ✅ Drop nulls, drop columns    |

---

## ✅ What's New in Phase 2

### 📁 New Files & Folders

| Path                                  | Description |
|---------------------------------------|-------------|
| `data/synthetic_invoices/`            | *(NEW)* Folder to store synthetic invoices. |
| `invoice_data.db`                     | *(NEW)* SQLite database created from structured CSV. |
| `src/eda.py`                          | *(NEW)* EDA logic and dashboard visualization via Streamlit. |

---

## ⚙️ New Functionalities in Phase 2

### ✅ Streamlit Dashboard
- **Streamlit UI added** for interactive dashboard.
- Replaces manual EDA with an intuitive interface.

### ✅ Data Cleaning
- Drops all rows with missing values (`df.dropna()`).
- Drops unnecessary or sensitive columns:
  - `GSTIN`, `PAN`, `Terms`, `Source_File`

### ✅ Save to SQLite
- Saves cleaned data to `invoice_data.db` using `df.to_sql()`.

### 📊 Enhanced Visualizations
- Raw Data Table
- Column Types & Nulls Summary
- Top 10 Items by Quantity (Barplot)
- Distribution of Amount or Total (Histogram + KDE)
- Boxplot of Rates
- Correlation Heatmap
- Terms Pie Chart
- Daily Total Trend (Lineplot)
- Hourly Time Distribution (Barplot)

---

## 📂 Folder Structure (Updated)

```

AI\_DRIVEN\_INVOICE\_INTELLIGENCE\_SYSTEM/
├── app.py
├── invoice\_data.db                    # (New) SQLite DB file
├── data/
│   ├── ocr\_outputs/
│   ├── raw\_invoices/
│   ├── structured\_csv/
│   │   └── invoice\_data.csv
│   ├── synthetic\_invoices/           # (New)
│   └── user.json
├── src/
│   ├── auth.py
│   ├── eda.py                        # (New)
│   ├── extract.py
│   ├── generate\_invoices\_indian.py
│   ├── ocr.py
│   ├── user.json
│   └── utils.py

````

---

## 🚀 Run Instructions

1. Ensure `invoice_data.csv` is present in `data/structured_csv/`.
2. Run the Streamlit app:

```bash
streamlit run app.py
````

3. Login or Register.
4. Dashboard will show:

   * Invoice extraction button.
   * EDA summary.
   * Option to save data to SQLite.


