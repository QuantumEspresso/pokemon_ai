# Pokémon Champions AI Team Builder

An evolving knowledge base and toolkit designed to help AI understand Pokémon Champions competitive play, analyze the metagame, and build well-structured competitive teams.

The goal of this project is to go beyond a traditional Pokédex. Instead of simply storing information about Pokémon, moves, abilities, and items, this project aims to provide AI with the knowledge and analytical tools needed to understand competitive Pokémon battles and make informed team-building decisions.

The long-term vision is to create an AI assistant capable of building complete teams, evaluating matchups, identifying strategic synergies, calculating damage, and explaining the reasoning behind its recommendations.

---

## Project Status

**Current stage: Foundation – Core Data Collection**

The project currently includes scripts that collect and generate structured databases based on information available on [Serebii.net](https://www.serebii.net/).

### Currently Implemented

- [x] Pokémon database generation
- [x] Ability database generation
- [x] Move database generation
- [x] Item database generation
- [ ] Game mechanics documentation
- [ ] Battle rules and regulation database
- [ ] Competitive metagame data collection
- [ ] Competitive Pokémon sets
- [ ] Team synergy and matchup databases
- [ ] Battle calculation tools
- [ ] AI-powered team builder

The project is under active development. Its architecture and planned features may evolve as new data sources and requirements are explored.

---

## Core Data

The current implementation focuses on four fundamental datasets.

| Database | Description |
|---|---|
| `pokemon_database.json` | Available Pokémon species, base stats, types, and other relevant information. |
| `abilities_database.json` | Pokémon abilities and their effects. |
| `moves_database.json` | Moves, their properties, parameters, and battle effects. |
| `items_database.json` | Available items and their descriptions. |

These databases provide the foundation for more advanced competitive analysis.

For example, they allow an AI system to answer questions about available Pokémon, their abilities, and their learnable moves. However, competitive team building requires additional context, including battle mechanics, regulations, metagame trends, and strategic relationships between Pokémon.

This is why the project is designed to grow into a comprehensive competitive knowledge base.

---

## Vision & Planned Architecture

The long-term architecture is divided into several independent but interconnected layers.

### 1. Game Mechanics & Rules

**Priority: Very High**

A reliable understanding of game mechanics is essential for accurate competitive analysis.

Rather than relying on general Pokémon knowledge or assumptions based on previous games, the AI should have access to dedicated documentation describing the mechanics and rules applicable to Pokémon Champions.

Planned documentation:

| File | Description |
|---|---|
| `game_mechanics.md` | General overview of Pokémon Champions mechanics. |
| `battle_rules.md` | Battle formats, team selection, regulations, and competitive restrictions. |
| `damage_calculation.md` | Damage formulas, STAB, type effectiveness, critical hits, modifiers, and rounding. |
| `stat_points.md` | Stat Points distribution, limits, stat calculations, and nature interactions. |
| `stat_stages.md` | Stat boosts and reductions, including the -6 to +6 stage system. |
| `speed_and_turn_order.md` | Move priority, Speed calculations, Trick Room, Tailwind, paralysis, and other modifiers. |
| `weather_and_terrain.md` | Weather conditions, terrains, and their interactions. |
| `status_conditions.md` | Burn, Poison, Sleep, Paralysis, Freeze, and other status conditions. |
| `doubles_mechanics.md` | Spread moves, redirection, Protect, Fake Out, Helping Hand, Ally Switch, and other Doubles mechanics. |
| `team_building_guide.md` | Team roles, synergies, defensive coverage, and competitive team-building principles. |

#### Stat Points vs. EVs and IVs

One important consideration is that Pokémon Champions uses its own Stat Points system rather than the traditional EV distribution system.

The AI must understand both traditional Pokémon terminology and Champions-specific mechanics without confusing them.

For example:

- A request for `252 EV Speed` should be interpreted as a request for maximum Speed investment and translated into the appropriate Stat Points distribution.
- A request for `max Speed` should result in an actual calculated Speed stat.
- A request for `minimum Speed for Trick Room` should result in an optimized Stat Points distribution.

Rules and regulations must be versioned and dated. This will prevent the AI from applying outdated mechanics or competitive restrictions after a regulation change.

### 2. Metagame Database

**Priority: Very High**

Knowing what a Pokémon can do is not enough. The AI should also understand how Pokémon are actually used in competitive play.

The planned metagame database will store usage statistics and competitive trends, including:

- Usage percentage.
- Win rate.
- Top Cut usage.
- Most common moves.
- Most common items.
- Most common abilities.
- Common Stat Points distributions.
- Common natures and stat configurations.
- Most frequent teammates.
- Common competitive roles.
- Usage trends over time.


#### Planned Data Sources

- **Pokémon Champions Battle Data** – In-game usage statistics, popular Pokémon, moves, abilities, items, teammates, and Stat Points distributions.
- **INF VGC** – Tournament statistics, usage, win rates, cores, matchups, Speed tiers, and competitive trends.
- **Smogon Stats** – Monthly Pokémon Showdown usage statistics and competitive sets.
- **Victory Road** – Tournament results, published teams, and team reports.

An important architectural principle is to keep data from different environments separate.

Official in-game ladder statistics, Pokémon Showdown statistics, and tournament results represent different competitive environments. They should never be combined into a single usage metric without clear labeling and methodology.

### 3. Competitive Sets Database

**Priority: Very High**

This database will store ready-to-use competitive configurations for individual Pokémon.

A Pokémon should not be limited to a single recommended set. Different configurations may serve different roles, team archetypes, and strategic purposes.

For example, Garchomp could have:

- Offensive Sweeper.
- Choice Scarf.
- Focus Sash Lead.
- Bulky Setup.
- Sand Team Attacker.


### 4. Team Synergies & Cores

**Priority: High**

This layer should help the AI understand why certain Pokémon work well together.

It will store:

- Frequently paired Pokémon.
- Popular three- and four-Pokémon cores.
- Ability synergies.
- Move synergies.
- Weather and terrain combinations.
- Offensive combinations.
- Defensive combinations.
- Complementary type coverage.
- Mutual weakness coverage.


The database should distinguish between two concepts:

- **Popular Synergy** – Pokémon frequently appear together in competitive teams.
- **Strategic Synergy** – Pokémon have meaningful mechanical or tactical interactions that improve their effectiveness together.

A popular combination is not necessarily a strategically optimal one.

### 5. Matchups & Threat Analysis

**Priority: High**

The AI should be able to evaluate how a team performs against common competitive threats and archetypes.

Examples of questions it should eventually answer:

- How does this team perform against Rain?
- What options does it have against Trick Room?
- Does it have a reliable answer to Gholdengo?
- How does it handle Intimidate-heavy teams?
- Can it deal with Tailwind pressure?
- Which popular Pokémon are the biggest threats?

Two types of matchup data are planned.

**Pokémon vs. Pokémon Matchups**

```json
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
```

**Archetype Matchups**

Matchup evaluations should not rely exclusively on manually assigned ratings.

Where possible, they should be derived from damage calculations, game mechanics, and actual competitive statistics.

### 6. Strategies & Team Archetypes

**Priority: High**

The AI should understand common competitive strategies and recognize the structure of different team archetypes.

Planned archetypes include:

| Archetype | Description |
|---|---|
| Rain | Uses rain to boost Water-type attacks and activate weather-related abilities. |
| Sun | Exploits sunlight, Fire-type damage, Chlorophyll, and related synergies. |
| Trick Room | Controls turn order to benefit slower Pokémon. |
| Tailwind | Uses Speed control to gain a positional advantage. |
| Sand | Combines sandstorm mechanics, defensive synergies, and offensive pressure. |
| Hyper Offense | Focuses on overwhelming opponents through offensive pressure and setup. |
| Balance | Combines offensive and defensive tools with flexible game plans. |
| Bulky Offense | Uses powerful attackers with enough durability to survive retaliation. |

Each archetype should eventually contain:

- Strategy description.
- Primary win conditions.
- Typical Pokémon.
- Common cores.
- Common moves and items.
- Strengths and weaknesses.
- Methods of identifying the archetype.
- Recommended counterplay.
- Example tournament teams.

Structured information should primarily be stored in JSON, with more detailed strategic explanations documented in Markdown.

### 7. Tournament Database

**Priority: Medium**

This database will preserve actual competitive achievements rather than relying only on general usage statistics.

Planned information includes:

- Tournament name.
- Event date.
- Format and regulation.
- Number of participants.
- Winner.
- Top 8 / Top 16 placements.
- Competitor teams.
- Final standings.
- Links to original team lists and reports.

This will allow the AI to distinguish between a Pokémon combination that is simply popular and one that has demonstrated success in high-level competition.

Potential sources include Victory Road and official Play! Pokémon tournament results.

Original source URLs should always be preserved.

---

## Analytical Tools

An important part of the project is moving beyond static information and providing the AI with tools capable of performing actual calculations.

The AI should not be expected to estimate complex battle mechanics from textual descriptions alone.

Instead, it should pass structured inputs to dedicated calculation tools and use their results when making recommendations.

### 1. Damage Calculator

**Planned**

A damage calculation engine should accept information about both Pokémon, their moves, and the current battle conditions.

Example input:

```text
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
```

Expected output:

```text
Damage:
    Minimum: ...
    Maximum: ...
    Percentage: ...%

KO Chance:
    Guaranteed: No
    Possible: ...
```

A potential implementation is [`@smogon/calc`](https://github.com/smogon/damage-calc), which provides a reusable damage calculation engine and includes Pokémon Champions mechanics.

The calculator should be treated as the source of truth for damage calculations whenever its supported mechanics and data match the active game version.

### 2. Stat Points Calculator

**Planned**

A dedicated calculator for:

- Stat Points distribution.
- Final stat calculations.
- Nature interactions.
- Maximum and minimum stat values.
- Optimized defensive benchmarks.
- Speed optimization.
- Traditional EV terminology conversion.

### 3. Speed Calculator

**Planned**

A tool for calculating Speed values and comparing Speed tiers under different conditions.

It should account for:

- Base Speed.
- Level.
- Nature.
- Stat Points.
- Stat stages.
- Tailwind.
- Trick Room.
- Paralysis.
- Other relevant Speed modifiers.

### 4. Type Coverage Analyzer

**Planned**

Analyze offensive type coverage and identify Pokémon that resist or are immune to the team's primary attacks.

### 5. Team Analyzer

**Planned**

Evaluate a complete team for:

- Defensive weaknesses.
- Offensive coverage.
- Shared vulnerabilities.
- Speed control.
- Defensive switching options.
- Role distribution.
- Matchup performance.
- Archetype weaknesses.

---

## Planned Team Building Workflow

The ultimate goal is to create an AI system that follows a structured team-building process instead of randomly selecting six Pokémon.

The proposed workflow:

### Input

The user specifies their goals and restrictions.

Example:

> Build a Balance team for VGC Doubles without Legendary Pokémon.

### Step 1 – Analyze Requirements

Determine:

- Active regulation.
- Available Pokémon.
- Battle format.
- Team restrictions.
- User preferences.
- Relevant competitive rules.

### Step 2 – Select Strategy and Cores

Use metagame statistics, competitive sets, synergies, and successful tournament teams to identify suitable foundations.

### Step 3 – Build the Team

Select six Pokémon and determine:

- Abilities.
- Moves.
- Items.
- Natures.
- Stat Points distributions.
- Individual roles.
- Team synergies.

### Step 4 – Technical Validation

Validate:

- Pokémon and set legality.
- Damage calculations.
- Speed tiers.
- Type coverage.
- Defensive weaknesses.
- Important matchups.
- Team consistency.

### Output

A complete team recommendation containing:

- Six Pokémon with full competitive sets.
- Explanation of each Pokémon's role.
- Team strategy and win conditions.
- Recommended leads.
- Game plans for important matchups.
- Strengths and weaknesses.
- Potential threats.
- Alternative Pokémon or sets.

The most important principle is that the AI should understand the team's intended strategy and win conditions before selecting individual Pokémon.

---

## Additional Planned Features

### Team Roles

A dedicated classification system should describe the competitive roles that Pokémon can perform.

Examples:

- Physical Sweeper.
- Special Sweeper.
- Wallbreaker.
- Bulky Attacker.
- Special Wall.
- Physical Wall.
- Support.
- Speed Control.
- Redirection.
- Setup Sweeper.
- Pivot.
- Revenge Killer.
- Weather Setter.
- Weather Abuser.

Roles should not necessarily be permanently assigned to individual Pokémon. A Pokémon's role can change depending on its competitive set and team composition.

### Lead Selection & Early-Game Planning

Doubles battles require careful consideration of opening Pokémon combinations.

The AI should understand:

- Which Pokémon combinations make effective leads.
- Their available turn-one options.
- Their offensive and defensive interactions.
- How to respond to common opposing leads.
- How to establish an early positional advantage.

### Battle Logs & Replays

A potential future feature is collecting and analyzing battle replays or detailed battle logs.

This could provide information about:

- Moves actually selected during battles.
- Combinations that lead to victories.
- Repeated mistakes in specific matchups.
- Successful and unsuccessful strategies.
- Real-world effectiveness of competitive sets.

Battle replay analysis could eventually become an important source of practical strategic knowledge.

---

## Project Structure

The following is the proposed long-term project structure. Not all directories and files have been implemented yet.

```text
pokemon_ai/
│
├── data/
│   ├── pokemon_database.json
│   ├── abilities_database.json
│   ├── moves_database.json
│   ├── items_database.json
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
```

The structure is intended to be modular, allowing individual components to be implemented and updated independently.

---

## Data Sources & References

The project relies on external sources for collecting and validating Pokémon data, competitive statistics, and game mechanics.

| Source | Intended Use |
|---|---|
| [Serebii](https://www.serebii.net/) | Pokémon, abilities, moves, items, and game information. |
| Pokémon Champions Battle Data | In-game competitive usage statistics and distributions. |
| [INF VGC](https://infovgc.com/) | Tournament statistics, usage, cores, matchups, and competitive analysis. |
| [Smogon](https://www.smogon.com/stats/) | Pokémon Showdown statistics and competitive trends. |
| [Victory Road](https://victoryroad.pro/) | Tournament results, published teams, and team reports. |
| [VGC Builder](https://vgc.build/) | Champions rules, Stat Points, competitive team building, and damage calculations. |
| [Smogon Damage Calculator](https://github.com/smogon/damage-calc) | Damage calculation engine and battle mechanics reference. |
| [Play! Pokémon](https://www.pokemon.com/us/play-pokemon) | Official competitive regulations and tournament rules. |

Different sources may represent different game environments, formats, and regulations. Their data should be stored separately and labeled accordingly.

---

## Data Quality & Versioning

Data accuracy is essential for a competitive AI system.

Every database record should preserve its origin and, whenever possible, information about its reliability and validity.

The AI must be able to distinguish between:

- Official game data.
- Official competitive regulations.
- Community statistics.
- Tournament results.
- Calculated values.
- Estimated or inferred information.
- Unverified strategic claims.

Where applicable, datasets should also include:

- Game version.
- Regulation identifier.
- Data collection date.
- Source methodology.
- Confidence level.
- Whether values are verified or estimated.

Historical regulations and datasets should be preserved rather than overwritten.

This will allow the AI to work with historical competitive environments and avoid applying outdated rules to current teams.

---

## Development Roadmap

Development is divided into four major stages.

### Phase 1 – Foundations

**Current priority**

- [ ] Create `game_mechanics.md`.
- [ ] Create `battle_rules.md`.
- [ ] Document the Stat Points system.
- [ ] Document stat stages.
- [ ] Document Speed and turn order.
- [ ] Create `type_chart.json`.
- [ ] Establish regulation versioning.
- [ ] Establish consistent data metadata.

### Phase 2 – Competitive Knowledge

- [ ] Develop metagame statistics scrapers.
- [ ] Create the competitive sets database.
- [ ] Collect popular Pokémon cores.
- [ ] Create the strategies and archetypes database.
- [ ] Collect tournament teams and results.
- [ ] Implement team role classification.
- [ ] Develop matchup information.

### Phase 3 – Analytical Tools

- [ ] Implement the Damage Calculator.
- [ ] Implement the Stat Points Calculator.
- [ ] Implement the Speed Calculator.
- [ ] Implement the Type Coverage Analyzer.
- [ ] Implement the Team Weakness Analyzer.
- [ ] Implement automated team validation.

### Phase 4 – AI Team Builder

- [ ] Create the AI system prompt.
- [ ] Implement knowledge base retrieval.
- [ ] Implement competitive team generation.
- [ ] Integrate analytical tools.
- [ ] Implement automatic team validation.
- [ ] Generate strategic explanations and alternatives.
- [ ] Add matchup-specific game plans.
- [ ] Develop lead selection and turn planning.

---

## Development Priorities

The recommended development order is intentional.

The first priority is not collecting as much competitive data as possible. It is establishing a reliable foundation of game mechanics and regulations.

Even excellent tournament statistics can produce misleading recommendations if the AI does not correctly understand the underlying battle mechanics.

Therefore, the initial focus should be:

1. Document Pokémon Champions mechanics.
2. Document battle rules and regulations.
3. Implement accurate Stat Points calculations.
4. Document Speed, stat stages, damage, and Doubles mechanics.
5. Only then expand into competitive data collection and team analysis.

---

## Long-Term Goal

The ultimate objective is to build an AI-powered Pokémon Champions competitive assistant that acts as a knowledgeable team-building partner rather than a simple Pokémon information database.

It should be able to:

- Understand the current competitive environment.
- Identify viable strategies and team archetypes.
- Build teams around specific win conditions.
- Select appropriate Pokémon sets.
- Calculate damage and defensive benchmarks.
- Analyze Speed interactions.
- Identify weaknesses and problematic matchups.
- Suggest effective leads and opening strategies.
- Validate team legality.
- Explain its decisions using reliable data.
- Adapt recommendations when regulations and metagame trends change.

**The goal is not simply to find six strong Pokémon. It is to build a coherent team with a clear strategy, reliable answers to common threats, and a realistic plan for winning battles.**

---

## License & Data Attribution

This project uses information collected from external websites and data sources.

All original Pokémon-related intellectual property belongs to its respective owners, including Nintendo, The Pokémon Company, and Game Freak.

External datasets, statistics, and documentation remain subject to their respective sources' terms of use and attribution requirements.

This project is an independent fan-made development project and is not affiliated with or endorsed by Nintendo, The Pokémon Company, or Game Freak.