
import json
import re
import time

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from tqdm import tqdm


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_URL = "https://www.vizukan.app"

OUTPUT_FILE = Path("database/rulesets.json")

DEBUG = False
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; PokemonChampionsResearchBot/1.0)"
    )
}

TYPE_NAMES = {
    "Normal", "Fire", "Water", "Electric", "Grass",
    "Ice", "Fighting", "Poison", "Ground", "Flying",
    "Psychic", "Bug", "Rock", "Ghost", "Dragon",
    "Dark", "Steel", "Fairy"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# --------------------------------------------------
# Utilities
# --------------------------------------------------

def debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")


def clean_text(value):
    return re.sub(r"\s+", " ", value).strip()


def get_soup(url):
    response = SESSION.get(url, timeout=30)
    response.raise_for_status()

    return BeautifulSoup(response.text, "lxml")


def find_heading(soup, text):
    """Find a heading by its exact text."""
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        if clean_text(heading.get_text()) == text:
            return heading

    return None


def get_regulation_list():
    """Load the regulation index from the existing rulesets database."""
    if not OUTPUT_FILE.exists():
        raise FileNotFoundError(
            f"Rulesets database not found: {OUTPUT_FILE}. "
            "Create the initial rulesets.json before running this scraper."
        )

    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    regulations = data.get("regulations", [])

    if not isinstance(regulations, list):
        raise ValueError(
            f"Invalid rulesets format in {OUTPUT_FILE}: "
            "'regulations' must be a list."
        )

    valid_regulations = []
    for regulation in regulations:
        if not isinstance(regulation, dict):
            debug(f"Skipping invalid regulation entry: {regulation!r}")
            continue

        if not regulation.get("url"):
            debug(
                "Skipping regulation without URL: "
                f"{regulation.get('name', regulation.get('slug', 'Unknown'))}"
            )
            continue

        valid_regulations.append(regulation)

    return valid_regulations


# --------------------------------------------------
# Overview
# --------------------------------------------------

def scrape_overview(soup):
    heading = soup.find("h1")

    name = (
        clean_text(heading.get_text())
        if heading
        else None
    )

    page_text = clean_text(soup.get_text(" ", strip=True))

    date_match = re.search(
        r"(\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2})"
        r"\s*[–-]\s*"
        r"(\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2})"
        r"\s*[·|]\s*(.+?UTC[+-]\d+)",
        page_text
    )

    dates = {
        "start": None,
        "end": None,
        "timezone": None
    }

    if date_match:
        dates = {
            "start": date_match.group(1),
            "end": date_match.group(2),
            "timezone": date_match.group(3)
        }

    # Read the regulation state from the page badge first.
    # ViZukan currently uses "In effect" for the active regulation and
    # may use "Ended" / "This regulation has ended" for older ones.
    status = "unknown"

    badge_texts = [
        clean_text(element.get_text(" ", strip=True)).casefold()
        for element in soup.select('[data-slot="badge"]')
    ]

    visible_status_text = " ".join(badge_texts) + " " + page_text.casefold()

    if re.search(r"\bin effect\b|\bcurrently active\b", visible_status_text):
        status = "current"
    elif re.search(
        r"\bended\b|\bthis regulation has ended\b|\bprevious regulation\b",
        visible_status_text
    ):
        status = "previous"

    key_facts = {}

    heading = find_heading(soup, "Key facts")

    if heading:
        for item in heading.find_all_next("li"):
            if item.find_previous(["h2", "h3"]) != heading:
                break

            text = clean_text(item.get_text(" ", strip=True))

            if ":" in text:
                key, value = text.split(":", 1)
                key_facts[clean_text(key).lower()] = clean_text(value)
            elif "·" in text:
                key, value = text.split("·", 1)
                key_facts[clean_text(key).lower()] = clean_text(value)

    return {
        "name": name,
        "dates": dates,
        "status": status,
        "key_facts": key_facts
    }


# --------------------------------------------------
# Changes
# --------------------------------------------------

def scrape_changes(soup):
    result = {
        "previous_regulation": None,
        "added": [],
        "removed": []
    }

    heading = soup.find(
        lambda tag: tag.name in ("h2", "h3")
        and clean_text(tag.get_text()).startswith("Changes from")
    )

    if not heading:
        return result

    previous_match = re.search(
        r"Changes from (.+)",
        clean_text(heading.get_text())
    )

    if previous_match:
        result["previous_regulation"] = previous_match.group(1)

    table = heading.find_next("table")

    if not table:
        return result

    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)

        if len(cells) < 5:
            continue

        dex_match = re.search(
            r"#?(\d{1,4})",
            clean_text(cells[0].get_text())
        )

        if not dex_match:
            continue

        pokemon_links = cells[1].find_all("a")

        name = (
            clean_text(pokemon_links[0].get_text())
            if pokemon_links
            else clean_text(cells[1].get_text())
        )

        types = [
            clean_text(link.get_text())
            for link in cells[2].find_all("a")
        ]

        before = clean_text(cells[3].get_text())
        now = clean_text(cells[4].get_text())

        entry = {
            "dex_number": int(dex_match.group(1)),
            "name": name,
            "types": types,
            "before": before,
            "now": now
        }

        if before.lower() == "absent" and now.lower() == "selectable":
            result["added"].append(entry)

        elif now.lower() == "absent":
            result["removed"].append(entry)

    return result


