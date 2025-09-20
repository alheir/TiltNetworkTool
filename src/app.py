# PyQt5 modules
from PyQt6 import QtWidgets
import qdarktheme

# Python modules
import sys

# Main window ui import
from src.mainwindow import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
