from pathlib import Path


def ensure_output_dir(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
