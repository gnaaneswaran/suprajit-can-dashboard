from datetime import datetime


class VehicleState:

    def __init__(self):

        # ── Motion ──────────────────────────────────
        self.speed          = 62.0
        self.rpm            = 3200

        # ── Battery / Range ─────────────────────────
        self.battery        = 78.0       # 0–100 %
        self.range_km       = 85.0
        self.charging       = False

        # ── Riding Mode ─────────────────────────────
        self.ride_mode      = "SMART ECO"
        self.ride_mode_label = "ECO"

        # ── Trips ────────────────────────────────────
        self.trip_a         = 32.4
        self.trip_b         = 0.0
        self.odo            = 1254.0

        # ── Motor ────────────────────────────────────
        self.motor_on       = True
        self.motor_fault    = False

        # ── Indicators / Warnings ────────────────────
        self.left_indicator  = False
        self.right_indicator = False
        self.high_beam       = False
        self.side_stand_down = True
        self.overheat        = False
        self.brake_warning   = False

        # ── Connectivity ─────────────────────────────
        self.bluetooth      = True
        self.wifi           = False
        self.mobile_signal  = 3          # 0–4 bars

        # ── Navigation ───────────────────────────────
        self.nav_active          = False
        self.next_turn           = "Head southeast"
        self.distance_to_turn    = "120 m"
        self.eta_time            = "12:44 PM"
        self.total_nav_distance  = "4.2 km"
        self.nav_duration        = "12 min"

        # ── Clock ─────────────────────────────────────
        self.time_string    = datetime.now().strftime("%I:%M %p")

        # ── Ride Statistics ───────────────────────────
        self.stat_distance       = 32.4
        self.stat_avg_speed      = 42.0
        self.stat_avg_efficiency = 34.0
        self.stat_top_speed      = 78.0

        # ── Settings ──────────────────────────────────
        self.brightness     = 80
        self.unit_kmh       = True
        self.unit_celsius   = True

        # ── Park Assist ───────────────────────────────
        self.park_assist_active = False

    def update_from_dict(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)