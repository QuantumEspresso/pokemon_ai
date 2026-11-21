
from typing import Any

from .database import db


def _get_move_entries() -> list[dict[str, Any]]:
    """Return all move entries from the database."""
    data = db.get("moves")

    if not isinstance(data, list):
        return []

    return [
        entry
        for entry in data
        if isinstance(entry, dict) and entry.get("name")
    ]


def _format_search_result(entry: dict[str, Any]) -> dict[str, Any]:
    """Return a compact move search result."""
    return {
        "name": entry.get("name"),
        "type": entry.get("type"),
        "category": entry.get("category"),
        "power": entry.get("power"),
        "accuracy": entry.get("accuracy"),
        "priority": entry.get("priority"),
    }


def search_moves(
    query: str = "",
    move_type: str | None = None,
    category: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search moves by name, type or category."""
    query = query.strip().casefold()
    move_type = move_type.strip().casefold() if move_type else None
    category = category.strip().casefold() if category else None

    max_results = max(1, min(limit, 100))
    results = []

    for entry in _get_move_entries():
        name = entry.get("name", "")

        if query and query not in name.casefold():
            continue

        if move_type and (entry.get("type") or "").casefold() != move_type:
            continue

        if category and (entry.get("category") or "").casefold() != category:
            continue

        results.append(_format_search_result(entry))

        if len(results) >= max_results:
            break

    return results


def get_move_details(name: str) -> dict[str, Any] | None:
    """Return complete details for an exact move name."""
    query = name.strip().casefold()

    if not query:
        return None

    for entry in _get_move_entries():
        if entry.get("name", "").casefold() == query:
            return entry

    return None


def get_moves_for_pokemon(
    pokemon_name: str,
    move_type: str | None = None,
    category: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return moves that a Pokemon can learn."""
    query = pokemon_name.strip().casefold()

    if not query:
        return []

    move_type = move_type.strip().casefold() if move_type else None
    category = category.strip().casefold() if category else None

    max_results = max(1, min(limit, 500))
    results = []

    for entry in _get_move_entries():
        learnable_by = entry.get("pokemon_that_learn", [])

        if not any(
            isinstance(name, str) and name.casefold() == query
            for name in learnable_by
        ):
            continue

        if move_type and (entry.get("type") or "").casefold() != move_type:
            continue

        if category and (entry.get("category") or "").casefold() != category:
            continue

        results.append(_format_search_result(entry))

        if len(results) >= max_results:
            break

    return results
