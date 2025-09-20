from PyQt6 import QtCore, QtWidgets, QtSerialPort
import qdarktheme
from PyQt6.QtCore import QTimer
import numpy as np

import time
station_angles = [
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0]
]
station_dirs = [
    1,
    1,
    1,
    1,
    1,
    1
]
station_ang = [
    0,
    0,
    0,
    0,
    0,
    0
]
station_id = [
    'A','B','C','D','E','F'
]

angles = ['R', 'P', 'Y']

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.message_le = QtWidgets.QLineEdit()
        self.send_btn = QtWidgets.QPushButton(
            text="Send",
            clicked=self.send
        )
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.button = QtWidgets.QPushButton(
            text="Connect", 
            checkable=True,
            toggled=self.on_toggled
        )
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.message_le)
        hlay.addWidget(self.send_btn)
        lay.addLayout(hlay)
        lay.addWidget(self.output_te)
        lay.addWidget(self.button)

        self.serial = QtSerialPort.QSerialPort(self)
        self.serial.setPortName('COM3')
        self.serial.setBaudRate(QtSerialPort.QSerialPort.BaudRate.Baud115200.value)
        self.serial.readyRead.connect(self.receive)

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.send)

        self.sta_counter = 0
        self.iter_counter = 0

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.output_te.append(text)

    @QtCore.pyqtSlot()
    def send(self):
        if(self.sta_counter == 0):
            if(self.iter_counter >= 30):
                for i in range(6):
                    if(np.random.rand() > 0.5):
                        station_dirs[i] = 1
                    else:
                        station_dirs[i] = -1
                    a = np.random.rand()
                    if(a > 0.66):
                        station_ang[i] = 2
                    elif(a > 0.33):
                        station_ang[i] = 1
                    else:
                        station_ang[i] = 0
                self.iter_counter = 0

        self.sta_counter += 1
        if(self.sta_counter >= 6):
            self.iter_counter += 1
            self.sta_counter = 0
            
        if(station_dirs[self.sta_counter] > 0):
            station_angles[self.sta_counter][station_ang[self.sta_counter]] += 1
        else:
            station_angles[self.sta_counter][station_ang[self.sta_counter]] -= 1
        if(station_angles[self.sta_counter][station_ang[self.sta_counter]] > 180):
            station_angles[self.sta_counter][station_ang[self.sta_counter]] = -179
        elif(station_angles[self.sta_counter][station_ang[self.sta_counter]] < -179):
            station_angles[self.sta_counter][station_ang[self.sta_counter]] = 180
        s= "{}{}{}#".format(station_id[self.sta_counter], angles[station_ang[self.sta_counter]], int(station_angles[self.sta_counter][station_ang[self.sta_counter]]))
        print(s)
        self.serial.write(s.encode())

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.timer.stop()
        self.button.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
                    self.button.setChecked(False)
                else:
                    self.timer.start()
        else:
            self.serial.close()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    w = Widget()
    w.show()
    sys.exit(app.exec())
