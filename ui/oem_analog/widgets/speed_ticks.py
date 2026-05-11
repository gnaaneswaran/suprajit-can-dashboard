"""
ui/oem_analog/widgets/speed_ticks.py
──────────────────────────────────────
Draws tick marks and numeric speed labels for the analog speedometer.
Matches reference: white major ticks, fine minor ticks, white labels.
"""

import math
from PyQt5.QtGui  import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF


TICK_MAJOR_COL = "#d8e8f0"
TICK_MINOR_COL = "#2e3e50"
LABEL_COL      = "#dce8f0"


def _deg(v: float, max_val: float = 120.0) -> float:
    return 220.0 - (v / max_val) * 260.0


def draw_speed_ticks(p: QPainter, cx: float, cy: float, R: float, max_val: float = 120.0):
    """
    Draw tick marks and labels. Call inside cached QPixmap builder.
    Reference labels: 0, 20, 40, 60, 80, 100, 120
    """
    t_out = R - 18
    t_maj = R - 34
    t_med = R - 27
    t_min = R - 23
    l_r   = R - 50

    # Major ticks + labels every 20 km/h
    for val in range(0, int(max_val) + 1, 20):
        ang = math.radians(_deg(val, max_val))
        ca, sa = math.cos(ang), -math.sin(ang)

        # Glow
        p.setPen(QPen(QColor(200, 220, 240, 35), 5))
        p.drawLine(QPointF(cx + ca * t_maj, cy + sa * t_maj),
                   QPointF(cx + ca * t_out,  cy + sa * t_out))
        # Solid tick
        p.setPen(QPen(QColor(TICK_MAJOR_COL), 2.2))
        p.drawLine(QPointF(cx + ca * t_maj, cy + sa * t_maj),
                   QPointF(cx + ca * t_out,  cy + sa * t_out))

        # Label
        f = QFont("Segoe UI", max(7, int(R * 0.088)))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QPen(QColor(LABEL_COL)))
        tw, th = 36, 22
        p.drawText(QRectF(cx + ca * l_r - tw/2, cy + sa * l_r - th/2, tw, th),
                   Qt.AlignCenter, str(val))

    # Medium ticks every 10 km/h
    for val in range(10, int(max_val) + 1, 10):
        if val % 20 == 0:
            continue
        ang = math.radians(_deg(val, max_val))
        ca, sa = math.cos(ang), -math.sin(ang)
        p.setPen(QPen(QColor("#283848"), 1.5))
        p.drawLine(QPointF(cx + ca * t_med, cy + sa * t_med),
                   QPointF(cx + ca * t_out,  cy + sa * t_out))

    # Minor ticks every 5 km/h
    for val in range(5, int(max_val) + 1, 10):
        ang = math.radians(_deg(val, max_val))
        ca, sa = math.cos(ang), -math.sin(ang)
        p.setPen(QPen(QColor(TICK_MINOR_COL), 1))
        p.drawLine(QPointF(cx + ca * t_min, cy + sa * t_min),
                   QPointF(cx + ca * t_out,  cy + sa * t_out))

    # km/h label
    kf = QFont("Segoe UI", max(8, int(R * 0.082)))
    p.setFont(kf)
    p.setPen(QPen(QColor("#3a5068")))
    p.drawText(QRectF(cx - 28, cy - R * 0.22, 56, 16),
               Qt.AlignCenter, "km/h")