
import json
import logging
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# Configuration
ITEMS_LIST_URL = "https://www.serebii.net/pokemonchampions/items.shtml"
OUTPUT_FILE = "database/items.json"

DEBUG = False

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
}


def log(message):
    if DEBUG:
        print(f"[DEBUG] {message}")


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text):
    return clean_text(text).lower().rstrip(":")


def fetch_page(url):
    """Download and parse the Serebii items page."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    return BeautifulSoup(response.text, "lxml")


def find_miscellaneous_table(soup):
    """
    Find the first table belonging to the Miscellaneous Items section.
    Tables after this point are excluded.
    """
    heading = soup.find(
        string=lambda text: (
            text is not None
            and normalize_text(text) == "miscellaneous items"
        )
    )

    if heading is None:
        log("Miscellaneous Items heading was not found.")
        return None

    parent = heading.parent
    return parent.find_next("table")


def get_tables_before_miscellaneous(soup):
    """Return tables appearing before the Miscellaneous Items section."""
    tables = soup.find_all("table")
    miscellaneous_table = find_miscellaneous_table(soup)

    if miscellaneous_table is None:
        return tables

    result = []

    for table in tables:
        if table is miscellaneous_table:
            break

        result.append(table)

    return result


def extract_item_from_row(row):
    """Extract an item name and description from a table row."""
    cells = row.find_all(["td", "th"])

    if len(cells) < 3:
        return None

    # Find the cell containing the item's name link.
    name_link = None
    name_cell = None

    for cell in cells:
        link = cell.find("a", href=True)

        if link and clean_text(link.get_text(" ", strip=True)):
            name_link = link
            name_cell = cell
            break

    if name_link is None or name_cell is None:
        return None

    name = clean_text(name_link.get_text(" ", strip=True))

    # Find the name cell position and read the following cell.
    try:
        name_index = cells.index(name_cell)
    except ValueError:
        return None

    if name_index + 1 >= len(cells):
        return None

    description = clean_text(
        cells[name_index + 1].get_text(" ", strip=True)
    )

    if not name or not description:
        return None

    # Ignore column headers.
    if normalize_text(name) in {
        "name",
        "picture",
        "effect",
        "location",
    }:
        return None

    return {
        "name": name,
        "description": description,
    }


def scrape_items(soup):
    """Collect items from Hold Items, Mega Stones and Berries."""
    items = []
    seen_names = set()

    tables = get_tables_before_miscellaneous(soup)

    print(f"Found {len(tables)} tables before Miscellaneous Items.")

    for table in tqdm(tables, desc="Processing item tables", unit="table"):
        rows = table.find_all("tr")

        for row in rows:
            item = extract_item_from_row(row)

            if item is None:
                continue

            name_key = item["name"].lower()

            if name_key in seen_names:
                continue

            seen_names.add(name_key)
            items.append(item)

            log(f"Found item: {item['name']}")

    return items


def save_database(items):
    """Save items to a JSON database."""
    output_path = Path(OUTPUT_FILE)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            items,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"\nSaved {len(items)} items to {output_path.resolve()}")


def main():
    print("Downloading Pokémon Champions items...")

    try:
        soup = fetch_page(ITEMS_LIST_URL)

        print("Processing item database...")
        items = scrape_items(soup)

        if not items:
            raise RuntimeError(
                "No items found. Check the page structure and DEBUG output."
            )

        save_database(items)

    except requests.RequestException as error:
        print(f"Download error: {error}", file=sys.stderr)
        sys.exit(1)

    except Exception as error:
        print(f"Scraping error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
