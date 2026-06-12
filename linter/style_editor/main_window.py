from __future__ import annotations
#
# NOTE: This file is for window layout and signal wiring ONLY.
# Do NOT add new functionality here.
#   - Form panels  → panels/*.py
#   - Visual widgets → widgets/*.py
#   - Data/IO      → style_data_manager.py
#   - Utils        → style_utils.py / mapping_utils.py
# See AGENTS.md for details.
#

from typing import Dict, Any, Optional, List

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTabWidget, QPushButton, QStatusBar,
)
from PyQt5.QtCore import Qt

import copy as py_copy

from linter.converter.tables.advanced.models import (
    TableStyle, RowTypeStyle, CellOverride, BorderStyle
)
from linter.converter.docx_builder import DocxBuilder
from linter.converter.markdown_processor import preprocess_markdown
from linter.config import load_configuration
from linter.utils import ensure_output_dir

from .widgets.visual_grid import VisualGridWidget
from .widgets.style_list_panel import StyleListPanel
from .widgets.json_preview import JsonPreviewWidget
from .panels.properties import PropertiesPanel
from .panels.color_rules import ColorRulesWidget
from .panels.table_structure import TableStructurePanel
from .panels.general_settings import GeneralSettingsWidget
from .style_utils import (
    get_cell_shading, get_cell_bold, get_cell_italic, expand_border_side
)
from .mapping_utils import find_mapping_for_style
from .style_data_manager import StyleDataManager


