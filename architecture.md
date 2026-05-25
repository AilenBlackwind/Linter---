# Архитектура проекта Linter+++

Конвертер Markdown → DOCX для автоматической вёрстки документов с кастомными стилями.

---

## Текущее состояние

**Версия:** Альфа 11
**Состояние:** Основной функционал работает, рефакторинг архитектуры редактора

**Готово:**
- ✅ Markdown → DOCX конвертация
- ✅ Вложенное форматирование (`***жирный курсив***`)
- ✅ Инфобоксы через `:::` теги
- ✅ Система пресетов таблиц (plain, zebra, fancy)
- ✅ Advanced renderer для таблиц (с каскадными стилями)
- ✅ Цветовые правила по содержимому ячеек (equals, contains, starts_with, ends_with, matches_regex, has_text)
- ✅ Автоматическое открытие результата после конвертации (настраивается в `app_config.json`)
- ✅ PyQt5 визуальный редактор стилей таблиц
- ✅ 6x6 сетка в редакторе (повторяется для больших таблиц)
- ✅ Выделение нескольких ячеек (Shift+клик, Ctrl+клик)
- ✅ Сохранение стилей в `configs/table_styles.json`
- ✅ Сохранение маппингов тегов в `configs/table_mappings.json`
- ✅ Архитектура src/layout (`linter/` — единый пакет с кодом)
- ✅ Переименование стилей двойным кликом в списке
- ✅ Кастомные размеры колонок (ширина/веса) и строк (высота в twip)
- ✅ Опция принудительного вписывания таблицы в страницу с умным масштабированием
- ✅ Триггер `has_text` — цвет по колонке, если ячейка не пуста (для element_colors)
- ✅ Поле тега в Markdown (`<!tag>`) редактируется из визуального редактора
- ✅ Ширина колонок в редакторе указывается в процентах
- ✅ Единый конфиг `configs/spacing.json` для всех отступов (before_heading, after_heading, after_list, after_table, table_before_heading)
- ✅ Отступ после таблицы через `spaceBefore` на следующем абзаце (а не пустой абзац)
- ✅ Раздельный отступ для заголовков после таблиц (`table_before_heading`)
- ✅ Поля «Стиль заголовка» и «Стиль текста» в редакторе — выбор из параграф-стилей DOCX-шаблона
- ✅ Исправлен отступ перед заголовком после инфобоксов (single_tag, block_start/block_end, списки, таблицы)
- ✅ Изолированный виджет «Стили абзацев» (`panels/paragraph_styles.py`) вместо вкладки в MainWindow
- ✅ `StyleDataManager` — единый слой доступа к данным для всех панелей редактора
- ✅ Глобальный `QTabWidget` с двумя вкладками: «Общие настройки» и «Редактор таблиц»
- ✅ Вкладка «Общие настройки»: список стилей абзацев + под-табы [АБЗАЦ] [ОБЩЕЕ] [JSON] с авто-сохранением
- ✅ Вкладка «Редактор таблиц»: под-таб «Структура и свойства» (тег, стили абзацев, обтекание, размеры)
- ✅ `PropertiesPanel` сокращена до редактирования ячеек (заливка/шрифт/границы)
- ✅ `TableStructurePanel` — новый виджет для структуры таблицы
- ✅ `VisualGridWidget`: spacing=2 для компактной сетки

**Требует доработки:**
- ⚠️ Нет undo/redo в редакторе
- ⚠️ Нет предварительного просмотра DOCX перед сохранением

---

## Структура проекта

