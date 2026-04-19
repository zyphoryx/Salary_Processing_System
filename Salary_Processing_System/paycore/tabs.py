"""PayCore — All tab panels"""
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QFrame, QScrollArea, QGridLayout,
    QAbstractItemView, QMessageBox, QDialog, QDialogButtonBox,
    QCheckBox, QButtonGroup, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib; matplotlib.use("Qt5Agg")
import base64, styles as S
from widgets import KPICard, StatusBadge, CardFrame, Divider

DEPARTMENTS = ["Engineering","Finance","HR","IT","Marketing","Operations","Sales","Legal"]
MONTHS_LBL  = ["May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr"]

EMP_COLS = ["emp_id","name","department","designation","location",
            "basic_salary","hra","da","bonus","gross","pf","esi","tds",
            "total_deductions","net_salary","days_worked","total_days","attendance","pay_status"]
EMP_HDRS = ["ID","Name","Dept","Designation","Location",
            "Basic","HRA","DA","Bonus","Gross","PF","ESI","TDS",
            "Deductions","Net Salary","Worked","Total","Attend.","Status"]

CHART_COLORS = ["#2563EB","#16A34A","#D97706","#DC2626","#7C3AED","#0891B2","#DB2777","#65A30D"]


def _fmt(v, money=False):
    try:
        f = float(v)
        return f"₹{f:,.0f}" if money else (f"{f:.1%}" if f <= 1 else str(round(f,2)))
    except: return str(v)


def _make_table(ncols, hdrs, height=None, multi_select=False):
    t = QTableWidget()
    t.setColumnCount(ncols)
    if hdrs: t.setHorizontalHeaderLabels(hdrs)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    if multi_select:
        t.setSelectionMode(QAbstractItemView.MultiSelection)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.setShowGrid(False)
    t.setStyleSheet(f"""
        QTableWidget {{
            background:{S._t("CARD")}; border:1px solid {S._t("BORDER")};
            border-radius:10px; alternate-background-color:{S._t("ALT_ROW")};
            outline:none; color:{S._t("TEXT")};
        }}
        QTableWidget::item {{ padding:7px 8px; border-bottom:1px solid {S._t("BORDER")}; }}
        QTableWidget::item:selected {{ background:{S._t("BLUE_L")}; color:{S._t("TEXT")}; }}
    """)
    # Use ResizeToContents so numbers show fully, then stretch last column
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    t.horizontalHeader().setStretchLastSection(True)
    if height: t.setFixedHeight(height)
    return t


def _btn(label, color=None, height=34, width=None):
    if color is None: color = S._t("BLUE")
    b = QPushButton(label); b.setFixedHeight(height)
    if width: b.setFixedWidth(width)
    dark = S._darken(color)
    b.setStyleSheet(f"""
        QPushButton {{ background:{color}; color:white; border:none; border-radius:7px;
                       padding:0 14px; font-size:12px; font-weight:600; }}
        QPushButton:hover   {{ background:{dark}; }}
        QPushButton:pressed {{ opacity:0.8; }}
    """)
    return b


def _inp(ph="", w=None, h=34):
    e = QLineEdit(); e.setPlaceholderText(ph); e.setFixedHeight(h)
    if w: e.setFixedWidth(w)
    return e


def _combo(items, w=None, h=34):
    c = QComboBox(); c.addItems(items); c.setFixedHeight(h)
    if w: c.setFixedWidth(w)
    return c


def _lbl(text, sz=12, bold=False, color=None, align=Qt.AlignLeft):
    l = QLabel(text); f = QFont("Segoe UI", sz); f.setBold(bold); l.setFont(f)
    col = color or S._t("TEXT")
    l.setStyleSheet(f"color:{col};background:transparent;border:none;"); l.setAlignment(align)
    return l


def _chart_setup(fig_w, fig_h):
    fig = Figure(figsize=(fig_w, fig_h), dpi=90)
    fig.patch.set_facecolor(S._t("CARD"))
    ax = fig.add_subplot(111); ax.set_facecolor(S._t("CARD"))
    canvas = FigureCanvas(fig); canvas.setStyleSheet("background:transparent;")
    return fig, ax, canvas


