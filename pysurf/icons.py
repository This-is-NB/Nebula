from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def icon(name, color="#26324a"):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(color), 2.1, Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name in ("back", "forward"):
        tip = 7 if name == "back" else 25
        wing = 7 if name == "back" else -7
        painter.drawLine(7, 16, 25, 16)
        painter.drawLine(tip, 16, tip + wing, 9)
        painter.drawLine(tip, 16, tip + wing, 23)
    elif name == "reload":
        painter.drawArc(QRectF(6, 6, 20, 20), 35 * 16, 285 * 16)
        painter.drawLine(23, 5, 26, 12)
        painter.drawLine(26, 12, 19, 12)
    elif name == "stop":
        painter.drawRoundedRect(QRectF(8, 8, 16, 16), 3, 3)
    elif name == "bookmark":
        path = QPainterPath()
        path.moveTo(9, 5)
        path.lineTo(23, 5)
        path.lineTo(23, 27)
        path.lineTo(16, 22)
        path.lineTo(9, 27)
        path.closeSubpath()
        painter.drawPath(path)
    elif name == "menu":
        for x in (8, 16, 24):
            painter.drawEllipse(QPointF(x, 16), 1.7, 1.7)
    elif name == "plus":
        painter.drawLine(16, 7, 16, 25)
        painter.drawLine(7, 16, 25, 16)
    elif name == "close":
        painter.drawLine(9, 9, 23, 23)
        painter.drawLine(23, 9, 9, 23)
    elif name == "home":
        path = QPainterPath()
        path.moveTo(4, 15)
        path.lineTo(16, 5)
        path.lineTo(28, 15)
        path.moveTo(8, 13)
        path.lineTo(8, 27)
        path.lineTo(24, 27)
        path.lineTo(24, 13)
        path.moveTo(14, 27)
        path.lineTo(14, 19)
        path.lineTo(19, 19)
        path.lineTo(19, 27)
        painter.drawPath(path)
    elif name == "find":
        painter.drawEllipse(QRectF(5, 5, 16, 16))
        painter.drawLine(18, 19, 27, 28)
    elif name == "history":
        painter.drawEllipse(QRectF(7, 7, 20, 20))
        painter.drawLine(16, 11, 16, 17)
        painter.drawLine(16, 17, 21, 20)
        painter.drawLine(4, 10, 4, 17)
        painter.drawLine(4, 10, 10, 10)
    elif name == "download":
        painter.drawLine(16, 5, 16, 20)
        painter.drawLine(10, 14, 16, 20)
        painter.drawLine(16, 20, 22, 14)
        painter.drawLine(7, 24, 7, 27)
        painter.drawLine(7, 27, 25, 27)
        painter.drawLine(25, 27, 25, 24)
    elif name == "settings":
        painter.drawEllipse(QRectF(11, 11, 10, 10))
        for angle in range(0, 360, 45):
            painter.save()
            painter.translate(16, 16)
            painter.rotate(angle)
            painter.drawLine(0, -8, 0, -12)
            painter.restore()
    elif name == "private":
        painter.drawEllipse(QRectF(11, 7, 10, 10))
        painter.drawArc(QRectF(6, 14, 20, 16), 0, 180 * 16)
        painter.drawLine(5, 15, 27, 15)
    elif name == "restore":
        painter.drawArc(QRectF(7, 7, 19, 19), 35 * 16, 290 * 16)
        painter.drawLine(7, 8, 7, 15)
        painter.drawLine(7, 8, 14, 8)
    elif name == "duplicate":
        painter.drawRoundedRect(QRectF(10, 6, 15, 17), 2, 2)
        painter.drawLine(7, 11, 7, 26)
        painter.drawLine(7, 26, 21, 26)
    elif name == "lock":
        painter.drawRoundedRect(QRectF(7, 14, 18, 14), 3, 3)
        painter.drawArc(QRectF(11, 5, 10, 17), 0, 180 * 16)
        painter.drawLine(16, 19, 16, 23)
    elif name == "warning":
        path = QPainterPath()
        path.moveTo(16, 5)
        path.lineTo(28, 26)
        path.lineTo(4, 26)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(16, 12, 16, 19)
        painter.drawPoint(16, 23)
    elif name == "zoom_in":
        painter.drawEllipse(QRectF(4, 4, 17, 17))
        painter.drawLine(18, 18, 27, 27)
        painter.drawLine(12, 12, 12, 20)
        painter.drawLine(8, 16, 16, 16)
    elif name == "zoom_out":
        painter.drawEllipse(QRectF(4, 4, 17, 17))
        painter.drawLine(18, 18, 27, 27)
        painter.drawLine(8, 16, 16, 16)

    painter.end()
    return QIcon(pixmap)
