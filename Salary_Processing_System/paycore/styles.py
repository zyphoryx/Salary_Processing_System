"""PayCore — Theme system with multiple themes"""

# ── Theme definitions ──────────────────────────────────────────────────────────
THEMES = {
    "light": {
        "BG": "#F8FAFC", "CARD": "#FFFFFF", "BORDER": "#E8EDF3",
        "TEXT": "#111827", "SUBTEXT": "#6B7280",
        "NAVY": "#0F172A", "NAVY2": "#1E293B", "NAVY3": "#334155",
        "BLUE": "#2563EB", "BLUE_L": "#EFF6FF", "BLUE_T": "#BFDBFE",
        "GREEN": "#16A34A", "GREEN_L": "#F0FDF4",
        "AMBER": "#D97706", "AMBER_L": "#FFFBEB",
        "RED": "#DC2626",   "RED_L": "#FEF2F2",
        "PURPLE": "#7C3AED","PURPLE_L": "#F5F3FF",
        "TEAL": "#0891B2",  "TEAL_L": "#ECFEFF",
        "WHITE": "#FFFFFF",
        "SIDEBAR_TOP": "#0d1b3e", "SIDEBAR_BTM": "#0a1628",
        "TOPBAR": "#FFFFFF", "TOPBAR_BORDER": "#E8EDF3",
        "ALT_ROW": "#FAFBFC",
    },
    "dark": {
        "BG": "#0F172A", "CARD": "#1E293B", "BORDER": "#334155",
        "TEXT": "#F1F5F9", "SUBTEXT": "#94A3B8",
        "NAVY": "#020817", "NAVY2": "#0F172A", "NAVY3": "#1E293B",
        "BLUE": "#3B82F6", "BLUE_L": "#1E3A5F", "BLUE_T": "#1E40AF",
        "GREEN": "#22C55E", "GREEN_L": "#052E16",
        "AMBER": "#F59E0B", "AMBER_L": "#1C1206",
        "RED": "#EF4444",   "RED_L": "#1F0808",
        "PURPLE": "#A855F7","PURPLE_L": "#1A0538",
        "TEAL": "#22D3EE",  "TEAL_L": "#042F39",
        "WHITE": "#1E293B",
        "SIDEBAR_TOP": "#020817", "SIDEBAR_BTM": "#020817",
        "TOPBAR": "#1E293B", "TOPBAR_BORDER": "#334155",
        "ALT_ROW": "#162032",
    },
    "ocean": {
        "BG": "#EFF6FF", "CARD": "#FFFFFF", "BORDER": "#BFDBFE",
        "TEXT": "#1E3A5F", "SUBTEXT": "#4B7EC8",
        "NAVY": "#1E3A5F", "NAVY2": "#1D4ED8", "NAVY3": "#2563EB",
        "BLUE": "#1D4ED8", "BLUE_L": "#DBEAFE", "BLUE_T": "#93C5FD",
        "GREEN": "#059669", "GREEN_L": "#D1FAE5",
        "AMBER": "#D97706", "AMBER_L": "#FEF3C7",
        "RED": "#DC2626",   "RED_L": "#FEE2E2",
        "PURPLE": "#6D28D9","PURPLE_L": "#EDE9FE",
        "TEAL": "#0891B2",  "TEAL_L": "#CFFAFE",
        "WHITE": "#FFFFFF",
        "SIDEBAR_TOP": "#1E3A5F", "SIDEBAR_BTM": "#1E40AF",
        "TOPBAR": "#FFFFFF", "TOPBAR_BORDER": "#BFDBFE",
        "ALT_ROW": "#F0F7FF",
    },
    "forest": {
        "BG": "#F0FDF4", "CARD": "#FFFFFF", "BORDER": "#BBF7D0",
        "TEXT": "#14532D", "SUBTEXT": "#4B7A5E",
        "NAVY": "#14532D", "NAVY2": "#166534", "NAVY3": "#15803D",
        "BLUE": "#16A34A", "BLUE_L": "#DCFCE7", "BLUE_T": "#86EFAC",
        "GREEN": "#15803D", "GREEN_L": "#F0FDF4",
        "AMBER": "#B45309", "AMBER_L": "#FEF3C7",
        "RED": "#B91C1C",   "RED_L": "#FEE2E2",
        "PURPLE": "#6D28D9","PURPLE_L": "#EDE9FE",
        "TEAL": "#0D9488",  "TEAL_L": "#CCFBF1",
        "WHITE": "#FFFFFF",
        "SIDEBAR_TOP": "#14532D", "SIDEBAR_BTM": "#052E16",
        "TOPBAR": "#FFFFFF", "TOPBAR_BORDER": "#BBF7D0",
        "ALT_ROW": "#F7FEF9",
    },
    "rose": {
        "BG": "#FFF1F2", "CARD": "#FFFFFF", "BORDER": "#FECDD3",
        "TEXT": "#4C0519", "SUBTEXT": "#9F1239",
        "NAVY": "#4C0519", "NAVY2": "#881337", "NAVY3": "#9F1239",
        "BLUE": "#E11D48", "BLUE_L": "#FFE4E6", "BLUE_T": "#FECDD3",
        "GREEN": "#16A34A", "GREEN_L": "#DCFCE7",
        "AMBER": "#D97706", "AMBER_L": "#FFFBEB",
        "RED": "#BE123C",   "RED_L": "#FFE4E6",
        "PURPLE": "#7C3AED","PURPLE_L": "#F5F3FF",
        "TEAL": "#0891B2",  "TEAL_L": "#ECFEFF",
        "WHITE": "#FFFFFF",
        "SIDEBAR_TOP": "#4C0519", "SIDEBAR_BTM": "#3B0013",
        "TOPBAR": "#FFFFFF", "TOPBAR_BORDER": "#FECDD3",
        "ALT_ROW": "#FFF5F6",
    },
}

