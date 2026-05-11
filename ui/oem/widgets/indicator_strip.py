from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter, QColor, QFont, QPen, QBrush, QRadialGradient
from PyQt5.QtCore    import Qt, QRectF, QPointF


class IndicatorStrip(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.left_on     = False
        self.right_on    = False
        self.high_beam   = False
        self.eco_on      = True
        self.engine_warn = False
        self.charging    = False

    def update_state(self, left=False, right=False,
                     high=False, eco=True,
                     engine=False, charging=False):
        self.left_on     = left
        self.right_on    = right
        self.high_beam   = high
        self.eco_on      = eco
        self.engine_warn = engine
        self.charging    = charging
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Background
        p.fillRect(0, 0, w, h, QColor("#0a0d12"))

        # Subtle separator bottom
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.drawLine(0, h - 1, w, h - 1)

        def icon(cx, text, color, active, size=13):
            col = QColor(color) if active else QColor(40, 50, 60)
            if active:
                # soft glow
                gr = QRadialGradient(cx, h//2, 20)
                glow = QColor(color)
                glow.setAlpha(40)
                gr.setColorAt(0, glow)
                gr.setColorAt(1, QColor(0,0,0,0))
                p.setBrush(QBrush(gr))
                p.setPen(Qt.NoPen)
                p.drawEllipse(QPointF(cx, h//2), 20, 18)
            p.setPen(QPen(col))
            p.setFont(QFont("Segoe UI", size, QFont.Bold))
            p.drawText(QRectF(cx - 30, 0, 60, h), Qt.AlignCenter, text)

        # Positions
        icon(40,      "◄",       "#22dd44", self.left_on,    16)
        icon(100,     "≡◉",      "#4ab0ff", self.high_beam,  12)
        icon(w//2,    "ECO",     "#44ee66", self.eco_on,     11)
        icon(w - 100, "⚙",       "#ff9933", self.engine_warn,14)
        icon(w - 40,  "►",       "#22dd44", self.right_on,   16)

        if self.charging:
            p.setPen(QPen(QColor("#22aaff")))
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(QRectF(w//2 - 50, 0, 100, h),
                       Qt.AlignCenter, "⚡ CHARGING")

        p.end()