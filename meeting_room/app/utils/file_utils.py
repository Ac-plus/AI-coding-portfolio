import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


def ensure_parent_dir(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def read_json(file_path: Path, default: Any) -> Any:
    if not file_path.exists():
        return default
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_atomic(file_path: Path, payload: Any) -> None:
    ensure_parent_dir(file_path)
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=file_path.parent,
        delete=False,
    ) as tmp_file:
        json.dump(payload, tmp_file, ensure_ascii=False, indent=2)
        tmp_file.flush()
        temp_path = Path(tmp_file.name)
    temp_path.replace(file_path)
