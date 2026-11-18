import sys
import json
import re
import time
import html
import builtins
from collections import OrderedDict
from urllib.parse import urljoin, urldefrag

import requests
from bs4 import BeautifulSoup, NavigableString


# ============================================================
# KONFIGURACJA
# ============================================================

DEBUG = False

ROSTER_URLS = [
    "https://www.serebii.net/pokemonchampions/pokemon.shtml",
    "https://www.serebii.net/pokemonchampions/transferonly.shtml",
]

OUTPUT_JSON = "database/pokemon.json"
OUTPUT_TXT = "pokemon_list.txt"

REQUEST_DELAY = 0.25
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
        "Gecko/20100101 Firefox/128.0"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# DEBUG — CENTRALNA OBSŁUGA KOMUNIKATÓW
# ============================================================

def debug_print(*args, **kwargs):
    """
    Wypisuje komunikaty wyłącznie wtedy, gdy DEBUG = True.
    """

    if DEBUG:
        builtins.print(*args, **kwargs)


# Wszystkie dotychczasowe wywołania print() w skrypcie
# korzystają z debug_print().
print = debug_print


# ============================================================
# PASEK POSTĘPU — AKTYWNY, GDY DEBUG = False
# ============================================================

def show_progress(current, total, start_time, name=""):
    """
    Wyświetla pasek postępu podczas analizowania Pokémonów.

    Pasek jest aktywny wyłącznie wtedy, gdy DEBUG = False.
    Aktualizuje tę samą linię terminala.
    """

    if DEBUG:
        return

    if total <= 0:
        return

    percentage = current / total
    bar_width = 30

    filled = int(bar_width * percentage)
    bar = "█" * filled + "░" * (bar_width - filled)

    elapsed = time.time() - start_time

    if current > 0:
        average_time = elapsed / current
        remaining = average_time * (total - current)
    else:
        remaining = 0

    def format_time(seconds):
        seconds = max(0, int(seconds))

        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            return f"{hours}h {minutes:02d}m"
        if minutes:
            return f"{minutes}m {seconds:02d}s"

        return f"{seconds}s"

    percentage_text = f"{percentage * 100:5.1f}%"

    current_name = normalize(name)

    if len(current_name) > 24:
        current_name = current_name[:21] + "..."

    line = (
        f"\r[{bar}] "
        f"{percentage_text} "
        f"{current}/{total} "
        f"| ETA: {format_time(remaining)} "
        f"| {current_name:<24}"
    )

    sys.stdout.write(line)
    sys.stdout.flush()

    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


# ============================================================
# NORMALIZACJA I POMOCNICZE
# ============================================================

def normalize(value):
    if value is None:
        return ""

    value = html.unescape(str(value))
    value = value.replace("\xa0", " ")
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def unique(items):
    result = []
    seen = set()

    for item in items:
        item = normalize(item)

        if not item:
            continue

        key = item.casefold()

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def fetch_soup(url):
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    return BeautifulSoup(response.text, "lxml")


def get_text(element):
    if element is None:
        return ""

    return normalize(element.get_text(" ", strip=True))


def clean_url(url):
    url = urldefrag(url)[0]
    return url.rstrip("/") + "/"


def get_dex_number(text):
    match = re.search(r"#\s*0*(\d{1,4})", normalize(text))

    if match:
        return int(match.group(1))

    return None


# ============================================================
# ROSTER
# ============================================================

def is_pokemon_detail_link(href):
    if not href:
        return False

    href = href.casefold()

    return (
        "/pokedex-champions/" in href
        or "/pokemonchampions/pokemon/" in href
    )


def get_roster():
    # Zachowana dotychczasowa architektura i deduplikacja.
    roster = OrderedDict()

    for roster_url in ROSTER_URLS:
        print(f"Pobieram roster: {roster_url}")

        soup = fetch_soup(roster_url)

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")

            if not is_pokemon_detail_link(href):
                continue

            pokemon_url = clean_url(urljoin(roster_url, href))
            name = get_text(link)

            if not name:
                continue

            dex_number = None
            parent = link

            for _ in range(5):
                if parent is None:
                    break

                dex_number = get_dex_number(get_text(parent))

                if dex_number is not None:
                    break

                parent = parent.parent

            key = (
                f"dex:{dex_number}"
                if dex_number is not None
                else pokemon_url.casefold()
            )

            if key not in roster:
                roster[key] = {
                    "name": name,
                    "url": pokemon_url,
                    "dex_number": dex_number,
                }

    return list(roster.values())


# ============================================================
# NAGŁÓWKI I ETYKIETY
# ============================================================

HEADING_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6"
}


def heading_text_nodes(soup):
    result = []

    for node in soup.find_all(string=True):
        text = normalize(node)

        if not text:
            continue

        parent = node.parent

        if parent is None:
            continue

        if parent.name in HEADING_TAGS:
            result.append(text)
            continue

        if parent.name in ("b", "strong"):
            if get_text(parent) == text:
                result.append(text)
                continue

        if parent.name in ("td", "th"):
            if len(text) < 100:
                result.append(text)

    return unique(result)


def get_heading_labels(soup, pattern):
    regex = re.compile(pattern, re.I)
    found = []

    for text in heading_text_nodes(soup):
        match = regex.fullmatch(text)

        if not match:
            continue

        label = normalize(match.group(1))

        if label:
            found.append(label)

    return unique(found)


# ============================================================
# ROZPOZNAWANIE KOŃCA SEKCJI
# ============================================================

def is_section_heading(text):
    text = normalize(text)

    patterns = [
        r"^Alternate Forms$",
        r"^Evolutionary Chain$",
        r"^Gender Differences$",
        r"^Standard Moves(?:\s*[-:].*)?$",
        r"^Special Moves(?:\s*[-:].*)?$",
        r"^Stats(?:\s*[-:].*)?$",
        r"^Egg Moves$",
        r"^Weakness$",
        r"^Locations$",
        r"^Damage Taken(?:\s+.*)?$",
        r"^.*\s+Abilities:$",
    ]

    return any(
        re.fullmatch(pattern, text, flags=re.I)
        for pattern in patterns
    )


def find_section_start(soup, section_name):
    target = normalize(section_name).casefold()

    for node in soup.find_all(string=True):
        if normalize(node).casefold() == target:
            return node

    return None


def get_section_images(soup, section_name):
    start_node = find_section_start(soup, section_name)

    if start_node is None:
        return []

    result = []
    started = False

    for element in soup.descendants:
        if element is start_node:
            started = True
            continue

        if not started:
            continue

        if isinstance(element, NavigableString):
            text = normalize(element)

            if text and is_section_heading(text):
                break

        elif getattr(element, "name", None) == "img":
            alt = normalize(element.get("alt", ""))

            if alt:
                result.append(alt)

    return unique(result)


# ============================================================
# ALTERNATE FORMS
# ============================================================