# ── Dashboard ──────────────────────────────────────────────────────────────────
class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{S._t('BG')};")
        inner = QWidget(); inner.setStyleSheet(f"background:{S._t('BG')};")
        lay = QVBoxLayout(inner); lay.setContentsMargins(24,20,24,24); lay.setSpacing(16)

        # KPI row — clickable
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        self.kpi_emp  = KPICard("Total Employees",  "—", accent=S._t("BLUE"))
        self.kpi_pay  = KPICard("Monthly Payroll",  "—", accent=S._t("GREEN"))
        self.kpi_avg  = KPICard("Avg Net Salary",   "—", accent=S._t("PURPLE"))
        self.kpi_comp = KPICard("Payroll Processed","—", accent=S._t("AMBER"))
        for k in (self.kpi_emp, self.kpi_pay, self.kpi_avg, self.kpi_comp):
            k.setCursor(Qt.PointingHandCursor)
            kpi_row.addWidget(k)
        # KPI click tooltips
        self.kpi_emp.setToolTip("Total headcount across all departments")
        self.kpi_pay.setToolTip("Total net salary disbursement this month")
        self.kpi_avg.setToolTip("Average net take-home across all employees")
        self.kpi_comp.setToolTip("Percentage of employees with Paid status")
        lay.addLayout(kpi_row)

        # Charts
        charts = QHBoxLayout(); charts.setSpacing(12)
        dept_frame = CardFrame("Payroll by Department")
        self._dept_fig, self._dept_ax, self._dept_canvas = _chart_setup(5, 2.8)
        dept_frame.add(self._dept_canvas)
        trend_frame = CardFrame("12-Month Trend  (₹ Lakhs)")
        self._trend_fig, self._trend_ax, self._trend_canvas = _chart_setup(4, 2.8)
        trend_frame.add(self._trend_canvas)
        charts.addWidget(dept_frame, 55); charts.addWidget(trend_frame, 45)
        lay.addLayout(charts)
        lay.addWidget(self._compliance_card())

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;")
        scroll.setWidget(inner)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _compliance_card(self):
        frame = CardFrame("Statutory Compliance")
        grid = QGridLayout(); grid.setSpacing(10)
        self._compliance_items = [
            ("PF — Apr 2026",       "Due 15 May 2026", "Ready"),
            ("ESI — Apr 2026",      "Due 15 May 2026", "Ready"),
            ("TDS Q4 FY26",         "Due 30 Apr 2026", "Overdue"),
            ("PT — Maharashtra",    "Due 30 Apr 2026", "Pending"),
            ("Gratuity Fund",       "Due 1 May 2026",  "Filed"),
            ("Labour Welfare Fund", "Due 30 Apr 2026", "Ready"),
        ]
        for i, (name, due, status) in enumerate(self._compliance_items):
            r, c = divmod(i, 3)
            cell = QFrame()
            cell.setStyleSheet(f"QFrame{{background:{S._t('BG')};border:1px solid {S._t('BORDER')};border-radius:8px;}}QLabel{{background:transparent;border:none;}}")
            cell.setCursor(Qt.PointingHandCursor)
            cell.setToolTip(f"{name}  |  {due}  |  Status: {status}")
            cl = QVBoxLayout(cell); cl.setContentsMargins(14,12,14,12); cl.setSpacing(4)
            n = _lbl(name, 12, True); d = _lbl(due, 10, False, S._t("SUBTEXT")); b = StatusBadge(status); b.setFixedWidth(80)
            cl.addWidget(n); cl.addWidget(d); cl.addWidget(b, 0, Qt.AlignLeft)
            grid.addWidget(cell, r, c)
        frame.body.addLayout(grid)
        return frame

    def refresh(self, employees):
        if not employees: return
        df = pd.DataFrame(employees)
        n = len(df); total = df["net_salary"].sum(); avg = df["net_salary"].mean()
        paid = (df["pay_status"] == "Paid").sum(); pct = int(paid/n*100)
        self.kpi_emp.update(f"{n:,}")
        self.kpi_pay.update(f"₹{total/100000:.1f}L", f"Total: ₹{total:,.0f}")
        self.kpi_avg.update(f"₹{avg:,.0f}")
        self.kpi_comp.update(f"{pct}%", f"{paid}/{n} processed", delta_up=(pct>=80))
        self._draw_dept(df); self._draw_trend()

    def _draw_dept(self, df):
        ax = self._dept_ax; ax.clear(); ax.set_facecolor(S._t("CARD"))
        s = df.groupby("department")["net_salary"].sum().sort_values(ascending=True)
        colors = [S._t("BLUE") if i==len(s)-1 else S._t("BLUE_T") for i in range(len(s))]
        bars = ax.barh(s.index, s.values/100000, color=colors, height=0.5)
        ax.set_xlabel("₹ Lakhs", fontsize=8, color=S._t("SUBTEXT"))
        ax.tick_params(labelsize=8, colors=S._t("SUBTEXT"))
        for sp in ["top","right","bottom"]: ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color(S._t("BORDER"))
        for bar in bars:
            ax.text(bar.get_width()+0.02, bar.get_y()+bar.get_height()/2,
                    f"₹{bar.get_width():.1f}L", va="center", fontsize=7.5, color=S._t("TEXT"))
        self._dept_fig.patch.set_facecolor(S._t("CARD"))
        self._dept_fig.tight_layout(); self._dept_canvas.draw()

    def _draw_trend(self):
        ax = self._trend_ax; ax.clear(); ax.set_facecolor(S._t("CARD"))
        import math, random; random.seed(42)
        data = [round(47+2*math.sin(i/2)+random.uniform(-1,1),1) for i in range(12)]
        colors = [S._t("BLUE") if i==11 else S._t("BLUE_T") for i in range(12)]
        ax.bar(MONTHS_LBL, data, color=colors, width=0.55)
        ax.set_ylabel("₹ Lakhs", fontsize=8, color=S._t("SUBTEXT"))
        ax.tick_params(labelsize=7.5, colors=S._t("SUBTEXT"))
        for sp in ["top","right"]: ax.spines[sp].set_visible(False)
        for sp in ["left","bottom"]: ax.spines[sp].set_color(S._t("BORDER"))
        self._trend_fig.patch.set_facecolor(S._t("CARD"))
        self._trend_fig.tight_layout(); self._trend_canvas.draw()


