
import json
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# Configuration
DEBUG = False

MOVES_LIST_URL = "https://www.serebii.net/pokemonchampions/moves.shtml"
OUTPUT_JSON = "database/moves.json"

REQUEST_DELAY = 0.15
TIMEOUT = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def log(message):
    if DEBUG:
        print(message)


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_label(value):
    value = clean_text(value).casefold()
    value = value.replace("?", "")
    value = value.replace(":", "")
    value = value.replace("/", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def fetch_page(url):
    try:
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "latin-1"

        return BeautifulSoup(response.text, "lxml")

    except requests.RequestException as error:
        log(f"Request failed: {url} ({error})")
        return None


def get_direct_cells(row):
    return row.find_all(["td", "th"], recursive=False)


def get_cell_value(cell):
    """
    Extract readable text from a cell.
    If the cell contains images, use their alt/title or filename.
    """
    images = cell.find_all("img")

    if images:
        labels = []

        for image in images:
            label = image.get("alt") or image.get("title")

            if not label:
                src = image.get("src", "")
                filename = src.rsplit("/", 1)[-1]
                label = re.sub(r"\.[^.]+$", "", filename)
                label = label.replace("-", " ").replace("_", " ").title()

            if label:
                labels.append(clean_text(label))

        if labels:
            return ", ".join(labels)

    return clean_text(cell.get_text(" ", strip=True))


def get_image_label(cell):
    """
    Extract a type or category from an image.
    Serebii images often have no alt/title attributes.
    """
    image = cell.find("img")

    if not image:
        return clean_text(cell.get_text(" ", strip=True))

    label = image.get("alt") or image.get("title")

    if label:
        return clean_text(label)

    src = image.get("src", "")
    filename = src.rsplit("/", 1)[-1]
    filename = re.sub(r"\.[^.]+$", "", filename).lower()

    known_labels = {
        "normal": "Normal",
        "fire": "Fire",
        "water": "Water",
        "electric": "Electric",
        "grass": "Grass",
        "ice": "Ice",
        "fighting": "Fighting",
        "poison": "Poison",
        "ground": "Ground",
        "flying": "Flying",
        "psychic": "Psychic",
        "bug": "Bug",
        "rock": "Rock",
        "ghost": "Ghost",
        "dragon": "Dragon",
        "dark": "Dark",
        "steel": "Steel",
        "fairy": "Fairy",
        "physical": "Physical",
        "special": "Special",
        "other": "Status",
        "status": "Status",
    }

    return known_labels.get(
        filename,
        filename.replace("-", " ").replace("_", " ").title()
    )


# --------------------------------------------------
# Table parsing helpers
# --------------------------------------------------

def expand_table_row(row):
    """
    Expand cells according to colspan.
    """
    expanded = []

    for cell in get_direct_cells(row):
        try:
            colspan = int(cell.get("colspan", 1))
        except (TypeError, ValueError):
            colspan = 1

        colspan = max(1, colspan)
        value = get_cell_value(cell)

        for _ in range(colspan):
            expanded.append(value)

    return expanded


def get_table_rows(table):
    return [
        expand_table_row(row)
        for row in table.find_all("tr")
    ]


def find_row_index(rows, expected_label, start_index=0):
    """
    Find a row containing a given label.
    Search starts at start_index.
    """
    expected = normalize_label(expected_label)

    for row_index in range(start_index, len(rows)):
        for cell in rows[row_index]:
            if normalize_label(cell) == expected:
                return row_index

    return None


def get_value_below_label(rows, expected_label, start_index=0):
    """
    Find a label and return the value directly below it
    in the same expanded column.
    """
    expected = normalize_label(expected_label)

    for row_index in range(start_index, len(rows)):
        row = rows[row_index]

        for column_index, cell in enumerate(row):
            if normalize_label(cell) != expected:
                continue

            if row_index + 1 >= len(rows):
                return ""

            value_row = rows[row_index + 1]

            if column_index >= len(value_row):
                return ""

            return clean_text(value_row[column_index])

    return ""


def find_detail_table(soup):
    """
    Find the table containing the main move information.
    """
    required_labels = {
        "attack name",
        "battle type",
        "category",
        "power points",
        "base power",
        "accuracy",
    }

    for table in soup.find_all("table"):
        rows = get_table_rows(table)

        labels = {
            normalize_label(cell)
            for row in rows
            for cell in row
        }

        if required_labels.issubset(labels):
            return table

    return None



def find_properties_table(soup):
    """
    Find the actual move properties table.
    Ignore Pokedex and other unrelated tables.
    """
    dex_labels = {
        "gen ix dex",
        "name",
        "abilities",
        "hp",
        "att",
        "def",
        "s.att",
        "s.def",
        "spd",
    }

    property_labels = {
        "physical contact",
        "sound-type - details",
        "punch move - details",
        "biting move - details",
        "snatchable",
        "slicing move - details",
        "bullet-type - details",
        "wind move - details",
        "powder move",
        "metronome",
        "affected by gravity",
        "defrosts when used",
        "reflected by magic coat magic bounce",
        "blocked by protect detect",
        "copyable by mirror move",
    }

    for table in soup.find_all("table"):
        rows = get_table_rows(table)

        labels = {
            normalize_label(cell)
            for row in rows
            for cell in row
        }

        # Ignore Pokedex tables.
        if labels.intersection(dex_labels):
            continue

        # Require several known move property labels.
        matching_labels = labels.intersection(property_labels)

        if len(matching_labels) >= 5:
            return table

    return None



def get_attack_name_row_index(rows):
    """
    Find the Attack Name row.
    All rows before this one are ignored.
    """
    return find_row_index(rows, "Attack Name")


# --------------------------------------------------
# Move list
# --------------------------------------------------

def get_move_list():
    """
    Collect all move names and their detail page URLs.
    """
    soup = fetch_page(MOVES_LIST_URL)

    if soup is None:
        raise RuntimeError("Could not download the moves list page.")

    moves = {}

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/attackdex-champions/" not in href:
            continue

        if not href.lower().endswith(".shtml"):
            continue

        name = clean_text(link.get_text(" ", strip=True))

        if not name:
            continue

        url = urljoin(MOVES_LIST_URL, href)

        moves[url] = {
            "name": name,
            "url": url,
        }

    if not moves:
        raise RuntimeError("No moves were found on the moves list page.")

    return list(moves.values())


# --------------------------------------------------
# Move name
# --------------------------------------------------

def extract_move_name(table, fallback_name):
    """
    Find Attack Name first, then extract the value below it.
    """
    rows = get_table_rows(table)

    attack_name_index = get_attack_name_row_index(rows)

    if attack_name_index is None:
        log(f"Attack Name label not found. Using fallback: {fallback_name}")
        return fallback_name

    if attack_name_index + 1 >= len(rows):
        return fallback_name

    header_row = rows[attack_name_index]
    value_row = rows[attack_name_index + 1]

    for column_index, cell in enumerate(header_row):
        if normalize_label(cell) != "attack name":
            continue

        if column_index >= len(value_row):
            continue

        raw_name = clean_text(value_row[column_index])

        # Remove Japanese characters and everything following them.
        raw_name = re.sub(
            r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff].*$",
            "",
            raw_name
        ).strip()

        # Do not accept a header label as a move name.
        if raw_name and normalize_label(raw_name) != "attack name":
            return raw_name

    return fallback_name


