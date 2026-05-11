class VehicleModel:
    def __init__(self):
        self.speed    = 0.0
        self.fuel     = 100.0
        self.temp     = 45.0
        self.rpm      = 800.0
        self.odometer = 0.0
        self.trip     = 0.0

        self.throttle = 0.0
        self.brake    = 0.0

        self._tick        = 0
        self._fuel_ticks  = 0   # counts ticks before draining 1%
        # ~10 s at 80 ms/tick = 125 ticks per drain event
        self.FUEL_DRAIN_TICKS = 125   # drain 1% every 10 s idle; less under throttle

    def update(self, dt=0.08):
        self._tick += 1

        # ── RPM ──────────────────────────────────────────────────
        rpm_target = 800 + self.throttle * 7200 + (self.speed / 140) * 2000
        self.rpm  += (rpm_target - self.rpm) * 0.12
        self.rpm   = max(700, min(8500, self.rpm))

        # ── SPEED ─────────────────────────────────────────────────
        drive_force  = self.throttle * 28.0
        drag         = 0.004 * self.speed ** 1.6
        engine_brake = (1.0 - self.throttle) * 0.6
        brake_force  = self.brake * 22.0

        accel      = drive_force - drag - engine_brake - brake_force
        self.speed += accel * dt * 10
        self.speed  = max(0.0, min(140.0, self.speed))

        # ── ODOMETER / TRIP ───────────────────────────────────────
        dist = self.speed * dt / 3600.0
        self.odometer += dist
        self.trip     += dist

        # ── FUEL — very slow drain ────────────────────────────────
        # Base: 1% per 10 s (125 ticks). Heavy throttle doubles drain rate.
        rate = self.FUEL_DRAIN_TICKS * (1.0 - self.throttle * 0.5)
        self._fuel_ticks += 1
        if self._fuel_ticks >= rate:
            self.fuel        = max(0.0, self.fuel - 1.0)
            self._fuel_ticks = 0

        # ── ENGINE TEMP ───────────────────────────────────────────
        target    = 45 + (self.rpm - 800) / 7200 * 75
        self.temp += (target - self.temp) * 0.015
        self.temp  = max(40.0, min(115.0, self.temp))

        return {
            "speed":    round(self.speed, 1),
            "fuel":     round(self.fuel,  1),
            "temp":     round(self.temp,  1),
            "rpm":      round(self.rpm,   0),
            "odometer": round(self.odometer, 2),
            "trip":     round(self.trip,     2),
        }
