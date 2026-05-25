from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from .main_window import StyleEditorMainWindow
from .style_data_manager import StyleDataManager


def main():
    app = QApplication(sys.argv)

    root = Path(__file__).resolve().parent.parent.parent

    template_path = root / "workspace" / "templates" / "RpRef1.docx"
    config_path = root / "configs" / "app_config.json"
    if config_path.exists():
        try:
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tp = data.get("paths", {}).get("template", "")
            if tp:
                user_template = root / tp
                if user_template.exists():
                    template_path = user_template
        except Exception:
            pass
    if not template_path.exists():
        template_path = None

    data_manager = StyleDataManager(
        styles_path=root / "configs" / "table_styles.json",
        mappings_path=root / "configs" / "table_mappings.json",
        template_path=template_path,
        spacing_path=root / "configs" / "spacing.json",
        general_styles_path=root / "configs" / "styles.json",
        app_config_path=root / "configs" / "app_config.json",
    )

    window = StyleEditorMainWindow(data_manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
