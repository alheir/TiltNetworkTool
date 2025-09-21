# PyQt5 modules
from PyQt6 import QtWidgets
import logging
import argparse

# Python modules
import sys

# Main window ui import
from src.mainwindow import MainWindow
from src.themes import LIGHT_THEME, DARK_THEME

def main():
    parser = argparse.ArgumentParser(description="Tilt Network Tool")
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help='Set the logging level (default: ERROR)'
    )
    parser.add_argument(
        '--theme', '-t',
        choices=['light', 'dark'],
        default='light',
        help='Set the UI theme (default: light)'
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(levelname)s: %(message)s')
   
    app = QtWidgets.QApplication(sys.argv)
    
    if args.theme == 'dark':
        app.setStyleSheet(DARK_THEME)
    else:
        app.setStyleSheet(LIGHT_THEME)

    window = MainWindow()
    window.setTheme(args.theme)
    window.show()
    sys.exit(app.exec())
