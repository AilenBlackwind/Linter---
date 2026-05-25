from __future__ import annotations

from typing import Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QDoubleSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..widgets.color_picker import ColorPickerWidget
from linter.converter.tables.advanced.models import BorderStyle


class PropertiesPanel(QWidget):
    property_changed = pyqtSignal()
    apply_border_clicked = pyqtSignal()
    clear_borders_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_target: str = "cell_override"
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        target_group = QGroupBox("\u0426\u0435\u043B\u044C \u0440\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u044F")
        target_layout = QVBoxLayout(target_group)

        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "\u041F\u043E \u0443\u043C\u043E\u043B\u0447\u0430\u043D\u0438\u044E (table_defaults)",
            "\u0417\u0430\u0433\u043E\u043B\u043E\u0432\u043E\u043A (header)",
            "\u041D\u0435\u0447\u0451\u0442\u043D\u044B\u0435 \u0441\u0442\u0440\u043E\u043A\u0438 (odd)",
            "\u0427\u0451\u0442\u043D\u044B\u0435 \u0441\u0442\u0440\u043E\u043A\u0438 (even)",
            "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u044F\u044F \u0441\u0442\u0440\u043E\u043A\u0430 (last_row)",
            "\u041F\u0435\u0440\u0432\u0430\u044F \u043A\u043E\u043B\u043E\u043D\u043A\u0430 (first_column)",
            "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u044F\u044F \u043A\u043E\u043B\u043E\u043D\u043A\u0430 (last_column)",
            "\u0412\u044B\u0431\u0440\u0430\u043D\u043D\u044B\u0435 \u044F\u0447\u0435\u0439\u043A\u0438 (cell_override)",
        ])
        self.target_combo.setCurrentIndex(7)
        self.target_combo.currentIndexChanged.connect(self._on_target_changed)
        target_layout.addWidget(self.target_combo)

        layout.addWidget(target_group)

        shading_group = QGroupBox("\u0417\u0430\u043B\u0438\u0432\u043A\u0430")
        shading_layout = QVBoxLayout(shading_group)

        self.use_shading_cb = QCheckBox("\u0418\u0441\u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u044C \u0437\u0430\u043B\u0438\u0432\u043A\u0443")
        self.use_shading_cb.stateChanged.connect(self._on_shading_enabled)
        shading_layout.addWidget(self.use_shading_cb)

        shading_color_layout = QHBoxLayout()
        shading_color_layout.addWidget(QLabel("\u0426\u0432\u0435\u0442:"))
        self.shading_picker = ColorPickerWidget()
        self.shading_picker.color_changed.connect(self._on_property_changed)
        shading_color_layout.addWidget(self.shading_picker)
        shading_color_layout.addStretch()
        shading_layout.addLayout(shading_color_layout)

        layout.addWidget(shading_group)

        font_group = QGroupBox("\u0428\u0440\u0438\u0444\u0442")
        font_layout = QVBoxLayout(font_group)

        self.use_bold_cb = QCheckBox("\u0416\u0438\u0440\u043D\u044B\u0439")
        self.use_bold_cb.setTristate(True)
        self.use_bold_cb.stateChanged.connect(self._on_property_changed)
        font_layout.addWidget(self.use_bold_cb)

        self.use_italic_cb = QCheckBox("\u041A\u0443\u0440\u0441\u0438\u0432")
        self.use_italic_cb.setTristate(True)
        self.use_italic_cb.stateChanged.connect(self._on_property_changed)
        font_layout.addWidget(self.use_italic_cb)

        font_color_layout = QHBoxLayout()
        self.use_font_color_cb = QCheckBox("\u0426\u0432\u0435\u0442 \u0448\u0440\u0438\u0444\u0442\u0430:")
        self.use_font_color_cb.stateChanged.connect(self._on_font_color_enabled)
        font_color_layout.addWidget(self.use_font_color_cb)
        self.font_color_picker = ColorPickerWidget()
        self.font_color_picker.color_changed.connect(self._on_property_changed)
        font_color_layout.addWidget(self.font_color_picker)
        font_color_layout.addStretch()
        font_layout.addLayout(font_color_layout)

        layout.addWidget(font_group)

        borders_group = QGroupBox("\u0413\u0440\u0430\u043D\u0438\u0446\u044B")
        borders_layout = QVBoxLayout(borders_group)

        sides_label = QLabel("\u0421\u0442\u043E\u0440\u043E\u043D\u044B:")
        borders_layout.addWidget(sides_label)

        sides_check_layout = QHBoxLayout()
        self.border_top_cb = QCheckBox("\u0412\u0435\u0440\u0445")
        self.border_bottom_cb = QCheckBox("\u041D\u0438\u0437")
        self.border_left_cb = QCheckBox("\u041B\u0435\u0432\u043E")
        self.border_right_cb = QCheckBox("\u041F\u0440\u0430\u0432\u043E")
        self.border_all_cb = QCheckBox("\u0412\u0441\u0435")
        self.border_all_cb.stateChanged.connect(self._on_border_all_toggled)
        for cb in [self.border_top_cb, self.border_bottom_cb, self.border_left_cb, self.border_right_cb]:
            cb.stateChanged.connect(self._on_border_side_toggled)
        sides_check_layout.addWidget(self.border_top_cb)
        sides_check_layout.addWidget(self.border_bottom_cb)
        sides_check_layout.addWidget(self.border_left_cb)
        sides_check_layout.addWidget(self.border_right_cb)
        sides_check_layout.addWidget(self.border_all_cb)
        borders_layout.addLayout(sides_check_layout)

        border_style_layout = QHBoxLayout()
        border_style_layout.addWidget(QLabel("\u0422\u0438\u043F:"))
        self.border_type_combo = QComboBox()
        self.border_type_combo.addItems(["single", "double", "dashed", "dotted", "nil"])
        border_style_layout.addWidget(self.border_type_combo)
        borders_layout.addLayout(border_style_layout)

        border_size_layout = QHBoxLayout()
        border_size_layout.addWidget(QLabel("\u0422\u043E\u043B\u0449\u0438\u043D\u0430:"))
        self.border_size_spin = QDoubleSpinBox()
        self.border_size_spin.setRange(0, 12.5)
        self.border_size_spin.setSingleStep(0.5)
        self.border_size_spin.setValue(1.0)
        self.border_size_spin.valueChanged.connect(self._on_property_changed)
        border_size_layout.addWidget(self.border_size_spin)
        border_size_layout.addWidget(QLabel("\u043F\u0442"))
        borders_layout.addLayout(border_size_layout)

        border_color_layout = QHBoxLayout()
        border_color_layout.addWidget(QLabel("\u0426\u0432\u0435\u0442:"))
        self.border_color_picker = ColorPickerWidget()
        self.border_color_picker.set_color("666666")
        border_color_layout.addWidget(self.border_color_picker)
        border_color_layout.addStretch()
        borders_layout.addLayout(border_color_layout)

        self.apply_border_btn = QPushButton("\u041F\u0440\u0438\u043C\u0435\u043D\u0438\u0442\u044C \u0433\u0440\u0430\u043D\u0438\u0446\u0443")
        self.apply_border_btn.clicked.connect(self._on_apply_border)
        borders_layout.addWidget(self.apply_border_btn)

        self.clear_border_btn = QPushButton("\u041E\u0447\u0438\u0441\u0442\u0438\u0442\u044C \u0433\u0440\u0430\u043D\u0438\u0446\u044B")
        self.clear_border_btn.clicked.connect(self._on_clear_borders)
        borders_layout.addWidget(self.clear_border_btn)

        layout.addWidget(borders_group)

        layout.addStretch()

    def _on_target_changed(self, index: int):
        targets = [
            "table_defaults", "header", "odd", "even",
            "last_row", "first_column", "last_column", "cell_override",
        ]
        self._current_target = targets[index]
        self.property_changed.emit()

    def _on_shading_enabled(self, state):
        enabled = state == Qt.Checked
        self.shading_picker.setEnabled(enabled)
        self._on_property_changed()

    def _on_font_color_enabled(self, state):
        enabled = state == Qt.Checked
        self.font_color_picker.setEnabled(enabled)
        self._on_property_changed()

    def _on_property_changed(self):
        if not self._updating:
            self.property_changed.emit()

    def _on_apply_border(self):
        self.apply_border_clicked.emit()

    def _on_clear_borders(self):
        self.clear_borders_clicked.emit()

    def get_target(self) -> str:
        return self._current_target

    def get_shading(self) -> Optional[str]:
        if self.use_shading_cb.checkState() == Qt.Checked:
            return self.shading_picker.get_color()
        return None

    def get_bold(self) -> Optional[bool]:
        state = self.use_bold_cb.checkState()
        if state == Qt.Checked:
            return True
        elif state == Qt.Unchecked:
            return False
        return None

    def get_italic(self) -> Optional[bool]:
        state = self.use_italic_cb.checkState()
        if state == Qt.Checked:
            return True
        elif state == Qt.Unchecked:
            return False
        return None

    def get_font_color(self) -> Optional[str]:
        if self.use_font_color_cb.checkState() == Qt.Checked:
            return self.font_color_picker.get_color()
        return None

    def set_shading(self, color: Optional[str], block_signals=True):
        if block_signals:
            self._updating = True
        if color:
            self.use_shading_cb.setCheckState(Qt.Checked)
            self.shading_picker.set_color(color)
            self.shading_picker.setEnabled(True)
        else:
            self.use_shading_cb.setCheckState(Qt.Unchecked)
            self.shading_picker.setEnabled(False)
        if block_signals:
            self._updating = False

    def set_bold(self, value: Optional[bool], block_signals=True):
        if block_signals:
            self._updating = True
        if value is None:
            self.use_bold_cb.setCheckState(Qt.PartiallyChecked)
        elif value:
            self.use_bold_cb.setCheckState(Qt.Checked)
        else:
            self.use_bold_cb.setCheckState(Qt.Unchecked)
        if block_signals:
            self._updating = False

    def set_italic(self, value: Optional[bool], block_signals=True):
        if block_signals:
            self._updating = True
        if value is None:
            self.use_italic_cb.setCheckState(Qt.PartiallyChecked)
        elif value:
            self.use_italic_cb.setCheckState(Qt.Checked)
        else:
            self.use_italic_cb.setCheckState(Qt.Unchecked)
        if block_signals:
            self._updating = False

    def set_font_color(self, color: Optional[str], block_signals=True):
        if block_signals:
            self._updating = True
        if color:
            self.use_font_color_cb.setCheckState(Qt.Checked)
            self.font_color_picker.set_color(color)
            self.font_color_picker.setEnabled(True)
        else:
            self.use_font_color_cb.setCheckState(Qt.Unchecked)
            self.font_color_picker.setEnabled(False)
        if block_signals:
            self._updating = False

    def _on_border_all_toggled(self, state):
        checked = state == Qt.Checked
        self.border_top_cb.setChecked(checked)
        self.border_bottom_cb.setChecked(checked)
        self.border_left_cb.setChecked(checked)
        self.border_right_cb.setChecked(checked)

    def _on_border_side_toggled(self, _state):
        all_checked = all([
            self.border_top_cb.isChecked(),
            self.border_bottom_cb.isChecked(),
            self.border_left_cb.isChecked(),
            self.border_right_cb.isChecked()
        ])
        self.border_all_cb.blockSignals(True)
        self.border_all_cb.setChecked(all_checked)
        self.border_all_cb.blockSignals(False)

    def get_border_sides(self) -> List[str]:
        sides = []
        if self.border_top_cb.isChecked():
            sides.append("top")
        if self.border_bottom_cb.isChecked():
            sides.append("bottom")
        if self.border_left_cb.isChecked():
            sides.append("left")
        if self.border_right_cb.isChecked():
            sides.append("right")
        if not sides:
            sides.append("all")
        return sides

    def get_border_side(self) -> str:
        checked = self.get_border_sides()
        if len(checked) == 4:
            return "all"
        if set(checked) == {"top", "bottom"}:
            return "horizontal"
        if set(checked) == {"left", "right"}:
            return "vertical"
        return checked[0] if checked else "all"



    def get_border_style(self) -> BorderStyle:
        return BorderStyle(
            color=self.border_color_picker.get_color(),
            size=int(self.border_size_spin.value() * 8),
            val=self.border_type_combo.currentText()
        )
