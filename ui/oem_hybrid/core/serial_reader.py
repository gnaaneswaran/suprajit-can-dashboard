import serial
import threading


class SerialReader:

    def __init__(self, port='COM7', baud=115200):

        self.value = 0    # potentiometer ADC (0–1023)
        self.ax = 0       # MPU6050 X acceleration
        self.ay = 0       # MPU6050 Y acceleration
        self.az = 0       # MPU6050 Z acceleration

        try:
            self.serial = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            print(f"[SerialReader] Could not open {port}: {e}")
            self.serial = None
            return

        self.thread = threading.Thread(
            target=self.read_loop,
            daemon=True
        )
        self.thread.start()

    def read_loop(self):

        while True:

            try:

                if self.serial is None:
                    break

                line = (
                    self.serial
                    .readline()
                    .decode('utf-8', errors='ignore')
                    .strip()
                )

                parts = line.split(",")

                if len(parts) == 4:
                    self.value = int(parts[0])
                    self.ax    = int(parts[1])
                    self.ay    = int(parts[2])
                    self.az    = int(parts[3])

            except Exception:
                pass