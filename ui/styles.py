"""
Design system for the Beam Analysis Solver desktop application.

This module centralizes the visual language of the application: a single
source of truth for color, typography and the compiled Qt stylesheet (QSS).
Nothing engineering-related lives here -- this is presentation only.

Palette philosophy
-------------------
Dark graphite/slate chrome (inspired by professional CAE tools such as
Fusion 360 / ANSYS Mechanical) with a restrained steel-blue accent, a
teal/cyan secondary highlight, and muted status colors. The plotting
canvas itself is left on its natural light background (see plotting.py,
which is intentionally untouched) so the engineering diagrams remain the
sharpest, most readable element in the window -- exactly like a CAD
viewport sitting inside a dark application frame.
"""

# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #
PALETTE = {
    # Chrome / surfaces
    "bg_app": "#1B1F24",
    "bg_panel": "#20252B",
    "bg_elevated": "#262C33",
    "bg_input": "#1B1F24",
    "bg_input_hover": "#232922",
    "bg_hover": "#2C333B",
    "bg_pressed": "#141810",

    # Borders
    "border": "#333B44",
    "border_strong": "#454F5A",
    "border_focus": "#4FA3D1",

    # Typography
    "text_primary": "#E8ECEF",
    "text_secondary": "#98A4AE",
    "text_tertiary": "#69747E",
    "text_on_accent": "#0D1117",

    # Accent
    "accent": "#4FA3D1",
    "accent_hover": "#6BB8E0",
    "accent_pressed": "#3D87B3",
    "accent_muted": "#2A3B44",

    "accent2": "#4FD1C5",   # secondary teal highlight (selection / links)

    # Status
    "success": "#4CAF7D",
    "success_bg": "#1E2B23",
    "warning": "#D9A441",
    "warning_bg": "#2C2618",
    "error": "#D9635C",
    "error_bg": "#2E1E1C",

    # Load-type identity colors (mirrors plotting.py conventions loosely)
    "point_load": "#D9635C",
    "moment": "#B084CC",
    "udl": "#D99A41",
    "uvl": "#4FD1C5",
}

FONT_FAMILY = '"Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif'
MONO_FAMILY = '"Cascadia Mono", "Consolas", "JetBrains Mono", "Courier New", monospace'

BASE_PT = 9


