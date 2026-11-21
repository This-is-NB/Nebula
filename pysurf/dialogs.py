from importlib import metadata

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .config import APP_ICON, APP_VERSION, HOME_PAGE


class ListDialog(QDialog):
    def __init__(self, title, rows, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setWindowTitle(title)
        self.resize(760, 520)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)
        for row in rows:
            url = row[0]
            label = row[1] or url
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, url)
            item.setToolTip(url)
            self.list.addItem(item)
        buttons = QHBoxLayout()
        open_button = QPushButton("Open")
        open_button.clicked.connect(self.open_selected)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.addWidget(open_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
        self.list.itemDoubleClicked.connect(lambda _item: self.open_selected())

    def open_selected(self):
        item = self.list.currentItem()
        if item:
            self.browser.navigate_text(item.data(Qt.ItemDataRole.UserRole))
            self.close()


class FindBar(QWidget):
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        self.field = QLineEdit()
        self.field.setPlaceholderText("Find in page")
        self.field.textChanged.connect(self.find)
        self.field.returnPressed.connect(self.find_next)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(self.field)
        layout.addWidget(close_button)
        self.setMaximumHeight(44)

    def find(self):
        view = self.browser.current_view()
        if view:
            view.findText(self.field.text())

    def find_next(self):
        view = self.browser.current_view()
        if view:
            view.findText(self.field.text())

    def showEvent(self, event):
        super().showEvent(event)
        self.field.setFocus()
        self.field.selectAll()

    def closeEvent(self, event):
        view = self.browser.current_view()
        if view:
            view.findText("")
        super().closeEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setObjectName("settingsDialog")
        self.setWindowTitle("Nebula Settings")
        self.resize(820, 600)
        self.setMinimumSize(720, 520)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(14)
        brand = QLabel("N")
        brand.setObjectName("settingsBrand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFixedSize(48, 48)
        if APP_ICON.exists():
            brand.setPixmap(
                QPixmap(str(APP_ICON)).scaled(
                    48,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            brand.setText("N")
        header.addWidget(brand)
        heading = QVBoxLayout()
        title = QLabel("Nebula settings")
        title.setObjectName("settingsTitle")
        subtitle = QLabel("Personalize your browsing experience")
        subtitle.setObjectName("settingsHint")
        heading.addWidget(title)
        heading.addWidget(subtitle)
        header.addLayout(heading)
        header.addStretch()
        layout.addLayout(header)

        self.pages = QTabWidget()
        self.pages.setTabPosition(QTabWidget.TabPosition.West)
        self.pages.setDocumentMode(True)
        self.pages.addTab(self._general_page(), "General")
        self.pages.addTab(self._privacy_page(), "Privacy")
        self.pages.addTab(self._appearance_page(), "Appearance")
        self.pages.addTab(self._updates_page(), "Updates")
        layout.addWidget(self.pages, 1)

        footer = QHBoxLayout()
        footer.addStretch()
        close_button = QPushButton("Done")
        close_button.clicked.connect(self.close)
        footer.addWidget(close_button)
        layout.addLayout(footer)

    def _general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()
        home_page = self.browser.settings.get("home")
        self.home = QLineEdit(
            "Nebula Start Page" if home_page == HOME_PAGE else home_page
        )
        self.home.setClearButtonEnabled(True)
        self.home.setPlaceholderText("https://example.com")
        self.home.editingFinished.connect(self.save_home)
        form.addRow("Home page", self.home)
        layout.addLayout(form)
        home_hint = QLabel("Choose the page Nebula opens for Home and new tabs.")
        home_hint.setWordWrap(True)
        home_hint.setObjectName("settingsHint")
        layout.addWidget(home_hint)

        self.restore = QCheckBox("Restore my tabs when Nebula starts")
        self.restore.setChecked(self.browser.settings.get("restore_session", True))
        self.restore.toggled.connect(
            lambda value: self.browser.settings.set("restore_session", value)
        )
        layout.addWidget(self.restore)

        zoom_heading = QLabel("Page zoom")
        zoom_heading.setObjectName("settingsSection")
        layout.addWidget(zoom_heading)
        zoom_row = QHBoxLayout()
        self.zoom_value = QLabel(f"{round(self.browser.zoom * 100)}%")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 500)
        self.zoom_slider.setSingleStep(10)
        self.zoom_slider.setValue(round(self.browser.zoom * 100))
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        zoom_row.addWidget(self.zoom_slider, 1)
        zoom_row.addWidget(self.zoom_value)
        layout.addLayout(zoom_row)
        layout.addStretch()
        return page

    def _privacy_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.trackers = QCheckBox("Block known third-party trackers")
        self.trackers.setChecked(self.browser.settings.get("block_trackers", True))
        self.trackers.toggled.connect(
            lambda value: self.browser.settings.set("block_trackers", value)
        )
        layout.addWidget(self.trackers)
        explanation = QLabel(
            "Nebula blocks a small built-in list of tracking hosts. This is not "
            "comprehensive tracker protection and does not hide your IP address."
        )
        explanation.setWordWrap(True)
        explanation.setObjectName("settingsHint")
        layout.addWidget(explanation)

        data_heading = QLabel("Browsing data")
        data_heading.setObjectName("settingsSection")
        layout.addWidget(data_heading)
        clear_button = QPushButton("Clear history, cache, and cookies")
        clear_button.clicked.connect(self.clear_browsing_data)
        layout.addWidget(clear_button)
        layout.addStretch()
        return page

    def _appearance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.dark = QCheckBox("Use the dark interface")
        self.dark.setChecked(self.browser.settings.get("dark_mode", False))
        self.dark.toggled.connect(self.browser.apply_theme)
        layout.addWidget(self.dark)

        self.motion = QCheckBox("Enable animated energy effects")
        self.motion.setChecked(self.browser.settings.get("animations", True))
        self.motion.toggled.connect(self.browser.set_animations_enabled)
        layout.addWidget(self.motion)
        explanation = QLabel(
            "Subtle motion accents appear on the toolbar, tabs, and Nebula start "
            "page. Turn them off here whenever you prefer a still interface."
        )
        explanation.setWordWrap(True)
        explanation.setObjectName("settingsHint")
        layout.addWidget(explanation)
        layout.addStretch()
        return page

    def _updates_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        update_heading = QLabel("Keep Chromium up to date")
        update_heading.setObjectName("settingsSection")
        layout.addWidget(update_heading)
        try:
            webengine_version = metadata.version("PySide6-WebEngine")
        except metadata.PackageNotFoundError:
            webengine_version = "unknown"
        version = QLabel(
            f"Nebula {APP_VERSION}  ·  Qt WebEngine {webengine_version}"
        )
        version.setObjectName("settingsHint")
        layout.addWidget(version)
        update_button = QPushButton("Check for Chromium / Qt updates")
        update_button.clicked.connect(self.browser.check_for_updates)
        layout.addWidget(update_button)
        layout.addStretch()
        return page

    def save_home(self):
        value = self.home.text().strip()
        if value:
            self.browser.settings.set(
                "home",
                HOME_PAGE if value == "Nebula Start Page" else value,
            )

    def change_zoom(self, value):
        self.zoom_value.setText(f"{value}%")
        self.browser.set_zoom_percent(value)

    def clear_browsing_data(self):
        answer = QMessageBox.question(
            self,
            "Clear browsing data",
            "This deletes browsing history, cached files, and cookies. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.browser.store.clear_history()
        self.browser.normal_profile.clearHttpCache()
        self.browser.normal_profile.cookieStore().deleteAllCookies()
        QMessageBox.information(self, "Privacy", "Browsing data cleared.")
