from __future__ import annotations

from typing import Optional, Set, Tuple, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QApplication, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent

from linter.converter.tables.advanced.models import TableStyle

from .grid_cell import GridCellWidget, CellBorderStyle
from ..style_utils import get_cell_shading, get_cell_bold, get_cell_italic, get_cell_borders


GRID_SIZE = 6


class VisualGridWidget(QWidget):
    selection_changed = pyqtSignal()
    style_rename_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_cells: Set[Tuple[int, int]] = set()
        self._last_clicked: Optional[Tuple[int, int]] = None
        self._grid_widgets: List[List[GridCellWidget]] = []
        self._current_style_name = ""

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        name_label = QLabel("\u0421\u0442\u0438\u043B\u044C:")
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(name_label)

        self._style_name_edit = QLineEdit()
        self._style_name_edit.setReadOnly(True)
        self._style_name_edit.setPlaceholderText("\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0441\u0442\u0438\u043B\u044F")
        self._style_name_edit.setStyleSheet("""
            QLineEdit {
                font-size: 12px; padding: 4px 8px;
                border: 1px solid #ccc; border-radius: 3px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                background-color: #fff;
                border: 1px solid #4a90d9;
            }
        """)
        self._style_name_edit.installEventFilter(self)
        self._style_name_edit.editingFinished.connect(self._on_style_name_edited)
        header_layout.addWidget(self._style_name_edit, stretch=1)

        layout.addLayout(header_layout)

        grid_group = QGroupBox(
            "6x6 \u0421\u0435\u0442\u043A\u0430 "
            "(\u043A\u043B\u0438\u043A \u0434\u043B\u044F \u0432\u044B\u0431\u043E\u0440\u0430, "
            "Shift+\u043A\u043B\u0438\u043A \u0434\u043B\u044F \u0434\u0438\u0430\u043F\u0430\u0437\u043E\u043D\u0430)"
        )
        grid_layout = QGridLayout(grid_group)
        grid_layout.setSpacing(2)

        for row in range(GRID_SIZE):
            row_widgets = []
            for col in range(GRID_SIZE):
                cell = GridCellWidget(row, col)
                cell.clicked.connect(self._on_cell_clicked)
                grid_layout.addWidget(cell, row, col)
                row_widgets.append(cell)
            self._grid_widgets.append(row_widgets)

        layout.addWidget(grid_group)

        info_label = QLabel(
            "\u041F\u043E\u0434\u0441\u043A\u0430\u0437\u043A\u0438:\n"
            "\u2022 \u041A\u043B\u0438\u043A \u2014 \u0432\u044B\u0431\u0440\u0430\u0442\u044C \u043E\u0434\u043D\u0443 \u044F\u0447\u0435\u0439\u043A\u0443\n"
            "\u2022 Shift+\u043A\u043B\u0438\u043A \u2014 \u0432\u044B\u0431\u0440\u0430\u0442\u044C \u0434\u0438\u0430\u043F\u0430\u0437\u043E\u043D\n"
            "\u2022 \u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 '\u0412\u044B\u0431\u0440\u0430\u043D\u043D\u044B\u0435 \u044F\u0447\u0435\u0439\u043A\u0438' \u0432 \u043F\u0430\u043D\u0435\u043B\u0438 \u0441\u043F\u0440\u0430\u0432\u0430 \u0434\u043B\u044F \u0440\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u044F\n"
            "\u2022 \u041D\u0435 \u0437\u0430\u0431\u0443\u0434\u044C\u0442\u0435 \u043D\u0430\u0436\u0430\u0442\u044C '\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C JSON' \u043F\u043E\u0441\u043B\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u0439!"
        )
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)

    @property
    def selected_cells(self) -> Set[Tuple[int, int]]:
        return self._selected_cells

    def get_selected_columns(self) -> Set[int]:
        cols = set()
        for _, col in self._selected_cells:
            cols.add(col)
        return cols

    def clear_selection(self):
        self._selected_cells.clear()
        self._last_clicked = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self._grid_widgets[r][c].set_selected(False)

    def _on_cell_clicked(self, row: int, col: int, is_shift: bool):
        cell_pos = (row, col)

        if is_shift and self._last_clicked is not None:
            last_r, last_c = self._last_clicked

            min_r, max_r = min(last_r, row), max(last_r, row)
            min_c, max_c = min(last_c, col), max(last_c, col)

            self._selected_cells.clear()
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self._grid_widgets[r][c].set_selected(False)

            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    self._selected_cells.add((r, c))
                    self._grid_widgets[r][c].set_selected(True)
        else:
            modifiers = QApplication.keyboardModifiers()
            is_ctrl = modifiers & Qt.ControlModifier

            if is_ctrl:
                if cell_pos in self._selected_cells:
                    self._selected_cells.discard(cell_pos)
                    self._grid_widgets[row][col].set_selected(False)
                else:
                    self._selected_cells.add(cell_pos)
                    self._grid_widgets[row][col].set_selected(True)
            else:
                self.clear_selection()
                self._selected_cells.add(cell_pos)
                self._grid_widgets[row][col].set_selected(True)

        self._last_clicked = cell_pos
        self.selection_changed.emit()

    def update_visuals(self, style: Optional[TableStyle]):
        if not style:
            return

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                shading = get_cell_shading(style, row, col, GRID_SIZE, GRID_SIZE)
                bold = get_cell_bold(style, row, col, GRID_SIZE, GRID_SIZE)
                italic = get_cell_italic(style, row, col, GRID_SIZE, GRID_SIZE)
                borders = get_cell_borders(style, row, col, GRID_SIZE, GRID_SIZE)
                self._grid_widgets[row][col].set_shading(shading)
                self._grid_widgets[row][col].set_bold(bold)
                self._grid_widgets[row][col].set_italic(italic)

                self._grid_widgets[row][col].clear_borders()
                for side, border_style in borders.items():
                    cell_border = CellBorderStyle(
                        color=border_style.color,
                        size=border_style.size,
                        val=border_style.val
                    )
                    self._grid_widgets[row][col].set_border(side, cell_border)

    def eventFilter(self, obj, event):
        if obj == self._style_name_edit and event.type() == QEvent.MouseButtonDblClick:
            self._style_name_edit.setReadOnly(False)
            self._style_name_edit.setFocus()
            self._style_name_edit.selectAll()
            return True
        return super().eventFilter(obj, event)

    def _on_style_name_edited(self):
        new_name = self._style_name_edit.text().strip()
        old_name = self._current_style_name

        if not new_name or new_name == old_name:
            self._style_name_edit.blockSignals(True)
            self._style_name_edit.setText(old_name)
            self._style_name_edit.setReadOnly(True)
            self._style_name_edit.blockSignals(False)
            return

        self.style_rename_requested.emit(old_name, new_name)

    def set_style_name(self, name: str):
        self._current_style_name = name
        self._style_name_edit.blockSignals(True)
        self._style_name_edit.setText(name)
        self._style_name_edit.setReadOnly(True)
        self._style_name_edit.blockSignals(False)
