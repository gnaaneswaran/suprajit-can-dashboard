"""
hybrid_cluster.py — Suprajit CAN Bus Analyzer
OEM-grade hybrid cluster: Suzuki/TVS/Yamaha aesthetic
- Matte charcoal housing with layered bezels
- Analog speedometer (62% width) with metallic feel
- Recessed LCD panel (38% width) with pale blue-grey tint
- Real-time clock, date, live location (ip-api.com, no key needed)
- Needle smoothing animation
- Blinking turn indicators with glow
- QPainter-drawn icons (no emojis)
- Condensed italic automotive fonts
- Vehicle State Engine with realistic scooter physics
- Keyboard controls: ↑ throttle, ↓ brake, ←/→ indicators, 1/2/3 modes
"""

import math
import urllib.request
import json
import threading

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QSizePolicy, QApplication)
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QTimer,
    QPropertyAnimation,
    pyqtProperty
)
from PyQt5.QtGui     import (QPainter, QColor, QPen, QBrush, QFont,
                             QRadialGradient, QLinearGradient, QPainterPath,
                             QFontDatabase)
from datetime        import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  PALETTE  — matte charcoal / graphite / Suzuki LCD
# ─────────────────────────────────────────────────────────────────────────────
P = {
    "shell_outer":  "#05070b",
    "shell_inner":  "#0c1016",
    "bezel_outer":  "#1b2430",
    "bezel_inner":  "#2d3f52",
    "bezel_rim":    "#4a6070",
    "dial_bg":      "#07090d",
    "dial_ring":    "#1a2535",
    "lcd_bg_top":   "#c8d8e8",
    "lcd_bg_bot":   "#9fb6ca",
    "lcd_text":     "#111827",
    "lcd_muted":    "#3a5570",
    "lcd_border":   "#7a9ab8",
    "lcd_divider":  "#8aafc8",
    "tick_major":   "#ccd8e2",
    "tick_minor":   "#3a4f62",
    "tick_label":   "#dbe7f2",
    "arc_green":    "#22c55e",
    "arc_amber":    "#f59e0b",
    "arc_red":      "#ef4444",
    "needle":       "#e8e8e8",
    "hub_outer":    "#1a2535",
    "hub_inner":    "#3d5470",
    "eco_green":    "#0d6b22",
    "warn_amber":   "#8a5500",
    "danger_red":   "#8a1010",
    "text_primary": "#dbe7f2",
    "text_muted":   "#4a6070",
    "strip_bg":     "#9fb0c0",
}


# ─────────────────────────────────────────────────────────────────────────────
#  LOCATION FETCHER  (background thread)
# ─────────────────────────────────────────────────────────────────────────────
class _Loc:
    city = "--"; region = "--"

    @classmethod
    def fetch(cls):
        def _w():
            try:
                with urllib.request.urlopen(
                        "http://ip-api.com/json/?fields=city,regionName",
                        timeout=4) as r:
                    d = json.loads(r.read())
                cls.city   = d.get("city", "--")
                cls.region = d.get("regionName", "--")
            except Exception:
                pass
        threading.Thread(target=_w, daemon=True).start()

    @classmethod
    def text(cls):
        s = f"{cls.city}, {cls.region}"
        return s[:24] if len(s) > 24 else s

_Loc.fetch()