def clean_image_alt(value):
    value = normalize(value)

    value = re.sub(
        r"^image:\s*",
        "",
        value,
        flags=re.I,
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_gender_label(value):
    value = clean_image_alt(value)

    value = re.sub(
        r"\b(sprite|image)\b",
        " ",
        value,
        flags=re.I,
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def extract_alternate_forms(soup, species_name):
    found = []

    labels = get_section_images(soup, "Alternate Forms")

    for label in labels:
        label = clean_image_alt(label)

        if not label:
            continue

        if species_name.casefold() in label.casefold():
            found.append(label)
        else:
            found.append(f"{species_name} {label}")

    # Formy płciowe z sekcji Gender Differences.
    gender_labels = get_section_images(
        soup,
        "Gender Differences",
    )

    for label in gender_labels:
        label = clean_gender_label(label)

        if not label:
            continue

        if label.casefold() not in ("male", "female"):
            continue

        found.append(f"{species_name} {label}")

    return unique(found)


# ============================================================
# NORMALIZACJA NAZW FORM
# ============================================================

REGIONAL_ADJECTIVES = {
    "alolan": "alola",
    "alola": "alola",
    "galarian": "galar",
    "galar": "galar",
    "hisuian": "hisui",
    "hisui": "hisui",
    "paldean": "paldea",
    "paldea": "paldea",
    "unovan": "unova",
    "unova": "unova",
    "johtonian": "johto",
    "johto": "johto",
    "kantonian": "kanto",
    "kanto": "kanto",
    "kalosian": "kalos",
    "kalos": "kalos",
}


def form_key(value, species_name):
    value = normalize(value).casefold()
    species = normalize(species_name).casefold()

    value = re.sub(
        rf"\b{re.escape(species)}\b",
        " ",
        value,
        flags=re.I,
    )

    for adjective, region in REGIONAL_ADJECTIVES.items():
        value = re.sub(
            rf"\b{adjective}\b",
            region,
            value,
        )

    value = re.sub(
        r"\b(forms?|forme|form)\b",
        " ",
        value,
    )

    value = re.sub(
        r"\bflower\b",
        " ",
        value,
    )

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return normalize(value)


def form_matches(label, form_name, species_name):
    label_key = form_key(label, species_name)
    form_key_value = form_key(form_name, species_name)

    if not label_key or not form_key_value:
        return False

    if label_key == form_key_value:
        return True

    label_tokens = set(label_key.split())
    form_tokens = set(form_key_value.split())

    if not label_tokens or not form_tokens:
        return False

    if form_tokens.issubset(label_tokens):
        return True

    if label_tokens.issubset(form_tokens):
        return True

    return False


def label_matches_any_form(label, alternate_forms, species_name):
    return any(
        form_matches(label, form, species_name)
        for form in alternate_forms
    )


def resolve_form_label(
    label,
    species_name,
    forms,
    base_label,
):
    """
    Przypisuje etykietę ze strony Serebii do konkretnej formy.

    Normal / Base / nazwa gatunku oznaczają formę bazową.
    Pozostałe etykiety są dopasowywane do listy form.
    """

    label = normalize(label)

    if not label:
        return None

    key = form_key(label, species_name)

    if key in ("normal", "base", "default"):
        return base_label

    if label.casefold() == species_name.casefold():
        return base_label

    for form in forms:
        if form_matches(label, form, species_name):
            return form

    if form_matches(label, base_label, species_name):
        return base_label

    return None


# ============================================================
# EVOLUTIONARY CHAIN / MEGA
# ============================================================

def extract_evolutionary_forms(soup, species_name):
    found = []

    mega_pattern = re.compile(
        rf"^Mega\s+{re.escape(species_name)}"
        rf"(?:\s+[A-Z])?$",
        flags=re.I,
    )

    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6"]
    ):
        heading_text = get_text(heading)

        if mega_pattern.fullmatch(heading_text):
            found.append(heading_text)

    evo_table = soup.find("table", class_="evochain")

    if evo_table is not None:
        mega_names_by_sprite = {}

        for heading in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6"]
        ):
            heading_text = get_text(heading)

            if not re.match(
                r"^Mega\s+",
                heading_text,
                flags=re.I,
            ):
                continue

            section_table = heading.find_parent("table")

            if section_table is not None:
                images = section_table.find_all("img", src=True)
            else:
                images = []

            for image in images:
                src = image.get("src", "").split("?", 1)[0]

                if "/pokemon/" not in src.casefold():
                    continue

                filename = src.rsplit("/", 1)[-1].casefold()
                mega_names_by_sprite[filename] = heading_text

        mega_icons = evo_table.find_all(
            "img",
            src=re.compile(r"mega", re.I),
        )

        for mega_icon in mega_icons:
            icon_src = mega_icon.get("src", "")

            if not re.search(
                r"/evoicon/mega",
                icon_src,
                flags=re.I,
            ):
                continue

            target_cell = None

            for candidate in mega_icon.find_all_next(
                "td",
                class_="pkmn",
            ):
                if candidate.find_parent("table") is not evo_table:
                    continue

                target_cell = candidate
                break

            if target_cell is None:
                continue

            target_image = target_cell.find("img", src=True)

            if target_image is None:
                continue

            target_src = target_image.get("src", "").split("?", 1)[0]
            filename = target_src.rsplit("/", 1)[-1]
            filename_key = filename.casefold()

            mega_name = mega_names_by_sprite.get(filename_key)

            if not mega_name:
                stem = filename.rsplit(".", 1)[0]

                match = re.search(
                    r"-m([a-z]*)$",
                    stem,
                    flags=re.I,
                )

                if not match:
                    continue

                suffix = match.group(1).upper()
                mega_name = f"Mega {species_name}"

                if suffix:
                    mega_name += f" {suffix}"

            found.append(mega_name)

    found = unique(found)

    for mega_name in found:
        print(f"  Mega wykryte: {mega_name}")

    return found


def is_mega_form(form_name):
    return bool(
        re.search(
            r"\bmega\b",
            normalize(form_name),
            flags=re.I,
        )
    )


# ============================================================
# TYPES — WYKRYWANIE FORM
# ============================================================

