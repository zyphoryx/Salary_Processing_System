"""PayCore — JSON Data Backend (extended: profile, themes, bonus, bulk pay)"""

import json, hashlib, os
from datetime import datetime
from pathlib import Path

_HERE    = Path(__file__).parent
DATA_DIR = _HERE.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

EMPLOYEES_FILE    = DATA_DIR / "employees.json"
USERS_FILE        = DATA_DIR / "users.json"
PAYMENTS_FILE     = DATA_DIR / "payments.json"
PAYROLL_RUNS_FILE = DATA_DIR / "payroll_runs.json"
AUDIT_FILE        = DATA_DIR / "audit_log.json"
SETTINGS_FILE     = DATA_DIR / "settings.json"

def _read(path):
    if path.exists():
        with open(path, encoding="utf-8") as f: return json.load(f)
    return []

def _write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()
def _now():    return datetime.now().isoformat(timespec="seconds")

# ── Settings (theme, etc.) ─────────────────────────────────────────────────────
def get_settings() -> dict:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, encoding="utf-8") as f: return json.load(f)
    return {"theme": "light"}

def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ── Users / Auth ───────────────────────────────────────────────────────────────
def _seed_users():
    users = _read(USERS_FILE)
    if not users:
        users = [
            {"user_id":"U001","username":"admin","password_hash":_hash("admin123"),
             "full_name":"System Administrator","role":"Admin","email":"admin@paycore.com",
             "created_at":_now(),"last_login":None,"active":True,
             "profile_pic": None},
            {"user_id":"U002","username":"hr","password_hash":_hash("hr1234"),
             "full_name":"HR Manager","role":"HR","email":"hr@paycore.com",
             "created_at":_now(),"last_login":None,"active":True,
             "profile_pic": None},
        ]
        _write(USERS_FILE, users)
    else:
        # Migrate older records without new fields
        changed = False
        for u in users:
            if "profile_pic" not in u: u["profile_pic"] = None; changed = True
            if "email" not in u: u["email"] = ""; changed = True
        if changed: _write(USERS_FILE, users)
    return users

def authenticate(username, password):
    users = _read(USERS_FILE)
    ph = _hash(password)
    for u in users:
        if u["username"] == username and u["password_hash"] == ph and u["active"]:
            u["last_login"] = _now()
            _write(USERS_FILE, users)
            return u
    return None

def get_users(): return _read(USERS_FILE)

def update_profile(username: str, full_name: str, email: str, profile_pic: str | None):
    users = _read(USERS_FILE)
    for u in users:
        if u["username"] == username:
            u["full_name"]   = full_name.strip() or u["full_name"]
            u["email"]       = email.strip()
            if profile_pic is not None:
                u["profile_pic"] = profile_pic   # base64 string
            _write(USERS_FILE, users)
            return u
    raise ValueError("User not found")

def get_user(username: str):
    for u in _read(USERS_FILE):
        if u["username"] == username: return u
    return None

def change_password(username, old_pw, new_pw):
    users = _read(USERS_FILE)
    for u in users:
        if u["username"] == username and u["password_hash"] == _hash(old_pw):
            u["password_hash"] = _hash(new_pw)
            _write(USERS_FILE, users)
            return True
    return False

def reset_password_by_email(email: str, new_pw: str) -> bool:
    """Reset password if email matches a registered user."""
    users = _read(USERS_FILE)
    for u in users:
        if u.get("email","").lower() == email.lower():
            u["password_hash"] = _hash(new_pw)
            _write(USERS_FILE, users)
            audit_log("RESET_PASSWORD", f"Password reset for {u['username']} via email")
            return True
    return False

