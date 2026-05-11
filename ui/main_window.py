# ─────────────────────────────────────────────────────────────
# FILE: ui/main_window.py
# FULL WORKING VERSION WITH HYBRID CLUSTER + _tick FIX
# ─────────────────────────────────────────────────────────────

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit,
    QHeaderView, QStackedWidget
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui  import QColor

from core.fake_data import fake_data_generator, model
from core.decoder   import decode

from ui.controls_panel  import ControlsPanel
from ui.digital_cluster import DigitalClusterWidget
from ui.analog_cluster  import AnalogClusterWidget
from ui.hybrid_cluster  import HybridClusterWidget


STYLE = """
QMainWindow, QWidget {
    background-color: #08101e;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
}

#headerBar {
    background-color: #060c18;
    border-bottom: 1px solid #1e293b;
}

#brandLabel {
    color: #38bdf8;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 3px;
    padding-left: 16px;
}

#appLabel {
    color: #334155;
    font-size: 10px;
    letter-spacing: 2px;
    padding-left: 4px;
}

#viewBtn {
    background-color: #0f172a;
    color: #475569;
    padding: 5px 14px;
    border-radius: 5px;
    border: 1px solid #1e293b;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

#viewBtn:checked {
    background-color: #0ea5e9;
    color: white;
    border: 1px solid #0ea5e9;
}

#clusterBar {
    background: transparent;
    border-bottom: 1px solid #0f172a;
}

#clusterTag {
    color: #1e3a5f;
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 2px;
}

#liveTag {
    color: #22c55e;
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 1px;
}

QTableWidget {
    background-color: #0a0f1e;
    gridline-color: #1e293b;
    border: none;
    font-size: 11px;
    selection-background-color: #1e3a5f;
}

QTableWidget::item {
    padding: 3px 8px;
    border-bottom: 1px solid #0f172a;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #475569;
    font-size: 9px;
    font-weight: bold;
    padding: 5px 8px;
    border: none;
    border-right: 1px solid #1e293b;
}

#statusBar {
    background-color: #060c18;
    border-top: 1px solid #1e293b;
}

#statusLabel {
    color: #334155;
    font-size: 9px;
}

#statusValue {
    color: #38bdf8;
    font-size: 10px;
    font-weight: bold;
}

#ctrlPanel {
    background-color: #060a14;
    border-left: 1px solid #1e293b;
}
"""