def extract_type_forms(soup, species_name, alternate_forms):
    found = []

    normal_types = {
        "normal", "fire", "water", "electric",
        "grass", "ice", "fighting", "poison",
        "ground", "flying", "psychic", "bug",
        "rock", "ghost", "dragon", "dark",
        "steel", "fairy",
    }

    for table in soup.find_all("table"):
        rows = table.find_all("tr")

        for row_index, row in enumerate(rows):
            cells = row.find_all(
                ["td", "th"],
                recursive=False,
            )

            if not cells:
                continue

            headers = [
                normalize(get_text(cell)).casefold()
                for cell in cells
            ]

            if "type" not in headers:
                continue

            type_index = headers.index("type")

            for data_row in rows[row_index + 1:]:
                data_cells = data_row.find_all(
                    ["td", "th"],
                    recursive=False,
                )

                if len(data_cells) <= type_index:
                    continue

                value = get_text(data_cells[type_index])

                if not value:
                    continue

                if value.casefold() in normal_types:
                    continue

                if label_matches_any_form(
                    value,
                    alternate_forms,
                    species_name,
                ):
                    found.append(value)

    for node in soup.find_all(string=True):
        text = normalize(node)

        match = re.fullmatch(
            r"(.+?)\s+Type",
            text,
            flags=re.I,
        )

        if not match:
            continue

        label = normalize(match.group(1))

        if not label or label.casefold() in normal_types:
            continue

        if label_matches_any_form(
            label,
            alternate_forms,
            species_name,
        ):
            found.append(label)

    for node in soup.find_all(string=True):
        text = normalize(node)

        match = re.fullmatch(
            r"Damage Taken\s+(.+)",
            text,
            flags=re.I,
        )

        if not match:
            continue

        label = normalize(match.group(1))

        if label_matches_any_form(
            label,
            alternate_forms,
            species_name,
        ):
            found.append(label)

    return unique(found)


# ============================================================
# ABILITIES — WYKRYWANIE FORM
# ============================================================

def extract_ability_forms(soup, species_name, alternate_forms):
    found = []

    labels = get_heading_labels(
        soup,
        r"(.+?)\s+Abilities:",
    )

    for label in labels:
        if label.casefold() == species_name.casefold():
            continue

        if label_matches_any_form(
            label,
            alternate_forms,
            species_name,
        ):
            found.append(label)

    for node in soup.find_all(string=True):
        text = normalize(node)

        if not re.match(
            r"^Abilities\s*:",
            text,
            flags=re.I,
        ):
            continue

        parent = node.parent

        if parent is None:
            continue

        for container in (parent, parent.parent):
            if container is None:
                continue

            container_text = get_text(container)

            if not re.match(
                r"^Abilities\s*:",
                container_text,
                flags=re.I,
            ):
                continue

            for match in re.finditer(
                r"\(([^()]{1,80})\)",
                container_text,
            ):
                label = normalize(match.group(1))

                if not label:
                    continue

                if label.casefold() == species_name.casefold():
                    continue

                if label_matches_any_form(
                    label,
                    alternate_forms,
                    species_name,
                ):
                    found.append(label)

            break

    return unique(found)


# ============================================================
# STANDARD MOVES — WYKRYWANIE FORM
# ============================================================

def extract_standard_moves_forms(soup, species_name, alternate_forms):
    found = []

    patterns = [
        r"Standard Moves\s*[-:]\s*(.+)",
        r"(.+?)\s+Standard Moves",
    ]

    for pattern in patterns:
        labels = get_heading_labels(soup, pattern)

        for label in labels:
            label = normalize(label)

            if not label:
                continue

            if label.casefold() == species_name.casefold():
                continue

            if label_matches_any_form(
                label,
                alternate_forms,
                species_name,
            ):
                found.append(label)

    return unique(found)


# ============================================================
# STATS — WYKRYWANIE FORM
# ============================================================

def extract_stats_forms(soup, species_name, alternate_forms):
    found = []

    labels = get_heading_labels(
        soup,
        r"Stats\s*[-:]\s*(.+)",
    )

    for label in labels:
        label = normalize(label)

        if not label:
            continue

        if label.casefold() in (
            "alternate forms",
            "alternate form",
        ):
            continue

        if label.casefold() == species_name.casefold():
            continue

        if label_matches_any_form(
            label,
            alternate_forms,
            species_name,
        ):
            found.append(label)

    return unique(found)


# ============================================================
# DOWODY RÓŻNIC MECHANICZNYCH
# ============================================================

def find_evidence_for_form(
    form_name,
    species_name,
    type_forms,
    stats_forms,
    ability_forms,
    standard_move_forms,
):
    evidence = []

    sources = [
        ("Types", type_forms),
        ("Abilities", ability_forms),
        ("Stats", stats_forms),
        ("Standard Moves", standard_move_forms),
    ]

    for source_name, labels in sources:
        for label in labels:
            if form_matches(
                label,
                form_name,
                species_name,
            ):
                evidence.append(source_name)
                break

    return evidence


# ============================================================
# POMOCNICZE DO EKSTRAKCJI DANYCH
# ============================================================

def get_heading_section_table(heading):
    """
    Znajduje tabelę zawierającą dane bezpośrednio po nagłówku.
    """
    heading_row = heading.find_parent("tr")

    if heading_row is not None:
        table = heading_row.find_parent("table")

        if table is not None:
            return table

    return heading.find_next("table")


def get_heading_rows(heading):
    """
    Zwraca wiersze tabeli następujące po wierszu nagłówka.
    """
    heading_row = heading.find_parent("tr")

    if heading_row is None:
        return []

    table = heading_row.find_parent("table")

    if table is None:
        return []

    rows = table.find_all("tr", recursive=False)

    try:
        start = rows.index(heading_row)
    except ValueError:
        return []

    return rows[start + 1:]


def get_stat_numbers(row):
    """
    Wyciąga sześć wartości z wiersza Base Stats - Total.
    Nie pobiera Max Stats.
    """
    cells = row.find_all(["td", "th"], recursive=False)

    values = []

    for cell in cells:
        text = get_text(cell)

        if re.fullmatch(r"\d+", text):
            values.append(int(text))

    if len(values) < 6:
        return None

    values = values[-6:]

    return {
        "hp": values[0],
        "attack": values[1],
        "defense": values[2],
        "special_attack": values[3],
        "special_defense": values[4],
        "speed": values[5],
    }


# ============================================================
# STATYSTYKI BAZOWE
# ============================================================

def extract_base_stats(soup, species_name, forms, base_label):
    """
    Zwraca statystyki bazowe dla form.

    Formy płciowe bez własnego bloku Stats
    dziedziczą statystyki formy bazowej.
    """

    result = {}

    headings = soup.find_all(list(HEADING_TAGS))

    for heading in headings:
        label = get_text(heading)

        if not re.fullmatch(
            r"Stats(?:\s*[-:].*)?",
            label,
            flags=re.I,
        ):
            continue

        if label.casefold() == "stats":
            target = base_label

        else:
            suffix = re.sub(
                r"^Stats\s*[-:]\s*",
                "",
                label,
                flags=re.I,
            ).strip()

            if suffix.casefold() == "alternate forms":
                stats = None

                for row in get_heading_rows(heading):
                    if "Base Stats - Total" in get_text(row):
                        stats = get_stat_numbers(row)
                        break

                if stats:
                    for form in forms:
                        if not is_mega_form(form):
                            result.setdefault(form, dict(stats))

                continue

            target = None

            if suffix:
                target = resolve_form_label(
                    suffix,
                    species_name,
                    forms,
                    base_label,
                )

            else:
                previous_heading = heading.find_previous(
                    list(HEADING_TAGS)
                )

                if (
                    previous_heading is not None
                    and is_mega_form(get_text(previous_heading))
                ):
                    target = resolve_form_label(
                        get_text(previous_heading),
                        species_name,
                        forms,
                        base_label,
                    )

        if target is None:
            continue

        for row in get_heading_rows(heading):
            if "Base Stats - Total" not in get_text(row):
                continue

            stats = get_stat_numbers(row)

            if stats:
                result[target] = stats

            break

    # --------------------------------------------------------
    # DZIEDZICZENIE STATYSTYK PRZEZ FORMY PŁCIOWE
    # --------------------------------------------------------

    base_stats = result.get(base_label)

    if base_stats:
        for form in forms:
            gender = form_key(form, species_name)

            if gender not in ("male", "female"):
                continue

            if form not in result:
                result[form] = dict(base_stats)

    return result


