import matplotlib
matplotlib.use('Qt5Agg') # Fuerza el uso de Qt5Agg como backend de Matplotlib

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import time

class PlotWidget(QWidget):
    def __init__(self, station_index, angle_histories):
        super().__init__()
        self.station_index = station_index
        self.angle_histories = angle_histories  # List of [roll_history, pitch_history, yaw_history], each as [(timestamp, value), ...]
        self.setWindowTitle(f"Station {station_index} Angle Plot")
        self.setGeometry(100, 100, 800, 600)

        # Set up Matplotlib figure and canvas
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.updatePlot()

    def updatePlot(self, angle_histories=None):
        if angle_histories:
            self.angle_histories = angle_histories
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        labels = ['Roll', 'Pitch', 'Yaw']
        colors = ['r', 'g', 'b']
        for i, (history, label, color) in enumerate(zip(self.angle_histories, labels, colors)):
            if history:
                times, values = zip(*history)
                ax.plot(times, values, label=label, color=color)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Angle (°)')
        ax.set_title(f'Station {self.station_index} Angles Over Time')
        ax.legend()
        ax.grid(True)
        self.canvas.draw()
