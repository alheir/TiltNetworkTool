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

STOP_MASK = 0xC0
STOP_BITS = 0xC0

MAX_MSG_SIZE = 3
IDLE_TIMER_MS = 2500 # 2.5s max
RX_TIMER_MS = 10

ID_SHIFT = 3
ID_MASK = 0x07
SIGN_SHIFT = 5
SIGN_MASK = 0x01
FRAMETYPE_SHIFT = 3
FRAMETYPE_MASK = 0x03

class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.serialConnected = False
        self.connection_but.clicked.connect(self.toggleSerialConnection)

        self.actionRefresh_ports.triggered.connect(self.updateAvailablePorts)
        self.updateAvailablePorts()
        self.serial = serial.Serial()

        self.currBuf = QByteArray()
        self.isMidFrame = False
        
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

    def processBuffer(self):
        buff = self.currBuf[-2:]
        b1 = int.from_bytes(buff[1])
        index = b1 & ID_MASK
        angle = (b1 >> FRAMETYPE_SHIFT) & FRAMETYPE_MASK
        value = int.from_bytes(buff[0])
        if((b1 >> SIGN_SHIFT) & SIGN_MASK):
            value = -value
        if(self.stations[index].assignAngle(angle, value)):
            self.timers[index].start()
            self.stationInfoWidgets[index].setEnabled(True)
            self.stationInfoWidgets[index].setAngleLabels(self.stations[index].angles)
            self.oglw.setOrientation(
                index,
                -self.stations[index].roll,
                -self.stations[index].pitch,
                +self.stations[index].yaw + 90
            )
        self.currBuf.clear()

    def receive(self):
        while(self.serial.is_open and self.serial.in_waiting > 0):
            read = self.serial.read(1)
            if(self.currBuf.length() >= MAX_MSG_SIZE):
                self.currBuf = self.currBuf.right(MAX_MSG_SIZE - 1)
            self.currBuf.append(read)
            if((int.from_bytes(read) & STOP_MASK) == STOP_BITS):
                if(self.currBuf.length() > 1):
                    self.processBuffer()


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
        
        print(f"Sent LED command: Station {self.selected_station_index}, (R:{self.selected_r}, G:{self.selected_g}, B:{self.selected_b})")

        # Replace with actual message construction logic
        #
        #
        #
        # message = "Example Message"
        #
        #
        #
        # self.serial.write(message)
        