_current_theme = "light"

def set_theme(name: str):
    global _current_theme
    if name in THEMES:
        _current_theme = name
        import database as DB
        s = DB.get_settings(); s["theme"] = name; DB.save_settings(s)

def load_theme():
    global _current_theme
    import database as DB
    _current_theme = DB.get_settings().get("theme", "light")

def _t(key):
    return THEMES.get(_current_theme, THEMES["light"]).get(key, THEMES["light"][key])


# ── Property proxies — used throughout the codebase ───────────────────────────
def __getattr__(name):
    t = THEMES.get(_current_theme, THEMES["light"])
    if name in t: return t[name]
    raise AttributeError(f"module 'styles' has no attribute '{name}'")

# Direct attribute access helpers (so `import styles as S; S.BG` works)
@property
def BG(): return _t("BG")


def get(key, fallback=""):
    return _t(key) if key in THEMES[_current_theme] else fallback


# All theme properties — must be callable as module-level names
# We expose them as functions that read from current theme at call time
def _prop(key):
    return _t(key)

BG       = property(lambda: _t("BG"))
CARD     = property(lambda: _t("CARD"))

# ── Simple flat accessors (evaluated at import but re-called via S.refresh()) ──
# We use a mutable container trick so reassignment works after theme switch
class _Theme:
    def __getattr__(self, k): return _t(k)

import sys as _sys
_mod = _sys.modules[__name__]


class _ThemeMod(_sys.modules[__name__].__class__):
    def __getattr__(self, k):
        t = THEMES.get(_current_theme, THEMES["light"])
        if k in t: return t[k]
        raise AttributeError(k)

_sys.modules[__name__].__class__ = _ThemeMod


def _darken(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"#{max(0,r-22):02x}{max(0,g-22):02x}{max(0,b-22):02x}"


def btn(color=None, text_color="#FFFFFF", hover=None):
    if color is None: color = _t("BLUE")
    hover = hover or _darken(color)
    return f"""
        QPushButton {{
            background: {color}; color: {text_color};
            border: none; border-radius: 7px;
            padding: 7px 16px; font-size: 12px; font-weight: 600;
        }}
        QPushButton:hover   {{ background: {hover}; }}
        QPushButton:pressed {{ background: {_darken(hover)}; }}
        QPushButton:disabled{{ background: #E2E8F0; color: #94A3B8; }}
    """


def app_style():
    BG=_t("BG"); CARD=_t("CARD"); BORDER=_t("BORDER")
    TEXT=_t("TEXT"); SUBTEXT=_t("SUBTEXT"); BLUE=_t("BLUE")
    BLUE_L=_t("BLUE_L"); TOPBAR=_t("TOPBAR"); ALT=_t("ALT_ROW")
    return f"""
QWidget {{
    font-family: 'Inter','Segoe UI',Arial,sans-serif;
    font-size: 13px; color: {TEXT}; background-color: {BG};
}}
QMainWindow {{ background: {BG}; }}
QScrollArea  {{ border: none; background: transparent; }}
QScrollBar:vertical {{ width:5px; background:transparent; }}
QScrollBar::handle:vertical {{ background:#CBD5E1; border-radius:3px; min-height:28px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QTableWidget {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
    gridline-color:{BORDER}; selection-background-color:{BLUE_L};
    selection-color:{TEXT}; outline:none;
}}
QTableWidget::item {{ padding:8px 10px; border-bottom:1px solid {BORDER}; }}
QTableWidget::item:selected {{ background:{BLUE_L}; color:{TEXT}; }}
QHeaderView::section {{
    background:{BG}; color:{SUBTEXT}; font-size:11px; font-weight:600;
    letter-spacing:0.5px; padding:8px 10px; border:none;
    border-bottom:2px solid {BORDER};
}}
QHeaderView {{ background:transparent; }}
QLineEdit {{
    border:1.5px solid {BORDER}; border-radius:8px;
    padding:7px 12px; background:{CARD}; font-size:13px;
    min-height:34px; color:{TEXT};
}}
QLineEdit:focus {{ border-color:{BLUE}; }}
QComboBox {{
    border:1.5px solid {BORDER}; border-radius:8px;
    padding:6px 10px; background:{CARD}; font-size:13px;
    min-height:34px; color:{TEXT};
}}
QComboBox::drop-down {{ border:none; width:20px; }}
QComboBox QAbstractItemView {{
    border:1px solid {BORDER}; background:{CARD};
    selection-background-color:{BLUE_L};
}}
QComboBox:focus {{ border-color:{BLUE}; }}
QSpinBox, QDoubleSpinBox {{
    border:1.5px solid {BORDER}; border-radius:8px;
    padding:6px 10px; background:{CARD}; font-size:13px;
    min-height:34px; color:{TEXT};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color:{BLUE}; }}
QStatusBar {{ background:{BG}; color:{SUBTEXT}; font-size:11px; border-top:1px solid {BORDER}; }}
QDialog {{ background:{BG}; }}
QMessageBox {{ background:{BG}; }}
QToolTip {{
    background:{_t("NAVY")}; color:white;
    border:none; padding:4px 8px; border-radius:6px; font-size:11px;
}}
"""

# Backwards compat alias
CARD_STYLE = property(lambda: f"QFrame {{ background: {_t('CARD')}; border: 1px solid {_t('BORDER')}; border-radius: 10px; }}")

def card_style():
    return f"QFrame {{ background: {_t('CARD')}; border: 1px solid {_t('BORDER')}; border-radius: 10px; }}"
