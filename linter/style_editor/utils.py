from __future__ import annotations

from typing import Optional

from PyQt5.QtGui import QColor


def hex_to_qcolor(hex_str: Optional[str]) -> QColor:
    if not hex_str:
        return QColor(255, 255, 255)
    hex_str = hex_str.lstrip('#')
    return QColor(
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16)
    )


def qcolor_to_hex(color: QColor) -> str:
    return f"{color.red():02X}{color.green():02X}{color.blue():02X}"
