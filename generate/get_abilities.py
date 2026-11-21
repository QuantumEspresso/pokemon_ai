
import json
import re
import sys
import time
import builtins

from pathlib import Path
from collections import OrderedDict
from urllib.parse import urljoin, urldefrag

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

DEBUG = False

POKEDEX_URL = "https://www.serebii.net/pokedex-champions/"

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_DIR / "database"

OUTPUT_JSON = DATABASE_DIR / "abilities.json"

REQUEST_DELAY = 0.2
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# OUTPUT
# ============================================================

def debug_print(*args, **kwargs):
    if DEBUG:
        builtins.print(*args, **kwargs)


def progress_bar(current, total, start_time, label=""):
    if DEBUG or total <= 0:
        return

    percentage = current / total
    width = 30

    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)

    elapsed = time.time() - start_time

    if current:
        remaining = (elapsed / current) * (total - current)
    else:
        remaining = 0

    def format_time(seconds):
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}h {minutes:02d}m"

        if minutes:
            return f"{minutes}m {seconds:02d}s"

        return f"{seconds}s"

    label = clean_text(label)

    if len(label) > 25:
        label = label[:22] + "..."

    line = (
        f"\r[{bar}] "
        f"{percentage * 100:5.1f}% "
        f"{current}/{total} "
        f"| ETA: {format_time(remaining)} "
        f"| {label:<25}"
    )

    sys.stdout.write(line)
    sys.stdout.flush()

    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if not value:
        return ""

    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_key(value):
    return clean_text(value).casefold()


def fetch_soup(url):
    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.content,
        "html.parser"
    )


# ============================================================
# CHAMPIONS POKEDEX
# ============================================================

def get_pokedex_pages():
    """
    Finds all Pokémon listing pages linked from the
    Pokémon Champions Pokédex index.
    """

    soup = fetch_soup(POKEDEX_URL)

    pages = OrderedDict()

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/pokedex-champions/" not in href:
            continue

        url = urldefrag(
            urljoin(POKEDEX_URL, href)
        )[0]

        if not url.lower().endswith(".shtml"):
            continue

        pages[url] = True

    result = list(pages.keys())

    debug_print(
        f"Pokédex pages found: {len(result)}"
    )

    return result


# ============================================================
# COLLECT ABILITIES
# ============================================================

def collect_abilities(pokedex_pages):
    """
    Collects unique abilities linked from the
    Pokémon Champions Pokédex pages.
    """

    abilities = OrderedDict()

    total = len(pokedex_pages)
    start_time = time.time()

    for index, page_url in enumerate(pokedex_pages, start=1):
        debug_print(f"Reading: {page_url}")

        try:
            soup = fetch_soup(page_url)

            for link in soup.find_all("a", href=True):
                href = link["href"]

                if "/abilitydex/" not in href:
                    continue

                name = clean_text(
                    link.get_text(" ", strip=True)
                )

                if not name:
                    continue

                ability_url = urldefrag(
                    urljoin(page_url, href)
                )[0]

                key = normalize_key(name)

                if key not in abilities:
                    abilities[key] = {
                        "name": name,
                        "url": ability_url
                    }

        except Exception as error:
            debug_print(
                f"Error reading {page_url}: {error}"
            )

        progress_bar(
            index,
            total,
            start_time,
            "Collecting abilities"
        )

        time.sleep(REQUEST_DELAY)

    return list(abilities.values())


# ============================================================
# ABILITY DESCRIPTION EXTRACTION
# ============================================================

def extract_description(soup):
    """
    Extracts the ability description from the page text.

    If a Champions-specific description exists, it is preferred.
    Otherwise, the general In-Depth Effect or Game's Text
    description is used.
    """

    page_text = clean_text(
        soup.get_text(" ", strip=True)
    )

    # Find the In-Depth Effect section.
    in_depth_match = re.search(
        r"In-Depth Effect\s*:\s*(.*?)(?="
        r"Blocks Role Play|"
        r"Blocks Receive|"
        r"Blocks Entrainment|"
        r"Blocks Skill Swap|"
        r"Pokémon that can have|"
        r"Pok[eé]mon that can have|"
        r"$)",
        page_text,
        flags=re.IGNORECASE
    )

    in_depth = ""

    if in_depth_match:
        in_depth = clean_text(in_depth_match.group(1))

    # Prefer the Champions-specific effect.
    if in_depth:
        champions_match = re.search(
            r"\(Champions\)\s*(.*)",
            in_depth,
            flags=re.IGNORECASE
        )

        if champions_match:
            description = clean_text(
                champions_match.group(1)
            )

            if description:
                return description

        # If no Champions-specific text exists,
        # use the available general effect.
        description = re.sub(
            r"\s*\((Main Series|Champions)\)",
            "",
            in_depth,
            flags=re.IGNORECASE
        )

        description = clean_text(description)

        if description:
            return description

    # Fallback: Game's Text.
    game_text_match = re.search(
        r"Game's Text\s*:\s*(.*?)(?="
        r"In-Depth Effect|"
        r"Blocks Role Play|"
        r"Pokémon that can have|"
        r"$)",
        page_text,
        flags=re.IGNORECASE
    )

    if game_text_match:
        description = clean_text(
            game_text_match.group(1)
        )

        if description:
            return description

    return None


def get_ability_details(ability):
    soup = fetch_soup(ability["url"])

    description = extract_description(soup)

    if not description:
        raise ValueError(
            "No ability description found on the page."
        )

    return {
        "name": ability["name"],
        "description": description
    }


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database(abilities):
    """
    Downloads descriptions for all collected abilities.
    """

    database = []
    errors = []

    total = len(abilities)
    start_time = time.time()

    for index, ability in enumerate(abilities, start=1):
        name = ability["name"]

        debug_print(
            f"[{index}/{total}] Downloading: {name}"
        )

        try:
            result = get_ability_details(ability)
            database.append(result)

        except Exception as error:
            errors.append({
                "name": name,
                "url": ability["url"],
                "error": str(error)
            })

            debug_print(
                f"Error processing {name}: {error}"
            )

        progress_bar(
            index,
            total,
            start_time,
            name
        )

        time.sleep(REQUEST_DELAY)

    database.sort(
        key=lambda item: item["name"].casefold()
    )

    return database, errors


# ============================================================
# SAVE DATABASE
# ============================================================

def save_database(database):
    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            database,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# MAIN
# ============================================================

def main():
    debug_print("=" * 60)
    debug_print("POKEMON CHAMPIONS - ABILITIES SCRAPER")
    debug_print("=" * 60)

    pokedex_pages = get_pokedex_pages()

    debug_print(
        f"Pokédex pages: {len(pokedex_pages)}"
    )

    if not pokedex_pages:
        raise RuntimeError(
            "No Pokédex pages found. Check the Serebii page structure."
        )

    abilities = collect_abilities(pokedex_pages)

    debug_print(
        f"Unique abilities found: {len(abilities)}"
    )

    if not abilities:
        raise RuntimeError(
            "No abilities found in the Champions Pokédex."
        )

    database, errors = build_database(abilities)

    if not database:
        raise RuntimeError(
            "No ability descriptions were extracted. "
            "The existing JSON file was not overwritten."
        )

    save_database(database)

    debug_print()
    debug_print("=" * 60)
    debug_print("SCRAPING SUMMARY")
    debug_print("=" * 60)

    debug_print(f"Pokédex pages: {len(pokedex_pages)}")
    debug_print(f"Unique abilities: {len(abilities)}")
    debug_print(f"Saved abilities: {len(database)}")
    debug_print(f"Errors: {len(errors)}")
    debug_print(f"Output file: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
