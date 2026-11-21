import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QSize, Qt, QUrl
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWebEngineCore import (
    QWebEngineDownloadRequest,
    QWebEnginePage,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
    QLineEdit,
    QTabBar,
    QSizePolicy,
    QTabWidget,
    QToolButton,
    QWidget,
    QVBoxLayout,
)
from .chrome import MotionTabBar, MotionToolButton, MotionToolbar
from .config import (
    APP_DIR,
    APP_NAME,
    HOME_PAGE,
    HOME_PAGE_FILE,
    SEARCH_URL,
    get_app_icon_path,
)
from .dialogs import FindBar, ListDialog, SettingsDialog
from .icons import icon
from .navigation import resolve_address
from .privacy import create_profile
from .theme import apply_theme
from .updater import EngineUpdater


class BrowserWindow(QMainWindow):
    def __init__(self, settings, store, data_dir, private=False, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.store = store
        self.data_dir = Path(data_dir)
        self.is_private = private
        self.setWindowTitle(f"{APP_NAME} - Private Window" if private else APP_NAME)
        self.resize(1280, 800)

        icon_path = get_app_icon_path()
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.profile = create_profile(settings, self, private=private)
        if not private:
            self.profile.setPersistentStoragePath(str(self.data_dir / "web-storage"))
            self.profile.setCachePath(str(self.data_dir / "cache"))
            self.profile.setDownloadPath(settings.get("download_path"))
        self.profile.downloadRequested.connect(self.download_requested)

        self.downloads = []
        self.closed_tabs = []
        self.private_windows = []
        self.updater = None
        self.zoom = 1.0 if private else settings.get("zoom", 1.0)
        self.toolbar_icon_buttons = {}
        self.menu_icon_actions = []

        self.tabs = QTabWidget()
        self.tabs.setTabBar(MotionTabBar(self.tabs))
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.tabBarDoubleClicked.connect(
            lambda index: self.add_tab() if index == -1 else None
        )
        self.tabs.setStyleSheet("""
            QTabBar::tab { min-width: 160px; padding: 9px 10px; }
        """)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self.show_tab_menu)

        self.toolbar = MotionToolbar("Navigation", self)
        self.toolbar.set_motion_enabled(settings.get("animations", True))
        self.toolbar.set_dark_mode(settings.get("dark_mode", False))
        self.tabs.tabBar().set_motion_enabled(settings.get("animations", True))
        self.tabs.tabBar().set_dark_mode(settings.get("dark_mode", False))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.back_action, _ = self._add_toolbar_button(
            "back", "Back", self.go_back
        )
        self.forward_action, _ = self._add_toolbar_button(
            "forward", "Forward", self.go_forward
        )
        self.reload_action, _ = self._add_toolbar_button(
            "reload", "Reload or stop", self.reload_or_stop
        )
        self.address_bar = QLineEdit()
        self.address_bar.setClearButtonEnabled(True)
        self.address_bar.setPlaceholderText("Search or enter address")
        self.address_bar.setMinimumWidth(320)
        self.address_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.address_bar.returnPressed.connect(self.navigate_address)
        self.security_action = self.address_bar.addAction(
            icon("lock", self._icon_color()),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.security_action.setToolTip("Connection security")
        self.toolbar.addWidget(self.address_bar)

        if not private:
            self.bookmark_action, _ = self._add_toolbar_button(
                "bookmark", "Bookmark this page", self.toggle_bookmark
            )
        self._create_menu_button()

        self.new_tab_button = MotionToolButton(self.tabs)
        self.new_tab_button.set_motion_enabled(settings.get("animations", True))
        self.new_tab_button.setIcon(icon("plus", self._icon_color()))
        self.new_tab_button.setToolTip("New tab (Ctrl+T)")
        self.new_tab_button.setAccessibleName("New tab")
        self.new_tab_button.clicked.connect(lambda: self.add_tab())
        self.tabs.setCornerWidget(
            self.new_tab_button,
            Qt.Corner.TopRightCorner,
        )
        self._setup_shortcuts()

        self.find_bar = FindBar(self)
        self.find_bar.hide()
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.find_bar)
        shell_layout.addWidget(self.tabs)
        self.setCentralWidget(shell)
        self.statusBar()

        if not private and settings.get("restore_session", True):
            urls, active_index = store.session()
        else:
            urls, active_index = [], 0

        if urls and not private:
            for url in urls:
                self.add_tab(QUrl(url))
            if active_index < self.tabs.count():
                self.tabs.setCurrentIndex(active_index)
        else:
            self.add_tab()

        if settings.get("dark_mode", False):
            self.apply_theme(True, persist=False)
        else:
            self.apply_theme(False, persist=False)

    def _icon_color(self):
        return "#f4f6ff" if self.settings.get("dark_mode", False) else "#29334a"

    def _add_toolbar_button(self, name, label, callback):
        action = QAction(icon(name, self._icon_color()), label, self)
        action.setToolTip(label)
        action.setStatusTip(label)
        action.triggered.connect(lambda _checked=False: callback())
        button = MotionToolButton(self.toolbar)
        button.setDefaultAction(action)
        button.set_motion_enabled(self.settings.get("animations", True))
        button.setAccessibleName(label)
        button.setToolTip(label)
        self.toolbar.addWidget(button)
        self.toolbar_icon_buttons[name] = (action, button)
        return action, button

    def _add_menu_action(self, menu, name, label, callback):
        action = QAction(icon(name, self._icon_color()), label, menu)
        action.triggered.connect(lambda _checked=False: callback())
        menu.addAction(action)
        self.menu_icon_actions.append((name, action))
        return action

    def _create_menu_button(self):
        self.menu_button = MotionToolButton(self.toolbar)
        self.menu_button.set_motion_enabled(self.settings.get("animations", True))
        self.menu_button.setIcon(icon("menu", self._icon_color()))
        self.menu_button.setToolTip("Browser menu")
        self.menu_button.setAccessibleName("Browser menu")
        self.menu = QMenu(self.menu_button)
        self._add_menu_action(self.menu, "home", "Home", self.go_home)
        self._add_menu_action(self.menu, "find", "Find in page", self.show_find)

        zoom_menu = self.menu.addMenu("Zoom")
        self._add_menu_action(zoom_menu, "zoom_out", "Zoom out", lambda: self.change_zoom(-0.1))
        self._add_menu_action(zoom_menu, "zoom_in", "Zoom in", lambda: self.change_zoom(0.1))
        self._add_menu_action(zoom_menu, "reload", "Reset zoom", lambda: self.set_zoom_percent(100))
        self.menu.addSeparator()

        if not self.is_private:
            self._add_menu_action(self.menu, "history", "History", self.show_history)
            self._add_menu_action(self.menu, "bookmark", "Bookmarks", self.show_bookmarks)
            self._add_menu_action(self.menu, "download", "Downloads", self.show_downloads)
            self._add_menu_action(
                self.menu,
                "restore",
                "Restore closed tab",
                self.restore_closed_tab,
            )
            self.menu.addSeparator()
            self._add_menu_action(
                self.menu,
                "private",
                "New private window",
                self.open_private_window,
            )

        self.theme_menu_action = QAction("Dark interface", self.menu)
        self.theme_menu_action.setCheckable(True)
        self.theme_menu_action.setChecked(self.settings.get("dark_mode", False))
        self.theme_menu_action.triggered.connect(self.toggle_theme)
        self.menu.addAction(self.theme_menu_action)
        if not self.is_private:
            self._add_menu_action(self.menu, "settings", "Settings", self.show_settings)
        self.menu_button.setMenu(self.menu)
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toolbar.addWidget(self.menu_button)

    def _setup_shortcuts(self):
        self._bind_shortcut("Ctrl+L", self.focus_address)
        self._bind_shortcut("Ctrl+T", lambda: self.add_tab())
        self._bind_shortcut("Ctrl+W", lambda: self.close_tab(self.tabs.currentIndex()))
        self._bind_shortcut("Ctrl+F", self.show_find)
        self._bind_shortcut("Alt+Left", self.go_back)
        self._bind_shortcut("Alt+Right", self.go_forward)
        self._bind_shortcut("Ctrl+R", self.reload)
        if not self.is_private:
            self._bind_shortcut("Ctrl+H", self.show_history)
            self._bind_shortcut("Ctrl+D", self.toggle_bookmark)
            self._bind_shortcut("Ctrl+Shift+P", self.open_private_window)

    def _bind_shortcut(self, sequence, callback):
        action = QAction(self)
        action.setShortcut(QKeySequence(sequence))
        action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        action.triggered.connect(lambda _checked=False: callback())
        self.addAction(action)

    def focus_address(self):
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def toggle_theme(self):
        self.apply_theme(not self.settings.get("dark_mode", False))

    def set_animations_enabled(self, enabled, persist=True):
        self.toolbar.set_motion_enabled(enabled)
        self.tabs.tabBar().set_motion_enabled(enabled)
        motion_off = "false" if enabled else "true"
        for index in range(self.tabs.count()):
            view = self.tabs.widget(index)
            if (
                isinstance(view, QWebEngineView)
                and view.url().toLocalFile() == QUrl(HOME_PAGE_FILE).toLocalFile()
            ):
                view.page().runJavaScript(
                    "document.documentElement.classList.toggle("
                    f"'nebula-motion-off', {motion_off});"
                )
        if hasattr(self, "new_tab_button"):
            self.new_tab_button.set_motion_enabled(enabled)
        if persist and not self.is_private:
            self.settings.set("animations", enabled)

    def set_zoom_percent(self, percent):
        self.zoom = max(0.25, min(5.0, percent / 100))
        if not self.is_private:
            self.settings.set("zoom", self.zoom)
        view = self.current_view()
        if view:
            view.setZoomFactor(self.zoom)

    def _update_toolbar_icons(self):
        color = self._icon_color()
        for name, (action, button) in self.toolbar_icon_buttons.items():
            action.setIcon(icon(name, color))
            button.setIcon(icon(name, color))
        for name, action in self.menu_icon_actions:
            action.setIcon(icon(name, color))
        if hasattr(self, "tabs"):
            for index in range(self.tabs.count()):
                close_button = self.tabs.tabBar().tabButton(
                    index,
                    QTabBar.ButtonPosition.RightSide,
                )
                if isinstance(close_button, QToolButton):
                    close_button.setIcon(icon("close", color))
        if hasattr(self, "menu_button"):
            self.menu_button.setIcon(icon("menu", color))
        if hasattr(self, "new_tab_button"):
            self.new_tab_button.setIcon(icon("plus", color))
        if hasattr(self, "security_action"):
            self._update_security_icon(self.address_bar.text())

    def _update_security_icon(self, address):
        qurl = QUrl(address)
        scheme = qurl.scheme().lower()
        if not address:
            name, tooltip = "find", "Search or enter an address"
        elif scheme == "https":
            name, tooltip = "lock", "Secure HTTPS connection"
        elif scheme == "http":
            name, tooltip = "warning", "Not secure: this page uses HTTP"
        else:
            name, tooltip = "lock", "Connection information"
        self.security_action.setIcon(icon(name, self._icon_color()))
        self.security_action.setToolTip(tooltip)

    def current_view(self):
        view = self.tabs.currentWidget()
        return view if isinstance(view, QWebEngineView) else None

    def add_tab(self, url=None, title="New tab"):
        if url is None:
            url = self._home_url()
        elif isinstance(url, str):
            url = QUrl(url)
        if url.toString() == HOME_PAGE:
            url = QUrl(HOME_PAGE_FILE)
        if url.toLocalFile() == QUrl(HOME_PAGE_FILE).toLocalFile():
            url.setQuery(
                "motion=on" if self.settings.get("animations", True) else "motion=off"
            )

        view = QWebEngineView()
        page = QWebEnginePage(self.profile, view)
        view.setPage(page)
        view.setUrl(url)
        view.setZoomFactor(self.zoom)
        index = self.tabs.addTab(view, title)
        self._add_tab_close_button(index, view)
        self.tabs.setCurrentIndex(index)

        view.urlChanged.connect(lambda qurl, v=view: self.view_url_changed(v, qurl))
        view.titleChanged.connect(lambda text, v=view: self.view_title_changed(v, text))
        view.loadStarted.connect(lambda v=view: self.view_load_started(v))
        view.loadFinished.connect(lambda ok, v=view: self.view_load_finished(v, ok))
        view.iconChanged.connect(lambda icon, v=view: self.view_icon_changed(v, icon))
        view.loadProgress.connect(
            lambda progress, v=view: self.view_progress(v, progress)
        )
        page.permissionRequested.connect(self.permission_requested)
        page.certificateError.connect(self.certificate_error)
        return view

    def _add_tab_close_button(self, index, view):
        button = QToolButton(self.tabs.tabBar())
        button.setObjectName("tabCloseButton")
        button.setIcon(icon("close", self._icon_color()))
        button.setIconSize(QSize(13, 13))
        button.setFixedSize(28, 26)
        button.setAutoRaise(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip("Close tab")
        button.setAccessibleName("Close tab")
        button.setStyleSheet("""
            QToolButton#tabCloseButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 0;
            }
            QToolButton#tabCloseButton:hover {
                background: rgba(232, 82, 116, 35);
                border: 1px solid rgba(232, 82, 116, 110);
            }
        """)
        button.clicked.connect(
            lambda _checked=False, tab=view: self.close_tab(self.tabs.indexOf(tab))
        )
        self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, button)

    def _home_url(self):
        home = self.settings.get("home", HOME_PAGE)
        url = QUrl(HOME_PAGE_FILE if home == HOME_PAGE else home)
        if url.toLocalFile() == QUrl(HOME_PAGE_FILE).toLocalFile():
            url.setQuery(
                "motion=on" if self.settings.get("animations", True) else "motion=off"
            )
        return url

    def close_tab(self, index):
        if self.tabs.count() == 1:
            self.add_tab()
        view = self.tabs.widget(index)
        if isinstance(view, QWebEngineView):
            url = view.url().toString()
            if url:
                self.closed_tabs.append(url)
        self.tabs.removeTab(index)
        if view:
            view.deleteLater()
        self.save_session()

    def restore_closed_tab(self):
        if not self.closed_tabs:
            self.statusBar().showMessage("No recently closed tabs", 3000)
            return
        self.add_tab(QUrl(self.closed_tabs.pop()))

    def show_tab_menu(self, position):
        index = self.tabs.tabBar().tabAt(position)
        if index < 0:
            return
        menu = QMenu(self)
        menu.addAction("Duplicate", lambda: self.duplicate_tab(index))
        menu.addAction("Close", lambda: self.close_tab(index))
        menu.addAction("Restore last closed", self.restore_closed_tab)
        menu.exec(self.tabs.tabBar().mapToGlobal(position))

    def duplicate_tab(self, index):
        view = self.tabs.widget(index)
        if isinstance(view, QWebEngineView):
            self.add_tab(view.url())

    def current_tab_changed(self, index):
        view = self.tabs.widget(index)
        if isinstance(view, QWebEngineView):
            self.update_address(view.url())
            self.back_action.setEnabled(view.history().canGoBack())
            self.forward_action.setEnabled(view.history().canGoForward())
            self._set_loading_icon(view.page().isLoading())

    def view_url_changed(self, view, qurl):
        index = self.tabs.indexOf(view)
        if index >= 0:
            title = qurl.host() if qurl.scheme() in ("http", "https") else ""
            self.tabs.setTabText(index, title or qurl.toDisplayString()[:40] or "New tab")
            if view == self.current_view():
                self.update_address(qurl)
            self.save_session()

    def view_title_changed(self, view, title):
        index = self.tabs.indexOf(view)
        if index >= 0 and title:
            self.tabs.setTabText(index, title[:32])

    def view_load_started(self, view):
        if view == self.current_view():
            self._set_loading_icon(True)
            self.statusBar().showMessage("Loading...")

    def view_load_finished(self, view, success):
        qurl = view.url()
        if success and not self.is_private and qurl.scheme() in ("http", "https"):
            self.store.add_history(qurl.toString(), view.title())
        if view == self.current_view():
            self._set_loading_icon(False)
            self.statusBar().showMessage(
                "Page loaded" if success else "Page could not be loaded",
                4000,
            )
            self.back_action.setEnabled(view.history().canGoBack())
            self.forward_action.setEnabled(view.history().canGoForward())

    def view_icon_changed(self, view, icon):
        index = self.tabs.indexOf(view)
        if index >= 0 and not icon.isNull():
            self.tabs.setTabIcon(index, icon)

    def view_progress(self, view, progress):
        if view == self.current_view():
            self.statusBar().showMessage(f"Loading {progress}%")

    def update_address(self, qurl):
        text = qurl.toString()
        if qurl.toLocalFile() == QUrl(HOME_PAGE_FILE).toLocalFile():
            text = ""
        elif text.startswith(("chrome://", "about:", "data:", "qrc:")):
            text = ""
        self.address_bar.setText(text)
        self.address_bar.setProperty("secure", qurl.scheme() == "https")
        self.address_bar.style().unpolish(self.address_bar)
        self.address_bar.style().polish(self.address_bar)
        self._update_security_icon(text)

    def _set_loading_icon(self, loading):
        name = "stop" if loading else "reload"
        self.reload_action.setIcon(icon(name, self._icon_color()))
        self.reload_action.setToolTip("Stop loading" if loading else "Reload")
        self.toolbar_icon_buttons["reload"][1].setIcon(icon(name, self._icon_color()))

    def reload_or_stop(self):
        view = self.current_view()
        if not view:
            return
        if view.page().isLoading():
            view.stop()
        else:
            view.reload()

    def normalize_url(self, text):
        return resolve_address(
            text,
            home=self.settings.get("home", HOME_PAGE),
            search_url=SEARCH_URL,
        )

    def navigate_address(self):
        view = self.current_view()
        if view:
            view.setUrl(self.normalize_url(self.address_bar.text()))

    def navigate_text(self, text):
        view = self.current_view()
        if view:
            view.setUrl(self.normalize_url(text))

    def go_back(self):
        if self.current_view():
            self.current_view().back()

    def go_forward(self):
        if self.current_view():
            self.current_view().forward()

    def reload(self):
        if self.current_view():
            self.current_view().reload()

    def stop(self):
        if self.current_view():
            self.current_view().stop()

    def go_home(self):
        if self.current_view():
            self.current_view().setUrl(self._home_url())

    def change_zoom(self, delta):
        if delta is None:
            self.zoom = 1.0
        else:
            self.zoom = max(0.25, min(5.0, self.zoom + delta))
        if not self.is_private:
            self.settings.set("zoom", self.zoom)
        if self.current_view():
            self.current_view().setZoomFactor(self.zoom)

    def toggle_bookmark(self):
        view = self.current_view()
        if not view:
            return
        url = view.url().toString()
        if not url or url.startswith(("about:", "data:", "chrome:")):
            return
        if self.store.is_bookmarked(url):
            self.store.remove_bookmark(url)
            self.statusBar().showMessage("Bookmark removed", 3000)
        else:
            self.store.add_bookmark(url, view.title())
            self.statusBar().showMessage("Bookmark added", 3000)

    def show_history(self):
        ListDialog("Browsing History", self.store.history(), self, self).exec()

    def show_bookmarks(self):
        ListDialog("Bookmarks", self.store.bookmarks(), self, self).exec()

    def show_downloads(self):
        if not self.downloads:
            QMessageBox.information(self, "Downloads", "No downloads in this session.")
            return
        lines = [
            f"{item.suggestedFileName()}: {item.downloadDirectory()}"
            for item in self.downloads
        ]
        QMessageBox.information(self, "Downloads", "\n".join(lines)[:4000])

    def download_requested(self, download):
        if not isinstance(download, QWebEngineDownloadRequest):
            return
        downloads = Path(self.settings.get("download_path"))
        downloads.mkdir(parents=True, exist_ok=True)
        download.setDownloadDirectory(str(downloads))
        download.accept()
        self.downloads.append(download)
        download.finished.connect(
            lambda d=download: self.statusBar().showMessage(
                f"Download finished: {d.downloadFileName()}",
                5000,
            )
        )

    def show_find(self):
        self.find_bar.show()

    def show_settings(self):
        SettingsDialog(self, self).exec()

    def open_private_window(self):
        private_window = BrowserWindow(
            self.settings,
            self.store,
            self.data_dir,
            private=True,
            parent=self,
        )
        private_window.show()
        self.private_windows.append(private_window)

    def permission_requested(self, permission):
        origin = permission.origin().toString()
        kind = str(permission.permissionType()).split(".")[-1]
        answer = QMessageBox.question(
            self,
            "Site permission",
            f"{origin}\n\nAllow {kind.lower()}?",
            QMessageBox.StandardButton.Allow | QMessageBox.StandardButton.Deny,
        )
        if answer == QMessageBox.StandardButton.Allow:
            permission.grant()
        else:
            permission.deny()

    def certificate_error(self, error):
        reply = QMessageBox.warning(
            self,
            "Certificate warning",
            "A certificate error was detected. Continuing may expose data "
            "to an untrusted network.",
            QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Ignore:
            error.acceptCertificate()
        else:
            error.rejectCertificate()

    def apply_theme(self, dark, persist=True):
        if persist and not self.is_private:
            self.settings.set("dark_mode", dark)
        if hasattr(self, "theme_menu_action"):
            self.theme_menu_action.setChecked(dark)
        apply_theme(self, dark)
        self._update_toolbar_icons()
        if hasattr(self, "tabs"):
            self.tabs.tabBar().set_dark_mode(dark)

    def save_session(self):
        if self.is_private:
            return
        urls = [
            self.tabs.widget(index).url().toString()
            for index in range(self.tabs.count())
            if isinstance(self.tabs.widget(index), QWebEngineView)
        ]
        if urls:
            self.store.save_session(urls, self.tabs.currentIndex())

    def check_for_updates(self):
        if self.updater and self.updater.process.state() != QProcess.ProcessState.NotRunning:
            return
        self.updater = EngineUpdater(self)
        self.updater.finished.connect(self.update_finished)
        self.updater.start()
        self.statusBar().showMessage("Checking for Qt WebEngine updates...")

    def update_finished(self, success, output):
        if not success:
            QMessageBox.critical(
                self,
                "Update failed",
                f"Qt WebEngine could not be updated:\n{output[-3000:]}",
            )
            return
        reply = QMessageBox.question(
            self,
            "Update complete",
            "Qt WebEngine packages were updated. Restart Nebula now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()
            subprocess.Popen(
                [sys.executable, str(APP_DIR / "main.py")],
                cwd=str(APP_DIR),
            )

    def closeEvent(self, event):
        self.save_session()
        if not self.is_private:
            self.store.close()
        super().closeEvent(event)
