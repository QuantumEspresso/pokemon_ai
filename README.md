Moim zdaniem jesteśmy już na etapie, na którym warto przestać myśleć o tym projekcie jak o zwykłym Pokédexie, a zacząć projektować bazę wiedzy dla trenera Pokémonów.

Masz już cztery bardzo ważne fundamenty:
- Pokémony — statystyki, typy i dostępne gatunki.
- Abilities — zdolności i ich efekty.
- Moves — ruchy, parametry i właściwości bojowe.
- Items — przedmioty i ich opisy.
To wystarczy, żeby AI odpowiadało na pytania typu „jaki ruch może nauczyć się Garchomp?”, ale jeszcze nie wystarczy, żeby rzetelnie odpowiedzieć na pytanie:
„Zbuduj mi drużynę sześciu Pokémonów do aktualnego formatu, która ma plan na popularne zagrożenia, sensowne match-upy, speed control, defensywne przełączenia i nie przegrywa z jednym konkretnym archetypem”.

Do tego potrzebujemy trzech dodatkowych warstw: mechaniki gry, danych o metagame oraz wiedzy strategicznej.
1. Jakie dodatkowe bazy danych bym stworzył?
Nie robiłbym jednej gigantycznej bazy. Podzieliłbym dane według ich charakteru i częstotliwości aktualizacji.
A. Dane o zasadach i mechanice — game_mechanics
Bardzo wysoki priorytet
To jest dokładnie ta część, którą proponujesz w formie pliku TXT/Markdown. I zdecydowanie ją dodajemy.

Tylko nie ograniczałbym się do jednego pliku. Zrobiłbym katalog:
knowledge/
├── game_mechanics.md
├── battle_rules.md
├── damage_calculation.md
├── stat_points.md
├── stat_stages.md
├── speed_and_turn_order.md
├── weather_and_terrain.md
├── status_conditions.md
├── doubles_mechanics.md
└── team_building_guide.md


Co powinno się w nich znaleźć?
Plik	Zawartość
game_mechanics.md	Ogólny opis mechaniki Pokémon Champions
battle_rules.md	Format walki, liczba Pokémonów, wybór Pokémonów do walki, zasady regulaminowe
damage_calculation.md	Wzór obrażeń, STAB, typy, krytyki, modyfikatory, zaokrąglenia
stat_points.md	Stat Points, ich limity, wpływ na statystyki i nature
stat_stages.md	Boosty i obniżenia statystyk od -6 do +6
speed_and_turn_order.md	Priorytet ruchów, Speed, Trick Room, Tailwind, paraliż i inne modyfikatory
weather_and_terrain.md	Pogoda, tereny i ich interakcje
status_conditions.md	Burn, Poison, Sleep, Paralysis, Freeze itd.
doubles_mechanics.md	Spread moves, redirection, Protect, Fake Out, Helping Hand, Ally Switch itd.
team_building_guide.md	Jak budować drużynę, role, synergie i pokrywanie słabości

Ważna korekta dotycząca EV i IV
W Pokémon Champions nie powinniśmy bezrefleksyjnie opisywać klasycznego systemu EV.

W aktualnym modelu Champions stosuje się Stat Points, a nie tradycyjne EV. VGC Builder podaje następujące zasady dla opisywanego formatu:
- Level 50.
- 66 Stat Points do rozdysponowania.
- Maksymalnie 32 Stat Points w jednej statystyce.
- Perfect IVs.
- Species Clause, Item Clause.
- Jedna Mega Ewolucja na walkę.
Źródło mechaniki i zasad: 
VGC Builder


Dlatego AI powinno rozumieć zarówno terminologię Champions (Stat Points), jak i klasyczną terminologię Pokémonów (EVs, IVs), ale nie może ich mylić.

