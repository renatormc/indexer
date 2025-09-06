from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QScrollArea,
    QVBoxLayout, QMainWindow
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

import config
from gui.result_widget import ResultWidget
from repo import search_documents
from utils import startfile


def get_icon(name) -> QIcon:
    path = config.APPDIR / "gui/assets" / name
    return QIcon(str(path))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Indexer")
        self.setMinimumSize(800, 800)
        self.setWindowIcon(get_icon("app_icon.jpg"))

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter search query and press Enter...")
        self.search_bar.returnPressed.connect(self.perform_search)
        main_layout.addWidget(self.search_bar)

        # Scrollable area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)
        main_layout.addWidget(self.scroll_area)

    def perform_search(self) -> None:
        query = self.search_bar.text().strip()
        docs = search_documents(query)

        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for doc in docs:
            widget = ResultWidget(doc)
            widget.openRequested.connect(self.open_file)
            self.results_layout.addWidget(widget)

    def open_file(self, path: str | Path) -> None:
        startfile((Path(".") / path).absolute())

    