# ─────────────────────────────────────────────────────────────────────────────
#  QPainter ICON HELPERS  (no emojis)
# ─────────────────────────────────────────────────────────────────────────────
def draw_fuel_icon(p, cx, cy, size, color):
    """Draw a simple fuel-pump symbol."""
    c = QColor(color)
    p.setPen(QPen(c, max(1, size // 6)))
    p.setBrush(Qt.NoBrush)
    s = size
    # body rectangle
    p.drawRect(int(cx - s*0.35), int(cy - s*0.4),
               int(s * 0.5),      int(s * 0.8))
    # nozzle arm
    p.drawLine(QPointF(cx + s*0.15, cy - s*0.3),
               QPointF(cx + s*0.45, cy - s*0.3))
    p.drawLine(QPointF(cx + s*0.45, cy - s*0.3),
               QPointF(cx + s*0.45, cy + s*0.05))
    # fuel line inside body
    p.setPen(QPen(c, max(1, size // 8)))
    p.drawLine(QPointF(cx - s*0.12, cy - s*0.15),
               QPointF(cx + s*0.12, cy - s*0.15))


def draw_location_icon(p, cx, cy, size, color):
    """Draw a map-pin / teardrop."""
    c = QColor(color)
    p.setPen(QPen(c, max(1, size // 7)))
    p.setBrush(Qt.NoBrush)
    r = size * 0.35
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy - size * 0.1), r, r)
    path.moveTo(cx, cy - size * 0.1 + r)
    path.lineTo(cx, cy + size * 0.45)
    p.drawPath(path)


def draw_thermometer(p, cx, cy, size, color):
    """Minimal thermometer symbol."""
    c = QColor(color)
    p.setPen(QPen(c, max(1, size // 7)))
    p.setBrush(Qt.NoBrush)
    # stem
    p.drawLine(QPointF(cx, cy - size*0.42), QPointF(cx, cy + size*0.15))
    # bulb
    p.setBrush(QBrush(c))
    p.setPen(Qt.NoPen)
    p.drawEllipse(QRectF(cx - size*0.18, cy + size*0.14,
                         size*0.36, size*0.36))


def draw_stand_icon(p, cx, cy, size, color):
    """Side-stand triangle."""
    c = QColor(color)
    p.setPen(QPen(c, max(1, size // 7)))
    pts = [QPointF(cx, cy - size*0.42),
           QPointF(cx + size*0.3, cy + size*0.42),
           QPointF(cx - size*0.3, cy + size*0.42)]
    p.drawPolygon(*pts)


# ─────────────────────────────────────────────────────────────────────────────
#  SPEEDOMETER  — analog dial, OEM feel
# ─────────────────────────────────────────────────────────────────────────────
class SpeedometerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._speed_target = 0.0
        self._speed_disp   = 0.0   # smoothed display value
        self._fuel         = 100.0
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Needle smoothing timer
        self._smooth = QTimer()
        self._smooth.setInterval(16)   # ~60 fps
        self._smooth.timeout.connect(self._smooth_tick)
        self._smooth.start()

    def _smooth_tick(self):
        diff = self._speed_target - self._speed_disp
        if abs(diff) > 0.2:
            self._speed_disp += diff * 0.12   # damping factor
            self.update()

    def set_speed(self, v):
        self._speed_target = max(0.0, min(140.0, float(v)))

    def set_fuel(self, v):
        self._fuel = max(0.0, min(100.0, float(v)))
        self.update()

    def _deg(self, v):
        # 0 km/h = 225°, 140 km/h = -45°  (270° sweep)
        return 225.0 - (v / 140.0) * 270.0

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H  = self.width(), self.height()
        cx, cy = W / 2.0, H / 2.0
        R = min(W, H) / 2.0 - 8

        # ── 1. Outer metallic bezel ring ──────────────────────────
        bezel_grad = QRadialGradient(cx, cy, R + 6)
        bezel_grad.setColorAt(0.82, QColor("#2d3f52"))
        bezel_grad.setColorAt(0.88, QColor("#4a6070"))
        bezel_grad.setColorAt(0.94, QColor("#1b2535"))
        bezel_grad.setColorAt(1.00, QColor("#0e1825"))
        p.setBrush(QBrush(bezel_grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(cx - R - 6, cy - R - 6,
                             (R + 6) * 2, (R + 6) * 2))

        # ── 2. Concentric texture rings (brushed metal feel) ───────
        for i, (rad, alpha) in enumerate([(R-2,25),(R-5,18),(R-9,12)]):
            ring_col = QColor(180, 200, 220, alpha)
            p.setPen(QPen(ring_col, 1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(cx - rad, cy - rad, rad*2, rad*2))

        # ── 3. Dial face ───────────────────────────────────────────
        face_grad = QRadialGradient(cx, cy - R*0.1, R)
        face_grad.setColorAt(0.0,  QColor("#0f161f"))
        face_grad.setColorAt(0.6,  QColor("#08101a"))
        face_grad.setColorAt(1.0,  QColor("#040810"))
        p.setBrush(QBrush(face_grad))
        p.setPen(QPen(QColor("#101c28"), 1.5))
        p.drawEllipse(QRectF(cx - R, cy - R, R*2, R*2))

        # ── 4. Colored speed arc zones ─────────────────────────────
        ar    = R - 10
        arect = QRectF(cx - ar, cy - ar, ar*2, ar*2)

        def arc_zone(v0, v1, col, w=15):
            a0   = self._deg(v0)
            span = -(v1 - v0) / 140.0 * 270.0
            # glow layer (wider, dimmer)
            gc = QColor(col)
            gc.setAlpha(60)
            p.setPen(QPen(gc, w + 6, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawArc(arect, int(a0*16), int(span*16))
            # solid arc
            p.setPen(QPen(QColor(col), w, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(arect, int(a0*16), int(span*16))

        arc_zone(0,   60,  P["arc_green"])
        arc_zone(60,  100, P["arc_amber"])
        arc_zone(100, 140, P["arc_red"])

        # ── 5. Major tick marks + labels ───────────────────────────
        majors = [0, 20, 40, 60, 80, 100, 120, 140]
        t_out = R - 14
        t_maj = R - 30
        t_min = R - 22
        t_med = R - 26
        l_r   = R - 46

        for val in majors:
            ang = math.radians(self._deg(val))
            ca, sa = math.cos(ang), -math.sin(ang)
            p.setPen(QPen(QColor(P["tick_major"]), 2.2))
            p.drawLine(QPointF(cx + ca*t_maj, cy + sa*t_maj),
                       QPointF(cx + ca*t_out,  cy + sa*t_out))
            # label — condensed italic feel
            f = QFont("Segoe UI", max(7, int(R*0.088)), QFont.Bold)
            f.setItalic(True)
            f.setLetterSpacing(QFont.AbsoluteSpacing, -0.5)
            p.setFont(f)
            p.setPen(QPen(QColor(P["tick_label"])))
            p.drawText(QRectF(cx+ca*l_r-17, cy+sa*l_r-11, 34, 22),
                       Qt.AlignCenter, str(val))

        # Minor ticks every 5 km/h
        for val in range(0, 141, 5):
            if val % 20 == 0:
                continue
            ang = math.radians(self._deg(val))
            ca, sa = math.cos(ang), -math.sin(ang)
            if val % 10 == 0:
                p.setPen(QPen(QColor("#2d4460"), 1.5))
                p.drawLine(QPointF(cx+ca*t_med, cy+sa*t_med),
                           QPointF(cx+ca*t_out,  cy+sa*t_out))
            else:
                p.setPen(QPen(QColor(P["tick_minor"]), 1))
                p.drawLine(QPointF(cx+ca*t_min, cy+sa*t_min),
                           QPointF(cx+ca*t_out,  cy+sa*t_out))

        # km/h label
        f2 = QFont("Segoe UI", max(8, int(R*0.09)))
        f2.setItalic(True)
        p.setFont(f2)
        p.setPen(QPen(QColor("#2d4460")))
        p.drawText(QRectF(cx-30, cy - R*0.30, 60, 20),
                   Qt.AlignCenter, "km/h")

        # ── 6. Fuel sub-gauge (bottom, 6 o'clock) ─────────────────
        fr   = R * 0.25
        fcy2 = cy + R * 0.58
        f_start = 210
        f_span  = 120
        frect = QRectF(cx-fr, fcy2-fr, fr*2, fr*2)

        # background track
        p.setPen(QPen(QColor("#131e2a"), 7, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawArc(frect, int(f_start*16), int(f_span*16))

        # filled portion
        filled = (self._fuel / 100.0) * f_span
        fc = (P["arc_green"] if self._fuel > 30
              else P["arc_amber"] if self._fuel > 15
              else P["arc_red"])
        p.setPen(QPen(QColor(fc), 5, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(f_start*16), int(filled*16))

        # E / F labels
        fs3 = max(7, int(R*0.085))
        f3 = QFont("Segoe UI", fs3, QFont.Bold); f3.setItalic(True)
        p.setFont(f3)
        p.setPen(QPen(QColor(P["arc_red"])))
        p.drawText(QRectF(cx-fr-20, fcy2+fr*0.05, 18, 14),
                   Qt.AlignCenter, "E")
        p.setPen(QPen(QColor(P["arc_green"])))
        p.drawText(QRectF(cx+fr+4, fcy2+fr*0.05, 18, 14),
                   Qt.AlignCenter, "F")

        # fuel pump icon (QPainter drawn)
        p.save()
        draw_fuel_icon(p, cx, fcy2 - fr*0.45, int(fr*0.75),
                       P["tick_minor"])
        p.restore()

        # ── 7. Needle — tapered shape ─────────────────────────────
        ang = math.radians(self._deg(self._speed_disp))
        ca, sa = math.cos(ang), -math.sin(ang)
        nl = R - 24

        # tapered needle path
        perp_ca = -sa
        perp_sa =  ca
        base_w  = 5.0
        tip_w   = 0.8

        path = QPainterPath()
        # base points (wide end near pivot)
        bx = cx - ca * 12
        by = cy - sa * 12
        tx = cx + ca * nl
        ty = cy + sa * nl

        path.moveTo(bx + perp_ca*base_w, by + perp_sa*base_w)
        path.lineTo(tx + perp_ca*tip_w,  ty + perp_sa*tip_w)
        path.lineTo(tx - perp_ca*tip_w,  ty - perp_sa*tip_w)
        path.lineTo(bx - perp_ca*base_w, by - perp_sa*base_w)
        path.closeSubpath()

        # needle shadow
        p.setPen(Qt.NoPen)
        shadow_col = QColor(0, 0, 0, 80)
        p.setBrush(QBrush(shadow_col))
        p.translate(2, 2)
        p.drawPath(path)
        p.translate(-2, -2)

        # needle fill
        needle_grad = QLinearGradient(
            bx + perp_ca*base_w, by + perp_sa*base_w,
            bx - perp_ca*base_w, by - perp_sa*base_w)
        needle_grad.setColorAt(0.0, QColor("#ffffff"))
        needle_grad.setColorAt(0.4, QColor("#e8e8e8"))
        needle_grad.setColorAt(1.0, QColor("#9ab0c0"))
        p.setBrush(QBrush(needle_grad))
        p.drawPath(path)

        # ── 8. Center hub — layered ───────────────────────────────
        p.setPen(Qt.NoPen)
        # outer shadow ring
        p.setBrush(QBrush(QColor("#020507")))
        p.drawEllipse(QRectF(cx-14, cy-14, 28, 28))
        # hub ring
        hub_g = QRadialGradient(cx-2, cy-2, 12)
        hub_g.setColorAt(0.0, QColor("#3d5470"))
        hub_g.setColorAt(0.6, QColor("#1e2e3f"))
        hub_g.setColorAt(1.0, QColor("#0d1825"))
        p.setBrush(QBrush(hub_g))
        p.drawEllipse(QRectF(cx-11, cy-11, 22, 22))
        # center dot
        p.setBrush(QBrush(QColor("#4a6a85")))
        p.drawEllipse(QRectF(cx-4, cy-4, 8, 8))

        # ── 9. Top glare (glass reflection) ───────────────────────
        glare_rect = QRectF(cx - R*0.55, cy - R*0.85, R*1.1, R*0.35)
        glare_g = QLinearGradient(0, cy - R*0.85, 0, cy - R*0.5)
        glare_g.setColorAt(0.0, QColor(255, 255, 255, 18))
        glare_g.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glare_g))
        p.drawEllipse(glare_rect)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  LCD PANEL  — recessed, Suzuki-style, pale blue-grey
# ─────────────────────────────────────────────────────────────────────────────
class LCDPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Layered bezel (3 layers) ───────────────────────────────
        # Layer 1: outer dark bezel
        l1 = QFrame()
        l1.setStyleSheet(f"""
            QFrame {{
                background: {P['bezel_outer']};
                border: 3px solid {P['bezel_rim']};
                border-radius: 14px;
            }}
            QLabel {{ border:none; background:transparent; }}
        """)
        l1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        l1l = QVBoxLayout(l1)
        l1l.setContentsMargins(4, 4, 4, 4)
        l1l.setSpacing(0)

        # Layer 2: inner trim ring
        l2 = QFrame()
        l2.setStyleSheet(f"""
            QFrame {{
                background: {P['bezel_inner']};
                border: 2px solid {P['bezel_rim']};
                border-radius: 11px;
            }}
            QLabel {{ border:none; background:transparent; }}
        """)
        l2l = QVBoxLayout(l2)
        l2l.setContentsMargins(3, 3, 3, 3)
        l2l.setSpacing(0)

        # Layer 3: inset LCD glass
        lcd = QFrame()
        lcd.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {P['lcd_bg_top']},
                    stop:1 {P['lcd_bg_bot']}
                );
                border: 1px solid {P['lcd_border']};
                border-radius: 9px;
            }}
            QLabel {{ border:none; background:transparent; }}
        """)
        lcd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ll = QVBoxLayout(lcd)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # ── LCD content ────────────────────────────────────────────

        # Row 1: time + date + BT
        r1 = self._lrow(40)
        r1l = QHBoxLayout(r1)
        r1l.setContentsMargins(12, 0, 12, 0)

        self.time_lbl = QLabel("10:30 AM")
        self._lcd_style(self.time_lbl, 15, bold=True)

        self.date_lbl = QLabel("Mon 11 May")
        self._lcd_style(self.date_lbl, 10, color=P["lcd_muted"])

        # BT icon (simple square as stand-in for BT symbol)
        self.bt_lbl = _BTIcon()
        self.bt_lbl.setFixedSize(18, 18)

        r1l.addWidget(self.time_lbl)
        r1l.addSpacing(8)
        r1l.addWidget(self.date_lbl)
        r1l.addStretch()
        r1l.addWidget(self.bt_lbl)
        ll.addWidget(r1)
        ll.addWidget(self._hline())

        # Row 2: big speed
        r2 = self._lrow()
        r2l = QVBoxLayout(r2)
        r2l.setContentsMargins(0, 2, 0, 2)
        r2l.setSpacing(0)

        self.spd_lbl = QLabel("0")
        self.spd_lbl.setAlignment(Qt.AlignCenter)
        f_spd = QFont("Courier New", 62, QFont.Bold)
        self.spd_lbl.setFont(f_spd)
        self.spd_lbl.setStyleSheet(f"color:{P['lcd_text']};")

        spd_u = QLabel("km/h")
        spd_u.setAlignment(Qt.AlignCenter)
        self._lcd_style(spd_u, 10, color=P["lcd_muted"])

        r2l.addWidget(self.spd_lbl)
        r2l.addWidget(spd_u)
        ll.addWidget(r2, 2)
        ll.addWidget(self._hline())

        # Row 3: ODO
        self.odo_val  = self._add_row(ll, "ODO",       "0.0 km",  alt=False)
        # Row 4: TRIP A
        self.trip_val = self._add_row(ll, "TRIP A",    "0.0 km",  alt=True)
        # Row 5: RANGE with icon
        self.range_val = self._add_row(ll, None,       "300 km",
                                       alt=False, icon="fuel",
                                       val_col=P["eco_green"])
        # Row 6: LOCATION
        self.loc_val  = self._add_row(ll, None,        "-- --",
                                      alt=True, icon="loc",
                                      val_col=P["lcd_muted"], val_size=10)

        ll.addWidget(self._hline())

        # Bottom strip
        strip = _StatusStrip()
        self.strip = strip
        ll.addWidget(strip)

        l2l.addWidget(lcd)
        l1l.addWidget(l2)
        root.addWidget(l1)

    # helpers

    def _lrow(self, h=None):
        f = QFrame()
        f.setStyleSheet("QFrame{background:transparent;border:none;} QLabel{border:none;background:transparent;}")
        if h:
            f.setFixedHeight(h)
        return f

    def _hline(self):
        f = QFrame()
        f.setFixedHeight(1)
        f.setStyleSheet(f"background:{P['lcd_divider']};border:none;")
        return f

    def _lcd_style(self, lbl, size, bold=False, color=None):
        if color is None:
            color = P["lcd_text"]
        w = QFont.Bold if bold else QFont.Normal
        f = QFont("Segoe UI", size, w)
        lbl.setFont(f)
        lbl.setStyleSheet(f"color:{color};")

    def _add_row(self, parent, label, value,
                 alt=False, icon=None, val_col=None, val_size=15):
        if val_col is None:
            val_col = P["lcd_text"]
        row = QFrame()
        row.setFixedHeight(34)
        row.setStyleSheet(
            "QFrame{background:transparent;border:none;} "
            "QLabel{border:none;background:transparent;}")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 0, 12, 0)

        if icon == "fuel":
            ic = _FuelIconLabel()
            ic.setFixedSize(22, 22)
            rl.addWidget(ic)
            rl.addSpacing(4)
            lbl_w = QLabel("RANGE")
            self._lcd_style(lbl_w, 11, bold=True, color=P["lcd_muted"])
            rl.addWidget(lbl_w)
        elif icon == "loc":
            ic = _LocIconLabel()
            ic.setFixedSize(22, 22)
            rl.addWidget(ic)
            rl.addSpacing(4)
            lbl_w = QLabel("LOCATION")
            self._lcd_style(lbl_w, 10, color=P["lcd_muted"])
            rl.addWidget(lbl_w)
        else:
            lbl_w = QLabel(label or "")
            self._lcd_style(lbl_w, 11, bold=True, color=P["lcd_muted"])
            rl.addWidget(lbl_w)

        rl.addStretch()

        val = QLabel(value)
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        f_val = QFont("Courier New", val_size, QFont.Bold)
        val.setFont(f_val)
        val.setStyleSheet(f"color:{val_col};")
        val.setObjectName("val")
        rl.addWidget(val)

        parent.addWidget(row)
        parent.addWidget(self._hline())
        return val

    # update — range is now driven by VehicleState via vehicle_tick
    def update_data(self, speed, fuel, temp, odo, trip):
        now = datetime.now()
        self.time_lbl.setText(now.strftime("%I:%M %p"))
        self.date_lbl.setText(now.strftime("%a %d %b"))
        self.spd_lbl.setText(str(int(speed)))
        self.odo_val.setText(f"{odo:.1f} km")
        self.trip_val.setText(f"{trip:.1f} km")
        self.loc_val.setText(_Loc.text())
        self.strip.update(speed, temp)


# ─────────────────────────────────────────────────────────────────────────────
#  ICON LABEL WIDGETS  (QPainter, no emoji)
# ─────────────────────────────────────────────────────────────────────────────
class _BTIcon(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(P["lcd_muted"]), 2))
        cx, cy = self.width()/2, self.height()/2
        s = min(self.width(), self.height()) * 0.4
        # simple BT approximation: vertical line + two diamonds
        p.drawLine(QPointF(cx, cy-s), QPointF(cx, cy+s))
        p.drawLine(QPointF(cx, cy-s), QPointF(cx+s*0.6, cy-s*0.4))
        p.drawLine(QPointF(cx+s*0.6, cy-s*0.4), QPointF(cx, cy))
        p.drawLine(QPointF(cx, cy), QPointF(cx+s*0.6, cy+s*0.4))
        p.drawLine(QPointF(cx+s*0.6, cy+s*0.4), QPointF(cx, cy+s))
        p.end()


class _FuelIconLabel(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_fuel_icon(p, self.width()/2, self.height()/2,
                       int(min(self.width(), self.height()) * 0.85),
                       P["lcd_muted"])
        p.end()


class _LocIconLabel(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_location_icon(p, self.width()/2, self.height()/2,
                           int(min(self.width(), self.height()) * 0.85),
                           P["lcd_muted"])
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  STATUS STRIP  — TEMP | SIDE STAND | MODE
# ─────────────────────────────────────────────────────────────────────────────
class _StatusStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {P['strip_bg']},
                    stop:1 #8fa6ba
                );
                border:none;
                border-bottom-left-radius:8px;
                border-bottom-right-radius:8px;
            }}
            QLabel {{ border:none; background:transparent; }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._temp_ic, self._temp_v, tw   = self._cell("TEMP",       "45°C",  P["lcd_text"],  icon="therm")
        self._stand_ic, self._stand_v, sw = self._cell("SIDE STAND", "UP",    P["eco_green"], icon="stand")
        self._mode_v, mw                  = self._mode_cell()

        lay.addWidget(tw, 1)
        lay.addWidget(self._vline())
        lay.addWidget(sw, 1)
        lay.addWidget(self._vline())
        lay.addWidget(mw, 1)

    def _vline(self):
        f = QFrame()
        f.setFixedWidth(1)
        f.setStyleSheet(f"background:{P['lcd_border']};border:none;")
        return f

    def _cell(self, label, value, col, icon=None):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        wl = QVBoxLayout(w)
        wl.setContentsMargins(4, 3, 4, 3)
        wl.setSpacing(1)

        # top row: icon + label
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0,0,0,0)
        top_row.setSpacing(3)

        if icon == "therm":
            ic = _ThermWidget()
            ic.setFixedSize(14, 14)
            top_row.addWidget(ic)
        elif icon == "stand":
            ic = _StandWidget()
            ic.setFixedSize(14, 14)
            top_row.addWidget(ic)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{P['lcd_muted']};font-size:8px;font-weight:bold;")
        top_row.addWidget(lbl)
        top_row.addStretch()
        wl.addLayout(top_row)

        val = QLabel(value)
        val.setAlignment(Qt.AlignCenter)
        f_v = QFont("Segoe UI", 12, QFont.Bold)
        val.setFont(f_v)
        val.setStyleSheet(f"color:{col};")
        wl.addWidget(val)

        return ic if icon else None, val, w

    def _mode_cell(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        wl = QVBoxLayout(w)
        wl.setContentsMargins(4, 3, 4, 3)
        wl.setSpacing(1)

        lbl = QLabel("MODE")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color:{P['lcd_muted']};font-size:8px;font-weight:bold;")

        val = QLabel("ECO")
        val.setAlignment(Qt.AlignCenter)
        f_v = QFont("Segoe UI", 12, QFont.Bold)
        val.setFont(f_v)
        val.setStyleSheet(
            f"color:{P['eco_green']};border:2px solid {P['eco_green']};"
            f"border-radius:3px;padding:1px 6px;")

        wl.addWidget(lbl)
        wl.addWidget(val)
        return val, w

    def update(self, speed, temp):
        # temperature
        if temp < 70:
            tc = P["lcd_text"]
        elif temp < 90:
            tc = P["warn_amber"]
        else:
            tc = P["danger_red"]
        self._temp_v.setText(f"{int(temp)}°C")
        self._temp_v.setStyleSheet(f"color:{tc};font-size:12px;font-weight:bold;")

        # mode
        if speed < 40:
            mode, mc = "ECO",   P["eco_green"]
        elif speed < 80:
            mode, mc = "CITY",  "#0a3a7a"
        else:
            mode, mc = "SPORT", P["danger_red"]
        self._mode_v.setText(mode)
        self._mode_v.setStyleSheet(
            f"color:{mc};border:2px solid {mc};border-radius:3px;"
            f"padding:1px 6px;font-size:12px;font-weight:bold;")


class _ThermWidget(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_thermometer(p, self.width()/2, self.height()/2,
                         min(self.width(), self.height()), P["lcd_muted"])
        p.end()


class _StandWidget(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_stand_icon(p, self.width()/2, self.height()/2,
                        min(self.width(), self.height()), P["lcd_muted"])
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  INDICATOR STRIP  — top warning icons, blinking turn arrows
# ─────────────────────────────────────────────────────────────────────────────
class IndicatorStrip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(f"background:{P['shell_inner']};border-bottom:1px solid {P['bezel_outer']};")

        self._left_on  = False
        self._right_on = False
        self._blink    = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(0)

        self.l_arr  = QLabel("◄")
        self.r_arr  = QLabel("►")
        for a in [self.l_arr, self.r_arr]:
            a.setStyleSheet(f"color:{P['bezel_outer']};font-size:15px;font-weight:bold;background:transparent;")

        self.ic_beam   = self._ic("BEAM",   P["bezel_outer"])
        self.ic_engine = self._ic("ENGINE", P["bezel_outer"])
        self.ic_temp   = self._ic("TEMP",   P["bezel_outer"])
        self.ic_eco    = self._ic("ECO",    P["arc_green"])
        self.ic_abs    = self._ic("ABS",    P["arc_green"])

        lay.addWidget(self.l_arr)
        lay.addSpacing(10)
        for w in [self.ic_beam, self.ic_engine, self.ic_temp, self.ic_eco]:
            lay.addWidget(w); lay.addSpacing(14)
        lay.addStretch()
        lay.addWidget(self.ic_abs)
        lay.addSpacing(10)
        lay.addWidget(self.r_arr)

        # blink timer
        self._blink_t = QTimer()
        self._blink_t.setInterval(500)
        self._blink_t.timeout.connect(self._do_blink)
        self._blink_t.start()

    def _ic(self, label, color):
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{color};font-size:8px;font-weight:bold;"
            f"letter-spacing:1px;background:transparent;")
        return lbl

    def _do_blink(self):
        self._blink = not self._blink
        # left arrow
        lc = P["arc_amber"] if (self._left_on and self._blink) else P["bezel_outer"]
        self.l_arr.setStyleSheet(
            f"color:{lc};font-size:15px;font-weight:bold;background:transparent;")
        # right arrow
        rc = P["arc_amber"] if (self._right_on and self._blink) else P["bezel_outer"]
        self.r_arr.setStyleSheet(
            f"color:{rc};font-size:15px;font-weight:bold;background:transparent;")

    def _set_ic(self, widget, color):
        widget.setStyleSheet(
            f"color:{color};font-size:8px;font-weight:bold;"
            f"letter-spacing:1px;background:transparent;")

    def set_temp_warn(self, on):
        self._set_ic(self.ic_temp, P["arc_amber"] if on else P["bezel_outer"])

    def set_engine_warn(self, on):
        self._set_ic(self.ic_engine, P["arc_red"] if on else P["bezel_outer"])


# ─────────────────────────────────────────────────────────────────────────────
#  STAT BAR  — bottom strip
# ─────────────────────────────────────────────────────────────────────────────
class StatBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(f"background:{P['shell_inner']};border-top:1px solid {P['bezel_outer']};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(28)

        self.avg  = self._s("AVG SPEED",  "0 km/h")
        self.top  = self._s("TOP SPEED",  "0 km/h")
        self.co2  = self._s("CO₂ SAVED",  "0.0 kg")
        self.dist = self._s("TRIP DIST",  "0.0 km")
        for w in [self.avg, self.top, self.co2, self.dist]:
            lay.addWidget(w)
        lay.addStretch()

    def _s(self, label, val):
        f  = QFrame(); f.setStyleSheet("background:transparent;border:none;")
        fl = QHBoxLayout(f); fl.setContentsMargins(0,0,0,0); fl.setSpacing(4)
        t  = QLabel(label + ":")
        t.setStyleSheet(f"color:{P['bezel_inner']};font-size:8px;font-weight:bold;background:transparent;")
        v  = QLabel(val)
        v.setStyleSheet(f"color:{P['text_muted']};font-size:9px;font-weight:bold;background:transparent;")
        v.setObjectName("val")
        fl.addWidget(t); fl.addWidget(v)
        return f

    def _set(self, frame, text):
        frame.findChild(QLabel, "val").setText(text)

    def update_stats(self, avg, top, co2, dist):
        self._set(self.avg,  f"{int(avg)} km/h")
        self._set(self.top,  f"{int(top)} km/h")
        self._set(self.co2,  f"{co2:.1f} kg")
        self._set(self.dist, f"{dist:.1f} km")


# ─────────────────────────────────────────────────────────────────────────────
#  OUTER HOUSING WIDGET  — matte charcoal shell with curved contour
# ─────────────────────────────────────────────────────────────────────────────
class ClusterHousing(QWidget):
    """
    Paints a curved dashboard-style housing behind the cluster.
    Asymmetric: wider on the left (analog side), narrower on the right.
    """
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()

        # Outer shell path (asymmetric trapezoid with rounded corners)
        path = QPainterPath()
        pad = 6
        r   = 24
        path.moveTo(pad + r, pad)
        path.lineTo(W - pad - r, pad)
        path.quadTo(W - pad, pad, W - pad, pad + r)
        path.lineTo(W - pad - 10, H - pad - r)          # right side tapers inward
        path.quadTo(W - pad - 10, H - pad, W - pad - 10 - r, H - pad)
        path.lineTo(pad + r, H - pad)
        path.quadTo(pad, H - pad, pad, H - pad - r)
        path.lineTo(pad, pad + r)
        path.quadTo(pad, pad, pad + r, pad)
        path.closeSubpath()

        # Outer shell gradient
        shell_g = QLinearGradient(0, 0, 0, H)
        shell_g.setColorAt(0.0, QColor("#141922"))
        shell_g.setColorAt(0.5, QColor("#0c1016"))
        shell_g.setColorAt(1.0, QColor("#07090d"))
        p.setBrush(QBrush(shell_g))
        p.setPen(QPen(QColor("#1b2430"), 2))
        p.drawPath(path)

        # Top glare stripe
        glare_g = QLinearGradient(0, pad, 0, pad + 18)
        glare_g.setColorAt(0.0, QColor(255, 255, 255, 22))
        glare_g.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glare_g))
        p.drawPath(path)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  VEHICLE STATE ENGINE — realistic scooter dynamics
# ─────────────────────────────────────────────────────────────────────────────
class VehicleState:
    def __init__(self):
        self.speed = 0.0
        self.rpm = 1100.0
        self.fuel = 78.0
        self.temp = 42.0
        self.odometer = 12458.2
        self.trip = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.mode = "ECO"
        self.top_speed = 0.0
        self.avg_speed = 0.0
        self.distance_accumulator = 0.0
        self.sample_count = 0
        self.left_indicator = False
        self.right_indicator = False
        self.hazard = False
        self.side_stand = False
        self.engine_warning = False
        self.temp_warning = False
        self.low_fuel_warning = False
        self.range_km = 0.0
        self.efficiency = 48.0

    def update(self, dt):
        throttle_force = self.throttle * 16.0
        brake_force = self.brake * 28.0
        drag_force = self.speed * 0.018
        acceleration = throttle_force - brake_force - drag_force
        self.speed += acceleration * dt
        if self.speed < 0:
            self.speed = 0
        if self.speed > 140:
            self.speed = 140
        if self.throttle < 0.05 and self.brake < 0.05:
            self.speed *= 0.998

        target_rpm = 1100 + (self.speed * 52)
        if self.throttle > 0.4:
            target_rpm += 900
        self.rpm += (target_rpm - self.rpm) * 0.08

        dist = (self.speed / 3600.0) * dt
        self.odometer += dist
        self.trip += dist

        if self.mode == "ECO":
            base_eff = 56
        elif self.mode == "CITY":
            base_eff = 46
        else:
            base_eff = 34
        throttle_penalty = self.throttle * 10
        speed_penalty = self.speed * 0.05
        self.efficiency = max(
            20,
            base_eff - throttle_penalty - speed_penalty
        )

        fuel_use = (
            self.speed *
            (1.0 / self.efficiency) *
            0.00016 *
            dt
        )
        self.fuel -= fuel_use
        if self.fuel < 0:
            self.fuel = 0

        liters_remaining = (self.fuel / 100.0) * 5.2
        self.range_km = liters_remaining * self.efficiency

        self.temp += (
            (self.speed * 0.008)
            + (self.throttle * 0.04)
        ) * dt
        if self.speed < 10:
            self.temp -= 0.015 * dt
        self.temp = max(38, min(118, self.temp))

        self.temp_warning = self.temp > 95
        self.engine_warning = self.temp > 108
        self.low_fuel_warning = self.fuel < 15

        self.sample_count += 1
        self.distance_accumulator += self.speed
        self.avg_speed = (
            self.distance_accumulator /
            self.sample_count
        )
        if self.speed > self.top_speed:
            self.top_speed = self.speed


# ─────────────────────────────────────────────────────────────────────────────
#  HYBRID CLUSTER  — main widget
# ─────────────────────────────────────────────────────────────────────────────
class HybridCluster(QWidget):
    def __init__(self, energy_model=None):
        super().__init__()
        self.setStyleSheet(f"QWidget{{background:{P['shell_outer']};color:{P['text_primary']};font-family:'Segoe UI';}} QLabel{{background:transparent;}}")

        self._top = 0.0
        self._sum = 0.0
        self._n   = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────
        hdr = QFrame()
        hdr.setFixedHeight(42)
        hdr.setStyleSheet(f"background:{P['shell_inner']};border-bottom:1px solid {P['bezel_outer']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 0, 14, 0)

        logo = QLabel("SUPRAJIT")
        logo.setStyleSheet(f"color:{P['text_primary']};font-size:18px;font-weight:bold;letter-spacing:3px;background:transparent;")

        tag = QLabel("HYBRID CLUSTER")
        tag.setStyleSheet(f"color:{P['text_muted']};font-size:8px;letter-spacing:3px;background:transparent;")

        self.hdr_time = QLabel("--:--")
        self.hdr_time.setStyleSheet(f"color:{P['tick_label']};font-size:12px;font-weight:bold;background:transparent;font-family:'Courier New';")

        live = QLabel("● LIVE")
        live.setStyleSheet(f"color:{P['arc_green']};font-size:8px;font-weight:bold;background:transparent;")

        hl.addWidget(logo)
        hl.addSpacing(8)
        hl.addWidget(tag)
        hl.addStretch()
        hl.addWidget(self.hdr_time)
        hl.addSpacing(12)
        hl.addWidget(live)
        root.addWidget(hdr)

        # ── Indicator strip ───────────────────────────────────────
        self.ind = IndicatorStrip()
        root.addWidget(self.ind)

        # ── Housing + main body ───────────────────────────────────
        housing = ClusterHousing()
        housing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hl2 = QHBoxLayout(housing)
        hl2.setContentsMargins(14, 12, 14, 10)
        hl2.setSpacing(16)

        # Left 62%: analog speedo
        self.speedo = SpeedometerWidget()
        hl2.addWidget(self.speedo, 62)

        # Right 38%: LCD panel
        self.lcd = LCDPanel()
        hl2.addWidget(self.lcd, 38)

        root.addWidget(housing, 1)

        # ── Stat bar ──────────────────────────────────────────────
        self.stat_bar = StatBar()
        root.addWidget(self.stat_bar)

        # ── Timers ────────────────────────────────────────────────
        self._clk = QTimer()
        self._clk.timeout.connect(self._tick_clock)
        self._clk.start(1000)
        self._tick_clock()

        self._loc_t = QTimer()
        self._loc_t.timeout.connect(_Loc.fetch)
        self._loc_t.start(300_000)

        # ── Vehicle Engine ────────────────────────────────────────
        self.initialize_vehicle_engine()
        self.setFocusPolicy(Qt.StrongFocus)

    def _tick_clock(self):
        self.hdr_time.setText(datetime.now().strftime("%I:%M %p"))

    def initialize_vehicle_engine(self):
        self.vehicle = VehicleState()
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.vehicle_tick)
        self.physics_timer.start(16)
        self.boot_animation()

    def boot_animation(self):
        self.boot_stage = 0

        def animate():
            if self.boot_stage < 140:
                self.speedo.set_speed(self.boot_stage)
                self.boot_stage += 4
            elif self.boot_stage < 280:
                self.speedo.set_speed(280 - self.boot_stage)
                self.boot_stage += 4
            else:
                boot.stop()

        boot = QTimer()
        boot.timeout.connect(animate)
        boot.start(10)

    def vehicle_tick(self):
        dt = 0.016
        self.vehicle.update(dt)
        v = self.vehicle
        self.set_data(
            v.speed,
            v.fuel,
            v.temp,
            v.rpm,
            v.odometer,
            v.trip
        )
        self.lcd.range_val.setText(
            f"{int(v.range_km)} km"
        )
        self.stat_bar.update_stats(
            v.avg_speed,
            v.top_speed,
            v.trip * 0.12,
            v.trip
        )
        self.ind.set_temp_warn(v.temp_warning)
        self.ind.set_engine_warn(v.engine_warning)
        self.ind._left_on = v.left_indicator
        self.ind._right_on = v.right_indicator

    def set_data(self, speed, fuel, temp, rpm, odo, trip):
        self.speedo.set_speed(speed)
        self.speedo.set_fuel(fuel)
        self.lcd.update_data(speed, fuel, temp, odo, trip)
        self.ind.set_temp_warn(temp > 85)
        self.ind.set_engine_warn(temp > 100)

        if speed > self._top:
            self._top = speed
        self._sum += speed
        self._n   += 1
        avg = self._sum / self._n if self._n else 0
        self.stat_bar.update_stats(avg, self._top, trip * 0.12, trip)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Up:
            self.vehicle.throttle = 1.0
        if e.key() == Qt.Key_Down:
            self.vehicle.brake = 1.0
        if e.key() == Qt.Key_Left:
            self.vehicle.left_indicator = not self.vehicle.left_indicator
        if e.key() == Qt.Key_Right:
            self.vehicle.right_indicator = not self.vehicle.right_indicator
        if e.key() == Qt.Key_1:
            self.vehicle.mode = "ECO"
        if e.key() == Qt.Key_2:
            self.vehicle.mode = "CITY"
        if e.key() == Qt.Key_3:
            self.vehicle.mode = "SPORT"

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Up:
            self.vehicle.throttle = 0.0
        if e.key() == Qt.Key_Down:
            self.vehicle.brake = 0.0

    def update_cluster(self, speed, fuel):
        pass


HybridClusterWidget = HybridCluster