ROW_COLORS = {
    "0x100": ("#0e2a3a", "#38bdf8"),
    "0x200": ("#2a1f0a", "#f59e0b"),
    "0x300": ("#2a0f0f", "#f87171"),
}


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Suprajit CAN Bus Analyzer")
        self.setMinimumSize(1280, 760)
        self.setStyleSheet(STYLE)

        self.data_gen = fake_data_generator()

        self.signal_state = {
            "speed": 0,
            "fuel": 100,
            "temp": 40
        }

        self._running = False
        self._filter_id = ""
        self._row_limit = 200

        self._physics_timer = QTimer()
        self._physics_timer.setInterval(30)
        self._physics_timer.timeout.connect(self._physics_tick)

        self._build_ui()

        self._start()

    # ─────────────────────────────────────────

    def _build_ui(self):

        root = QWidget()

        self.setCentralWidget(root)

        root_lay = QVBoxLayout(root)

        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        root_lay.addWidget(self._make_header())

        body = QHBoxLayout()

        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._make_centre_area(), 1)
        body.addWidget(self._make_controls_panel())

        body_widget = QWidget()
        body_widget.setLayout(body)

        root_lay.addWidget(body_widget, 1)

        root_lay.addWidget(self._make_bottom_bar())

    # ─────────────────────────────────────────

    def _make_header(self):

        bar = QWidget()

        bar.setObjectName("headerBar")
        bar.setFixedHeight(44)

        lay = QHBoxLayout(bar)

        brand = QLabel("SUPRAJIT")
        brand.setObjectName("brandLabel")

        app = QLabel("CAN BUS ANALYZER")
        app.setObjectName("appLabel")

        lay.addWidget(brand)
        lay.addWidget(app)

        lay.addStretch()

        self.btn_table = QPushButton("▦ TABLE VIEW")
        self.btn_cluster = QPushButton("⊙ CLUSTER VIEW")

        for btn in [self.btn_table, self.btn_cluster]:
            btn.setObjectName("viewBtn")
            btn.setCheckable(True)

        self.btn_cluster.setChecked(True)

        self.btn_table.clicked.connect(
            lambda: self._switch_view(0)
        )

        self.btn_cluster.clicked.connect(
            lambda: self._switch_view(1)
        )

        lay.addWidget(self.btn_table)
        lay.addWidget(self.btn_cluster)

        return bar

    # ─────────────────────────────────────────

    def _make_centre_area(self):

        w = QWidget()

        lay = QVBoxLayout(w)

        sub = QWidget()

        sub.setObjectName("clusterBar")
        sub.setFixedHeight(26)

        sl = QHBoxLayout(sub)

        t1 = QLabel("INSTRUMENT CLUSTER")
        t1.setObjectName("clusterTag")

        t2 = QLabel("● LIVE DATA")
        t2.setObjectName("liveTag")

        sl.addWidget(t1)
        sl.addStretch()
        sl.addWidget(t2)

        lay.addWidget(sub)

        self.stack = QStackedWidget()

        self.stack.addWidget(self._make_table_page())
        self.stack.addWidget(self._make_cluster_page())

        self.stack.setCurrentIndex(1)

        lay.addWidget(self.stack, 1)

        return w

    # ─────────────────────────────────────────

    def _make_table_page(self):

        w = QWidget()

        lay = QVBoxLayout(w)

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "TIMESTAMP",
            "CAN ID",
            "DLC",
            "DATA"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.Stretch
        )

        lay.addWidget(self.table)

        filter_bar = QWidget()

        fl = QHBoxLayout(filter_bar)

        self.filter_edit = QLineEdit()

        self.filter_edit.setPlaceholderText(
            "Filter by CAN ID"
        )

        self.filter_edit.textChanged.connect(
            lambda t: setattr(self, '_filter_id', t.strip())
        )

        fl.addWidget(self.filter_edit)

        lay.addWidget(filter_bar)

        return w

    # ─────────────────────────────────────────

    def _make_cluster_page(self):

        w = QWidget()

        lay = QVBoxLayout(w)

        tabs = QTabWidget()

        self.digital_cluster = DigitalClusterWidget()
        self.analog_cluster  = AnalogClusterWidget()
        self.hybrid_cluster  = HybridClusterWidget()

        tabs.addTab(self.digital_cluster, "⬡ DIGITAL")
        tabs.addTab(self.analog_cluster,  "◎ ANALOG")
        tabs.addTab(self.hybrid_cluster,  "⊕ HYBRID")

        lay.addWidget(tabs)

        return w

    # ─────────────────────────────────────────

    def _make_controls_panel(self):

        w = QWidget()

        w.setObjectName("ctrlPanel")
        w.setFixedWidth(116)

        lay = QVBoxLayout(w)

        self.ctrl_panel = ControlsPanel()

        lay.addWidget(self.ctrl_panel)

        self.ctrl_panel.throttle_btn.stateChanged.connect(
            lambda v: setattr(model, 'throttle', v)
        )

        self.ctrl_panel.brake_btn.stateChanged.connect(
            lambda v: setattr(model, 'brake', v)
        )

        return w

    # ─────────────────────────────────────────

    def _make_bottom_bar(self):

        bar = QWidget()

        bar.setObjectName("statusBar")
        bar.setFixedHeight(38)

        lay = QHBoxLayout(bar)

        for key in ["SPEED", "FUEL", "TEMP", "BUS"]:

            col = QVBoxLayout()

            lbl = QLabel(key)
            lbl.setObjectName("statusLabel")

            val = QLabel("--")
            val.setObjectName("statusValue")

            col.addWidget(lbl)
            col.addWidget(val)

            setattr(self, f"_status_{key.lower()}", val)

            cw = QWidget()
            cw.setLayout(col)

            lay.addWidget(cw)

        return bar

    # ─────────────────────────────────────────

    def _switch_view(self, idx):

        self.stack.setCurrentIndex(idx)

        self.btn_table.setChecked(idx == 0)
        self.btn_cluster.setChecked(idx == 1)

    # ─────────────────────────────────────────

    def _start(self):

        if self._running:
            return

        self._running = True

        self._physics_timer.start()

        self.timer = QTimer()

        self.timer.timeout.connect(self._tick)

        self.timer.start(80)

        self._status_bus.setText("ON")

    # ─────────────────────────────────────────

    def _stop(self):

        if hasattr(self, 'timer'):
            self.timer.stop()

        self._physics_timer.stop()

        self._running = False

        self._status_bus.setText("OFF")

    # ─────────────────────────────────────────

    def _physics_tick(self):

        self.ctrl_panel.update_indicators(
            model.throttle,
            model.brake
        )

        model.update(dt=0.030)

        speed = model.speed
        fuel  = model.fuel
        temp  = model.temp
        rpm   = model.rpm
        odo   = model.odometer
        trip  = model.trip

        self.digital_cluster.set_data(
            speed, fuel, temp, rpm, odo, trip
        )

        self.analog_cluster.set_data(
            speed, fuel, temp, rpm, odo, trip
        )

        self.hybrid_cluster.set_data(
            speed, fuel, temp, rpm, odo, trip
        )

        self._status_speed.setText(
            f"{int(speed)} km/h"
        )

        self._status_fuel.setText(
            f"{int(fuel)}%"
        )

        self._status_temp.setText(
            f"{int(temp)}°C"
        )

    # ─────────────────────────────────────────
    # FIXED _tick METHOD
    # ─────────────────────────────────────────

    def _tick(self):

        line = next(self.data_gen)

        parts = line.split(",")

        if len(parts) != 4:
            return

        timestamp, can_id, dlc, data = parts

        if self._filter_id == "" or self._filter_id.lower() in can_id.lower():

            bg_col, fg_col = ROW_COLORS.get(
                can_id,
                ("#0a0f1e", "#e2e8f0")
            )

            row = self.table.rowCount()

            if row >= self._row_limit:
                self.table.removeRow(0)
                row = self.table.rowCount()

            self.table.insertRow(row)

            for col_i, text in enumerate([
                timestamp,
                can_id,
                dlc,
                data
            ]):

                item = QTableWidgetItem(text)

                item.setForeground(QColor(fg_col))
                item.setBackground(QColor(bg_col))

                self.table.setItem(row, col_i, item)

            self.table.scrollToBottom()

        decoded = decode(can_id, data)

        if decoded["type"]:
            self.signal_state[
                decoded["type"]
            ] = decoded["value"]