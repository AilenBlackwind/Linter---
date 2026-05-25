from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt

try:
    from linter.converter.tables.advanced import AdvancedTableRenderer, TableStyle
    HAS_ADVANCED_RENDERER = True
except ImportError:
    HAS_ADVANCED_RENDERER = False


def get_or_create_child(parent, tag_name):
    child = parent.find(qn(tag_name))
    if child is None:
        child = OxmlElement(tag_name)
        parent.append(child)
    return child


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = get_or_create_child(tc_pr, 'w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    if fill:
        shd.set(qn('w:fill'), fill)
    else:
        shd.set(qn('w:fill'), 'FFFFFF')


def set_cell_borders(cell, color="666666", size=8):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = get_or_create_child(tc_pr, 'w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        set_border_edge(tc_borders, edge, color=color, size=size)


def set_border_edge(tc_borders, edge, color="auto", size=0, val='single'):
    edge_el = tc_borders.find(qn(f'w:{edge}'))
    if edge_el is None:
        edge_el = OxmlElement(f'w:{edge}')
        tc_borders.append(edge_el)
    if val != 'nil' and size <= 0:
        val = 'nil'
    edge_el.set(qn('w:val'), val)
    if val != 'nil':
        edge_el.set(qn('w:sz'), str(size))
        edge_el.set(qn('w:color'), color)


def clear_cell_borders(cell):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = get_or_create_child(tc_pr, 'w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        set_border_edge(tc_borders, edge, val='nil')


def set_cell_margins(cell, top=70, start=90, bottom=70, end=90):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = get_or_create_child(tc_pr, 'w:tcMar')
    for side, value in {'top': top, 'start': start, 'bottom': bottom, 'end': end}.items():
        side_el = tc_mar.find(qn(f'w:{side}'))
        if side_el is None:
            side_el = OxmlElement(f'w:{side}')
            tc_mar.append(side_el)
        side_el.set(qn('w:w'), str(value))
        side_el.set(qn('w:type'), 'dxa')


def apply_text_wrap(table, text_wrap="around", left_from_text=0, right_from_text=0):
    tblPr = table._tbl.tblPr
    existing = tblPr.find(qn('w:tblpPr'))
    if text_wrap == "inline":
        if existing is not None:
            tblPr.remove(existing)
        return
    if existing is not None:
        tblPr.remove(existing)
    tblpPr = OxmlElement('w:tblpPr')
    tblpPr.set(qn('w:leftFromText'), str(left_from_text))
    tblpPr.set(qn('w:rightFromText'), str(right_from_text))
    tblpPr.set(qn('w:vertAnchor'), 'text')
    tblpPr.set(qn('w:horzAnchor'), 'margin')
    tblPr.insert(0, tblpPr)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = tr_pr.find(qn('w:tblHeader'))
    if tbl_header is None:
        tbl_header = OxmlElement('w:tblHeader')
        tr_pr.append(tbl_header)
    tbl_header.set(qn('w:val'), '1')


def set_row_cant_split(row):
    tr_pr = get_or_create_child(row._tr, 'w:trPr')
    cant_split = tr_pr.find(qn('w:cantSplit'))
    if cant_split is None:
        cant_split = OxmlElement('w:cantSplit')
        tr_pr.append(cant_split)


def set_paragraph_keep(paragraph, keep_with_next=False):
    p_pr = get_or_create_child(paragraph._element, 'w:pPr')

    keep_lines = p_pr.find(qn('w:keepLines'))
    if keep_lines is None:
        keep_lines = OxmlElement('w:keepLines')
        p_pr.append(keep_lines)
    keep_lines.set(qn('w:val'), '1')

    keep_next = p_pr.find(qn('w:keepNext'))
    if keep_with_next:
        if keep_next is None:
            keep_next = OxmlElement('w:keepNext')
            p_pr.append(keep_next)
        keep_next.set(qn('w:val'), '1')
    elif keep_next is not None:
        p_pr.remove(keep_next)


def format_cell_paragraph(paragraph, style_name=None, bold=False):
    try:
        if style_name:
            paragraph.style = style_name
    except:
        pass
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)
    for run in paragraph.runs:
        if bold:
            run.bold = True


def set_table_spacing_after(table, points=10):
    tbl_pr = get_or_create_child(table._tbl, 'w:tblPr')
    spacing = get_or_create_child(tbl_pr, 'w:tblSpacing')
    spacing.set(qn('w:after'), str(int(points * 20)))


def keep_table_together(table):
    last_row_index = len(table.rows) - 1
    for row_idx, row in enumerate(table.rows):
        set_row_cant_split(row)
        keep_with_next = row_idx < last_row_index
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                set_paragraph_keep(paragraph, keep_with_next=keep_with_next)


def apply_zebra_preset(table, preset):
    row_types = preset.get('row_types', {})
    default_borders = preset.get('default_borders', {})
    cell_overrides = preset.get('cell_overrides', {})

    hdr = row_types.get('header', {})
    if not isinstance(hdr, dict):
        hdr = {}
    hdr_shading = hdr.get('shading') or preset.get('header_fill')

    odd_row = row_types.get('odd', {})
    if not isinstance(odd_row, dict):
        odd_row = {}
    row_shading = odd_row.get('shading') or preset.get('row_fill')

    hdr_bottom_color = preset.get('header_bottom_color')
    hdr_bottom_size = preset.get('header_bottom_size')
    hdr_borders = hdr.get('borders', {})
    if isinstance(hdr_borders, dict) and 'bottom' in hdr_borders:
        hb = hdr_borders['bottom']
        if isinstance(hb, dict):
            hdr_bottom_color = hb.get('color') or hdr_bottom_color
            hdr_bottom_size = hb.get('size') or hdr_bottom_size

    inner_v_size = preset.get('inner_v_size', 0)
    inner_v_color = preset.get('inner_v_color', 'E7E7F7')
    for side_key in ('right', 'left', 'vertical', 'all'):
        bs = default_borders.get(side_key, {})
        if isinstance(bs, dict) and bs.get('size', 0) > 0:
            inner_v_size = bs['size']
            inner_v_color = bs.get('color', inner_v_color)
            break

    for row_idx, row in enumerate(table.rows):
        is_header = row_idx == 0
        if is_header:
            set_repeat_table_header(row)
        for cell_idx, cell in enumerate(row.cells):
            clear_cell_borders(cell)
            set_cell_margins(cell, top=90, start=110, bottom=90, end=110)

            if is_header:
                if hdr_shading:
                    set_cell_shading(cell, hdr_shading)
                tc_borders = get_or_create_child(cell._tc.get_or_add_tcPr(), 'w:tcBorders')
                if hdr_bottom_color and hdr_bottom_size:
                    set_border_edge(tc_borders, 'bottom',
                                     color=hdr_bottom_color,
                                     size=hdr_bottom_size)
            elif row_idx % 2 == 0:
                if row_shading:
                    set_cell_shading(cell, row_shading)
            else:
                set_cell_shading(cell, 'FFFFFF')

            if cell_idx < len(row.cells) - 1 and inner_v_size > 0:
                tc_borders = get_or_create_child(cell._tc.get_or_add_tcPr(), 'w:tcBorders')
                set_border_edge(tc_borders, 'right', color=inner_v_color, size=inner_v_size)

            col_letter = chr(ord('A') + cell_idx)
            cell_ref = f"{col_letter}{row_idx + 1}"
            override = cell_overrides.get(cell_ref) if isinstance(cell_overrides, dict) else None
            if override:
                if override.get('shading'):
                    set_cell_shading(cell, override['shading'])
                if override.get('borders'):
                    tc_borders = get_or_create_child(cell._tc.get_or_add_tcPr(), 'w:tcBorders')
                    for side, bs in override['borders'].items():
                        if isinstance(bs, dict):
                            set_border_edge(tc_borders, side,
                                            color=bs.get('color', 'auto'),
                                            size=bs.get('size', 0),
                                            val=bs.get('val', 'single'))


def apply_table_preset(table, preset_name, presets):
    preset = presets.get(preset_name, presets.get('plain', {}))

    if preset.get('renderer') == 'advanced' and HAS_ADVANCED_RENDERER:
        try:
            renderer = AdvancedTableRenderer.from_dict(preset, preset_name)
            renderer.apply_to_table(table)
            return
        except Exception as e:
            print(f"[!] Ошибка применения advanced renderer: {e}")

    if preset.get('renderer') == 'zebra':
        apply_zebra_preset(table, preset)
        apply_text_wrap(table, preset.get('text_wrap', 'around'),
                        preset.get('left_from_text', 0), preset.get('right_from_text', 0))
        return

    for row_idx, row in enumerate(table.rows):
        is_header = row_idx == 0
        if is_header:
            set_repeat_table_header(row)
        for cell in row.cells:
            set_cell_borders(cell, preset.get('border_color', '666666'), preset.get('border_size', 8))
            set_cell_margins(cell)
            if is_header:
                if 'header_fill' in preset and preset['header_fill']:
                    set_cell_shading(cell, preset['header_fill'])
            elif preset.get('band_fill') and row_idx % 2 == 1:
                set_cell_shading(cell, preset['band_fill'])
    apply_text_wrap(table, preset.get('text_wrap', 'around'),
                    preset.get('left_from_text', 0), preset.get('right_from_text', 0))


def get_section_column_width(section):
    sect_pr = section._sectPr
    cols = sect_pr.find(qn('w:cols'))

    page_width = section.page_width
    left_margin = section.left_margin or 0
    right_margin = section.right_margin or 0
    gutter = section.gutter or 0

    if page_width is None:
        page_width = 12240

    usable_width = page_width - left_margin - right_margin - gutter

    if cols is None:
        return usable_width

    num = int(cols.get(qn('w:num'), '1'))
    if num <= 1:
        return usable_width

    if cols.get(qn('w:equalWidth'), '1') in ('1', 'true'):
        space_twips = int(cols.get(qn('w:space'), '0'))
        space_emu = space_twips * 635
        return int((usable_width - space_emu * (num - 1)) / num)

    col_nodes = cols.findall(qn('w:col'))
    if col_nodes:
        first_width_twips = int(col_nodes[0].get(qn('w:w'), '0'))
        if first_width_twips > 0:
            return first_width_twips * 635

    return usable_width


def set_table_width(table, width_emu):
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn('w:tblW'))
    if tbl_w is None:
        tbl_w = OxmlElement('w:tblW')
        tbl_pr.append(tbl_w)
    tbl_w.set(qn('w:type'), 'dxa')
    tbl_w.set(qn('w:w'), str(int(width_emu / 635)))


def set_table_grid_widths(table, widths_emu):
    tbl_grid = table._tbl.tblGrid
    existing_cols = list(tbl_grid)
    for col in existing_cols:
        tbl_grid.remove(col)
    for width in widths_emu:
        grid_col = OxmlElement('w:gridCol')
        grid_col.set(qn('w:w'), str(int(width / 635)))
        tbl_grid.append(grid_col)


def normalize_width_weights(widths, cols_count):
    if not isinstance(widths, list) or len(widths) < 1:
        return None
    if len(widths) < cols_count:
        avg = sum(widths) / len(widths)
        widths = list(widths) + [avg] * (cols_count - len(widths))
    elif len(widths) > cols_count:
        widths = widths[:cols_count]
    cleaned = []
    for value in widths:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if number < 0:
            return None
        cleaned.append(number)
    total = sum(cleaned)
    if total <= 0:
        return None
    return [value / total for value in cleaned]


def estimate_column_weights(header_cells_nodes, body_rows_nodes, cols_count, get_text_recursive_func):
    if cols_count <= 0:
        return []

    narrow_titles = {
        'сложность', 'цена', 'кд', 'кс', 'урон', 'броня', 'hp', 'xp', 'ур', 'lvl', 'dc', 'ac'
    }

    scores = [0.0] * cols_count
    for idx, cell_node in enumerate(header_cells_nodes):
        text = get_text_recursive_func(cell_node).strip()
        scores[idx] += max(4, min(len(text), 30))

    for row_node in body_rows_nodes:
        row_cells_nodes = row_node.get('children', [])
        for idx in range(cols_count):
            text = get_text_recursive_func(row_cells_nodes[idx]) if idx < len(row_cells_nodes) else ''
            text_len = len(text)
            scores[idx] += max(2, min(text_len, 80) * 0.75)

    header_titles = [get_text_recursive_func(node).strip().lower() for node in header_cells_nodes]
    if cols_count == 2:
        left_title = header_titles[0] if header_titles else ''
        if left_title in narrow_titles:
            return [0.28, 0.72]

        left_texts = []
        right_texts = []
        for row_node in body_rows_nodes:
            row_cells_nodes = row_node.get('children', [])
            if len(row_cells_nodes) > 0:
                left_texts.append(len(get_text_recursive_func(row_cells_nodes[0])))
            if len(row_cells_nodes) > 1:
                right_texts.append(len(get_text_recursive_func(row_cells_nodes[1])))
        left_avg = (sum(left_texts) / len(left_texts)) if left_texts else 0
        right_avg = (sum(right_texts) / len(right_texts)) if right_texts else 0
        if left_avg and right_avg and left_avg < right_avg * 0.45:
            return [0.3, 0.7]

    min_share = 0.16 if cols_count == 2 else 0.12
    total = sum(scores) or cols_count
    weights = [score / total for score in scores]
    weights = [max(min_share, weight) for weight in weights]
    normalized_total = sum(weights)
    return [weight / normalized_total for weight in weights]


def fit_table_to_page(table, section, cols_count, width_weights=None, fit_to_page=True, row_heights=None, table_width=None):
    if cols_count <= 0:
        return

    if fit_to_page:
        total_width_emu = get_section_column_width(section)
    elif table_width is not None and table_width > 0:
        total_width_emu = table_width
    elif width_weights and isinstance(width_weights, list) and len(width_weights) > 0:
        total_width_emu = get_section_column_width(section)
    else:
        table.autofit = True
        _apply_row_heights(table, row_heights)
        return

    weights = normalize_width_weights(width_weights, cols_count)
    if weights is None:
        weights = [1 / cols_count] * cols_count

    widths_emu = [int(total_width_emu * weight) for weight in weights]

    overflow = sum(widths_emu) - total_width_emu
    if overflow > 0:
        sorted_idx = sorted(range(cols_count), key=lambda i: widths_emu[i], reverse=True)
        for idx in sorted_idx:
            reduction = min(overflow, max(widths_emu[idx] - 100, 0))
            widths_emu[idx] -= reduction
            overflow -= reduction
            if overflow <= 0:
                break

    diff = total_width_emu - sum(widths_emu)
    if widths_emu:
        widths_emu[-1] += diff

    table.autofit = False
    set_table_width(table, total_width_emu)
    set_table_grid_widths(table, widths_emu)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if idx < len(widths_emu):
                cell.width = widths_emu[idx]

    _apply_row_heights(table, row_heights)


def _apply_row_heights(table, row_heights):
    if row_heights and len(row_heights) == len(table.rows):
        for idx, row in enumerate(table.rows):
            if idx < len(row_heights) and row_heights[idx] > 0:
                row.height = row_heights[idx]
