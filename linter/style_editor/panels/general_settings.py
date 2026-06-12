from __future__ import annotations

import json
from typing import Dict, Any, Optional, List
import copy

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QPushButton, QListWidget,
    QListWidgetItem, QGroupBox, QLineEdit, QComboBox,
    QSpinBox, QMessageBox, QAbstractItemView, QCheckBox, QInputDialog,
    QTabWidget, QFileDialog,
)
from PyQt5.QtCore import Qt

from ..style_data_manager import StyleDataManager
from ..widgets.json_preview import JsonPreviewWidget
from .color_tags import ColorTagsPanel


class GeneralSettingsWidget(QWidget):
    def __init__(self, data_manager: StyleDataManager,
                 paragraph_styles: Optional[List[str]] = None,
                 parent=None):
        super().__init__(parent)
        self._data_manager = data_manager
        self._paragraph_styles: List[str] = paragraph_styles or []
        self._para_styles_data: Dict[str, Dict[str, Any]] = {}
        self._line_styles_data: Dict[str, Dict[str, Any]] = {}
        self._spacing_data: Dict[str, Any] = {}
        self._para_updating = False
        self._para_renaming_old_name = ""
        self._selected_para_key: Optional[str] = None
        self._no_indent_keys: set = set()

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        left_group = QGroupBox("\u0421\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432")
        left_inner = QVBoxLayout(left_group)

        btn_layout = QHBoxLayout()
        self.para_add_btn = QPushButton("+ \u041D\u043E\u0432\u044B\u0439")
        self.para_add_btn.clicked.connect(self._on_para_style_add)
        btn_layout.addWidget(self.para_add_btn)
        self.para_dup_btn = QPushButton("\u2261 \u041A\u043E\u043F\u0438\u044F")
        self.para_dup_btn.clicked.connect(self._on_para_style_duplicate)
        btn_layout.addWidget(self.para_dup_btn)
        self.para_delete_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        self.para_delete_btn.clicked.connect(self._on_para_style_delete)
        btn_layout.addWidget(self.para_delete_btn)
        btn_layout.addStretch()
        left_inner.addLayout(btn_layout)

        self.para_style_list = QListWidget()
        self.para_style_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.para_style_list.currentRowChanged.connect(self._on_para_style_selected)
        self.para_style_list.itemDoubleClicked.connect(self._on_para_item_double_clicked)
        self.para_style_list.itemChanged.connect(self._on_para_item_renamed)
        left_inner.addWidget(self.para_style_list)

        save_layout = QHBoxLayout()
        self.para_save_btn = QPushButton("[>] \u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C JSON")
        self.para_save_btn.clicked.connect(self._save_para_all)
        save_layout.addWidget(self.para_save_btn)
        left_inner.addLayout(save_layout)

        left_outer = QWidget()
        left_outer_layout = QVBoxLayout(left_outer)
        left_outer_layout.addWidget(left_group)
        left_outer.setMaximumWidth(250)
        layout.addWidget(left_outer)

        self.general_tabs = QTabWidget()

        para_tab = QWidget()
        self._setup_para_properties_tab(para_tab)
        self.general_tabs.addTab(para_tab, "\u0410\u0411\u0417\u0410\u0426")

        spacing_tab = QWidget()
        self._setup_spacing_tab(spacing_tab)
        self.general_tabs.addTab(spacing_tab, "\u041E\u0411\u0429\u0415\u0415")

        line_tab = QWidget()
        self._setup_line_styles_tab(line_tab)
        self.general_tabs.addTab(line_tab, "\u041B\u0418\u041D\u0418\u0418")

        color_tab = QWidget()
        self._setup_color_tags_tab(color_tab)
        self.general_tabs.addTab(color_tab, "\u0426\u0412\u0415\u0422\u0410")

        self.general_json_preview = JsonPreviewWidget()
        self.general_tabs.addTab(self.general_json_preview, "JSON")

        layout.addWidget(self.general_tabs, stretch=2)

    def _setup_para_properties_tab(self, container):
        layout = QVBoxLayout(container)

        self.para_props_label = QLabel("\u0421\u0432\u043E\u0439\u0441\u0442\u0432\u0430 \u0441\u0442\u0438\u043B\u044F:")
        self.para_props_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px;")
        layout.addWidget(self.para_props_label)

        form_group = QGroupBox()
        form_layout = QVBoxLayout(form_group)

        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("\u0422\u0435\u0433 \u0432 MD:"))
        self.para_tag_edit = QLineEdit()
        self.para_tag_edit.setPlaceholderText(":::style_name")
        self.para_tag_edit.editingFinished.connect(self._on_para_tag_changed)
        tag_row.addWidget(self.para_tag_edit)
        form_layout.addLayout(tag_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("\u0422\u0438\u043F:"))
        self.para_type_combo = QComboBox()
        self.para_type_combo.addItems(["\u041C\u043D\u043E\u0433\u043E\u0441\u0442\u0440\u043E\u0447\u043D\u044B\u0439", "\u041E\u0434\u043D\u043E\u0441\u0442\u0440\u043E\u0447\u043D\u044B\u0439"])
        self.para_type_combo.currentIndexChanged.connect(self._on_para_type_changed)
        type_row.addWidget(self.para_type_combo)
        type_row.addStretch()
        form_layout.addLayout(type_row)

        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("\u0421\u0442\u0438\u043B\u044C Word:"))
        self.para_word_style_combo = QComboBox()
        self.para_word_style_combo.setEditable(True)
        self.para_word_style_combo.setInsertPolicy(QComboBox.NoInsert)
        self.para_word_style_combo.currentTextChanged.connect(self._on_para_word_style_changed)
        style_row.addWidget(self.para_word_style_combo)
        form_layout.addLayout(style_row)

        bullet_row = QHBoxLayout()
        bullet_row.addWidget(QLabel("Стиль Bullet-списка:"))
        self.para_list_bullet_combo = QComboBox()
        self.para_list_bullet_combo.setEditable(True)
        self.para_list_bullet_combo.setInsertPolicy(QComboBox.NoInsert)
        self.para_list_bullet_combo.currentTextChanged.connect(self._on_para_list_style_changed)
        bullet_row.addWidget(self.para_list_bullet_combo)
        form_layout.addLayout(bullet_row)

        number_row = QHBoxLayout()
        number_row.addWidget(QLabel("Стиль Number-списка:"))
        self.para_list_number_combo = QComboBox()
        self.para_list_number_combo.setEditable(True)
        self.para_list_number_combo.setInsertPolicy(QComboBox.NoInsert)
        self.para_list_number_combo.currentTextChanged.connect(self._on_para_list_style_changed)
        number_row.addWidget(self.para_list_number_combo)
        form_layout.addLayout(number_row)

        self.para_no_indent_cb = QCheckBox(
            "\u0443\u0431\u0440\u0430\u0442\u044C \u0430\u0431\u0437\u0430\u0446\u043D\u044B\u0439 \u043E\u0442\u0441\u0442\u0443\u043F \u043F\u043E\u0441\u043B\u0435 \u044D\u0442\u043E\u0433\u043E \u0441\u0442\u0438\u043B\u044F"
        )
        self.para_no_indent_cb.stateChanged.connect(self._on_para_no_indent_changed)
        form_layout.addWidget(self.para_no_indent_cb)

        layout.addWidget(form_group)
        layout.addStretch()

    def _setup_spacing_tab(self, container):
        layout = QVBoxLayout(container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("\u0420\u0435\u0436\u0438\u043C:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["\u041E\u0434\u0438\u043D\u043E\u0447\u043D\u044B\u0439 \u0444\u0430\u0439\u043B", "\u041F\u0430\u043A\u0435\u0442\u043D\u0430\u044F \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430"])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()
        scroll_layout.addLayout(mode_row)

        paths_group = QGroupBox("\u041F\u0443\u0442\u0438 \u043A \u0444\u0430\u0439\u043B\u0430\u043C")
        paths_form = QVBoxLayout(paths_group)

        def make_path_row(label_text, browse_callback):
            row = QHBoxLayout()
            label = QLabel(label_text)
            row.addWidget(label)
            edit = QLineEdit()
            edit.textChanged.connect(self._on_path_changed)
            row.addWidget(edit)
            btn = QPushButton("\u041E\u0431\u0437\u043E\u0440...")
            btn.clicked.connect(browse_callback)
            row.addWidget(btn)
            paths_form.addLayout(row)
            return edit, label, btn

        self.template_path_edit, _, _ = make_path_row(
            "\u0428\u0430\u0431\u043B\u043E\u043D DOCX:",
            self._browse_template
        )
        self.input_md_path_edit, self._input_label, _ = make_path_row(
            "MD \u043D\u0430 \u0432\u0445\u043E\u0434:",
            self._browse_input_md
        )
        self.output_docx_path_edit, self._output_label, _ = make_path_row(
            "DOCX \u043D\u0430 \u0432\u044B\u0445\u043E\u0434:",
            self._browse_output_docx
        )
        scroll_layout.addWidget(paths_group)

        spacing_group = QGroupBox("\u041E\u0442\u0441\u0442\u0443\u043F\u044B (\u0432 \u043F\u0442)")
        spacing_form = QVBoxLayout(spacing_group)

        self.spacing_widgets = {}
        spacing_fields = [
            ("before_heading", "\u041F\u0435\u0440\u0435\u0434 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u043E\u043C:"),
            ("after_heading", "\u041F\u043E\u0441\u043B\u0435 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u0430:"),
            ("after_list", "\u041F\u043E\u0441\u043B\u0435 \u0441\u043F\u0438\u0441\u043A\u0430:"),
            ("after_table", "\u041F\u043E\u0441\u043B\u0435 \u0442\u0430\u0431\u043B\u0438\u0446\u044B:"),
            ("table_before_heading", "\u041F\u0435\u0440\u0435\u0434 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043A\u043E\u043C \u043F\u043E\u0441\u043B\u0435 \u0442\u0430\u0431\u043B\u0438\u0446\u044B:"),
            ("before_table", "\u041F\u0435\u0440\u0435\u0434 \u0442\u0430\u0431\u043B\u0438\u0446\u0435\u0439 (\u043D\u0435 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043E\u043A):"),
        ]
        for key, label in spacing_fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            spin = QSpinBox()
            spin.setRange(0, 200)
            spin.setValue(0)
            spin.setSuffix(" \u043F\u0442")
            spin.valueChanged.connect(self._on_spacing_changed)
            row.addWidget(spin)
            row.addStretch()
            spacing_form.addLayout(row)
            self.spacing_widgets[key] = spin

        scroll_layout.addWidget(spacing_group)

        indent_group = QGroupBox("\u0423\u0431\u0440\u0430\u0442\u044C \u043A\u0440\u0430\u0441\u043D\u0443\u044E \u0441\u0442\u0440\u043E\u043A\u0443 \u043F\u043E\u0441\u043B\u0435 \u0442\u0438\u043F\u043E\u0432 \u0431\u043B\u043E\u043A\u043E\u0432:")
        indent_layout = QVBoxLayout(indent_group)
        self.block_type_list = QListWidget()
        indent_layout.addWidget(self.block_type_list)
        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ \u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C")
        add_btn.clicked.connect(self._on_block_type_add)
        btn_row.addWidget(add_btn)
        rm_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        rm_btn.clicked.connect(self._on_block_type_remove)
        btn_row.addWidget(rm_btn)
        indent_layout.addLayout(btn_row)
        self.bold_indent_cb = QCheckBox("\u0435\u0441\u043B\u0438 \u043F\u0435\u0440\u0432\u043E\u0435 \u0441\u043B\u043E\u0432\u043E \u0436\u0438\u0440\u043D\u043E\u0435")
        self.bold_indent_cb.stateChanged.connect(self._on_spacing_changed)
        indent_layout.addWidget(self.bold_indent_cb)
        scroll_layout.addWidget(indent_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _setup_line_styles_tab(self, container):
        layout = QHBoxLayout(container)

        left_group = QGroupBox("\u0421\u0442\u0438\u043B\u0438 \u043B\u0438\u043D\u0438\u0439")
        left_inner = QVBoxLayout(left_group)

        btn_layout = QHBoxLayout()
        self.line_add_btn = QPushButton("+ \u041D\u043E\u0432\u0430\u044F")
        self.line_add_btn.clicked.connect(self._on_line_style_add)
        btn_layout.addWidget(self.line_add_btn)
        self.line_dup_btn = QPushButton("\u2261 \u041A\u043E\u043F\u0438\u044F")
        self.line_dup_btn.clicked.connect(self._on_line_style_duplicate)
        btn_layout.addWidget(self.line_dup_btn)
        self.line_delete_btn = QPushButton("- \u0423\u0434\u0430\u043B\u0438\u0442\u044C")
        self.line_delete_btn.clicked.connect(self._on_line_style_delete)
        btn_layout.addWidget(self.line_delete_btn)
        btn_layout.addStretch()
        left_inner.addLayout(btn_layout)

        self.line_style_list = QListWidget()
        self.line_style_list.currentRowChanged.connect(self._on_line_style_selected)
        left_inner.addWidget(self.line_style_list)

        left_outer = QWidget()
        left_outer_layout = QVBoxLayout(left_outer)
        left_outer_layout.addWidget(left_group)
        left_outer.setMaximumWidth(250)
        layout.addWidget(left_outer)

        props_group = QGroupBox("\u0421\u0432\u043E\u0439\u0441\u0442\u0432\u0430 \u043B\u0438\u043D\u0438\u0438")
        props_layout = QVBoxLayout(props_group)

        tag_info = QLabel("\u0422\u0435\u0433 \u0432 MD: #st/\u0438\u043C\u044F_\u0442\u0435\u0433\u0430")
        tag_info.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px;")
        props_layout.addWidget(tag_info)

        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("\u0418\u043C\u044F \u0442\u0435\u0433\u0430:"))
        self.line_tag_edit = QLineEdit()
        self.line_tag_edit.setPlaceholderText("purple-line")
        self.line_tag_edit.editingFinished.connect(self._on_line_style_prop_changed)
        tag_row.addWidget(self.line_tag_edit)
        props_layout.addLayout(tag_row)

        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("\u0421\u0442\u0438\u043B\u044C Word:"))
        self.line_word_style_combo = QComboBox()
        self.line_word_style_combo.setEditable(True)
        self.line_word_style_combo.setInsertPolicy(QComboBox.NoInsert)
        self.line_word_style_combo.currentTextChanged.connect(self._on_line_style_prop_changed)
        style_row.addWidget(self.line_word_style_combo)
        props_layout.addLayout(style_row)

        props_layout.addStretch()
        layout.addWidget(props_group, stretch=2)

    def _setup_color_tags_tab(self, container):
        layout = QVBoxLayout(container)
        self.color_tags_panel = ColorTagsPanel()
        self.color_tags_panel.data_changed.connect(self._on_color_tags_changed)
        layout.addWidget(self.color_tags_panel)

    def _on_color_tags_changed(self):
        self._update_general_json_preview()
        self._save_general_styles_to_disk()

    def _on_line_style_add(self):
        base = "new_line"
        name = base
        idx = 1
        while name in self._line_styles_data:
            idx += 1
            name = f"{base}_{idx}"
        self._line_styles_data[name] = {
            "style_name": "",
        }
        item = QListWidgetItem(name)
        self.line_style_list.addItem(item)
        self.line_style_list.setCurrentRow(self.line_style_list.count() - 1)
        self._save_general_styles_to_disk()

    def _on_line_style_duplicate(self):
        item = self.line_style_list.currentItem()
        if not item:
            return
        old_name = item.text()
        base = old_name + "_copy"
        new_name = base
        idx = 1
        while new_name in self._line_styles_data:
            idx += 1
            new_name = f"{base}_{idx}"

        self._line_styles_data[new_name] = copy.deepcopy(self._line_styles_data[old_name])

        list_item = QListWidgetItem(new_name)
        self.line_style_list.addItem(list_item)
        self.line_style_list.setCurrentRow(self.line_style_list.count() - 1)
        self._save_general_styles_to_disk()

    def _on_line_style_delete(self):
        item = self.line_style_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(
            self, "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435",
            f"\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u044C \u043B\u0438\u043D\u0438\u0438 '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if name in self._line_styles_data:
            del self._line_styles_data[name]
        row = self.line_style_list.row(item)
        self.line_style_list.takeItem(row)
        self._save_general_styles_to_disk()
        if self.line_style_list.count() > 0:
            self.line_style_list.setCurrentRow(0)

    def _on_line_style_selected(self, row: int):
        if row < 0 or row >= self.line_style_list.count():
            return
        name = self.line_style_list.item(row).text()
        data = self._line_styles_data.get(name, {})
        self._line_updating = True
        self.line_tag_edit.setText(name)
        self.line_word_style_combo.setCurrentText(data.get("style_name", ""))
        self._line_updating = False

    def _on_line_style_prop_changed(self):
        if getattr(self, '_line_updating', False):
            return
        item = self.line_style_list.currentItem()
        if not item:
            return
        old_name = item.text()
        new_name = self.line_tag_edit.text().strip()
        if not new_name:
            return

        data = self._line_styles_data.pop(old_name, {})
        data["style_name"] = self.line_word_style_combo.currentText().strip()
        self._line_styles_data[new_name] = data

        self.line_style_list.blockSignals(True)
        item.setText(new_name)
        self.line_style_list.blockSignals(False)
        self._save_general_styles_to_disk()

    def _fill_line_word_style_combo(self):
        self.line_word_style_combo.clear()
        for name in self._paragraph_styles:
            self.line_word_style_combo.addItem(name)

    def _on_mode_changed(self, index):
        is_batch = index == 1
        if is_batch:
            self._input_label.setText("\u041F\u0430\u043F\u043A\u0430 \u0441 MD \u0444\u0430\u0439\u043B\u0430\u043C\u0438:")
            self._output_label.setText("\u041F\u0430\u043F\u043A\u0430 \u0434\u043B\u044F DOCX:")
        else:
            self._input_label.setText("MD \u043D\u0430 \u0432\u0445\u043E\u0434:")
            self._output_label.setText("DOCX \u043D\u0430 \u0432\u044B\u0445\u043E\u0434:")
        try:
            cfg = self._data_manager.load_app_config()
            cfg["batch_mode"] = is_batch
            self._data_manager.save_app_config(cfg)
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0440\u0435\u0436\u0438\u043C: {e}")

    def _browse_template(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0448\u0430\u0431\u043B\u043E\u043D DOCX",
            "", "DOCX \u0444\u0430\u0439\u043B\u044B (*.docx)"
        )
        if path:
            self.template_path_edit.setText(path)

    def _browse_input_md(self):
        if self._mode_combo.currentIndex() == 1:
            path = QFileDialog.getExistingDirectory(
                self, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u043F\u0430\u043F\u043A\u0443 \u0441 MD \u0444\u0430\u0439\u043B\u0430\u043C\u0438"
            )
            if path:
                self.input_md_path_edit.setText(path)
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 MD \u0444\u0430\u0439\u043B",
                "", "Markdown \u0444\u0430\u0439\u043B\u044B (*.md)"
            )
            if path:
                self.input_md_path_edit.setText(path)

    def _browse_output_docx(self):
        if self._mode_combo.currentIndex() == 1:
            path = QFileDialog.getExistingDirectory(
                self, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u043F\u0430\u043F\u043A\u0443 \u0434\u043B\u044F DOCX"
            )
            if path:
                self.output_docx_path_edit.setText(path)
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C DOCX \u043A\u0430\u043A",
                "", "DOCX \u0444\u0430\u0439\u043B\u044B (*.docx)"
            )
            if path:
                self.output_docx_path_edit.setText(path)

    def _on_path_changed(self):
        try:
            cfg = self._data_manager.load_app_config()
            cfg.setdefault("paths", {})
            cfg["paths"]["template"] = self.template_path_edit.text().strip()
            cfg["paths"]["input_md"] = self.input_md_path_edit.text().strip()
            cfg["paths"]["output_docx"] = self.output_docx_path_edit.text().strip()
            cfg["batch_mode"] = self._mode_combo.currentIndex() == 1
            self._data_manager.save_app_config(cfg)
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043F\u0443\u0442\u0438: {e}")

    def _load_data(self):
        try:
            raw = self._data_manager.load_general_styles()
        except Exception:
            raw = {}
        try:
            self._spacing_data = self._data_manager.load_spacing()
        except Exception:
            self._spacing_data = {}

        self._para_styles_data = {}
        ib = raw.get("infobox_styles", {})
        if isinstance(ib, dict):
            for key, sdef in ib.items():
                self._para_styles_data[key] = {
                    "style_name": sdef.get("style_name", ""),
                    "tag": sdef.get("opening_tag", f":::{key}"),
                    "type": "multi",
                    "list_bullet_style": sdef.get("list_bullet_style", ""),
                    "list_number_style": sdef.get("list_number_style", ""),
                }

        inline = raw.get("inline_styles", {}).get("single_paragraph", {})
        if isinstance(inline, dict):
            for key, sdef in inline.items():
                self._para_styles_data[key] = {
                    "style_name": sdef.get("style_name", ""),
                    "tag": sdef.get("tag", f":::{key}"),
                    "type": "single",
                    "list_bullet_style": "",
                    "list_number_style": "",
                }

        self._line_styles_data = {}
        line_styles_raw = raw.get("line_styles", {})
        if isinstance(line_styles_raw, dict):
            for key, sdef in line_styles_raw.items():
                self._line_styles_data[key] = {
                    "style_name": sdef.get("style_name", ""),
                }

        custom_colors = raw.get("custom_colors", {})
        self.color_tags_panel.load_data(custom_colors if isinstance(custom_colors, dict) else {})

        self._populate_para_style_list()
        self._fill_para_word_style_combo()
        self._populate_line_style_list()
        self._fill_line_word_style_combo()

        loaded = set(self._spacing_data.get("no_indent_after_block_types", []))
        self._no_indent_keys = {
            self._get_style_match_key(k)
            for k in self._para_styles_data
            if self._get_style_match_key(k) in loaded
        }

        if self.para_style_list.count() > 0:
            self._on_para_style_selected(0)
        self._update_general_json_preview()

        for spin in self.spacing_widgets.values():
            spin.blockSignals(True)
        for key, spin in self.spacing_widgets.items():
            val = self._spacing_data.get(key, 0)
            spin.setValue(val)
        for spin in self.spacing_widgets.values():
            spin.blockSignals(False)

        self._load_block_type_list()
        self.bold_indent_cb.setChecked(self._spacing_data.get("no_indent_if_first_bold", True))

        try:
            ac = self._data_manager.load_app_config()
            p = ac.get("paths", {})
            self._mode_combo.blockSignals(True)
            self._mode_combo.setCurrentIndex(1 if ac.get("batch_mode", False) else 0)
            self._mode_combo.blockSignals(False)
            self._on_mode_changed(self._mode_combo.currentIndex())
            self.template_path_edit.blockSignals(True)
            self.input_md_path_edit.blockSignals(True)
            self.output_docx_path_edit.blockSignals(True)
            self.template_path_edit.setText(p.get("template", ""))
            self.input_md_path_edit.setText(p.get("input_md", ""))
            self.output_docx_path_edit.setText(p.get("output_docx", ""))
            self.template_path_edit.blockSignals(False)
            self.input_md_path_edit.blockSignals(False)
            self.output_docx_path_edit.blockSignals(False)
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043F\u0443\u0442\u0438: {e}")

    def _fill_para_word_style_combo(self):
        self._para_updating = True
        self.para_word_style_combo.clear()
        self.para_list_bullet_combo.clear()
        self.para_list_number_combo.clear()
        for name in self._paragraph_styles:
            self.para_word_style_combo.addItem(name)
            self.para_list_bullet_combo.addItem(name)
            self.para_list_number_combo.addItem(name)
        self._para_updating = False

    def _fill_line_word_style_combo(self):
        self.line_word_style_combo.clear()
        for name in self._paragraph_styles:
            self.line_word_style_combo.addItem(name)

    def set_paragraph_styles(self, styles: List[str]):
        self._paragraph_styles = styles
        self._fill_para_word_style_combo()
        self._fill_line_word_style_combo()

    def _populate_line_style_list(self):
        self.line_style_list.blockSignals(True)
        self.line_style_list.clear()
        for key in sorted(self._line_styles_data.keys()):
            item = QListWidgetItem(key)
            self.line_style_list.addItem(item)
        self.line_style_list.blockSignals(False)
        if self.line_style_list.count() > 0:
            self.line_style_list.setCurrentRow(0)

    def _populate_para_style_list(self):
        self.para_style_list.blockSignals(True)
        self.para_style_list.clear()
        for key in sorted(self._para_styles_data.keys()):
            item = QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.para_style_list.addItem(item)
        self.para_style_list.blockSignals(False)
        if self.para_style_list.count() > 0:
            self.para_style_list.setCurrentRow(0)

    def _update_general_json_preview(self):
        rebuilt = self._build_general_styles_dict()
        self.general_json_preview.set_data(rebuilt)

    def _build_general_styles_dict(self) -> dict:
        ib_styles = {}
        single_styles = {}
        for key, data in self._para_styles_data.items():
            if data["type"] == "multi":
                ib_styles[key] = {
                    "style_name": data["style_name"],
                    "multi_paragraph": True,
                    "opening_tag": data["tag"],
                    "closing_tag": ":::",
                    "list_bullet_style": data.get("list_bullet_style", ""),
                    "list_number_style": data.get("list_number_style", ""),
                }
            else:
                single_styles[key] = {
                    "style_name": data["style_name"],
                    "tag": data["tag"],
                }
        line_styles = {}
        for key, data in self._line_styles_data.items():
            line_styles[key] = {
                "style_name": data.get("style_name", ""),
                "tag": f"#st/{key}",
            }
        return {
            "infobox_styles": ib_styles,
            "inline_styles": {
                "single_paragraph": single_styles,
            },
            "line_styles": line_styles,
            "custom_colors": self.color_tags_panel.get_data(),
        }

    def _on_para_style_selected(self, row: int):
        if row < 0 or row >= self.para_style_list.count():
            return
        key = self.para_style_list.item(row).text()
        self._selected_para_key = key
        data = self._para_styles_data.get(key, {})
        self._para_updating = True
        self.para_props_label.setText(f'\u0421\u0432\u043E\u0439\u0441\u0442\u0432\u0430 \u0441\u0442\u0438\u043B\u044F "{key}":')
        self.para_tag_edit.setText(data.get("tag", ""))
        is_multi = data.get("type", "multi") == "multi"
        self.para_type_combo.setCurrentIndex(0 if is_multi else 1)
        self.para_word_style_combo.setCurrentText(data.get("style_name", ""))
        self.para_list_bullet_combo.setCurrentText(data.get("list_bullet_style", ""))
        self.para_list_number_combo.setCurrentText(data.get("list_number_style", ""))
        self.para_list_bullet_combo.setEnabled(is_multi)
        self.para_list_number_combo.setEnabled(is_multi)
        self.para_no_indent_cb.setChecked(self._get_style_match_key(key) in self._no_indent_keys)
        self._para_updating = False

    def _on_para_style_add(self):
        base = "new_style"
        name = base
        idx = 1
        while name in self._para_styles_data:
            idx += 1
            name = f"{base}_{idx}"
        self._para_styles_data[name] = {
            "style_name": "",
            "tag": f":::{name}",
            "type": "multi",
            "list_bullet_style": "",
            "list_number_style": "",
        }
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.para_style_list.addItem(item)
        self.para_style_list.setCurrentRow(self.para_style_list.count() - 1)
        self._save_general_styles_to_disk()

    def _on_para_style_duplicate(self):
        if not self._selected_para_key:
            return
        old_name = self._selected_para_key
        base = old_name + "_copy"
        new_name = base
        idx = 1
        while new_name in self._para_styles_data:
            idx += 1
            new_name = f"{base}_{idx}"

        self._para_styles_data[new_name] = copy.deepcopy(self._para_styles_data[old_name])
        self._para_styles_data[new_name]["tag"] = f":::{new_name}"

        item = QListWidgetItem(new_name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.para_style_list.addItem(item)
        self.para_style_list.setCurrentRow(self.para_style_list.count() - 1)
        self._save_general_styles_to_disk()

    def _on_para_style_delete(self):
        item = self.para_style_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(
            self, "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435",
            f"\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u044C '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if name in self._para_styles_data:
            del self._para_styles_data[name]
        row = self.para_style_list.row(item)
        self.para_style_list.takeItem(row)
        self._save_general_styles_to_disk()
        if self.para_style_list.count() > 0:
            self.para_style_list.setCurrentRow(0)
        else:
            self._selected_para_key = None
            self.para_props_label.setText("\u0421\u0432\u043E\u0439\u0441\u0442\u0432\u0430 \u0441\u0442\u0438\u043B\u044F:")
            self.para_tag_edit.clear()
            self.para_word_style_combo.setCurrentText("")

    def _on_para_item_double_clicked(self, item: QListWidgetItem):
        self._para_renaming_old_name = item.text()

    def _on_para_item_renamed(self, item: QListWidgetItem):
        new_name = item.text().strip()
        old = self._para_renaming_old_name
        if not new_name or new_name == old:
            self.para_style_list.blockSignals(True)
            item.setText(old)
            self.para_style_list.blockSignals(False)
            self._para_renaming_old_name = ""
            return

        if new_name in self._para_styles_data and new_name != old:
            QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430",
                               f"\u0421\u0442\u0438\u043B\u044C '{new_name}' \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442")
            self.para_style_list.blockSignals(True)
            item.setText(old)
            self.para_style_list.blockSignals(False)
            self._para_renaming_old_name = ""
            return

        self._para_styles_data[new_name] = self._para_styles_data.pop(old)
        self._para_renaming_old_name = ""
        if self._selected_para_key == old:
            self._selected_para_key = new_name
            self.para_props_label.setText(f'\u0421\u0432\u043E\u0439\u0441\u0442\u0432\u0430 \u0441\u0442\u0438\u043B\u044F "{new_name}":')
        self._save_general_styles_to_disk()
        self._update_general_json_preview()

    def _on_para_tag_changed(self):
        if self._para_updating or not self._selected_para_key:
            return
        tag = self.para_tag_edit.text().strip()
        if tag and not tag.startswith(":::"):
            tag = ":::" + tag
        self._para_styles_data[self._selected_para_key]["tag"] = tag
        self._update_general_json_preview()
        self._save_general_styles_to_disk()

    def _on_para_type_changed(self, index: int):
        if self._para_updating or not self._selected_para_key:
            return
        self._para_styles_data[self._selected_para_key]["type"] = "multi" if index == 0 else "single"
        is_multi = index == 0
        self.para_list_bullet_combo.setEnabled(is_multi)
        self.para_list_number_combo.setEnabled(is_multi)
        self._update_general_json_preview()
        self._save_general_styles_to_disk()

    def _on_para_word_style_changed(self, text: str):
        if self._para_updating or not self._selected_para_key:
            return
        self._para_styles_data[self._selected_para_key]["style_name"] = text
        self._update_general_json_preview()
        self._save_general_styles_to_disk()

    def _on_para_list_style_changed(self, _text: str):
        if self._para_updating or not self._selected_para_key:
            return
        data = self._para_styles_data[self._selected_para_key]
        data["list_bullet_style"] = self.para_list_bullet_combo.currentText().strip()
        data["list_number_style"] = self.para_list_number_combo.currentText().strip()
        self._update_general_json_preview()
        self._save_general_styles_to_disk()

    def _get_style_match_key(self, para_key: str) -> str:
        data = self._para_styles_data.get(para_key, {})
        return data.get("style_name", "").strip() or para_key

    def _on_para_no_indent_changed(self, state: int):
        if self._para_updating or not self._selected_para_key:
            return
        match_key = self._get_style_match_key(self._selected_para_key)
        if state == Qt.Checked:
            self._no_indent_keys.add(match_key)
        else:
            self._no_indent_keys.discard(match_key)
        self._merge_and_save_spacing()

    def _merge_and_save_spacing(self):
        merged = list(dict.fromkeys(self._get_block_types_from_list() + list(self._no_indent_keys)))
        self._spacing_data["no_indent_after_block_types"] = merged
        self._data_manager.save_spacing(self._spacing_data)

    def _on_spacing_changed(self):
        for key, spin in self.spacing_widgets.items():
            self._spacing_data[key] = spin.value()
        self._spacing_data["no_indent_if_first_bold"] = self.bold_indent_cb.isChecked()
        self._merge_and_save_spacing()

    def _get_block_types_from_list(self) -> list:
        return [self.block_type_list.item(i).text() for i in range(self.block_type_list.count())]

    def _load_block_type_list(self):
        self.block_type_list.blockSignals(True)
        self.block_type_list.clear()
        types = self._spacing_data.get("no_indent_after_block_types", [])
        if not types:
            old = self._spacing_data.get("no_indent_after_heading_list")
            types = ["heading", "list", "table", "thematic_break"] if (old is None or old) else []
        for t in types:
            self.block_type_list.addItem(t)
        self.block_type_list.blockSignals(False)

    def _on_block_type_add(self):
        items = ["heading", "list", "table", "thematic_break"]
        item, ok = QInputDialog.getItem(
            self,
            "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C",
            "\u0418\u043C\u044F \u0441\u0442\u0438\u043B\u044F \u0430\u0431\u0437\u0430\u0446\u0430 \u0438\u043B\u0438 \u0442\u0438\u043F \u0431\u043B\u043E\u043A\u0430:",
            items, editable=True
        )
        if ok and item:
            item = item.strip()
            if item:
                self.block_type_list.addItem(item)
                self._on_spacing_changed()

    def _on_block_type_remove(self):
        row = self.block_type_list.currentRow()
        if row >= 0:
            self.block_type_list.takeItem(row)
            self._on_spacing_changed()

    def _save_para_all(self):
        self._save_general_styles_to_disk()
        self._on_spacing_changed()
        path_str = str(self._data_manager.general_styles_path)
        QMessageBox.information(self, "\u0423\u0441\u043F\u0435\u0445",
            f"\u0421\u0442\u0438\u043B\u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u044B \u0432 {path_str}")

    def _save_general_styles_to_disk(self):
        try:
            out = self._build_general_styles_dict()
            self._data_manager.save_general_styles(out)
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C styles.json: {e}")
