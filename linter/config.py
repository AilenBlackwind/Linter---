import json
from pathlib import Path
from typing import Dict, Any, Optional


def deep_copy(data):
    return json.loads(json.dumps(data))


DEFAULT_TABLE_PRESETS = {
    "plain": {
        "renderer": "standard",
        "border_color": "666666",
        "border_size": 8,
        "header_fill": "D9D9D9",
        "band_fill": None
    },
    "zebra": {
        "renderer": "zebra",
        "header_fill": "FFFFFF",
        "header_bottom_color": "8A8A8A",
        "header_bottom_size": 8,
        "row_fill": "DCDCF7",
        "inner_v_color": "E7E7F7",
        "inner_v_size": 4
    },
    "fancy": {
        "renderer": "standard",
        "border_color": "5B6C8F",
        "border_size": 10,
        "header_fill": "DCE6F1",
        "band_fill": "EEF3F8"
    }
}

DEFAULT_TABLE_MAPPINGS = {
    "<!zebra>": {
        "table": "Простая таблица 1",
        "header": "Table Header 1",
        "text": "Table Text 1",
        "preset": "zebra"
    },
    "<!plain>": {
        "table": "Простая таблица 2",
        "header": "Table Header 2",
        "text": "Table Text 2",
        "preset": "plain"
    },
    "<!fancy>": {
        "table": "Простая таблица 1",
        "header": "Table Header 1",
        "text": "Table Text 1",
        "preset": "fancy"
    }
}


def normalize_preset(name, preset):
    base_name = 'zebra' if preset.get('renderer') == 'zebra' or name == 'zebra' else 'plain'
    if name == 'fancy':
        base_name = 'fancy'
    normalized = deep_copy(DEFAULT_TABLE_PRESETS[base_name])
    normalized.update(preset)
    if 'renderer' not in normalized:
        normalized['renderer'] = 'zebra' if name == 'zebra' else 'standard'
    return normalized


def normalize_table_mapping(tag, config):
    base = {
        "table": "Простая таблица 2",
        "header": "Table Header 2",
        "text": "Table Text 2",
        "preset": "plain",
        "column_widths": None
    }
    if tag in DEFAULT_TABLE_MAPPINGS:
        base.update(DEFAULT_TABLE_MAPPINGS[tag])
    base.update(config)
    return base


class InfoboxStyle:
    def __init__(self, key: str, data: dict):
        self.key = key
        self.style_name = data.get("style_name", "")
        self.multi_paragraph = data.get("multi_paragraph", False)
        self.opening_tag = data.get("opening_tag", f"::: {key}")
        self.closing_tag = data.get("closing_tag", ":::")
        self.list_bullet_style = data.get("list_bullet_style", "")
        self.list_number_style = data.get("list_number_style", "")


class TableStyle:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.header_bold = data.get("header", {}).get("bold", True)
        self.header_bg_color = data.get("header", {}).get("background_color", "#4472C4")
        self.header_font_color = data.get("header", {}).get("font_color", "#FFFFFF")
        self.alternating_rows = data.get("alternating_rows", {})
        self.borders = data.get("borders", {})
        self.cell_padding = data.get("cell_padding", {})
        self.auto_fit = data.get("auto_fit", True)

    @property
    def is_alternating(self) -> bool:
        return self.alternating_rows.get("enabled", False)

    def alternating_colors(self):
        if self.is_alternating:
            return (
                self.alternating_rows.get("even_color", "#D9E2F3"),
                self.alternating_rows.get("odd_color", "#FFFFFF")
            )
        return None


