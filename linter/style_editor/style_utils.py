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

    row_key = _get_row_type_key(row_idx, row_count)
    if row_key and row_key in style.row_types:
        s = style.row_types[row_key]
        if s.shading:
            shading = s.shading

    col_key = _get_col_type_key(col_idx, col_count)
    if col_key and col_key in style.row_types:
        s = style.row_types[col_key]
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


def _get_row_type_key(row_idx: int, row_count: int) -> Optional[str]:
    if row_idx == 0:
        return 'header'
    elif row_idx == row_count - 1:
        return 'last_row'
    elif row_idx % 2 == 0:
        return 'odd'
    else:
        return 'even'


def _get_col_type_key(col_idx: int, col_count: int) -> Optional[str]:
    if col_idx == 0:
        return 'first_column'
    elif col_idx == col_count - 1:
        return 'last_column'
    return None


def get_cell_bold(style: Optional[TableStyle], row_idx: int, col_idx: int, row_count: int, col_count: int) -> Optional[bool]:
    if not style:
        return None
    bold: Optional[bool] = None

    row_key = _get_row_type_key(row_idx, row_count)
    if row_key and row_key in style.row_types:
        rt = style.row_types[row_key]
        if rt.bold is not None:
            bold = rt.bold

    col_key = _get_col_type_key(col_idx, col_count)
    if col_key and col_key in style.row_types:
        ct = style.row_types[col_key]
        if ct.bold is not None:
            bold = ct.bold

    col_letter = chr(ord('A') + col_idx)
    cell_ref = f"{col_letter}{row_idx + 1}"
    for ovr in style.cell_overrides:
        if ovr.cell_ref == cell_ref and ovr.bold is not None:
            bold = ovr.bold
            break

    return bold


def get_cell_italic(style: Optional[TableStyle], row_idx: int, col_idx: int, row_count: int, col_count: int) -> Optional[bool]:
    if not style:
        return None
    italic: Optional[bool] = None

    row_key = _get_row_type_key(row_idx, row_count)
    if row_key and row_key in style.row_types:
        rt = style.row_types[row_key]
        if rt.italic is not None:
            italic = rt.italic

    col_key = _get_col_type_key(col_idx, col_count)
    if col_key and col_key in style.row_types:
        ct = style.row_types[col_key]
        if ct.italic is not None:
            italic = ct.italic

    col_letter = chr(ord('A') + col_idx)
    cell_ref = f"{col_letter}{row_idx + 1}"
    for ovr in style.cell_overrides:
        if ovr.cell_ref == cell_ref and ovr.italic is not None:
            italic = ovr.italic
            break

    return italic


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

    row_key = _get_row_type_key(row_idx, row_count)
    if row_key and row_key in style.row_types:
        row_style = style.row_types[row_key]
        for side, bs in row_style.borders.items():
            for s in expand_border_side(side):
                borders[s] = BorderStyle(
                    color=bs.color,
                    size=bs.size,
                    val=bs.val
                )

    col_key = _get_col_type_key(col_idx, col_count)
    if col_key and col_key in style.row_types:
        col_style = style.row_types[col_key]
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