# ── Employee Register ──────────────────────────────────────────────────────────
class EmployeeTab(QWidget):
    request_add    = pyqtSignal()
    request_edit   = pyqtSignal(str)
    request_delete = pyqtSignal(str)
    request_pay_selected = pyqtSignal(list)   # list of emp dicts

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{S._t('BG')};")
        lay = QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(10)

        # Toolbar row 1 — search + filter
        row1 = QHBoxLayout(); row1.setSpacing(8)
        self._search = _inp("Search name, ID, department…", h=34); self._search.setMinimumWidth(260)
        self._dept_cb = _combo(["All Departments"]+DEPARTMENTS, w=160)
        self._search.textChanged.connect(self._filter)
        self._dept_cb.currentTextChanged.connect(self._filter)
        row1.addWidget(self._search); row1.addWidget(self._dept_cb); row1.addStretch()
        lay.addLayout(row1)

        # Toolbar row 2 — actions
        row2 = QHBoxLayout(); row2.setSpacing(8)
        btn_add  = _btn("+ Add",        S._t("BLUE"))
        btn_edit = _btn("Edit",          S._t("AMBER"))
        btn_del  = _btn("Delete",        S._t("RED"))
        btn_bonus= _btn("Bulk Bonus",    "#7C3AED")
        btn_pay  = _btn("Pay Selected",  S._t("GREEN"))
        btn_payone=_btn("Pay One",       S._t("GREEN"))
        btn_add.clicked.connect(self.request_add)
        btn_edit.clicked.connect(self._emit_edit)
        btn_del.clicked.connect(self._emit_delete)
        btn_bonus.clicked.connect(self._bulk_bonus)
        btn_pay.clicked.connect(self._pay_selected)
        btn_payone.clicked.connect(self._pay_one)
        for b in (btn_add,btn_edit,btn_del,btn_bonus,btn_pay,btn_payone):
            row2.addWidget(b)
        row2.addStretch()

        sel_all = QPushButton("Select All"); sel_all.setFixedHeight(28)
        sel_all.setStyleSheet(f"QPushButton{{background:transparent;color:{S._t('BLUE')};border:1px solid {S._t('BLUE')};border-radius:5px;padding:0 10px;font-size:11px;}}QPushButton:hover{{background:{S._t('BLUE_L')};}}"); sel_all.clicked.connect(lambda: self._tbl.selectAll())
        clr_sel = QPushButton("Clear"); clr_sel.setFixedHeight(28)
        clr_sel.setStyleSheet(sel_all.styleSheet()); clr_sel.clicked.connect(lambda: self._tbl.clearSelection())
        row2.addWidget(sel_all); row2.addWidget(clr_sel)
        lay.addLayout(row2)

        self._tbl = _make_table(len(EMP_COLS), EMP_HDRS, multi_select=True)
        lay.addWidget(self._tbl)
        self._employees = []

    def load(self, employees):
        self._employees = employees; self._populate(employees)

    def _filter(self):
        q = self._search.text().lower(); dept = self._dept_cb.currentText()
        res = self._employees
        if q: res = [e for e in res if any(q in str(e.get(c,"")).lower() for c in ["emp_id","name","department","designation","location"])]
        if dept != "All Departments": res = [e for e in res if e.get("department")==dept]
        self._populate(res)

    def _populate(self, employees):
        MONEY = {"basic_salary","hra","da","bonus","gross","pf","esi","tds","total_deductions","net_salary"}
        self._tbl.setRowCount(len(employees))
        for r, emp in enumerate(employees):
            for c, col in enumerate(EMP_COLS):
                v = emp.get(col,"")
                if col == "pay_status":
                    self._tbl.setCellWidget(r, c, StatusBadge(str(v)))
                else:
                    text = _fmt(v, col in MONEY) if isinstance(v,(int,float)) else str(v)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    if col == "net_salary":
                        try:
                            fv = float(v)
                            item.setForeground(QColor(S._t("GREEN") if fv>=60000 else S._t("AMBER") if fv>=40000 else S._t("RED")))
                            item.setFont(QFont("Segoe UI",11,QFont.Bold))
                        except: pass
                    self._tbl.setItem(r, c, item)
        # Resize to show full content, then stretch last
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._tbl.horizontalHeader().setStretchLastSection(True)

    def _selected_ids(self):
        rows = set(i.row() for i in self._tbl.selectedIndexes())
        return [self._tbl.item(r,0).text() for r in rows if self._tbl.item(r,0)]

    def _selected_employees(self):
        ids = set(self._selected_ids())
        return [e for e in self._employees if e["emp_id"] in ids]

    def selected_id(self):
        r = self._tbl.currentRow()
        if r < 0: return None
        it = self._tbl.item(r,0); return it.text() if it else None

    def _emit_edit(self):
        eid = self.selected_id()
        if eid: self.request_edit.emit(eid)
        else: QMessageBox.information(self,"Select","Select a row first.")

    def _emit_delete(self):
        eid = self.selected_id()
        if eid: self.request_delete.emit(eid)
        else: QMessageBox.information(self,"Select","Select a row first.")

    def _bulk_bonus(self):
        from dialogs import BulkBonusDialog
        import database as DB
        dlg = BulkBonusDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            count = DB.bulk_bonus(d["amount"], d["dept"])
            QMessageBox.information(self,"Done", f"Added ₹{d['amount']:,.0f} bonus to {count} employees.\nReload to see updated values.")

    def _pay_selected(self):
        emps = self._selected_employees()
        if not emps: QMessageBox.information(self,"Select","Select employees first."); return
        from dialogs import BulkPayDialog
        import database as DB
        total = sum(float(e["net_salary"]) for e in emps)
        dlg = BulkPayDialog(len(emps), total, self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            import __main__
            username = getattr(__main__, "_current_user", {}).get("username","system")
            DB.bulk_pay(emps, d["month"], d["method"], username)
            QMessageBox.information(self,"Done",f"Paid {len(emps)} employees for {d['month']}.")

    def _pay_one(self):
        eid = self.selected_id()
        if not eid: QMessageBox.information(self,"Select","Select a row first."); return
        emp = next((e for e in self._employees if e["emp_id"]==eid), None)
        if not emp: return
        from dialogs import PaymentDialog
        import database as DB, __main__
        month = datetime.now().strftime("%B %Y")
        dlg = PaymentDialog(emp, month, self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            username = getattr(__main__, "_current_user", {}).get("username","system")
            DB.record_payment(emp["emp_id"],emp["name"],d["amount"],d["month"],d["method"],username)
            QMessageBox.information(self,"Done",f"Paid ₹{d['amount']:,.2f} to {emp['name']}.")


# ── Payroll Runs ───────────────────────────────────────────────────────────────
class PayrollRunsTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self._user = user
        self.setStyleSheet(f"background:{S._t('BG')};")
        lay = QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(14)
        row = QHBoxLayout(); row.setSpacing(8)
        lbl = QLabel("Month:"); lbl.setStyleSheet(f"color:{S._t('TEXT')};background:transparent;")
        self._month = _inp(datetime.now().strftime("%B %Y"), w=180)
        btn_run = _btn("Run Payroll", S._t("BLUE"))
        btn_ref = _btn("Refresh",     S._t("NAVY2"))
        btn_run.clicked.connect(self._run); btn_ref.clicked.connect(self._load)
        row.addWidget(lbl); row.addWidget(self._month); row.addWidget(btn_run); row.addWidget(btn_ref); row.addStretch()
        lay.addLayout(row)
        frame = CardFrame("Payroll Run History")
        self._tbl = _make_table(7, ["Run ID","Month","Date","Employees","Total Amount","Status","Run By"])
        frame.add(self._tbl); lay.addWidget(frame)
        self._employees = []; self._load()

    def set_employees(self, e): self._employees = e

    def _load(self):
        import database as DB
        runs = list(reversed(DB.get_payroll_runs()))
        self._tbl.setRowCount(len(runs))
        for r, run in enumerate(runs):
            vals = [run["run_id"],run["month"],run["run_date"][:10],
                    str(run["total_employees"]),f"₹{run['total_amount']:,.0f}",run["status"],run["run_by"]]
            for c, v in enumerate(vals):
                if c == 5: self._tbl.setCellWidget(r,c,StatusBadge(v))
                else:
                    it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._tbl.setItem(r,c,it)

    def _run(self):
        import database as DB
        if not self._employees: QMessageBox.warning(self,"No Data","No employees."); return
        month = self._month.text().strip()
        if not month: QMessageBox.warning(self,"Input","Enter a month."); return
        total = sum(float(e["net_salary"]) for e in self._employees)
        if QMessageBox.question(self,"Confirm",f"Run payroll for {month}?\n{len(self._employees)} employees  ·  ₹{total:,.0f}",
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            DB.create_payroll_run(month,len(self._employees),total,self._user["username"])
            QMessageBox.information(self,"Done",f"Payroll for {month} complete.")
            self._load()


# ── Payments ───────────────────────────────────────────────────────────────────
class PaymentsTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self._user = user
        self.setStyleSheet(f"background:{S._t('BG')};")
        lay = QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(14)
        row = QHBoxLayout(); row.setSpacing(8)
        lbl = QLabel("Filter:"); lbl.setStyleSheet(f"color:{S._t('TEXT')};background:transparent;")
        self._filter = _inp("Month filter…", w=180)
        self._filter.textChanged.connect(self._load)
        btn_pay  = _btn("+ Process Payment", S._t("GREEN"))
        btn_bulk = _btn("Bulk Pay All",      "#7C3AED")
        btn_pend = _btn("View Pending",       S._t("AMBER"))
        btn_pay.clicked.connect(self._process); btn_bulk.clicked.connect(self._bulk)
        btn_pend.clicked.connect(self._pending)
        row.addWidget(lbl); row.addWidget(self._filter)
        row.addWidget(btn_pay); row.addWidget(btn_bulk); row.addWidget(btn_pend); row.addStretch()
        lay.addLayout(row)
        kpi = QHBoxLayout(); kpi.setSpacing(12)
        self.kpi_total = KPICard("Total Payments","0",  accent=S._t("BLUE"))
        self.kpi_amt   = KPICard("Disbursed",     "₹0", accent=S._t("GREEN"))
        self.kpi_pend  = KPICard("Pending",       "0",  accent=S._t("AMBER"))
        for k in (self.kpi_total,self.kpi_amt,self.kpi_pend): kpi.addWidget(k)
        lay.addLayout(kpi)
        frame = CardFrame("Payment History")
        self._tbl = _make_table(7, ["Payment ID","Employee ID","Name","Amount","Month","Method","Date"])
        frame.add(self._tbl); lay.addWidget(frame)
        self._employees = []; self._load()

    def set_employees(self, e): self._employees = e; self._upd_kpi()

    def _load(self):
        import database as DB
        payments = DB.get_payments()
        f = self._filter.text().lower()
        if f: payments = [p for p in payments if f in p.get("month","").lower()]
        self._tbl.setRowCount(len(payments))
        for r, p in enumerate(reversed(payments)):
            vals=[p["payment_id"],p["emp_id"],p["emp_name"],
                  f"₹{p['amount']:,.2f}",p["month"],p["payment_method"],p["payment_date"][:10]]
            for c,v in enumerate(vals):
                it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._tbl.setItem(r,c,it)
        self._upd_kpi()

    def _upd_kpi(self):
        import database as DB
        payments = DB.get_payments()
        self.kpi_total.update(str(len(payments)))
        self.kpi_amt.update(f"₹{sum(p['amount'] for p in payments)/100000:.1f}L")
        month = datetime.now().strftime("%B %Y")
        self.kpi_pend.update(str(len(DB.get_pending_payments(self._employees, month))))

    def _process(self):
        import database as DB
        from dialogs import PaymentDialog
        if not self._employees: QMessageBox.warning(self,"No Data","No employees."); return
        dlg = _PickEmpDlg(self._employees, self)
        if dlg.exec_()!=QDialog.Accepted: return
        emp = dlg.selected_employee()
        if not emp: return
        month = datetime.now().strftime("%B %Y")
        pdlg = PaymentDialog(emp, month, self)
        if pdlg.exec_()==QDialog.Accepted:
            d=pdlg.get_data()
            DB.record_payment(emp["emp_id"],emp["name"],d["amount"],d["month"],d["method"],self._user["username"])
            QMessageBox.information(self,"Done",f"₹{d['amount']:,.2f} paid to {emp['name']}.")
            self._load()

    def _bulk(self):
        import database as DB
        from dialogs import BulkPayDialog
        month = datetime.now().strftime("%B %Y")
        pending = DB.get_pending_payments(self._employees, month)
        if not pending: QMessageBox.information(self,"All Paid","All employees already paid!"); return
        total = sum(float(e["net_salary"]) for e in pending)
        dlg = BulkPayDialog(len(pending), total, self)
        if dlg.exec_()==QDialog.Accepted:
            d=dlg.get_data()
            DB.bulk_pay(pending, d["month"], d["method"], self._user["username"])
            QMessageBox.information(self,"Done",f"Paid {len(pending)} employees for {d['month']}.")
            self._load()

    def _pending(self):
        import database as DB
        month = datetime.now().strftime("%B %Y")
        pending = DB.get_pending_payments(self._employees, month)
        if not pending: QMessageBox.information(self,"Pending",f"All paid for {month}!"); return
        names = "\n".join(f"  {e['emp_id']}  {e['name']}" for e in pending[:25])
        QMessageBox.information(self,f"Pending ({len(pending)}) — {month}",names)


class _PickEmpDlg(QDialog):
    def __init__(self, employees, parent=None):
        super().__init__(parent); self.setWindowTitle("Select Employee"); self.setMinimumSize(460,360)
        self._employees=employees; self._visible=employees
        self.setStyleSheet(f"QDialog{{background:{S._t('BG')};}}QLabel{{background:transparent;border:none;}}")
        lay=QVBoxLayout(self); lay.setContentsMargins(14,14,14,14); lay.setSpacing(8)
        search=_inp("Search…",h=34); search.textChanged.connect(self._flt); lay.addWidget(search)
        self._tbl=_make_table(4,["ID","Name","Dept","Net Salary"]); self._tbl.doubleClicked.connect(self.accept); lay.addWidget(self._tbl)
        btns=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject); lay.addWidget(btns)
        self._populate(employees)

    def _flt(self,q):
        q=q.lower()
        self._visible=[e for e in self._employees if q in e.get("emp_id","").lower() or q in e.get("name","").lower() or q in e.get("department","").lower()] if q else self._employees
        self._populate(self._visible)

    def _populate(self,employees):
        self._tbl.setRowCount(len(employees))
        for r,e in enumerate(employees):
            for c,v in enumerate([e["emp_id"],e["name"],e["department"],f"₹{float(e['net_salary']):,.0f}"]):
                it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._tbl.setItem(r,c,it)

    def selected_employee(self):
        r=self._tbl.currentRow()
        return self._visible[r] if 0<=r<len(self._visible) else None


# ── Dept Analytics ─────────────────────────────────────────────────────────────
class DeptTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{S._t('BG')};")
        lay = QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(14)
        charts = QHBoxLayout(); charts.setSpacing(12)
        pie_f = CardFrame("Headcount by Department")
        self._pie_fig,self._pie_ax,self._pie_canvas = _chart_setup(3.5,3.2); pie_f.add(self._pie_canvas)
        bar_f = CardFrame("Avg Net Salary by Department")
        self._bar_fig,self._bar_ax,self._bar_canvas = _chart_setup(4.5,3.2); bar_f.add(self._bar_canvas)
        charts.addWidget(pie_f); charts.addWidget(bar_f); lay.addLayout(charts)
        frame = CardFrame("Department Summary")
        self._tbl = _make_table(6,["Department","Headcount","Total Payroll","Avg Net","Avg Basic","Avg Attendance"],height=230)
        frame.add(self._tbl); lay.addWidget(frame)

    def refresh(self, employees):
        if not employees: return
        df = pd.DataFrame(employees)
        s = (df.groupby("department").agg(employees=("emp_id","count"),total_payroll=("net_salary","sum"),
             avg_net=("net_salary","mean"),avg_basic=("basic_salary","mean"),avg_attendance=("attendance","mean")).round(2).reset_index())
        self._draw_pie(s); self._draw_bar(s); self._fill_tbl(s)

    def _draw_pie(self, s):
        ax=self._pie_ax; ax.clear(); ax.set_facecolor(S._t("CARD"))
        ax.pie(s["employees"],labels=s["department"],autopct="%1.0f%%",startangle=90,
               colors=CHART_COLORS[:len(s)],textprops={"fontsize":7.5,"color":S._t("TEXT")},pctdistance=0.75)
        self._pie_fig.patch.set_facecolor(S._t("CARD"))
        self._pie_fig.tight_layout(); self._pie_canvas.draw()

    def _draw_bar(self, s):
        ax=self._bar_ax; ax.clear(); ax.set_facecolor(S._t("CARD"))
        s2=s.sort_values("avg_net",ascending=True)
        colors=[S._t("BLUE") if i==len(s2)-1 else S._t("BLUE_T") for i in range(len(s2))]
        ax.barh(s2["department"],s2["avg_net"],color=colors,height=0.5)
        ax.set_xlabel("₹",fontsize=8,color=S._t("SUBTEXT")); ax.tick_params(labelsize=7.5,colors=S._t("SUBTEXT"))
        for sp in ["top","right","bottom"]: ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color(S._t("BORDER"))
        self._bar_fig.patch.set_facecolor(S._t("CARD"))
        self._bar_fig.tight_layout(); self._bar_canvas.draw()

    def _fill_tbl(self, s):
        self._tbl.setRowCount(len(s))
        for r,row in s.iterrows():
            for c,v in enumerate([row["department"],str(int(row["employees"])),f"₹{row['total_payroll']:,.0f}",f"₹{row['avg_net']:,.0f}",f"₹{row['avg_basic']:,.0f}",f"{row['avg_attendance']:.1%}"]):
                it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._tbl.setItem(r,c,it)


# ── Pay Slips ──────────────────────────────────────────────────────────────────
class PayslipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{S._t('BG')};")
        outer = QVBoxLayout(self); outer.setContentsMargins(24,18,24,18); outer.setSpacing(12)
        bar=QHBoxLayout(); bar.setSpacing(8)
        bar.addWidget(_lbl("Employee ID", 12, False, S._t("SUBTEXT")))
        self._inp=_inp("e.g. E001",w=180); btn=_btn("View Slip",S._t("BLUE"))
        btn.clicked.connect(self._view); self._inp.returnPressed.connect(self._view)
        bar.addWidget(self._inp); bar.addWidget(btn); bar.addStretch(); outer.addLayout(bar)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;")
        self._inner=QWidget(); self._inner.setStyleSheet(f"background:{S._t('BG')};")
        self._lay=QVBoxLayout(self._inner); self._lay.setContentsMargins(0,0,0,0)
        hint=QLabel("Enter an Employee ID above to view their pay slip.")
        hint.setStyleSheet(f"color:{S._t('SUBTEXT')};background:transparent;padding:20px;")
        self._lay.addWidget(hint); scroll.setWidget(self._inner); outer.addWidget(scroll)
        self._employees=[]

    def load(self, employees): self._employees=employees

    def _view(self):
        eid=self._inp.text().strip().upper()
        if not eid: QMessageBox.warning(self,"Input","Enter ID."); return
        emp=next((e for e in self._employees if e["emp_id"]==eid),None)
        if not emp: QMessageBox.warning(self,"Not Found",f"No employee: {eid}"); return
        self._render(emp)

    def _render(self, e):
        while self._lay.count():
            it=self._lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        card=QFrame()
        card.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:12px;}}QLabel{{background:transparent;border:none;}}")
        cl=QVBoxLayout(card); cl.setContentsMargins(32,28,32,28); cl.setSpacing(14)
        cl.addWidget(_lbl("PayCore",18,True,S._t("TEXT"),Qt.AlignCenter))
        cl.addWidget(_lbl("Payroll Department  ·  Salary Slip",10,False,S._t("SUBTEXT"),Qt.AlignCenter))
        cl.addWidget(Divider())
        meta=QGridLayout(); meta.setSpacing(8)
        fields=[("Employee ID",str(e["emp_id"])),("Name",str(e["name"])),
                ("Department",str(e["department"])),("Designation",str(e["designation"])),
                ("Location",str(e.get("location","—"))),("Type",str(e.get("employment_type","—"))),
                ("Join Date",str(e.get("join_date","—"))),("Bank",str(e.get("bank_account","****"))),
                ("Days Worked",f"{int(e['days_worked'])} / {int(e['total_days'])}"),
                ("Attendance",f"{float(e['attendance']):.1%}")]
        for i,(k,v) in enumerate(fields):
            r,c=divmod(i,2)
            meta.addWidget(_lbl(k,10,False,S._t("SUBTEXT")),r,c*2)
            meta.addWidget(_lbl(v,11,True,S._t("TEXT")),r,c*2+1)
        cl.addLayout(meta); cl.addWidget(Divider())
        two=QHBoxLayout(); two.setSpacing(14)
        for title, rows, total_key, total_color in [
            ("Earnings",[("Basic Salary","basic_salary"),("HRA (20%)","hra"),("DA (15%)","da"),("Travel Allow.","ta"),("Bonus","bonus")],"gross",S._t("GREEN")),
            ("Deductions",[("PF (12%)","pf"),("ESI (1.75%)","esi"),("Prof. Tax","pt"),("TDS","tds")],"total_deductions",S._t("RED"))
        ]:
            f=QFrame(); f.setStyleSheet(f"QFrame{{background:{S._t('BG')};border:1px solid {S._t('BORDER')};border-radius:8px;}}QLabel{{background:transparent;border:none;}}")
            fl=QVBoxLayout(f); fl.setContentsMargins(16,12,16,12); fl.setSpacing(5)
            fl.addWidget(_lbl(title,11,True)); fl.addWidget(Divider())
            for k,col in rows:
                row_w=QHBoxLayout(); row_w.addWidget(_lbl(k,11,False,S._t("SUBTEXT"))); row_w.addStretch()
                row_w.addWidget(_lbl(f"₹{float(e.get(col,0)):,.0f}",11,False,S._t("TEXT"))); fl.addLayout(row_w)
            fl.addWidget(Divider())
            tot_row=QHBoxLayout(); tot_row.addWidget(_lbl("Total" if title=="Earnings" else "Total Deductions",11,True)); tot_row.addStretch()
            tot_row.addWidget(_lbl(f"₹{float(e[total_key]):,.0f}",12,True,total_color)); fl.addLayout(tot_row)
            two.addWidget(f)
        cl.addLayout(two)
        net=QFrame(); net.setStyleSheet(f"QFrame{{background:{S._t('BLUE')};border-radius:8px;border:none;}}")
        nl=QHBoxLayout(net); nl.setContentsMargins(20,14,20,14)
        nl.addWidget(_lbl("NET SALARY",12,True,"white")); nl.addStretch()
        nl.addWidget(_lbl(f"₹{float(e['net_salary']):,.2f}",20,True,"white"))
        cl.addWidget(net)
        sr=QHBoxLayout(); sr.addWidget(_lbl("Status:",10,False,S._t("SUBTEXT"))); sr.addWidget(StatusBadge(str(e["pay_status"]))); sr.addStretch()
        cl.addLayout(sr)
        cl.addWidget(_lbl("System generated · No signature required",9,False,S._t("SUBTEXT"),Qt.AlignCenter))
        self._lay.addWidget(card); self._lay.addStretch()