```
F:\Linter+++\
│
├── main.py                          # Обёртка: from linter.cli import run; run()
│
├── run_converter.bat                # Запуск конвертера (двойной клик)
├── run_style_editor.bat             # Запуск редактора стилей (двойной клик)
├── run.ps1                          # PowerShell-скрипт запуска
│
├── requirements.txt                 # Зависимости (python-docx, mistune, PyQt5)
├── architecture.md                  # Этот файл
│
├── configs/                         # Все настройки в одном месте
│   ├── app_config.json              # Пользовательские пути (input, output, template)
│   ├── spacing.json                 # Все отступы (before_heading, after_table, table_before_heading и т.д.)
│   ├── styles.json                  # Стили инфобоксов (legacy, spacing вынесен в spacing.json)
│   ├── table_styles.json            # Пресеты стилей таблиц
│   └── table_mappings.json          # Маппинг тегов <!tag> → пресет
│
├── workspace/                       # Вход/Выход/Шаблоны
│   ├── input/
│   │   └── input.md                 # Входной файл по умолчанию
│   ├── output/
│   │   └── Result.docx              # Выходной файл по умолчанию
│   └── templates/
│       └── RpRef1.docx              # DOCX шаблон со стилями
│
├── linter/                          # ГЛАВНАЯ ПАПКА С КОДОМ
│   ├── __init__.py
│   ├── cli.py                       # Точка входа: функция run() + auto-open результата
│   ├── config.py                    # Загрузка конфигурации (Config, load_configuration)
│   │                                # - open_after_convert (из app_config.json)
│   ├── utils.py                     # ensure_output_dir()
│   │
│   ├── converter/                   # Ядро конвертера
│   │   ├── __init__.py
│   │   ├── markdown_processor.py    # Предобработка Markdown (:::-теги → маркеры)
│   │   ├── docx_builder.py          # Построение DOCX (DocxBuilder)
│   │   │                            # - Читает column_widths/fit_to_page/row_heights из пресета
│   │   │
│   │   └── tables/                  # Вся логика таблиц
│   │       ├── __init__.py
│   │       ├── processor.py         # Применение пресетов, подгонка ширины
│   │       │                        # - apply_table_preset()
│   │       │                        # - apply_zebra_preset()
│   │       │                        # - fit_table_to_page() с умным масштабированием
│   │       │                        # - set_repeat_table_header()
│   │       │
│   │       └── advanced/            # Продвинутая система стилей
│   │           ├── __init__.py
│   │           ├── models.py        # Data classes: TableStyle, ColorRule, BorderStyle...
│   │           │                    # - column_widths, row_heights, fit_to_page
│   │           │                    # - ColorRule.column + trigger "has_text"
│   │           ├── rules_engine.py  # Движок проверки цветовых правил (RulesEngine)
│   │           │                    # - col_idx пробрасывается в matches()
│   │           └── renderer.py      # Рендерер каскадных стилей (AdvancedTableRenderer)
│   │                                # - Передаёт col_idx в apply_rules()
│   │
│   └── style_editor/                # PyQt5 редактор стилей таблиц
│       ├── __init__.py
│       ├── __main__.py              # Точка входа для python -m
│       ├── main.py                  # Функция main() — создаёт StyleDataManager + StyleEditorMainWindow
│       ├── main_window.py           # StyleEditorMainWindow (оркестратор)
│       │                            # - Глобальный QTabWidget: [Общие настройки] [Редактор таблиц]
│       │                            # - Вкладка "Общие настройки":
│       │                            #     Левая панель: список стилей абзацев (+/-)
│       │                            #     Под-табы: [АБЗАЦ] [ОБЩЕЕ] [JSON]
│       │                            #     - АБЗАЦ: тег в MD, тип (многостр/одностр), стиль Word
│       │                            #     - ОБЩЕЕ: отступы (spacing.json)
│       │                            #     - JSON: превью styles.json
│       │                            #     Авто-сохранение в StyleDataManager при любом изменении
│       │                            # - Вкладка "Редактор таблиц":
│       │                            #     Левая панель: StyleListPanel (список табличных стилей)
│       │                            #     Под-табы: [Визуальный редактор] [Цветовые правила]
│       │                            #              [Структура и свойства] [JSON предпросмотр]
│       │                            #     Правая панель: PropertiesPanel (заливка/шрифт/границы)
│       ├── style_data_manager.py    # StyleDataManager — единый слой доступа к данным
│       │                            # - load/save_table_styles(), load/save_mappings()
│       │                            # - load_template_styles() — парсинг DOCX-шаблона
│       │                            # - load/save_spacing(), load/save_general_styles()
│       │                            # - from_root() — фабрика от корня проекта
│       ├── utils.py                 # Конвертация цветов (hex <-> QColor)
│       ├── style_utils.py           # Чистые функции: expand_border_side, get_cell_shading, get_cell_borders
│       ├── mapping_utils.py         # find_mapping_for_style — поиск тега в маппингах
│       │
│       ├── widgets/                 # Базовые виджеты
│       │   ├── __init__.py
│       │   ├── color_picker.py      # ColorPickerWidget
│       │   ├── grid_cell.py         # GridCellWidget + CellBorderStyle
│       │   ├── visual_grid.py       # VisualGridWidget — 6×6 сетка + выделения
│       │   │                        # - spacing=2 в QGridLayout для компактности
│       │   │                        # - Управление selection (single, shift, ctrl)
│       │   │                        # - update_visuals(style) — отрисовка заливок/границ
│       │   │                        # - Сигнал selection_changed
│       │   └── style_list_panel.py  # StyleListPanel — список стилей + кнопки
│       │                            # - Кнопки [+ Новый] / [- Удалить] / [> Сохранить]
│       │                            # - Сигналы: style_selected, style_created,
│       │                            #   style_deleted, style_renamed, save_requested
│       │
│       └── panels/                  # Панели редактора
│           ├── __init__.py
│           ├── properties.py        # PropertiesPanel — редактирование ячеек
│           │                        # - Цель редактирования (table_defaults/header/odd/even/…)
│           │                        # - Заливка, шрифт (жирный/курсив/цвет), границы
│           ├── table_structure.py   # TableStructurePanel — структура и свойства таблицы
│           │                        # - Тег в Markdown, стили абзацев (заголовок/текст)
│           │                        # - Обтекание текстом, размеры таблицы
│           │                        #   (ширина колонок в %, высота строк, fit_to_page)
│           ├── color_rules.py       # ColorRulesWidget
│           │                        # - Триггер has_text + выбор колонки A–F
│           └── paragraph_styles.py  # ParagraphStylesPanel — виджет «Стили абзацев»
│                                    # - Отступы (spacing.json)
│                                    # - Таблица стилей абзацев (styles.json)
│                                    # - Использует StyleDataManager для чтения/записи
│
└── test_scripts/                    # (папка для заметок нейросети)
```

