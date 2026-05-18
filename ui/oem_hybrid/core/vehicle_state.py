class VehicleState:

    def __init__(self):

        self.speed = 0
        self.rpm = 0
        self.fuel = 100
        self.engine_temp = 40
        self.temp = 40

        self.throttle = 0
        self.brake = 0

        self.odo = 12458.3
        self.odometer = 12458.3
        self.trip = 0.1
        self.range_km = 268

        self.avg_speed = 0.0
        self.top_speed = 0.0
        self.temp_warning = False
        self.engine_warning = False

        self.eco_mode = True

        self.left_indicator = False
        self.right_indicator = False
        self.high_beam = False

        self.side_stand = False
        self.motor_on = True