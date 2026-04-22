import json
from pathlib import Path


class Manifest:
    def __init__(self, entries: list[dict]):
        self._pages = {e["url"]: e for e in entries}

    @classmethod
    def from_path(cls, path: Path) -> "Manifest":
        return cls(json.loads(path.read_text()))

    def get(self, url_path: str) -> dict | None:
        """Look up a URL path, trying with and without trailing slash."""
        return (
            self._pages.get(url_path)
            or self._pages.get(url_path.rstrip("/") + "/")
            or self._pages.get(url_path.rstrip("/"))
        )
