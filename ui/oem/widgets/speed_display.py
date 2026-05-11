from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen
from PyQt5.QtCore    import Qt, QRectF


class SpeedDisplay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed = 0
        self.unit  = "km/h"

    def set_speed(self, v):
        self.speed = max(0, v)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#0a0d12"))

        # Speed number — sized relative to widget height, capped
        font_size = min(int(h * 0.48), 72)
        p.setPen(QColor("#f0f4f8"))
        p.setFont(QFont("Rajdhani", font_size, QFont.Bold))
        p.drawText(
            QRectF(0, 0, w, h * 0.72),
            Qt.AlignCenter,
            str(int(self.speed))
        )

        # km/h label
        p.setFont(QFont("Rajdhani", min(int(h * 0.1), 16)))
        p.setPen(QColor("#6a8090"))
        p.drawText(
            QRectF(0, h * 0.68, w, h * 0.18),
            Qt.AlignCenter,
            self.unit
        )

        # Vertical separators
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawLine(0, 12, 0, h - 12)
        p.drawLine(w - 1, 12, w - 1, h - 12)

        p.end()