Przykładowo:
- Gracz pyta o „252 EV Speed” — AI powinno rozumieć, o jaką inwestycję chodzi, ale przeliczyć ją na system Stat Points.
- Gracz pyta o „max Speed” — AI powinno policzyć rzeczywistą wartość statystyki na poziomie 50.
- Gracz pyta o „minimum Speed pod Trick Room” — AI powinno umieć dobrać odpowiedni rozkład punktów.
Jedna bardzo ważna rzecz: zasady powinny mieć wersję i datę obowiązywania. Nie chcemy, żeby AI korzystało z mechaniki poprzedniej regulacji po zmianie zasad.

B. Statystyki użycia i metagame — metagame_database
Bardzo wysoki priorytet
To będzie prawdopodobnie jedna z najważniejszych części całego projektu.

AI powinno wiedzieć nie tylko, co Pokémon potrafi, ale też jak ludzie faktycznie go wykorzystują.

Przykładowe dane dla każdego Pokémona:
- Usage % — jak często występuje w drużynach.
- Win Rate — skuteczność drużyn, w których występuje.
- Top Cut Usage — jak często pojawia się w najlepszych drużynach.
- Najczęściej używane ruchy.
- Najczęściej używane przedmioty.
- Najczęściej używane abilities.
- Najczęstsze rozkłady Stat Points.
- Najczęstsze nature / Stat Alignments.
- Najczęściej spotykani partnerzy.
- Najczęstsze role.
- Trend użycia — czy Pokémon zyskuje, czy traci popularność.
Przykładowa struktura:
{
    "pokemon": "Incineroar",
    "regulation": "M-C",
    "format": "VGC Doubles",
    "period": "2026-11",
    "usage": {
        "usage_percent": 32.5,
        "win_rate": 49.4,
        "top_cut_usage": null
    },
    "common_moves": [
        "Fake Out",
        "Flare Blitz",
        "Parting Shot",
        "Knock Off"
    ],
    "common_items": [
        "Sitrus Berry",
        "Safety Goggles"
    ],
    "common_abilities": [
        "Intimidate"
    ],
    "common_partners": [
        "Rillaboom",
        "Sneasler"
    ]
}


Wartości w tym przykładzie są wyłącznie ilustracyjne — nie traktujmy ich jako kompletnego zestawu danych.
Skąd brać te informacje?










Pokémon Champions Battle Data
Otwórz Battle DataNajcenniejsze źródło dla danych z samej gry: popularność Pokémonów, przedmioty, abilities, ruchy, partnerzy i rozkłady Stat Points.













INF VGC
Otwórz INF VGCStatystyki turniejowe, usage, win rate, cores, matchupy, trendy, speed tiers i drużyny z turniejów. Serwis opisuje również sposób liczenia wskaźników. 
infovgc














Smogon
Otwórz statystyki SmogonMiesięczne statystyki z Pokémon Showdown, w tym popularność, sety, rozkłady i partnerzy. Trzeba jednak oddzielać dane z symulatora od danych z oficjalnego laddera Champions. 
DexDB














Victory Road
Otwórz Victory RoadPublikowane drużyny turniejowe, team reporty, rozpiski i wyniki.



Moja rekomendacja: przechowujmy dane z różnych źródeł oddzielnie. In-game ladder, Showdown i turnieje nie są tym samym środowiskiem. Nie wolno ich mieszać w jedną liczbę usage.

C. Gotowe konfiguracje Pokémonów — competitive_sets
Bardzo wysoki priorytet
To osobna baza, której nie pomijałbym nawet wtedy, gdy mamy już metagame.

Dla każdego Pokémona przechowujemy wiele gotowych konfiguracji, a nie tylko jedną „najlepszą”.

Przykładowo Garchomp może mieć:
1. Offensive sweeper.
2. Choice Scarf.
3. Focus Sash lead.
4. Bulky setup.
5. Sand team attacker.
Każdy set powinien zawierać:
{
    "pokemon": "Garchomp",
    "regulation": "M-C",
    "role": [
        "physical_attacker",
        "speed_control_check"
    ],
    "ability": "Rough Skin",
    "item": "Focus Sash",
    "nature": "Jolly",
    "stat_points": {
        "hp": 0,
        "attack": 32,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 32
    },
    "moves": [
        "Earthquake",
        "Dragon Claw",
        "Protect",
        "Rock Slide"
    ],
    "strategy": "Fast physical attacker with strong spread damage.",
    "source": "tournament",
    "sample_size": null
}