# ============================================================
# TYPY DLA KAŻDEJ FORMY
# ============================================================

POKEMON_TYPES = {
    "Normal", "Fire", "Water", "Electric",
    "Grass", "Ice", "Fighting", "Poison",
    "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark",
    "Steel", "Fairy",
}


def extract_type_names(element):
    """
    Wyciąga typy z ikon Serebii.
    Sprawdza alt, a jeśli go nie ma — nazwę pliku w src.
    """

    result = []

    if element is None:
        return result

    type_names = "|".join(
        re.escape(name)
        for name in POKEMON_TYPES
    )

    for image in element.find_all("img"):
        alt = normalize(image.get("alt", ""))

        match = re.search(
            rf"\b({type_names})-type\b",
            alt,
            flags=re.I,
        )

        type_name = match.group(1).title() if match else None

        if not type_name:
            src = image.get("src", "")
            filename = src.split("?", 1)[0].rsplit("/", 1)[-1]

            match = re.fullmatch(
                rf"({type_names})\.(?:gif|png)",
                filename,
                flags=re.I,
            )

            if match:
                type_name = match.group(1).title()

        if type_name and type_name in POKEMON_TYPES:
            result.append(type_name)

    return unique(result)


def find_type_cell(soup):
    """
    Znajduje komórkę z typami w głównej tabeli Pokémona.

    W tabeli Serebii nagłówek Type wskazuje indeks kolumny.
    Dane znajdują się w tym samym indeksie w następnym wierszu.
    """

    for table in soup.find_all("table"):
        rows = table.find_all("tr", recursive=False)

        if not rows:
            rows = table.find_all("tr")

        for row_index, row in enumerate(rows):
            cells = row.find_all(
                ["td", "th"],
                recursive=False,
            )

            headers = [
                get_text(cell).strip(":").casefold()
                for cell in cells
            ]

            if "type" not in headers:
                continue

            type_index = headers.index("type")

            # Szukamy pierwszego wiersza danych po nagłówku.
            for data_row in rows[row_index + 1:]:
                data_cells = data_row.find_all(
                    ["td", "th"],
                    recursive=False,
                )

                if len(data_cells) <= type_index:
                    continue

                candidate = data_cells[type_index]

                # Pomijamy puste komórki i kolejne nagłówki.
                if not candidate.find("img") and not candidate.find("table"):
                    continue

                return candidate

    return None


def extract_types_from_cell(
    type_cell,
    species_name,
    forms,
    base_label,
):
    """
    Odczytuje typy z pojedynczej komórki.

    Jeżeli komórka zawiera tabelę form:
        nazwa formy | ikony typów

    przypisuje typy osobno do każdej formy.

    Jeżeli nie zawiera tabeli form, zwraca jeden zestaw
    typów, który będzie wspólny dla wszystkich form.
    """

    result = {}

    if type_cell is None:
        return result

    nested_tables = type_cell.find_all("table")

    # --------------------------------------------------------
    # JEDEN ZESTAW TYPÓW
    # --------------------------------------------------------

    if not nested_tables:
        types = extract_type_names(type_cell)

        if types:
            result[base_label] = types

        return result

    # --------------------------------------------------------
    # OSOBNE ZESTAWY TYPÓW DLA FORM
    # --------------------------------------------------------

    for nested_table in nested_tables:
        for row in nested_table.find_all("tr"):
            cells = row.find_all(
                ["td", "th"],
                recursive=False,
            )

            if len(cells) < 2:
                continue

            form_label = get_text(cells[0])

            if not form_label:
                continue

            row_types = []

            for cell in cells[1:]:
                row_types.extend(
                    extract_type_names(cell)
                )

            row_types = unique(row_types)

            if not row_types:
                continue

            target = resolve_form_label(
                form_label,
                species_name,
                forms,
                base_label,
            )

            if target is None:
                continue

            result[target] = row_types

    return result


def extract_mega_type_cells(soup, species_name, forms, base_label):
    mega_types = {}

    for heading in soup.find_all(HEADING_TAGS):
        heading_text = get_text(heading)

        if not is_mega_form(heading_text):
            continue

        # Szukamy tabeli z kolumną Type należącej
        # do konkretnej sekcji Mega.
        for table in heading.find_all_next("table"):

            # Nie przechodzimy do kolejnej sekcji.
            next_heading = table.find_previous(
                HEADING_TAGS
            )

            if next_heading is not None and next_heading != heading:
                break

            header_row = None
            type_column_index = None

            for row in table.find_all("tr", recursive=False):
                cells = row.find_all(
                    ["td", "th"],
                    recursive=False
                )

                for index, cell in enumerate(cells):
                    if get_text(cell).strip().lower() == "type":
                        header_row = row
                        type_column_index = index
                        break

                if header_row is not None:
                    break

            if header_row is None:
                continue

            # Komórka z typami znajduje się w tym samym
            # indeksie kolumny w następnym wierszu.
            data_row = header_row.find_next_sibling("tr")

            if data_row is None:
                continue

            data_cells = data_row.find_all(
                ["td", "th"],
                recursive=False
            )

            if type_column_index >= len(data_cells):
                continue

            type_cell = data_cells[type_column_index]

            types = extract_types_from_cell(
                type_cell,
                species_name,
                forms,
                base_label
            )

            if types:
                form_label = resolve_form_label(
                    heading_text,
                    species_name,
                    forms,
                    base_label
                )

                mega_types[form_label] = types
                break

    return mega_types


def find_type_cell_in_table(table):
    """
    Szuka komórki Type w konkretnej tabeli.
    Wykorzystywane do odczytywania typów Mega Ewolucji.
    """

    rows = table.find_all("tr", recursive=False)

    if not rows:
        rows = table.find_all("tr")

    for row_index, row in enumerate(rows):
        cells = row.find_all(
            ["td", "th"],
            recursive=False,
        )

        labels = [
            get_text(cell).strip(":").casefold()
            for cell in cells
        ]

        if "type" not in labels:
            continue

        type_index = labels.index("type")

        for data_row in rows[row_index + 1:]:
            data_cells = data_row.find_all(
                ["td", "th"],
                recursive=False,
            )

            if len(data_cells) <= type_index:
                continue

            candidate = data_cells[type_index]

            if candidate.find("img") or candidate.find("table"):
                return candidate

    return None


