from __future__ import annotations

from typing import Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QGroupBox, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..widgets.color_picker import ColorPickerWidget


class TableStructurePanel(QWidget):
    tag_changed = pyqtSignal(str)
    structure_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False
        self._paragraph_styles: list[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tag_group = QGroupBox("\u0422\u0435\u0433 \u0432 Markdown")
        tag_layout = QVBoxLayout(tag_group)
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("‹!style_name›")
        self.tag_edit.editingFinished.connect(self._on_tag_changed)
        tag_layout.addWidget(self.tag_edit)
        layout.addWidget(tag_group)

        style_group = QGroupBox("\u0421\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432")
        style_layout = QVBoxLayout(style_group)

        style_layout.addWidget(QLabel("\u0421\u0442\u0438\u043B\u044C \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u0430:"))
        self.header_style_combo = QComboBox()
        self.header_style_combo.setEditable(True)
        self.header_style_combo.setInsertPolicy(QComboBox.NoInsert)
        self.header_style_combo.currentTextChanged.connect(self._on_structure_changed)
        style_layout.addWidget(self.header_style_combo)

        style_layout.addWidget(QLabel("\u0421\u0442\u0438\u043B\u044C \u0442\u0435\u043A\u0441\u0442\u0430:"))
        self.text_style_combo = QComboBox()
        self.text_style_combo.setEditable(True)
        self.text_style_combo.setInsertPolicy(QComboBox.NoInsert)
        self.text_style_combo.currentTextChanged.connect(self._on_structure_changed)
        style_layout.addWidget(self.text_style_combo)

        layout.addWidget(style_group)

        wrap_group = QGroupBox("\u041E\u0431\u0442\u0435\u043A\u0430\u043D\u0438\u0435 \u0442\u0435\u043A\u0441\u0442\u043E\u043C")
        wrap_layout = QVBoxLayout(wrap_group)

        wrap_type_layout = QHBoxLayout()
        wrap_type_layout.addWidget(QLabel("\u0422\u0438\u043F:"))
        self.wrap_type_combo = QComboBox()
        self.wrap_type_combo.addItems(["\u0412\u043E\u043A\u0440\u0443\u0433", "\u041D\u0435\u0442 (\u0432\u0441\u0442\u0440\u043E\u0435\u043D\u043D\u043E\u0435)"])
        self.wrap_type_combo.currentIndexChanged.connect(self._on_wrap_type_changed)
        wrap_type_layout.addWidget(self.wrap_type_combo)
        wrap_layout.addLayout(wrap_type_layout)

        wrap_left_layout = QHBoxLayout()
        wrap_left_layout.addWidget(QLabel("\u041E\u0442\u0441\u0442\u0443\u043F \u0441\u043B\u0435\u0432\u0430:"))
        self.left_from_text_spin = QSpinBox()
        self.left_from_text_spin.setRange(0, 100)
        self.left_from_text_spin.setValue(0)
        self.left_from_text_spin.setSuffix(" \u043F\u0442")
        self.left_from_text_spin.valueChanged.connect(self._on_structure_changed)
        wrap_left_layout.addWidget(self.left_from_text_spin)
        wrap_layout.addLayout(wrap_left_layout)

        wrap_right_layout = QHBoxLayout()
        wrap_right_layout.addWidget(QLabel("\u041E\u0442\u0441\u0442\u0443\u043F \u0441\u043F\u0440\u0430\u0432\u0430:"))
        self.right_from_text_spin = QSpinBox()
        self.right_from_text_spin.setRange(0, 100)
        self.right_from_text_spin.setValue(0)
        self.right_from_text_spin.setSuffix(" \u043F\u0442")
        self.right_from_text_spin.valueChanged.connect(self._on_structure_changed)
        wrap_right_layout.addWidget(self.right_from_text_spin)
        wrap_layout.addLayout(wrap_right_layout)

        layout.addWidget(wrap_group)

        sizing_group = QGroupBox("\u0420\u0430\u0437\u043C\u0435\u0440\u044B \u0442\u0430\u0431\u043B\u0438\u0446\u044B")
        sizing_layout = QVBoxLayout(sizing_group)

        self.use_widths_cb = QCheckBox("\u0428\u0438\u0440\u0438\u043D\u0430 \u0441\u0442\u043E\u043B\u0431\u0446\u043E\u0432 (\u0432 %)")
        self.use_widths_cb.stateChanged.connect(self._on_widths_enabled)
        sizing_layout.addWidget(self.use_widths_cb)

        self.width_spins = []
        self.width_checkboxes = []
        width_grid = QGridLayout()
        col_labels = ["A", "B", "C", "D", "E", "F"]
        for i in range(6):
            cb = QCheckBox()
            cb.setEnabled(False)
            cb.stateChanged.connect(self._on_width_checkbox_toggled)
            self.width_checkboxes.append(cb)

            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setValue(16)
            spin.setSuffix("%")
            spin.setEnabled(False)
            spin.valueChanged.connect(self._on_width_spin_value_changed)
            self.width_spins.append(spin)

            row_pos = i // 3
            base_col = (i % 3) * 3
            width_grid.addWidget(cb, row_pos, base_col)
            width_grid.addWidget(QLabel(col_labels[i]), row_pos, base_col + 1)
            width_grid.addWidget(spin, row_pos, base_col + 2)
        sizing_layout.addLayout(width_grid)

        self.fit_page_cb = QCheckBox("\u0412\u043F\u0438\u0441\u044B\u0432\u0430\u0442\u044C \u0432 \u0448\u0438\u0440\u0438\u043D\u0443 \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u044B")
        self.fit_page_cb.setChecked(True)
        self.fit_page_cb.stateChanged.connect(self._on_fit_page_toggled)
        sizing_layout.addWidget(self.fit_page_cb)

        tw_layout = QHBoxLayout()
        tw_layout.addWidget(QLabel("\u0428\u0438\u0440\u0438\u043D\u0430 \u0442\u0430\u0431\u043B\u0438\u0446\u044B:"))
        self.table_width_spin = QSpinBox()
        self.table_width_spin.setRange(100, 5000)
        self.table_width_spin.setValue(800)
        self.table_width_spin.setSuffix(" px")
        self.table_width_spin.setEnabled(False)
        self.table_width_spin.valueChanged.connect(self._on_structure_changed)
        tw_layout.addWidget(self.table_width_spin)
        tw_layout.addStretch()
        sizing_layout.addLayout(tw_layout)

        self.use_heights_cb = QCheckBox("\u0412\u044B\u0441\u043E\u0442\u0430 \u0441\u0442\u0440\u043E\u043A")
        self.use_heights_cb.stateChanged.connect(self._on_heights_enabled)
        sizing_layout.addWidget(self.use_heights_cb)

        self.height_spins = []
        height_grid = QGridLayout()
        for i in range(6):
            spin = QSpinBox()
            spin.setRange(0, 5000)
            spin.setValue(300)
            spin.setSuffix(" twip")
            spin.setEnabled(False)
            spin.valueChanged.connect(self._on_structure_changed)
            self.height_spins.append(spin)
            height_grid.addWidget(QLabel(f"\u0421\u0442\u0440. {i + 1}"), i // 2, (i % 2) * 2)
            height_grid.addWidget(spin, i // 2, (i % 2) * 2 + 1)
        sizing_layout.addLayout(height_grid)

        layout.addWidget(sizing_group)
        layout.addStretch()

        empty_group = QGroupBox("\u041F\u0443\u0441\u0442\u044B\u0435 \u0441\u0442\u0440\u043E\u043A\u0438 \u0432\u043E\u043A\u0440\u0443\u0433 \u0442\u0430\u0431\u043B\u0438\u0446\u044B")
        empty_layout = QVBoxLayout(empty_group)

        self.empty_row_top_cb = QCheckBox("\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043F\u0443\u0441\u0442\u0443\u044E \u0441\u0442\u0440\u043E\u043A\u0443 \u0441\u0432\u0435\u0440\u0445\u0443")
        self.empty_row_top_cb.stateChanged.connect(self._on_structure_changed)
        empty_layout.addWidget(self.empty_row_top_cb)

        self.empty_row_bottom_cb = QCheckBox("\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043F\u0443\u0441\u0442\u0443\u044E \u0441\u0442\u0440\u043E\u043A\u0443 \u0441\u043D\u0438\u0437\u0443")
        self.empty_row_bottom_cb.stateChanged.connect(self._on_structure_changed)
        empty_layout.addWidget(self.empty_row_bottom_cb)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("\u0412\u044B\u0441\u043E\u0442\u0430:"))
        self.empty_row_height_spin = QSpinBox()
        self.empty_row_height_spin.setRange(20, 5000)
        self.empty_row_height_spin.setValue(200)
        self.empty_row_height_spin.setSuffix(" twip")
        self.empty_row_height_spin.valueChanged.connect(self._on_structure_changed)
        height_layout.addWidget(self.empty_row_height_spin)
        height_layout.addStretch()
        empty_layout.addLayout(height_layout)

        layout.addWidget(empty_group)

    def load_paragraph_styles(self, template_or_styles):
        self._paragraph_styles = []
        if isinstance(template_or_styles, list):
            self._paragraph_styles = sorted(template_or_styles)
        else:
            try:
                from docx import Document
                doc = Document(template_or_styles)
                self._paragraph_styles = sorted(
                    s.name for s in doc.styles
                    if s.type is not None and s.type == 1
                )
            except Exception as e:
                print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u0438 \u0438\u0437 \u0448\u0430\u0431\u043B\u043E\u043D\u0430: {e}")
                self._paragraph_styles = []

        self._updating = True
        self.header_style_combo.clear()
        self.text_style_combo.clear()
        for name in self._paragraph_styles:
            self.header_style_combo.addItem(name)
            self.text_style_combo.addItem(name)
        self._updating = False

    def get_header_style(self) -> str:
        return self.header_style_combo.currentText().strip()

    def set_header_style(self, name: str, block_signals=True):
        if block_signals:
            self._updating = True
        idx = self.header_style_combo.findText(name)
        if idx >= 0:
            self.header_style_combo.setCurrentIndex(idx)
        else:
            self.header_style_combo.setCurrentText(name)
        if block_signals:
            self._updating = False

    def get_text_style(self) -> str:
        return self.text_style_combo.currentText().strip()

    def set_text_style(self, name: str, block_signals=True):
        if block_signals:
            self._updating = True
        idx = self.text_style_combo.findText(name)
        if idx >= 0:
            self.text_style_combo.setCurrentIndex(idx)
        else:
            self.text_style_combo.setCurrentText(name)
        if block_signals:
            self._updating = False

    def _on_tag_changed(self):
        if not self._updating:
            self.tag_changed.emit(self.tag_edit.text().strip())

    def set_tag(self, tag: str, block_signals=True):
        if block_signals:
            self._updating = True
        self.tag_edit.setText(tag)
        if block_signals:
            self._updating = False

    def get_tag(self) -> str:
        return self.tag_edit.text().strip()

    def _on_structure_changed(self):
        if not self._updating:
            self.structure_changed.emit()

    def _on_wrap_type_changed(self, index):
        is_around = (index == 0)
        self.left_from_text_spin.setEnabled(is_around)
        self.right_from_text_spin.setEnabled(is_around)
        self._on_structure_changed()

    def _on_widths_enabled(self, state):
        enabled = state == Qt.Checked
        for spin in self.width_spins:
            spin.setEnabled(enabled)
        for cb in self.width_checkboxes:
            cb.setEnabled(enabled)
        self._on_structure_changed()

    def _on_heights_enabled(self, state):
        enabled = state == Qt.Checked
        for spin in self.height_spins:
            spin.setEnabled(enabled)
        self._on_structure_changed()

    def _on_fit_page_toggled(self, state):
        self.table_width_spin.setEnabled(state != Qt.Checked)
        self._on_structure_changed()

    def auto_distribute_widths(self, selected_columns: set[int]):
        if self._updating or self.use_widths_cb.checkState() != Qt.Checked:
            return
        if any(cb.isChecked() for cb in self.width_checkboxes):
            return
        values = [spin.value() for spin in self.width_spins]
        selected_sum = sum(values[col] for col in selected_columns if col < 6)
        remaining = max(0, 100 - selected_sum)

        unselected_nonzero = [col for col in range(6) if col not in selected_columns and values[col] > 0]
        current_sum = sum(values[col] for col in unselected_nonzero)

        if unselected_nonzero and remaining != current_sum:
            self._updating = True
            per_col = remaining // len(unselected_nonzero)
            rem = remaining % len(unselected_nonzero)
            for i, col in enumerate(unselected_nonzero):
                self.width_spins[col].setValue(per_col + (1 if i < rem else 0))
            self._updating = False

    def _on_width_spin_value_changed(self):
        if self._updating:
            return
        if self.use_widths_cb.checkState() != Qt.Checked:
            return

        checked = [i for i in range(6) if self.width_checkboxes[i].isChecked()]
        if not checked:
            self._on_structure_changed()
            return

        sender = self.sender()
        if sender not in self.width_spins:
            self._on_structure_changed()
            return

        changed_idx = self.width_spins.index(sender)
        if not self.width_checkboxes[changed_idx].isChecked():
            self._on_structure_changed()
            return

        self._updating = True

        target = self.width_spins[changed_idx].value()
        if target == 0:
            self._updating = False
            self._on_structure_changed()
            return

        checked_nonzero = [i for i in checked if self.width_spins[i].value() > 0]
        for i in checked_nonzero:
            if i != changed_idx:
                self.width_spins[i].setValue(target)

        checked_sum = target * len(checked_nonzero)
        remaining = max(0, 100 - checked_sum)

        unchecked_nonzero = [i for i in range(6) if not self.width_checkboxes[i].isChecked() and self.width_spins[i].value() > 0]
        if unchecked_nonzero and remaining >= 0:
            per_col = remaining // len(unchecked_nonzero)
            rem = remaining % len(unchecked_nonzero)
            for j, i in enumerate(unchecked_nonzero):
                self.width_spins[i].setValue(per_col + (1 if j < rem else 0))

        self._updating = False
        self._on_structure_changed()

    def _on_width_checkbox_toggled(self):
        if self._updating:
            return
        if self.use_widths_cb.checkState() != Qt.Checked:
            return

        checked = [i for i in range(6) if self.width_checkboxes[i].isChecked()]
        if not checked:
            return

        self._updating = True

        checked_nonzero = [i for i in checked if self.width_spins[i].value() > 0]
        if not checked_nonzero:
            self._updating = False
            return

        target_value = self.width_spins[checked_nonzero[0]].value()
        for i in checked_nonzero:
            self.width_spins[i].setValue(target_value)

        checked_sum = target_value * len(checked_nonzero)
        remaining = max(0, 100 - checked_sum)

        unchecked_nonzero = [i for i in range(6) if not self.width_checkboxes[i].isChecked() and self.width_spins[i].value() > 0]
        if unchecked_nonzero and remaining >= 0:
            per_col = remaining // len(unchecked_nonzero)
            rem = remaining % len(unchecked_nonzero)
            for j, i in enumerate(unchecked_nonzero):
                self.width_spins[i].setValue(per_col + (1 if j < rem else 0))

        self._updating = False
        self._on_structure_changed()

    PX_TO_EMU = 9525

    def get_column_widths(self) -> Optional[List[float]]:
        if self.use_widths_cb.checkState() == Qt.Checked:
            return [spin.value() / 100.0 for spin in self.width_spins]
        return None

    def set_column_widths(self, widths: Optional[List[float]], block_signals=True):
        if block_signals:
            self._updating = True
        if widths and len(widths) == 6:
            self.use_widths_cb.setCheckState(Qt.Checked)
            total = sum(widths)
            if total > 0:
                for i, spin in enumerate(self.width_spins):
                    pct = max(0, min(100, round(widths[i] / total * 100)))
                    spin.setValue(pct)
                    spin.setEnabled(True)
        else:
            self.use_widths_cb.setCheckState(Qt.Unchecked)
            for spin in self.width_spins:
                spin.setEnabled(False)
        if block_signals:
            self._updating = False

    def get_table_width(self) -> Optional[int]:
        if self.fit_page_cb.checkState() != Qt.Checked and self.table_width_spin.isEnabled():
            return self.table_width_spin.value() * self.PX_TO_EMU
        return None

    def set_table_width(self, width_emu: Optional[int], block_signals=True):
        if block_signals:
            self._updating = True
        if width_emu is not None and width_emu > 0:
            px = max(100, width_emu // self.PX_TO_EMU)
            self.table_width_spin.setValue(px)
        else:
            self.table_width_spin.setValue(800)
        if block_signals:
            self._updating = False

    def get_row_heights(self) -> Optional[List[int]]:
        if self.use_heights_cb.checkState() == Qt.Checked:
            return [spin.value() for spin in self.height_spins]
        return None

    def set_row_heights(self, heights: Optional[List[int]], block_signals=True):
        if block_signals:
            self._updating = True
        if heights and len(heights) == 6:
            self.use_heights_cb.setCheckState(Qt.Checked)
            for i, spin in enumerate(self.height_spins):
                spin.setValue(heights[i])
                spin.setEnabled(True)
        else:
            self.use_heights_cb.setCheckState(Qt.Unchecked)
            for spin in self.height_spins:
                spin.setEnabled(False)
        if block_signals:
            self._updating = False

    def get_fit_to_page(self) -> bool:
        return self.fit_page_cb.checkState() == Qt.Checked

    def set_fit_to_page(self, value: bool, block_signals=True):
        if block_signals:
            self._updating = True
        self.fit_page_cb.setChecked(value)
        self.table_width_spin.setEnabled(not value)
        if block_signals:
            self._updating = False

    def get_text_wrap(self) -> str:
        return "around" if self.wrap_type_combo.currentIndex() == 0 else "inline"

    def set_text_wrap(self, value: str, block_signals=True):
        if block_signals:
            self._updating = True
        idx = 0 if value == "around" else 1
        self.wrap_type_combo.setCurrentIndex(idx)
        is_around = (idx == 0)
        self.left_from_text_spin.setEnabled(is_around)
        self.right_from_text_spin.setEnabled(is_around)
        if block_signals:
            self._updating = False

    def get_left_from_text(self) -> int:
        return self.left_from_text_spin.value()

    def set_left_from_text(self, value: int, block_signals=True):
        if block_signals:
            self._updating = True
        self.left_from_text_spin.setValue(value)
        if block_signals:
            self._updating = False

    def get_right_from_text(self) -> int:
        return self.right_from_text_spin.value()

    def set_right_from_text(self, value: int, block_signals=True):
        if block_signals:
            self._updating = True
        self.right_from_text_spin.setValue(value)
        if block_signals:
            self._updating = False

    def get_empty_row_top(self) -> bool:
        return self.empty_row_top_cb.checkState() == Qt.Checked

    def set_empty_row_top(self, value: bool, block_signals=True):
        if block_signals:
            self._updating = True
        self.empty_row_top_cb.setChecked(value)
        if block_signals:
            self._updating = False

    def get_empty_row_bottom(self) -> bool:
        return self.empty_row_bottom_cb.checkState() == Qt.Checked

    def set_empty_row_bottom(self, value: bool, block_signals=True):
        if block_signals:
            self._updating = True
        self.empty_row_bottom_cb.setChecked(value)
        if block_signals:
            self._updating = False

    def get_empty_row_height(self) -> int:
        return self.empty_row_height_spin.value()

    def set_empty_row_height(self, value: int, block_signals=True):
        if block_signals:
            self._updating = True
        self.empty_row_height_spin.setValue(value)
        if block_signals:
            self._updating = False