# ── Reports ────────────────────────────────────────────────────────────────────
class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{S._t('BG')};")
        lay=QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(14)
        row=QHBoxLayout(); row.setSpacing(8)
        self._btn_audit  = QPushButton("Audit Log")
        self._btn_salary = QPushButton("Salary Summary")
        for b in (self._btn_audit,self._btn_salary):
            b.setCheckable(True); b.setFixedHeight(32)
            b.setStyleSheet(f"QPushButton{{background:{S._t('CARD')};color:{S._t('SUBTEXT')};border:1px solid {S._t('BORDER')};border-radius:6px;padding:0 14px;font-size:12px;font-weight:600;}}QPushButton:checked{{background:{S._t('BLUE')};color:white;border-color:{S._t('BLUE')};}}QPushButton:hover{{border-color:{S._t('BLUE')};color:{S._t('TEXT')};}}")
        self._btn_audit.setChecked(True)
        self._btn_audit.clicked.connect(lambda:self._sw(0)); self._btn_salary.clicked.connect(lambda:self._sw(1))
        row.addWidget(self._btn_audit); row.addWidget(self._btn_salary); row.addStretch(); lay.addLayout(row)
        self._af=CardFrame("Audit Log"); self._at=_make_table(3,["Timestamp","Action","Detail"]); self._af.add(self._at); lay.addWidget(self._af)
        self._sf=CardFrame("Salary Summary"); self._st=_make_table(6,["Department","Headcount","Gross Total","Deductions","Net Total","Avg Net"]); self._sf.add(self._st); self._sf.setVisible(False); lay.addWidget(self._sf)
        self._employees=[]; self._load_audit()

    def _sw(self,idx):
        self._btn_audit.setChecked(idx==0); self._btn_salary.setChecked(idx==1)
        self._af.setVisible(idx==0); self._sf.setVisible(idx==1)
        if idx==0: self._load_audit()
        else: self._load_salary()

    def _load_audit(self):
        import database as DB
        log=DB.get_audit_log(); self._at.setRowCount(len(log))
        for r,entry in enumerate(log):
            for c,v in enumerate([entry["ts"],entry["action"],entry["detail"]]):
                it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._at.setItem(r,c,it)

    def _load_salary(self):
        if not self._employees: return
        df=pd.DataFrame(self._employees)
        s=(df.groupby("department").agg(headcount=("emp_id","count"),gross=("gross","sum"),
           deductions=("total_deductions","sum"),net=("net_salary","sum"),avg_net=("net_salary","mean")).round(0).reset_index())
        self._st.setRowCount(len(s))
        for r,row in s.iterrows():
            for c,v in enumerate([row["department"],str(int(row["headcount"])),f"₹{row['gross']:,.0f}",f"₹{row['deductions']:,.0f}",f"₹{row['net']:,.0f}",f"₹{row['avg_net']:,.0f}"]):
                it=QTableWidgetItem(v); it.setTextAlignment(Qt.AlignCenter); self._st.setItem(r,c,it)

    def set_employees(self,e): self._employees=e