def build_stylesheet() -> str:
    p = PALETTE
    return f"""
    /* ---------- Base ---------- */
    QWidget {{
        background-color: {p['bg_app']};
        color: {p['text_primary']};
        font-family: {FONT_FAMILY};
        font-size: {BASE_PT}pt;
    }}

    QMainWindow {{
        background-color: {p['bg_app']};
    }}

    QToolTip {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border: 1px solid {p['border_strong']};
        padding: 5px 8px;
        border-radius: 3px;
        font-size: {BASE_PT - 1}pt;
    }}

    /* ---------- Header ---------- */
    QFrame#appHeader {{
        background-color: {p['bg_panel']};
        border-bottom: 1px solid {p['border']};
    }}
    QLabel#appTitle {{
        color: {p['text_primary']};
        font-size: 13pt;
        font-weight: 600;
    }}
    QLabel#appSubtitle {{
        color: {p['text_tertiary']};
        font-size: {BASE_PT - 1}pt;
    }}
    QLabel#appVersion {{
        color: {p['text_tertiary']};
        font-size: {BASE_PT - 1}pt;
    }}

    /* ---------- Toolbar ---------- */
    QToolBar#mainToolBar {{
        background-color: {p['bg_panel']};
        border: none;
        border-bottom: 1px solid {p['border']};
        padding: 4px 8px;
        spacing: 2px;
    }}
    QToolBar#mainToolBar QToolButton {{
        background-color: transparent;
        color: {p['text_secondary']};
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: {BASE_PT}pt;
    }}
    QToolBar#mainToolBar QToolButton:hover {{
        background-color: {p['bg_hover']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
    }}
    QToolBar#mainToolBar QToolButton:pressed {{
        background-color: {p['bg_pressed']};
    }}
    QToolBar#mainToolBar QToolButton#runAction {{
        background-color: {p['accent_muted']};
        color: {p['accent']};
        font-weight: 600;
        border: 1px solid {p['accent']};
    }}
    QToolBar#mainToolBar QToolButton#runAction:hover {{
        background-color: {p['accent']};
        color: {p['text_on_accent']};
    }}
    QToolBar::separator {{
        background-color: {p['border']};
        width: 1px;
        margin: 6px 6px;
    }}

    /* ---------- Status Bar ---------- */
    QStatusBar {{
        background-color: {p['bg_panel']};
        color: {p['text_secondary']};
        border-top: 1px solid {p['border']};
        font-size: {BASE_PT - 1}pt;
    }}
    QStatusBar::item {{ border: none; }}
    QLabel#statusUnits {{
        color: {p['text_tertiary']};
        padding: 0 6px;
    }}

    /* ---------- Scroll area / panel surfaces ---------- */
    QScrollArea {{
        background-color: {p['bg_app']};
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background-color: {p['bg_app']};
    }}

    QFrame#card {{
        background-color: {p['bg_panel']};
        border: 1px solid {p['border']};
        border-radius: 5px;
    }}

    QSplitter::handle {{
        background-color: {p['bg_app']};
    }}
    QSplitter::handle:horizontal {{ width: 6px; }}
    QSplitter::handle:vertical {{ height: 6px; }}
    QSplitter::handle:hover {{ background-color: {p['border_strong']}; }}

    /* ---------- Section labels ---------- */
    QLabel[role="section"] {{
        color: {p['text_secondary']};
        font-size: {BASE_PT - 1}pt;
        font-weight: 600;
        padding-top: 2px;
    }}
    QLabel[role="fieldLabel"] {{
        color: {p['text_secondary']};
        font-size: {BASE_PT - 1}pt;
    }}
    QLabel[role="hint"] {{
        color: {p['text_tertiary']};
        font-size: {BASE_PT - 2}pt;
    }}

    /* ---------- Beam-type segmented control ---------- */
    QFrame#segmentedControl {{
        background-color: {p['bg_input']};
        border: 1px solid {p['border']};
        border-radius: 5px;
    }}
    QRadioButton#segmentOption {{
        color: {p['text_secondary']};
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 7px 10px;
        font-size: {BASE_PT}pt;
        font-weight: 500;
    }}
    QRadioButton#segmentOption::indicator {{
        width: 0px;
        height: 0px;
    }}
    QRadioButton#segmentOption:hover {{
        color: {p['text_primary']};
    }}
    QRadioButton#segmentOption:checked {{
        background-color: {p['accent_muted']};
        color: {p['accent']};
        font-weight: 600;
    }}

    /* ---------- Inputs ---------- */
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {{
        background-color: {p['bg_input']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
        border-radius: 3px;
        padding: 4px 6px;
        min-height: 20px;
        selection-background-color: {p['accent_muted']};
    }}
    QLineEdit:hover, QDoubleSpinBox:hover, QSpinBox:hover, QComboBox:hover {{
        border: 1px solid {p['border_strong']};
    }}
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {p['border_focus']};
    }}
    QLineEdit:disabled, QDoubleSpinBox:disabled {{
        color: {p['text_tertiary']};
        background-color: {p['bg_panel']};
    }}
    QDoubleSpinBox, QSpinBox {{
        font-family: {MONO_FAMILY};
    }}
    QDoubleSpinBox::up-button, QSpinBox::up-button,
    QDoubleSpinBox::down-button, QSpinBox::down-button {{
        width: 14px;
        background-color: transparent;
        border: none;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border: 1px solid {p['border_strong']};
        selection-background-color: {p['accent_muted']};
        outline: none;
    }}

    /* ---------- Buttons ---------- */
    QPushButton {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border: 1px solid {p['border_strong']};
        border-radius: 4px;
        padding: 6px 14px;
        font-size: {BASE_PT}pt;
    }}
    QPushButton:hover {{
        background-color: {p['bg_hover']};
        border: 1px solid {p['border_strong']};
    }}
    QPushButton:pressed {{
        background-color: {p['bg_pressed']};
    }}
    QPushButton:disabled {{
        color: {p['text_tertiary']};
        border: 1px solid {p['border']};
    }}
    QPushButton#primaryButton {{
        background-color: {p['accent']};
        color: {p['text_on_accent']};
        border: 1px solid {p['accent']};
        font-weight: 600;
        padding: 9px 14px;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {p['accent_hover']};
        border: 1px solid {p['accent_hover']};
    }}
    QPushButton#primaryButton:pressed {{
        background-color: {p['accent_pressed']};
    }}
    QPushButton#ghostButton {{
        background-color: transparent;
        border: 1px solid {p['border']};
        color: {p['text_secondary']};
    }}
    QPushButton#ghostButton:hover {{
        color: {p['text_primary']};
        border: 1px solid {p['border_strong']};
    }}
    QPushButton#addRowButton {{
        background-color: transparent;
        border: 1px dashed {p['border_strong']};
        color: {p['text_secondary']};
        padding: 5px 10px;
        font-size: {BASE_PT - 1}pt;
    }}
    QPushButton#addRowButton:hover {{
        color: {p['accent']};
        border: 1px dashed {p['accent']};
        background-color: {p['accent_muted']};
    }}

    QToolButton#removeRowButton {{
        background-color: transparent;
        border: none;
        color: {p['text_tertiary']};
        border-radius: 3px;
    }}
    QToolButton#removeRowButton:hover {{
        color: {p['error']};
        background-color: {p['error_bg']};
    }}

    /* ---------- Tables (load editors) ---------- */
    QTableWidget {{
        background-color: {p['bg_input']};
        alternate-background-color: {p['bg_panel']};
        gridline-color: {p['border']};
        border: 1px solid {p['border']};
        border-radius: 3px;
        selection-background-color: {p['accent_muted']};
        selection-color: {p['text_primary']};
    }}
    QTableWidget::item {{
        padding: 2px;
        border: none;
    }}
    QHeaderView::section {{
        background-color: {p['bg_panel']};
        color: {p['text_tertiary']};
        border: none;
        border-bottom: 1px solid {p['border']};
        border-right: 1px solid {p['border']};
        padding: 5px 6px;
        font-size: {BASE_PT - 2}pt;
        font-weight: 600;
    }}
    QTableCornerButton::section {{
        background-color: {p['bg_panel']};
        border: none;
    }}

    /* ---------- Results panel (QTextEdit acting as a property panel) ---------- */
    QTextEdit#resultsPanel {{
        background-color: {p['bg_panel']};
        color: {p['text_primary']};
        border: none;
        font-family: {MONO_FAMILY};
        font-size: {BASE_PT}pt;
        padding: 8px;
    }}

    /* ---------- Plot viewport ---------- */
    QFrame#viewportHeader {{
        background-color: {p['bg_panel']};
        border-bottom: 1px solid {p['border']};
    }}
    QLabel#viewportTitle {{
        color: {p['text_secondary']};
        font-size: {BASE_PT - 1}pt;
        font-weight: 600;
    }}
    QWidget#plotCanvasHost {{
        background-color: #FFFFFF;
    }}
    QToolBar#plotToolBar {{
        background-color: {p['bg_panel']};
        border: none;
        padding: 2px 6px;
        spacing: 0px;
    }}
    QToolBar#plotToolBar QToolButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 3px;
        margin: 1px;
    }}
    QToolBar#plotToolBar QToolButton:hover {{
        background-color: {p['bg_hover']};
        border: 1px solid {p['border']};
    }}

    /* ---------- Scrollbars ---------- */
    QScrollBar:vertical {{
        background: transparent;
        width: 11px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {p['border_strong']};
        min-height: 24px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {p['text_tertiary']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 11px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {p['border_strong']};
        min-width: 24px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

    /* ---------- Dialogs ---------- */
    QDialog {{
        background-color: {p['bg_app']};
    }}
    QListWidget {{
        background-color: {p['bg_input']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        outline: none;
    }}
    QListWidget::item {{
        border-bottom: 1px solid {p['border']};
        padding: 8px;
    }}
    QListWidget::item:selected {{
        background-color: {p['accent_muted']};
        color: {p['text_primary']};
    }}

    QMessageBox {{
        background-color: {p['bg_panel']};
    }}
    """
