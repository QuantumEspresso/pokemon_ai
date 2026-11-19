from __future__ import annotations

import argparse
import json
import logging
import re
import threading
import time
import unicodedata

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


# ============================================================
# Configuration
# ============================================================

API_BASE = "https://championsbattledata.com/api"

INFOVGC_BASE = "https://infovgc.com"
INFOVGC_SOURCE = "infovgc"

OUTPUT_FILE = Path("database/meta.json")

FORMATS = ("Doubles", "Singles")

REGULATIONS = {
    "M-A": "M2",
    "M-B": "M5",
    "M-C": "Current",
}

INFOVGC_REGULATIONS = ("M-C",)

DEFAULT_WORKERS = 8

REQUEST_TIMEOUT = 30
MAX_RETRIES = 5
RETRY_DELAY = 1.0

HISTORY_DAYS = 31

INFOVGC_REQUEST_INTERVAL = 0.25

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
    "User-Agent": "PokemonChampionsMetaScraper/5.0",
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

        except (requests.RequestException, ValueError) as error:
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
    if value is None:
        return ""

    return " ".join(str(value).strip().casefold().split())


def parse_number(value: Any) -> float | int | None:
    if value is None or value == "" or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    cleaned = (
        str(value)
        .replace("%", "")
        .replace(",", ".")
        .strip()
    )

    if not cleaned:
        return None

    try:
        number = float(cleaned)
        return int(number) if number.is_integer() else number
    except ValueError:
        return None


def normalize_row(
    row: dict[str, Any],
    category: str,
) -> dict[str, Any]:
    percentage = parse_number(row.get("percentage_value"))

    if percentage is None:
        percentage = parse_number(row.get("percentage"))

    result = {
        "name": row.get("name") or None,
        "rank": parse_number(row.get("rank")),
        "percentage": percentage,
    }

    if category == "stat_alignment":
        result["stat_up"] = row.get("stat_up") or None
        result["stat_down"] = row.get("stat_down") or None

    elif category == "stat_points":
        result["points"] = {
            "hp": parse_number(row.get("hp_points")),
            "attack": parse_number(row.get("attack_points")),
            "defense": parse_number(row.get("defense_points")),
            "sp_attack": parse_number(row.get("sp_atk_points")),
            "sp_defense": parse_number(row.get("sp_def_points")),
            "speed": parse_number(row.get("speed_points")),
        }

    return result


# ============================================================
# Battle data categories
# ============================================================