Tu też ważne zastrzeżenie: nie każda publiczna drużyna zawiera dokładne Stat Points. Jeśli ich nie znamy, zapisujemy null, a nie wymyślamy rozkład.

INF VGC sam zaznacza, że w przypadku niektórych drużyn rozkłady są szacowane, ponieważ turniejowe listy nie publikują wszystkich danych. 
infovgc

D. Synergie Pokémonów i gotowe cores — team_synergies
Wysoki priorytet
To jest moim zdaniem coś, co odróżni nasze AI od zwykłego generatora drużyn.

Nie wystarczy wiedzieć, że Rillaboom jest dobry, a Incineroar jest dobry. AI powinno wiedzieć, dlaczego razem mogą być jeszcze lepsi.

Przechowywałbym:
- Pary Pokémonów, które często występują razem.
- Trójki i czwórki tworzące popularne cores.
- Synergie umiejętności.
- Synergie ruchów.
- Synergie pogodowe i terenowe.
- Kombinacje ofensywne.
- Kombinacje defensywne.
- Wzajemne pokrywanie słabości.
Przykładowa baza:
{
    "core_name": "Rain Core",
    "pokemon": [
        "Pelipper",
        "Archaludon"
    ],
    "strategy": [
        "rain",
        "weather_abuse",
        "special_offense"
    ],
    "synergies": [
        {
            "pokemon": "Pelipper",
            "reason": "Sets rain with Drizzle."
        },
        {
            "pokemon": "Archaludon",
            "reason": "Benefits from rain and can use Electro Shot."
        }
    ],
    "common_support": [
        "Rillaboom",
        "Basculegion"
    ]
}


Przy czym rozróżniałbym dwie rzeczy:
- Popular synergy — Pokémony często występują razem.
- Strategic synergy — Pokémony rzeczywiście wzajemnie wzmacniają swoje możliwości.
To nie zawsze jest to samo.

Dane o popularnych parach, trójkach i czwórkach oraz wskaźniki ich współwystępowania są dostępne np. w INF VGC. 
infovgc

E. Matchupy i zagrożenia — matchups_database
Wysoki priorytet
Chciałbym, żeby AI potrafiło odpowiedzieć na pytania:
- Jak nasza drużyna radzi sobie z Rain?
- Co robimy przeciwko Trick Room?
- Czy mamy odpowiedź na Gholdengo?
- Jak poradzimy sobie z Intimidate spam?
- Czy przeciwnik może nas łatwo zdominować przez Tailwind?
- Które popularne Pokémony stanowią dla nas największe zagrożenie?
Możemy przechowywać dane w dwóch formach.

1. Matchupy Pokémon vs Pokémon
{
    "pokemon": "Garchomp",
    "opponent": "Gholdengo",
    "matchup": "unfavorable",
    "reason": [
        "Gholdengo threatens Garchomp with strong special attacks.",
        "Garchomp can threaten Gholdengo with Ground-type attacks."
    ],
    "recommended_answers": [
        "Incineroar",
        "Kingambit"
    ]
}


2. Matchupy archetypów
{
    "archetype": "Rain",
    "strengths": [
        "Strong Water-type attacks",
        "Weather-dependent offensive pressure"
    ],
    "weaknesses": [
        "Weather replacement",
        "Electric-type pressure"
    ],
    "recommended_answers": [
        "Weather control",
        "Grass-type attackers",
        "Electric-type attackers"
    ]
}


Nie tworzyłbym jednak takich ocen ręcznie dla każdej możliwej pary. Część powinna być wyliczana przez kalkulator obrażeń, a część wynikać z rzeczywistych danych turniejowych.