# --------------------------------------------------
# Pokémon
# --------------------------------------------------

def scrape_pokemon_page(soup):
    """Extract selectable Pokémon forms from the current roster page."""
    section = soup.select_one("section#pokemon")
    if section is None:
        debug("Selectable Pokémon section (#pokemon) not found")
        return []

    grid = section.select_one(".pokemon-grid")
    if grid is None:
        debug("Pokémon grid (.pokemon-grid) not found inside #pokemon")
        return []

    pokemon = []

    # Each selectable form is represented by one entity-card.
    for card in grid.select(":scope > .entity-card"):
        dex_element = card.select_one('[data-slot="card-description"]')
        name_link = card.select_one('[data-slot="card-title"] a[href*="/en/pokemon/"]')
        footer = card.select_one('[data-slot="card-footer"]')

        if dex_element is None or name_link is None:
            debug(f"Skipping malformed Pokémon card: {card.get_text(' ', strip=True)}")
            continue

        dex_match = re.search(r"#?\s*(\d{1,4})", dex_element.get_text(" ", strip=True))
        if dex_match is None:
            debug(f"Could not read Dex number for {name_link.get_text(strip=True)}")
            continue

        name = clean_text(name_link.get_text(" ", strip=True))
        types = []
        for type_link in card.select(".type-list a[data-type]"):
            type_name = clean_text(type_link.get("data-type", "")).title()
            if type_name:
                types.append(type_name)

        form_label = clean_text(footer.get_text(" ", strip=True)) if footer else ""
        form_type = "alternate" if form_label.lower() == "alternate form" else "base"

        pokemon.append({
            "dex_number": int(dex_match.group(1)),
            "name": name,
            "types": types,
            "form_type": form_type
        })

    debug(f"Parsed {len(pokemon)} Pokémon cards from .pokemon-grid")
    return pokemon

def get_next_page(soup):
    """Find the actual Next page link."""
    for link in soup.find_all("a", href=True):
        if clean_text(link.get_text(" ", strip=True)) == "Next page":
            return urljoin(BASE_URL, link["href"])

    return None


def get_total_pokemon_forms(soup):
    page_text = clean_text(soup.get_text(" ", strip=True))

    match = re.search(
        r"Showing\s+\d+[-–]\d+\s+of\s+(\d+)\s+Pokémon forms",
        page_text,
        re.IGNORECASE
    )

    return int(match.group(1)) if match else None


def scrape_all_pokemon(url, first_soup):
    """Follow pagination links until the last Pokémon page."""
    all_pokemon = []
    visited_urls = set()

    current_url = url
    current_soup = first_soup

    expected_total = get_total_pokemon_forms(first_soup)

    print(f"  Expected Pokémon forms: {expected_total}")

    page_number = 0

    while current_url and current_url not in visited_urls:
        visited_urls.add(current_url)
        page_number += 1

        if page_number > 1:
            time.sleep(REQUEST_DELAY)
            current_soup = get_soup(current_url)

        page_pokemon = scrape_pokemon_page(current_soup)
        all_pokemon.extend(page_pokemon)

        print(
            f"    Page {page_number}: "
            f"{len(page_pokemon)} Pokémon forms"
        )

        next_url = get_next_page(current_soup)

        if not next_url:
            break

        current_url = next_url

    # Remove duplicates while preserving order.
    unique_pokemon = []
    seen = set()

    for pokemon in all_pokemon:
        key = (
            pokemon["dex_number"],
            pokemon["name"],
            pokemon["form_type"]
        )

        if key not in seen:
            seen.add(key)
            unique_pokemon.append(pokemon)

    if expected_total is not None and len(unique_pokemon) != expected_total:
        print(
            f"  [WARNING] Expected {expected_total}, "
            f"extracted {len(unique_pokemon)}."
        )

    return unique_pokemon


