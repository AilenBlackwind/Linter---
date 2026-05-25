from dataclasses import dataclass, field
from typing import Dict, Optional, List, Literal, get_type_hints
import re


BorderSide = Literal['top', 'bottom', 'left', 'right', 'horizontal', 'vertical', 'all']

TriggerType = Literal['equals', 'contains', 'starts_with', 'ends_with', 'matches_regex', 'has_text']


@dataclass
class BorderStyle:
    color: str = "666666"
    size: int = 8
    val: str = "single"


@dataclass
class CellMargins:
    top: int = 90
    start: int = 110
    bottom: int = 90
    end: int = 110


@dataclass
class ColorRule:
    name: str = ""
    trigger: TriggerType = "equals"
    value: str = ""
    case_sensitive: bool = False
    column: Optional[str] = None

    shading: Optional[str] = None
    font_color: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None

    priority: int = 0

    borders: Optional[Dict[BorderSide, BorderStyle]] = None

    def matches(self, cell_text: str, col_idx: Optional[int] = None) -> bool:
        text = cell_text.strip()

        if self.trigger == 'has_text':
            if not text:
                return False
            if self.column and col_idx is not None:
                col_letter = chr(ord('A') + col_idx)
                return col_letter == self.column.upper()
            return True

        if not self.case_sensitive:
            text = text.lower()
            rule_value = self.value.lower()
        else:
            rule_value = self.value

        if self.trigger == 'equals':
            return text == rule_value

        elif self.trigger == 'contains':
            return rule_value in text

        elif self.trigger == 'starts_with':
            return text.startswith(rule_value)

        elif self.trigger == 'ends_with':
            return text.endswith(rule_value)

        elif self.trigger == 'matches_regex':
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.match(self.value, text, flags))
            except re.error:
                return False

        return False

    def apply_to_style(self, style_dict: dict) -> dict:
        result = style_dict.copy()

        if self.shading is not None:
            result['shading'] = self.shading
        if self.font_color is not None:
            result['font_color'] = self.font_color
        if self.bold is not None:
            result['bold'] = self.bold
        if self.italic is not None:
            result['italic'] = self.italic
        if self.borders:
            if 'borders' not in result:
                result['borders'] = {}
            for side, border_style in self.borders.items():
                result['borders'][side] = border_style

        return result


@dataclass
class RowTypeStyle:
    shading: Optional[str] = None
    font_color: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    font_size: Optional[int] = None
    borders: Dict[BorderSide, BorderStyle] = field(default_factory=dict)
    repeat: bool = False


@dataclass
class CellOverride:
    cell_ref: str
    shading: Optional[str] = None
    font_color: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    borders: Dict[BorderSide, BorderStyle] = field(default_factory=dict)


