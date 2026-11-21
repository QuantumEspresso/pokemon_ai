import json
import threading
from pathlib import Path
from typing import Any
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = Path(
    os.environ.get(
        "POKEMON_AI_DATABASE_DIR",
        PROJECT_DIR / "database"
    )
)

DATABASE_FILES = {
    "pokemon": "pokemon.json",
    "moves": "moves.json",
    "abilities": "abilities.json",
    "items": "items.json",
    "meta": "meta.json",
    "rulesets": "rulesets.json",
}


class DatabaseError(Exception):
    """Raised when a database cannot be loaded or accessed."""


class JSONDatabase:
    """
    Read-only JSON database with automatic cache invalidation.

    A database is reloaded when its modification time or file size changes.
    """

    def __init__(self, directory: Path = DATABASE_DIR):
        self.directory = Path(directory)
        self._cache: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def available_databases(self) -> list[str]:
        return list(DATABASE_FILES.keys())

    def _get_path(self, name: str) -> Path:
        if name not in DATABASE_FILES:
            raise DatabaseError(f"Unknown database: {name}")

        return self.directory / DATABASE_FILES[name]

    def get(self, name: str) -> Any:
        """
        Return database contents, using cached data when the file is unchanged.
        """
        path = self._get_path(name)

        with self._lock:
            try:
                stat = path.stat()
            except OSError as exc:
                raise DatabaseError(
                    f"Cannot access database file '{path}': {exc}"
                ) from exc

            cached = self._cache.get(name)

            if (
                cached is not None
                and cached["mtime_ns"] == stat.st_mtime_ns
                and cached["size"] == stat.st_size
            ):
                return cached["data"]

            try:
                with path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
            except json.JSONDecodeError as exc:
                raise DatabaseError(
                    f"Invalid JSON in '{path}': {exc}"
                ) from exc
            except OSError as exc:
                raise DatabaseError(
                    f"Cannot read database file '{path}': {exc}"
                ) from exc

            self._cache[name] = {
                "mtime_ns": stat.st_mtime_ns,
                "size": stat.st_size,
                "data": data,
            }

            return data

    def reload(self, name: str) -> Any:
        """Force reload of a database, bypassing its cache."""
        with self._lock:
            self._cache.pop(name, None)
            return self.get(name)

    def clear_cache(self) -> None:
        """Clear all cached databases."""
        with self._lock:
            self._cache.clear()


db = JSONDatabase()