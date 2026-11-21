
from typing import Any

from .database import db


def _get_regulations() -> list[dict[str, Any]]:
    """Return all regulation entries from the database."""
    data = db.get("rulesets")

    if not isinstance(data, dict):
        return []

    regulations = data.get("regulations", [])

    if not isinstance(regulations, list):
        return []

    return [
        entry
        for entry in regulations
        if isinstance(entry, dict) and entry.get("name")
    ]


def _find_regulation(name: str) -> dict[str, Any] | None:
    """Find a regulation by its name or slug."""
    query = name.strip().casefold()

    if not query:
        return None

    normalized_query = query.removeprefix("regulation ").strip()

    for regulation in _get_regulations():
        regulation_name = regulation.get("name", "").casefold()
        slug = regulation.get("slug", "").casefold()

        if (
            query == regulation_name
            or normalized_query == slug
            or normalized_query == regulation_name.removeprefix("regulation ")
        ):
            return regulation

    return None


def get_available_regulations() -> list[dict[str, Any]]:
    """Return available regulations and their basic information."""
    results = []

    for regulation in _get_regulations():
        overview = regulation.get("overview", {})
        dates = overview.get("dates", {}) if isinstance(overview, dict) else {}
        pokemon = regulation.get("pokemon", {})
        mega = regulation.get("mega_evolutions", {})

        results.append({
            "name": regulation.get("name"),
            "slug": regulation.get("slug"),
            "status": regulation.get("status"),
            "start_date": dates.get("start"),
            "end_date": dates.get("end"),
            "total_selectable_forms": pokemon.get("total_forms"),
            "total_mega_evolutions": mega.get("total"),
        })

    return results


def get_regulation_details(
    name: str,
) -> dict[str, Any] | None:
    """Return general information about a regulation."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    overview = regulation.get("overview", {})
    pokemon = regulation.get("pokemon", {})
    mega = regulation.get("mega_evolutions", {})
    changes = regulation.get("changes", {})
    sources = regulation.get("sources", {})

    return {
        "name": regulation.get("name"),
        "slug": regulation.get("slug"),
        "url": regulation.get("url"),
        "status": regulation.get("status"),
        "overview": overview,
        "previous_regulation": changes.get("previous_regulation"),
        "total_selectable_forms": pokemon.get("total_forms"),
        "total_mega_evolutions": mega.get("total"),
        "verification": regulation.get("verification"),
        "sources": sources,
        "update_history": regulation.get("update_history", []),
    }


def get_regulation_pokemon(
    name: str,
    query: str,
    limit: int = 100,
) -> dict[str, Any] | None:
    """Search all matching selectable Pokemon forms in a regulation."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    search = query.strip().casefold()

    if not search:
        return {
            "regulation": regulation.get("name"),
            "query": query,
            "matches": [],
            "total_matches": 0,
        }

    pokemon_data = regulation.get("pokemon", {})
    forms = pokemon_data.get("selectable_forms", [])

    if not isinstance(forms, list):
        forms = []

    matches = [
        form
        for form in forms
        if isinstance(form, dict)
        and search in form.get("name", "").casefold()
    ]

    max_results = max(1, min(limit, 500))

    return {
        "regulation": regulation.get("name"),
        "query": query,
        "total_matches": len(matches),
        "matches": [
            {
                "name": form.get("name"),
                "dex_number": form.get("dex_number"),
                "types": form.get("types", []),
                "form_type": form.get("form_type"),
                "selectable": True,
            }
            for form in matches[:max_results]
        ],
    }


def get_regulation_changes(
    name: str,
) -> dict[str, Any] | None:
    """Return Pokemon added and removed in a regulation."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    changes = regulation.get("changes", {})

    return {
        "regulation": regulation.get("name"),
        "previous_regulation": changes.get("previous_regulation"),
        "added": changes.get("added", []),
        "removed": changes.get("removed", []),
    }


def get_regulation_mega_evolutions(
    name: str,
    query: str = "",
    limit: int = 100,
) -> dict[str, Any] | None:
    """Search Mega Evolutions available in a regulation."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    mega_data = regulation.get("mega_evolutions", {})
    forms = mega_data.get("forms", [])

    if not isinstance(forms, list):
        forms = []

    search = query.strip().casefold()

    matches = []

    for entry in forms:
        if not isinstance(entry, dict):
            continue

        base = entry.get("base_pokemon", {})
        mega = entry.get("mega_form", {})

        base_name = base.get("name", "")
        mega_name = mega.get("name", "")

        if search and (
            search not in base_name.casefold()
            and search not in mega_name.casefold()
        ):
            continue

        matches.append({
            "base_pokemon": base,
            "mega_form": mega,
        })

    max_results = max(1, min(limit, 500))

    return {
        "regulation": regulation.get("name"),
        "query": query,
        "total_matches": len(matches),
        "mega_evolutions": matches[:max_results],
    }


def get_regulation_rules(
    name: str,
    category: str = "",
) -> dict[str, Any] | None:
    """Return rules and restrictions for a regulation."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    rules = regulation.get("rules", {})

    if not isinstance(rules, dict):
        rules = {}

    search = category.strip().casefold()

    if search:
        matches = {
            key: value
            for key, value in rules.items()
            if search in key.casefold()
        }

        return {
            "regulation": regulation.get("name"),
            "category": category,
            "rules": matches,
        }

    return {
        "regulation": regulation.get("name"),
        "rules": rules,
    }


def get_regulation_verification(
    name: str,
) -> dict[str, Any] | None:
    """Return verification statistics and known information gaps."""
    regulation = _find_regulation(name)

    if not regulation:
        return None

    return {
        "regulation": regulation.get("name"),
        "verification": regulation.get("verification", {}),
        "rules": regulation.get("rules", {}),
        "sources": regulation.get("sources", {}),
    }