@dataclass
class TableStyle:
    name: str = ""
    renderer: Literal['advanced', 'zebra', 'standard'] = "advanced"
    layout: Literal['auto', 'fixed'] = "auto"
    cell_margins: CellMargins = field(default_factory=CellMargins)
    default_borders: Dict[BorderSide, BorderStyle] = field(default_factory=dict)
    default_shading: Optional[str] = None
    column_widths: Optional[List[float]] = None
    row_heights: Optional[List[int]] = None
    empty_row_top: bool = False
    empty_row_bottom: bool = False
    empty_row_height: int = 200
    fit_to_page: bool = True
    table_width: Optional[int] = None
    row_types: Dict[str, RowTypeStyle] = field(default_factory=lambda: {
        'header': RowTypeStyle(),
        'odd': RowTypeStyle(),
        'even': RowTypeStyle(),
        'last_row': RowTypeStyle(),
        'first_column': RowTypeStyle(),
        'last_column': RowTypeStyle(),
    })
    cell_overrides: List[CellOverride] = field(default_factory=list)
    color_rules: List[ColorRule] = field(default_factory=list)
    text_wrap: str = "around"
    left_from_text: int = 0
    right_from_text: int = 0

    @classmethod
    def from_dict(cls, data: dict, name: str = "") -> 'TableStyle':
        style = cls(name=name)
        style.renderer = data.get('renderer', 'advanced')
        style.layout = data.get('layout', 'auto')

        if 'cell_margins' in data:
            margins = data['cell_margins']
            style.cell_margins = CellMargins(
                top=margins.get('top', 90),
                start=margins.get('start', 110),
                bottom=margins.get('bottom', 90),
                end=margins.get('end', 110),
            )

        if 'default_borders' in data:
            for side, border_data in data['default_borders'].items():
                style.default_borders[side] = BorderStyle(
                    color=border_data.get('color', '666666'),
                    size=border_data.get('size', 8),
                    val=border_data.get('val', 'single'),
                )
        elif 'borders' in data.get('table_defaults', {}):
            borders = data['table_defaults']['borders']
            for side, border_data in borders.items():
                style.default_borders[side] = BorderStyle(
                    color=border_data.get('color', '666666'),
                    size=border_data.get('size', 8),
                    val=border_data.get('val', 'single'),
                )

        if 'default_shading' in data:
            style.default_shading = data['default_shading']
        elif 'shading' in data.get('table_defaults', {}):
            style.default_shading = data['table_defaults']['shading']

        if 'row_types' in data:
            for row_type_name, row_data in data['row_types'].items():
                row_style = RowTypeStyle()
                row_style.shading = row_data.get('shading')
                row_style.font_color = row_data.get('font_color')
                row_style.bold = row_data.get('bold')
                row_style.italic = row_data.get('italic')
                row_style.repeat = row_data.get('repeat', False)

                if 'borders' in row_data:
                    for side, border_data in row_data['borders'].items():
                        row_style.borders[side] = BorderStyle(
                            color=border_data.get('color', '666666'),
                            size=border_data.get('size', 8),
                            val=border_data.get('val', 'single'),
                        )

                style.row_types[row_type_name] = row_style

        if 'cell_overrides' in data:
            for cell_ref, cell_data in data['cell_overrides'].items() if isinstance(data['cell_overrides'], dict) else []:
                override = CellOverride(cell_ref=cell_ref)
                override.shading = cell_data.get('shading')
                override.font_color = cell_data.get('font_color')
                override.bold = cell_data.get('bold')
                override.italic = cell_data.get('italic')

                if 'borders' in cell_data:
                    for side, border_data in cell_data['borders'].items():
                        override.borders[side] = BorderStyle(
                            color=border_data.get('color', '666666'),
                            size=border_data.get('size', 8),
                            val=border_data.get('val', 'single'),
                        )

                style.cell_overrides.append(override)

        if 'column_widths' in data and isinstance(data['column_widths'], list):
            style.column_widths = [float(w) for w in data['column_widths']]
        if 'row_heights' in data and isinstance(data['row_heights'], list):
            style.row_heights = [int(h) for h in data['row_heights']]
        if 'empty_row_top' in data:
            style.empty_row_top = bool(data['empty_row_top'])
        if 'empty_row_bottom' in data:
            style.empty_row_bottom = bool(data['empty_row_bottom'])
        if 'empty_row_height' in data:
            style.empty_row_height = int(data['empty_row_height'])
        if 'fit_to_page' in data:
            style.fit_to_page = bool(data['fit_to_page'])
        if 'table_width' in data and data['table_width'] is not None:
            style.table_width = int(data['table_width'])

        if 'color_rules' in data:
            for rule_data in data['color_rules']:
                rule = ColorRule(
                    name=rule_data.get('name', ''),
                    trigger=rule_data.get('trigger', 'equals'),
                    value=rule_data.get('value', ''),
                    case_sensitive=rule_data.get('case_sensitive', False),
                    column=rule_data.get('column'),
                    shading=rule_data.get('apply', {}).get('shading') if 'apply' in rule_data else rule_data.get('shading'),
                    font_color=rule_data.get('apply', {}).get('font_color') if 'apply' in rule_data else rule_data.get('font_color'),
                    bold=rule_data.get('apply', {}).get('bold') if 'apply' in rule_data else rule_data.get('bold'),
                    italic=rule_data.get('apply', {}).get('italic') if 'apply' in rule_data else rule_data.get('italic'),
                    priority=rule_data.get('priority', 0),
                )
                style.color_rules.append(rule)

        style.text_wrap = data.get('text_wrap', 'around')
        style.left_from_text = data.get('left_from_text', 0)
        style.right_from_text = data.get('right_from_text', 0)

        return style

    def to_dict(self) -> dict:
        sorted_rules = sorted(self.color_rules, key=lambda r: r.priority, reverse=True)

        result = {
            'renderer': self.renderer,
            'layout': self.layout,
            'cell_margins': {
                'top': self.cell_margins.top,
                'start': self.cell_margins.start,
                'bottom': self.cell_margins.bottom,
                'end': self.cell_margins.end,
            },
            'default_borders': {
                side: {
                    'color': bs.color,
                    'size': bs.size,
                    'val': bs.val,
                }
                for side, bs in self.default_borders.items()
            },
            'default_shading': self.default_shading,
            'empty_row_top': self.empty_row_top,
            'empty_row_bottom': self.empty_row_bottom,
            'empty_row_height': self.empty_row_height,
            'fit_to_page': self.fit_to_page,
            'table_width': self.table_width,
            'column_widths': self.column_widths,
            'row_heights': self.row_heights,
            'row_types': {},
            'cell_overrides': {},
            'color_rules': [
                {
                    'name': rule.name,
                    'trigger': rule.trigger,
                    'value': rule.value,
                    'case_sensitive': rule.case_sensitive,
                    'column': rule.column,
                    'shading': rule.shading,
                    'font_color': rule.font_color,
                    'bold': rule.bold,
                    'italic': rule.italic,
                    'priority': rule.priority,
                }
                for rule in sorted_rules
            ],
            'text_wrap': self.text_wrap,
            'left_from_text': self.left_from_text,
            'right_from_text': self.right_from_text,
        }

        for row_type_name, row_style in self.row_types.items():
            if row_style.shading or row_style.font_color or row_style.bold or row_style.italic or row_style.borders or row_style.repeat:
                row_data = {}
                if row_style.shading:
                    row_data['shading'] = row_style.shading
                if row_style.font_color:
                    row_data['font_color'] = row_style.font_color
                if row_style.bold is not None:
                    row_data['bold'] = row_style.bold
                if row_style.italic is not None:
                    row_data['italic'] = row_style.italic
                if row_style.repeat:
                    row_data['repeat'] = row_style.repeat
                if row_style.borders:
                    row_data['borders'] = {
                        side: {
                            'color': bs.color,
                            'size': bs.size,
                            'val': bs.val,
                        }
                        for side, bs in row_style.borders.items()
                    }
                result['row_types'][row_type_name] = row_data

        for override in self.cell_overrides:
            cell_data = {}
            if override.shading:
                cell_data['shading'] = override.shading
            if override.font_color:
                cell_data['font_color'] = override.font_color
            if override.bold is not None:
                cell_data['bold'] = override.bold
            if override.italic is not None:
                cell_data['italic'] = override.italic
            if override.borders:
                cell_data['borders'] = {
                    side: {
                        'color': bs.color,
                        'size': bs.size,
                        'val': bs.val,
                    }
                    for side, bs in override.borders.items()
                }
            result['cell_overrides'][override.cell_ref] = cell_data

        return result
