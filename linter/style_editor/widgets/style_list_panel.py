from __future__ import annotations

from typing import Optional, List, Set

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal


class StyleListPanel(QWidget):
    style_selected = pyqtSignal(str)
    style_created = pyqtSignal(str)
    style_deleted = pyqtSignal(str)
    save_requested = pyqtSignal()
    style_renamed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._style_names: Set[str] = set()
        self._renaming_old_name: str = ""

        self._setup_ui()

    def _setup_ui(self):
        group = QGroupBox("\u0421\u0442\u0438\u043B\u0438")
        layout = QVBoxLayout(group)

        btn_layout = QHBoxLayout()
        self.new_btn = QPushButton("+ \u041D\u043E\u0432\u044B\u0439")
        self.new_btn.clicked.connect(self._add_new_style)
        btn_layout.addWidget(self.new_btn)

        self.delete_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.style_list = QListWidget()
        self.style_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.style_list.currentRowChanged.connect(self._on_current_row_changed)
        self.style_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.style_list.itemChanged.connect(self._on_item_renamed)
        layout.addWidget(self.style_list)

        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("[>] \u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C JSON")
        self.save_btn.clicked.connect(self.save_requested.emit)
        save_layout.addWidget(self.save_btn)
        layout.addLayout(save_layout)

        outer = QVBoxLayout(self)
        outer.addWidget(group)

    def set_style_names(self, names: List[str]):
        self._style_names = set(names)
        self.style_list.clear()
        for name in sorted(names):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.style_list.addItem(item)
        if self.style_list.count() > 0:
            self.style_list.setCurrentRow(0)

    def current_style_name(self) -> Optional[str]:
        item = self.style_list.currentItem()
        return item.text() if item else None

    def select_style(self, name: str):
        for i in range(self.style_list.count()):
            if self.style_list.item(i).text() == name:
                self.style_list.setCurrentRow(i)
                return

    def rename_style(self, old_name: str, new_name: str) -> bool:
        if not new_name:
            return False
        if new_name == old_name:
            return False
        if new_name in self._style_names:
            QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430",
                               f"\u0421\u0442\u0438\u043B\u044C '{new_name}' \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442")
            return False

        self._style_names.discard(old_name)
        self._style_names.add(new_name)

        for i in range(self.style_list.count()):
            if self.style_list.item(i).text() == old_name:
                self.style_list.blockSignals(True)
                self.style_list.item(i).setText(new_name)
                self.style_list.sortItems()
                self.style_list.blockSignals(False)
                break

        self._renaming_old_name = old_name
        self.style_renamed.emit(old_name, new_name)
        self._renaming_old_name = ""
        return True

    def _add_new_style(self):
        base = "new_style"
        name = base
        idx = 1
        while name in self._style_names:
            idx += 1
            name = f"{base}_{idx}"

        self._style_names.add(name)
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.style_list.addItem(item)
        self.style_list.setCurrentRow(self.style_list.count() - 1)
        self.style_created.emit(name)

    def _delete_selected(self):
        item = self.style_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(
            self, "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435",
            f"\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u044C '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self._style_names.discard(name)
        row = self.style_list.row(item)
        self.style_list.takeItem(row)
        self.style_deleted.emit(name)

    def _on_current_row_changed(self, row: int):
        if row < 0 or row >= self.style_list.count():
            return
        name = self.style_list.item(row).text()
        self.style_selected.emit(name)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._renaming_old_name = item.text()

    def _on_item_renamed(self, item: QListWidgetItem):
        new_name = item.text().strip()
        if not new_name or new_name == self._renaming_old_name:
            self.style_list.blockSignals(True)
            item.setText(self._renaming_old_name)
            self.style_list.blockSignals(False)
            self._renaming_old_name = ""
            return

        old = self._renaming_old_name
        if new_name in self._style_names and new_name != old:
            QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430",
                               f"\u0421\u0442\u0438\u043B\u044C '{new_name}' \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442")
            self.style_list.blockSignals(True)
            item.setText(old)
            self.style_list.blockSignals(False)
            self._renaming_old_name = ""
            return

        self._style_names.discard(old)
        self._style_names.add(new_name)
        self.style_list.blockSignals(True)
        self.style_list.sortItems()
        self.style_list.blockSignals(False)
        self._renaming_old_name = ""
        self.style_renamed.emit(old, new_name)