def add_user(username, password, full_name, role, email):
    users = _read(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError(f"Username '{username}' already exists.")
    new = {"user_id":f"U{len(users)+1:03d}","username":username,
           "password_hash":_hash(password),"full_name":full_name,
           "role":role,"email":email,"created_at":_now(),
           "last_login":None,"active":True,"profile_pic":None}
    users.append(new); _write(USERS_FILE, users)
    return new

# ── Employees ──────────────────────────────────────────────────────────────────
SAMPLE_EMPLOYEES = [
    {"emp_id":"E001","name":"Rahul Kumar Singh","department":"Engineering","designation":"Tech Lead","basic_salary":90000.0,"days_worked":26,"total_days":26,"bonus":7000.0,"join_date":"2021-03-01","employment_type":"Full-time","location":"Mumbai","bank_account":"HDFC****1234"},
    {"emp_id":"E002","name":"Priya Sharma","department":"HR","designation":"HR Manager","basic_salary":65000.0,"days_worked":25,"total_days":26,"bonus":3000.0,"join_date":"2020-07-15","employment_type":"Full-time","location":"Delhi","bank_account":"ICIC****5678"},
    {"emp_id":"E003","name":"Amit Verma","department":"Finance","designation":"Senior Accountant","basic_salary":55000.0,"days_worked":22,"total_days":26,"bonus":2000.0,"join_date":"2022-01-10","employment_type":"Full-time","location":"Pune","bank_account":"SBI*****9012"},
    {"emp_id":"E004","name":"Sneha Patel","department":"Marketing","designation":"Marketing Lead","basic_salary":60000.0,"days_worked":26,"total_days":26,"bonus":4000.0,"join_date":"2019-11-20","employment_type":"Full-time","location":"Mumbai","bank_account":"AXIS****3456"},
    {"emp_id":"E005","name":"Vikram Singh","department":"Engineering","designation":"Software Engineer","basic_salary":70000.0,"days_worked":24,"total_days":26,"bonus":3500.0,"join_date":"2023-06-01","employment_type":"Full-time","location":"Bangalore","bank_account":"HDFC****7890"},
    {"emp_id":"E006","name":"Anjali Mishra","department":"Operations","designation":"Operations Head","basic_salary":80000.0,"days_worked":26,"total_days":26,"bonus":6000.0,"join_date":"2018-04-12","employment_type":"Full-time","location":"Hyderabad","bank_account":"ICIC****2345"},
    {"emp_id":"E007","name":"Rohit Joshi","department":"Finance","designation":"Finance Analyst","basic_salary":52000.0,"days_worked":20,"total_days":26,"bonus":1500.0,"join_date":"2022-09-05","employment_type":"Full-time","location":"Delhi","bank_account":"SBI*****6789"},
    {"emp_id":"E008","name":"Kavya Reddy","department":"IT","designation":"System Admin","basic_salary":58000.0,"days_worked":26,"total_days":26,"bonus":2500.0,"join_date":"2021-12-01","employment_type":"Full-time","location":"Bangalore","bank_account":"AXIS****0123"},
    {"emp_id":"E009","name":"Suresh Kumar","department":"Engineering","designation":"Principal Engineer","basic_salary":95000.0,"days_worked":25,"total_days":26,"bonus":8000.0,"join_date":"2017-08-22","employment_type":"Full-time","location":"Mumbai","bank_account":"HDFC****4567"},
    {"emp_id":"E010","name":"Meena Iyer","department":"HR","designation":"HR Executive","basic_salary":48000.0,"days_worked":23,"total_days":26,"bonus":1000.0,"join_date":"2023-02-14","employment_type":"Full-time","location":"Chennai","bank_account":"ICIC****8901"},
    {"emp_id":"E011","name":"Karan Malhotra","department":"Sales","designation":"Sales Manager","basic_salary":72000.0,"days_worked":26,"total_days":26,"bonus":5500.0,"join_date":"2020-03-10","employment_type":"Full-time","location":"Delhi","bank_account":"SBI*****2345"},
    {"emp_id":"E012","name":"Divya Nair","department":"Engineering","designation":"QA Engineer","basic_salary":55000.0,"days_worked":24,"total_days":26,"bonus":2000.0,"join_date":"2022-07-18","employment_type":"Full-time","location":"Kochi","bank_account":"AXIS****6789"},
    {"emp_id":"E013","name":"Arun Gupta","department":"Legal","designation":"Legal Counsel","basic_salary":88000.0,"days_worked":26,"total_days":26,"bonus":4000.0,"join_date":"2019-05-30","employment_type":"Full-time","location":"Mumbai","bank_account":"HDFC****0123"},
    {"emp_id":"E014","name":"Swathi Krishnan","department":"IT","designation":"DevOps Engineer","basic_salary":75000.0,"days_worked":26,"total_days":26,"bonus":3500.0,"join_date":"2021-09-14","employment_type":"Full-time","location":"Bangalore","bank_account":"ICIC****4567"},
    {"emp_id":"E015","name":"Manish Tiwari","department":"Operations","designation":"Supply Chain Lead","basic_salary":68000.0,"days_worked":21,"total_days":26,"bonus":2500.0,"join_date":"2020-11-25","employment_type":"Full-time","location":"Pune","bank_account":"SBI*****8901"},
    {"emp_id":"E016","name":"Pooja Sharma","department":"Marketing","designation":"Brand Executive","basic_salary":50000.0,"days_worked":26,"total_days":26,"bonus":2000.0,"join_date":"2023-01-09","employment_type":"Full-time","location":"Mumbai","bank_account":"AXIS****2345"},
    {"emp_id":"E017","name":"Nikhil Das","department":"Sales","designation":"Business Dev Exec","basic_salary":60000.0,"days_worked":25,"total_days":26,"bonus":4000.0,"join_date":"2021-04-20","employment_type":"Full-time","location":"Kolkata","bank_account":"HDFC****6789"},
    {"emp_id":"E018","name":"Lakshmi Rao","department":"Finance","designation":"CFO Assistant","basic_salary":82000.0,"days_worked":26,"total_days":26,"bonus":5000.0,"join_date":"2018-12-01","employment_type":"Full-time","location":"Hyderabad","bank_account":"ICIC****0123"},
    {"emp_id":"E019","name":"Tarun Bajaj","department":"Engineering","designation":"Data Engineer","basic_salary":78000.0,"days_worked":23,"total_days":26,"bonus":3000.0,"join_date":"2022-03-15","employment_type":"Full-time","location":"Bangalore","bank_account":"SBI*****4567"},
    {"emp_id":"E020","name":"Geeta Pillai","department":"HR","designation":"Talent Acquisition","basic_salary":54000.0,"days_worked":26,"total_days":26,"bonus":1500.0,"join_date":"2023-06-30","employment_type":"Full-time","location":"Chennai","bank_account":"AXIS****8901"},
]

RAW_KEYS = ["emp_id","name","department","designation","basic_salary",
            "days_worked","total_days","bonus","join_date",
            "employment_type","location","bank_account"]

def _compute(emp):
    basic = float(emp["basic_salary"])
    dw    = int(emp["days_worked"])
    dt    = int(emp["total_days"])
    bonus = float(emp.get("bonus", 0))
    hra   = round(basic * 0.20, 2)
    da    = round(basic * 0.15, 2)
    ta    = 1500.0
    gross = round(basic + hra + da + ta + bonus, 2)
    pf    = round(basic * 0.12, 2)
    esi   = round(basic * 0.0175, 2)
    pt    = 200.0
    tds   = round(gross * 0.10, 2) if gross > 50000 else (round(gross * 0.05, 2) if gross > 30000 else 0.0)
    deduct= round(pf + esi + pt + tds, 2)
    att   = round(dw / dt, 4) if dt > 0 else 0.0
    net   = round((gross - deduct) * att, 2)
    status= "Paid" if att >= 0.90 else ("Review" if att >= 0.75 else "Hold")
    return {**emp, "hra":hra,"da":da,"ta":ta,"gross":gross,
            "pf":pf,"esi":esi,"pt":pt,"tds":tds,
            "total_deductions":deduct,"attendance":att,
            "net_salary":net,"pay_status":status}

def load_employees():
    raw = _read(EMPLOYEES_FILE)
    if not raw:
        raw = SAMPLE_EMPLOYEES
        _write(EMPLOYEES_FILE, raw)
    return [_compute(e) for e in raw]

def add_employee(data):
    employees = _read(EMPLOYEES_FILE)
    if any(e["emp_id"] == data["emp_id"] for e in employees):
        raise ValueError(f"Employee ID '{data['emp_id']}' already exists.")
    raw = {k: data[k] for k in RAW_KEYS if k in data}
    employees.append(raw); _write(EMPLOYEES_FILE, employees)
    audit_log("ADD_EMPLOYEE", f"Added {data['emp_id']} - {data['name']}")
    return _compute(raw)

def update_employee(emp_id, data):
    employees = _read(EMPLOYEES_FILE)
    for i, e in enumerate(employees):
        if e["emp_id"] == emp_id:
            employees[i] = {k: data[k] for k in RAW_KEYS if k in data}
            _write(EMPLOYEES_FILE, employees)
            audit_log("EDIT_EMPLOYEE", f"Updated {emp_id}")
            return _compute(employees[i])
    raise ValueError(f"Employee '{emp_id}' not found.")

def delete_employee(emp_id):
    employees = _read(EMPLOYEES_FILE)
    new = [e for e in employees if e["emp_id"] != emp_id]
    if len(new) == len(employees): raise ValueError(f"Not found: {emp_id}")
    _write(EMPLOYEES_FILE, new)
    audit_log("DELETE_EMPLOYEE", f"Deleted {emp_id}")

def bulk_bonus(amount: float, dept_filter: str = "All"):
    """Add fixed bonus to all (or dept) employees."""
    employees = _read(EMPLOYEES_FILE)
    count = 0
    for e in employees:
        if dept_filter == "All" or e["department"] == dept_filter:
            e["bonus"] = round(float(e.get("bonus", 0)) + amount, 2)
            count += 1
    _write(EMPLOYEES_FILE, employees)
    scope = dept_filter if dept_filter != "All" else "all departments"
    audit_log("BULK_BONUS", f"Added ₹{amount:,.0f} bonus to {count} employees ({scope})")
    return count

# ── Payments ───────────────────────────────────────────────────────────────────
def get_payments(): return _read(PAYMENTS_FILE)

def record_payment(emp_id, emp_name, amount, month, method, processed_by):
    payments = _read(PAYMENTS_FILE)
    p = {"payment_id": f"PAY{len(payments)+1:05d}", "emp_id": emp_id,
         "emp_name": emp_name, "amount": amount, "month": month,
         "payment_method": method, "payment_date": _now(),
         "status": "Completed", "processed_by": processed_by}
    payments.append(p); _write(PAYMENTS_FILE, payments)
    audit_log("PAYMENT", f"{emp_id} ₹{amount:,.0f} via {method}")
    return p

def bulk_pay(employees: list, month: str, method: str, processed_by: str) -> int:
    """Pay all given employees in one shot."""
    count = 0
    for e in employees:
        record_payment(e["emp_id"], e["name"], float(e["net_salary"]),
                       month, method, processed_by)
        count += 1
    audit_log("BULK_PAY", f"Bulk paid {count} employees for {month} via {method}")
    return count

def get_pending_payments(employees, month):
    payments = _read(PAYMENTS_FILE)
    paid_ids = {p["emp_id"] for p in payments if p["month"] == month}
    return [e for e in employees if e["emp_id"] not in paid_ids]

# ── Payroll runs ───────────────────────────────────────────────────────────────
def get_payroll_runs(): return _read(PAYROLL_RUNS_FILE)

def create_payroll_run(month, total_employees, total_amount, run_by):
    runs = _read(PAYROLL_RUNS_FILE)
    run = {"run_id": f"RUN{len(runs)+1:04d}", "month": month,
           "run_date": _now(), "total_employees": total_employees,
           "total_amount": total_amount, "status": "Completed", "run_by": run_by}
    runs.append(run); _write(PAYROLL_RUNS_FILE, runs)
    audit_log("PAYROLL_RUN", f"Month={month} Total=₹{total_amount:,.0f}")
    return run

# ── Audit ──────────────────────────────────────────────────────────────────────
def audit_log(action, detail):
    log = _read(AUDIT_FILE)
    log.append({"ts": _now(), "action": action, "detail": detail})
    _write(AUDIT_FILE, log)

def get_audit_log(): return list(reversed(_read(AUDIT_FILE)))

# ── Init ───────────────────────────────────────────────────────────────────────
_seed_users()
