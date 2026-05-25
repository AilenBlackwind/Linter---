from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from PyQt5.QtWidgets import QFrame, QSizePolicy, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush

from ..utils import hex_to_qcolor


@dataclass
class CellBorderStyle:
    color: str = "666666"
    size: int = 8
    val: str = "single"


class GridCellWidget(QFrame):
    clicked = pyqtSignal(int, int, bool)

    def __init__(self, row: int, col: int, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self._selected = False
        self._shading: Optional[str] = None
        self._text = ""
        self._borders: Dict[str, CellBorderStyle] = {}
        self._set_cell_text()
        self._setup_ui()

    def _set_cell_text(self):
        col_letter = chr(ord('A') + self.col)
        self._text = f"{col_letter}{self.row + 1}"

    def _setup_ui(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setMinimumSize(60, 40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)

    def set_shading(self, hex_color: Optional[str]):
        self._shading = hex_color
        self.update()

    def set_border(self, side: str, style: Optional[CellBorderStyle]):
        if style:
            self._borders[side] = style
        else:
            self._borders.pop(side, None)
        self.update()

    def clear_borders(self):
        self._borders.clear()
        self.update()

    def is_selected(self) -> bool:
        return self._selected

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            is_shift = modifiers & Qt.ShiftModifier
            self.clicked.emit(self.row, self.col, is_shift)

    def _draw_border_line(self, painter: QPainter, side: str, rect: QRect, style: CellBorderStyle):
        if style.val == 'nil' or style.size <= 0:
            return

        color = hex_to_qcolor(style.color)
        pen_width = max(1, style.size // 4)
        pen = QPen(color, pen_width)

        if style.val == 'dashed':
            pen.setStyle(Qt.DashLine)
        elif style.val == 'dotted':
            pen.setStyle(Qt.DotLine)
        elif style.val == 'double':
            pen.setStyle(Qt.SolidLine)

        painter.setPen(pen)

        if side == 'top':
            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
        elif side == 'bottom':
            painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        elif side == 'left':
            painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
        elif side == 'right':
            painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(3, 3, -3, -3)

        if self._shading:
            color = hex_to_qcolor(self._shading)
            painter.fillRect(rect, QBrush(color))
        else:
            painter.fillRect(rect, QBrush(QColor(255, 255, 255)))

        default_border = CellBorderStyle(color="CCCCCC", size=4, val="single")

        for side in ['top', 'bottom', 'left', 'right']:
            border_style = self._borders.get(side, default_border)
            self._draw_border_line(painter, side, rect, border_style)

        if self._selected:
            pen = QPen(QColor(0, 120, 215), 3)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))

        painter.setPen(QColor(0, 0, 0))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self._text)
