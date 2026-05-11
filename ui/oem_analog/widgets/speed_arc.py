"""
ui/oem_analog/widgets/speed_arc.py
────────────────────────────────────
Draws the blue (0-60) and red (80-120) speed arcs
matching the Honda Activa / Suzuki analog cluster reference.
Renders into a supplied QPainter at given cx, cy, R.
"""

import math
from PyQt5.QtGui  import QPainter, QColor, QPen
from PyQt5.QtCore import Qt


# Arc colour constants — match reference image
ARC_BLUE  = "#3a8fd4"   # 0–60 km/h zone
ARC_RED   = "#e03030"   # 80–120 km/h zone
ARC_TRACK = "#1a1a1a"   # background track


def _deg(v: float, max_val: float = 120.0) -> float:
    """Map 0–max_val → 220° down to -40° (260° sweep)."""
    return 220.0 - (v / max_val) * 260.0


def draw_speed_arcs(p: QPainter, cx: float, cy: float, R: float, max_val: float = 120.0):
    """
    Draw the three-zone speed arc (track + blue + red) onto p.
    Call this inside a cached QPixmap builder.

    Zones:
        0  – 60  → blue
        60 – 80  → dark gap (no colour, just track)
        80 – 120 → red
    """
    ar = R - 14
    from PyQt5.QtCore import QRectF
    rect = QRectF(cx - ar, cy - ar, ar * 2, ar * 2)

    # ── Background track ──────────────────────────────────────
    p.setPen(QPen(QColor(ARC_TRACK), 14, Qt.SolidLine, Qt.RoundCap))
    p.setBrush(Qt.NoBrush)
    a0 = _deg(0, max_val); span = _deg(max_val, max_val) - a0
    p.drawArc(rect, int(a0 * 16), int(span * 16))

    # ── Blue zone: 0–60 ───────────────────────────────────────
    def arc(v0, v1, col, width=9):
        a_start = _deg(v0, max_val)
        a_span  = _deg(v1, max_val) - a_start
        # glow
        gc = QColor(col); gc.setAlpha(50)
        p.setPen(QPen(gc, width + 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, int(a_start * 16), int(a_span * 16))
        # solid
        p.setPen(QPen(QColor(col), width, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, int(a_start * 16), int(a_span * 16))

    arc(0,  60,  ARC_BLUE)
    arc(80, 120, ARC_RED)