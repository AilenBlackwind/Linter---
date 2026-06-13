import re
from linter.config import Config

_BREAK_INLINE_RE = re.compile(r'‹!br[pc]›', re.IGNORECASE)
_BREAK_HTML_RE = re.compile(r'<!--break:(page|column)-->')
_CUSTOM_COLOR_RE = re.compile(r'~=\{([^}]+)\}(.*?)=\s*~')


def _replace_break(m):
    return '<!--break:page-->' if m.group(0).lower() == '‹!brp›' else '<!--break:column-->'


def preprocess_markdown(md_text: str, config: Config) -> str:
    lines = md_text.split('\n')
    n = len(lines)

    tag_to_key = {}
    for k, ib in config.infobox_styles.items():
        tag_raw = ib.opening_tag
        if tag_raw.startswith(':::'):
            tag_val = tag_raw[3:].strip()
            if tag_val:
                tag_to_key[tag_val.lower()] = (k, 'multi')
    for k, sp in config.single_paragraph_styles.items():
        tag_raw = sp.get('tag', f':::{k}')
        if tag_raw.startswith(':::'):
            tag_val = tag_raw[3:].strip()
            if tag_val:
                tag_to_key.setdefault(tag_val.lower(), (k, 'single'))

    infobox_keys_lower = {k.lower(): k for k in config.infobox_styles.keys()}
    single_keys_lower = {k.lower(): k for k in config.single_paragraph_styles.keys()}
    all_keys_lower = {}
    all_keys_lower.update(infobox_keys_lower)
    all_keys_lower.update(single_keys_lower)

    sorted_key_items = sorted(all_keys_lower.items(), key=lambda x: len(x[0]), reverse=True)
    sorted_tag_items = sorted(tag_to_key.items(), key=lambda x: len(x[0]), reverse=True)

    def get_key_if_tag_line(line: str):
        stripped = line.strip()
        stripped_lower = stripped.lower()

        if stripped_lower in (':::', '::::'):
            return (None, None, None)

        if not stripped_lower.startswith(':::'):
            return (None, None, None)

        after_colons = stripped[3:]
        after_colons_stripped = after_colons.strip()
        after_colons_stripped_lower = after_colons_stripped.lower()

        for tag_lower, (key, style_type) in sorted_tag_items:
            if after_colons_stripped_lower == tag_lower:
                return (key, style_type == 'single', '')
            if after_colons_stripped_lower.startswith(tag_lower + ' '):
                text_after = after_colons_stripped[len(tag_lower):].strip()
                return (key, True, text_after)

        for key_lower, key_original in sorted_key_items:
            if after_colons_stripped_lower.startswith(key_lower):
                remaining = after_colons_stripped[len(key_lower):]
                if not remaining or remaining.startswith(' '):
                    text_after = remaining.strip()
                    is_single_line = bool(text_after)
                    return (key_original, is_single_line, text_after)

        return (None, None, None)

    events = []

    open_stack = []
    keep_stack = []

    line_style_tags = set()
    for key in config.line_styles:
        line_style_tags.add(key.lower())
    LINE_STYLE_RE = re.compile(r'^\s*#st/(\S+?)([›→⋙❭]*)\s*$', re.IGNORECASE)
    STANDALONE_ARROW_RE = re.compile(r'^([‹❬›❭]+)\s*$')

    custom_colors = config.custom_colors

    def _replace_custom_color(m):
        tag = m.group(1)
        text = m.group(2)
        hex_color = custom_colors.get(tag.lower(), tag.upper())
        hex_color = hex_color.lstrip('#')
        if not re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
            return m.group(0)
        return f'<font color="{hex_color}">{text}</font>'

    for i in range(n):
        line = lines[i]
        line = _CUSTOM_COLOR_RE.sub(_replace_custom_color, line)
        lines[i] = line
        stripped = line.strip()
        stripped_lower = stripped.lower()

        if stripped == '{{{':
            keep_stack.append(i)
            continue
        if stripped == '}}}':
            if keep_stack:
                open_idx = keep_stack.pop()
                events.append((open_idx, 'keep_open', ''))
                events.append((i, 'keep_close', ''))
            continue

        if stripped_lower in (':::', '::::'):
            if open_stack:
                open_idx, open_key = open_stack.pop()
                events.append((open_idx, 'open', open_key))
                events.append((i, 'close', open_key))
            continue

        key, is_single, text_after = get_key_if_tag_line(line)
        if key is not None:
            if is_single:
                if (text_after == "" and
                    key.lower() in single_keys_lower and
                    key.lower() not in infobox_keys_lower):
                    events.append((i, 'open_single_tag', key))
                else:
                    events.append((i, 'single_tag', (key, text_after)))
            else:
                open_stack.append((i, key))

    for open_idx, open_key in open_stack:
        events.append((open_idx, 'open_single', open_key))

    events.sort(key=lambda x: x[0])

    new_lines = []
    events_by_index = {}
    for idx, evt_type, data in events:
        if idx not in events_by_index:
            events_by_index[idx] = []
        events_by_index[idx].append((evt_type, data))

    in_multi_block = False
    pending_single_open = None
    pending_single_tag = None

    for i in range(n):
        line = lines[i]

        if i in events_by_index:
            for evt_type, data in events_by_index[i]:
                if evt_type == 'open':
                    new_lines.append(f"<!--block_start:{data}-->")
                    in_multi_block = True
                elif evt_type == 'close':
                    new_lines.append(f"<!--block_end:{data}-->")
                    in_multi_block = False
                elif evt_type == 'single_tag':
                    key, text = data
                    new_lines.append(f"<!--single_tag:{key}:{text}-->")
                elif evt_type == 'open_single':
                    pending_single_open = data
                elif evt_type == 'open_single_tag':
                    pending_single_tag = data
                elif evt_type == 'keep_open':
                    new_lines.append('<!--keep_together_start-->')
                elif evt_type == 'keep_close':
                    new_lines.append('<!--keep_together_end-->')

        stripped = line.strip()
        stripped_lower = stripped.lower()
        is_only_tag_or_close = False

        if stripped in ('{{{', '}}}'):
            is_only_tag_or_close = True
        elif stripped_lower in (':::', '::::'):
            is_only_tag_or_close = True
        else:
            key, is_single, _ = get_key_if_tag_line(line)
            if key is not None:
                is_only_tag_or_close = True

        if is_only_tag_or_close:
            continue

        m = LINE_STYLE_RE.match(line)
        if m and m.group(1).lower() in line_style_tags:
            arrows = m.group(2)
            if arrows:
                new_lines.append(f"<!--line_style:{m.group(1)}|arrows:{arrows}-->")
            else:
                new_lines.append(f"<!--line_style:{m.group(1)}-->")
            continue

        m = STANDALONE_ARROW_RE.match(line)
        if m:
            new_lines.append(f"<!--standalone_arrows:{m.group(1)}-->")
            continue

        line = _BREAK_INLINE_RE.sub(_replace_break, line)

        # If break marker is at line start, mistune treats it as block HTML
        # and eats following text. Split marker onto its own line.
        break_extracted = False
        while True:
            m = _BREAK_HTML_RE.match(line)
            if m and m.start() == 0:
                new_lines.append(line[:m.end()])
                line = line[m.end():]
                break_extracted = True
            else:
                break

        if not line and break_extracted:
            continue

        if pending_single_tag is not None:
            if stripped:
                new_lines.append(f"<!--single_tag:{pending_single_tag}:{line}-->")
                pending_single_tag = None
            else:
                new_lines.append(line)
        elif pending_single_open is not None:
            if stripped:
                new_lines.append(f"<!--block_start:{pending_single_open}-->")
                new_lines.append(line)
                new_lines.append(f"<!--block_end:{pending_single_open}-->")
                pending_single_open = None
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    return '\n'.join(new_lines)
