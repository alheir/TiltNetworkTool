# PyQt5 modules
from PyQt6 import QtWidgets
import logging
import argparse

# Python modules
import sys

# Main window ui import
from src.mainwindow import MainWindow


def main():
    parser = argparse.ArgumentParser(description="Tilt Network Tool")
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help='Set the logging level (default: ERROR)'
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(levelname)s: %(message)s')
   
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
