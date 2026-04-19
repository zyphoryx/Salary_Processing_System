"""PayCore — All Dialogs"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QPushButton,
    QFrame, QMessageBox, QFileDialog, QWidget, QSlider, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
import base64, styles as S

DEPARTMENTS   = ["Engineering","Finance","HR","IT","Marketing","Operations","Sales","Legal"]
PAYMENT_METHODS = ["Bank Transfer","Cheque","Cash","UPI"]


def _dlg_style():
    return f"""
        QDialog  {{ background:{S._t("BG")}; }}
        QLabel   {{ color:{S._t("TEXT")}; font-size:12px; background:transparent; border:none; }}
        QFrame   {{ background:{S._t("CARD")}; border:1px solid {S._t("BORDER")}; border-radius:8px; }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background:{S._t("CARD")}; border:1.5px solid {S._t("BORDER")};
            border-radius:7px; padding:6px 10px; color:{S._t("TEXT")};
        }}
    """

def _hdr(text, sz=13):
    l = QLabel(text); l.setFont(QFont("Segoe UI", sz, QFont.Bold))
    l.setStyleSheet(f"color:{S._t('TEXT')};background:transparent;border:none;")
    return l

def _lbl(text, sub=False):
    l = QLabel(text)
    l.setStyleSheet(f"color:{S._t('SUBTEXT') if sub else S._t('TEXT')};background:transparent;border:none;")
    return l


# ── Employee dialog ────────────────────────────────────────────────────────────
class EmployeeDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Employee" if not data else "Edit Employee")
        self.setMinimumWidth(500)
        self.setStyleSheet(_dlg_style())
        self._build(data)

    def _field(self, ph=""):
        w = QLineEdit(); w.setPlaceholderText(ph); return w

    def _build(self, data):
        root = QVBoxLayout(self); root.setSpacing(12); root.setContentsMargins(16,16,16,16)
        root.addWidget(_hdr("Employee Details"))

        sec1 = QFrame()
        sec1.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:8px;}} QLabel{{background:transparent;border:none;}}")
        f1 = QFormLayout(sec1); f1.setContentsMargins(14,12,14,12); f1.setSpacing(9); f1.setLabelAlignment(Qt.AlignRight)
        self.f_id    = self._field("e.g. E021")
        self.f_name  = self._field("Full name")
        self.f_dept  = QComboBox(); self.f_dept.addItems(DEPARTMENTS)
        self.f_desig = self._field("Job title")
        self.f_type  = QComboBox(); self.f_type.addItems(["Full-time","Part-time","Contract","Intern"])
        self.f_loc   = self._field("City")
        self.f_bank  = self._field("Bank account (masked)")
        self.f_join  = self._field("YYYY-MM-DD")
        for label, widget in [("ID *",self.f_id),("Name *",self.f_name),("Dept",self.f_dept),
                               ("Designation",self.f_desig),("Type",self.f_type),("Location",self.f_loc),
                               ("Bank",self.f_bank),("Join Date",self.f_join)]:
            f1.addRow(label, widget)
        root.addWidget(sec1)

        sec2 = QFrame()
        sec2.setStyleSheet(sec1.styleSheet())
        f2 = QFormLayout(sec2); f2.setContentsMargins(14,12,14,12); f2.setSpacing(9); f2.setLabelAlignment(Qt.AlignRight)
        self.f_basic = QDoubleSpinBox(); self.f_basic.setRange(10000,1000000); self.f_basic.setPrefix("₹ "); self.f_basic.setSingleStep(1000); self.f_basic.setDecimals(0)
        self.f_bonus = QDoubleSpinBox(); self.f_bonus.setRange(0,200000); self.f_bonus.setPrefix("₹ "); self.f_bonus.setDecimals(0)
        self.f_dw = QSpinBox(); self.f_dw.setRange(0,31); self.f_dw.setValue(26)
        self.f_dt = QSpinBox(); self.f_dt.setRange(1,31); self.f_dt.setValue(26)
        for label, widget in [("Basic *",self.f_basic),("Bonus",self.f_bonus),("Days Worked",self.f_dw),("Total Days",self.f_dt)]:
            f2.addRow(label, widget)
        root.addWidget(sec2)

        if data:
            self.f_id.setText(str(data.get("emp_id",""))); self.f_id.setEnabled(False)
            self.f_name.setText(str(data.get("name","")))
            idx = self.f_dept.findText(str(data.get("department",""))); self.f_dept.setCurrentIndex(idx) if idx>=0 else None
            self.f_desig.setText(str(data.get("designation","")))
            tidx = self.f_type.findText(str(data.get("employment_type",""))); self.f_type.setCurrentIndex(tidx) if tidx>=0 else None
            self.f_loc.setText(str(data.get("location",""))); self.f_bank.setText(str(data.get("bank_account","")))
            self.f_join.setText(str(data.get("join_date","")))
            self.f_basic.setValue(float(data.get("basic_salary",10000))); self.f_bonus.setValue(float(data.get("bonus",0)))
            self.f_dw.setValue(int(data.get("days_worked",26))); self.f_dt.setValue(int(data.get("total_days",26)))

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Save"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("BLUE")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self._validate); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _validate(self):
        if not self.f_id.text().strip(): QMessageBox.warning(self,"Validation","ID required."); return
        if not self.f_name.text().strip(): QMessageBox.warning(self,"Validation","Name required."); return
        self.accept()

    def get_data(self):
        return {"emp_id":self.f_id.text().strip(),"name":self.f_name.text().strip(),
                "department":self.f_dept.currentText(),"designation":self.f_desig.text().strip(),
                "basic_salary":self.f_basic.value(),"days_worked":self.f_dw.value(),
                "total_days":self.f_dt.value(),"bonus":self.f_bonus.value(),
                "join_date":self.f_join.text().strip() or "2024-01-01",
                "employment_type":self.f_type.currentText(),
                "location":self.f_loc.text().strip() or "N/A",
                "bank_account":self.f_bank.text().strip() or "****"}


# ── Payment dialog ─────────────────────────────────────────────────────────────
class PaymentDialog(QDialog):
    def __init__(self, employee, month, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Pay — {employee['name']}")
        self.setMinimumWidth(400); self._emp = employee
        self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(12)
        root.addWidget(_hdr("Process Salary Payment"))
        card = QFrame()
        card.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:8px;}} QLabel{{background:transparent;border:none;}}")
        cl = QFormLayout(card); cl.setContentsMargins(14,12,14,12); cl.setSpacing(8)
        for k,v,color in [("Employee",f"{employee['emp_id']} — {employee['name']}",S._t("TEXT")),
                           ("Department",employee["department"],S._t("TEXT")),
                           ("Net Salary",f"₹{float(employee['net_salary']):,.2f}",S._t("GREEN"))]:
            kl=QLabel(k); kl.setStyleSheet(f"color:{S._t('SUBTEXT')};font-size:11px;background:transparent;border:none;")
            vl=QLabel(v); vl.setStyleSheet(f"color:{color};font-size:12px;font-weight:bold;background:transparent;border:none;")
            cl.addRow(kl,vl)
        root.addWidget(card)
        ff = QFrame(); ff.setStyleSheet(card.styleSheet())
        fl = QFormLayout(ff); fl.setContentsMargins(14,12,14,12); fl.setSpacing(9)
        self._month  = QLineEdit(month)
        self._method = QComboBox(); self._method.addItems(PAYMENT_METHODS)
        self._amount = QDoubleSpinBox(); self._amount.setRange(0,10000000); self._amount.setPrefix("₹ "); self._amount.setDecimals(2); self._amount.setValue(float(employee["net_salary"]))
        fl.addRow("Month:",self._month); fl.addRow("Method:",self._method); fl.addRow("Amount:",self._amount)
        root.addWidget(ff)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Confirm Payment"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("GREEN")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def get_data(self): return {"month":self._month.text().strip(),"method":self._method.currentText(),"amount":self._amount.value()}


# ── Bulk Bonus dialog ──────────────────────────────────────────────────────────
class BulkBonusDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Bonus"); self.setFixedWidth(380)
        self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(12)
        root.addWidget(_hdr("Add Bonus to All Employees"))
        ff = QFrame(); ff.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:8px;}} QLabel{{background:transparent;border:none;}}")
        fl = QFormLayout(ff); fl.setContentsMargins(14,12,14,12); fl.setSpacing(9)
        self._amount = QDoubleSpinBox(); self._amount.setRange(100,500000); self._amount.setPrefix("₹ "); self._amount.setDecimals(0); self._amount.setValue(5000)
        self._dept   = QComboBox(); self._dept.addItems(["All Departments"] + DEPARTMENTS)
        fl.addRow("Bonus Amount:", self._amount); fl.addRow("Apply To:", self._dept)
        root.addWidget(ff)
        note = QLabel("This adds the bonus to each employee's existing bonus.")
        note.setWordWrap(True); note.setStyleSheet(f"color:{S._t('SUBTEXT')};font-size:10px;background:transparent;border:none;")
        root.addWidget(note)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Apply Bonus"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("GREEN")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def get_data(self):
        dept = self._dept.currentText()
        return {"amount": self._amount.value(), "dept": "All" if dept == "All Departments" else dept}


# ── Bulk Pay dialog ────────────────────────────────────────────────────────────
class BulkPayDialog(QDialog):
    def __init__(self, count, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Pay"); self.setFixedWidth(380)
        self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(12)
        root.addWidget(_hdr("Pay Selected Employees"))
        info = QLabel(f"You are about to pay {count} employee(s)\nTotal: ₹{total:,.2f}")
        info.setStyleSheet(f"color:{S._t('TEXT')};background:transparent;border:none;font-size:13px;")
        root.addWidget(info)
        ff = QFrame(); ff.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:8px;}} QLabel{{background:transparent;border:none;}}")
        fl = QFormLayout(ff); fl.setContentsMargins(14,12,14,12); fl.setSpacing(9)
        self._month  = QLineEdit(__import__("datetime").datetime.now().strftime("%B %Y"))
        self._method = QComboBox(); self._method.addItems(PAYMENT_METHODS)
        fl.addRow("Month:", self._month); fl.addRow("Method:", self._method)
        root.addWidget(ff)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText(f"Pay {count} Employees"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("GREEN")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def get_data(self): return {"month":self._month.text().strip(),"method":self._method.currentText()}


# ── Change Password dialog ─────────────────────────────────────────────────────
class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password"); self.setFixedWidth(360)
        self._username = username; self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(12)
        root.addWidget(_hdr("Change Password"))
        fl = QFormLayout(); fl.setSpacing(10)
        self._old = QLineEdit(); self._old.setEchoMode(QLineEdit.Password)
        self._new = QLineEdit(); self._new.setEchoMode(QLineEdit.Password)
        self._conf= QLineEdit(); self._conf.setEchoMode(QLineEdit.Password)
        fl.addRow("Current:",self._old); fl.addRow("New:",self._new); fl.addRow("Confirm:",self._conf)
        root.addLayout(fl)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Update"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("BLUE")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self._validate); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _validate(self):
        if not self._old.text(): QMessageBox.warning(self,"Error","Enter current password."); return
        if len(self._new.text()) < 6: QMessageBox.warning(self,"Error","Min 6 characters."); return
        if self._new.text() != self._conf.text(): QMessageBox.warning(self,"Error","Passwords don't match."); return
        self.accept()

    def get_data(self): return {"old":self._old.text(),"new":self._new.text()}


# ── Forgot Password dialog ─────────────────────────────────────────────────────
class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset Password"); self.setFixedWidth(380)
        self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(12)
        root.addWidget(_hdr("Reset Password"))
        note = QLabel("Enter your registered email address.\nA new password will be set if your email is found.")
        note.setWordWrap(True); note.setStyleSheet(f"color:{S._t('SUBTEXT')};background:transparent;border:none;font-size:11px;")
        root.addWidget(note)
        fl = QFormLayout(); fl.setSpacing(10)
        self._email   = QLineEdit(); self._email.setPlaceholderText("you@company.com")
        self._new_pw  = QLineEdit(); self._new_pw.setEchoMode(QLineEdit.Password); self._new_pw.setPlaceholderText("New password")
        self._conf_pw = QLineEdit(); self._conf_pw.setEchoMode(QLineEdit.Password); self._conf_pw.setPlaceholderText("Confirm")
        fl.addRow("Email:",self._email); fl.addRow("New Password:",self._new_pw); fl.addRow("Confirm:",self._conf_pw)
        root.addLayout(fl)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Reset Password"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("BLUE")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self._validate); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _validate(self):
        if not self._email.text().strip(): QMessageBox.warning(self,"Error","Enter email."); return
        if len(self._new_pw.text()) < 6: QMessageBox.warning(self,"Error","Min 6 characters."); return
        if self._new_pw.text() != self._conf_pw.text(): QMessageBox.warning(self,"Error","Don't match."); return
        self.accept()

    def get_data(self): return {"email":self._email.text().strip(),"new_pw":self._new_pw.text()}


# ── Profile dialog ─────────────────────────────────────────────────────────────
class ProfileDialog(QDialog):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Profile"); self.setMinimumWidth(420)
        self._user = user; self._pic_b64 = user.get("profile_pic")
        self.setStyleSheet(_dlg_style())
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(14)
        root.addWidget(_hdr("Edit Profile"))

        # Avatar
        av_row = QHBoxLayout(); av_row.setSpacing(14)
        self._avatar_lbl = QLabel()
        self._avatar_lbl.setFixedSize(72, 72)
        self._avatar_lbl.setAlignment(Qt.AlignCenter)
        self._avatar_lbl.setStyleSheet(f"background:{S._t('BLUE')};color:white;border-radius:36px;font-size:22px;font-weight:bold;border:none;")
        self._refresh_avatar()
        btn_pic = QPushButton("Upload Photo")
        btn_pic.setStyleSheet(S.btn(S._t("NAVY2"), "#94A3B8"))
        btn_pic.clicked.connect(self._pick_photo)
        av_col = QVBoxLayout()
        av_col.addWidget(self._avatar_lbl)
        av_col.addWidget(btn_pic)
        av_row.addLayout(av_col)
        info_col = QVBoxLayout(); info_col.setSpacing(4)
        info_col.addWidget(_lbl(user["username"], sub=True))
        info_col.addWidget(_lbl(user["role"], sub=True))
        info_col.addWidget(_lbl(f"Last login: {str(user.get('last_login','—'))[:19]}", sub=True))
        av_row.addLayout(info_col); av_row.addStretch()
        root.addLayout(av_row)

        ff = QFrame(); ff.setStyleSheet(f"QFrame{{background:{S._t('CARD')};border:1px solid {S._t('BORDER')};border-radius:8px;}} QLabel{{background:transparent;border:none;}}")
        fl = QFormLayout(ff); fl.setContentsMargins(14,12,14,12); fl.setSpacing(9)
        self._name  = QLineEdit(user.get("full_name",""))
        self._email = QLineEdit(user.get("email",""))
        fl.addRow("Display Name:", self._name)
        fl.addRow("Email:", self._email)
        root.addWidget(ff)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Save Profile"); btns.button(QDialogButtonBox.Ok).setStyleSheet(S.btn(S._t("BLUE")))
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(S.btn("#6B7280"))
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _refresh_avatar(self):
        if self._pic_b64:
            try:
                img_data = base64.b64decode(self._pic_b64)
                qimg = QImage.fromData(img_data)
                px = QPixmap.fromImage(qimg).scaled(72, 72, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self._avatar_lbl.setPixmap(px); self._avatar_lbl.setText(""); return
            except: pass
        initials = "".join(w[0].upper() for w in self._user.get("full_name","U").split()[:2])
        self._avatar_lbl.setText(initials); self._avatar_lbl.setPixmap(QPixmap())

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            with open(path, "rb") as f: self._pic_b64 = base64.b64encode(f.read()).decode()
            self._refresh_avatar()

    def get_data(self): return {"full_name":self._name.text(),"email":self._email.text(),"profile_pic":self._pic_b64}
