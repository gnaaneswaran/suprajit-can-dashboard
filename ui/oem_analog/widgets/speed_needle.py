import math

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QRadialGradient,
    QPolygonF
)

from PyQt5.QtCore import Qt, QPointF, QRectF


class NeedlePhysics:

    def __init__(self):
        self.value = 0.0
        self.velocity = 0.0

        self.stiffness = 0.12
        self.damping = 0.82

    def tick(self, target):

        force = (target - self.value) * self.stiffness

        self.velocity += force
        self.velocity *= self.damping

        self.value += self.velocity

        return self.value


def speed_to_angle(speed, max_speed=120):

    return 220 - ((speed / max_speed) * 260)


def draw_needle(p, cx, cy, R, speed, max_speed=120):

    angle = math.radians(
        speed_to_angle(speed, max_speed)
    )

    needle_len = R * 0.78

    x = cx + math.cos(angle) * needle_len
    y = cy - math.sin(angle) * needle_len

    tail_x = cx - math.cos(angle) * 18
    tail_y = cy + math.sin(angle) * 18

    left_x = cx + math.cos(angle + math.pi/2) * 6
    left_y = cy - math.sin(angle + math.pi/2) * 6

    right_x = cx + math.cos(angle - math.pi/2) * 6
    right_y = cy - math.sin(angle - math.pi/2) * 6

    poly = QPolygonF([
        QPointF(tail_x, tail_y),
        QPointF(left_x, left_y),
        QPointF(x, y),
        QPointF(right_x, right_y),
    ])

    glow = QColor("#ff3030")
    glow.setAlpha(90)

    p.setPen(Qt.NoPen)

    p.setBrush(QBrush(glow))
    p.drawPolygon(poly)

    p.setBrush(QBrush(QColor("#ff2020")))
    p.drawPolygon(poly)

    p.setPen(QPen(QColor("#ff9090"), 1))
    p.drawLine(
        QPointF(cx, cy),
        QPointF(x, y)
    )


def draw_hub(p, cx, cy):

    p.setPen(Qt.NoPen)

    outer = QRadialGradient(cx - 4, cy - 4, 24)

    outer.setColorAt(0, QColor("#3a3a3a"))
    outer.setColorAt(1, QColor("#090909"))

    p.setBrush(QBrush(outer))

    p.drawEllipse(
        QRectF(
            cx - 24,
            cy - 24,
            48,
            48
        )
    )

    inner = QRadialGradient(cx - 2, cy - 2, 10)

    inner.setColorAt(0, QColor("#505050"))
    inner.setColorAt(1, QColor("#101010"))

    p.setBrush(QBrush(inner))

    p.drawEllipse(
        QRectF(
            cx - 10,
            cy - 10,
            20,
            20
        )
    )