def extract_types(soup, species_name, forms, base_label):
    """
    Typy dla form Pokémona.

    Zasady:
    1. Jeden zestaw typów w tabeli głównej oznacza,
       że wszystkie formy mają te same typy.
    2. Kilka wierszy w tabeli oznacza osobne typy
       dla wskazanych form.
    3. Formy bez osobnego wpisu dziedziczą typy bazowe.
    4. Mega Ewolucje mogą mieć własny zestaw typów
       w sekcji swojej ewolucji.
    """

    result = {}

    # --------------------------------------------------------
    # GŁÓWNA TABELA POKÉMONA
    # --------------------------------------------------------

    type_cell = find_type_cell(soup)

    if type_cell is not None:
        main_types = extract_types_from_cell(
            type_cell,
            species_name,
            forms,
            base_label,
        )

        result.update(main_types)

    # --------------------------------------------------------
    # TYPY MEGA EWOLUCJI
    # --------------------------------------------------------

    mega_types = extract_mega_type_cells(
        soup,
        species_name,
        forms,
        base_label,
    )

    # Typy z sekcji Mega mają pierwszeństwo
    # przed typami odziedziczonymi z tabeli głównej.
    result.update(mega_types)

    # --------------------------------------------------------
    # DZIEDZICZENIE TYPÓW
    # --------------------------------------------------------

    base_types = result.get(base_label, [])

    for form in forms:
        if form not in result:
            result[form] = list(base_types)

    return result


# ============================================================
# UMIEJĘTNOŚCI — SAME NAZWY
# ============================================================

def get_main_abilities_cell(soup):
    """
    Zachowana funkcja pomocnicza.
    Zwraca pierwszą główną komórkę Abilities.
    """

    for cell in soup.find_all("td", class_="fooleft"):
        bold = cell.find(["b", "strong"])

        if bold and re.search(
            r"\bAbilities\b",
            get_text(bold),
            flags=re.I,
        ):
            return cell

    return None


def get_ability_links(cell):
    """
    Zwraca wyłącznie linki prowadzące do stron abilities.
    Odrzuca np. linki do ruchów takich jak Psychic Terrain.
    """

    if cell is None:
        return []

    result = []

    for link in cell.find_all("a", href=True):
        href = link.get("href", "").casefold()

        if "ability" not in href:
            continue

        name = get_text(link)

        if name:
            result.append(link)

    return result


def extract_main_ability_names(cell):
    return unique([
        get_text(link)
        for link in get_ability_links(cell)
    ])


def get_ability_block_label(cell):
    """
    Zwraca etykietę z pogrubionego fragmentu komórki,
    np.:
        Abilities:
        Female Abilities:
        Alola Form Abilities:
    """

    bold = cell.find(["b", "strong"])

    if bold:
        label = get_text(bold)

        if re.search(r"\bAbilities\b", label, flags=re.I):
            return label

    text = get_text(cell)

    match = re.search(
        r"([A-Za-z ]*Abilities)\s*:",
        text,
        flags=re.I,
    )

    if match:
        return match.group(0)

    return ""


def get_ability_annotation(link):
    """
    Odczytuje adnotację bezpośrednio po linku.

    Przykłady:
        Psychic Surge (Male Hidden Ability)
        Competitive (Female Hidden Ability)

    Zwraca wyłącznie tekst w nawiasie.
    """

    if link is None:
        return ""

    parts = []

    for sibling in link.next_siblings:
        if getattr(sibling, "name", None) == "a":
            break

        if isinstance(sibling, NavigableString):
            parts.append(str(sibling))
        else:
            parts.append(get_text(sibling))

    remainder = normalize(" ".join(parts))

    match = re.search(
        r"\(([^()]*)\)",
        remainder,
    )

    if match:
        return normalize(match.group(1))

    return ""


def ability_annotation_target(
    annotation,
    species_name,
    forms,
    base_label,
):
    """
    Rozpoznaje formę na podstawie adnotacji umiejętności.
    """

    annotation = normalize(annotation)

    if not annotation:
        return None

    return resolve_form_label(
        annotation,
        species_name,
        forms,
        base_label,
    )


def extract_ability_cells(soup):
    """
    Zbiera wszystkie komórki zawierające bloki Abilities.

    Dzięki temu nie pomijamy bloków znajdujących się
    w sekcjach Mega ani osobnych list form.
    """

    result = []
    seen = set()

    for cell in soup.find_all(["td", "th"]):
        label = get_ability_block_label(cell)

        if not label:
            continue

        if id(cell) in seen:
            continue

        seen.add(id(cell))

        result.append({
            "cell": cell,
            "label": label,
        })

    return result


def get_ability_context(cell):
    """
    Ustala kontekst sekcji, w której znajduje się blok umiejętności.

    Jeżeli blok znajduje się pod nagłówkiem Mega,
    zwraca nazwę tej formy Mega.
    """

    heading = cell.find_previous(list(HEADING_TAGS))

    if heading is None:
        return ""

    heading_text = get_text(heading)

    if is_mega_form(heading_text):
        return heading_text

    return ""


def extract_separate_ability_lists(
    soup,
    species_name,
    forms,
    base_label,
):
    """
    Odczytuje osobne listy abilities z komórek opisowych.

    Ważne:
    - pobiera linki dopiero PO nagłówku formy,
    - ignoruje abilities opisane przed tym nagłówkiem,
    - nie łączy list różnych form.
    """

    result = {}

    for block in extract_ability_cells(soup):
        cell = block["cell"]
        label = block["label"]

        label_without_colon = normalize(
            re.sub(r":\s*$", "", label)
        )

        if label_without_colon.casefold() == "abilities":
            continue

        prefix = re.sub(
            r"\s+Abilities$",
            "",
            label_without_colon,
            flags=re.I,
        ).strip()

        target = resolve_form_label(
            prefix,
            species_name,
            forms,
            base_label,
        )

        if target is None:
            continue

        # Znajdź rzeczywisty element nagłówka,
        # np. <b>Female Abilities</b>.
        heading = None

        for bold in cell.find_all(["b", "strong"]):
            bold_text = normalize(get_text(bold))

            if re.search(
                r"\bAbilities\b",
                bold_text,
                flags=re.I,
            ):
                heading = bold
                break

        # Bez rzeczywistego nagłówka nie próbujemy
        # wyciągać listy z całej komórki.
        if heading is None:
            continue

        # Zbieramy wyłącznie linki znajdujące się
        # za nagłówkiem, a nie przed nim.
        names = []
        after_heading = False

        for element in cell.descendants:

            if element is heading:
                after_heading = True
                continue

            if not after_heading:
                continue

            if getattr(element, "name", None) != "a":
                continue

            href = element.get("href", "").casefold()

            if "ability" not in href:
                continue

            name = get_text(element)

            if name:
                names.append(name)

        if names:
            # Pełna lista zastępuje poprzednią listę formy.
            result[target] = unique(names)

    return result