class Config:
    def __init__(self, styles_data: dict, table_styles_data: dict, paths_data: dict = None,
                 table_presets_data: dict = None, table_mappings_data: dict = None,
                 spacing_data: dict = None):
        self.input_md = "workspace/input/input.md"
        self.output_docx = "workspace/output/Result.docx"
        self.template = "workspace/templates/RpRef1.docx"
        self.open_after_convert = True

        if paths_data:
            paths = paths_data.get("paths", {})
            if "input_md" in paths:
                self.input_md = paths["input_md"]
            if "output_docx" in paths:
                self.output_docx = paths["output_docx"]
            if "template" in paths:
                self.template = paths["template"]
            if "open_after_convert" in paths_data:
                self.open_after_convert = bool(paths_data["open_after_convert"])

        self.infobox_styles = {}
        self.single_paragraph_styles = {}

        infobox_config = styles_data.get("infobox_styles", {})
        for key, style_def in infobox_config.items():
            ib_style = InfoboxStyle(key, style_def)
            self.infobox_styles[key] = ib_style

        single_config = styles_data.get("inline_styles", {}).get("single_paragraph", {})
        for key, style_def in single_config.items():
            self.single_paragraph_styles[key] = {
                "style_name": style_def.get("style_name"),
                "tag": style_def.get("tag", f"::: {key}")
            }

        spacing = spacing_data or {}
        self.before_heading_spacing = spacing.get("before_heading", 25)
        self.after_heading_spacing = spacing.get("after_heading", 0)
        self.after_list_spacing = spacing.get("after_list", 10)
        self.after_table_spacing = spacing.get("after_table", 10)
        self.table_before_heading = spacing.get("table_before_heading", 25)
        self.before_table_spacing = spacing.get("before_table", 0)

        raw_block_types = spacing.get("no_indent_after_block_types")
        if raw_block_types is None:
            old_bool = spacing.get("no_indent_after_heading_list", True)
            raw_block_types = ["heading", "list", "table", "thematic_break"] if old_bool else []
        self.no_indent_after_block_types = raw_block_types
        self.no_indent_if_first_bold = spacing.get("no_indent_if_first_bold", True)

        self.table_styles = {}
        custom_table_styles = table_styles_data.get("custom_styles", {})
        for name, data in custom_table_styles.items():
            self.table_styles[name] = TableStyle(name, data)
        self.default_table_style = table_styles_data.get("default_style", "Table Grid")

        self.table_presets = deep_copy(DEFAULT_TABLE_PRESETS)
        if table_presets_data:
            for name, preset in table_presets_data.items():
                if isinstance(preset, dict):
                    self.table_presets[name] = normalize_preset(name, preset)

        self.table_mappings = {}
        for tag, config in DEFAULT_TABLE_MAPPINGS.items():
            self.table_mappings[tag.lower()] = normalize_table_mapping(tag.lower(), config)

        if table_mappings_data:
            for tag, config in table_mappings_data.items():
                if isinstance(config, dict):
                    self.table_mappings[tag.lower()] = normalize_table_mapping(tag.lower(), config)

    def get_infobox_style(self, key: str) -> Optional[InfoboxStyle]:
        return self.infobox_styles.get(key)

    def get_single_paragraph_style(self, key: str) -> Optional[dict]:
        return self.single_paragraph_styles.get(key)

    def get_table_style(self, name: Optional[str] = None) -> TableStyle:
        if name and name in self.table_styles:
            return self.table_styles[name]
        return TableStyle("_default", {})


def load_configuration() -> Config:
    project_root = Path(__file__).parent.parent

    styles_path = project_root / "configs" / "styles.json"
    if not styles_path.exists():
        raise FileNotFoundError(f"Файл стилей не найден: {styles_path}")
    with open(styles_path, "r", encoding="utf-8") as f:
        styles_data = json.load(f)

    table_styles_path = project_root / "configs" / "table_styles.json"
    table_styles_data = {}
    table_presets_data = {}
    if table_styles_path.exists():
        with open(table_styles_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if 'plain' in raw or 'zebra' in raw or 'fancy' in raw or 'custom_styles' not in raw:
            table_presets_data = raw
        else:
            table_styles_data = raw
        print(f"[+] Загружены стили таблиц из table_styles.json")

    table_mappings_path = project_root / "configs" / "table_mappings.json"
    table_mappings_data = {}
    if table_mappings_path.exists():
        with open(table_mappings_path, "r", encoding="utf-8") as f:
            table_mappings_data = json.load(f)
        print(f"[+] Загружены маппинги таблиц из table_mappings.json")

    config_path = project_root / "configs" / "app_config.json"
    paths_data = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            paths_data = json.load(f)
        print(f"[+] Используем пользовательские пути из configs/app_config.json")

    spacing_path = project_root / "configs" / "spacing.json"
    spacing_data = None
    if spacing_path.exists():
        with open(spacing_path, "r", encoding="utf-8") as f:
            spacing_data = json.load(f)
        print(f"[+] Загружены отступы из spacing.json")

    validate_config(styles_data, table_styles_data)

    return Config(styles_data, table_styles_data, paths_data, table_presets_data, table_mappings_data, spacing_data)


def validate_config(styles_data: dict, table_styles_data: dict) -> None:
    for key, val in styles_data.get("infobox_styles", {}).items():
        if "style_name" not in val:
            raise ValueError(f"В инфобоксе '{key}' не указан 'style_name'.")

    for name, val in table_styles_data.get("custom_styles", {}).items():
        if "header" not in val:
            print(f"\u26A0\uFE0F В стиле таблицы '{name}' нет секции 'header', используется заголовок по умолчанию.")
