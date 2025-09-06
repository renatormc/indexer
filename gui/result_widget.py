from pathlib import Path
from PySide6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QHBoxLayout
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap

import config
from models import Document


class ResultWidget(QFrame):
    openRequested = Signal(str)

    def __init__(self, doc: Document) -> None:
        super().__init__()
        thumb = doc.thumb
        if not thumb.is_file():
            thumb = config.THUMB_PLACEHOLDER
        self.doc = doc
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ResultWidget {
                background: white;
            }
            ResultWidget:hover {
                background: #e0e0e0;
            }
        """)

        main_layout = QHBoxLayout()
        thumb_label = QLabel()
        pixmap = QPixmap(str(thumb))
        pixmap = pixmap.scaled(100, 100)  
        thumb_label.setPixmap(pixmap)
        thumb_label.setFixedSize(100, 100)
        main_layout.addWidget(thumb_label)

        text_layout = QVBoxLayout()
        self.title_label = QLabel(doc.title)
        self.title_label.setStyleSheet("font-weight: bold;")
        self.path_label = QLabel(doc.path)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.path_label)

        main_layout.addLayout(text_layout)
        self.setLayout(main_layout)

    def mouseDoubleClickEvent(self, event):
        self.openRequested.emit(self.doc.path)
        super().mouseDoubleClickEvent(event)