# PyQt5 modules
from math import inf
from PyQt6.QtWidgets import QMainWindow
# Project modules
from src.ui.mainwindow import Ui_MainWindow

from PyQt6.QtCore import QByteArray, QTimer
import serial
from serial.tools.list_ports import comports
from src.package.Station import Station, STATION_ID, STATION_ID_NAMES, STATION_COUNT, STATION_ANGLES
from src.widgets.station_info_widget import StationInfoWidget
from src.protocol.protocol_handler import ProtocolHandler  # NUEVO: capa intermedia de protocolo

IDLE_TIMER_MS = 2500  # 2.5s
RX_TIMER_MS = 10

class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.serialConnected = False
        self.connection_but.clicked.connect(self.toggleSerialConnection)

        self.actionRefresh_ports.triggered.connect(self.updateAvailablePorts)
        self.updateAvailablePorts()
        self.serial = serial.Serial()
        self.protocol = ProtocolHandler()

        self.stationInfoWidgets = []
        self.actionFRDM_K64F.triggered.connect(self.selectFRDMModel)
        self.actionPlane.triggered.connect(self.selectPlaneModel)

        for i in range(len(STATION_ID)):
            siw = StationInfoWidget(self)
            self.stationInfoLayout.addWidget(siw)
            self.stationInfoWidgets.append(siw)
        self.timers = []

        # this section builds the network viewer for each station
        for i, siw in enumerate(self.stationInfoWidgets):
            siw.setEnabled(False)
            siw.setName('Station {}'.format(STATION_ID_NAMES[i])) 
            timer = QTimer()
            timer.setInterval(IDLE_TIMER_MS)
            timer.setSingleShot(True)
            timer.timeout.connect(self.buildStationTimeout(i))
            timer.start()
            self.timers.append(timer)

        self.stations = []
        for x in range(STATION_COUNT):
            self.stations.append(Station(id=STATION_ID[x]))

        # checks RX buffer every RX_TIMER_MS ms
        timer = QTimer()
        timer.setInterval(RX_TIMER_MS)
        timer.setSingleShot(False)
        timer.timeout.connect(self.receive)
        timer.start()
        self.rxTimer = timer

        self.stationSelector_cb.addItems(STATION_ID_NAMES)
        self.send_pb.clicked.connect(self.sendLEDCommand)
        self.LED_gb.setEnabled(False)
        

    def buildStationTimeout(self, stationIndex):
        return lambda : self.disableStationInfoWidget(stationIndex)

    def disableStationInfoWidget(self, stationIndex):
        self.stationInfoWidgets[stationIndex].setEnabled(False)
        self.oglw.setStationInactive(stationIndex)

    def processParsedMessage(self, msg: dict):
        """
        msg dict esperado (lo produce ProtocolHandler.on_bytes):
          - station_index: int
          - angle: int en {0: roll, 1: pitch, 2: yaw}
          - value: float/int
        """
        try:
            station_index = int(msg.get('station_index'))
            angle_id = msg.get('angle')
            value = msg.get('value')
        except Exception as e:
            print(f"[MainWindow] Mensaje inválido (faltan campos): {msg} ({e})")
            return

        angle_index = self._resolve_angle_index(angle_id)
        if angle_index not in (0, 1, 2):
            print(f"[MainWindow] 'angle' no reconocido: {angle_id}")
            return

        if station_index < 0 or station_index >= STATION_COUNT:
            print(f"[MainWindow] 'station_index' fuera de rango: {station_index}")
            return

        if self.stations[station_index].assignAngle(angle_index, value):
            self.timers[station_index].start()
            self.stationInfoWidgets[station_index].setEnabled(True)
            self.stationInfoWidgets[station_index].setAngleLabels(self.stations[station_index].angles)
            self.oglw.setOrientation(
                station_index,
                -self.stations[station_index].roll,
                -self.stations[station_index].pitch,
                +self.stations[station_index].yaw + 90
            )

    def _resolve_angle_index(self, angle_id):
        if isinstance(angle_id, int) and angle_id in (0, 1, 2):
            return angle_id
        return -1

    def receive(self):
        try:
            while self.serial.is_open and self.serial.in_waiting > 0:
                to_read = self.serial.in_waiting or 1
                chunk = self.serial.read(to_read)
                try:
                    messages = self.protocol.on_bytes(chunk)
                except NotImplementedError as e:
                    print(f"[MainWindow] ProtocolHandler.on_bytes no implementado aún: {e}")
                    break

                if not messages:
                    continue
                for msg in messages:
                    self.processParsedMessage(msg)
        except Exception as e:
            print(f"[MainWindow] Error en receive(): {e}")

    def toggleSerialConnection(self):
        if(not self.serialConnected):
            port = self.getPort()
            self.serial.baudrate = int(self.baudrate_cb.currentText())
            self.serial.port = port
            self.serial.open()
            self.serialConnected = self.serial.is_open
        else:
            self.serial.close()
            self.serialConnected = False
        self.configPortSettings(self.serialConnected)
    
    def configPortSettings(self, connected=False):
        self.COM_gb.setEnabled(not connected)
        self.LED_gb.setEnabled(connected)
        if(connected):
            self.connection_but.setText('Disconnect')
        else:
            self.connection_but.setText('Connect')

    def updateAvailablePorts(self):
        self.port_cb.clear()
        for port, desc, hwid in comports():
            self.port_cb.addItem(f"{port} - {desc}")

    def getPort(self):
        text = self.port_cb.currentText()
        if text:
            port = text.split(" - ")[0]
            return port
        return None

    def selectFRDMModel(self):
        if(self.actionFRDM_K64F.isChecked()):
            self.actionPlane.setChecked(False)
            self.oglw.setModelIndex(0)
        else:
            self.actionPlane.setChecked(True)
            self.selectPlaneModel()

    def selectPlaneModel(self):
        if(self.actionPlane.isChecked()):
            self.actionFRDM_K64F.setChecked(False)
            self.oglw.setModelIndex(1)
        else:
            self.actionFRDM_K64F.setChecked(True)
            self.selectFRDMModel()

    def sendLEDCommand(self):
        if not self.serialConnected:
            return
        
        self.selected_station_index = STATION_ID_NAMES.index(self.stationSelector_cb.currentText())
        self.selected_r = self.r_checkb.isChecked()
        self.selected_g = self.g_checkb.isChecked()
        self.selected_b = self.b_checkb.isChecked()
        
        try:
            message = self.protocol.build_led_command(
                self.selected_station_index,
                self.selected_r,
                self.selected_g,
                self.selected_b
            )
        except NotImplementedError as e:
            print(f"[MainWindow] ProtocolHandler.build_led_command no implementado aún: {e}")
            return
        except Exception as e:
            print(f"[MainWindow] Error construyendo LED cmd: {e}")
            return

        if not message:
            print("[MainWindow] build_led_command devolvió vacío/None, no se envía nada.")
            return

        try:
            self.serial.write(message)
            print(f"[MainWindow] Enviado {len(message)} bytes: {message}")
        except Exception as e:
            print(f"[MainWindow] Error enviando por serial: {e}")
