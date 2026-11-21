
from typing import Any

from .database import db


def _get_item_entries() -> list[dict[str, Any]]:
    """Return all item entries from the database."""
    data = db.get("items")

    if not isinstance(data, list):
        return []

    return [
        entry
        for entry in data
        if isinstance(entry, dict) and entry.get("name")
    ]


def search_items(
    query: str = "",
    limit: int = 20,
) -> list[dict[str, str]]:
    """Search items by name."""
    query = query.strip().casefold()
    max_results = max(1, min(limit, 100))

    results = []

    for entry in _get_item_entries():
        name = entry.get("name", "")

        if query and query not in name.casefold():
            continue

        results.append({
            "name": name,
            "description": entry.get("description", ""),
        })

        if len(results) >= max_results:
            break

    return results


def get_item_details(name: str) -> dict[str, str] | None:
    """Return details for an exact item name."""
    query = name.strip().casefold()

    if not query:
        return None

    for entry in _get_item_entries():
        if entry.get("name", "").casefold() == query:
            return {
                "name": entry.get("name", ""),
                "description": entry.get("description", ""),
            }

    return None
