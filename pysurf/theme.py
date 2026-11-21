from PySide6.QtWidgets import QWidget


DARK_STYLESHEET = """
    QMainWindow, QWidget { background: #12151d; color: #f4f6fb; }
    QDialog#settingsDialog { background: #171b25; }
    QLabel#settingsBrand {
        color: white; font-size: 24px; font-weight: 700;
        border-radius: 15px; background: qlineargradient(
            x1:0, y1:1, x2:1, y2:0,
            stop:0 #20d9d2, stop:0.55 #7559ee, stop:1 #c56bff
        );
    }
    QLabel#settingsTitle { font-size: 22px; font-weight: 700; }
    QToolBar { background: transparent; border: none; spacing: 5px; padding: 8px 12px; }
    QToolButton {
        background: rgba(32, 38, 54, 170); color: #f4f6fb;
        border: 1px solid rgba(255,255,255,24); border-radius: 10px;
        padding: 7px;
    }
    QToolButton:hover { background: rgba(113, 87, 255, 125); border-color: #9c8cff; }
    QToolButton:pressed { background: #684eff; }
    QToolButton:focus { border: 1px solid #21d8d1; }
    QLineEdit {
        background: rgba(16, 20, 32, 220); border: 1px solid #3c4357;
        border-radius: 15px; padding: 9px 14px;
        selection-background-color: #7559ee; min-height: 22px;
    }
    QLineEdit:hover { border-color: #7c70a9; }
    QLineEdit:focus { border: 1px solid #20d9d2; }
    QLineEdit[secure="true"] { border-color: #35c9a5; }
    QTabWidget::pane { border: none; background: #12151d; }
    QTabBar::tab {
        background: #1b1f2a; color: #b6bccb;
        border: 1px solid transparent; border-bottom: 2px solid transparent;
        border-top-left-radius: 10px; border-top-right-radius: 10px;
        padding: 11px 18px; margin: 4px 3px 0;
    }
    QTabBar::tab:hover { background: #282d3c; color: white; }
    QTabBar::tab:selected {
        background: #242938; color: white; border-bottom-color: #20d9d2;
    }
    QDialog { background: #171b25; color: #f4f6fb; }
    QListWidget { background: #171b25; color: #f4f6fb; border: 1px solid #32394a; }
    QListWidget::item { padding: 9px; border-radius: 7px; }
    QListWidget::item:selected { background: #363b55; }
    QPushButton {
        background: #292f41; border: 1px solid #414a60; border-radius: 9px;
        padding: 9px 14px;
    }
    QPushButton:hover { background: #3a4160; border-color: #8270ff; }
    QCheckBox { spacing: 10px; }
    QCheckBox::indicator {
        width: 18px; height: 18px; border: 1px solid #59627a; border-radius: 5px;
        background: #202636;
    }
    QCheckBox::indicator:checked { background: #7559ee; border-color: #9c8cff; }
    QSlider::groove:horizontal { height: 4px; background: #3a4154; border-radius: 2px; }
    QSlider::sub-page:horizontal { background: #20d9d2; border-radius: 2px; }
    QSlider::handle:horizontal {
        width: 16px; margin: -6px 0; border-radius: 8px; background: #a08aff;
    }
    QLabel#settingsSection { font-size: 16px; font-weight: 650; margin-top: 12px; }
    QLabel#settingsHint { color: #aeb8c9; }
    QTabWidget::tab-bar { left: 8px; }
    QStatusBar { background: #171b25; color: #aeb8c9; }
    QMenu {
        background: #202432; color: #f4f6fb;
        border: 1px solid #41485a; padding: 6px; border-radius: 10px;
    }
    QMenu::item { padding: 9px 24px; border-radius: 6px; }
    QMenu::item:selected { background: #414969; }
"""

LIGHT_STYLESHEET = """
    QMainWindow, QWidget { background: #f5f6fb; color: #202436; }
    QDialog#settingsDialog { background: #f8f9fd; }
    QLabel#settingsBrand {
        color: white; font-size: 24px; font-weight: 700;
        border-radius: 15px; background: qlineargradient(
            x1:0, y1:1, x2:1, y2:0,
            stop:0 #009eaa, stop:0.55 #7559ee, stop:1 #bd67ee
        );
    }
    QLabel#settingsTitle { font-size: 22px; font-weight: 700; }
    QToolBar { background: transparent; border: none; spacing: 5px; padding: 8px 12px; }
    QToolButton {
        background: rgba(255,255,255,205); color: #25283a;
        border: 1px solid rgba(41, 47, 70, 30); border-radius: 10px; padding: 7px;
    }
    QToolButton:hover { background: #e8e4ff; border-color: #9b8cff; }
    QToolButton:pressed { background: #d6ceff; }
    QToolButton:focus { border: 1px solid #008e9c; }
    QLineEdit {
        background: rgba(255,255,255,235); border: 1px solid #d5d9e5;
        border-radius: 15px; padding: 9px 14px; min-height: 22px;
        selection-background-color: #7559ee;
    }
    QLineEdit:hover { border-color: #a79be3; }
    QLineEdit:focus { border: 1px solid #009eaa; }
    QLineEdit[secure="true"] { border-color: #35a884; }
    QTabWidget::pane { border: none; background: #f5f6fb; }
    QTabBar::tab {
        background: #e9ebf3; color: #626a7d; border: 1px solid transparent;
        border-bottom: 2px solid transparent; border-top-left-radius: 10px;
        border-top-right-radius: 10px; padding: 11px 18px; margin: 4px 3px 0;
    }
    QTabBar::tab:hover { background: #e1def2; color: #25283a; }
    QTabBar::tab:selected {
        background: #ffffff; color: #22263a; border-bottom-color: #009eaa;
    }
    QDialog { background: #f8f9fd; color: #202436; }
    QListWidget { background: white; color: #202436; border: 1px solid #dfe2eb; }
    QListWidget::item { padding: 9px; border-radius: 7px; }
    QListWidget::item:selected { background: #e8e4ff; }
    QPushButton {
        background: #ffffff; border: 1px solid #d7dbe6; border-radius: 9px;
        padding: 9px 14px;
    }
    QPushButton:hover { background: #ece9ff; border-color: #a294f5; }
    QCheckBox { spacing: 10px; }
    QCheckBox::indicator {
        width: 18px; height: 18px; border: 1px solid #b9bfce; border-radius: 5px;
        background: #ffffff;
    }
    QCheckBox::indicator:checked { background: #7559ee; border-color: #7559ee; }
    QSlider::groove:horizontal { height: 4px; background: #d7dbe6; border-radius: 2px; }
    QSlider::sub-page:horizontal { background: #009eaa; border-radius: 2px; }
    QSlider::handle:horizontal {
        width: 16px; margin: -6px 0; border-radius: 8px; background: #7559ee;
    }
    QLabel#settingsSection { font-size: 16px; font-weight: 650; margin-top: 12px; }
    QLabel#settingsHint { color: #626a7d; }
    QTabWidget::tab-bar { left: 8px; }
    QStatusBar { background: #eceef5; color: #626a7d; }
    QMenu {
        background: #ffffff; color: #202436;
        border: 1px solid #d7dbe6; padding: 6px; border-radius: 10px;
    }
    QMenu::item { padding: 9px 24px; border-radius: 6px; }
    QMenu::item:selected { background: #eeebff; }
"""


def apply_theme(window: QWidget, dark: bool) -> None:
    window.setStyleSheet(DARK_STYLESHEET if dark else LIGHT_STYLESHEET)
    if hasattr(window, "toolbar"):
        window.toolbar.set_dark_mode(dark)