# --------------------------------------------------
# Mega Evolution
# --------------------------------------------------

def scrape_mega_evolutions(soup):
    """Extract Mega Evolution pairs from the dedicated Mega section."""
    section = soup.select_one("section#mega")
    if section is None:
        debug("Mega Evolution section (#mega) not found")
        return []

    mega_forms = []

    for card in section.select(".mega-card"):
        endpoints = card.select("a.mega-endpoint")
        if len(endpoints) != 2:
            debug(f"Skipping malformed Mega card: {card.get_text(' ', strip=True)}")
            continue

        parsed = []
        for endpoint in endpoints:
            caption = endpoint.select_one(".mega-caption")
            name_element = endpoint.select_one(".mega-name")
            if caption is None or name_element is None:
                parsed = []
                break

            caption_text = clean_text(caption.get_text(" ", strip=True)).lower()
            label_text = clean_text(name_element.get_text(" ", strip=True))
            dex_match = re.search(r"#(\d{1,4})", label_text)
            name_match = re.search(r"#\d{1,4}\s*(.+)$", label_text)
            if dex_match is None or name_match is None:
                parsed = []
                break

            parsed.append({
                "kind": caption_text,
                "dex_number": int(dex_match.group(1)),
                "name": clean_text(name_match.group(1))
            })

        if len(parsed) != 2:
            debug(f"Could not parse Mega endpoints: {card.get_text(' ', strip=True)}")
            continue

        base = next((item for item in parsed if item["kind"] == "base form"), None)
        mega = next((item for item in parsed if item["kind"] == "mega form"), None)
        if base is None or mega is None:
            continue

        mega_forms.append({
            "base_pokemon": {
                "dex_number": base["dex_number"],
                "name": base["name"]
            },
            "mega_form": {
                "dex_number": mega["dex_number"],
                "name": mega["name"]
            }
        })

    debug(f"Parsed {len(mega_forms)} Mega Evolution cards")
    return mega_forms


# --------------------------------------------------
# Rules
# --------------------------------------------------

def scrape_rules(soup):
    result = {}

    heading = find_heading(soup, "Rules and conditions")

    if not heading:
        return result

    for subheading in heading.find_all_next(["h3", "h4"]):
        if subheading.find_previous("h2") != heading:
            break

        title = clean_text(subheading.get_text())

        content = []
        element = subheading.find_next_sibling()

        while element:
            if element.name in ("h2", "h3", "h4"):
                break

            if element.name in ("p", "li"):
                text = clean_text(element.get_text(" ", strip=True))

                if text:
                    content.append(text)

            elif element.name == "table":
                for row in element.find_all("tr"):
                    cells = [
                        clean_text(cell.get_text(" ", strip=True))
                        for cell in row.find_all(["th", "td"])
                    ]

                    if cells:
                        content.append({"table_row": cells})

            element = element.find_next_sibling()

        result[title.lower().replace(" ", "_")] = content

    return result


# --------------------------------------------------
# Verification and sources
# --------------------------------------------------

def scrape_verification(soup):
    result = {}

    heading = soup.find(
        lambda tag: tag.name in ("h2", "h3")
        and "How much of this ruleset is verified"
        in clean_text(tag.get_text())
    )

    if not heading:
        return result

    section = heading.find_parent("section") or heading.parent
    text = clean_text(section.get_text(" ", strip=True))

    for label in (
        "Confirmed",
        "Partial information",
        "Cannot confirm"
    ):
        match = re.search(
            rf"{re.escape(label)}\s+(\d+)",
            text
        )

        if match:
            key = label.lower().replace(" ", "_")
            result[key] = int(match.group(1))

    return result


