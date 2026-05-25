from __future__ import annotations

from typing import Dict, Any, Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QEvent

from ..style_data_manager import StyleDataManager


class ParagraphStylesPanel(QWidget):
    def __init__(self, data_manager: StyleDataManager,
                 paragraph_styles: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self._data_manager = data_manager
        self._paragraph_styles = paragraph_styles or []
        self._spacing_data: Dict[str, Any] = {}

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        spacing_group = QGroupBox("\u041E\u0442\u0441\u0442\u0443\u043F\u044B (\u0432 \u043F\u0442)")
        spacing_form = QVBoxLayout(spacing_group)

        self.spacing_widgets = {}

        spacing_fields = [
            ("before_heading", "\u041F\u0435\u0440\u0435\u0434 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u043E\u043C:"),
            ("after_heading", "\u041F\u043E\u0441\u043B\u0435 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u0430:"),
            ("after_list", "\u041F\u043E\u0441\u043B\u0435 \u0441\u043F\u0438\u0441\u043A\u0430:"),
            ("after_table", "\u041F\u043E\u0441\u043B\u0435 \u0442\u0430\u0431\u043B\u0438\u0446\u044B:"),
            ("table_before_heading", "\u041F\u0435\u0440\u0435\u0434 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u043E\u043C \u043F\u043E\u0441\u043B\u0435 \u0442\u0430\u0431\u043B\u0438\u0446\u044B:"),
        ]

        for key, label in spacing_fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            spin = QSpinBox()
            spin.setRange(0, 200)
            spin.setValue(0)
            spin.setSuffix(" \u043F\u0442")
            row.addWidget(spin)
            row.addStretch()
            spacing_form.addLayout(row)
            self.spacing_widgets[key] = spin

        scroll_layout.addWidget(spacing_group)

        para_group = QGroupBox("\u0421\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432")
        para_layout = QVBoxLayout(para_group)

        para_btn_layout = QHBoxLayout()
        self.add_para_btn = QPushButton("+ \u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C")
        self.add_para_btn.clicked.connect(self._add_para_style)
        para_btn_layout.addWidget(self.add_para_btn)
        self.remove_para_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        self.remove_para_btn.clicked.connect(self._remove_para_style)
        para_btn_layout.addWidget(self.remove_para_btn)
        para_btn_layout.addStretch()
        para_layout.addLayout(para_btn_layout)

        self.para_table = QTableWidget()
        self.para_table.setColumnCount(4)
        self.para_table.setHorizontalHeaderLabels(["\u041A\u043B\u044E\u0447", "\u0421\u0442\u0438\u043B\u044C \u0430\u0431\u0437\u0430\u0446\u0430", "\u0422\u0435\u0433", "\u0422\u0438\u043F"])
        self.para_table.horizontalHeader().setStretchLastSection(True)
        self.para_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.para_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.para_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.para_table.verticalHeader().setVisible(False)
        self.para_table.viewport().installEventFilter(self)
        self.para_table.verticalScrollBar().installEventFilter(self)
        para_layout.addWidget(self.para_table)

        scroll_layout.addWidget(para_group)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        self.save_general_btn = QPushButton("\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432")
        self.save_general_btn.clicked.connect(self._save_general_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_general_btn)
        layout.addLayout(btn_layout)

    def set_paragraph_styles(self, styles: List[str]):
        self._paragraph_styles = styles

    def load_settings(self):
        self._spacing_data = self._data_manager.load_spacing()
        for key, spin in self.spacing_widgets.items():
            val = self._spacing_data.get(key, 0)
            spin.setValue(val)
        self._populate_para_table()

    def save_settings(self, silent=False):
        errors = []
        try:
            for key, spin in self.spacing_widgets.items():
                self._spacing_data[key] = spin.value()
            self._data_manager.save_spacing(self._spacing_data)
        except Exception as e:
            errors.append(f"\u043E\u0442\u0441\u0442\u0443\u043F\u044B: {e}")

        try:
            ib_styles = {}
            single_styles = {}
            for row in range(self.para_table.rowCount()):
                key_item = self.para_table.item(row, 0)
                if not key_item or not key_item.text().strip():
                    continue
                key = key_item.text().strip()
                combo = self.para_table.cellWidget(row, 1)
                style_name = combo.currentText() if combo else ""
                tag_item = self.para_table.item(row, 2)
                tag = tag_item.text().strip() if tag_item else f":::{key}"
                if tag and not tag.startswith(":::"):
                    tag = ":::" + tag
                type_combo = self.para_table.cellWidget(row, 3)
                is_multi = type_combo and type_combo.currentIndex() == 0

                if is_multi:
                    ib_styles[key] = {
                        "style_name": style_name,
                        "multi_paragraph": True,
                        "opening_tag": tag,
                        "closing_tag": ":::"
                    }
                else:
                    single_styles[key] = {
                        "style_name": style_name,
                        "tag": tag
                    }

            out_data = {
                "infobox_styles": ib_styles,
                "inline_styles": {
                    "single_paragraph": single_styles
                }
            }
            self._data_manager.save_general_styles(out_data)
        except Exception as e:
            errors.append(f"\u0441\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432: {e}")

        if not silent:
            if errors:
                QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430", "\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C: " + "; ".join(errors))
            else:
                QMessageBox.information(self, "\u0423\u0441\u043F\u0435\u0445", "\u0421\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u044B")

    def _save_general_settings(self):
        self.save_settings(silent=False)

    def _add_para_style(self):
        row = self.para_table.rowCount()
        self.para_table.insertRow(row)
        self.para_table.setItem(row, 0, QTableWidgetItem(""))
        self.para_table.setCellWidget(row, 1, self._make_para_combo())
        self.para_table.setItem(row, 2, QTableWidgetItem(":::"))
        self.para_table.setCellWidget(row, 3, self._make_type_combo(True))

    def _remove_para_style(self):
        rows = set()
        for item in self.para_table.selectedItems():
            rows.add(item.row())
        for row in sorted(rows, reverse=True):
            self.para_table.removeRow(row)

    def _make_para_combo(self, value="") -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.installEventFilter(self)
        combo.setFocusPolicy(Qt.StrongFocus)
        for name in self._paragraph_styles:
            combo.addItem(name)
        if value:
            combo.setCurrentText(value)
        elif self._paragraph_styles:
            combo.setCurrentText(self._paragraph_styles[0])
        return combo

    def _make_type_combo(self, is_multi: bool = True) -> QComboBox:
        combo = QComboBox()
        combo.addItems(["\u041C\u043D\u043E\u0433\u043E\u0441\u0442\u0440\u043E\u0447\u043D\u044B\u0439", "\u041E\u0434\u043D\u043E\u0441\u0442\u0440\u043E\u0447\u043D\u044B\u0439"])
        combo.setCurrentIndex(0 if is_multi else 1)
        combo.installEventFilter(self)
        combo.setFocusPolicy(Qt.StrongFocus)
        return combo

    def _populate_para_table(self):
        self.para_table.setRowCount(0)
        try:
            gs_data = self._data_manager.load_general_styles()
        except Exception:
            return
        if not gs_data:
            return

        ib_styles = gs_data.get("infobox_styles", {})
        for key, style_def in ib_styles.items():
            row = self.para_table.rowCount()
            self.para_table.insertRow(row)
            self.para_table.setItem(row, 0, QTableWidgetItem(key))
            self.para_table.setCellWidget(row, 1, self._make_para_combo(style_def.get("style_name", "")))
            self.para_table.setItem(row, 2, QTableWidgetItem(style_def.get("opening_tag", f"::: {key}")))
            self.para_table.setCellWidget(row, 3, self._make_type_combo(True))

        single_config = gs_data.get("inline_styles", {}).get("single_paragraph", {})
        for key, style_def in single_config.items():
            row = self.para_table.rowCount()
            self.para_table.insertRow(row)
            self.para_table.setItem(row, 0, QTableWidgetItem(key))
            self.para_table.setCellWidget(row, 1, self._make_para_combo(style_def.get("style_name", "")))
            self.para_table.setItem(row, 2, QTableWidgetItem(style_def.get("tag", f"::: {key}")))
            self.para_table.setCellWidget(row, 3, self._make_type_combo(False))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if obj is self.para_table or obj is self.para_table.viewport() or obj is self.para_table.verticalScrollBar():
                return True
            for r in range(self.para_table.rowCount()):
                for c in range(self.para_table.columnCount()):
                    w = self.para_table.cellWidget(r, c)
                    if w is obj:
                        return True
        return super().eventFilter(obj, event)
