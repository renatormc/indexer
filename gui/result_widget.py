import os
from pathlib import Path
from PySide6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QHBoxLayout, QMenu,
    QInputDialog, QTextEdit, QDialog, QDialogButtonBox, QLineEdit
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from sqlalchemy import update

import config
from database import DBSession
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
        self.loc_label = QLabel(doc.loc or "")
        self.title_label.setStyleSheet("font-weight: bold;")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.path_label)
        text_layout.addWidget(self.loc_label)

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
        self.loc_label.setText(doc.loc or "")

    def mouseDoubleClickEvent(self, event):
        startfile((Path(".") / self.doc.path).absolute())
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = menu.addAction("Open")
        show_action = menu.addAction("Show in folder")
        edit_desc_action = menu.addAction("Edit description")
        set_loc_action = menu.addAction("Set location")
        action = menu.exec(event.globalPos())
        if action == open_action:
            startfile((Path(".") / self.doc.path).absolute())
        elif action == show_action:
            show_in_file_manager((Path(".") / self.doc.path).absolute())
        elif action == edit_desc_action:
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Description")
            dialog.resize(500, 300) 
            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit(dialog)
            text_edit.setPlainText(getattr(self.doc, "description", ""))
            layout.addWidget(text_edit)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
            layout.addWidget(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.doc.description = text_edit.toPlainText()
                with DBSession() as db_session:
                    db_session.execute(update(Document).where(Document.id == self.doc.id).values(description=self.doc.description))
                    db_session.commit()
        elif action == set_loc_action:
            dialog = QDialog(self)
            dialog.setWindowTitle("Set Location")
            dialog.resize(400, 120)
            layout = QVBoxLayout(dialog)
            line_edit = QLabel("Location:")
            layout.addWidget(line_edit)
            loc_edit = QLineEdit(dialog)
            loc_edit.setText(self.doc.loc or "")
            layout.addWidget(loc_edit)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
            layout.addWidget(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.doc.loc = loc_edit.text()
                with DBSession() as db_session:
                    db_session.execute(update(Document).where(Document.id == self.doc.id).values(loc=self.doc.loc))
                    db_session.commit()
                self.load(self.doc)