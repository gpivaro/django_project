```
clinic_dash_pro/README.md
```

---

# 📘 **Clinic Dash Pro**

**Clinic Dash Pro** is a full‑stack Django application designed to unify financial, operational, and clinical data for healthcare clinics. It ingests raw data from multiple external systems — **Gusto**, **Xero**, and **Jane** — normalizes and deduplicates records, stores them in a unified database, and generates financial dashboards, charts, and reports.

This project provides:

- Automated ingestion pipelines
- Unified financial reporting
- Interactive charts
- Generic list views with filtering, sorting, pagination, and export
- A complete test suite
- A clean, extensible architecture

---

## 🚀 **Features**

### 🔹 Multi‑Source Data Ingestion

Supports ingestion from:

- **Gusto Payroll** (CSV)
- **Xero Transactions** (XLSX)
- **Jane Sessions** (CSV)
- **Jane Processed Claims** (CSV)

Each ingestion pipeline includes:

- File validation
- Column validation
- Data normalization
- Composite dedupe keys
- Safe database insertion
- Error reporting
- Inserted / skipped / updated row counts

---

### 🔹 Unified Financial Reporting

The reporting engine merges data from all sources to produce:

- Income Statement
- Unified Financials
- Therapist Profitability
- Operating Expenses Breakdown
- Revenue Details
- Monthly Operational Reports

All reports are available through the dashboard and can be exported.

---

### 🔹 Interactive Charts

Charts are generated using Chart.js and include:

- Income Statement Chart
- Unified Financials Chart
- Therapist Profitability Chart
- Monthly YOY Expense Chart
- Monthly Account Trend Chart

Charts support:

- Dynamic filtering
- Positive‑value normalization
- Custom tooltips
- Legend alignment
- Multi‑series rendering

---

### 🔹 Generic List View System

All ORM and DataFrame tables use a unified list view with:

- Filtering
- Sorting
- Pagination
- Export to CSV/XLSX
- Dynamic field exclusion
- JSON‑safe DF export

This keeps the UI consistent across all data types.

---

### 🔹 Full Test Suite

The project includes automated tests for:

- Authentication
- Staff‑only protection
- POST protection
- ORM list view behavior
- Export correctness
- Report math validation
- Pagination and sorting
- Ingestion logic

---

## 🏗️ **Project Structure**

```
clinic_dash_pro/
│   admin.py
│   apps.py
│   exports.py
│   models.py
│   urls.py
│   views.py
│
├── helper/
│   └── helper.py
│
├── ingestion/
│   ├── database.py
│   ├── gusto.py
│   ├── jane.py
│   ├── xero.py
│
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_janesessions_invoice_number_janesessions_payer.py
│   ├── 0003_janesessions_updated_date.py
│   └── 0004_gustopayroll_updated_date_and_more.py
│
├── reports/
│   ├── accrual_reports.py
│   ├── analyze_financias.py
│   ├── expenses_reports.py
│   ├── generate_reports.py
│   ├── revenue_report.py
│   └── unified_reports.py
│
├── services/
│   ├── chart_generator.py
│   └── data_pipeline.py
│
├── static/clinic_dash_pro/
│   ├── charts/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/clinic_dash_pro/
│   ├── home.html
│   ├── list_view.html
│   ├── report_home.html
│   ├── upload_gusto.html
│   ├── upload_jane_processed_claims.html
│   ├── upload_jane_sessions.html
│   ├── upload_success.html
│   └── upload_xero.html
│
├── templatetags/
│   ├── format_extras.py
│   └── getattr_extras.py
│
└── tests/
    ├── test_auth.py
    ├── test_exportcontent.py
    ├── test_listviews.py
    ├── test_orm_generic_list_view.py
    ├── test_postprotection.py
    ├── test_reportmath.py
    ├── test_staffonly.py
```

---

## ⚙️ **Installation**

### 1. Clone the repository

```bash
git clone https://github.com/yourrepo/clinic_dash_pro.git
cd clinic_dash_pro
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Run the server

```bash
python manage.py runserver
```

---

## 📥 **Data Ingestion Workflow**

Each upload page follows the same pattern:

1. User uploads a file
2. File is validated
3. Ingestion pipeline runs
4. Errors are captured and shown
5. Inserted/skipped/updated counts are stored
6. User is redirected to a success page

Success pages show:

- Total rows
- Date range
- Inserted/skipped/updated
- Any ingestion errors
- Link to upload additional files

---

## 📊 **Reporting Workflow**

The reporting engine:

1. Loads all ORM data
2. Normalizes and merges datasets
3. Computes financial metrics
4. Converts results to DataFrames
5. Converts DataFrames to JSON for charts
6. Renders charts and tables in templates

---

## 📤 **Exporting Data**

Exports support:

- ORM → CSV/XLSX
- DataFrame → CSV/XLSX
- Full filtered dataset (pagination ignored)

Exports use:

- `filtered_ids` for ORM
- `df_export` for DataFrames

---

## 🧪 **Testing**

Run all tests:

```bash
pytest
```

Tests cover:

- Authentication
- Staff-only access
- POST protection
- List view behavior
- Export correctness
- Report math
- Ingestion logic

---

## 🛠️ **Development Notes**

- All ingestion pipelines use composite dedupe keys
- All upload views use unified session keys
- All success pages use a shared template
- All list views use `generic_list_view`
- All charts use Chart.js
- All reports use Pandas DataFrames

---

## 📄 **License**

This project is proprietary and not licensed for public distribution.

---

## 🙌 **Contributors**

- **Gabriel Pivaro** — Lead Developer
- **Clinic Dash Pro Team**

---
