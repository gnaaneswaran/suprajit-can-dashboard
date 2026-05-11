from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PyQt5.QtCore    import Qt, QRectF


class WarningStrip(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.side_stand   = False
        self.charging     = False
        self.charge_pct   = 0      # 0–100 during charge animation

    def set_state(self, side_stand=False, charging=False, charge_pct=0):
        self.side_stand = side_stand
        self.charging   = charging
        self.charge_pct = charge_pct
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#060810"))
        p.setPen(QPen(QColor(255, 255, 255, 15), 1))
        p.drawLine(0, 0, w, 0)

        if self.charging:
            # Charge progress bar
            filled = int((self.charge_pct / 100) * (w - 40))
            grad = QLinearGradient(20, 0, w - 20, 0)
            grad.setColorAt(0, QColor("#1144aa"))
            grad.setColorAt(1, QColor("#22aaff"))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(20, h//2 - 5, filled, 10, 5, 5)
            # track
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255,255,255,30), 1))
            p.drawRoundedRect(20, h//2 - 5, w - 40, 10, 5, 5)
            # label
            p.setFont(QFont("Rajdhani", 10, QFont.Bold))
            p.setPen(QColor("#22aaff"))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter,
                       f"⚡ CHARGING  {int(self.charge_pct)}%")

        elif self.side_stand:
            p.setFont(QFont("Rajdhani", 12, QFont.Bold))
            p.setPen(QColor("#ff4444"))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter,
                       "⚠  SIDE STAND DOWN")
        else:
            # Normal — faint status
            p.setFont(QFont("Rajdhani", 9))
            p.setPen(QColor("#2a3540"))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "SYSTEM OK")

        p.end()