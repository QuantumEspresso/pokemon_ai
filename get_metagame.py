
from __future__ import annotations

import argparse
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


# ============================================================
# Configuration
# ============================================================

API_BASE = "https://championsbattledata.com/api"

OUTPUT_FILE = Path("database/meta.json")

FORMATS = ("Doubles", "Singles")

# Regulation -> representative API season.
#
# M-A uses the final season M2.
# M-B uses the final season M5.
# M-C uses current data.
#
# Change these mappings if you want to use a different
# representative season for a regulation.

REGULATIONS = {
    "M-A": "M2",
    "M-B": "M5",
    "M-C": "Current",
}

DEFAULT_WORKERS = 8

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Maximum number of archived daily snapshots requested.
HISTORY_DAYS = 31

SOURCE_NAME = "pokemon_champions_battle_data"


# ============================================================
# Logging and HTTP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("metagame")

session = requests.Session()

session.headers.update({
    "User-Agent": "PokemonChampionsMetaScraper/3.0",
    "Accept": "application/json",
})


def fetch_json(
    url: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch JSON with retries for temporary errors."""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 404:
                raise FileNotFoundError(response.url)

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise ValueError(
                    f"Expected JSON object: {response.url}"
                )

            return data

        except FileNotFoundError:
            raise

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            if attempt == MAX_RETRIES:
                raise

            logger.warning(
                "Request failed (%s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

            time.sleep(RETRY_DELAY * attempt)

    raise RuntimeError(f"Could not fetch {url}")


# ============================================================
# Data normalization
# ============================================================

def normalize_category(value: Any) -> str:
    """Normalize category names."""

    if value is None:
        return ""

    return " ".join(
        str(value).strip().casefold().split()
    )


def parse_number(value: Any) -> float | int | None:
    """Convert a value to an integer or float."""

    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        cleaned = (
            value
            .replace("%", "")
            .replace(",", ".")
            .strip()
        )

        if not cleaned:
            return None

        try:
            number = float(cleaned)

            if number.is_integer():
                return int(number)

            return number

        except ValueError:
            return None

    return None


def normalize_row(
    row: dict[str, Any],
    category: str,
) -> dict[str, Any]:
    """Normalize one battle data row."""

    percentage = parse_number(
        row.get("percentage_value")
    )

    if percentage is None:
        percentage = parse_number(
            row.get("percentage")
        )

    rank = parse_number(row.get("rank"))

    result = {
        "name": row.get("name") or None,
        "rank": rank,
        "percentage": percentage,
    }

    # Stat alignments represent nature-like choices.
    if category == "stat_alignment":
        result["stat_up"] = (
            row.get("stat_up") or None
        )

        result["stat_down"] = (
            row.get("stat_down") or None
        )

    # Stat Points are stored as a structured object.
    elif category == "stat_points":
        result["points"] = {
            "hp": parse_number(
                row.get("hp_points")
            ),
            "attack": parse_number(
                row.get("attack_points")
            ),
            "defense": parse_number(
                row.get("defense_points")
            ),
            "sp_attack": parse_number(
                row.get("sp_atk_points")
            ),
            "sp_defense": parse_number(
                row.get("sp_def_points")
            ),
            "speed": parse_number(
                row.get("speed_points")
            ),
        }

    return result


# ============================================================
# Battle data categories
# ============================================================

def extract_categories(
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group API rows into database categories."""

    aliases = {
        "move": "moves",
        "moves": "moves",

        "held_item": "items",
        "item": "items",
        "items": "items",
        "held item": "items",
        "held items": "items",

        "ability": "abilities",
        "abilities": "abilities",

        "teammate": "partners",
        "teammates": "partners",
        "partner": "partners",
        "partners": "partners",

        "stat_alignment": "natures",
        "stat alignment": "natures",
        "nature": "natures",
        "natures": "natures",

        "stat_points": "stat_spreads",
        "stat points": "stat_spreads",
        "stat_spread": "stat_spreads",
        "stat spread": "stat_spreads",
        "spread": "stat_spreads",
    }

    result = {
        "moves": [],
        "items": [],
        "abilities": [],
        "partners": [],
        "stat_spreads": [],
        "natures": [],
    }

    unknown_categories = set()

    for row in rows:
        if not isinstance(row, dict):
            continue

        category = normalize_category(
            row.get("category")
        )

        output_category = aliases.get(category)

        if output_category is None:
            unknown_categories.add(category)
            continue

        result[output_category].append(
            normalize_row(row, category)
        )

    # Sort all categories by rank.
    for values in result.values():
        values.sort(
            key=lambda item: (
                item["rank"] is None,
                item["rank"] if item["rank"] is not None else 0,
            )
        )

    if unknown_categories:
        logger.debug(
            "Unknown API categories: %s",
            sorted(unknown_categories),
        )

    return result


# ============================================================
# Snapshot helpers
# ============================================================

def parse_snapshot_date(
    value: str | None,
) -> datetime | None:
    """Parse API snapshot dates in DD_MM_YYYY format."""

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%d_%m_%Y",
        )

    except ValueError:
        return None


