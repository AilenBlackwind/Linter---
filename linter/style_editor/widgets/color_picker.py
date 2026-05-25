from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame, QLineEdit, QPushButton, QColorDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from ..utils import hex_to_qcolor, qcolor_to_hex


class ColorPickerWidget(QWidget):
    color_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_hex: str = "FFFFFF"
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.color_preview = QFrame()
        self.color_preview.setFrameShape(QFrame.Box)
        self.color_preview.setLineWidth(1)
        self.color_preview.setMinimumSize(40, 24)
        self.color_preview.setCursor(Qt.PointingHandCursor)
        self.color_preview.mousePressEvent = self._open_color_dialog

        self.hex_edit = QLineEdit()
        self.hex_edit.setMaxLength(6)
        self.hex_edit.setText("FFFFFF")
        self.hex_edit.setMaximumWidth(70)
        self.hex_edit.textChanged.connect(self._on_hex_changed)

        self.picker_btn = QPushButton("...")
        self.picker_btn.setMaximumWidth(30)
        self.picker_btn.clicked.connect(self._open_color_dialog)

        layout.addWidget(self.color_preview)
        layout.addWidget(self.hex_edit)
        layout.addWidget(self.picker_btn)

        self._update_preview()

    def _update_preview(self):
        hex_color = self._current_hex
        self.color_preview.setStyleSheet(f"background-color: #{hex_color};")

    def _open_color_dialog(self, event=None):
        current = hex_to_qcolor(self._current_hex)
        color = QColorDialog.getColor(current, self, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0446\u0432\u0435\u0442")
        if color.isValid():
            self.set_color(qcolor_to_hex(color))

    def _on_hex_changed(self, text: str):
        text = text.upper()
        if len(text) == 6 and all(c in "0123456789ABCDEF" for c in text):
            self._current_hex = text
            self._update_preview()
            self.color_changed.emit(text)

    def set_color(self, hex_color: str):
        if hex_color and len(hex_color) >= 6:
            self._current_hex = hex_color.upper()[:6]
            self.hex_edit.setText(self._current_hex)
            self._update_preview()

    def get_color(self) -> str:
        return self._current_hex
