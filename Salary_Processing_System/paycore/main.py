"""PayCore — Main Window"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush, QPixmap, QImage

import styles as S
import database as DB

# Expose current user globally so tabs can access it
import __main__

class Loader(QThread):
    done=pyqtSignal(list); error=pyqtSignal(str)
    def run(self):
        try: self.done.emit(DB.load_employees())
        except Exception as e: self.error.emit(str(e))


class NavBtn(QPushButton):
    def __init__(self, icon, label, parent=None):
        super().__init__(f" {icon}  {label}", parent)
        self.setCheckable(True); self.setFixedHeight(38); self.setCursor(Qt.PointingHandCursor)
        self._set(False)

    def _set(self, checked):
        if checked:
            self.setStyleSheet(f"QPushButton{{background:rgba(37,99,235,0.18);color:#93C5FD;border:none;border-radius:8px;text-align:left;padding-left:14px;font-size:13px;font-weight:600;}}")
        else:
            self.setStyleSheet(f"QPushButton{{background:transparent;color:#64748B;border:none;border-radius:8px;text-align:left;padding-left:14px;font-size:13px;}}QPushButton:hover{{background:rgba(255,255,255,0.06);color:#CBD5E1;}}")

    def setChecked(self, v): super().setChecked(v); self._set(v)


class Sidebar(QFrame):
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        g=QLinearGradient(0,0,0,self.height())
        top=S.THEMES.get(S._current_theme,S.THEMES["light"]).get("SIDEBAR_TOP","#0d1b3e")
        btm=S.THEMES.get(S._current_theme,S.THEMES["light"]).get("SIDEBAR_BTM","#0a1628")
        g.setColorAt(0,QColor(top)); g.setColorAt(1,QColor(btm))
        p.fillRect(self.rect(),QBrush(g))
        p.setPen(QColor(255,255,255,12)); p.drawLine(self.width()-1,0,self.width()-1,self.height()); p.end()


class MainWindow(QMainWindow):
    def __init__(self, user: dict):
        super().__init__()
        self._user = user
        __main__._current_user = user   # expose globally
        S.load_theme()
        self.setWindowTitle("PayCore")
        self.setMinimumSize(1280,780)
        self._employees=[]
        QApplication.instance().setStyleSheet(S.app_style())
        self._build_ui(); self._load_data()

    def _build_ui(self):
        root=QWidget(); self.setCentralWidget(root)
        lay=QHBoxLayout(root); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        lay.addWidget(self._build_sidebar()); lay.addWidget(self._build_main(),1)
        self._status=QStatusBar()
        self._status.setStyleSheet(f"QStatusBar{{background:{S._t('BG')};color:{S._t('SUBTEXT')};font-size:11px;border-top:1px solid {S._t('BORDER')};}}")
        self.setStatusBar(self._status); self._status.showMessage("Loading…")

    def _build_sidebar(self):
        self._side=Sidebar(); self._side.setFixedWidth(210); self._side.setStyleSheet("border:none;")
        lay=QVBoxLayout(self._side); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Logo
        logo_w=QWidget(); logo_w.setFixedHeight(62); logo_w.setStyleSheet("background:transparent;")
        ll=QVBoxLayout(logo_w); ll.setContentsMargins(20,14,16,10); ll.setSpacing(0)
        brand=QLabel("PayCore"); brand.setFont(QFont("Segoe UI",16,QFont.Bold))
        brand.setStyleSheet("color:white;background:transparent;letter-spacing:1px;"); ll.addWidget(brand)
        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:rgba(255,255,255,0.08);border:none;")
        lay.addWidget(logo_w); lay.addWidget(sep)

        # Nav
        nav=QWidget(); nav.setStyleSheet("background:transparent;")
        nl=QVBoxLayout(nav); nl.setContentsMargins(10,14,10,10); nl.setSpacing(2)
        def section(txt):
            l=QLabel(txt); l.setStyleSheet("color:rgba(100,116,139,0.8);font-size:9px;font-weight:700;letter-spacing:1.5px;padding:10px 6px 4px;background:transparent;"); nl.addWidget(l)

        self._nav_btns=[]
        section("MAIN")
        for icon,lbl,idx in [("⬛","Dashboard",0),("▶","Payroll Runs",1),
                               ("—","Payments",2),("≡","Employees",3),("□","Pay Slips",4)]:
            b=NavBtn(icon,lbl); b.clicked.connect(lambda _,i=idx:self._switch(i))
            nl.addWidget(b); self._nav_btns.append(b)
        section("ANALYTICS")
        for icon,lbl,idx in [("◑","Dept Analytics",5),("☰","Reports",6)]:
            b=NavBtn(icon,lbl); b.clicked.connect(lambda _,i=idx:self._switch(i))
            nl.addWidget(b); self._nav_btns.append(b)
        section("SYSTEM")

        #b=NavBtn("⚙","Settings",7)
        b=NavBtn("⚙","Settings"); b.clicked.connect(lambda _:self._switch(7))
        nl.addWidget(b); self._nav_btns.append(b)
        nl.addStretch(); lay.addWidget(nav,1)

        # Footer — user info
        fsep=QFrame(); fsep.setFixedHeight(1); fsep.setStyleSheet("background:rgba(255,255,255,0.07);border:none;"); lay.addWidget(fsep)
        footer=QWidget(); footer.setFixedHeight(68); footer.setStyleSheet("background:transparent;")
        fl=QVBoxLayout(footer); fl.setContentsMargins(14,8,14,8); fl.setSpacing(4)
        user_row=QHBoxLayout(); user_row.setSpacing(8)
        self._ava_lbl=QLabel()
        self._ava_lbl.setFixedSize(28,28); self._ava_lbl.setAlignment(Qt.AlignCenter)
        self._ava_lbl.setStyleSheet(f"background:{S._t('BLUE')};color:white;border-radius:14px;font-size:10px;font-weight:bold;")
        self._refresh_avatar()
        info=QVBoxLayout(); info.setSpacing(0)
        self._name_footer=QLabel(self._user["full_name"]); self._name_footer.setStyleSheet("color:#CBD5E1;font-size:11px;font-weight:600;background:transparent;")
        self._role_footer=QLabel(self._user["role"]); self._role_footer.setStyleSheet("color:#475569;font-size:10px;background:transparent;")
        info.addWidget(self._name_footer); info.addWidget(self._role_footer)
        user_row.addWidget(self._ava_lbl); user_row.addLayout(info); user_row.addStretch(); fl.addLayout(user_row)
        btn_row=QHBoxLayout(); btn_row.setSpacing(4)
        btn_out=QPushButton("Sign out"); btn_out.setFixedHeight(20)
        btn_out.setStyleSheet("QPushButton{background:rgba(220,38,38,0.15);color:#F87171;border:none;border-radius:4px;font-size:9px;padding:1px 8px;}QPushButton:hover{background:rgba(220,38,38,0.28);}")
        btn_out.clicked.connect(self._logout); btn_row.addWidget(btn_out); btn_row.addStretch(); fl.addLayout(btn_row)
        lay.addWidget(footer); return self._side

    def _refresh_avatar(self):
        pic=self._user.get("profile_pic")
        if pic:
            try:
                img=QImage.fromData(__import__("base64").b64decode(pic))
                px=QPixmap.fromImage(img).scaled(28,28,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation)
                self._ava_lbl.setPixmap(px); self._ava_lbl.setText(""); return
            except: pass
        initials="".join(w[0].upper() for w in self._user.get("full_name","U").split()[:2])
        self._ava_lbl.setText(initials); self._ava_lbl.setPixmap(QPixmap())

    def _build_main(self):
        from tabs import (DashboardTab, PayrollRunsTab, PaymentsTab,
                          EmployeeTab, PayslipTab, DeptTab, ReportsTab, SettingsTab)
        main=QFrame(); main.setStyleSheet(f"QFrame{{background:{S._t('BG')};border:none;}}")
        lay=QVBoxLayout(main); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Top bar
        topbar=QFrame(); topbar.setFixedHeight(52)
        topbar.setStyleSheet(f"QFrame{{background:{S._t('TOPBAR')};border-bottom:1px solid {S._t('TOPBAR_BORDER')};}}QLabel{{background:transparent;border:none;}}")
        tl=QHBoxLayout(topbar); tl.setContentsMargins(24,0,24,0)
        self._page_title=QLabel("Dashboard"); self._page_title.setFont(QFont("Segoe UI",14,QFont.Bold))
        self._page_title.setStyleSheet(f"color:{S._t('TEXT')};")
        self._badge=QLabel("Loading…")
        self._badge.setStyleSheet(f"background:{S._t('AMBER_L')};color:{S._t('AMBER')};font-size:11px;font-weight:600;padding:3px 12px;border-radius:20px;")
        tl.addWidget(self._page_title); tl.addStretch(); tl.addWidget(self._badge); lay.addWidget(topbar)

        # Pages
        self._tab_dash    = DashboardTab()
        self._tab_payroll = PayrollRunsTab(self._user)
        self._tab_pay     = PaymentsTab(self._user)
        self._tab_emp     = EmployeeTab()
        self._tab_slip    = PayslipTab()
        self._tab_dept    = DeptTab()
        self._tab_rep     = ReportsTab()
        self._tab_set     = SettingsTab(self._user)
        self._tab_set.theme_changed.connect(self._on_theme_change)

        self._pages=[self._tab_dash,self._tab_payroll,self._tab_pay,
                     self._tab_emp,self._tab_slip,self._tab_dept,self._tab_rep,self._tab_set]
        pc=QFrame(); pc.setStyleSheet(f"QFrame{{background:{S._t('BG')};border:none;}}")
        pcl=QVBoxLayout(pc); pcl.setContentsMargins(0,0,0,0)
        for p in self._pages: pcl.addWidget(p); p.setVisible(False)
        lay.addWidget(pc,1)

        self._tab_emp.request_add.connect(self._add_emp)
        self._tab_emp.request_edit.connect(self._edit_emp)
        self._tab_emp.request_delete.connect(self._del_emp)
        self._switch(0); return main

    def _on_theme_change(self, key):
        QApplication.instance().setStyleSheet(S.app_style())
        self._status.showMessage(f"Theme '{key}' applied — restart for full effect")

    def _switch(self, idx):
        TITLES=["Dashboard","Payroll Runs","Payments","Employees","Pay Slips","Dept Analytics","Reports","Settings"]
        for i,p in enumerate(self._pages): p.setVisible(i==idx)
        for i,b in enumerate(self._nav_btns): b.setChecked(i==idx)
        self._page_title.setText(TITLES[idx])

    def _load_data(self):
        self._loader=Loader(); self._loader.done.connect(self._on_loaded); self._loader.error.connect(self._on_err); self._loader.start()

    def _on_loaded(self, employees):
        self._employees=employees; self._refresh_all()
        self._badge.setText(f"{len(employees)} employees")
        self._badge.setStyleSheet(f"background:{S._t('GREEN_L')};color:{S._t('GREEN')};font-size:11px;font-weight:600;padding:3px 12px;border-radius:20px;")
        self._status.showMessage(f"{len(employees)} employees  ·  {self._user['username']} ({self._user['role']})")

    def _on_err(self, msg):
        self._badge.setText("Error")
        self._badge.setStyleSheet(f"background:{S._t('RED_L')};color:{S._t('RED')};font-size:11px;font-weight:600;padding:3px 12px;border-radius:20px;")
        QMessageBox.critical(self,"Error",msg)

    def _refresh_all(self):
        self._tab_emp.load(self._employees); self._tab_slip.load(self._employees)
        self._tab_dash.refresh(self._employees); self._tab_dept.refresh(self._employees)
        self._tab_payroll.set_employees(self._employees); self._tab_pay.set_employees(self._employees)
        self._tab_rep.set_employees(self._employees)
        self._status.showMessage(f"{len(self._employees)} employees  ·  {self._user['username']}")

    def _add_emp(self):
        from dialogs import EmployeeDialog
        dlg=EmployeeDialog(self)
        if dlg.exec_()!=EmployeeDialog.Accepted: return
        d=dlg.get_data()
        try: DB.add_employee(d); self._employees=DB.load_employees(); self._refresh_all(); QMessageBox.information(self,"Added",f"{d['name']} added.")
        except ValueError as e: QMessageBox.warning(self,"Duplicate",str(e))
        except Exception as e: QMessageBox.critical(self,"Error",str(e))

    def _edit_emp(self, emp_id):
        from dialogs import EmployeeDialog
        emp=next((e for e in self._employees if e["emp_id"]==emp_id),None)
        if not emp: return
        dlg=EmployeeDialog(self,emp)
        if dlg.exec_()!=EmployeeDialog.Accepted: return
        d=dlg.get_data()
        try: DB.update_employee(emp_id,d); self._employees=DB.load_employees(); self._refresh_all(); QMessageBox.information(self,"Updated",f"{d['name']} updated.")
        except Exception as e: QMessageBox.critical(self,"Error",str(e))

    def _del_emp(self, emp_id):
        emp=next((e for e in self._employees if e["emp_id"]==emp_id),None)
        if not emp: return
        if QMessageBox.question(self,"Delete",f"Delete {emp['name']}?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try: DB.delete_employee(emp_id); self._employees=DB.load_employees(); self._refresh_all()
            except Exception as e: QMessageBox.critical(self,"Error",str(e))

    def _logout(self):
        if QMessageBox.question(self,"Sign out","Sign out of PayCore?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.close()
            from login import LoginWindow
            login=LoginWindow()
            if login.exec_()==LoginWindow.Accepted:
                user=login.get_user()
                if user: w=MainWindow(user); w.show(); QApplication.instance()._win=w


def main():
    app=QApplication(sys.argv); app.setStyle("Fusion")
    S.load_theme()
    from login import LoginWindow
    login=LoginWindow()
    if login.exec_()!=LoginWindow.Accepted: sys.exit(0)
    user=login.get_user()
    if not user: sys.exit(0)
    win=MainWindow(user); win.show(); sys.exit(app.exec_())

if __name__=="__main__": main()