def get_snapshot_period(
    snapshot_date: str | None,
) -> str | None:
    """Return YYYY-MM based on the snapshot date."""

    parsed = parse_snapshot_date(snapshot_date)

    if parsed is None:
        return None

    return parsed.strftime("%Y-%m")


# ============================================================
# Empty database structures
# ============================================================

def empty_ladder_format() -> dict[str, Any]:
    """Create an empty official ladder format entry."""

    return {
        "period": None,
        "snapshot_date": None,
        "rank": None,
        "moves": [],
        "items": [],
        "abilities": [],
        "partners": [],
        "stat_spreads": [],
        "natures": [],
    }


def empty_pokemon_record(
    name: str,
    form: str | None,
) -> dict[str, Any]:
    """Create the complete database structure for one Pokémon."""

    regulations = {}

    for regulation in REGULATIONS:
        regulations[regulation] = {
            "formats": {}
        }

    return {
        "pokemon": name,
        "form": form,
        "sources": {
            "official_ladder": {
                "source": SOURCE_NAME,
                "regulations": regulations,
            },
            "tournaments": {
                "source": "infovgc",
                "regulations": {},
            },
            "showdown": {
                "source": "smogon",
                "regulations": {},
            },
        },
    }


# ============================================================
# API index and rankings
# ============================================================

def get_index() -> dict[str, Any]:
    """Fetch the Pokémon index."""

    return fetch_json(f"{API_BASE}/index")


def get_rankings(
    battle_format: str,
    api_season: str,
) -> dict[str, int]:
    """Return Pokémon ranking positions for one season."""

    params = {
        "format": battle_format,
    }

    if api_season != "Current":
        params["season"] = api_season

    data = fetch_json(
        f"{API_BASE}/rankings",
        params=params,
    )

    result = {}

    for entry in data.get("rankings", []):
        if not isinstance(entry, dict):
            continue

        showdown_id = entry.get("showdownId")
        position = entry.get("position")

        if showdown_id is None:
            continue

        parsed_position = parse_number(position)

        if parsed_position is None:
            continue

        result[str(showdown_id).casefold()] = int(
            parsed_position
        )

    return result


# ============================================================
# Individual Pokémon battle data
# ============================================================

def get_battle_data(
    showdown_id: str,
    battle_format: str,
    api_season: str,
) -> dict[str, Any]:
    """Fetch current data or the latest archived seasonal snapshot."""

    encoded_id = quote(showdown_id, safe="")

    endpoint = (
        f"{API_BASE}/battle/{battle_format}/{encoded_id}"
    )

    if api_season == "Current":
        data = fetch_json(endpoint)

        rows = data.get("rows", [])

        if not isinstance(rows, list):
            rows = []

        result = extract_categories(rows)

        result["snapshot_date"] = data.get("date")
        result["source"] = data.get("source")

        return result

    # Archived seasons are available through daily snapshots.
    data = fetch_json(
        endpoint,
        params={
            "season": api_season,
            "days": HISTORY_DAYS,
        },
    )

    daily_snapshots = data.get("daily", [])

    if (
        not isinstance(daily_snapshots, list)
        or not daily_snapshots
    ):
        logger.debug(
            "No archived snapshots for %s (%s, %s).",
            showdown_id,
            battle_format,
            api_season,
        )

        result = extract_categories([])

        result["snapshot_date"] = None
        result["source"] = None

        return result

    # API documentation specifies newest-first ordering.
    latest_snapshot = daily_snapshots[0]

    rows = latest_snapshot.get("rows", [])

    if not isinstance(rows, list):
        rows = []

    result = extract_categories(rows)

    result["snapshot_date"] = latest_snapshot.get("date")
    result["source"] = latest_snapshot.get("source")

    return result