# ── Settings ───────────────────────────────────────────────────────────────────
class SettingsTab(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, user: dict):
        super().__init__()
        self._user = user
        self.setStyleSheet(f"background:{S._t('BG')};")
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;")
        inner=QWidget(); inner.setStyleSheet(f"background:{S._t('BG')};")
        lay=QVBoxLayout(inner); lay.setContentsMargins(24,20,24,24); lay.setSpacing(20)

        # ── Profile section ──────────────────────────────────────────────
        pf=CardFrame("My Profile")
        prof_row=QHBoxLayout(); prof_row.setSpacing(18)
        self._avatar=QLabel()
        self._avatar.setFixedSize(70,70)
        self._avatar.setAlignment(Qt.AlignCenter)
        self._avatar.setStyleSheet(f"background:{S._t('BLUE')};color:white;border-radius:35px;font-size:20px;font-weight:bold;border:none;")
        self._refresh_avatar()
        info_col=QVBoxLayout(); info_col.setSpacing(4)
        self._name_lbl=_lbl(user.get("full_name",""),13,True)
        self._email_lbl=_lbl(user.get("email","—"),11,False,S._t("SUBTEXT"))
        self._role_lbl=_lbl(f"Role: {user.get('role','—')}",11,False,S._t("SUBTEXT"))
        info_col.addWidget(self._name_lbl); info_col.addWidget(self._email_lbl); info_col.addWidget(self._role_lbl)
        prof_row.addWidget(self._avatar); prof_row.addLayout(info_col); prof_row.addStretch()
        btn_edit=_btn("Edit Profile",S._t("BLUE"),height=32); btn_edit.clicked.connect(self._edit_profile)
        prof_row.addWidget(btn_edit)
        pf.body.addLayout(prof_row); lay.addWidget(pf)

        # ── Theme section ────────────────────────────────────────────────
        tf=CardFrame("Appearance — Choose Theme")
        themes_grid=QGridLayout(); themes_grid.setSpacing(10)
        self._theme_btns={}
        theme_meta=[
            ("light",  "Light",  "#F8FAFC","#111827"),
            ("dark",   "Dark",   "#0F172A","#F1F5F9"),
            ("ocean",  "Ocean",  "#EFF6FF","#1E3A5F"),
            ("forest", "Forest", "#F0FDF4","#14532D"),
            ("rose",   "Rose",   "#FFF1F2","#4C0519"),
        ]
        import database as DB
        current_theme = DB.get_settings().get("theme","light")
        for i,(key,label,bg,fg) in enumerate(theme_meta):
            btn=QPushButton(label)
            btn.setFixedHeight(60); btn.setCheckable(True)
            active = (key==current_theme)
            border = "#2563EB" if active else "#CBD5E1"
            btn.setStyleSheet(f"""
                QPushButton{{background:{bg};color:{fg};border:2px solid {border};
                             border-radius:10px;font-size:13px;font-weight:600;}}
                QPushButton:hover{{border-color:#2563EB;}}
                QPushButton:checked{{border-color:#2563EB;border-width:3px;}}
            """)
            btn.setChecked(active)
            btn.clicked.connect(lambda _, k=key, b=btn: self._apply_theme(k))
            themes_grid.addWidget(btn,0,i)
            self._theme_btns[key]=btn
        tf.body.addLayout(themes_grid); lay.addWidget(tf)

        # ── Password section ─────────────────────────────────────────────
        pwf=CardFrame("Security")
        pw_row=QHBoxLayout()
        pw_row.addWidget(_lbl("Change your account password",12,False,S._t("SUBTEXT")))
        pw_row.addStretch()
        btn_pw=_btn("Change Password",S._t("BLUE"),height=32)
        btn_pw.clicked.connect(self._change_pw); pw_row.addWidget(btn_pw)
        pwf.body.addLayout(pw_row); lay.addWidget(pwf)

        lay.addStretch()
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); scroll.setWidget(inner); outer.addWidget(scroll)

    def _refresh_avatar(self):
        pic=self._user.get("profile_pic")
        if pic:
            try:
                img_data=base64.b64decode(pic); qimg=QImage.fromData(img_data)
                px=QPixmap.fromImage(qimg).scaled(70,70,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation)
                self._avatar.setPixmap(px); self._avatar.setText(""); return
            except: pass
        initials="".join(w[0].upper() for w in self._user.get("full_name","U").split()[:2])
        self._avatar.setText(initials); self._avatar.setPixmap(QPixmap())

    def _edit_profile(self):
        from dialogs import ProfileDialog
        import database as DB
        dlg=ProfileDialog(self._user, self)
        if dlg.exec_()==QDialog.Accepted:
            d=dlg.get_data()
            updated=DB.update_profile(self._user["username"],d["full_name"],d["email"],d["profile_pic"])
            self._user.update(updated)
            self._name_lbl.setText(updated.get("full_name",""))
            self._email_lbl.setText(updated.get("email","—"))
            self._refresh_avatar()
            QMessageBox.information(self,"Saved","Profile updated. Restart to refresh the sidebar.")

    def _apply_theme(self, key):
        S.set_theme(key)
        for k,b in self._theme_btns.items():
            active=(k==key)
            bg=S.THEMES[k]["BG"]; fg=S.THEMES[k]["TEXT"]
            border="#2563EB" if active else "#CBD5E1"
            b.setStyleSheet(f"""
                QPushButton{{background:{bg};color:{fg};border:2px solid {border};
                             border-radius:10px;font-size:13px;font-weight:600;}}
                QPushButton:hover{{border-color:#2563EB;}}
                QPushButton:checked{{border-color:#2563EB;border-width:3px;}}
            """)
            b.setChecked(active)
        self.theme_changed.emit(key)
        QMessageBox.information(self,"Theme Applied",f"Theme '{key}' applied.\nRestart the app to see full effect.")

    def _change_pw(self):
        from dialogs import ChangePasswordDialog
        import database as DB
        dlg=ChangePasswordDialog(self._user["username"],self)
        if dlg.exec_()==QDialog.Accepted:
            d=dlg.get_data()
            if DB.change_password(self._user["username"],d["old"],d["new"]):
                QMessageBox.information(self,"Done","Password updated.")
            else:
                QMessageBox.warning(self,"Error","Current password incorrect.")