# --------------------------------------------------
# Main move statistics
# --------------------------------------------------

def extract_type_and_category(rows, start_index=0):
    """
    Extract Battle Type and Category from their label row.
    """
    result = {
        "type": "",
        "category": "",
    }

    type_row_index = find_row_index(
        rows,
        "Battle Type",
        start_index
    )

    if type_row_index is None:
        return result

    headers = rows[type_row_index]

    if type_row_index + 1 >= len(rows):
        return result

    values = rows[type_row_index + 1]

    for index, header in enumerate(headers):
        label = normalize_label(header)

        if index >= len(values):
            continue

        if label == "battle type":
            result["type"] = values[index]

        elif label == "category":
            result["category"] = values[index]

    return result


def extract_main_stats(table):
    """
    Extract standard battle statistics using labels.
    Ignore all rows before Attack Name.
    """
    all_rows = get_table_rows(table)

    attack_name_index = get_attack_name_row_index(all_rows)

    if attack_name_index is None:
        log("Attack Name row not found in main details table.")
        rows = all_rows
        start_index = 0
    else:
        rows = all_rows
        start_index = attack_name_index

    result = {
        "type": "",
        "category": "",
        "pp": "",
        "power": "",
        "accuracy": "",
        "battle_effect": "",
        "in_depth_effect": "",
        "secondary_effect": "",
        "effect_rate": "",
        "critical_hit_rate": "",
        "priority": "",
        "pokemon_hit_in_battle": "",
    }

    # Battle Type and Category
    type_category = extract_type_and_category(
        rows,
        start_index
    )

    result["type"] = type_category["type"]
    result["category"] = type_category["category"]

    # Basic statistics
    result["pp"] = get_value_below_label(
        rows, "Power Points", start_index
    )

    result["power"] = get_value_below_label(
        rows, "Base Power", start_index
    )

    result["accuracy"] = get_value_below_label(
        rows, "Accuracy", start_index
    )

    # Effects
    result["battle_effect"] = get_value_below_label(
        rows, "Battle Effect", start_index
    )

    result["in_depth_effect"] = get_value_below_label(
        rows, "In-Depth Effect", start_index
    )

    result["secondary_effect"] = get_value_below_label(
        rows, "Secondary Effect", start_index
    )

    result["effect_rate"] = get_value_below_label(
        rows, "Effect Rate", start_index
    )

    # Additional battle statistics
    result["critical_hit_rate"] = get_value_below_label(
        rows, "Base Critical Hit Rate", start_index
    )

    result["priority"] = get_value_below_label(
        rows, "Speed Priority", start_index
    )

    result["pokemon_hit_in_battle"] = get_value_below_label(
        rows, "Pokémon Hit in Battle", start_index
    )

    return result


