from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
)
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QTabBar, QToolBar, QToolButton


class MotionToolbar(QToolBar):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self._phase = 0
        self._motion_enabled = True
        self._dark = False
        self.setMovable(False)
        self.setIconSize(QSize(19, 19))
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def set_motion_enabled(self, enabled):
        self._motion_enabled = enabled
        for button in self.findChildren(MotionToolButton):
            button.set_motion_enabled(enabled)
        if enabled and self.isVisible():
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def set_dark_mode(self, enabled):
        self._dark = enabled
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self._motion_enabled:
            self._timer.start()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def _advance(self):
        self._phase = (self._phase + 3) % max(self.width() + 120, 1)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = self.rect()

        if self._dark:
            start, end = QColor("#111622"), QColor("#1d2032")
            accent = QColor("#7c63ff")
            secondary = QColor("#20d9d2")
        else:
            start, end = QColor("#f9f8ff"), QColor("#e8f4ff")
            accent = QColor("#7559ee")
            secondary = QColor("#009fba")

        gradient = QLinearGradient(0, 0, bounds.width(), bounds.height())
        gradient.setColorAt(0, start)
        gradient.setColorAt(1, end)
        painter.fillRect(bounds, gradient)

        if self._motion_enabled:
            painter.setClipRect(bounds)
            for index in range(12):
                drift = self._phase * (0.48 + index * 0.045)
                x = int((index * 149 + drift) % (bounds.width() + 90)) - 45
                y = 8 + (index * 23) % max(bounds.height() - 12, 1)
                color = QColor(accent if index % 2 else secondary)
                color.setAlpha(48 if index % 3 else 82)
                painter.setPen(QPen(color, 1.4 if index % 3 else 2.2))
                painter.drawLine(x, y, x + 66 + index * 3, y - 19)

            for index in range(3):
                x = int((self._phase * (0.8 + index * 0.12) + index * 311)
                        % (bounds.width() + 100)) - 50
                lightning = QPainterPath(QPointF(x, 0))
                lightning.lineTo(x + 10, 12)
                lightning.lineTo(x + 3, 21)
                lightning.lineTo(x + 16, 36)
                spark = QColor(secondary)
                spark.setAlpha(105)
                painter.setPen(QPen(spark, 1.7))
                painter.drawPath(lightning)

            beam_x = int(self._phase % max(bounds.width() + 150, 1)) - 75
            beam = QLinearGradient(beam_x - 55, 0, beam_x + 55, 0)
            beam.setColorAt(0, QColor(secondary.red(), secondary.green(), secondary.blue(), 0))
            beam.setColorAt(0.5, QColor(accent.red(), accent.green(), accent.blue(), 112))
            beam.setColorAt(1, QColor(secondary.red(), secondary.green(), secondary.blue(), 0))
            painter.fillRect(beam_x - 55, 0, 110, bounds.height(), beam)

        line = QLinearGradient(0, 0, bounds.width(), 0)
        line.setColorAt(0, QColor(secondary.red(), secondary.green(), secondary.blue(), 0))
        line.setColorAt(0.45, secondary)
        line.setColorAt(1, QColor(accent.red(), accent.green(), accent.blue(), 0))
        painter.fillRect(0, bounds.height() - 2, bounds.width(), 2, line)


class MotionTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0
        self._motion_enabled = True
        self._dark = False
        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def set_motion_enabled(self, enabled):
        self._motion_enabled = enabled
        if enabled and self.isVisible():
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def set_dark_mode(self, enabled):
        self._dark = enabled
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self._motion_enabled:
            self._timer.start()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def _advance(self):
        self._phase = (self._phase + 4) % 120
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._motion_enabled or self.currentIndex() < 0:
            return
        rect = self.tabRect(self.currentIndex())
        glow = QLinearGradient(rect.left(), 0, rect.right(), 0)
        if self._dark:
            colors = (QColor("#20d9d2"), QColor("#a08aff"), QColor("#20d9d2"))
        else:
            colors = (QColor("#009eaa"), QColor("#7559ee"), QColor("#009eaa"))
        offset = (self._phase % 120) / 120
        glow.setColorAt(0, QColor(colors[0].red(), colors[0].green(), colors[0].blue(), 90))
        glow.setColorAt(max(0.01, offset), colors[1])
        glow.setColorAt(1, QColor(colors[2].red(), colors[2].green(), colors[2].blue(), 90))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawRoundedRect(rect.adjusted(8, rect.height() - 3, -8, -1), 1.5, 1.5)


class MotionToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setAutoRaise(True)
        self.setIconSize(QSize(19, 19))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Browser toolbar button")
        self._base_icon_size = QSize(19, 19)
        self._hover_icon_size = QSize(22, 22)
        self._motion_enabled = True
        self._icon_animation = QPropertyAnimation(self, b"iconSize", self)
        self._icon_animation.setDuration(150)
        self._icon_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    def enterEvent(self, event):
        if self._motion_enabled:
            self._animate_icon(self._hover_icon_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._motion_enabled:
            self._animate_icon(self._base_icon_size)
        super().leaveEvent(event)

    def set_motion_enabled(self, enabled):
        self._motion_enabled = enabled
        if not enabled:
            self._icon_animation.stop()
            self.setIconSize(self._base_icon_size)

    def _animate_icon(self, size):
        self._icon_animation.stop()
        self._icon_animation.setStartValue(self.iconSize())
        self._icon_animation.setEndValue(size)
        self._icon_animation.start()