def extract_annotated_ability_lists(
    main_cell,
    species_name,
    forms,
    base_label,
):
    """
    Każda grupa abilities zakończona adnotacją należy
    w całości do wskazanej formy.

    Przykład:
        Ability A - Ability B (Raichu)
        Ability C (Alola Form)

    oznacza:
        forma bazowa: Ability A, Ability B
        Alola: Ability C

    Nie ma dziedziczenia ani współdzielenia abilities
    pomiędzy grupami.
    """

    result = {}

    if main_cell is None:
        return result

    pending = []

    for element in main_cell.descendants:

        # Link do konkretnej umiejętności.
        if getattr(element, "name", None) == "a":
            href = element.get("href", "").casefold()

            if "ability" in href:
                name = get_text(element)

                if name:
                    pending.append(name)

            continue

        # Szukamy adnotacji poza linkami abilities.
        if isinstance(element, NavigableString):

            if element.find_parent("a") is not None:
                continue

            text = normalize(element)

            if not text:
                continue

            annotations = re.findall(
                r"\(([^()]*)\)",
                text,
            )

            for annotation in annotations:

                if not pending:
                    continue

                target = resolve_form_label(
                    annotation,
                    species_name,
                    forms,
                    base_label,
                )

                if target is None:
                    target = base_label

                result.setdefault(target, []).extend(
                    pending
                )

                pending = []

    # Jeśli pozostała grupa bez adnotacji,
    # przypisujemy ją do formy bazowej.
    if pending:
        result.setdefault(base_label, []).extend(
            pending
        )

    return {
        key: unique(value)
        for key, value in result.items()
    }


def extract_abilities(
    soup,
    species_name,
    forms,
    base_label,
):
    """
    Zwraca nazwy abilities dla poszczególnych form.

    Jeżeli strona zawiera adnotacje form:
    - każda grupa jest kompletną listą danej formy,
    - abilities nie są współdzielone,
    - nie ma dziedziczenia listy bazowej.

    Jeżeli adnotacji nie ma, zachowujemy dotychczasowe
    dziedziczenie dla zwykłych Pokémonów.

    Osobne bloki Mega nadal zastępują swoje listy.
    """

    result = {}

    main_cell = get_main_abilities_cell(soup)

    base_abilities = extract_main_ability_names(
        main_cell
    )

    # --------------------------------------------------------
    # GRUPY Z ADNOTACJAMI FORM
    # --------------------------------------------------------

    annotated = extract_annotated_ability_lists(
        main_cell,
        species_name,
        forms,
        base_label,
    )

    has_separate_form_groups = any(
        form != base_label
        for form in annotated
    )

    if has_separate_form_groups:

        # Każda forma otrzymuje wyłącznie własną listę.
        result = {
            form: list(annotated.get(form, []))
            for form in unique([base_label] + list(forms))
        }

    else:

        # Dotychczasowe zachowanie dla zwykłych przypadków.
        result[base_label] = list(base_abilities)

        for form in forms:
            result[form] = list(base_abilities)

        for form, names in annotated.items():
            result[form] = unique(names)

    # --------------------------------------------------------
    # OSOBNE LISTY FORM
    # --------------------------------------------------------

    separate = extract_separate_ability_lists(
        soup,
        species_name,
        forms,
        base_label,
    )

    for form, names in separate.items():
        result[form] = unique(names)

    # --------------------------------------------------------
    # BLOKI ABILITIES W SEKCJACH MEGA
    # --------------------------------------------------------

    for block in extract_ability_cells(soup):
        cell = block["cell"]
        label = normalize(block["label"])

        if label.casefold().replace(":", "").strip() != "abilities":
            continue

        context = get_ability_context(cell)

        if not context:
            continue

        target = resolve_form_label(
            context,
            species_name,
            forms,
            base_label,
        )

        if target is None or not is_mega_form(target):
            continue

        names = [
            get_text(link)
            for link in get_ability_links(cell)
        ]

        if names:
            result[target] = unique(names)

    # --------------------------------------------------------
    # BRAKUJĄCE FORMY
    # --------------------------------------------------------

    for form in forms:
        result.setdefault(
            form,
            [] if has_separate_form_groups
            else list(result.get(base_label, base_abilities)),
        )

    return {
        key: unique(value)
        for key, value in result.items()
    }


# ============================================================
# RUCHY — SAME NAZWY
# ============================================================

def parse_move_names_from_rows(rows):
    """
    Pobiera nazwy ruchów z wierszy tabeli.
    Nie pobiera typów, mocy, celności, PP ani opisów.
    """

    result = []

    for row in rows:
        cells = row.find_all(
            ["td", "th"],
            recursive=False,
        )

        if not cells:
            continue

        # Nazwa ruchu jest linkiem w pierwszej komórce.
        link = cells[0].find("a")

        if link is None:
            continue

        name = get_text(link)

        if name:
            result.append(name)

    return unique(result)


def extract_standard_move_tables(
    soup,
    species_name,
    forms,
    base_label,
):
    """
    Zwraca listy Standard Moves dla poszczególnych form.

    Standard Moves - Female zastępuje Standard Moves.
    Alola Form Standard Moves zastępuje Standard Moves.
    Jeśli forma nie ma własnej tabeli, dziedziczy bazową.
    """

    result = {}

    headings = soup.find_all(list(HEADING_TAGS))

    for heading in headings:
        label = get_text(heading)

        if not re.search(r"Standard Moves", label, re.I):
            continue

        target = None

        if label.casefold() == "standard moves":
            target = base_label
        else:
            for form in forms:
                if form_matches(
                    label,
                    form,
                    species_name,
                ):
                    target = form
                    break

            # Alternatywna kolejność nazwy:
            # Alola Form Standard Moves.
            if target is None:
                match = re.match(
                    r"(.+?)\s+Standard Moves",
                    label,
                    flags=re.I,
                )

                if match:
                    suffix = normalize(match.group(1))

                    target = resolve_form_label(
                        suffix,
                        species_name,
                        forms,
                        base_label,
                    )

        if target is None:
            continue

        rows = get_heading_rows(heading)
        names = parse_move_names_from_rows(rows)

        if names:
            result[target] = names

    return result


