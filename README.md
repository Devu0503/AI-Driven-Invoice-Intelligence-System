

📊 AI-Driven Invoice Intelligence System

An end-to-end AI + OCR + Data Intelligence solution for automating invoice management, from extraction to analytics and editing.
The project is built in 4 incremental phases, with each phase adding new features and capabilities.

Deployed link of the project
https://ai-driven-invoice-intelligence-system-phase-5.streamlit.app/

📅 Project Phases Overview

| Phase    | Focus Area                | Key Features                                                                |
| ---------| ------------------------- | --------------------------------------------------------------------------- |
|  Phase 1 | OCR Extraction            | Generate invoices, extract text, structure data into CSV                    |
|  Phase 2 | EDA & SQLite              | Streamlit dashboard, EDA visualizations, database integration               |
|  Phase 3 | Invoice Builder & Editor  | Create, edit, and upload invoices directly from UI                          |
|  Phase 4 | User-Specific Data Access | Multi-user system, `devu_05` seeded with 2000+ invoices, others start empty |



 📂 Project Structure

```
AI_DRIVEN_INVOICE_INTELLIGENCE_SYSTEM/
├── app.py                               # Main Streamlit app
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
│
├── data/
│   ├── raw_invoices/                    # Uploaded or scanned invoice images
│   ├── ocr_outputs/                     # Raw OCR text files
│   ├── structured_csv/
│   │   └── invoice_data.csv             # Final structured CSV (per user)
│   ├── synthetic_invoices/              # Phase 1 generated invoices
│   └── users/                           # Per-user CSV & DB storage
│
├── src/
│   ├── auth.py                          # User authentication
│   ├── eda.py                           # EDA & visualizations
│   ├── extract.py                       # OCR text parsing & field extraction
│   ├── generate_invoices_indian.py      # Synthetic invoice generator
│   ├── ocr.py                           # OCR with pytesseract
│   ├── utils.py                         # Utility functions
│   └── db.py                            # SQLite database operations
```


## 🚀 Phase-wise Features

### **Phase 1 – OCR & CSV Structuring**

* Generate **synthetic Indian-style invoices**.
* Perform **OCR** using `pytesseract`.
* Extract fields via **regex & parsing**:

  * Invoice No, Date, Buyer Name, Buyer Address, PAN, GSTIN, Items, Quantity, Rate, Amount, Taxes, Total, Terms.
* Save extracted records to `data/structured_csv/invoice_data.csv`.


Phase 2 – EDA Dashboard & Database
Streamlit dashboard with:

 Raw data table
 Column summaries
 Top items analysis
 Sales trends
 Correlation heatmaps
 Distribution plots
 Data cleaning (drop nulls & sensitive columns).
Store cleaned data in SQLite(`invoice_data.db`).



Phase 3 – Invoice Builder & Editor

Create invoices directly in UI.
Edit existing invoices.
Upload invoices for OCR & auto-extraction.
Download or print generated invoices.


Phase 4 – Multi-User Mode with Preloaded Data

 User-based storage:

   Each user gets their own CSV & DB.
  `devu_05`account is preloaded with 2000+ invoices for instant EDA access.
   Other users start with an empty database.
 Secure login & registration system.




## 📌 Usage Guide

1. Login / Register via the app.
2. If `devu_05` – you’ll see preloaded data with full EDA.
3. Other users – start fresh and upload invoices.
4. Create / Edit / Upload invoices  interface.
5. Analyze data in the EDA dashboard.



## 📊 Example Visualizations

* Top 10 sold items (bar chart)
* Daily revenue trend (line chart)
* GST distribution (pie chart)
* Price variation (box plot)
* Correlation between numeric fields (heatmap)


## 📌 Tech Stack

Python (Pandas, NumPy, Regex, PyTesseract, Matplotlib, Seaborn, Plotly)
Streamlit (Interactive Dashboard)
SQLite (Data storage)
PIL (Invoice generation)
OS / Pathlib (File handling)


##
Made by 
Devanshi Gupta
