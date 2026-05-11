from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.oem.cluster_shell import ClusterShell
from ui.oem.glass_layer   import GlassLayer
from ui.oem.tft_screen    import TFTScreen


class DigitalCluster(QWidget):

    def __init__(self, energy_model=None):
        super().__init__()

        # State
        self.speed  = 0.0
        self.fuel   = 80.0
        self.temp   = 45.0
        self.odo    = 0.0
        self.trip_a = 0.0
        self.trip_b = 0.0

        # Layers
        self.shell = ClusterShell(self)
        self.glass = GlassLayer(self.shell)
        self.tft   = TFTScreen(self.shell)

        # Layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.shell)

    def resizeEvent(self, e):
        self.shell.resize(self.size())
        self.glass.resize(self.shell.size())
        self.tft.resize(self.shell.size())
        self._push()

    def _push(self):
        t = self.tft
        t.speed  = self.speed
        t.fuel   = self.fuel
        t.temp   = self.temp
        t.odo    = self.odo
        t.trip_a = self.trip_a
        t.trip_b = self.trip_b
        t.sync()

    # ── Called by main_window physics tick ──────────────────────
    def set_data(self, speed, fuel, temp, rpm, odo, trip):
        # Block throttle while charging
        if self.tft.charging:
            speed = 0.0
        self.speed  = speed
        self.fuel   = fuel
        self.temp   = temp
        self.odo    = odo
        self.trip_a = trip
        self._push()

    def update_cluster(self, speed, battery):
        self.set_data(speed, battery, 45, 0, self.odo, self.trip_a)


DigitalClusterWidget = DigitalCluster