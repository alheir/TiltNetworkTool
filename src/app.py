# PyQt5 modules
from PyQt6 import QtWidgets
import qdarktheme
import logging

# Python modules
import sys

# Main window ui import
from src.mainwindow import MainWindow


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
