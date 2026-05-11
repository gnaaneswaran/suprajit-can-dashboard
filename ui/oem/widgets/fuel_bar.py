from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen, QLinearGradient, QBrush
from PyQt5.QtCore    import Qt, QRectF


class FuelBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(64)
        self.fuel = 80   # 0–100

    def set_fuel(self, value):
        self.fuel = max(0.0, min(100.0, value))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#0a0d12"))

        # F / E labels
        p.setFont(QFont("Rajdhani", 11, QFont.Bold))
        p.setPen(QColor("#c8d8e8"))
        p.drawText(QRectF(0, 6, w, 18), Qt.AlignCenter, "F")
        p.drawText(QRectF(0, h - 24, w, 18), Qt.AlignCenter, "E")

        # Bar geometry
        bx    = w // 2 - 10
        b_top = 28
        b_bot = h - 28
        b_h   = b_bot - b_top
        segs  = 8
        seg_h = max(4, b_h // segs - 2)
        gap   = 2
        filled = max(0, int((self.fuel / 100.0) * segs))

        for i in range(segs):
            yy = b_bot - (i + 1) * (seg_h + gap)
            if i < filled:
                if i < 2:
                    col = QColor("#ff4444")   # low fuel — red
                elif i < 4:
                    col = QColor("#ffaa22")   # mid — amber
                else:
                    col = QColor("#e8eef4")   # full — white
            else:
                col = QColor("#1e2a36")
            p.fillRect(bx, yy, 20, seg_h, col)

        # Fuel pump icon
        p.setFont(QFont("Segoe UI Emoji", 11))
        p.setPen(QColor("#8899aa"))
        p.drawText(QRectF(0, h // 2 - 2, w, 20), Qt.AlignCenter, "⛽")

        p.end()