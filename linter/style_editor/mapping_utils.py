from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def find_mapping_for_style(mappings: Dict[str, Any], style_name: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    for tag, mapping in mappings.items():
        if mapping.get("preset") == style_name:
            return tag, mapping
    return "", None
