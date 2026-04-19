# PayCore 
## Salary Processing Management System

A complete, production-ready HR & Payroll management tool for companies of any size.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python run.py
```

### Default Login Credentials
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | Admin |
| hr       | hr1234    | HR    |

---

## 📁 Project Structure

```
paycore_enterprise/
├── run.py                  ← Launch script
├── requirements.txt
├── README.md
├── data/                   ← ALL DATA STORED HERE (JSON files)
│   ├── employees.json      ← Employee records
│   ├── users.json          ← User accounts & hashed passwords
│   ├── payments.json       ← Payment history
│   ├── payroll_runs.json   ← Payroll run records
│   └── audit_log.json      ← Complete audit trail
└── paycore/                ← Application source code
    ├── main.py             ← Main window
    ├── login.py            ← Login screen
    ├── database.py         ← JSON data backend
    ├── tabs.py             ← All tab panels
    ├── dialogs.py          ← Dialogs (employee, payment, etc.)
    ├── widgets.py          ← Reusable UI components
    └── styles.py           ← Qt stylesheets & theme
```

---

## ✅ Features

### 🔐 Security / Login
- Secure login screen with hashed passwords (SHA-256)
- Role-based access (Admin, HR)
- Change password functionality
- Logout button
- Session tracking with last-login timestamps

### 📊 Dashboard
- Live KPI cards: Total Employees, Monthly Payroll, Avg Net Salary, % Processed
- Department payroll breakdown bar chart
- 12-month payroll trend chart
- Statutory compliance status panel (PF, ESI, TDS, PT)

### ▶ Payroll Runs
- Run payroll for any month with one click
- Full payroll run history with date, amount, employee count
- All runs persisted to `data/payroll_runs.json`

### 💳 Payments
- Process individual salary payments
- Payment method: Bank Transfer / Cheque / Cash / UPI
- View pending payments for current month
- Full payment history table
- All payments persisted to `data/payments.json`

### 👥 Employees
- Full employee register with all salary fields
- Add / Edit / Delete employees (persisted to `data/employees.json`)
- Search by name, ID, department, location
- Filter by department
- Color-coded net salary (green/amber/red)
- Pay status badges (Paid / Review / Hold)

### 🧾 Pay Slips
- Generate full pay slip for any employee by ID
- Shows: earnings breakdown, deductions, net salary, payment status
- Company-branded, system-generated slip format

### 📈 Department Analytics
- Pie chart: headcount by department
- Bar chart: average net salary by department
- Summary table with totals and averages

### 📋 Reports & Audit
- **Audit Log**: Every action logged with timestamp (add/edit/delete employee, payments, payroll runs)
- **Salary Summary**: Department-wise gross, deductions, net salary breakdown

### 🧮 Payroll Computation (Auto-calculated)
| Component        | Formula                              |
|-----------------|--------------------------------------|
| HRA             | 20% of Basic                         |
| DA              | 15% of Basic                         |
| Travel Allow.   | ₹1,500 flat                          |
| Gross Salary    | Basic + HRA + DA + TA + Bonus        |
| PF              | 12% of Basic                         |
| ESI             | 1.75% of Basic                       |
| Professional Tax| ₹200 flat                            |
| TDS             | 10% if Gross > 50k, 5% if > 30k     |
| Net Salary      | (Gross − Deductions) × Attendance    |
| Pay Status      | Paid ≥90% | Review ≥75% | Hold <75% |

---

## 💾 Data Storage

All data is stored as human-readable JSON files in the `data/` folder:

- **employees.json** — Raw employee records (recomputed on load)
- **users.json** — User accounts with SHA-256 hashed passwords
- **payments.json** — Complete payment history
- **payroll_runs.json** — Payroll run records
- **audit_log.json** — Timestamped audit trail of all actions

No database server required. Data persists across sessions automatically.

---

## 🔧 Dependencies

- **PyQt5** — GUI framework
- **pandas** — Data manipulation & analytics
- **matplotlib** — Charts and visualizations

> Note: PySpark dependency removed. All computation done with pure Python/pandas for easier deployment.

---
