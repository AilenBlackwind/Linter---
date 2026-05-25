# Style Editor — Module Architecture

Keep this in mind when adding or modifying code:

## Key Rule
**DO NOT add new functionality to `main_window.py`.** It should only contain window layout and signal wiring between widgets. New features go into existing or new modules.

## Where to put code
| What | Where |
|------|-------|
| Window coordination, signals | `main_window.py` — keep lean |
| Form-based control panels | `panels/*.py` — e.g. `PropertiesPanel`, `GeneralSettingsWidget` |
| Custom-drawn / visual widgets | `widgets/*.py` — e.g. `VisualGridWidget`, `JsonPreviewWidget` |
| Data access & I/O | `style_data_manager.py` — `StyleDataManager` |
| Pure data transformations | `style_data_manager.py` (static methods) |
| Utility functions | `style_utils.py`, `mapping_utils.py` |

## Patterns
- All panels and widgets receive `StyleDataManager` in constructor, never access files directly.
- Business logic (format conversion, validation) lives in `StyleDataManager` or utility modules, not in GUI classes.
- A widget/panel should be testable in isolation — pass dependencies explicitly.