F. Strategie i archetypy drużyn — strategies_database
Wysoki priorytet
Tutaj właśnie trafia Twoja propozycja rozpiski popularnych strategii.

Chciałbym, żeby AI znało zarówno klasyczne archetypy, jak i bardziej specyficzne strategie.










Rain

Ustawianie deszczu i wykorzystywanie wzmocnionych ruchów Water.











Sun

Pogoda, Fire damage, Chlorophyll i inne synergie.











Trick Room

Kontrola kolejności ruchów i wykorzystanie wolnych Pokémonów.











Tailwind

Kontrola prędkości przez podwojenie Speed własnej strony.











Sand

Pogoda, defensywne synergie i ofensywne wykorzystanie Speed.











Hyper Offense

Maksymalna presja ofensywna, setup i szybkie eliminowanie zagrożeń.











Balance

Połączenie ofensywy, defensywy i kontroli tempa.











Bulky Offense

Mocne ataki, ale z wystarczającą wytrzymałością do przetrwania kontrataku.


Dla każdego archetypu przygotowałbym:
- Opis strategii.
- Warunki zwycięstwa.
- Typowe Pokémony.
- Typowe cores.
- Najczęstsze ruchy i przedmioty.
- Mocne i słabe strony.
- Jak rozpoznać archetyp przeciwnika.
- Jak grać przeciwko niemu.
- Przykładowe drużyny turniejowe.
To powinno być w dużej części w formacie JSON, a szersze omówienia strategii w Markdown.

G. Turnieje i osiągnięcia — tournament_database
Tutaj przechowywałbym konkretne wyniki, a nie tylko ogólne statystyki.

Dla każdego turnieju:
- Nazwa wydarzenia.
- Data.
- Format i regulacja.
- Liczba uczestników.
- Zwycięzca.
- Top 8 / Top 16.
- Drużyny zawodników.
- Zajęte miejsca.
- Link do źródła i team reportu.
Dzięki temu AI będzie mogło powiedzieć:
Ten core nie tylko jest popularny. Był też wykorzystywany przez drużyny osiągające wysokie wyniki na dużych turniejach.

To ważne, bo sama popularność nie oznacza skuteczności.

Źródłami mogą być Victory Road, oficjalne wyniki Play! Pokémon i zestawienia turniejowe. Warto zachowywać oryginalny link do każdej drużyny i wydarzenia. 
DexDB+1

2. Jeszcze jedna rzecz: kalkulator zamiast zgadywania
To jest moim zdaniem absolutnie kluczowe.

Nie chciałbym, żeby AI samodzielnie próbowało liczyć obrażenia na podstawie tekstowego opisu mechaniki.

Powinniśmy mieć zewnętrzny silnik obliczeniowy, któremu AI przekazuje konkretne parametry, a silnik zwraca wynik.

Przykładowo:
Attacker:
    Pokémon: Garchomp
    Level: 50
    Move: Earthquake
    Nature: Jolly
    Stat Points: 32 Attack

Defender:
    Pokémon: Incineroar
    Level: 50
    Nature: Careful
    Stat Points: 32 HP / 32 Defense

Battle:
    Weather: None
    Terrain: Grassy Terrain
    Critical Hit: False
    Spread Move: True


Wynik:
Damage:
    Minimum:  ...
    Maximum:  ...
    Percentage: ...%

KO Chance:
    Guaranteed: No
    Possible: ...


Nie musimy pisać całego silnika od zera. Istnieje biblioteka @smogon/calc, która ma mechanikę Pokémon Champions. VGC Builder wykorzystuje ją do kalkulacji obrażeń i korzysta również z danych Pokémon Showdown. 
VGC Builder


To pozwoli AI robić rzeczy w rodzaju:
Ten Pokémon przeżyje atak przeciwnika w 87% przypadków przy obecnym rozkładzie Stat Points. Jeżeli zmienimy rozkład, uzyskamy gwarantowane przeżycie.