class StyleEditorMainWindow(QMainWindow):
    def __init__(self, data_manager: StyleDataManager):
        super().__init__()
        self.data_manager = data_manager
        self._current_style: Optional[TableStyle] = None
        self._styles: Dict[str, Any] = {}
        self._mappings: Dict[str, Any] = {}

        self._setup_ui()
        self._load_styles()
        self._load_mappings()

    def _setup_ui(self):
        self.setWindowTitle("Table Style Editor - PyQt5")
        self.setMinimumSize(1400, 900)
        self.resize(1400, 910)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.main_global_tabs = QTabWidget()

        paragraph_styles = self._load_template_styles()
        self.general_settings_tab = GeneralSettingsWidget(
            self.data_manager, paragraph_styles
        )
        self.main_global_tabs.addTab(self.general_settings_tab, "\u041E\u0431\u0449\u0438\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438")

        table_tab = QWidget()
        self._setup_table_editor_tab(table_tab)
        self.main_global_tabs.addTab(table_tab, "\u0420\u0435\u0434\u0430\u043A\u0442\u043E\u0440 \u0442\u0430\u0431\u043B\u0438\u0446")

        if paragraph_styles:
            self.structure_panel.load_paragraph_styles(paragraph_styles)

        outer_layout.addWidget(self.main_global_tabs)

        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(6, 2, 6, 4)
        self.layout_btn = QPushButton("\u0412\u0451\u0440\u0441\u0442\u043A\u0430")
        self.layout_btn.setMinimumHeight(30)
        self.layout_btn.setStyleSheet(
            "QPushButton { background-color: #2d7d2d; color: white; font-weight: bold; "
            "border-radius: 4px; padding: 4px 16px; }"
            "QPushButton:hover { background-color: #3a9e3a; }"
        )
        self.layout_btn.clicked.connect(self._run_layout)
        bottom_bar.addWidget(self.layout_btn)
        bottom_bar.addStretch()
        outer_layout.addLayout(bottom_bar)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("\u0413\u043E\u0442\u043E\u0432")
        self.setStatusBar(self.status_bar)

    def _setup_table_editor_tab(self, container):
        layout = QHBoxLayout(container)

        self.style_list_panel = StyleListPanel()
        self.style_list_panel.style_selected.connect(self._on_style_selected)
        self.style_list_panel.style_created.connect(self._on_style_created)
        self.style_list_panel.style_deleted.connect(self._on_style_deleted)
        self.style_list_panel.save_requested.connect(self._save_styles)
        self.style_list_panel.style_renamed.connect(self._on_style_renamed)
        self.style_list_panel.duplicate_requested.connect(self._on_style_duplicated)
        self.style_list_panel.setMaximumWidth(250)
        layout.addWidget(self.style_list_panel)

        self.tabs = QTabWidget()

        self.grid_widget = VisualGridWidget()
        self.grid_widget.selection_changed.connect(self._on_grid_selection_changed)
        self.grid_widget.style_rename_requested.connect(self._on_visual_style_rename)
        self.tabs.addTab(self.grid_widget, "\u0412\u0438\u0437\u0443\u0430\u043B\u044C\u043D\u044B\u0439 \u0440\u0435\u0434\u0430\u043A\u0442\u043E\u0440")

        self.structure_panel = TableStructurePanel()
        self.structure_panel.tag_changed.connect(self._on_tag_changed)
        self.structure_panel.structure_changed.connect(self._on_structure_changed)
        self.tabs.addTab(self.structure_panel, "\u0421\u0442\u0440\u0443\u043A\u0442\u0443\u0440\u0430 \u0438 \u0441\u0432\u043E\u0439\u0441\u0442\u0432\u0430")

        self.color_rules_widget = ColorRulesWidget()
        self.color_rules_widget.rules_changed.connect(self._on_rules_changed)
        self.tabs.addTab(self.color_rules_widget, "\u0426\u0432\u0435\u0442\u043E\u0432\u044B\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u0430")

        self.json_preview = JsonPreviewWidget()
        self.tabs.addTab(self.json_preview, "JSON \u043F\u0440\u0435\u0434\u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440")

        layout.addWidget(self.tabs, stretch=2)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.properties_panel = PropertiesPanel()
        self.properties_panel.property_changed.connect(self._on_property_changed)
        self.properties_panel.apply_border_clicked.connect(self._on_apply_border)
        self.properties_panel.clear_borders_clicked.connect(self._on_clear_borders)
        self.properties_panel.target_combo.currentIndexChanged.connect(self._on_editor_target_changed)
        right_layout.addWidget(self.properties_panel)

        right_panel.setMaximumWidth(380)
        layout.addWidget(right_panel)

    def _load_styles(self):
        try:
            self._styles = self.data_manager.load_table_styles()
            self.style_list_panel.set_style_names(list(self._styles.keys()))
        except Exception as e:
            QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430", f"\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u0438: {e}")

    def _load_mappings(self):
        try:
            self._mappings = self.data_manager.load_mappings()
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u043C\u0430\u043F\u043F\u0438\u043D\u0433\u0438: {e}")

    def _load_template_styles(self) -> List[str]:
        try:
            return self.data_manager.load_template_styles()
        except Exception as e:
            print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 \u0441\u0442\u0438\u043B\u0435\u0439 \u0448\u0430\u0431\u043B\u043E\u043D\u0430: {e}")
            return []

    def _save_mappings(self):
        try:
            self.data_manager.save_mappings(self._mappings)
        except Exception as e:
            print(f"[-] \u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043C\u0430\u043F\u043F\u0438\u043D\u0433\u0438: {e}")

    def _save_styles(self):
        try:
            self._update_current_style_in_dict()
            self.structure_panel.tag_edit.editingFinished.emit()
            self._save_mappings()

            self.data_manager.save_table_styles(self._styles)

            path_str = str(self.data_manager.styles_path)
            QMessageBox.information(self, "\u0423\u0441\u043F\u0435\u0445",
                f"\u0421\u0442\u0438\u043B\u0438 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u044B \u0432 {path_str}")
        except Exception as e:
            QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430", f"\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0441\u0442\u0438\u043B\u0438: {e}")

    def _on_style_created(self, name: str):
        self._styles[name] = {
            "renderer": "advanced",
            "layout": "auto",
            "cell_margins": {"top": 90, "start": 110, "bottom": 90, "end": 110},
            "default_borders": {},
            "default_shading": None,
            "empty_row_top": False,
            "empty_row_bottom": False,
            "empty_row_height": 200,
            "fit_to_page": True,
            "table_width": None,
            "column_widths": None,
            "row_heights": None,
            "row_types": {},
            "cell_overrides": {},
            "color_rules": []
        }

        self._mappings["‹!" + name + "›"] = {
            "table": "\u041F\u0440\u043E\u0441\u0442\u0430\u044F \u0442\u0430\u0431\u043B\u0438\u0446\u0430 1",
            "header": self.structure_panel.get_header_style() or "Table Header 1",
            "text": self.structure_panel.get_text_style() or "Table Text 1",
            "preset": name
        }

    def _on_style_duplicated(self, old_name: str, new_name: str):
        if old_name in self._styles:
            self._styles[new_name] = py_copy.deepcopy(self._styles[old_name])

        old_tag, old_mapping = find_mapping_for_style(self._mappings, old_name)
        if old_mapping:
            new_tag = "‹!" + new_name + "›"
            new_mapping = dict(old_mapping)
            new_mapping["preset"] = new_name
            self._mappings[new_tag] = new_mapping

    def _on_style_deleted(self, name: str):
        if name in self._styles:
            del self._styles[name]
        tag_to_delete, _ = find_mapping_for_style(self._mappings, name)
        if tag_to_delete:
            del self._mappings[tag_to_delete]

    def _on_style_selected(self, name: str):
        style_data = self._styles.get(name, {})

        if style_data.get('renderer') in ('advanced', 'zebra') or 'layout' in style_data:
            self._current_style = TableStyle.from_dict(style_data, name)
        else:
            converted = StyleDataManager.convert_flat_to_advanced(style_data)
            self._current_style = TableStyle.from_dict(converted, name)

        self.grid_widget.clear_selection()
        self.grid_widget.update_visuals(self._current_style)
        self.grid_widget.set_style_name(name)
        self._update_json_preview()
        self.color_rules_widget.set_rules(self._current_style.color_rules)
        self._load_panel_from_target(self.properties_panel.get_target())

        tag, found_mapping = find_mapping_for_style(self._mappings, name)
        self.structure_panel.set_tag(tag)

        mapping_header = found_mapping.get("header", "Table Header 1") if found_mapping else "Table Header 1"
        mapping_text = found_mapping.get("text", "Table Text 1") if found_mapping else "Table Text 1"
        self.structure_panel.set_header_style(mapping_header, block_signals=True)
        self.structure_panel.set_text_style(mapping_text, block_signals=True)

        self.structure_panel.set_column_widths(self._current_style.column_widths)
        self.structure_panel.set_row_heights(self._current_style.row_heights)
        self.structure_panel.set_empty_row_top(self._current_style.empty_row_top, block_signals=True)
        self.structure_panel.set_empty_row_bottom(self._current_style.empty_row_bottom, block_signals=True)
        self.structure_panel.set_empty_row_height(self._current_style.empty_row_height, block_signals=True)
        self.structure_panel.set_fit_to_page(self._current_style.fit_to_page, block_signals=True)
        self.structure_panel.set_table_width(self._current_style.table_width)
        self.structure_panel.set_text_wrap(self._current_style.text_wrap, block_signals=True)
        self.structure_panel.set_left_from_text(self._current_style.left_from_text, block_signals=True)
        self.structure_panel.set_right_from_text(self._current_style.right_from_text, block_signals=True)

    def _on_style_renamed(self, old_name: str, new_name: str):
        self._styles[new_name] = self._styles.pop(old_name)
        if self._current_style and self._current_style.name == old_name:
            self._current_style.name = new_name

        for mapping in self._mappings.values():
            if mapping.get("preset") == old_name:
                mapping["preset"] = new_name
                break

    def _on_visual_style_rename(self, old_name: str, new_name: str):
        success = self.style_list_panel.rename_style(old_name, new_name)
        if not success:
            self.grid_widget.set_style_name(old_name)

    def _on_grid_selection_changed(self):
        if not self.grid_widget.selected_cells or not self._current_style:
            return

        target = self.properties_panel.get_target()
        if target == "cell_override":
            self._load_panel_from_selected_cells()

    def _load_panel_from_selected_cells(self):
        selected = self.grid_widget.selected_cells
        if not selected:
            return
        first_cell = next(iter(selected))
        row, col = first_cell

        shading_values = set()
        bold_values = set()
        italic_values = set()
        font_color_values = set()

        for r, c in selected:
            c_ref = f"{chr(ord('A') + c)}{r + 1}"

            found = False
            for ovr in self._current_style.cell_overrides:
                if ovr.cell_ref == c_ref:
                    shading_values.add(ovr.shading)
                    bold_values.add(ovr.bold)
                    italic_values.add(ovr.italic)
                    font_color_values.add(ovr.font_color)
                    found = True
                    break

            if not found:
                def_shading = get_cell_shading(self._current_style, r, c, 6, 6)
                shading_values.add(def_shading)
                bold_values.add(None)
                italic_values.add(None)
                font_color_values.add(None)

        if len(shading_values) == 1:
            self.properties_panel.set_shading(next(iter(shading_values)))
        else:
            self.properties_panel.set_shading(None)

        if len(bold_values) == 1:
            self.properties_panel.set_bold(next(iter(bold_values)))
        else:
            self.properties_panel.set_bold(None)

        if len(italic_values) == 1:
            self.properties_panel.set_italic(next(iter(italic_values)))
        else:
            self.properties_panel.set_italic(None)

        if len(font_color_values) == 1:
            self.properties_panel.set_font_color(next(iter(font_color_values)))
        else:
            self.properties_panel.set_font_color(None)

    def _on_editor_target_changed(self, _index: int):
        if self._current_style is None:
            return
        target = self.properties_panel.get_target()
        self._load_panel_from_target(target)

    def _load_panel_from_target(self, target: str):
        if self._current_style is None:
            return

        if target == "table_defaults":
            self.properties_panel.set_shading(self._current_style.default_shading)
            self.properties_panel.set_bold(None)
            self.properties_panel.set_italic(None)
            self.properties_panel.set_font_color(None)
        elif target in ["header", "odd", "even", "last_row", "first_column", "last_column"]:
            rt = self._current_style.row_types.get(target)
            if rt:
                self.properties_panel.set_bold(rt.bold)
                self.properties_panel.set_italic(rt.italic)
                self.properties_panel.set_shading(rt.shading if rt.shading else None)
                self.properties_panel.set_font_color(rt.font_color if rt.font_color else None)
            else:
                self.properties_panel.set_bold(None)
                self.properties_panel.set_italic(None)
                self.properties_panel.set_shading(None)
                self.properties_panel.set_font_color(None)
        elif target == "cell_override":
            self._load_panel_from_selected_cells()

    def _on_tag_changed(self, tag: str):
        if not self._current_style:
            return

        style_name = self._current_style.name

        old_tag, _ = find_mapping_for_style(self._mappings, style_name)

        if old_tag:
            del self._mappings[old_tag]

        if tag:
            if not tag.startswith("‹!"):
                tag = "‹!" + tag
            if not tag.endswith("›"):
                tag = tag + "›"
            self._mappings[tag] = {
                "table": "\u041F\u0440\u043E\u0441\u0442\u0430\u044F \u0442\u0430\u0431\u043B\u0438\u0446\u0430 1",
                "header": self.structure_panel.get_header_style() or "Table Header 1",
                "text": self.structure_panel.get_text_style() or "Table Text 1",
                "preset": style_name
            }

    def _on_property_changed(self):
        if self._current_style is None:
            return

        target = self.properties_panel.get_target()
        shading = self.properties_panel.get_shading()
        bold = self.properties_panel.get_bold()
        italic = self.properties_panel.get_italic()
        font_color = self.properties_panel.get_font_color()

        use_shading = self.properties_panel.use_shading_cb.checkState() == Qt.Checked
        use_font_color = self.properties_panel.use_font_color_cb.checkState() == Qt.Checked

        if target == "table_defaults":
            if use_shading:
                self._current_style.default_shading = shading
        elif target in ["header", "odd", "even", "last_row", "first_column", "last_column"]:
            if target not in self._current_style.row_types:
                self._current_style.row_types[target] = RowTypeStyle()
            row_style = self._current_style.row_types[target]
            if use_shading:
                row_style.shading = shading
            row_style.bold = bold
            row_style.italic = italic
        elif target == "cell_override":
            for r, c in self.grid_widget.selected_cells:
                col_letter = chr(ord('A') + c)
                cell_ref = f"{col_letter}{r + 1}"

                existing = None
                for ovr in self._current_style.cell_overrides:
                    if ovr.cell_ref == cell_ref:
                        existing = ovr
                        break

                if existing is None:
                    existing = CellOverride(cell_ref=cell_ref)
                    self._current_style.cell_overrides.append(existing)

                if use_shading:
                    existing.shading = shading
                existing.bold = bold
                existing.italic = italic
                if use_font_color:
                    existing.font_color = font_color

        self.grid_widget.update_visuals(self._current_style)
        self._update_json_preview()
        self._update_current_style_in_dict()

    def _on_structure_changed(self):
        if self._current_style is None:
            return

        self.structure_panel.auto_distribute_widths(self.grid_widget.get_selected_columns())

        self._current_style.column_widths = self.structure_panel.get_column_widths()
        self._current_style.row_heights = self.structure_panel.get_row_heights()
        self._current_style.empty_row_top = self.structure_panel.get_empty_row_top()
        self._current_style.empty_row_bottom = self.structure_panel.get_empty_row_bottom()
        self._current_style.empty_row_height = self.structure_panel.get_empty_row_height()
        self._current_style.fit_to_page = self.structure_panel.get_fit_to_page()
        self._current_style.table_width = self.structure_panel.get_table_width()
        self._current_style.text_wrap = self.structure_panel.get_text_wrap()
        self._current_style.left_from_text = self.structure_panel.get_left_from_text()
        self._current_style.right_from_text = self.structure_panel.get_right_from_text()

        self.grid_widget.update_visuals(self._current_style)
        self._update_json_preview()
        self._update_current_style_in_dict()

    def _on_rules_changed(self):
        if self._current_style:
            self._current_style.color_rules = self.color_rules_widget.get_rules()
            self._update_json_preview()
            self._update_current_style_in_dict()

    def _on_apply_border(self):
        if self._current_style is None:
            return
        border_style = self.properties_panel.get_border_style()
        self._apply_border_style(border_style)

    def _on_clear_borders(self):
        if self._current_style is None:
            return
        nil_border = BorderStyle(color="000000", size=0, val="nil")
        self._apply_border_style(nil_border)

    def _apply_border_style(self, border_style: BorderStyle):
        target = self.properties_panel.get_target()
        border_side = self.properties_panel.get_border_side()
        sides = expand_border_side(border_side)

        if target == "table_defaults":
            for side in sides:
                self._current_style.default_borders[side] = BorderStyle(
                    color=border_style.color,
                    size=border_style.size,
                    val=border_style.val
                )
        elif target in ["header", "odd", "even", "last_row", "first_column", "last_column"]:
            if target not in self._current_style.row_types:
                self._current_style.row_types[target] = RowTypeStyle()
            row_style = self._current_style.row_types[target]
            for side in sides:
                row_style.borders[side] = BorderStyle(
                    color=border_style.color,
                    size=border_style.size,
                    val=border_style.val
                )
        elif target == "cell_override":
            for r, c in self.grid_widget.selected_cells:
                col_letter = chr(ord('A') + c)
                cell_ref = f"{col_letter}{r + 1}"

                existing = None
                for ovr in self._current_style.cell_overrides:
                    if ovr.cell_ref == cell_ref:
                        existing = ovr
                        break

                if existing is None:
                    existing = CellOverride(cell_ref=cell_ref)
                    self._current_style.cell_overrides.append(existing)

                for side in sides:
                    existing.borders[side] = BorderStyle(
                        color=border_style.color,
                        size=border_style.size,
                        val=border_style.val
                    )

        self.grid_widget.update_visuals(self._current_style)
        self._update_json_preview()
        self._update_current_style_in_dict()

    def _update_current_style_in_dict(self):
        if self._current_style is not None:
            name = self.style_list_panel.current_style_name()
            if name:
                self._styles[name] = self._current_style.to_dict()

    def _update_json_preview(self):
        if not self._current_style:
            self.json_preview.set_text("\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0442\u0438\u043B\u044C")
            return

        data = self._current_style.to_dict()
        self.json_preview.set_data(data)

    def _run_layout(self):
        import os
        from pathlib import Path
        import json
        from PyQt5.QtWidgets import QApplication

        self.status_bar.showMessage("\u0412\u0451\u0440\u0441\u0442\u043A\u0430...")
        QApplication.processEvents()

        try:
            root = Path(__file__).resolve().parent.parent.parent
            app_cfg_path = root / "configs" / "app_config.json"
            if app_cfg_path.exists():
                with open(app_cfg_path, "r", encoding="utf-8") as f:
                    ac = json.load(f)
            else:
                ac = {"paths": {}}
            paths = ac.get("paths", {})

            template_raw = paths.get("template", "")
            template_path = Path(template_raw) if template_raw else root / "workspace" / "templates" / "RpRef1.docx"
            if not template_path.is_absolute():
                template_path = root / template_path

            if not template_path.exists():
                QMessageBox.warning(
                    self, "\u041E\u0448\u0438\u0431\u043A\u0430",
                    f"\u0428\u0430\u0431\u043B\u043E\u043D \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D: {template_path}"
                )
                self.status_bar.showMessage("\u041E\u0448\u0438\u0431\u043A\u0430: \u0448\u0430\u0431\u043B\u043E\u043D \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D")
                return

            config = load_configuration()
            batch_mode = ac.get("batch_mode", False)

            if batch_mode:
                input_folder_raw = paths.get("input_md", "")
                output_folder_raw = paths.get("output_docx", "")
                input_folder = Path(input_folder_raw) if input_folder_raw else None
                output_folder = Path(output_folder_raw) if output_folder_raw else None

                if not input_folder or not input_folder.exists() or not input_folder.is_dir():
                    QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430", "\u041F\u0430\u043F\u043A\u0430 \u0441 MD \u0444\u0430\u0439\u043B\u0430\u043C\u0438 \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u0430")
                    self.status_bar.showMessage("\u041E\u0448\u0438\u0431\u043A\u0430: \u043F\u0430\u043F\u043A\u0430 \u0441 MD \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u0430")
                    return

                if not output_folder:
                    output_folder = input_folder
                if not output_folder.is_dir():
                    output_folder.mkdir(parents=True, exist_ok=True)

                md_files = sorted(input_folder.glob("*.md"))
                if not md_files:
                    QMessageBox.warning(self, "\u041E\u0448\u0438\u0431\u043A\u0430", f"MD \u0444\u0430\u0439\u043B\u044B \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u044B \u0432 {input_folder}")
                    self.status_bar.showMessage("\u041E\u0448\u0438\u0431\u043A\u0430: MD \u0444\u0430\u0439\u043B\u044B \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u044B")
                    return

                success_count = 0
                for md_file in md_files:
                    output_path = output_folder / f"{md_file.stem}.docx"
                    try:
                        raw_markdown = md_file.read_text(encoding="utf-8")
                        processed_md = preprocess_markdown(raw_markdown, config)
                        builder = DocxBuilder(template_path, config)
                        builder.build(processed_md)
                        ensure_output_dir(output_path.parent)
                        builder.save(output_path)
                        success_count += 1
                        print(f"[OK] {md_file.name} \u2192 {output_path.name}")
                    except Exception as e:
                        print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u043F\u0440\u0438 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0435 {md_file.name}: {e}")

                self.status_bar.showMessage(f"\u0413\u043E\u0442\u043E\u0432\u043E! \u041E\u0431\u0440\u0430\u0431\u043E\u0442\u0430\u043D\u043E {success_count}/{len(md_files)} \u0444\u0430\u0439\u043B\u043E\u0432")
            else:
                input_raw = paths.get("input_md", "")
                output_raw = paths.get("output_docx", "")

                input_md_path = Path(input_raw) if input_raw else root / "workspace" / "input" / "input.md"
                if not input_md_path.is_absolute():
                    input_md_path = root / input_md_path

                if not input_md_path.exists():
                    QMessageBox.warning(
                        self, "\u041E\u0448\u0438\u0431\u043A\u0430",
                        f"MD \u0444\u0430\u0439\u043B \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D: {input_md_path}"
                    )
                    self.status_bar.showMessage("\u041E\u0448\u0438\u0431\u043A\u0430: MD \u0444\u0430\u0439\u043B \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D")
                    return

                if not output_raw.strip():
                    output_path = input_md_path.with_suffix(".docx")
                else:
                    output_path = Path(output_raw)
                    if not output_path.is_absolute():
                        output_path = root / output_path

                raw_markdown = input_md_path.read_text(encoding="utf-8")
                processed_md = preprocess_markdown(raw_markdown, config)

                builder = DocxBuilder(template_path, config)
                builder.build(processed_md)

                ensure_output_dir(output_path.parent)
                builder.save(output_path)
                self.status_bar.showMessage(f"\u0413\u043E\u0442\u043E\u0432\u043E! \u0421\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E: {output_path}")

                if config.open_after_convert:
                    abs_path = output_path.resolve()
                    os.startfile(abs_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "\u041E\u0448\u0438\u0431\u043A\u0430 \u0432\u0451\u0440\u0441\u0442\u043A\u0438", str(e))
            self.status_bar.showMessage(f"\u041E\u0448\u0438\u0431\u043A\u0430: {e}")
