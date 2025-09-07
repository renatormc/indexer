import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QScrollArea,
    QFrame, QLabel, QVBoxLayout, QMainWindow, QSizePolicy
)
from PySide6.QtCore import Qt

from gui.main_window import MainWindow

def run_gui() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())