# --------------------------------------------------
# Additional move properties
# --------------------------------------------------


def extract_move_properties(table):
    """
    Extract additional move properties from the properties table.
    Only known move property labels are accepted.
    """
    properties = {}

    if table is None:
        return properties

    valid_labels = {
        "physical contact",
        "sound-type - details",
        "punch move - details",
        "biting move - details",
        "snatchable",
        "slicing move - details",
        "bullet-type - details",
        "wind move - details",
        "powder move",
        "metronome",
        "affected by gravity",
        "defrosts when used",
        "reflected by magic coat magic bounce",
        "blocked by protect detect",
        "copyable by mirror move",
    }

    rows = get_table_rows(table)

    for index in range(0, len(rows) - 1, 2):
        header_cells = rows[index]
        value_cells = rows[index + 1]

        for cell_index, label in enumerate(header_cells):
            normalized = normalize_label(label)

            if normalized not in valid_labels:
                continue

            if cell_index >= len(value_cells):
                continue

            value = clean_text(value_cells[cell_index])

            properties[clean_text(label)] = value

    return properties



# --------------------------------------------------
# Pokémon that learn the move
# --------------------------------------------------

def collect_standard_learners(soup):
    """
    Collect Pokémon listed in the move's Pokémon table.
    """
    learners = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = get_direct_cells(row)

            if len(cells) < 3:
                continue

            number = clean_text(
                cells[0].get_text(" ", strip=True)
            )

            if not re.fullmatch(r"#\d+", number):
                continue

            pokemon_name = clean_text(
                cells[2].get_text(" ", strip=True)
            )

            if pokemon_name and pokemon_name not in learners:
                learners.append(pokemon_name)

    return learners


# --------------------------------------------------
# Scrape one move
# --------------------------------------------------

def scrape_move_details(move):
    """
    Download and parse one move detail page.
    """
    soup = fetch_page(move["url"])

    if soup is None:
        return None

    main_table = find_detail_table(soup)

    if main_table is None:
        log(f"Could not find main details table: {move['name']}")
        return None

    properties_table = find_properties_table(soup)

    move_name = extract_move_name(
        main_table,
        move["name"]
    )

    stats = extract_main_stats(main_table)
    properties = extract_move_properties(properties_table)
    learners = collect_standard_learners(soup)

    result = {
        "name": move_name,
        "url": move["url"],
        "type": stats["type"],
        "category": stats["category"],
        "pp": stats["pp"],
        "power": stats["power"],
        "accuracy": stats["accuracy"],
        "battle_effect": stats["battle_effect"],
        "in_depth_effect": stats["in_depth_effect"],
        "secondary_effect": stats["secondary_effect"],
        "effect_rate": stats["effect_rate"],
        "critical_hit_rate": stats["critical_hit_rate"],
        "priority": stats["priority"],
        "pokemon_hit_in_battle": stats["pokemon_hit_in_battle"],
        "properties": properties,
        "pokemon_that_learn": learners,
    }

    return result


# --------------------------------------------------
# Build database
# --------------------------------------------------

def build_database():
    moves = get_move_list()

    print(f"Found {len(moves)} moves.")
    print("Downloading move details...")

    database = []
    failed = []

    for move in tqdm(
        moves,
        desc="Scraping moves",
        unit="move",
        disable=DEBUG,
    ):
        log(f"Scraping: {move['name']}")

        try:
            result = scrape_move_details(move)

            if result:
                database.append(result)
            else:
                failed.append(move["name"])

        except Exception as error:
            log(f"Error scraping {move['name']}: {error}")
            failed.append(move["name"])

        time.sleep(REQUEST_DELAY)

    if failed:
        print(f"Failed to scrape {len(failed)} moves.")

        if DEBUG:
            for name in failed:
                print(f"  - {name}")

    return database


# --------------------------------------------------
# Save database
# --------------------------------------------------

def save_database(database):
    if not database:
        print("No moves were scraped. JSON file was not overwritten.")
        return

    with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
        json.dump(
            database,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Saved {len(database)} moves to {OUTPUT_JSON}.")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("Pokémon Champions move scraper")
    print("--------------------------------")

    database = build_database()
    save_database(database)


if __name__ == "__main__":
    main()
