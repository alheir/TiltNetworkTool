from PyQt6 import QtCore, QtGui, QtWidgets

class StationInfoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = QtWidgets.QGridLayout()
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setLayout(QtWidgets.QGridLayout())


        labelRoll = QtWidgets.QLabel(text="Roll")
        labelPitch = QtWidgets.QLabel(text="Pitch")
        labelYaw = QtWidgets.QLabel(text="Yaw")
        self.groupBox.layout().addWidget(labelRoll, 0, 0)
        self.groupBox.layout().addWidget(labelPitch, 1, 0)
        self.groupBox.layout().addWidget(labelYaw, 2, 0)
        
        self.labelRollValue = QtWidgets.QLabel(text="")
        self.labelPitchValue = QtWidgets.QLabel(text="")
        self.labelYawValue = QtWidgets.QLabel(text="")
        self.groupBox.layout().addWidget(self.labelRollValue, 0, 1)
        self.groupBox.layout().addWidget(self.labelPitchValue, 1, 1)
        self.groupBox.layout().addWidget(self.labelYawValue, 2, 1)
        
        grid.addWidget(self.groupBox,0,0)
        self.setLayout(grid)

    def setName(self, name):
        self.groupBox.setTitle(name)

    def setAngleLabels(self, roll, pitch, yaw):
        self.labelRollValue.setText("{}°".format(roll))
        self.labelPitchValue.setText("{}°".format(pitch))
        self.labelYawValue.setText("{}°".format(yaw))
    def setAngleLabels(self, angles):
        self.labelRollValue.setText("{}°".format(angles[0]))
        self.labelPitchValue.setText("{}°".format(angles[1]))
        self.labelYawValue.setText("{}°".format(angles[2]))

    def setEnabled(self, enabled=True):
        self.groupBox.setEnabled(enabled)