---

## Каскадные стили таблиц (Advanced Renderer)

Приоритет стилей (от низшего к высшему):

```
1. table_defaults (базовые настройки)
         ↓
2. row_types по типу строки
   - header (первая строка)
   - odd / even (нечётные/чётные)
   - last_row (последняя строка)
         ↓
3. row_types по типу колонки
   - first_column (первая колонка)
   - last_column (последняя колонка)
         ↓
4. cell_overrides (конкретные ячейки A1, B3 и т.д.)
         ↓
5. color_rules (по содержимому/позиции ячейки)
```

**Приоритет цветовых правил:**
- Больше `priority` → выше приоритет
- При равном приоритете: правило, которое появилось раньше в списке

**Ширина колонок и высота строк:**
- `column_widths: List[float]` — веса колонок (нормализуются в пропорции)
- `row_heights: List[int]` — высоты строк в twip (None = авто)
- `fit_to_page: bool` — принудительное вписывание в ширину страницы
  - Если сумма весов превышает ширину — обрезка от самых широких колонок к узким
  - Остаток отдаётся последней колонке
  - При `false` — raw-ширины используются как есть (таблица может вылезти за край)

---

## Формат advanced стиля

```json
{
  "my_style": {
    "renderer": "advanced",
    "layout": "auto",
    "cell_margins": {
      "top": 90,
      "start": 110,
      "bottom": 90,
      "end": 110
    },
    "default_borders": {
      "all": {
        "color": "666666",
        "size": 8,
        "val": "single"
      }
    },
    "default_shading": "D9D9D9",
    "fit_to_page": true,
    "column_widths": [2.0, 1.5, 1.0, 1.0, 0.5, 0.5],
    "row_heights": null,
    "row_types": {},
    "cell_overrides": {},
    "color_rules": [
      {
        "name": "B - Синий",
        "trigger": "has_text",
        "column": "B",
        "value": "",
        "case_sensitive": false,
        "shading": "4E84E2",
        "font_color": "FFFFFF",
        "bold": true,
        "priority": 10
      }
    ]
  }
}
```

