from PyQt6 import QtWidgets, QtCore
from src.protocol.protocol_handler import ProtocolHandler
from src.package.Station import STATION_COUNT, STATION_ANGLES_COUNT, STATION_ID
import math
import time

AUTOSEND_INTERVAL_MS = 200

class SimulationWidget(QtWidgets.QWidget):
    def __init__(self, protocol: ProtocolHandler, main_window, parent=None):
        super(SimulationWidget, self).__init__(parent)
        self.protocol = protocol
        self.main_window = main_window
        self.setWindowTitle("Serial Data Emulator")
        self.setGeometry(100, 100, 400, 300)

        self.message_le = QtWidgets.QLineEdit()
        self.send_btn = QtWidgets.QPushButton("Send", clicked=self.send_simulated_data)
        self.auto_mode_cb = QtWidgets.QCheckBox("Toggle autosend mode, bypassing protocol_handler", toggled=self.toggle_auto_mode)

        self.station_checkboxes = []
        station_layout = QtWidgets.QHBoxLayout()
        station_layout.addWidget(QtWidgets.QLabel("Stations:"))
        for i, sid in enumerate(STATION_ID):
            cb = QtWidgets.QCheckBox(sid.decode('utf-8'))
            cb.setChecked(True if i == 0 else False)  # Simula solo estación 0 por defecto
            cb.setEnabled(False) 
            self.station_checkboxes.append(cb)
            station_layout.addWidget(cb)

        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.close_btn = QtWidgets.QPushButton("Close", clicked=self.close)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(QtWidgets.QLabel("Message simulating your protocol from K64F:"))
        lay.addWidget(self.message_le)
        lay.addWidget(self.send_btn)
        lay.addWidget(self.auto_mode_cb)
        lay.addLayout(station_layout)
        lay.addWidget(QtWidgets.QLabel("Logs:"))
        lay.addWidget(self.output_te)
        lay.addWidget(self.close_btn)

        self.auto_timer = QtCore.QTimer()
        self.auto_timer.setInterval(AUTOSEND_INTERVAL_MS)
        self.auto_timer.timeout.connect(self.send_auto_data)
        self.start_time = time.time()
        self.station_count = STATION_COUNT
        self.angle_count = STATION_ANGLES_COUNT

    @QtCore.pyqtSlot()
    def send_simulated_data(self):
        text = self.message_le.text().strip()
        if not text:
            return
        # Convertir a bytes y simular recepción
        data = text.encode('utf-8')
        try:
            messages = self.protocol.on_bytes(data) # Parsea el mensaje según protocol_handler
            self.output_te.append(f"Enviado: {text} -> {len(messages)} mensajes parseados")
            for msg in messages:
                self.main_window.processParsedMessage(msg)  # Envia a mainwindow
        except Exception as e:
            self.output_te.append(f"Error: {e}")
        self.message_le.clear()

    @QtCore.pyqtSlot(bool)
    def toggle_auto_mode(self, checked):
        for cb in self.station_checkboxes:
            cb.setEnabled(checked)
        if checked:
            self.start_time = time.time()
            self.auto_timer.start()
            self.output_te.append(f"Autosend ON, sending sinusoidal data every {AUTOSEND_INTERVAL_MS} ms")
        else:
            self.auto_timer.stop()
            self.output_te.append("Autosend OFF")

    @QtCore.pyqtSlot()
    def send_auto_data(self):
        current_time = time.time() - self.start_time
        messages = []
        for station_idx in range(self.station_count):
            if not self.station_checkboxes[station_idx].isChecked():
                continue  # Skip unselected stations
            for angle_idx in range(self.angle_count):
                # sin(tiempo + offset) * 90
                offset = (station_idx * 0.5) + (angle_idx * 0.3)  # Offset por estación/ángulo
                value = int(math.sin(current_time + offset) * 90)
                msg = {
                    'station_index': station_idx,
                    'angle': angle_idx,
                    'value': value
                }
                messages.append(msg)

                # Bypass ProtocolHandler
                self.main_window.processParsedMessage(msg)
        self.output_te.append(f"Autosend {len(messages)} messages.")

    def closeEvent(self, event):
        self.auto_timer.stop()
        self.main_window.toggleSerialConnection()
        super().closeEvent(event)
