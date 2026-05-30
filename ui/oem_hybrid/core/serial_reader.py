import serial
import threading
import json


class SerialReader:

    def __init__(self, port="COM8", baud=115200):

        self.value = 0
        self.percent = 0

        self.ax = 0
        self.ay = 0
        self.az = 0

        self.json_data = {}

        self.connected = False

        try:

            self.serial = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=1
            )

            self.connected = True

            print()
            print("=================================")
            print("SERIAL READER STARTED")
            print(f"PORT : {port}")
            print(f"BAUD : {baud}")
            print("=================================")
            print()

        except Exception as e:

            print()
            print("=================================")
            print("SERIAL CONNECTION FAILED")
            print(f"PORT : {port}")
            print(f"ERROR: {e}")
            print("=================================")
            print()

            self.serial = None
            return

        self.thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )

        self.thread.start()

    def _read_loop(self):

        while True:

            try:

                if self.serial is None:
                    break

                if not self.serial.is_open:
                    break

                line = (
                    self.serial
                    .readline()
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                    .strip()
                )

                if line:
                    print("RAW:", repr(line))

                if not line:
                    continue

                if line.startswith("{"):

                    try:

                        data = json.loads(line)

                        self.json_data = data

                        self.value = int(
                            data.get(
                                "adc",
                                0
                            )
                        )

                        self.percent = int(
                            data.get(
                                "percent",
                                0
                            )
                        )

                        self.ax = int(
                            data.get(
                                "ax",
                                0
                            )
                        )

                        self.ay = int(
                            data.get(
                                "ay",
                                0
                            )
                        )

                        self.az = int(
                            data.get(
                                "az",
                                0
                            )
                        )

                        print(
                            f"ADC={self.value} "
                            f"PERCENT={self.percent}"
                        )

                    except Exception as e:

                        print(
                            f"[JSON ERROR] {e}"
                        )

            except Exception as e:

                print(
                    f"[SERIAL READ ERROR] {e}"
                )