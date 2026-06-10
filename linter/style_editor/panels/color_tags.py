from __future__ import annotations

from typing import Dict, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..widgets.color_picker import ColorPickerWidget


class ColorTagsPanel(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._colors_data: Dict[str, str] = {}
        self._updating = False
        self._renaming_old = ""

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        left_group = QGroupBox("Цветовые теги")
        left_inner = QVBoxLayout(left_group)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Новый")
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)
        self.delete_btn = QPushButton("- Удалить")
        self.delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        left_inner.addLayout(btn_layout)

        self.tag_list = QListWidget()
        self.tag_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tag_list.currentRowChanged.connect(self._on_selected)
        self.tag_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tag_list.itemChanged.connect(self._on_item_renamed)
        left_inner.addWidget(self.tag_list)

        left_outer = QWidget()
        left_outer_layout = QVBoxLayout(left_outer)
        left_outer_layout.addWidget(left_group)
        left_outer.setMaximumWidth(250)
        layout.addWidget(left_outer)

        props_group = QGroupBox("Свойства тега")
        props_layout = QVBoxLayout(props_group)

        info_label = QLabel(
            "Формат в MD: <b>~={тег}текст=~</b>\n"
            "Тег может быть именем из списка или hex-цветом (FF0000, #00FF00)."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 5px;")
        props_layout.addWidget(info_label)

        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("Имя тега:"))
        self.tag_name_edit = QLineEdit()
        self.tag_name_edit.setPlaceholderText("blue")
        self.tag_name_edit.textChanged.connect(self._on_prop_changed)
        tag_row.addWidget(self.tag_name_edit)
        props_layout.addLayout(tag_row)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Цвет:"))
        self.color_picker = ColorPickerWidget()
        self.color_picker.color_changed.connect(self._on_color_changed)
        color_row.addWidget(self.color_picker)
        color_row.addStretch()
        props_layout.addLayout(color_row)

        props_layout.addStretch()
        layout.addWidget(props_group, stretch=2)

    def load_data(self, data: Dict[str, str]):
        self._colors_data = dict(data)
        self._populate_list()
        if self.tag_list.count() > 0:
            self.tag_list.setCurrentRow(0)

    def get_data(self) -> Dict[str, str]:
        return dict(self._colors_data)

    def _populate_list(self):
        self.tag_list.blockSignals(True)
        self.tag_list.clear()
        for key in sorted(self._colors_data.keys()):
            item = QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tag_list.addItem(item)
        self.tag_list.blockSignals(False)

    def _on_add(self):
        base = "new_color"
        name = base
        idx = 1
        while name in self._colors_data:
            idx += 1
            name = f"{base}_{idx}"
        self._colors_data[name] = "000000"
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tag_list.addItem(item)
        self.tag_list.setCurrentRow(self.tag_list.count() - 1)
        self.data_changed.emit()

    def _on_delete(self):
        item = self.tag_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить цветовой тег '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if name in self._colors_data:
            del self._colors_data[name]
        row = self.tag_list.row(item)
        self.tag_list.takeItem(row)
        self.data_changed.emit()
        if self.tag_list.count() > 0:
            self.tag_list.setCurrentRow(0)

    def _on_selected(self, row: int):
        if row < 0 or row >= self.tag_list.count():
            return
        name = self.tag_list.item(row).text()
        color = self._colors_data.get(name, "000000")
        self._updating = True
        self.tag_name_edit.setText(name)
        self.color_picker.set_color(color)
        self._updating = False

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._renaming_old = item.text()

    def _on_item_renamed(self, item: QListWidgetItem):
        old_name = self._renaming_old
        new_name = item.text().strip()
        if not new_name or new_name == old_name:
            return
        if new_name in self._colors_data:
            QMessageBox.warning(self, "Ошибка",
                               f"Тег '{new_name}' уже существует")
            self.tag_list.blockSignals(True)
            item.setText(old_name)
            self.tag_list.blockSignals(False)
            return
        self._colors_data[new_name] = self._colors_data.pop(old_name)
        self.data_changed.emit()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._renaming_old = item.text()

    def _on_prop_changed(self):
        if self._updating:
            return
        item = self.tag_list.currentItem()
        if not item:
            return
        new_name = self.tag_name_edit.text().strip()
        if not new_name:
            return
        old_name = item.text()
        if new_name != old_name:
            if new_name in self._colors_data:
                QMessageBox.warning(self, "Ошибка",
                                   f"Тег '{new_name}' уже существует")
                return
            self._colors_data[new_name] = self._colors_data.pop(old_name)
            self.tag_list.blockSignals(True)
            item.setText(new_name)
            self.tag_list.blockSignals(False)
        self.data_changed.emit()

    def _on_color_changed(self, hex_color: str):
        if self._updating:
            return
        item = self.tag_list.currentItem()
        if not item:
            return
        name = item.text()
        self._colors_data[name] = hex_color
        self.data_changed.emit()
