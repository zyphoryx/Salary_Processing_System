"""PayCore — Reusable widgets (theme-aware)"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import styles as S


def _t(k): return S._t(k)


class KPICard(QFrame):
    def __init__(self, label, value, delta="", delta_up=True, accent=None):
        super().__init__()
        self._accent = accent
        self._label = label
        self._value = value
        self._delta_text = delta
        self._delta_up = delta_up
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(88)
        self._build()

    def _build(self):
        accent = self._accent or _t("BLUE")
        self.setStyleSheet(f"""
            QFrame {{
                background:{_t("CARD")}; border:1px solid {_t("BORDER")};
                border-radius:10px; border-left:3px solid {accent};
            }}
            QLabel {{ background:transparent; border:none; }}
        """)
        # clear old layout
        old = self.layout()
        if old:
            while old.count():
                it = old.takeAt(0)
                if it.widget(): it.widget().deleteLater()
            import sip
            try: sip.delete(old)
            except: pass

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16,12,16,12); lay.setSpacing(3)
        self._lbl_w = QLabel(self._label.upper())
        self._lbl_w.setStyleSheet(f"color:{_t('SUBTEXT')};font-size:10px;font-weight:600;letter-spacing:0.8px;")
        self._val_w = QLabel(self._value)
        self._val_w.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self._val_w.setStyleSheet(f"color:{_t('TEXT')};font-size:20px;")
        self._dlt_w = QLabel(self._delta_text)
        dc = _t("GREEN") if self._delta_up else _t("AMBER")
        self._dlt_w.setStyleSheet(f"color:{dc};font-size:10px;")
        lay.addWidget(self._lbl_w); lay.addWidget(self._val_w)
        if self._delta_text: lay.addWidget(self._dlt_w)

    def update(self, value, delta="", delta_up=True):
        self._value = str(value); self._delta_text = delta; self._delta_up = delta_up
        if hasattr(self,"_val_w"):
            self._val_w.setText(str(value))
            if delta and hasattr(self,"_dlt_w"):
                self._dlt_w.setText(delta)
                dc = _t("GREEN") if delta_up else _t("AMBER")
                self._dlt_w.setStyleSheet(f"color:{dc};font-size:10px;")

    def refresh_theme(self):
        self._build()


class Divider(QFrame):
    def __init__(self, vertical=False):
        super().__init__()
        self.setFrameShape(QFrame.VLine if vertical else QFrame.HLine)
        self.setStyleSheet(f"background:{_t('BORDER')};border:none;")
        self.setFixedWidth(1) if vertical else self.setFixedHeight(1)


class StatusBadge(QLabel):
    COLORS = {
        "Paid":      ("GREEN_L","GREEN"),  "Review":    ("AMBER_L","AMBER"),
        "Hold":      ("RED_L","RED"),      "Processing":("BLUE_L","BLUE"),
        "Pending":   ("PURPLE_L","PURPLE"),"Done":      ("GREEN_L","GREEN"),
        "Overdue":   ("RED_L","RED"),      "Ready":     ("GREEN_L","GREEN"),
        "Filed":     ("TEAL_L","TEAL"),    "Completed": ("GREEN_L","GREEN"),
    }
    def __init__(self, status):
        super().__init__(status)
        bg_k, fg_k = self.COLORS.get(status, ("BG","SUBTEXT"))
        self.setStyleSheet(f"""
            QLabel {{ background:{_t(bg_k)}; color:{_t(fg_k)};
                      font-size:10px; font-weight:600;
                      padding:2px 10px; border-radius:20px; border:none; }}
        """)
        self.setAlignment(Qt.AlignCenter)


class CardFrame(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(S.card_style() + " QLabel { background:transparent; border:none; }")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16,14,16,14); outer.setSpacing(10)
        if title:
            hdr = QLabel(title)
            hdr.setFont(QFont("Segoe UI",12,QFont.Bold))
            hdr.setStyleSheet(f"color:{_t('TEXT')};font-size:12px;")
            outer.addWidget(hdr); outer.addWidget(Divider())
        self.body = QVBoxLayout(); self.body.setSpacing(6)
        outer.addLayout(self.body)

    def add(self, widget): self.body.addWidget(widget)


class SectionHeader(QWidget):
    def __init__(self, title, subtitle=""):
        super().__init__()
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,4); lay.setSpacing(2)
        t = QLabel(title); t.setFont(QFont("Segoe UI",14,QFont.Bold))
        t.setStyleSheet(f"color:{_t('TEXT')};background:transparent;")
        lay.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"color:{_t('SUBTEXT')};font-size:12px;background:transparent;")
            lay.addWidget(s)
