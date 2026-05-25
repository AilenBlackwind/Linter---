from __future__ import annotations

from typing import Dict, List, Optional

from linter.converter.tables.advanced.models import BorderStyle, TableStyle


def expand_border_side(side: str) -> List[str]:
    if side == 'all':
        return ['top', 'bottom', 'left', 'right']
    elif side == 'horizontal':
        return ['top', 'bottom']
    elif side == 'vertical':
        return ['left', 'right']
    return [side]


def get_cell_shading(style: Optional[TableStyle], row_idx: int, col_idx: int, row_count: int, col_count: int) -> Optional[str]:
    if not style:
        return None

    shading = style.default_shading

    if row_idx == 0 and 'header' in style.row_types:
        s = style.row_types['header']
        if s.shading:
            shading = s.shading
    elif row_idx == row_count - 1 and 'last_row' in style.row_types:
        s = style.row_types['last_row']
        if s.shading:
            shading = s.shading
    elif row_idx % 2 == 0 and 'odd' in style.row_types:
        s = style.row_types['odd']
        if s.shading:
            shading = s.shading
    elif row_idx % 2 == 1 and 'even' in style.row_types:
        s = style.row_types['even']
        if s.shading:
            shading = s.shading

    if col_idx == 0 and 'first_column' in style.row_types:
        s = style.row_types['first_column']
        if s.shading:
            shading = s.shading
    elif col_idx == col_count - 1 and 'last_column' in style.row_types:
        s = style.row_types['last_column']
        if s.shading:
            shading = s.shading

    col_letter = chr(ord('A') + col_idx)
    cell_ref = f"{col_letter}{row_idx + 1}"
    for ovr in style.cell_overrides:
        if ovr.cell_ref == cell_ref:
            if ovr.shading:
                shading = ovr.shading
            break

    return shading


def get_cell_borders(style: Optional[TableStyle], row_idx: int, col_idx: int, row_count: int, col_count: int) -> Dict[str, BorderStyle]:
    if not style:
        return {}

    borders: Dict[str, BorderStyle] = {}

    for side, bs in style.default_borders.items():
        for s in expand_border_side(side):
            borders[s] = BorderStyle(
                color=bs.color,
                size=bs.size,
                val=bs.val
            )

    row_type = None
    if row_idx == 0 and 'header' in style.row_types:
        row_type = 'header'
    elif row_idx == row_count - 1 and 'last_row' in style.row_types:
        row_type = 'last_row'
    elif row_idx % 2 == 0 and 'odd' in style.row_types:
        row_type = 'odd'
    elif row_idx % 2 == 1 and 'even' in style.row_types:
        row_type = 'even'

    if row_type and row_type in style.row_types:
        row_style = style.row_types[row_type]
        for side, bs in row_style.borders.items():
            for s in expand_border_side(side):
                borders[s] = BorderStyle(
                    color=bs.color,
                    size=bs.size,
                    val=bs.val
                )

    col_type = None
    if col_idx == 0 and 'first_column' in style.row_types:
        col_type = 'first_column'
    elif col_idx == col_count - 1 and 'last_column' in style.row_types:
        col_type = 'last_column'

    if col_type and col_type in style.row_types:
        col_style = style.row_types[col_type]
        for side, bs in col_style.borders.items():
            for s in expand_border_side(side):
                borders[s] = BorderStyle(
                    color=bs.color,
                    size=bs.size,
                    val=bs.val
                )

    col_letter = chr(ord('A') + col_idx)
    cell_ref = f"{col_letter}{row_idx + 1}"
    for ovr in style.cell_overrides:
        if ovr.cell_ref == cell_ref:
            for side, bs in ovr.borders.items():
                for s in expand_border_side(side):
                    borders[s] = BorderStyle(
                        color=bs.color,
                        size=bs.size,
                        val=bs.val
                    )
            break

    return borders