**Типы триггеров для color_rules:**
- `equals` — точное совпадение
- `contains` — содержит подстроку
- `starts_with` — начинается с
- `ends_with` — заканчивается на
- `matches_regex` — соответствует регулярному выражению
- `has_text` — ячейка не пуста (с опциональным `column`, например `"column": "B"`)
  - Если `column` указан: срабатывает только для ячеек в этой колонке
  - Если `column` не указан: срабатывает для любой непустой ячейки

**Типы границ:**
- `single` — сплошная
- `double` — двойная
- `dashed` — пунктирная
- `dotted` — точечная
- `nil` — нет границы

---

## Как работает конвертация

```
input.md (Markdown с тегами)
     ↓
preprocess_markdown()  ← linter/converter/markdown_processor.py
     ↓
Обработанный Markdown с маркерами:
<!--block_start:info-->
Текст инфобокса
<!--block_end:info-->
     ↓
DocxBuilder.build()  ← linter/converter/docx_builder.py
  - Парсит в AST через mistune (с плагином table)
  - Обходит AST узлы
  - Применяет стили из Config
  - Для таблиц:
    → Читает тег <!zebra>, <!advanced>, и т.д.
    → apply_table_preset() из linter/converter/tables/processor.py
    → Если renderer: advanced → AdvancedTableRenderer
    → fit_table_to_page() с column_widths, fit_to_page, row_heights из пресета
  - Генерирует DOCX через python-docx
     ↓
output.docx (готовый документ)
     ↓
(опционально) os.startfile() — авто-открытие, если open_after_convert: true
```

---

## Синтаксис тегов

### Инфобоксы

```
:::info
Первый абзац

Второй абзац
:::
```
→ Оба абзаца получат стиль из `configs/styles.json`

### Таблицы

```
<!zebra>

| Колонка 1 | Колонка 2 |
| --------- | --------- |
| Значение  | Значение  |
```

Доступные теги (из `configs/table_mappings.json`):
- `<!zebra>` — зебра-стиль
- `<!plain>` — простой стиль
- `<!fancy>` — декоративный стиль
- `<!advanced>` — продвинутый стиль с цветовыми правилами
- `<!elements>` — цвета по колонкам (B=синий, C=зелёный, D=оранжевый, E=фиолетовый)
  *Работает через триггер `has_text`: если ячейка в колонке B не пуста → синяя заливка, и т.д.*

---

## Используемые библиотеки

- **mistune** — парсер Markdown в AST
- **python-docx** — работа с DOCX документами
- **PyQt5** — GUI для редактора стилей

---

## Как запустить

**Конвертер:**
```cmd
run_converter.bat
```
или
```cmd
python main.py
```

**Редактор стилей:**
```cmd
run_style_editor.bat
```
или
```cmd
python -m linter.style_editor
```

---

## Известные проблемы и TODO

### Редактор стилей
- [ ] Нет undo/redo
- [ ] Нет предварительного просмотра как в Word
- [ ] Можно улучшить UX при работе с множественным выделением

### Конвертер
- [ ] Нет валидации JSON стилей при загрузке
- [ ] Можно добавить больше пресетов по умолчанию

---

## Google Docs — несовместимость и стратегия фиксов

**Корневая причина:** python-docx записывает в XML только `<w:pStyle>`, а все наследуемые свойства (`numPr`, `ind`, `spacing`, `shd`, `pBdr`) остаются только в определении стиля. Google Docs не разрешает их из цепочки стилей, в отличие от Microsoft Word и LibreOffice. Повторное сохранение в LibreOffice «уплощает» эти свойства в XML абзаца.