# ============================================================
# Pokémon identity
# ============================================================

def get_pokemon_identity(
    entry: dict[str, Any],
) -> tuple[str, str | None, str | None]:
    """Extract Pokémon name, form and Showdown ID."""

    showdown_id = (
        entry.get("showdownId")
        or entry.get("showdown_id")
    )

    name = (
        entry.get("name")
        or entry.get("showdownName")
        or entry.get("battleName")
        or showdown_id
    )

    form = entry.get("form")

    if not form:
        form = None

    return (
        str(name),
        str(form) if form else None,
        str(showdown_id) if showdown_id else None,
    )


# ============================================================
# Pokémon record processing
# ============================================================

def process_pokemon(
    entry: dict[str, Any],
    regulation: str,
    api_season: str,
    rankings: dict[str, dict[str, int]],
    fallback_period: str,
) -> tuple[str, dict[str, Any]] | None:
    """Fetch all supported format data for one Pokémon."""

    name, form, showdown_id = get_pokemon_identity(entry)

    if not showdown_id:
        return None

    record = empty_pokemon_record(name, form)

    for battle_format in FORMATS:
        rank = rankings[battle_format].get(
            showdown_id.casefold()
        )

        format_data = empty_ladder_format()

        format_data["rank"] = rank

        try:
            categories = get_battle_data(
                showdown_id=showdown_id,
                battle_format=battle_format,
                api_season=api_season,
            )

            snapshot_date = categories.pop(
                "snapshot_date",
                None,
            )

            source_path = categories.pop(
                "source",
                None,
            )

            format_data.update(categories)

            format_data["snapshot_date"] = snapshot_date

            # Archived snapshots have a real date.
            # Current data has no daily snapshot date.
            format_data["period"] = (
                get_snapshot_period(snapshot_date)
                or fallback_period
            )

            if source_path:
                format_data["data_source"] = source_path

        except FileNotFoundError:
            logger.debug(
                "No data for %s (%s, %s).",
                name,
                battle_format,
                api_season,
            )

        except Exception as error:
            logger.error(
                "Failed to fetch %s (%s, %s): %s",
                name,
                battle_format,
                api_season,
                error,
            )

        record["sources"]["official_ladder"][
            "regulations"
        ][regulation]["formats"][battle_format] = format_data

    return showdown_id, record


# ============================================================
# Scraping one regulation
# ============================================================

def scrape_regulation(
    pokemon_entries: list[dict[str, Any]],
    regulation: str,
    api_season: str,
    period: str,
    workers: int,
) -> dict[str, dict[str, Any]]:
    """Scrape all Pokémon for one regulation."""

    logger.info(
        "Processing regulation %s (API season: %s)",
        regulation,
        api_season,
    )

    rankings = {}

    for battle_format in FORMATS:
        logger.info(
            "Fetching %s rankings for %s...",
            battle_format,
            api_season,
        )

        rankings[battle_format] = get_rankings(
            battle_format,
            api_season,
        )

        logger.info(
            "%s rankings: %s Pokémon.",
            battle_format,
            len(rankings[battle_format]),
        )

    logger.info(
        "Found %s Pokémon in the index.",
        len(pokemon_entries),
    )

    results = {}
    completed = 0
    total = len(pokemon_entries)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                process_pokemon,
                entry,
                regulation,
                api_season,
                rankings,
                period,
            ): entry
            for entry in pokemon_entries
        }

        for future in as_completed(futures):
            completed += 1

            try:
                result = future.result()

                if result is not None:
                    showdown_id, record = result
                    results[showdown_id] = record

            except Exception:
                logger.exception(
                    "Unexpected Pokémon processing error."
                )

            if completed % 10 == 0 or completed == total:
                logger.info(
                    "%s progress: %s/%s",
                    regulation,
                    completed,
                    total,
                )

    return results