def extract_special_moves(
    soup,
    species_name,
    forms,
    base_label,
):
    """
    Special Moves są dodatkiem do Standard Moves.

    Forma może być określona:
    - przez alt obrazka w wierszu ruchu,
    - przez tekst "Form Name Only" w następnym wierszu.
    """

    result = {}

    for cell in soup.find_all("td", class_="fooevo"):
        if get_text(cell).casefold() != "special moves":
            continue

        heading_row = cell.find_parent("tr")

        if heading_row is None:
            continue

        table = heading_row.find_parent("table")

        if table is None:
            continue

        rows = table.find_all("tr")

        try:
            start = rows.index(heading_row)
        except ValueError:
            continue

        for index in range(start + 1, len(rows)):
            row = rows[index]

            # Kolejny nagłówek sekcji kończy Special Moves.
            section_cell = row.find(
                "td",
                class_="fooevo",
            )

            if section_cell is not None:
                if get_text(section_cell).casefold() != "special moves":
                    break

            cells = row.find_all(
                ["td", "th"],
                recursive=False,
            )

            if not cells:
                continue

            link = cells[0].find("a")

            if link is None:
                continue

            move_name = get_text(link)

            if not move_name:
                continue

            target = None

            # 1. Forma z alt obrazka w tym samym wierszu.
            for form_cell in reversed(cells[1:]):
                for img in form_cell.find_all("img"):
                    form_label = normalize(
                        img.get("alt", "")
                    )

                    if not form_label:
                        continue

                    candidate = resolve_form_label(
                        form_label,
                        species_name,
                        forms,
                        base_label,
                    )

                    if candidate is not None:
                        target = candidate
                        break

                if target is not None:
                    break

            # 2. Forma z tekstu w następnym wierszu,
            # np. "Heat Rotom Only".
            if target is None and index + 1 < len(rows):
                next_cells = rows[index + 1].find_all(
                    ["td", "th"],
                    recursive=False,
                )

                for form_cell in reversed(next_cells):
                    form_label = get_text(form_cell)

                    if not re.search(
                        r"\bOnly$",
                        form_label,
                        flags=re.I,
                    ):
                        continue

                    form_label = re.sub(
                        r"\s+Only$",
                        "",
                        form_label,
                        flags=re.I,
                    ).strip()

                    candidate = resolve_form_label(
                        form_label,
                        species_name,
                        forms,
                        base_label,
                    )

                    if candidate is not None:
                        target = candidate
                        break

            if target is None:
                continue

            result.setdefault(target, []).append(move_name)

    return {
        key: unique(value)
        for key, value in result.items()
    }


def extract_moves(
    soup,
    species_name,
    forms,
    base_label,
):
    """
    Łączy Standard Moves i Special Moves.

    Osobna tabela Standard Moves zastępuje listę bazową.
    Special Moves są dopisywane do listy konkretnej formy.
    """

    standard = extract_standard_move_tables(
        soup,
        species_name,
        forms,
        base_label,
    )

    special = extract_special_moves(
        soup,
        species_name,
        forms,
        base_label,
    )

    base_moves = standard.get(base_label, [])

    result = {}

    all_forms = unique([base_label] + list(forms))

    for form in all_forms:
        # Własna tabela Standard Moves zastępuje bazową.
        if form in standard:
            names = list(standard[form])
        else:
            names = list(base_moves)

        # Special Moves są dodatkiem.
        names.extend(special.get(form, []))

        result[form] = unique(names)

    return result


# ============================================================
# ANALIZA POJEDYNCZEGO POKÉMONA
# ============================================================

def analyse_pokemon(pokemon):
    species_name = pokemon["name"]

    print(f"Analizuję: {species_name}")

    # Strona pobierana tylko raz.
    soup = fetch_soup(pokemon["url"])

    alternate_forms = extract_alternate_forms(
        soup,
        species_name,
    )

    evolutionary_forms = extract_evolutionary_forms(
        soup,
        species_name,
    )

    type_forms = extract_type_forms(
        soup,
        species_name,
        alternate_forms,
    )

    ability_forms = extract_ability_forms(
        soup,
        species_name,
        alternate_forms,
    )

    stats_forms = extract_stats_forms(
        soup,
        species_name,
        alternate_forms,
    )

    standard_move_forms = extract_standard_moves_forms(
        soup,
        species_name,
        alternate_forms,
    )

    # --------------------------------------------------------
    # FILTROWANIE FORM
    # --------------------------------------------------------

    kept_forms = []
    discarded_forms = []
    diagnostics = {}

    base_candidates = []
    base_form = None

    # Formy płciowe są rozpoznawane niezależnie od tego,
    # czy mają osobny wpis w typach lub statystykach.
    gender_alternate_forms = []

    for form in alternate_forms:
        key = form_key(form, species_name)

        if key in ("male", "female"):
            gender_alternate_forms.append(form)

    for form in alternate_forms:

        if form.casefold() == species_name.casefold():
            continue

        if form_key(form, species_name) in ("normal", "kanto"):
            base_form = form

            diagnostics[form] = [
                "forma bazowa — odpowiednik formy Normal"
            ]

            continue

        if is_mega_form(form):
            kept_forms.append(form)
            diagnostics[form] = ["Mega Evolution"]
            continue

        evidence = find_evidence_for_form(
            form_name=form,
            species_name=species_name,
            type_forms=type_forms,
            stats_forms=stats_forms,
            ability_forms=ability_forms,
            standard_move_forms=standard_move_forms,
        )

        if evidence:
            kept_forms.append(form)
            diagnostics[form] = evidence
        else:
            discarded_forms.append(form)
            diagnostics[form] = []
            base_candidates.append(form)

    # --------------------------------------------------------
    # WYBÓR FORMY BAZOWEJ
    # --------------------------------------------------------

    if (
        base_form is None
        and len(alternate_forms) > 1
        and len(base_candidates) == 1
    ):
        base_form = base_candidates[0]

        discarded_forms = [
            form
            for form in discarded_forms
            if form.casefold() != base_form.casefold()
        ]

        diagnostics[base_form] = [
            "forma bazowa — jedyna forma bez wyróżników"
        ]

    # --------------------------------------------------------
    # FORMY PŁCIOWE ZASTĘPUJĄ NAZWĘ BAZOWĄ
    # --------------------------------------------------------

    gender_forms = {
        form_key(form, species_name)
        for form in kept_forms
        if form_key(form, species_name) in ("male", "female")
    }

    gender_forms_replace_base = (
        "male" in gender_forms
        and "female" in gender_forms
    )

    if gender_forms_replace_base:
        male_form = next(
            (
                form
                for form in kept_forms
                if form_key(form, species_name) == "male"
            ),
            None,
        )

        # Male staje się formą bazową zamiast gołego gatunku.
        if male_form:
            base_form = male_form

            diagnostics[male_form] = [
                "forma Male zastępuje bazowy wpis gatunku"
            ]

    # --------------------------------------------------------
    # MEGA Z EVOLUTIONARY CHAIN
    # --------------------------------------------------------

    mega_forms = [
        form
        for form in evolutionary_forms
        if is_mega_form(form)
    ]

    mega_forms.extend(
        form
        for form in alternate_forms
        if is_mega_form(form)
    )

    mega_forms = unique(mega_forms)

    for mega_form in mega_forms:
        if not any(
            form.casefold() == mega_form.casefold()
            for form in kept_forms
        ):
            kept_forms.append(mega_form)

        diagnostics.setdefault(
            mega_form,
            ["Mega Evolution"],
        )

        discarded_forms = [
            form
            for form in discarded_forms
            if form.casefold() != mega_form.casefold()
        ]

    kept_forms = unique(kept_forms)

    # --------------------------------------------------------
    # EKSTRAKCJA DANYCH
    # --------------------------------------------------------

    base_label = base_form or species_name

    # Formy do ekstrakcji obejmują również Mega.
    all_forms = unique(kept_forms)

    types = extract_types(
        soup,
        species_name,
        all_forms,
        base_label,
    )

    stats = extract_base_stats(
        soup,
        species_name,
        all_forms,
        base_label,
    )

    abilities = extract_abilities(
        soup,
        species_name,
        all_forms,
        base_label,
    )

    moves = extract_moves(
        soup,
        species_name,
        all_forms,
        base_label,
    )

    # --------------------------------------------------------
    # OSOBNY REKORD DLA KAŻDEJ FORMY
    # --------------------------------------------------------

    # Nie dodajemy osobnego wpisu z samą nazwą gatunku,
    # jeśli Male i Female zastępują formę bazową.
    if gender_forms_replace_base:
        entry_forms = unique(
            [base_label] + all_forms
        )
    else:
        entry_forms = unique(
            [base_label] + all_forms
        )

    entries = []

    for form in entry_forms:
        entries.append({
            "name": species_name,
            "form": form,
            "dex_number": pokemon.get("dex_number"),
            "types": types.get(form, []),
            "base_stats": stats.get(form),
            "abilities": abilities.get(form, []),
            "moves": moves.get(form, []),
        })

    return {
        "name": species_name,
        "url": pokemon["url"],
        "dex_number": pokemon.get("dex_number"),

        "forms": unique(kept_forms),
        "base_form": base_form,

        "gender_forms_replace_base": gender_forms_replace_base,

        "has_mega_evolution": bool(mega_forms),

        "discarded_forms": unique(discarded_forms),
        "diagnostics": diagnostics,

        "entries": entries,

        "detected": {
            "alternate_forms": alternate_forms,
            "type_forms": type_forms,
            "stats_forms": stats_forms,
            "ability_forms": ability_forms,
            "standard_move_forms": standard_move_forms,
            "mega_forms": mega_forms,
            "base_candidates": base_candidates,
            "gender_forms": sorted(gender_forms),
        },
    }


