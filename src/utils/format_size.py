from pathlib import Path


def format_size_from_path(path: Path) -> str:
    """Return the file size of a path in a more lisible way using (KB/MB/GB/...) suffix"""
    try:
        size = path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except Exception:  # noqa: BLE001
        return "?"
