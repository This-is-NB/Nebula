import sys

from PySide6.QtCore import QObject, QProcess, Signal


class EngineUpdater(QObject):
    finished = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._completion_reported = False
        self.process = QProcess(self)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

    def start(self):
        self._completion_reported = False
        self.process.start(
            sys.executable,
            [
                "-m",
                "pip",
                "install",
                "--upgrade",
                "PySide6",
                "PySide6-WebEngine",
            ],
        )

    def _on_finished(self, exit_code, _exit_status):
        if self._completion_reported:
            return
        output = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        errors = bytes(self.process.readAllStandardError()).decode(errors="replace")
        self._completion_reported = True
        self.finished.emit(exit_code == 0, (output + "\n" + errors).strip())

    def _on_error(self, _error):
        if self._completion_reported:
            return
        self._completion_reported = True
        self.finished.emit(False, self.process.errorString())
