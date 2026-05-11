from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen
from PyQt5.QtCore    import Qt, QRectF
from datetime        import datetime


class TripPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.trip      = 0.0
        self.trip_b    = 0.0
        self.range_km  = 100
        self.temp      = 45
        self.mode      = 0   # 0=TRIP A, 1=TRIP B, 2=RANGE
        self._labels   = ["TRIP A", "TRIP B", "RANGE"]

    def set_data(self, trip_a, trip_b, range_km, temp):
        self.trip     = trip_a
        self.trip_b   = trip_b
        self.range_km = range_km
        self.temp     = temp
        self.update()

    def cycle_mode(self):
        self.mode = (self.mode + 1) % 3
        self.update()

    def _current_label(self):
        return self._labels[self.mode]

    def _current_value(self):
        if self.mode == 0:   return f"{self.trip:.1f} km"
        elif self.mode == 1: return f"{self.trip_b:.1f} km"
        else:                return f"{self.range_km} km"

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#0a0d12"))

        # Left border separator
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawLine(0, 10, 0, h - 10)

        row_h = h // 3

        # ── Clock ──────────────────────────────────
        now = datetime.now().strftime("%I:%M %p")
        p.setPen(QColor("#e0ecf8"))
        p.setFont(QFont("Rajdhani", min(int(row_h * 0.52), 22), QFont.Bold))
        p.drawText(QRectF(8, 0, w - 8, row_h), Qt.AlignVCenter | Qt.AlignLeft, now)

        # Divider
        p.setPen(QPen(QColor(255, 255, 255, 25), 1))
        p.drawLine(12, row_h, w - 12, row_h)

        # ── Trip label ─────────────────────────────
        p.setFont(QFont("Rajdhani", min(int(row_h * 0.32), 12)))
        p.setPen(QColor("#607080"))
        p.drawText(QRectF(8, row_h + 4, w - 8, row_h * 0.38),
                   Qt.AlignLeft | Qt.AlignTop,
                   self._current_label() + " ▸")

        # ── Trip value ─────────────────────────────
        p.setFont(QFont("Rajdhani", min(int(row_h * 0.5), 20), QFont.Bold))
        p.setPen(QColor("#e0ecf8"))
        p.drawText(QRectF(8, row_h + row_h * 0.38, w - 8, row_h * 0.62),
                   Qt.AlignLeft | Qt.AlignVCenter,
                   self._current_value())

        # Divider
        p.setPen(QPen(QColor(255, 255, 255, 25), 1))
        p.drawLine(12, row_h * 2, w - 12, row_h * 2)

        # ── Temperature ────────────────────────────
        col = "#44cc66" if self.temp < 70 else ("#ffaa22" if self.temp < 90 else "#ff4444")
        p.setFont(QFont("Rajdhani", min(int(row_h * 0.3), 11)))
        p.setPen(QColor("#607080"))
        p.drawText(QRectF(8, row_h * 2 + 4, w - 8, row_h * 0.35),
                   Qt.AlignLeft | Qt.AlignTop, "TEMP")
        p.setFont(QFont("Rajdhani", min(int(row_h * 0.46), 18), QFont.Bold))
        p.setPen(QColor(col))
        p.drawText(QRectF(8, row_h * 2 + row_h * 0.36, w - 8, row_h * 0.6),
                   Qt.AlignLeft | Qt.AlignVCenter,
                   f"{int(self.temp)}°C")

        p.end()