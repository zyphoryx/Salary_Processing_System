"""
PayCore — Streamlit Web UI
Salary Processing System
"""

import streamlit as st
import pandas as pd
import json
import os
import hashlib
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PayCore — Salary Processing System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

EMPLOYEES_FILE    = os.path.join(DATA_DIR, "employees.json")
USERS_FILE        = os.path.join(DATA_DIR, "users.json")
PAYMENTS_FILE     = os.path.join(DATA_DIR, "payments.json")
PAYROLL_RUNS_FILE = os.path.join(DATA_DIR, "payroll_runs.json")
AUDIT_FILE        = os.path.join(DATA_DIR, "audit_log.json")

# ── Helpers ────────────────────────────────────────────────────────────────────
def _read(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

def _write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def _now():
    return datetime.now().isoformat(timespec="seconds")

def _fmt_inr(v):
    try:
        return f"₹{float(v):,.0f}"
    except:
        return str(v)

# ── Seed Users ─────────────────────────────────────────────────────────────────
def seed_users():
    users = _read(USERS_FILE)
    if not users:
        users = [
            {"username": "admin", "password_hash": _hash("admin123"),
             "full_name": "System Administrator", "role": "Admin"},
            {"username": "hr", "password_hash": _hash("hr1234"),
             "full_name": "HR Manager", "role": "HR"},
        ]
        _write(USERS_FILE, users)
    return users

# ── Seed Employees ─────────────────────────────────────────────────────────────
def seed_employees():
    employees = _read(EMPLOYEES_FILE)
    if not employees:
        employees = [
            {"emp_id": "E001", "name": "Rahul Kumar Singh", "department": "Engineering",
             "designation": "Tech Lead", "basic_salary": 90000, "days_worked": 26,
             "total_days": 26, "bonus": 8000, "location": "Mumbai"},
            {"emp_id": "E002", "name": "Priya Sharma", "department": "HR",
             "designation": "HR Manager", "basic_salary": 65000, "days_worked": 25,
             "total_days": 26, "bonus": 4000, "location": "Delhi"},
            {"emp_id": "E003", "name": "Amit Verma", "department": "Finance",
             "designation": "Senior Accountant", "basic_salary": 55000, "days_worked": 22,
             "total_days": 26, "bonus": 3000, "location": "Pune"},
        ]
        _write(EMPLOYEES_FILE, employees)
    return employees

# ── Payroll Compute ────────────────────────────────────────────────────────────
def compute_salary(emp):
    basic  = float(emp.get("basic_salary", 0))
    bonus  = float(emp.get("bonus", 0))
    worked = float(emp.get("days_worked", 26))
    total  = float(emp.get("total_days", 26))

    hra   = basic * 0.20
    da    = basic * 0.15
    ta    = 1500
    gross = basic + hra + da + ta + bonus

    pf   = basic * 0.12
    esi  = basic * 0.0175
    pt   = 200
    tds  = gross * 0.10 if gross > 50000 else (gross * 0.05 if gross > 30000 else 0)
    ded  = pf + esi + pt + tds

    att  = min(worked / total, 1.0) if total > 0 else 1.0
    net  = (gross - ded) * att

    status = "Paid" if att >= 0.90 else ("Review" if att >= 0.75 else "Hold")

    return {**emp,
            "hra": round(hra), "da": round(da), "ta": ta,
            "gross": round(gross), "pf": round(pf), "esi": round(esi),
            "pt": pt, "tds": round(tds), "total_deductions": round(ded),
            "attendance": round(att * 100, 1), "net_salary": round(net),
            "pay_status": status}

# ── Auth ───────────────────────────────────────────────────────────────────────
def authenticate(username, password):
    users = _read(USERS_FILE)
    for u in users:
        if u["username"] == username and u["password_hash"] == _hash(password):
            return u
    return None

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #fdf4f4; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #c0392b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .metric-label { font-size: 12px; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 28px; font-weight: 700; color: #1a1a2e; margin-top: 4px; }
    .section-title { font-size: 18px; font-weight: 700; color: #1a1a2e; margin: 1rem 0 0.5rem; }
    .badge-paid   { background:#d4edda; color:#155724; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-review { background:#fff3cd; color:#856404; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-hold   { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a0a0a 0%, #2d0f0f 100%); }
    [data-testid="stSidebar"] * { color: #f0f0f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session Init ───────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

seed_users()
seed_employees()

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:2rem;'>
            <h1 style='font-size:48px; font-weight:900; color:#c0392b; margin:0;'>💼 PayCore</h1>
            <p style='color:#666; font-size:16px; margin-top:4px;'>Salary Processing System</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        st.markdown("""
        <div style='text-align:center; margin-top:1rem; color:#999; font-size:13px;'>
            admin / admin123 &nbsp;·&nbsp; hr / hr1234
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
user = st.session_state.user

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:1rem;'>
        <h2 style='margin:0; font-size:22px; font-weight:800;'>💼 PayCore</h2>
        <p style='margin:2px 0 0; font-size:12px; opacity:0.6;'>Salary Processing System</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "📊 Dashboard",
        "▶ Payroll Runs",
        "💳 Payments",
        "👥 Employees",
        "🧾 Pay Slips",
        "📈 Analytics",
        "📋 Reports",
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='border-top:1px solid rgba(255,255,255,0.1); padding-top:1rem;'>
        <p style='margin:0; font-size:13px; font-weight:600;'>{user['full_name']}</p>
        <p style='margin:2px 0 0; font-size:11px; opacity:0.5;'>{user['role']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ── Load Data ──────────────────────────────────────────────────────────────────
raw_employees = _read(EMPLOYEES_FILE)
employees = [compute_salary(e) for e in raw_employees]
df = pd.DataFrame(employees) if employees else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")

    total_emp  = len(employees)
    total_pay  = sum(e["net_salary"] for e in employees)
    avg_net    = total_pay / total_emp if total_emp else 0
    paid_pct   = (sum(1 for e in employees if e["pay_status"] == "Paid") / total_emp * 100) if total_emp else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in [
        (c1, "TOTAL EMPLOYEES", str(total_emp)),
        (c2, "MONTHLY PAYROLL", f"₹{total_pay/100000:.1f}L"),
        (c3, "AVG NET SALARY", f"₹{avg_net:,.0f}"),
        (c4, "PAYROLL PROCESSED", f"{paid_pct:.0f}%"),
    ]:
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>Payroll by Department</div>", unsafe_allow_html=True)
        if not df.empty:
            dept_data = df.groupby("department")["net_salary"].sum().sort_values()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.barh(dept_data.index, dept_data.values / 100000, color="#c0392b", alpha=0.85)
            ax.set_xlabel("₹ Lakhs")
            ax.set_facecolor("#fdf4f4")
            fig.patch.set_facecolor("#fdf4f4")
            for i, v in enumerate(dept_data.values):
                ax.text(v / 100000 + 0.02, i, f"₹{v/100000:.1f}L", va="center", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col2:
        st.markdown("<div class='section-title'>12-Month Payroll Trend (₹ Lakhs)</div>", unsafe_allow_html=True)
        import random
        random.seed(42)
        months = ["May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr"]
        trend  = [round(total_pay * random.uniform(0.88, 0.97) / 100000, 1) for _ in months[:-1]] + [round(total_pay / 100000, 1)]
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(months, trend, color=["#e8a0a0"] * 11 + ["#c0392b"])
        ax2.set_ylabel("₹ Lakhs")
        ax2.set_facecolor("#fdf4f4")
        fig2.patch.set_facecolor("#fdf4f4")
        plt.xticks(fontsize=8, rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    st.markdown("### Statutory Compliance")
    sc1, sc2, sc3 = st.columns(3)
    sc1.success("✅ PF — Apr 2026 | Due 15 May 2026")
    sc2.success("✅ ESI — Apr 2026 | Due 15 May 2026")
    sc3.error("⚠️ TDS Q4 FY26 | Due 30 Apr 2026 — Overdue")

# ══════════════════════════════════════════════════════════════════════════════
# PAYROLL RUNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "▶ Payroll Runs":
    st.markdown("## ▶ Payroll Runs")
    month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))
    if st.button("🚀 Run Payroll", type="primary"):
        total = sum(e["net_salary"] for e in employees)
        run = {"run_id": f"RUN{len(_read(PAYROLL_RUNS_FILE))+1:04d}",
               "month": month, "date": _now(),
               "employees": len(employees), "total_amount": total,
               "status": "Complete", "run_by": user["username"]}
        runs = _read(PAYROLL_RUNS_FILE)
        runs.append(run)
        _write(PAYROLL_RUNS_FILE, runs)
        st.success(f"✅ Payroll run complete for {month} — {len(employees)} employees, Total: ₹{total:,.0f}")

    runs = _read(PAYROLL_RUNS_FILE)
    if runs:
        st.markdown("### Payroll Run History")
        rdf = pd.DataFrame(runs)
        rdf["total_amount"] = rdf["total_amount"].apply(_fmt_inr)
        st.dataframe(rdf, use_container_width=True, hide_index=True)
    else:
        st.info("No payroll runs yet. Click 'Run Payroll' to start.")

# ══════════════════════════════════════════════════════════════════════════════
# PAYMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💳 Payments":
    st.markdown("## 💳 Payments")
    if employees:
        emp_names = {e["emp_id"]: f"{e['emp_id']} — {e['name']}" for e in employees}
        sel = st.selectbox("Select Employee", list(emp_names.values()))
        emp_id = sel.split(" — ")[0]
        method = st.selectbox("Payment Method", ["Bank Transfer", "UPI", "Cheque", "Cash"])
        month  = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

        if st.button("💳 Process Payment", type="primary"):
            emp = next(e for e in employees if e["emp_id"] == emp_id)
            payment = {"payment_id": f"PAY-{datetime.now().strftime('%Y%m%d')}-{emp_id}",
                       "emp_id": emp_id, "employee_name": emp["name"],
                       "month": month, "amount": emp["net_salary"],
                       "method": method, "status": "Completed",
                       "processed_by": user["username"], "timestamp": _now()}
            payments = _read(PAYMENTS_FILE)
            payments.append(payment)
            _write(PAYMENTS_FILE, payments)
            st.success(f"✅ Payment of ₹{emp['net_salary']:,.0f} processed for {emp['name']} via {method}")

    payments = _read(PAYMENTS_FILE)
    if payments:
        st.markdown("### Payment History")
        pdf = pd.DataFrame(payments)
        pdf["amount"] = pdf["amount"].apply(_fmt_inr)
        st.dataframe(pdf, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# EMPLOYEES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Employees":
    st.markdown("## 👥 Employees")

    search = st.text_input("🔍 Search by name, ID, department...")
    filtered = employees
    if search:
        s = search.lower()
        filtered = [e for e in employees if s in e["name"].lower()
                    or s in e["emp_id"].lower()
                    or s in e["department"].lower()]

    if filtered:
        display_cols = ["emp_id","name","department","designation","location",
                        "basic_salary","gross","net_salary","pay_status"]
        edf = pd.DataFrame(filtered)[display_cols]
        edf.columns = ["ID","Name","Dept","Designation","Location","Basic","Gross","Net Salary","Status"]
        for col in ["Basic","Gross","Net Salary"]:
            edf[col] = edf[col].apply(_fmt_inr)
        st.dataframe(edf, use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} employees shown")
    else:
        st.info("No employees found.")

    with st.expander("➕ Add New Employee"):
        with st.form("add_emp"):
            c1, c2 = st.columns(2)
            name   = c1.text_input("Full Name")
            dept   = c2.selectbox("Department", ["Engineering","Finance","HR","IT","Marketing","Operations","Sales","Legal"])
            desig  = c1.text_input("Designation")
            loc    = c2.text_input("Location")
            basic  = c1.number_input("Basic Salary (₹)", min_value=0, value=50000)
            bonus  = c2.number_input("Bonus (₹)", min_value=0, value=0)
            worked = c1.number_input("Days Worked", min_value=0, max_value=31, value=26)
            total  = c2.number_input("Total Days", min_value=1, max_value=31, value=26)

            if st.form_submit_button("Save Employee"):
                emps = _read(EMPLOYEES_FILE)
                new_id = f"E{len(emps)+1:03d}"
                emps.append({"emp_id": new_id, "name": name, "department": dept,
                              "designation": desig, "location": loc,
                              "basic_salary": basic, "bonus": bonus,
                              "days_worked": worked, "total_days": total})
                _write(EMPLOYEES_FILE, emps)
                st.success(f"✅ Employee {name} added with ID {new_id}")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAY SLIPS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧾 Pay Slips":
    st.markdown("## 🧾 Pay Slips")
    emp_id = st.text_input("Employee ID", placeholder="e.g. E001")

    if st.button("View Slip") and emp_id:
        emp_list = [e for e in employees if e["emp_id"].upper() == emp_id.upper()]
        if emp_list:
            e = emp_list[0]
            st.markdown(f"""
            <div style='background:white; border-radius:12px; padding:2rem; box-shadow:0 2px 12px rgba(0,0,0,0.08);'>
                <div style='text-align:center; border-bottom:2px solid #c0392b; padding-bottom:1rem; margin-bottom:1.5rem;'>
                    <h2 style='color:#c0392b; margin:0;'>💼 PayCore</h2>
                    <p style='color:#666; margin:4px 0 0;'>Payroll Department · Salary Slip</p>
                </div>
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem;'>
                    <div><b>Employee ID:</b> {e['emp_id']}</div>
                    <div><b>Name:</b> {e['name']}</div>
                    <div><b>Department:</b> {e['department']}</div>
                    <div><b>Designation:</b> {e['designation']}</div>
                    <div><b>Location:</b> {e.get('location','—')}</div>
                    <div><b>Attendance:</b> {e['attendance']}%</div>
                </div>
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem;'>
                    <div style='background:#f8f9fa; border-radius:8px; padding:1rem;'>
                        <b style='font-size:15px;'>Earnings</b><hr/>
                        <div style='display:flex;justify-content:space-between;'><span>Basic Salary</span><span>{_fmt_inr(e['basic_salary'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>HRA (20%)</span><span>{_fmt_inr(e['hra'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>DA (15%)</span><span>{_fmt_inr(e['da'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>Travel Allowance</span><span>{_fmt_inr(e['ta'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>Bonus</span><span>{_fmt_inr(e['bonus'])}</span></div>
                        <hr/><div style='display:flex;justify-content:space-between;font-weight:700;color:#155724;'><span>Total</span><span>{_fmt_inr(e['gross'])}</span></div>
                    </div>
                    <div style='background:#f8f9fa; border-radius:8px; padding:1rem;'>
                        <b style='font-size:15px;'>Deductions</b><hr/>
                        <div style='display:flex;justify-content:space-between;'><span>PF (12%)</span><span>{_fmt_inr(e['pf'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>ESI (1.75%)</span><span>{_fmt_inr(e['esi'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>Prof. Tax</span><span>{_fmt_inr(e['pt'])}</span></div>
                        <div style='display:flex;justify-content:space-between;'><span>TDS</span><span>{_fmt_inr(e['tds'])}</span></div>
                        <hr/><div style='display:flex;justify-content:space-between;font-weight:700;color:#721c24;'><span>Total Deductions</span><span>{_fmt_inr(e['total_deductions'])}</span></div>
                    </div>
                </div>
                <div style='background:#c0392b; color:white; border-radius:8px; padding:1rem 1.5rem; margin-top:1rem; display:flex; justify-content:space-between; align-items:center;'>
                    <b style='font-size:16px;'>NET SALARY</b>
                    <b style='font-size:20px;'>{_fmt_inr(e['net_salary'])}</b>
                </div>
                <div style='text-align:center; margin-top:1rem; color:#666; font-size:12px;'>
                    Status: <span style='background:#d4edda;color:#155724;padding:3px 12px;border-radius:20px;font-weight:600;'>{e['pay_status']}</span>
                    &nbsp;&nbsp; System generated · No signature required
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Employee {emp_id} not found.")

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.markdown("## 📈 Department Analytics")
    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Headcount by Department**")
            hc = df.groupby("department").size()
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(hc.values, labels=hc.index, autopct="%1.0f%%", startangle=90,
                   colors=plt.cm.Set3.colors)
            fig.patch.set_facecolor("#fdf4f4")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            st.markdown("**Avg Net Salary by Department**")
            avg = df.groupby("department")["net_salary"].mean().sort_values()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.barh(avg.index, avg.values, color="#c0392b", alpha=0.85)
            ax2.set_xlabel("₹")
            ax2.set_facecolor("#fdf4f4")
            fig2.patch.set_facecolor("#fdf4f4")
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()

        st.markdown("### Department Summary")
        summary = df.groupby("department").agg(
            Headcount=("emp_id","count"),
            Total_Payroll=("net_salary","sum"),
            Avg_Net=("net_salary","mean"),
            Avg_Basic=("basic_salary","mean"),
            Avg_Attendance=("attendance","mean")
        ).reset_index()
        for col in ["Total_Payroll","Avg_Net","Avg_Basic"]:
            summary[col] = summary[col].apply(_fmt_inr)
        summary["Avg_Attendance"] = summary["Avg_Attendance"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Reports":
    st.markdown("## 📋 Reports & Audit")

    tab1, tab2 = st.tabs(["Audit Log", "Salary Summary"])

    with tab1:
        audit = _read(AUDIT_FILE)
        if audit:
            st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)
        else:
            st.info("No audit records yet.")

    with tab2:
        if not df.empty:
            summary = df.groupby("department").agg(
                Headcount=("emp_id","count"),
                Gross=("gross","sum"),
                Deductions=("total_deductions","sum"),
                Net=("net_salary","sum")
            ).reset_index()
            for col in ["Gross","Deductions","Net"]:
                summary[col] = summary[col].apply(_fmt_inr)
            st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#aaa; font-size:12px; margin-top:3rem; padding-top:1rem; border-top:1px solid #eee;'>
    © 2026 PayCore · Salary Processing System
</div>
""", unsafe_allow_html=True)
