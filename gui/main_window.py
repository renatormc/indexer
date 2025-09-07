from datetime import datetime
from pathlib import Path
import shutil
import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QScrollArea,
    QVBoxLayout, QMainWindow, QMenuBar, QMenu, QFileDialog, QInputDialog
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

import config
from database import DBSession
from gui.result_widget import ResultWidget
from indexer import index_pdf
from repo import search_documents
from utils import startfile
from watch import watch_folder


def get_icon(name) -> QIcon:
    path = config.APPDIR / "gui/assets" / name
    return QIcon(str(path))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Indexer")
        self.setMinimumSize(800, 800)
        self.setWindowIcon(get_icon("app_icon.jpg"))

        # Start watch_folder in a background thread
        self._watcher_thread = threading.Thread(target=watch_folder, daemon=True)
        self._watcher_thread.start()

        # Add menu bar and File menu
        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)
        add_file_action = QAction("Add file", self)
        add_file_action.triggered.connect(self.add_file)
        file_menu.addAction(add_file_action)
        menubar.addMenu(file_menu)
        self.setMenuBar(menubar)

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
            self.results_layout.addWidget(widget)

    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        if file_paths:
            prefix, ok = QInputDialog.getText(
                self,
                "Optional Prefix",
                "Enter an optional prefix for these files:"
            )
            
            if ok:
                if prefix:
                    folder = Path(prefix)
                    try:
                        folder.mkdir(parents=True)
                    except FileExistsError:
                        pass
                else:
                    folder = Path(".")
                with DBSession() as db_session:
                    t = datetime.now().timestamp()
                    for f in file_paths:
                        p = Path(f)
                        dest = folder / p.name
                        shutil.copy(p, folder / p.name)
                        index_pdf(db_session, dest, t, commit=False)
                    db_session.commit()






