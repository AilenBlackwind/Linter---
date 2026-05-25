from __future__ import annotations

from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..widgets.color_picker import ColorPickerWidget
from linter.converter.tables.advanced.models import ColorRule


class ColorRulesWidget(QWidget):
    rules_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: List[ColorRule] = []
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("+ \u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u0438\u043B\u043E")
        self.add_rule_btn.clicked.connect(self._add_rule)
        btn_layout.addWidget(self.add_rule_btn)

        self.remove_rule_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        self.remove_rule_btn.clicked.connect(self._remove_rule)
        btn_layout.addWidget(self.remove_rule_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(7)
        self.rules_table.setHorizontalHeaderLabels([
            "\u0418\u043C\u044F", "\u0422\u0440\u0438\u0433\u0433\u0435\u0440", "\u041A\u043E\u043B\u043E\u043D\u043A\u0430", "\u0417\u043D\u0430\u0447\u0435\u043D\u0438\u0435", "\u0417\u0430\u043B\u0438\u0432\u043A\u0430", "\u0416\u0438\u0440\u043D\u044B\u0439", "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rules_table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.rules_table)

        details_group = QGroupBox("\u0414\u0435\u0442\u0430\u043B\u0438 \u043F\u0440\u0430\u0432\u0438\u043B\u0430")
        details_layout = QVBoxLayout(details_group)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("\u0418\u043C\u044F:"))
        self.rule_name_edit = QLineEdit()
        self.rule_name_edit.textChanged.connect(self._update_current_rule)
        name_layout.addWidget(self.rule_name_edit)
        details_layout.addLayout(name_layout)

        trigger_layout = QHBoxLayout()
        trigger_layout.addWidget(QLabel("\u0422\u0440\u0438\u0433\u0433\u0435\u0440:"))
        self.rule_trigger_combo = QComboBox()
        self.rule_trigger_combo.addItems([
            "equals (\u0440\u0430\u0432\u043D\u043E)", "contains (\u0441\u043E\u0434\u0435\u0440\u0436\u0438\u0442)",
            "starts_with (\u043D\u0430\u0447\u0438\u043D\u0430\u0435\u0442\u0441\u044F \u0441)", "ends_with (\u0437\u0430\u043A\u0430\u043D\u0447\u0438\u0432\u0430\u0435\u0442\u0441\u044F \u043D\u0430)",
            "matches_regex (\u0440\u0435\u0433\u0443\u043B\u044F\u0440\u043A\u0430)",
            "has_text (\u0435\u0441\u0442\u044C \u0442\u0435\u043A\u0441\u0442 \u0432 \u043A\u043E\u043B\u043E\u043D\u043A\u0435)"
        ])
        self.rule_trigger_combo.currentIndexChanged.connect(self._on_trigger_changed)
        trigger_layout.addWidget(self.rule_trigger_combo)
        details_layout.addLayout(trigger_layout)

        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("\u041A\u043E\u043B\u043E\u043D\u043A\u0430:"))
        self.rule_column_combo = QComboBox()
        self.rule_column_combo.addItems(["-", "A", "B", "C", "D", "E", "F"])
        self.rule_column_combo.setEnabled(False)
        self.rule_column_combo.currentIndexChanged.connect(self._update_current_rule)
        column_layout.addWidget(self.rule_column_combo)
        column_layout.addStretch()
        details_layout.addLayout(column_layout)

        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("\u0417\u043D\u0430\u0447\u0435\u043D\u0438\u0435:"))
        self.rule_value_edit = QLineEdit()
        self.rule_value_edit.textChanged.connect(self._update_current_rule)
        value_layout.addWidget(self.rule_value_edit)
        details_layout.addLayout(value_layout)

        self.rule_case_sensitive_cb = QCheckBox("\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u043E\u0437\u0430\u0432\u0438\u0441\u0438\u043C\u044B\u0439")
        self.rule_case_sensitive_cb.stateChanged.connect(self._update_current_rule)
        details_layout.addWidget(self.rule_case_sensitive_cb)

        apply_group = QGroupBox("\u041F\u0440\u0438\u043C\u0435\u043D\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u0438:")
        apply_layout = QVBoxLayout(apply_group)

        shading_layout = QHBoxLayout()
        self.rule_shading_cb = QCheckBox("\u0417\u0430\u043B\u0438\u0432\u043A\u0430:")
        self.rule_shading_cb.stateChanged.connect(self._update_current_rule)
        shading_layout.addWidget(self.rule_shading_cb)
        self.rule_shading_picker = ColorPickerWidget()
        self.rule_shading_picker.color_changed.connect(self._update_current_rule)
        shading_layout.addWidget(self.rule_shading_picker)
        shading_layout.addStretch()
        apply_layout.addLayout(shading_layout)

        font_color_layout = QHBoxLayout()
        self.rule_font_color_cb = QCheckBox("\u0426\u0432\u0435\u0442 \u0448\u0440\u0438\u0444\u0442\u0430:")
        self.rule_font_color_cb.stateChanged.connect(self._update_current_rule)
        font_color_layout.addWidget(self.rule_font_color_cb)
        self.rule_font_color_picker = ColorPickerWidget()
        self.rule_font_color_picker.set_color("000000")
        self.rule_font_color_picker.color_changed.connect(self._update_current_rule)
        font_color_layout.addWidget(self.rule_font_color_picker)
        font_color_layout.addStretch()
        apply_layout.addLayout(font_color_layout)

        font_style_layout = QHBoxLayout()
        self.rule_bold_cb = QCheckBox("\u0416\u0438\u0440\u043D\u044B\u0439")
        self.rule_bold_cb.setTristate(True)
        self.rule_bold_cb.stateChanged.connect(self._update_current_rule)
        font_style_layout.addWidget(self.rule_bold_cb)

        self.rule_italic_cb = QCheckBox("\u041A\u0443\u0440\u0441\u0438\u0432")
        self.rule_italic_cb.setTristate(True)
        self.rule_italic_cb.stateChanged.connect(self._update_current_rule)
        font_style_layout.addWidget(self.rule_italic_cb)
        font_style_layout.addStretch()
        apply_layout.addLayout(font_style_layout)

        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442:"))
        self.rule_priority_spin = QSpinBox()
        self.rule_priority_spin.setRange(-100, 100)
        self.rule_priority_spin.setValue(0)
        self.rule_priority_spin.valueChanged.connect(self._update_current_rule)
        priority_layout.addWidget(self.rule_priority_spin)
        priority_layout.addStretch()
        apply_layout.addLayout(priority_layout)

        details_layout.addWidget(apply_group)
        layout.addWidget(details_group)

        self.rules_table.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_trigger_changed(self, idx):
        is_has_text = idx == 5
        self.rule_column_combo.setEnabled(is_has_text)
        self.rule_value_edit.setEnabled(not is_has_text)
        self._update_current_rule()

    def _add_rule(self):
        rule = ColorRule(
            name="\u041D\u043E\u0432\u043E\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u043E",
            trigger="equals",
            value="",
            priority=0
        )
        self._rules.append(rule)
        self._refresh_table()
        self.rules_table.selectRow(len(self._rules) - 1)
        self.rules_changed.emit()

    def _remove_rule(self):
        rows = self.rules_table.selectedItems()
        if rows:
            row = rows[0].row()
            if 0 <= row < len(self._rules):
                del self._rules[row]
                self._refresh_table()
                self.rules_changed.emit()

    def _refresh_table(self):
        self.rules_table.blockSignals(True)
        self.rules_table.setRowCount(len(self._rules))

        for i, rule in enumerate(self._rules):
            self.rules_table.setItem(i, 0, QTableWidgetItem(rule.name))
            self.rules_table.setItem(i, 1, QTableWidgetItem(rule.trigger))
            self.rules_table.setItem(i, 2, QTableWidgetItem(rule.column or ""))
            self.rules_table.setItem(i, 3, QTableWidgetItem(rule.value))
            self.rules_table.setItem(i, 4, QTableWidgetItem(rule.shading or ""))
            self.rules_table.setItem(i, 5, QTableWidgetItem("\u2713" if rule.bold else ""))
            self.rules_table.setItem(i, 6, QTableWidgetItem(str(rule.priority)))

        self.rules_table.blockSignals(False)

    def _on_item_changed(self, item):
        row = item.row()
        if 0 <= row < len(self._rules):
            col = item.column()
            if col == 0:
                self._rules[row].name = item.text()
            elif col == 2:
                self._rules[row].column = item.text() or None
            elif col == 3:
                self._rules[row].value = item.text()
            elif col == 6:
                try:
                    self._rules[row].priority = int(item.text())
                except ValueError:
                    pass
            self.rules_changed.emit()

    def _on_selection_changed(self):
        rows = self.rules_table.selectedItems()
        if rows:
            row = rows[0].row()
            if 0 <= row < len(self._rules):
                self._load_rule_to_editor(self._rules[row])

    def _load_rule_to_editor(self, rule: ColorRule):
        self._updating = True

        self.rule_name_edit.setText(rule.name)

        triggers = ["equals", "contains", "starts_with", "ends_with", "matches_regex", "has_text"]
        if rule.trigger in triggers:
            self.rule_trigger_combo.setCurrentIndex(triggers.index(rule.trigger))

        is_has_text = rule.trigger == "has_text"
        self.rule_column_combo.setEnabled(is_has_text)
        self.rule_value_edit.setEnabled(not is_has_text)
        if rule.column and rule.column in ["A", "B", "C", "D", "E", "F"]:
            self.rule_column_combo.setCurrentText(rule.column)
        else:
            self.rule_column_combo.setCurrentIndex(0)

        self.rule_value_edit.setText(rule.value)
        self.rule_case_sensitive_cb.setChecked(rule.case_sensitive)

        if rule.shading:
            self.rule_shading_cb.setChecked(True)
            self.rule_shading_picker.set_color(rule.shading)
        else:
            self.rule_shading_cb.setChecked(False)

        if rule.font_color:
            self.rule_font_color_cb.setChecked(True)
            self.rule_font_color_picker.set_color(rule.font_color)
        else:
            self.rule_font_color_cb.setChecked(False)

        if rule.bold is None:
            self.rule_bold_cb.setCheckState(Qt.PartiallyChecked)
        elif rule.bold:
            self.rule_bold_cb.setCheckState(Qt.Checked)
        else:
            self.rule_bold_cb.setCheckState(Qt.Unchecked)

        if rule.italic is None:
            self.rule_italic_cb.setCheckState(Qt.PartiallyChecked)
        elif rule.italic:
            self.rule_italic_cb.setCheckState(Qt.Checked)
        else:
            self.rule_italic_cb.setCheckState(Qt.Unchecked)

        self.rule_priority_spin.setValue(rule.priority)

        self._updating = False

    def _update_current_rule(self):
        if hasattr(self, '_updating') and self._updating:
            return

        rows = self.rules_table.selectedItems()
        if rows:
            row = rows[0].row()
            if 0 <= row < len(self._rules):
                rule = self._rules[row]
                rule.name = self.rule_name_edit.text()

                triggers = ["equals", "contains", "starts_with", "ends_with", "matches_regex", "has_text"]
                rule.trigger = triggers[self.rule_trigger_combo.currentIndex()]

                col_text = self.rule_column_combo.currentText()
                rule.column = col_text if col_text != "-" else None

                rule.value = self.rule_value_edit.text()
                rule.case_sensitive = self.rule_case_sensitive_cb.isChecked()

                if self.rule_shading_cb.isChecked():
                    rule.shading = self.rule_shading_picker.get_color()
                else:
                    rule.shading = None

                if self.rule_font_color_cb.isChecked():
                    rule.font_color = self.rule_font_color_picker.get_color()
                else:
                    rule.font_color = None

                bold_state = self.rule_bold_cb.checkState()
                if bold_state == Qt.PartiallyChecked:
                    rule.bold = None
                else:
                    rule.bold = bold_state == Qt.Checked

                italic_state = self.rule_italic_cb.checkState()
                if italic_state == Qt.PartiallyChecked:
                    rule.italic = None
                else:
                    rule.italic = italic_state == Qt.Checked

                rule.priority = self.rule_priority_spin.value()

                self._refresh_table()
                self.rules_changed.emit()

    def set_rules(self, rules: List[ColorRule]):
        self._rules = [ColorRule(
            name=r.name,
            trigger=r.trigger,
            value=r.value,
            case_sensitive=r.case_sensitive,
            column=r.column,
            shading=r.shading,
            font_color=r.font_color,
            bold=r.bold,
            italic=r.italic,
            priority=r.priority,
            borders=r.borders
        ) for r in rules]
        self._refresh_table()

    def get_rules(self) -> List[ColorRule]:
        return self._rules