def extract_categories(
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
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

        category = normalize_category(row.get("category"))
        output_category = aliases.get(category)

        if output_category is None:
            unknown_categories.add(category)
            continue

        result[output_category].append(
            normalize_row(row, category)
        )

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

def parse_snapshot_date(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.strptime(value, "%d_%m_%Y")
    except ValueError:
        return None


def get_snapshot_period(snapshot_date: str | None) -> str | None:
    parsed = parse_snapshot_date(snapshot_date)
    return parsed.strftime("%Y-%m") if parsed else None


# ============================================================
# Empty database structures
# ============================================================

def empty_ladder_format() -> dict[str, Any]:
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
    regulations = {
        regulation: {"formats": {}}
        for regulation in REGULATIONS
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
                "source": INFOVGC_SOURCE,
                "license": "CC BY 4.0",
                "attribution": "infovgc.com",
                "source_url": INFOVGC_BASE,
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
    return fetch_json(f"{API_BASE}/index")


def get_rankings(
    battle_format: str,
    api_season: str,
) -> dict[str, int]:
    params = {"format": battle_format}

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
        position = parse_number(entry.get("position"))

        if showdown_id is not None and position is not None:
            result[str(showdown_id).casefold()] = int(position)

    return result


# ============================================================
# Individual Pokémon battle data
# ============================================================

def get_battle_data(
    showdown_id: str,
    battle_format: str,
    api_season: str,
) -> dict[str, Any]:
    encoded_id = quote(showdown_id, safe="")
    endpoint = f"{API_BASE}/battle/{battle_format}/{encoded_id}"

    if api_season == "Current":
        data = fetch_json(endpoint)
        rows = data.get("rows", [])

        if not isinstance(rows, list):
            rows = []

        result = extract_categories(rows)
        result["snapshot_date"] = data.get("date")
        result["source"] = data.get("source")
        return result

    data = fetch_json(
        endpoint,
        params={
            "season": api_season,
            "days": HISTORY_DAYS,
        },
    )

    daily_snapshots = data.get("daily", [])

    if not isinstance(daily_snapshots, list) or not daily_snapshots:
        result = extract_categories([])
        result["snapshot_date"] = None
        result["source"] = None
        return result

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

    return (
        str(name),
        str(form) if form else None,
        str(showdown_id) if showdown_id else None,
    )


# ============================================================
# INF VGC helpers
# ============================================================

_infovgc_cache: dict[str, dict[str, Any] | None] = {}
_infovgc_cache_lock = threading.Lock()
_infovgc_request_lock = threading.Lock()
_infovgc_last_request = 0.0


def infovgc_slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def infovgc_number(value: Any) -> float | int | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    text = str(value).strip().replace(",", ".")

    match = re.search(r"-?\d+(?:\.\d+)?", text)

    if not match:
        return None

    number = float(match.group())

    return int(number) if number.is_integer() else number


def infovgc_text(element: Any) -> str:
    return " ".join(
        element.get_text(" ", strip=True).split()
    )


def infovgc_normalize_heading(value: str) -> str:
    value = value.casefold().strip()
    value = value.replace("pokémon", "pokemon")
    return re.sub(r"\s+", " ", value)


def fetch_infovgc_page(slug: str) -> BeautifulSoup | None:
    global _infovgc_last_request

    url = f"{INFOVGC_BASE}/pokemon/{quote(slug, safe='')}"

    with _infovgc_request_lock:
        elapsed = time.monotonic() - _infovgc_last_request

        if elapsed < INFOVGC_REQUEST_INTERVAL:
            time.sleep(INFOVGC_REQUEST_INTERVAL - elapsed)

        _infovgc_last_request = time.monotonic()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(compatible; PokemonChampionsMetaScraper/5.0)"
                    ),
                    "Accept": "text/html,application/xhtml+xml",
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 404:
                return None

            
            if response.status_code in {429, 500, 502, 503, 504}:
                retry_after = response.headers.get("Retry-After")

                try:
                    delay = float(retry_after)
                except (TypeError, ValueError):
                    delay = min(5 * (2 ** (attempt - 1)), 60)

                if attempt == MAX_RETRIES:
                    logger.warning(
                        "INF VGC server unavailable for %s after %s attempts.",
                        slug,
                        MAX_RETRIES,
                    )
                    return None

                logger.warning(
                    "INF VGC returned HTTP %s for %s. "
                    "Retrying in %.1f seconds (%s/%s).",
                    response.status_code,
                    slug,
                    delay,
                    attempt,
                    MAX_RETRIES,
                )

                time.sleep(delay)
                continue

            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")

        except requests.RequestException as error:
            if attempt == MAX_RETRIES:
                logger.warning(
                    "INF VGC request failed for %s: %s",
                    slug,
                    error,
                )
                return None

            time.sleep(RETRY_DELAY * attempt)

    return None


def infovgc_get_page(
    pokemon_name: str,
    showdown_id: str | None = None,
) -> tuple[BeautifulSoup | None, str | None]:
    candidates = []

    for value in (pokemon_name, showdown_id):
        if not value:
            continue

        slug = infovgc_slug(value)

        if slug and slug not in candidates:
            candidates.append(slug)

    for slug in candidates:
        soup = fetch_infovgc_page(slug)

        if soup is None:
            continue

        title = soup.find("h1")

        if title is None:
            continue

        title_text = infovgc_text(title).casefold()

        if "not found" in title_text:
            continue

        return soup, slug

    return None, None


def infovgc_get_lines(soup: BeautifulSoup) -> list[str]:
    """
    Return visible page text as separate lines.

    This is deliberately used for percentage sections because the
    page can put labels and percentages in different HTML elements.
    """

    text = soup.get_text("\n", strip=True)

    return [
        " ".join(line.split())
        for line in text.splitlines()
        if line.strip()
    ]


def infovgc_normalize_text(value: str) -> str:
    value = value.casefold().strip()
    value = value.replace("pokémon", "pokemon")
    value = re.sub(r"\s+", " ", value)
    return value


# ============================================================
# INF VGC metrics
# ============================================================

def infovgc_extract_metrics(
    soup: BeautifulSoup,
) -> dict[str, Any]:
    """Extract Pokémon-specific metrics from its profile paragraph."""

    empty = {
        "usage_percent": None,
        "teams": None,
        "total_teams_in_sample": None,
        "usage_rank": None,
        "adjusted_win_rate": None,
        "top_8_index": None,
        "games": None,
        "tournaments": None,
    }

    candidates = []

    for element in soup.find_all(["p", "div"]):
        text = infovgc_text(element)

        if (
            "appears on" in text.casefold()
            and "teams across" in text.casefold()
        ):
            candidates.append(text)

    if not candidates:
        return empty

    paragraph = min(candidates, key=len)

    usage_match = re.search(
        r"appears on\s+([\d.]+)%"
        r".*?\(([\d,]+)\s+of\s+([\d,]+)\s+teams"
        r"\s+across\s+([\d,]+)\s+online tournaments",
        paragraph,
        re.IGNORECASE,
    )

    rank_match = re.search(
        r"ranks\s+#([\d,]+)\s+in usage",
        paragraph,
        re.IGNORECASE,
    )

    wr_match = re.search(
        r"adjusted win rate of\s+([\d.]+)%",
        paragraph,
        re.IGNORECASE,
    )

    top8_match = re.search(
        r"Top 8 index of\s+([\d.]+)",
        paragraph,
        re.IGNORECASE,
    )

    result = dict(empty)

    if usage_match:
        result["usage_percent"] = float(usage_match.group(1))
        result["teams"] = int(usage_match.group(2).replace(",", ""))
        result["total_teams_in_sample"] = int(
            usage_match.group(3).replace(",", "")
        )
        result["tournaments"] = int(
            usage_match.group(4).replace(",", "")
        )

    if rank_match:
        result["usage_rank"] = int(
            rank_match.group(1).replace(",", "")
        )

    if wr_match:
        result["adjusted_win_rate"] = float(wr_match.group(1))

    if top8_match:
        result["top_8_index"] = float(top8_match.group(1))

    for element in soup.find_all(["div", "p", "span", "dt", "dd"]):
        text = infovgc_text(element)

        match = re.fullmatch(
            r"Games\s+([\d,]+)",
            text,
            re.IGNORECASE,
        )

        if match:
            result["games"] = int(
                match.group(1).replace(",", "")
            )
            break

    return result


# ============================================================
# INF VGC percentage sections
# ============================================================

INFOVGC_SECTION_HEADINGS = {
    "moves",
    "items",
    "abilities",
    "natures",
    "most common full sets",
    "teammates",
    "teams that run it",
    "common cores with this pokemon",
    "common cores",
    "pairs",
    "trios",
    "get it in your inbox every monday",
    "report language",
    "data updated on",
}


def infovgc_is_section_heading(value: str) -> bool:
    normalized = infovgc_normalize_text(value)

    if normalized in INFOVGC_SECTION_HEADINGS:
        return True

    if normalized.startswith("data updated on"):
        return True

    return False



def infovgc_extract_percentage_section(
    soup: BeautifulSoup,
    heading_names: set[str],
) -> list[dict[str, Any]]:
    """
    Extract percentage entries from one INF VGC profile section.

    Sections are located only after the "Teams that run it" section.
    This prevents navigation links and table headers from being
    mistaken for actual section headings.

    Supports:
        Blizzard 85.7 %
        Blizzard
        85.7 %

    Also supports multiple entries on one line:
        Timid 42.9 % Quiet 28.6 % Calm 14.3 %
    """

    lines = infovgc_get_lines(soup)

    normalized_lines = [
        infovgc_normalize_text(line)
        for line in lines
    ]

    # The metric sections appear after the team samples.
    try:
        teams_index = normalized_lines.index("teams that run it")
    except ValueError:
        return []

    section_order = [
        "moves",
        "items",
        "abilities",
        "natures",
        "most common full sets",
    ]

    wanted = {
        infovgc_normalize_text(name)
        for name in heading_names
    }

    # Locate section headings in their expected order.
    section_positions = {}

    search_from = teams_index + 1

    for section_name in section_order:
        try:
            position = normalized_lines.index(
                section_name,
                search_from,
            )
        except ValueError:
            continue

        section_positions[section_name] = position
        search_from = position + 1

    selected_name = next(
        (
            name
            for name in section_order
            if name in wanted
        ),
        None,
    )

    if selected_name is None:
        return []

    start_index = section_positions.get(selected_name)

    if start_index is None:
        return []

    # Find the next actual section boundary.
    later_positions = [
        position
        for name, position in section_positions.items()
        if position > start_index
    ]

    end_index = (
        min(later_positions)
        if later_positions
        else len(lines)
    )

    section_lines = lines[start_index + 1:end_index]

    # Join lines because HTML may split a label and its percentage
    # into separate text nodes.
    section_text = " ".join(
        " ".join(line.split())
        for line in section_lines
        if line.strip()
    )

    # Remove the chart explanation if it occurs in this section.
    explanation_index = section_text.casefold().find(
        "the bar is how often"
    )

    if explanation_index >= 0:
        section_text = section_text[:explanation_index]

    # Extract every name-percentage pair independently.
    pattern = re.compile(
        r"(?P<name>[A-Za-z0-9][A-Za-z0-9'’()./& -]*?)"
        r"\s+(?P<percentage>\d+(?:[.,]\d+)?)\s*%"
    )

    result = []
    seen = set()

    for match in pattern.finditer(section_text):
        name = match.group("name").strip(" -|")
        percentage = float(
            match.group("percentage").replace(",", ".")
        )

        if not name or len(name) > 60:
            continue

        # Discard accidental fragments.
        if name.casefold() in {
            "usage",
            "adjusted wr",
            "adjusted win rate",
            "top 8",
        }:
            continue

        key = name.casefold()

        if key in seen:
            continue

        seen.add(key)

        result.append({
            "name": name,
            "usage_percent": percentage,
        })

    return result



# ============================================================
# INF VGC tables
# ============================================================

def infovgc_extract_table_rows(table: Any) -> list[list[str]]:
    result = []

    for row in table.find_all("tr"):
        cells = [
            infovgc_text(cell)
            for cell in row.find_all(["th", "td"])
        ]

        if cells:
            result.append(cells)

    return result


def infovgc_extract_common_sets(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    """Extract the Most common full sets table."""

    heading = None

    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5"]):
        if infovgc_normalize_text(
            infovgc_text(element)
        ) == "most common full sets":
            heading = element
            break

    if heading is None:
        return []

    table = None

    for candidate in heading.find_all_next("table"):
        # Do not accidentally cross into a later section.
        previous_heading = candidate.find_previous(
            ["h1", "h2", "h3", "h4", "h5"]
        )

        if previous_heading is not None:
            previous_text = infovgc_normalize_text(
                infovgc_text(previous_heading)
            )

            if previous_text != "most common full sets":
                break

        table = candidate
        break

    if table is None:
        return []

    rows = infovgc_extract_table_rows(table)

    if len(rows) < 2:
        return []

    headers = [
        re.sub(r"\s+", " ", value.casefold()).strip()
        for value in rows[0]
    ]

    result = []

    for row in rows[1:]:
        if len(row) < 4:
            continue

        def get_cell(
            names: tuple[str, ...],
            fallback_index: int,
        ) -> str:
            for name in names:
                if name in headers:
                    index = headers.index(name)

                    if index < len(row):
                        return row[index]

            return (
                row[fallback_index]
                if fallback_index < len(row)
                else ""
            )

        moves_text = get_cell(("moves",), 2)

        result.append({
            "item": get_cell(("item",), 0) or None,
            "ability": get_cell(("ability",), 1) or None,
            "moves": [
                move.strip()
                for move in re.split(r"\s*/\s*|\s*,\s*", moves_text)
                if move.strip()
            ],
            "teams": infovgc_number(
                get_cell(("times", "teams"), 3)
            ),
            "usage_percent": infovgc_number(
                get_cell(("%", "usage %", "usage"), 4)
            ),
            "adjusted_win_rate": infovgc_number(
                get_cell(
                    ("adj. wr %", "adjusted wr %", "adjusted win rate"),
                    5,
                )
            ),
        })

    return result


# ============================================================
# INF VGC teammates
# ============================================================


def infovgc_extract_pokemon_links(
    element: Any,
) -> list[str]:
    """
    Extract individual Pokémon names from profile links.

    Prefer image alt/title attributes and link metadata.
    Never treat an entire cell containing multiple Pokémon
    as one Pokémon name.
    """

    result = []
    seen = set()

    for link in element.find_all("a"):
        href = str(link.get("href") or "")

        if "/pokemon/" not in href:
            continue

        image = link.find("img")

        candidates = []

        if image is not None:
            candidates.extend([
                image.get("alt"),
                image.get("title"),
            ])

        candidates.extend([
            link.get("title"),
            link.get("aria-label"),
        ])

        # Link text is a fallback, not the preferred source.
        candidates.append(infovgc_text(link))

        name = next(
            (
                str(value).strip()
                for value in candidates
                if value and str(value).strip()
            ),
            None,
        )

        if not name:
            slug = href.rstrip("/").split("/")[-1]
            name = re.sub(
                r"[-_]+",
                " ",
                slug,
            ).strip().title()

        # Do not accept a combined cell text as one name.
        if not name or len(name) > 40:
            continue

        key = name.casefold()

        if key not in seen:
            seen.add(key)
            result.append(name)

    return result




def infovgc_extract_teammates(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    """Extract teammate statistics from the Teammates SVG chart."""

    heading = None

    for element in soup.find_all(["h2", "h3", "h4"]):
        if infovgc_normalize_text(
            infovgc_text(element)
        ) == "teammates":
            heading = element
            break

    if heading is None:
        return []

    # The teammate chart is the SVG immediately following this heading.
    chart = heading.find_next("svg", class_="grafico")

    if chart is None:
        return []

    result = []
    seen = set()

    for bar in chart.find_all("g", class_="barra", recursive=False):
        title = bar.find("title")

        if title is None:
            continue

        text = infovgc_text(title)

        match = re.fullmatch(
            r"(?P<name>.+?)\s*·\s*% with it\s+"
            r"(?P<usage>\d+(?:[.,]\d+)?)\s*%\s*"
            r"·\s*Adj\.\s*WR\s*%\s+"
            r"(?P<win_rate>\d+(?:[.,]\d+)?)\s*%",
            text,
            re.IGNORECASE,
        )

        if not match:
            continue

        name = match.group("name").strip()

        if not name:
            continue

        key = name.casefold()

        if key in seen:
            continue

        seen.add(key)

        result.append({
            "name": name,
            "usage_percent": float(
                match.group("usage").replace(",", ".")
            ),
            "adjusted_win_rate": float(
                match.group("win_rate").replace(",", ".")
            ),
        })

    return result



# ============================================================
# INF VGC cores
# ============================================================


def infovgc_extract_cores(
    soup: BeautifulSoup,
) -> dict[str, list[dict[str, Any]]]:
    """Extract common Pokémon pairs and trios."""

    result = {
        "pairs": [],
        "trios": [],
    }

    heading = None

    for element in soup.find_all(["h2", "h3", "h4"]):
        text = infovgc_normalize_text(
            infovgc_text(element)
        )

        if text in {
            "common cores with this pokemon",
            "common cores",
        }:
            heading = element
            break

    if heading is None:
        return result

    current_group = None
    heading_level = int(heading.name[1])

    for element in heading.find_all_next():
        if element.name in {"h1", "h2", "h3", "h4"}:
            level = int(element.name[1])

            if level <= heading_level:
                break

            if level == heading_level + 1:
                label = infovgc_normalize_text(
                    infovgc_text(element)
                )

                current_group = (
                    label
                    if label in {"pairs", "trios"}
                    else None
                )

            continue

        if element.name != "table" or current_group is None:
            continue

        rows = infovgc_extract_table_rows(element)
        html_rows = element.find_all("tr")

        if len(rows) < 2:
            continue

        headers = [
            infovgc_normalize_text(value)
            for value in rows[0]
        ]

        for row_index, row in enumerate(rows[1:], start=1):
            if not row:
                continue

            html_row = (
                html_rows[row_index]
                if row_index < len(html_rows)
                else None
            )

            pokemon_names = []

            if html_row is not None:
                first_cell = html_row.find(["td", "th"])

                if first_cell is not None:
                    pokemon_names = (
                        infovgc_extract_pokemon_links(first_cell)
                    )

            # Fallback for tables that contain plain text rather
            # than individual Pokémon profile links.
            if not pokemon_names:
                raw_core = row[0].strip()

                pokemon_names = [
                    value.strip()
                    for value in re.split(
                        r"\s+\+\s+|\s{2,}",
                        raw_core,
                    )
                    if value.strip()
                ]

            def get_value(
                names: tuple[str, ...],
                fallback_index: int,
            ) -> str:
                for name in names:
                    normalized_name = infovgc_normalize_text(name)

                    if normalized_name in headers:
                        index = headers.index(normalized_name)

                        if index < len(row):
                            return row[index]

                if fallback_index < len(row):
                    return row[fallback_index]

                return ""

            result[current_group].append({
                "pokemon": pokemon_names,
                "teams": infovgc_number(
                    get_value(("teams",), 1)
                ),
                "usage_percent": infovgc_number(
                    get_value(("usage %", "%", "usage"), 2)
                ),
                "adjusted_win_rate": infovgc_number(
                    get_value(
                        ("adj. wr %", "adjusted wr %"),
                        3,
                    )
                ),
                "top_8": infovgc_number(
                    get_value(("top 8", "top8"), 4)
                ),
            })

    return result


# ============================================================
# INF VGC period and update date
# ============================================================

def infovgc_extract_period(
    soup: BeautifulSoup,
) -> str | None:
    """Extract the date range from the profile description."""

    for element in soup.find_all(["p", "div"]):
        text = infovgc_text(element)

        if (
            "appears on" not in text.casefold()
            or "teams across" not in text.casefold()
        ):
            continue

        match = re.search(
            r"from\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
            r"\s+to\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            text,
            re.IGNORECASE,
        )

        if match:
            return (
                f"{match.group(1)} – "
                f"{match.group(2)}"
            )

    return None


def infovgc_extract_updated_at(
    lines: list[str],
) -> str | None:
    for line in reversed(lines):
        match = re.search(
            r"Data updated on\s+(.+)",
            line,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


# ============================================================
# INF VGC Pokémon parser
# ============================================================

def infovgc_parse_pokemon(
    soup: BeautifulSoup,
    profile_url: str,
) -> dict[str, Any]:
    """Parse all supported tournament data from a Pokémon profile."""

    lines = infovgc_get_lines(soup)

    return {
        "metrics": infovgc_extract_metrics(soup),
        "period": infovgc_extract_period(soup),

        "moves": infovgc_extract_percentage_section(
            soup,
            {"moves"},
        ),

        "items": infovgc_extract_percentage_section(
            soup,
            {"items"},
        ),

        "abilities": infovgc_extract_percentage_section(
            soup,
            {"abilities"},
        ),

        "natures": infovgc_extract_percentage_section(
            soup,
            {"natures"},
        ),

        "teammates": infovgc_extract_teammates(soup),

        "common_sets": infovgc_extract_common_sets(soup),

        "cores": infovgc_extract_cores(soup),

        "data_updated_at": infovgc_extract_updated_at(lines),

        "profile_url": profile_url,
    }


# ============================================================
# INF VGC cache and data retrieval
# ============================================================

def get_infovgc_data(
    pokemon_name: str,
    showdown_id: str | None = None,
) -> dict[str, Any] | None:
    cache_key = (
        showdown_id or pokemon_name
    ).casefold()

    with _infovgc_cache_lock:
        if cache_key in _infovgc_cache:
            return _infovgc_cache[cache_key]

    soup, slug = infovgc_get_page(
        pokemon_name,
        showdown_id,
    )

    if soup is None or slug is None:
        logger.debug(
            "No INF VGC profile found for %s.",
            pokemon_name,
        )

        with _infovgc_cache_lock:
            _infovgc_cache[cache_key] = None

        return None

    profile_url = (
        f"{INFOVGC_BASE}/pokemon/{quote(slug, safe='')}"
    )

    data = infovgc_parse_pokemon(
        soup,
        profile_url,
    )

    metrics = data["metrics"]

    has_any_data = any([
        metrics["usage_percent"] is not None,
        metrics["teams"] is not None,
        data["moves"],
        data["items"],
        data["abilities"],
        data["natures"],
        data["teammates"],
        data["common_sets"],
        data["cores"]["pairs"],
        data["cores"]["trios"],
    ])

    if not has_any_data:
        logger.warning(
            "INF VGC profile found but no recognizable data for %s.",
            pokemon_name,
        )

        with _infovgc_cache_lock:
            _infovgc_cache[cache_key] = None

        return None

    missing_sections = [
        name
        for name in (
            "moves",
            "items",
            "abilities",
            "natures",
            "common_sets",
        )
        if not data[name]
    ]

    if missing_sections:
        logger.warning(
            "INF VGC %s: empty sections: %s",
            pokemon_name,
            ", ".join(missing_sections),
        )

    with _infovgc_cache_lock:
        _infovgc_cache[cache_key] = data

    return data


# ============================================================
# INF VGC output structure
# ============================================================

def build_infovgc_regulation(
    tournament_data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "period": tournament_data.get("period"),
        "format": "Doubles",
        "metrics": tournament_data["metrics"],
        "moves": tournament_data["moves"],
        "items": tournament_data["items"],
        "abilities": tournament_data["abilities"],
        "natures": tournament_data["natures"],
        "teammates": tournament_data["teammates"],
        "common_sets": tournament_data["common_sets"],
        "cores": tournament_data["cores"],
        "data_updated_at": tournament_data["data_updated_at"],
        "profile_url": tournament_data["profile_url"],
    }


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
    name, form, showdown_id = get_pokemon_identity(entry)

    if not showdown_id:
        return None

    record = empty_pokemon_record(name, form)

    if regulation in INFOVGC_REGULATIONS:
        try:
            tournament_data = get_infovgc_data(
                pokemon_name=name,
                showdown_id=showdown_id,
            )

            if tournament_data is not None:
                record["sources"]["tournaments"][
                    "regulations"
                ][regulation] = build_infovgc_regulation(
                    tournament_data
                )

        except Exception as error:
            logger.error(
                "INF VGC failed for %s: %s",
                name,
                error,
            )

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

            snapshot_date = categories.pop("snapshot_date", None)
            source_path = categories.pop("source", None)

            format_data.update(categories)
            format_data["snapshot_date"] = snapshot_date
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

    if regulation in INFOVGC_REGULATIONS:
        logger.info(
            "INF VGC tournament data enabled for %s.",
            regulation,
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
    logger.info("Fetching API index...")

    index = get_index()
    pokemon_entries = index.get("pokemon", [])

    if not isinstance(pokemon_entries, list):
        raise ValueError(
            "The API index does not contain a valid Pokémon list."
        )

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

    for entry in pokemon_entries:
        name, form, showdown_id = get_pokemon_identity(entry)

        if showdown_id:
            database[showdown_id.casefold()] = (
                empty_pokemon_record(name, form)
            )

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

        logger.info("Starting regulation %s.", regulation)

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

            tournament_regulation = (
                regulation_record["sources"]["tournaments"][
                    "regulations"
                ].get(regulation)
            )

            if tournament_regulation is not None:
                existing["sources"]["tournaments"][
                    "regulations"
                ][regulation] = tournament_regulation

    return {
        "metadata": {
            "database": "Pokemon Champions Metagame",
            "generated_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "period": fallback_period,
            "source": SOURCE_NAME,
            "api_url": API_BASE,
            "tournament_source": INFOVGC_SOURCE,
            "tournament_source_url": INFOVGC_BASE,
            "tournament_license": "CC BY 4.0",
            "tournament_regulations": list(
                INFOVGC_REGULATIONS
            ),
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
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = output_file.with_suffix(
        output_file.suffix + ".tmp"
    )

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_file.replace(output_file)

    except Exception:
        if temporary_file.exists():
            temporary_file.unlink()
        raise

    logger.info("Database saved: %s", output_file)


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
        raise SystemExit("--workers must be at least 1.")

    try:
        data = scrape_metagame(workers=args.workers)
        save_database(data=data, output_file=args.output)

    except KeyboardInterrupt:
        logger.warning(
            "Scraping interrupted. Database was not saved."
        )

    except Exception:
        logger.exception("Metagame scraping failed.")
        raise


if __name__ == "__main__":
    main()