To jest znacznie bardziej wartościowe niż ogólne stwierdzenie, że Pokémon jest „bulky”.
3. Jak zorganizowałbym cały projekt?
Moja propozycja docelowej struktury:
pokemon_ai/
│
├── data/
│   ├── pokemon_database.json
│   ├── abilities_database.json
│   ├── moves_database.json
│   ├── item_database.json
│   │
│   ├── competitive/
│   │   ├── usage_stats/
│   │   ├── competitive_sets/
│   │   ├── team_synergies.json
│   │   ├── matchups.json
│   │   ├── strategies.json
│   │   └── tournaments/
│   │
│   └── rules/
│       ├── current_regulation.json
│       ├── regulation_history.json
│       └── type_chart.json
│
├── knowledge/
│   ├── game_mechanics.md
│   ├── battle_rules.md
│   ├── damage_calculation.md
│   ├── stat_points.md
│   ├── stat_stages.md
│   ├── speed_and_turn_order.md
│   ├── weather_and_terrain.md
│   ├── status_conditions.md
│   ├── doubles_mechanics.md
│   └── team_building_guide.md
│
├── tools/
│   ├── damage_calculator/
│   ├── stat_calculator/
│   ├── speed_calculator/
│   ├── type_coverage.py
│   └── team_analyzer.py
│
├── scrapers/
│   ├── get_pokemon.py
│   ├── get_abilities.py
│   ├── get_moves.py
│   ├── get_items.py
│   └── get_metagame.py
│
└── prompts/
    ├── system_prompt.txt
    └── team_building_prompt.txt


Nie musimy od razu tworzyć wszystkich plików. To docelowy szkielet, do którego będziemy stopniowo dochodzić.
4. Jak powinno działać samo AI?
Wyobrażam sobie następujący proces:
WEJŚCIE
Użytkownik określa cel

Np. chcę drużynę Balance do VGC Doubles, bez legendarnych Pokémonów.


1. Analiza ograniczeń

Regulacja, dostępne Pokémony, legalność, format i preferencje użytkownika.


2. Wybór strategii i cores

Metagame, popularne konfiguracje, synergie i przykładowe drużyny.


3. Budowa drużyny

Dobór sześciu Pokémonów, abilities, ruchów, przedmiotów i Stat Points.


4. Walidacja techniczna

Legalność, kalkulator obrażeń, Speed Tiers, coverage, słabości i matchupy.


WYNIK
Gotowa drużyna + uzasadnienie

Sety, plan gry, mocne i słabe strony, zagrożenia oraz alternatywy.


Najważniejsze: AI nie powinno od razu generować sześciu Pokémonów na chybił trafił. Powinno najpierw zrozumieć, jaką drużynę budujemy i jaki ma być jej plan na wygrywanie.
5. Co jeszcze bym dodał?
Trzy rzeczy, które mogą mocno podnieść jakość projektu:

1. Team roles

Osobna klasyfikacja ról Pokémonów:
- Physical Sweeper
- Special Sweeper
- Wallbreaker
- Bulky Attacker
- Special Wall
- Physical Wall
- Support
- Speed Control
- Redirection
- Setup Sweeper
- Pivot
- Revenge Killer
- Weather Setter
- Weather Abuser
Nie wszystkie role muszą być przypisane na stałe. Pokémon może mieć kilka ról zależnie od konfiguracji.

2. Leads i plany na pierwsze tury

W doubles to bardzo istotne. AI powinno rozumieć, które pary Pokémonów najlepiej wystawiać na start, jakie mają opcje w pierwszej turze i jak reagować na typowe otwarcia przeciwnika.

Przykładowo:
{
    "core": [
        "Incineroar",
        "Rillaboom"
    ],
    "lead_strategy": "Defensive pivot",
    "turn_1_options": [
        "Fake Out",
        "Protect",
        "U-turn"
    ],
    "goal": "Gain positional advantage and control the pace."
}


3. Battle logs / replays

