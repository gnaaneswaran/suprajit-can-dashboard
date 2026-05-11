from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen
from PyQt5.QtCore    import Qt, QRectF


class OdoStrip(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.odo         = 0
        self.service_km  = 1520
        self.show_service = True

    def set_odo(self, value, service_km=None):
        self.odo = value
        if service_km is not None:
            self.service_km = service_km
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#080b0f"))

        # Top separator
        p.setPen(QPen(QColor(255, 255, 255, 22), 1))
        p.drawLine(0, 0, w, 0)

        # ODO label
        p.setFont(QFont("Rajdhani", 11))
        p.setPen(QColor("#607080"))
        p.drawText(QRectF(16, 0, 50, h), Qt.AlignVCenter, "ODO")

        # ODO value
        p.setFont(QFont("Rajdhani", 14, QFont.Bold))
        p.setPen(QColor("#c8d8e8"))
        p.drawText(QRectF(62, 0, 180, h), Qt.AlignVCenter,
                   f"{int(self.odo)} km")

        # Centre vertical divider
        mid = w // 2
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawLine(mid, 6, mid, h - 6)

        # Service due
        if self.show_service:
            p.setFont(QFont("Segoe UI Emoji", 11))
            p.setPen(QColor("#ffaa22"))
            p.drawText(QRectF(mid + 12, 0, 28, h), Qt.AlignVCenter, "🔧")
            p.setFont(QFont("Rajdhani", 12, QFont.Bold))
            p.drawText(QRectF(mid + 38, 0, 260, h), Qt.AlignVCenter,
                       f"SERVICE IN {int(self.service_km)} km")

        p.end()