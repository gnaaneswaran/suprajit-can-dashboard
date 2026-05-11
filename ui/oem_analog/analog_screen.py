import math

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ui.oem_analog.widgets.speed_arc import draw_speed_arcs
from ui.oem_analog.widgets.speed_ticks import draw_speed_ticks
from ui.oem_analog.widgets.speed_needle import (
    draw_needle,
    draw_hub,
    NeedlePhysics
)

from ui.oem_analog.widgets.odo_display import OdoDisplay


class AnalogScreen(QWidget):

    def __init__(self):

        super().__init__()

        self.speed = 0.0
        self.fuel = 82.0

        self.odo_value = 12458.0
        self.trip_value = 0.0

        self.needle = NeedlePhysics()

        self.odo = OdoDisplay()

        self.setMinimumSize(900, 600)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    # ─────────────────────────────

    def set_speed(self, v):

        self.speed = v

    def set_fuel(self, v):

        self.fuel = v

    def set_odo(self, v):

        self.odo_value = v

    def set_trip(self, v):

        self.trip_value = v

    # ─────────────────────────────

    def paintEvent(self, e):

        p = QPainter(self)

        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # background

        bg = QLinearGradient(
            0,
            0,
            0,
            h
        )

        bg.setColorAt(0, QColor("#10151d"))
        bg.setColorAt(1, QColor("#05070a"))

        p.fillRect(self.rect(), bg)

        # dial

        cx = w / 2
        cy = h / 2 - 20

        R = min(w, h) * 0.33

        dial_grad = QRadialGradient(
            cx,
            cy,
            R
        )

        dial_grad.setColorAt(0, QColor("#1d1d1d"))
        dial_grad.setColorAt(1, QColor("#050505"))

        p.setPen(QPen(QColor("#1f2d3c"), 8))

        p.setBrush(dial_grad)

        p.drawEllipse(
            QPointF(cx, cy),
            R,
            R
        )

        # arcs

        draw_speed_arcs(
            p,
            cx,
            cy,
            R
        )

        # ticks

        draw_speed_ticks(
            p,
            cx,
            cy,
            R
        )

        # animated needle

        smooth_speed = self.needle.tick(
            self.speed
        )

        draw_needle(
            p,
            cx,
            cy,
            R,
            smooth_speed
        )

        # hub

        draw_hub(
            p,
            cx,
            cy
        )

        # odometer

        self.odo.set_odo(
            self.odo_value
        )

        self.odo.draw(
            p,
            cx - 85,
            cy + 60
        )

        # fuel gauge

        self.draw_fuel(
            p,
            120,
            h - 150
        )

        # trip info

        self.draw_trip(
            p,
            220,
            h - 145
        )

    # ─────────────────────────────

    def draw_fuel(self, p, x, y):

        p.setPen(QPen(QColor("#dfe7ef"), 2))

        p.drawArc(
            QRectF(
                x,
                y,
                110,
                110
            ),
            30 * 16,
            120 * 16
        )

        angle = 30 + (
            (100 - self.fuel) * 1.2
        )

        rad = math.radians(angle)

        cx = x + 55
        cy = y + 55

        nx = cx + math.cos(rad) * 42
        ny = cy - math.sin(rad) * 42

        p.setPen(
            QPen(
                QColor("#ff4040"),
                4
            )
        )

        p.drawLine(
            QPointF(cx, cy),
            QPointF(nx, ny)
        )

        p.setPen(QColor("#ff4040"))

        p.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Bold
            )
        )

        p.drawText(
            x - 5,
            y + 90,
            "E"
        )

        p.setPen(QColor("#dfe7ef"))

        p.drawText(
            x + 90,
            y + 90,
            "F"
        )

    # ─────────────────────────────

    def draw_trip(self, p, x, y):

        p.setPen(QColor("#dfe7ef"))

        p.setFont(
            QFont(
                "Segoe UI",
                12
            )
        )

        p.drawText(
            x,
            y,
            f"TRIP A: {self.trip_value:.1f} km"
        )

        p.drawText(
            x,
            y + 28,
            f"RANGE: {int(self.fuel * 2.8)} km"
        )

        p.drawText(
            x,
            y + 56,
            f"ENG TEMP: {45 + int(self.speed * 0.8)}°C"
        )

        p.drawText(
            x,
            y + 84,
            f"RPM: {int(1200 + self.speed * 75)}"
        )