from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QSizePolicy, QPushButton)
from PyQt5.QtGui     import QPainter, QColor, QLinearGradient, QPen, QBrush, QPainterPath
from PyQt5.QtCore    import Qt, QRectF, QTimer

from ui.oem.widgets.indicator_strip import IndicatorStrip
from ui.oem.widgets.fuel_bar        import FuelBar
from ui.oem.widgets.speed_display   import SpeedDisplay
from ui.oem.widgets.trip_panel      import TripPanel
from ui.oem.widgets.odo_strip       import OdoStrip
from ui.oem.widgets.warning_strip   import WarningStrip


# ── Thin vertical separator ───────────────────────────────────────
class _Sep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(1)
    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(255,255,255,18))
        p.end()


class TFTScreen(QWidget):
    """
    Assembles the TFT display area using proper layouts —
    no manual coordinate drawing for child widgets.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ── State ────────────────────────────────────────────────
        self.speed      = 0.0
        self.fuel       = 80.0    # 0-100 %
        self.temp       = 45.0
        self.odo        = 0.0
        self.trip_a     = 0.0
        self.trip_b     = 0.0
        self.side_stand = False
        self.charging   = False
        self._charge_pct = 0.0
        self._charge_target = 100.0

        # ── Outer margin matches bezel radius ────────────────────
        M = 72
        outer = QVBoxLayout(self)
        outer.setContentsMargins(M, M, M, M)
        outer.setSpacing(0)

        # ── Indicator strip ──────────────────────────────────────
        self.indicators = IndicatorStrip()
        outer.addWidget(self.indicators)

        # ── Middle row ───────────────────────────────────────────
        mid = QHBoxLayout()
        mid.setContentsMargins(0, 0, 0, 0)
        mid.setSpacing(0)

        self.fuel_bar   = FuelBar()
        self.speed_disp = SpeedDisplay()
        self.trip_panel = TripPanel()

        mid.addWidget(self.fuel_bar,   0)
        mid.addWidget(_Sep(),          0)
        mid.addWidget(self.speed_disp, 1)
        mid.addWidget(_Sep(),          0)
        mid.addWidget(self.trip_panel, 0)

        outer.addLayout(mid, 1)

        # ── ODO strip ────────────────────────────────────────────
        self.odo_strip = OdoStrip()
        outer.addWidget(self.odo_strip)

        # ── Warning / charge strip ───────────────────────────────
        self.warn_strip = WarningStrip()
        outer.addWidget(self.warn_strip)

        # ── Charge button (shown when not driving) ───────────────
        self.charge_btn = QPushButton("⚡  CHARGE")
        self.charge_btn.setFixedHeight(28)
        self.charge_btn.setStyleSheet("""
            QPushButton {
                background:#102040;
                color:#22aaff;
                border:1px solid #224488;
                border-radius:6px;
                font-family:'Rajdhani';
                font-size:12px;
                font-weight:bold;
            }
            QPushButton:hover { background:#1a3060; }
            QPushButton:disabled { color:#2a3a4a; border-color:#162030; }
        """)
        self.charge_btn.clicked.connect(self._start_charge)
        outer.addWidget(self.charge_btn)

        # ── Charge animation timer ───────────────────────────────
        self._charge_timer = QTimer(self)
        self._charge_timer.setInterval(100)    # 100ms = 10s total for 100 steps
        self._charge_timer.timeout.connect(self._charge_tick)

        # ── Clock refresh ─────────────────────────────────────────
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self.trip_panel.update)
        self._clock_timer.start(1000)

    # ── Charge logic ──────────────────────────────────────────────
    def _start_charge(self):
        if self.speed > 0 or self.charging:
            return
        self.charging      = True
        self._charge_pct   = self.fuel
        self.charge_btn.setEnabled(False)
        self._charge_timer.start()
        self._push()

    def _charge_tick(self):
        step = (100.0 - self._charge_pct) / 90   # reach 100 in ~9s
        self._charge_pct = min(100.0, self._charge_pct + step)
        self.fuel = self._charge_pct
        if self._charge_pct >= 99.9:
            self.fuel      = 100.0
            self.charging  = False
            self._charge_timer.stop()
            self.charge_btn.setEnabled(True)
        self._push()

    # ── Sync all child widgets ────────────────────────────────────
    def sync(self):
        self._push()

    def _push(self):
        self.fuel_bar.set_fuel(self.fuel)
        self.speed_disp.set_speed(self.speed)
        range_km = int((self.fuel / 100.0) * 80)   # 80 km full range
        self.trip_panel.set_data(self.trip_a, self.trip_b, range_km, self.temp)
        self.odo_strip.set_odo(self.odo, max(0, 1520 - int(self.odo)))
        self.warn_strip.set_state(
            side_stand=self.side_stand,
            charging=self.charging,
            charge_pct=int(self._charge_pct)
        )
        self.indicators.update_state(
            eco=self.speed < 45,
            engine=self.temp > 88,
            charging=self.charging
        )
        self.charge_btn.setEnabled(not self.charging and self.speed == 0)

    # ── Screen background (draws behind child widgets) ────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        M  = 64
        w, h = self.width(), self.height()
        rect = QRectF(M, M, w - M*2, h - M*2)

        bg = QLinearGradient(0, rect.top(), 0, rect.bottom())
        bg.setColorAt(0.0, QColor("#0e1318"))
        bg.setColorAt(1.0, QColor("#06080b"))
        path = QPainterPath()
        path.addRoundedRect(rect, 22, 22)
        p.fillPath(path, QBrush(bg))

        p.setPen(QPen(QColor(255, 255, 255, 28), 1.5))
        p.drawPath(path)
        p.end()