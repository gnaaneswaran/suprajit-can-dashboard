"""
digital_cluster.py  —  drop-in replacement
Reads live data from core.fake_data.model every paint cycle.
Full dropdown + screen navigation wired in.
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from core.fake_data import model
from ui.oem_digital.screens.home_screen import HomeScreen
from ui.oem_digital.screens.menu_screen import MenuScreen
from ui.oem_digital.screens.ride_stats_screen import RideStatsScreen
from ui.oem_digital.screens.navigation_screen import NavigationScreen
from ui.oem_digital.screens.vehicle_screen import VehicleScreen
from ui.oem_digital.screens.settings_screen import SettingsScreen
from ui.oem_digital.screens.bluetooth_screen import BluetoothScreen


# ── Thin adapter: wraps model and exposes HomeScreen-compatible attributes ────
class _ModelAdapter:

    @property
    def speed(self):
        return getattr(model, "speed", 0.0)

    @property
    def battery(self):
        return getattr(model, "fuel", 78.0)

    @property
    def range_km(self):
        return max(0.0, round(self.battery * (85.0 / 100.0), 1))

    @property
    def odo(self):
        return getattr(model, "odometer", 1254.0)

    @property
    def trip_a(self):
        return getattr(model, "trip", 32.4)

    @property
    def ride_mode(self):
        return getattr(model, "ride_mode", "SMART ECO")

    @property
    def ride_mode_label(self):
        return getattr(model, "ride_mode_label", "ECO")

    @property
    def time_string(self):
        from datetime import datetime
        return datetime.now().strftime("%I:%M %p").lstrip("0")

    @property
    def mobile_signal(self):
        return getattr(model, "mobile_signal", 3)

    @property
    def bluetooth(self):
        return getattr(model, "bluetooth", True)

    @property
    def motor_on(self):
        return getattr(model, "throttle", False) or (self.speed > 0)

    @property
    def side_stand_down(self):
        return self.speed < 1.0 and getattr(model, "_side_stand", True)

    # ── Writable toggle properties (dropdown writes to model directly) ────────

    @property
    def left_indicator(self):
        return getattr(model, "left_indicator", False)

    @left_indicator.setter
    def left_indicator(self, v):
        model.left_indicator = v

    @property
    def right_indicator(self):
        return getattr(model, "right_indicator", False)

    @right_indicator.setter
    def right_indicator(self, v):
        model.right_indicator = v

    @property
    def high_beam(self):
        return getattr(model, "high_beam", False)

    @high_beam.setter
    def high_beam(self, v):
        model.high_beam = v

    @property
    def park_assist_active(self):
        return getattr(model, "park_assist_active", False)

    @park_assist_active.setter
    def park_assist_active(self, v):
        model.park_assist_active = v

    # ── Ride stats (for RideStatsScreen) ─────────────────────────────────────

    @property
    def stat_distance(self):
        return getattr(model, "trip", 32.4)

    @property
    def stat_avg_speed(self):
        return getattr(model, "stat_avg_speed", 42.0)

    @property
    def stat_avg_efficiency(self):
        return getattr(model, "stat_avg_efficiency", 34.0)

    @property
    def stat_top_speed(self):
        return getattr(model, "stat_top_speed", 78.0)

    # ── Navigation (for NavigationScreen) ────────────────────────────────────

    @property
    def next_turn(self):
        return getattr(model, "next_turn", "Head southeast")

    @property
    def distance_to_turn(self):
        return getattr(model, "distance_to_turn", "120 m")

    @property
    def eta_time(self):
        return getattr(model, "eta_time", "12:44 PM")

    @property
    def total_nav_distance(self):
        return getattr(model, "total_nav_distance", "4.2 km")

    @property
    def nav_duration(self):
        return getattr(model, "nav_duration", "12 min")

    # ── Settings (for SettingsScreen) ────────────────────────────────────────

    @property
    def brightness(self):
        return getattr(model, "brightness", 80)

    @property
    def wifi(self):
        return getattr(model, "wifi", False)


_adapter = _ModelAdapter()


# ── Minimal ScreenManager (no external import needed) ────────────────────────
class _ScreenManager:

    def __init__(self):
        self.current_screen = "home"
        self._history = []

    def switch(self, screen):
        self._history.append(self.current_screen)
        self.current_screen = screen

    def back(self):
        if self._history:
            self.current_screen = self._history.pop()


class DigitalClusterWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._home   = HomeScreen()
        self._sm     = _ScreenManager()

        self._screens = {
            "home":       self._home,
            "menu":       MenuScreen(),
            "ride_stats": RideStatsScreen(),
            "navigation": NavigationScreen(),
            "vehicle":    VehicleScreen(),
            "settings":   SettingsScreen(),
            "bluetooth":  BluetoothScreen(),
        }

        # Menu row → screen name mapping (rows start y=67, height=78)
        self._menu_destinations = [
            "ride_stats",
            "navigation",
            "vehicle",
            "settings",
            "bluetooth",
        ]

        # Legacy shims — main_window.py sets these; we accept but use model live
        self.speed = 0.0
        self.fuel  = 100.0
        self.temp  = 40.0
        self.odo   = 0.0
        self.trip  = 0.0

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        screen = self._screens.get(self._sm.current_screen, self._home)
        screen.render(p, _adapter)
        p.end()

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        current = self._sm.current_screen

        if current == "home":
            self._home.handle_click(x, y, _adapter, self._sm)

        else:
            # Back arrow — all sub-screens put it at x<80, y>520
            if x < 80 and y > 520:
                self._sm.back()

            elif current == "menu":
                self._handle_menu_click(x, y)

        self.update()

    def _handle_menu_click(self, x, y):
        # Rows are inside card x=70–948, starting y=67, each 78px tall
        if not (70 <= x <= 948):
            return
        idx = (y - 67) // 78
        if 0 <= idx < len(self._menu_destinations):
            self._sm.switch(self._menu_destinations[idx])