Jeżeli uda nam się pozyskiwać powtórki walk lub ich szczegółowe logi, możemy później analizować:
- Które ruchy rzeczywiście były wybierane.
- Jakie kombinacje prowadziły do zwycięstwa.
- Jakie błędy powtarzają się w konkretnych matchupach.
- Które strategie działają w praktyce, a które tylko dobrze wyglądają na papierze.
To byłaby świetna podstawa do przyszłego rozwijania AI.

6. Skąd brać dane i co robić najpierw?
Przydatne strony, które warto zachować w projekcie:
Źródło	Zastosowanie
Serebii	Dane podstawowe Pokémonów, ruchów, abilities i przedmiotów
Champions Battle Data	Statystyki z laddera w samej grze
INF VGC	Statystyki turniejowe, cores i matchupy
Smogon Stats	Miesięczne statystyki Showdown
Victory Road	Turnieje i drużyny zawodników
VGC Builder	Referencja dla mechaniki i kalkulatorów
Smogon Damage Calculator	Silnik kalkulacji obrażeń

Dodatkowo zachowałbym oficjalny regulamin Play! Pokémon. Trzeba tylko odróżniać zasady turniejowe od zasad samej gry.
7. Moja kolejność realizacji
Nie budowałbym wszystkiego jednocześnie. Proponuję taki roadmap:
Etap 1 — Fundamenty
Teraz

- [ ] game_mechanics.md
- [ ] battle_rules.md
- [ ] stat_points.md
- [ ] stat_stages.md
- [ ] speed_and_turn_order.md
- [ ] type_chart.json


Etap 2 — Wiedza competitive
- [ ] Scraper statystyk usage
- [ ] Baza competitive sets
- [ ] Baza popularnych cores
- [ ] Baza strategii i archetypów
- [ ] Baza drużyn turniejowych


Etap 3 — Narzędzia analityczne
- [ ] Damage Calculator
- [ ] Stat Points Calculator
- [ ] Speed Calculator
- [ ] Type Coverage Analyzer
- [ ] Team Weakness Analyzer


Etap 4 — AI Team Builder
- [ ] System prompt
- [ ] Wyszukiwanie w bazach danych
- [ ] Generowanie drużyn
- [ ] Automatyczna walidacja
- [ ] Uzasadnianie decyzji i proponowanie alternatyw


8. Jedna ważna decyzja architektoniczna
Zdecydowanie proponuję, żebyśmy każdemu rekordowi dodawali metadane:
{
    "source": "official_ladder",
    "source_url": "https://example.com/",
    "regulation": "M-C",
    "format": "doubles",
    "collected_at": "2026-11-18",
    "confidence": "high"
}


Nie każdy rekord będzie miał wszystkie te pola, ale idea jest ważna: AI musi wiedzieć, skąd pochodzi informacja, jak aktualna jest i czy jest oficjalna, wyliczona czy szacowana.

To zapobiegnie sytuacji, w której AI potraktuje niepotwierdzoną strategię z forum jako fakt mechaniczny.

Moja ostateczna rekomendacja
Nie zaczynałbym teraz od scrapowania turniejów. Najpierw stworzyłbym solidną warstwę mechaniki i reguł, bo bez niej nawet najlepsze dane competitive mogą prowadzić do błędnych rekomendacji.

Proponuję następny krok: Etap 1 — dokumentacja mechaniki Pokémon Champions.

Zacząłbym od game_mechanics.md, battle_rules.md i stat_points.md. Następnie opracowałbym kolejność ruchów, boosty, obrażenia i mechanikę doubles. Każdy dokument powinien mieć źródła, datę weryfikacji i oznaczenia informacji niepotwierdzonych.

Jedna rzecz, którą chciałbym jeszcze ustalić przed projektowaniem dokumentacji: czy docelowe AI ma budować drużyny wyłącznie do VGC Doubles (6 Pokémonów, z których wybiera się 4), czy chcemy od początku obsługiwać również Singles i inne formaty?

To istotnie wpłynie na strukturę reguł, statystyk i metagame.