# ============================================================
# Main scraping logic
# ============================================================

def scrape_metagame(
    workers: int = DEFAULT_WORKERS,
) -> dict[str, Any]:
    """Build the complete Pokémon metagame database."""

    logger.info("Fetching API index...")

    index = get_index()

    pokemon_entries = index.get("pokemon", [])

    if not isinstance(pokemon_entries, list):
        raise ValueError(
            "The API index does not contain a valid Pokémon list."
        )

    # Keep one entry per Showdown ID.
    # Different forms have different Showdown IDs.
    unique_entries = {}

    for entry in pokemon_entries:
        if not isinstance(entry, dict):
            continue

        _, _, showdown_id = get_pokemon_identity(entry)

        if showdown_id:
            unique_entries[showdown_id.casefold()] = entry

    pokemon_entries = list(unique_entries.values())

    fallback_period = datetime.now().strftime("%Y-%m")

    database = {}

    # Create one record per Pokémon.
    for entry in pokemon_entries:
        name, form, showdown_id = get_pokemon_identity(entry)

        if showdown_id:
            database[showdown_id.casefold()] = (
                empty_pokemon_record(name, form)
            )

    # Obtain available API seasons from rankings.
    # This prevents silently requesting nonexistent seasons.
    available_seasons = set()

    try:
        season_info = fetch_json(
            f"{API_BASE}/rankings",
            params={"format": "Doubles"},
        )

        available_seasons = {
            str(season)
            for season in season_info.get("seasons", [])
        }

        logger.info(
            "Available API seasons: %s",
            ", ".join(sorted(available_seasons)),
        )

    except Exception as error:
        logger.warning(
            "Could not retrieve API season list: %s",
            error,
        )

    # Scrape each regulation separately.
    for regulation, api_season in REGULATIONS.items():

        if (
            available_seasons
            and api_season not in available_seasons
        ):
            logger.warning(
                "Skipping %s: API season %s is not available.",
                regulation,
                api_season,
            )
            continue

        logger.info(
            "Starting regulation %s.",
            regulation,
        )

        regulation_data = scrape_regulation(
            pokemon_entries=pokemon_entries,
            regulation=regulation,
            api_season=api_season,
            period=fallback_period,
            workers=workers,
        )

        for showdown_id, regulation_record in regulation_data.items():
            key = showdown_id.casefold()

            existing = database.get(key)

            if existing is None:
                database[key] = regulation_record
                continue

            existing["sources"]["official_ladder"][
                "regulations"
            ][regulation] = regulation_record["sources"][
                "official_ladder"
            ]["regulations"][regulation]

    return {
        "metadata": {
            "database": "Pokemon Champions Metagame",
            "generated_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "period": fallback_period,
            "source": SOURCE_NAME,
            "api_url": API_BASE,
            "configured_regulations": REGULATIONS,
            "available_api_seasons": sorted(
                available_seasons
            ),
            "formats": list(FORMATS),
        },
        "pokemon": list(database.values()),
    }


# ============================================================
# Saving
# ============================================================

def save_database(
    data: dict[str, Any],
    output_file: Path,
) -> None:
    """Save database atomically."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = output_file.with_suffix(
        output_file.suffix + ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(output_file)

    logger.info(
        "Database saved: %s",
        output_file,
    )


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Pokémon Champions metagame database."
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
    )

    args = parser.parse_args()

    if args.workers < 1:
        raise SystemExit(
            "--workers must be at least 1."
        )

    try:
        data = scrape_metagame(
            workers=args.workers,
        )

        save_database(
            data=data,
            output_file=args.output,
        )

    except KeyboardInterrupt:
        logger.warning(
            "Scraping interrupted. Database was not saved."
        )

    except Exception:
        logger.exception(
            "Metagame scraping failed."
        )
        raise


if __name__ == "__main__":
    main()
