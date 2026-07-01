import logging
import shutil
from pathlib import Path

log = logging.getLogger("sentinel.actions.files")


class FileController:
    def __init__(self, sandbox_config: dict = None):
        self.sandbox_config = sandbox_config or {}

    def read(self, path: str, max_lines: int = 200) -> str:
        filepath = Path(path).resolve()
        if not filepath.exists():
            return f"File not found: {path}"
        if filepath.is_dir():
            return self.list_dir(path)

        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total = len(lines)
            if total <= max_lines:
                return "".join(lines)
            else:
                trunc = lines[:max_lines]
                return "".join(trunc) + f"\n[... Truncated: {total - max_lines} more lines ...]"
        except Exception as e:
            return f"Error reading file: {e}"

    def write(self, path: str, content: str) -> str:
        filepath = Path(path).resolve()
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            size = filepath.stat().st_size
            return f"Written {size} bytes to {filepath}."
        except Exception as e:
            return f"Error writing file: {e}"

    def list_dir(self, path: str = ".") -> str:
        dirpath = Path(path).resolve()
        if not dirpath.exists():
            return f"Directory not found: {path}"
        if not dirpath.is_dir():
            return f"Not a directory: {path}"

        try:
            items = []
            for item in sorted(dirpath.iterdir()):
                if item.is_dir():
                    items.append(f"  [DIR]  {item.name}/")
                else:
                    size = item.stat().st_size
                    suffix = "B"
                    if size >= 1024:
                        size /= 1024
                        suffix = "KB"
                    if size >= 1024:
                        size /= 1024
                        suffix = "MB"
                    items.append(f"  [FILE] {item.name} ({size:.1f}{suffix})")

            return f"Contents of {dirpath}:\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {e}"

    def delete(self, path: str) -> str:
        filepath = Path(path).resolve()
        if not filepath.exists():
            return f"Path not found: {path}"

        try:
            if filepath.is_dir():
                shutil.rmtree(filepath)
                return f"Deleted directory: {filepath}."
            else:
                filepath.unlink()
                return f"Deleted file: {filepath}."
        except Exception as e:
            return f"Error deleting: {e}"

    def copy(self, src: str, dst: str) -> str:
        src_path = Path(src).resolve()
        dst_path = Path(dst).resolve()

        if not src_path.exists():
            return f"Source not found: {src}"

        try:
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
                return f"Copied directory {src} to {dst}."
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                return f"Copied file {src} to {dst}."
        except Exception as e:
            return f"Error copying: {e}"

    def move(self, src: str, dst: str) -> str:
        src_path = Path(src).resolve()
        dst_path = Path(dst).resolve()

        if not src_path.exists():
            return f"Source not found: {src}"

        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            return f"Moved {src} to {dst}."
        except Exception as e:
            return f"Error moving: {e}"