**Стратегия фикса — принудительное уплощение (`_flatten_style_properties`):**
При создании параграфа с кастомным стилем (инфобокс, список, single_tag) вызывается `_flatten_style_properties(p)`, которая копирует `ind`, `spacing`, `shd`, `pBdr` из `<w:pPr>` стиля в `<w:pPr>` параграфа (кроме `<w:pStyle>`). Это делает документ совместимым с Google Docs без пересохранения.

**Списочные стили — дополнительный фикс (`_fix_list_paragraph`):**
- Для списков (List Bullet, List Number) дополнительно копируется `numPr` из стиля в параграф.
- Если стиль не найден (fallback на базовый), `ilvl` принудительно выставляется по уровню вложенности.

**Отступы перед заголовками — две схемы:**
1. **Параграф → заголовок** (без таблицы между): детектируется в `_process_ast` через look-ahead (`next_is_heading`). Отступ (`w:after`) добавляется к последнему параграфу перед заголовком.
   - Look-ahead теперь пропускает `blank_line` и `block_html`/`paragraph` маркеры (`<!--...-->`).
   - Для `<!--single_tag:-->` созданный параграф возвращается из `_handle_style_marker`, и `next_is_heading` проверяется отдельно.
2. **Таблица → заголовок**: обрабатывается в `_apply_table_spacing()` (post-processing). Отступ (`w:before`) добавляется к заголовку, идущему после таблицы.

---

## История обновлений

| Версия | Изменения |
|--------|-----------|
| Альфа 1 | Базовая конвертация, инфобоксы |
| Альфа 2 | Вложенное форматирование `***жирный курсив***` |
| Альфа 3 | Пресеты таблиц (zebra, plain, fancy) |
| Альфа 4 | Advanced renderer + цветовые правила |
| Альфа 5 | PyQt5 редактор стилей + рефакторинг на модули |
| Альфа 6 | Рефакторинг архитектуры: src/layout, configs/, workspace/, исправление импортов |
| Альфа 7 | Исправление бага с обновлением границ в редакторе. Переименование стилей. Поле тега в Markdown. 6×6 сетка. Кастомные размеры колонок/строк. Smart fit-to-page. Триггер has_text для element_colors. Авто-открытие результата. |
| Альфа 8 | Ширина колонок в редакторе в процентах. Единый `configs/spacing.json` (before_heading, after_list, after_table, table_before_heading). Отступ после таблицы через `spaceBefore` на следующем абзаце. Раздельный отступ для заголовков после таблиц. В редактор добавлены поля «Стиль заголовка» и «Стиль текста» — выбор именованных параграф-стилей из DOCX-шаблона. |
| Альфа 9 | Исправлен отступ `before_heading` после инфобоксов. Три бага: (1) `markdown_processor.py`: single_tag строки (`::: Info text`) не пропускались при генерации — дублировались в AST, блокируя детекцию заголовка. (2) `docx_builder.py`: look-ahead в `_process_ast` пропускал только `blank_line`, но не `block_html` маркеры (`<!--block_end:-->`). (3) `docx_builder.py`: `_handle_style_marker` не возвращал созданный параграф для single_tag и не проверял `next_is_heading`. |
| Альфа 10 | Вкладка «Общие стили» выделена в отдельный виджет `ParagraphStylesPanel` (`panels/paragraph_styles.py`) и переименована в «Стили абзацев». Создан `StyleDataManager` (`style_data_manager.py`) — единый слой доступа к данным, изолирующий всю файловую I/O от визуальных компонентов. MainWindow и все панели используют `StyleDataManager` вместо прямых файловых операций. |
| Альфа 11 | Рефакторинг главного окна: глобальный `QTabWidget` с вкладками «Общие настройки» и «Редактор таблиц». В «Общие настройки» перенесены стили абзацев (список слева + под-табы [АБЗАЦ] [ОБЩЕЕ] [JSON]) с авто-сохранением в `StyleDataManager`. В «Редактор таблиц» добавлен под-таб «Структура и свойства» (`TableStructurePanel`), куда вынесены тег, стили абзацев, обтекание и размеры таблицы. `PropertiesPanel` оставлена только для редактирования ячеек (заливка/шрифт/границы). `VisualGridWidget`: spacing=2. |
