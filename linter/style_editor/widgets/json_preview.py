from __future__ import annotations

import json

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt


class JsonPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel()
        self.label.setStyleSheet("""
            QLabel {
                font-family: Consolas, monospace;
                font-size: 11px;
                padding: 10px;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.label)
        layout.addWidget(scroll)

    def set_data(self, data: dict):
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.label.setText(json_str)

    def set_text(self, text: str):
        self.label.setText(text)
