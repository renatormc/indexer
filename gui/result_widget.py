import os
from pathlib import Path
from PySide6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QHBoxLayout, QMenu
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap

import config
from models import Document
from utils import show_in_file_manager, startfile


class ResultWidget(QFrame):

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
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(100, 100)
        main_layout.addWidget(self.thumb_label)

        text_layout = QVBoxLayout()
        self.title_label = QLabel(doc.title)
        self.path_label = QLabel(doc.path)
        self.title_label.setStyleSheet("font-weight: bold;")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.path_label)

        main_layout.addLayout(text_layout)
        self.setLayout(main_layout)

        self.load(doc)

    def load(self, doc: Document) -> None:
        self.doc = doc
        thumb = doc.thumb
        if not thumb.is_file():
            thumb = config.THUMB_PLACEHOLDER
        pixmap = QPixmap(str(thumb))
        pixmap = pixmap.scaled(100, 100) 
        self.thumb_label.setPixmap(pixmap)
        self.title_label.setText(doc.title)
        self.path_label.setText(doc.path)

    def mouseDoubleClickEvent(self, event):
        startfile((Path(".") / self.doc.path).absolute())
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = menu.addAction("Open")
        show_action = menu.addAction("Show in folder")
        action = menu.exec(event.globalPos())
        if action == open_action:
            startfile((Path(".") / self.doc.path).absolute())
        elif action == show_action:
            show_in_file_manager((Path(".") / self.doc.path).absolute())