def scrape_sources(soup):
    result = {
        "links": [],
        "checked_on": None,
        "data_releases": []
    }

    heading = find_heading(soup, "Sources")

    if heading:
        section = heading.find_parent("section") or heading.parent

        for link in section.find_all("a", href=True):
            name = clean_text(link.get_text(" ", strip=True))

            if name:
                result["links"].append({
                    "name": name,
                    "url": urljoin(BASE_URL, link["href"])
                })

    page_text = clean_text(soup.get_text(" ", strip=True))

    checked_match = re.search(
        r"Checked on (\d{2}/\d{2}/\d{4})",
        page_text
    )

    if checked_match:
        result["checked_on"] = checked_match.group(1)

    releases_match = re.search(
        r"Data releases used:\s*(.+?)(?:\s+ViZukan|\s+Feedback|$)",
        page_text
    )

    if releases_match:
        result["data_releases"] = [
            clean_text(item)
            for item in releases_match.group(1).split("/")
            if clean_text(item)
        ]

    return result


def scrape_update_history(soup):
    result = []

    heading = find_heading(soup, "Update history")

    if not heading:
        return result

    for item in heading.find_all_next("li"):
        if item.find_previous(["h2", "h3"]) != heading:
            break

        text = clean_text(item.get_text(" ", strip=True))

        if text:
            result.append(text)

    return result


# --------------------------------------------------
# Regulation
# --------------------------------------------------

def scrape_regulation(regulation):
    name = regulation.get("name", regulation.get("slug", "Unknown"))
    url = regulation["url"]

    print(f"\nScraping {name}...")

    soup = get_soup(url)

    overview = scrape_overview(soup)

    # Prefer the status badge on the regulation detail page. Fall back to
    # the regulation index metadata for older/changed page templates.
    raw_status = regulation.get("status")
    if raw_status is None:
        raw_status = regulation.get("label")

    if raw_status is None and isinstance(regulation.get("is_current"), bool):
        raw_status = "current" if regulation["is_current"] else "previous"

    normalized_status = clean_text(str(raw_status or "")).casefold()
    if normalized_status in {"current", "in effect", "active", "current regulation"}:
        index_status = "current"
    elif normalized_status in {"previous", "ended", "past", "previous regulation", "inactive"}:
        index_status = "previous"
    else:
        index_status = "unknown"

    # The page itself is the best source when it exposes a recognizable badge.
    status = overview["status"] if overview["status"] != "unknown" else index_status

    if status == "unknown":
        debug(
            f"Could not determine status for {name}; "
            f"page status={overview['status']!r}, index status={raw_status!r}"
        )

    changes = scrape_changes(soup)

    pokemon = scrape_all_pokemon(url, soup)

    mega_evolutions = scrape_mega_evolutions(soup)

    rules = scrape_rules(soup)

    verification = scrape_verification(soup)

    sources = scrape_sources(soup)

    update_history = scrape_update_history(soup)

    return {
        "name": overview["name"] or name,
        "slug": regulation.get("slug"),
        "url": url,
        "status": status,

        "overview": {
            "dates": overview["dates"],
            "key_facts": overview["key_facts"]
        },

        "changes": changes,

        "pokemon": {
            "total_forms": len(pokemon),
            "selectable_forms": pokemon
        },

        "mega_evolutions": {
            "total": len(mega_evolutions),
            "forms": mega_evolutions
        },

        "rules": rules,

        "verification": verification,

        "sources": sources,

        "update_history": update_history
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("Loading regulation list...")

    regulations = get_regulation_list()

    if not regulations:
        print("No regulations found.")
        return

    print(f"Found {len(regulations)} regulations.")

    results = []
    failed = []

    for regulation in tqdm(
        regulations,
        desc="Scraping regulations",
        unit="regulation"
    ):
        try:
            result = scrape_regulation(regulation)
            results.append(result)

            print(
                f"  Completed: {result['name']} "
                f"({result['pokemon']['total_forms']} Pokémon, "
                f"{result['mega_evolutions']['total']} Mega forms)"
            )

        except Exception as error:
            print(
                f"  [ERROR] Failed to scrape "
                f"{regulation.get('name')}: {error}"
            )

            failed.append({
                "name": regulation.get("name"),
                "url": regulation.get("url"),
                "error": str(error)
            })

        time.sleep(REQUEST_DELAY)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "source": f"{BASE_URL}/en/champions/regulations",
        "regulation_count": len(results),
        "failed_count": len(failed),
        "regulations": results,
        "failed": failed
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nScraping completed.")
    print("--------------------")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(failed)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
