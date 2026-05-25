import os
from pathlib import Path

from linter.config import load_configuration
from linter.converter.markdown_processor import preprocess_markdown
from linter.converter.docx_builder import DocxBuilder
from linter.utils import ensure_output_dir


def run():
    print("[+] Загружаю конфигурацию...")
    config = load_configuration()

    template_path = Path(config.template)
    input_md_path = Path(config.input_md)
    output_path = Path(config.output_docx)

    print(f"[*] Читаю {input_md_path}...")
    raw_markdown = input_md_path.read_text(encoding="utf-8")

    print("[*] Обрабатываю Markdown (блоки, теги)...")
    processed_md = preprocess_markdown(raw_markdown, config)

    print("[*] Строю DOCX документ...")
    builder = DocxBuilder(template_path, config)
    builder.build(processed_md)

    ensure_output_dir(output_path.parent)
    builder.save(output_path)
    print(f"[OK] Готово! Результат сохранён в {output_path}")

    if config.open_after_convert:
        abs_path = output_path.resolve()
        print(f"[*] Открываю {abs_path}...")
        os.startfile(abs_path)
