
from typing import Any

from .database import db


def _get_ability_entries() -> list[dict[str, Any]]:
    """Return all ability entries from the database."""
    data = db.get("abilities")

    if not isinstance(data, list):
        return []

    return [
        entry
        for entry in data
        if isinstance(entry, dict) and entry.get("name")
    ]


def search_abilities(
    query: str = "",
    limit: int = 20,
) -> list[dict[str, str]]:
    """Search abilities by name."""
    query = query.strip().casefold()
    max_results = max(1, min(limit, 100))

    results = []

    for entry in _get_ability_entries():
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


def get_ability_details(name: str) -> dict[str, str] | None:
    """Return details for an exact ability name."""
    query = name.strip().casefold()

    if not query:
        return None

    for entry in _get_ability_entries():
        if entry.get("name", "").casefold() == query:
            return {
                "name": entry.get("name", ""),
                "description": entry.get("description", ""),
            }

    return None



def get_pokemon_abilities(
    pokemon_name: str,
) -> dict[str, Any] | None:
    """Return abilities for all matching Pokemon forms."""
    query = pokemon_name.strip().casefold()

    if not query:
        return None

    data = db.get("pokemon")

    if not isinstance(data, dict):
        return None

    entries = [
        entry
        for entry in data.get("pokemon", [])
        if isinstance(entry, dict)
        and entry.get("name")
        and entry.get("base_stats")
    ]

    # Prefer exact matches before partial matches.
    matches = [
        entry
        for entry in entries
        if entry.get("name", "").casefold() == query
        or (entry.get("form") or "").casefold() == query
    ]

    if not matches:
        matches = [
            entry
            for entry in entries
            if query in entry.get("name", "").casefold()
            or query in (entry.get("form") or "").casefold()
        ]

    if not matches:
        return None

    abilities_by_name = {
        entry["name"].casefold(): entry
        for entry in _get_ability_entries()
    }

    abilities = []

    for pokemon in matches:
        form = pokemon.get("form") or pokemon.get("name")
        ability_names = pokemon.get("abilities", [])

        for ability_name in ability_names:
            if not isinstance(ability_name, str):
                continue

            ability = abilities_by_name.get(
                ability_name.casefold()
            )

            abilities.append({
                "name": ability_name,
                "form": form,
                "description": (
                    ability.get("description", "")
                    if ability else None
                ),
            })

    return {
        "name": matches[0].get("name"),
        "matched_forms": [
            entry.get("form") or entry.get("name")
            for entry in matches
        ],
        "abilities": abilities,
    }
