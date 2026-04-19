"""PayCore — Login Window (Glassmorphism)"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (QFont, QPainter, QLinearGradient, QColor,
                          QBrush, QPen, QRadialGradient, QPainterPath)
import math
from database import authenticate


class GlassBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tick = 0
        t = QTimer(self); t.timeout.connect(self._anim); t.start(40)

    def _anim(self): self._tick += 1; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        grad = QLinearGradient(0,0,w,h)
        grad.setColorAt(0.0, QColor("#0d2f82")); grad.setColorAt(0.45, QColor("#1040b0")); grad.setColorAt(1.0, QColor("#0b3acc"))
        p.fillRect(self.rect(), QBrush(grad))
        t = self._tick * 0.018
        blobs = [(w*.08,h*.20,130,"#2563eb",.28),(w*.80,h*.15,110,"#1d4ed8",.22),
                 (w*.18,h*.78,100,"#3b82f6",.24),(w*.75,h*.75,140,"#1e40af",.18),
                 (w*.50,h*.92,80,"#2563eb",.16),(w*.90,h*.48,75,"#60a5fa",.14)]
        for i,(bx,by,br,col,alpha) in enumerate(blobs):
            ox=math.sin(t+i*1.1)*20; oy=math.cos(t*.7+i*.8)*16
            rg=QRadialGradient(bx+ox,by+oy,br)
            c=QColor(col); c.setAlphaF(alpha); c2=QColor(col); c2.setAlphaF(0)
            rg.setColorAt(0,c); rg.setColorAt(1,c2)
            p.setBrush(QBrush(rg)); p.setPen(Qt.NoPen)
            p.drawEllipse(int(bx+ox-br),int(by+oy-br),br*2,br*2)
        sq=QColor("#7ab8ff"); sq.setAlphaF(.38)
        p.setPen(QPen(sq,7,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
        pa=QPainterPath(); pa.moveTo(w*.06,h*.28); pa.cubicTo(w*.00,h*.18,w*.16,h*.14,w*.10,h*.30); pa.cubicTo(w*.04,h*.44,w*.18,h*.46,w*.12,h*.56)
        p.drawPath(pa)
        sq2=QColor("#93c5fd"); sq2.setAlphaF(.26)
        p.setPen(QPen(sq2,6,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        pb=QPainterPath(); pb.moveTo(w*.86,h*.60); pb.cubicTo(w*.92,h*.50,w*.78,h*.46,w*.84,h*.64); pb.cubicTo(w*.90,h*.76,w*.78,h*.74,w*.82,h*.82)
        p.drawPath(pb)
        c3=QColor("#1d4ed8"); c3.setAlphaF(.18); p.setBrush(QBrush(c3)); p.setPen(Qt.NoPen)
        p.drawEllipse(int(w*.68),int(-h*.30),int(h*.80),int(h*.80))
        c4=QColor("#1e3a8a"); c4.setAlphaF(.22); p.setBrush(QBrush(c4))
        p.drawEllipse(int(-w*.12),int(h*.55),int(h*.70),int(h*.70))
        p.end()


class GlassCard(QWidget):
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); w,h=self.width(),self.height()
        bg=QColor(255,255,255,30); p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen); p.drawRoundedRect(0,0,w,h,18,18)
        bd=QColor(255,255,255,60); p.setPen(QPen(bd,1.2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(1,1,w-2,h-2,17,17)
        p.end()


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PayCore")
        self.setFixedSize(880, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._user = None; self._build()

    def _build(self):
        self._bg = GlassBackground(self); self._bg.setGeometry(0,0,880,500)

        brand = QLabel("PayCore", self); brand.setFont(QFont("Segoe UI",46,QFont.Bold))
        brand.setStyleSheet("color:rgba(255,255,255,0.92);background:transparent;border:none;"); brand.move(50,168)
        sub = QLabel("Salary Processing\nManagement System", self); sub.setFont(QFont("Segoe UI",12))
        sub.setStyleSheet("color:rgba(255,255,255,0.42);background:transparent;border:none;"); sub.move(52,232)
        copy = QLabel("© 2026 PayCore  ·  Secure Payroll", self)
        copy.setStyleSheet("color:rgba(255,255,255,0.25);font-size:10px;background:transparent;border:none;"); copy.move(24,476)

        card = GlassCard(self); cw,ch=348,440; cx=880-cw-52; cy=(500-ch)//2
        card.setGeometry(cx,cy,cw,ch)

        cl = QVBoxLayout(card); cl.setContentsMargins(36,26,36,22); cl.setSpacing(0)

        badge_row = QHBoxLayout()
        dot=QLabel("●"); dot.setStyleSheet("color:#93c5fd;font-size:9px;background:transparent;border:none;")
        badge=QLabel("PayCore"); badge.setStyleSheet("color:rgba(255,255,255,0.55);font-size:10px;font-weight:bold;letter-spacing:2px;background:transparent;border:none;")
        badge_row.addWidget(dot); badge_row.addSpacing(4); badge_row.addWidget(badge); badge_row.addStretch()
        cl.addLayout(badge_row); cl.addSpacing(4)

        title=QLabel("Login"); title.setFont(QFont("Segoe UI",26,QFont.Bold))
        title.setStyleSheet("color:white;background:transparent;border:none;"); cl.addWidget(title); cl.addSpacing(16)

        inp_style = """
            QLineEdit { background:rgba(255,255,255,0.93); border:none; border-radius:8px;
                        padding:8px 14px; font-size:13px; color:#0f172a; }
            QLineEdit:focus { background:white; border:2px solid #60a5fa; }
        """
        lbl_style = "color:rgba(255,255,255,0.75);font-size:11px;font-weight:600;background:transparent;border:none;"

        u_lbl=QLabel("Username"); u_lbl.setStyleSheet(lbl_style); cl.addWidget(u_lbl); cl.addSpacing(4)
        self._username=QLineEdit(); self._username.setPlaceholderText("username"); self._username.setFixedHeight(40); self._username.setText("admin"); self._username.setStyleSheet(inp_style); cl.addWidget(self._username); cl.addSpacing(10)

        p_lbl=QLabel("Password"); p_lbl.setStyleSheet(lbl_style); cl.addWidget(p_lbl); cl.addSpacing(4)
        self._password=QLineEdit(); self._password.setPlaceholderText("Password"); self._password.setEchoMode(QLineEdit.Password); self._password.setFixedHeight(40); self._password.setText("admin123"); self._password.setStyleSheet(inp_style); cl.addWidget(self._password); cl.addSpacing(5)

        row2=QHBoxLayout()
        show=QCheckBox("Show"); show.setStyleSheet("color:rgba(255,255,255,0.50);font-size:10px;background:transparent;border:none;")
        show.stateChanged.connect(lambda s: self._password.setEchoMode(QLineEdit.Normal if s else QLineEdit.Password))
        forgot=QPushButton("Forgot Password?"); forgot.setStyleSheet("QPushButton{color:rgba(255,255,255,0.50);background:transparent;border:none;font-size:10px;text-decoration:underline;}QPushButton:hover{color:white;}")
        forgot.clicked.connect(self._forgot)
        row2.addWidget(show); row2.addStretch(); row2.addWidget(forgot); cl.addLayout(row2); cl.addSpacing(5)

        self._err=QLabel(""); self._err.setStyleSheet("color:#fca5a5;background:rgba(220,38,38,0.22);border:1px solid rgba(220,38,38,0.35);border-radius:6px;padding:5px 10px;font-size:11px;"); self._err.setVisible(False); self._err.setWordWrap(True); cl.addWidget(self._err); cl.addSpacing(8)

        self._btn=QPushButton("Sign in"); self._btn.setFixedHeight(42)
        self._btn.setStyleSheet("QPushButton{background:#0c2872;color:white;border:none;border-radius:8px;font-size:14px;font-weight:bold;}QPushButton:hover{background:#1a3fa0;}QPushButton:pressed{background:#071b50;}")
        self._btn.clicked.connect(self._attempt); self._password.returnPressed.connect(self._attempt); self._username.returnPressed.connect(self._password.setFocus); cl.addWidget(self._btn); cl.addStretch()

        hint=QLabel("admin / admin123   ·   hr / hr1234"); hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:rgba(255,255,255,0.28);font-size:9px;background:transparent;border:none;"); cl.addWidget(hint)

    def _attempt(self):
        u=self._username.text().strip(); pw=self._password.text()
        if not u or not pw: self._show_err("Enter username and password."); return
        user=authenticate(u, pw)
        if user: self._user=user; self.accept()
        else: self._show_err("Invalid username or password."); self._password.clear(); self._password.setFocus()

    def _show_err(self, msg): self._err.setText(f"⚠  {msg}"); self._err.setVisible(True)

    def _forgot(self):
        from dialogs import ForgotPasswordDialog
        import database as DB
        dlg=ForgotPasswordDialog(self)
        if dlg.exec_()==QDialog.Accepted:
            d=dlg.get_data()
            if DB.reset_password_by_email(d["email"], d["new_pw"]):
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self,"Done","Password reset. You can now login with your new password.")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self,"Not Found",f"No account found for email: {d['email']}\n\nIf not registered, contact admin.")

    def get_user(self): return self._user

from PyQt5.QtWidgets import QDialog
