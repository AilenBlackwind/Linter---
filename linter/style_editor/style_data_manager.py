from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class StyleDataManager:
    def __init__(self, styles_path: Path, mappings_path: Path,
                 template_path: Optional[Path] = None,
                 spacing_path: Optional[Path] = None,
                 general_styles_path: Optional[Path] = None,
                 app_config_path: Optional[Path] = None):
        self.styles_path = styles_path
        self.mappings_path = mappings_path
        self.template_path = template_path
        self.spacing_path = spacing_path
        self.general_styles_path = general_styles_path
        self.app_config_path = app_config_path

    @classmethod
    def from_root(cls, root_dir: Path) -> StyleDataManager:
        configs_dir = root_dir / "configs"
        template_dir = root_dir / "workspace" / "templates"
        return cls(
            styles_path=configs_dir / "table_styles.json",
            mappings_path=configs_dir / "table_mappings.json",
            template_path=template_dir / "RpRef1.docx",
            spacing_path=configs_dir / "spacing.json",
            general_styles_path=configs_dir / "styles.json",
            app_config_path=configs_dir / "app_config.json",
        )

    def load_app_config(self) -> dict:
        if self.app_config_path and self.app_config_path.exists():
            try:
                with open(self.app_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] Ошибка загрузки app_config.json: {e}")
        return {"paths": {}, "open_after_convert": True}

    def save_app_config(self, data: dict) -> None:
        if self.app_config_path:
            try:
                with open(self.app_config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise IOError(f"не удалось сохранить app_config.json: {e}")

    def load_table_styles(self) -> Dict[str, Any]:
        if self.styles_path and self.styles_path.exists():
            try:
                with open(self.styles_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 table_styles.json: {e}")
        return {}

    def save_table_styles(self, styles: Dict[str, Any]) -> None:
        if self.styles_path:
            try:
                with open(self.styles_path, 'w', encoding='utf-8') as f:
                    json.dump(styles, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise IOError(f"\u043D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C table_styles.json: {e}")

    def load_mappings(self) -> Dict[str, Any]:
        if self.mappings_path and self.mappings_path.exists():
            try:
                with open(self.mappings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 table_mappings.json: {e}")
        return {}

    def save_mappings(self, mappings: Dict[str, Any]) -> None:
        if self.mappings_path:
            try:
                with open(self.mappings_path, 'w', encoding='utf-8') as f:
                    json.dump(mappings, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise IOError(f"\u043D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C table_mappings.json: {e}")

    def load_template_styles(self) -> List[str]:
        template = self._resolve_template()
        if not template:
            return []
        try:
            from docx import Document
            doc = Document(template)
            return [s.name for s in doc.styles if s.type == 1]
        except Exception as e:
            print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 \u0441\u0442\u0438\u043B\u0435\u0439 \u0448\u0430\u0431\u043B\u043E\u043D\u0430: {e}")
            return []

    def _resolve_template(self) -> Optional[str]:
        if self.template_path and self.template_path.exists():
            return str(self.template_path)
        default = Path(__file__).resolve().parent.parent.parent / "workspace" / "templates" / "RpRef1.docx"
        if default.exists():
            return str(default)
        return None

    def load_spacing(self) -> Dict[str, Any]:
        if self.spacing_path and self.spacing_path.exists():
            try:
                with open(self.spacing_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 spacing.json: {e}")
        return {}

    def save_spacing(self, data: Dict[str, Any]) -> None:
        if self.spacing_path:
            try:
                with open(self.spacing_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise IOError(f"\u043D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C spacing.json: {e}")

    def load_general_styles(self) -> Dict[str, Any]:
        if self.general_styles_path and self.general_styles_path.exists():
            try:
                with open(self.general_styles_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] \u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 styles.json: {e}")
        return {}

    def save_general_styles(self, data: Dict[str, Any]) -> None:
        if self.general_styles_path:
            try:
                with open(self.general_styles_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise IOError(f"\u043D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C styles.json: {e}")

    @staticmethod
    def convert_flat_to_advanced(data: dict) -> dict:
        result = {
            'renderer': 'advanced',
            'layout': data.get('layout', 'auto'),
            'cell_margins': data.get('cell_margins', {'top': 90, 'start': 110, 'bottom': 90, 'end': 110}),
            'default_borders': dict(data.get('default_borders', {})),
            'default_shading': data.get('default_shading'),
            'fit_to_page': data.get('fit_to_page', True),
            'table_width': data.get('table_width'),
            'column_widths': data.get('column_widths'),
            'row_heights': data.get('row_heights'),
            'row_types': dict(data.get('row_types', {})),
            'cell_overrides': dict(data.get('cell_overrides', {})),
            'color_rules': list(data.get('color_rules', [])),
        }

        renderer = data.get('renderer', 'standard')

        if renderer == 'zebra':
            row_types = result['row_types']
            if 'header_fill' in data:
                row_types['header'] = {'shading': data['header_fill']}
            if 'row_fill' in data:
                row_types['odd'] = {'shading': data['row_fill']}
            if 'header_bottom_color' in data:
                hdr = row_types.setdefault('header', {})
                borders = hdr.setdefault('borders', {})
                borders['bottom'] = {
                    'color': data['header_bottom_color'],
                    'size': data.get('header_bottom_size', 8),
                    'val': 'single',
                }
            if 'inner_v_color' in data:
                sz = data.get('inner_v_size', 4)
                v = {'color': data['inner_v_color'], 'size': sz, 'val': 'single'}
                result['default_borders'].setdefault('left', v)
                result['default_borders'].setdefault('right', v)
        elif renderer == 'standard':
            if 'header_fill' in data and data['header_fill']:
                result['row_types']['header'] = {'shading': data['header_fill']}
            if 'band_fill' in data and data['band_fill']:
                result['row_types']['odd'] = {'shading': data['band_fill']}
            if 'border_color' in data:
                result['default_borders']['all'] = {
                    'color': data['border_color'],
                    'size': data.get('border_size', 8),
                    'val': 'single',
                }

        return result
