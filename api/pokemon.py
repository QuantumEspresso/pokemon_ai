
from typing import Any

from .database import db


def _get_pokemon_entries() -> list[dict[str, Any]]:
    """Return valid Pokemon entries, excluding the database header."""
    data = db.get("pokemon")

    return [
        entry
        for entry in data.get("pokemon", [])
        if entry.get("name") and entry.get("base_stats")
    ]


def _get_types(entry: dict[str, Any]) -> list[str]:
    """Return types for the current Pokemon entry."""
    types = entry.get("types", [])

    if isinstance(types, list):
        return types

    if isinstance(types, dict):
        name = (entry.get("name") or "").casefold()
        form = (entry.get("form") or "").casefold()

        # Prefer an exact form key.
        for key, value in types.items():
            if key.casefold() == form and isinstance(value, list):
                return value

        # Then prefer an exact Pokemon name key.
        for key, value in types.items():
            if key.casefold() == name and isinstance(value, list):
                return value

        # If there is only one mapping, use it.
        # Do not merge multiple mappings because they may describe
        # different forms.
        if len(types) == 1:
            value = next(iter(types.values()))
            if isinstance(value, list):
                return value

    return []


def _format_search_result(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": entry.get("name"),
        "form": entry.get("form"),
        "dex_number": entry.get("dex_number"),
        "types": _get_types(entry),
    }


def _format_details(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": entry.get("name"),
        "form": entry.get("form"),
        "dex_number": entry.get("dex_number"),
        "types": _get_types(entry),
        "base_stats": entry.get("base_stats"),
        "abilities": entry.get("abilities", []),
        "moves": entry.get("moves", []),
    }


def _format_ambiguous_result(
    query: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return available forms when a query matches multiple entries."""
    return {
        "query": query,
        "ambiguous": True,
        "message": "Multiple Pokemon forms matched. Specify the exact form name.",
        "available_forms": [
            _format_search_result(entry)
            for entry in entries
        ],
    }


def search_pokemon(
    query: str = "",
    pokemon_type: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search Pokemon by name, form or type."""
    query = query.strip().casefold()
    pokemon_type = pokemon_type.strip().casefold() if pokemon_type else None

    results = []
    max_results = max(1, min(limit, 100))

    for entry in _get_pokemon_entries():
        name = entry.get("name", "")
        form = entry.get("form") or ""

        if query and query not in name.casefold() and query not in form.casefold():
            continue

        types = _get_types(entry)

        if pokemon_type and pokemon_type not in [t.casefold() for t in types]:
            continue

        results.append(_format_search_result(entry))

        if len(results) >= max_results:
            break

    return results


def get_pokemon_details(name: str) -> dict[str, Any] | None:
    """Return detailed data for a Pokemon or a specific form."""
    query = name.strip().casefold()

    if not query:
        return None

    entries = _get_pokemon_entries()

    # 1. Exact form match.
    exact_form_matches = [
        entry
        for entry in entries
        if (entry.get("form") or "").casefold() == query
    ]

    if len(exact_form_matches) == 1:
        return _format_details(exact_form_matches[0])

    if len(exact_form_matches) > 1:
        return _format_ambiguous_result(name, exact_form_matches)

    # 2. Exact Pokemon name match.
    exact_name_matches = [
        entry
        for entry in entries
        if entry.get("name", "").casefold() == query
    ]

    if len(exact_name_matches) == 1:
        return _format_details(exact_name_matches[0])

    if len(exact_name_matches) > 1:
        return _format_ambiguous_result(name, exact_name_matches)

    # 3. Partial name or form match.
    partial_matches = [
        entry
        for entry in entries
        if query in entry.get("name", "").casefold()
        or query in (entry.get("form") or "").casefold()
    ]

    if len(partial_matches) == 1:
        return _format_details(partial_matches[0])

    if len(partial_matches) > 1:
        return _format_ambiguous_result(name, partial_matches)

    return None