# ============================================================
# FORMATOWANIE NAZW FORM
# ============================================================

def format_form_name(species_name, form_name):
    form_name = normalize(form_name)

    if not form_name:
        return ""

    if form_name.casefold() == species_name.casefold():
        return ""

    if re.search(
        rf"\b{re.escape(species_name)}\b",
        form_name,
        flags=re.I,
    ):
        return form_name

    return f"{species_name} {form_name}"


# ============================================================
# KOŃCOWA LISTA
# ============================================================

def build_final_list(analysed):
    final_names = []
    seen = set()

    def add(name):
        name = normalize(name)

        if not name:
            return

        key = name.casefold()

        if key not in seen:
            seen.add(key)
            final_names.append(name)

    for pokemon in analysed:
        species_name = pokemon["name"]
        base_form = pokemon.get("base_form")

        # FORMA BAZOWA
        if base_form:
            add(
                format_form_name(
                    species_name,
                    base_form,
                )
            )

        elif not pokemon.get("gender_forms_replace_base", False):
            add(species_name)

        # FORMY MECHANICZNIE ODMIENNE
        for form in pokemon["forms"]:
            add(
                format_form_name(
                    species_name,
                    form,
                )
            )

        # MEGA EWOLUCJE
        for mega_form in pokemon.get(
            "detected",
            {},
        ).get("mega_forms", []):
            add(
                format_form_name(
                    species_name,
                    mega_form,
                )
            )

    return final_names


# ============================================================
# ZAPIS WYNIKÓW
# ============================================================

def save_results(analysed, final_names):
    # Główna baza danych: tylko rekordy poszczególnych form.
    entries = []

    for pokemon in analysed:
        entries.extend(pokemon.get("entries", []))

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "pokemon_count": len(analysed),
                "entry_count": len(entries),
                "pokemon": entries,
                "names": final_names,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    #with open(
    #    OUTPUT_TXT,
    #    "w",
    #    encoding="utf-8",
    #) as file:
    #    for name in final_names:
    #        file.write(name + "\n")


# ============================================================
# RAPORT
# ============================================================

def print_report(analysed, final_names):
    print()
    print("=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)

    print(f"Liczba gatunków: {len(analysed)}")
    print(f"Liczba wpisów razem z formami: {len(final_names)}")

    total_entries = sum(
        len(pokemon.get("entries", []))
        for pokemon in analysed
    )

    print(f"Liczba rekordów danych: {total_entries}")

    print()
    print("=" * 70)
    print("DANE FORM")
    print("=" * 70)

    for pokemon in analysed:
        if not pokemon.get("entries"):
            continue

        print()
        print(pokemon["name"])

        for entry in pokemon["entries"]:
            print(f"  {entry['form']}")
            print(f"    Typy: {', '.join(entry['types']) or '(brak)'}")
            print(
                f"    Statystyki: "
                f"{'OK' if entry['base_stats'] else '(brak)'}"
            )
            print(
                f"    Umiejętności: "
                f"{len(entry['abilities'])}"
            )
            print(
                f"    Ruchy: "
                f"{len(entry['moves'])}"
            )


# ============================================================
# MAIN
# ============================================================

def main():
    roster = get_roster()

    print()
    print(f"Znaleziono {len(roster)} unikalnych Pokémonów w rosterach.")
    print()

    analysed = []

    total = len(roster)
    start_time = time.time()

    for index, pokemon in enumerate(roster, start=1):

        if DEBUG:
            print(
                f"[{index}/{total}] "
                f"{pokemon['name']}"
            )

        try:
            result = analyse_pokemon(pokemon)
            analysed.append(result)

        except Exception as error:
            print(
                f"BŁĄD przy {pokemon['name']}: {error}"
            )

            analysed.append({
                "name": pokemon["name"],
                "url": pokemon["url"],
                "dex_number": pokemon.get("dex_number"),
                "forms": [],
                "base_form": None,
                "gender_forms_replace_base": False,
                "has_mega_evolution": False,
                "discarded_forms": [],
                "diagnostics": {},
                "entries": [],
                "detected": {},
                "error": str(error),
            })

        # Aktualizacja paska po zakończeniu analizy
        # danego Pokémona — również w przypadku błędu.
        show_progress(
            current=index,
            total=total,
            start_time=start_time,
            name=pokemon["name"],
        )

        time.sleep(REQUEST_DELAY)

    final_names = build_final_list(analysed)

    save_results(
        analysed,
        final_names,
    )

    print_report(
        analysed,
        final_names,
    )

    print()
    print(f"Zapisano: {OUTPUT_TXT}")
    print(f"Zapisano: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()