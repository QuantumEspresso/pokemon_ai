# Pokémon Champions — Battle Rules

## 1. Battle Formats

Pokémon Champions supports two primary battle formats:

### Singles
- Each side has one active Pokémon at a time.
- Players select a team according to the format's team-size rules.
- Pokémon battle one at a time, with switching used to change the active Pokémon.

### Doubles
- Each side has two active Pokémon at a time.
- Both active Pokémon can take actions during the same turn.
- Moves can target opponents, allies, the user, or the battlefield.
- Team positioning, partner synergy and turn order are important parts of battle strategy.

The exact team size and number of Pokémon selected for a battle depend on the selected format.

## 2. Team Structure

A competitive team consists of Pokémon registered before the battle.

The following terms should be kept distinct:
- **Battle Team** — the complete registered team.
- **Team Preview** — the stage in which players inspect the opposing team and make their selection.
- **Selected Pokémon** — Pokémon chosen from the registered team to participate in the battle.
- **Active Pokémon** — Pokémon currently on the battlefield.
- **Reserve Pokémon** — selected Pokémon that are not currently active.

In standard VGC Doubles:
- Each player registers six Pokémon.
- Each player selects four of the six for battle.
- Two selected Pokémon start on the battlefield.
- The remaining two selected Pokémon are reserves.
- A player normally wins by causing all four selected opposing Pokémon to faint, subject to the game's battle-ending rules.

Do not assume every Singles, Ranked or custom format uses the same team-selection structure.

## 3. Pokémon Levels and Stat Calculation

Pokémon Champions uses a fixed Level 50 stat baseline.

- All Pokémon used in Pokémon Champions have their stats calculated as if they were Level 50.
- This applies to Pokémon obtained directly in Pokémon Champions and Pokémon brought in from Pokémon HOME.
- A Pokémon's original level in another game does not affect its stat calculation in Pokémon Champions.
- Pokémon do not need to be levelled up before they can be used competitively.
- The game does not use the traditional levelling system for its competitive stat calculations.

**Important for the AI:** Always use Level 50 when calculating stats, damage or Speed in Pokémon Champions. Do not use a Pokémon's original level from Pokémon HOME or another game.

## 4. General Team Construction Rules

The following rules are part of the standard official VGC framework. They should not automatically be assumed to apply to every in-game mode or custom format.

### Species Clause
A team cannot contain two Pokémon with the same National Pokédex number. Different forms of the same species count as the same species.

Example: Two different Rotom forms cannot be used on the same team under this rule.

### Item Clause
No two Pokémon on the same team may hold the same item. Each Pokémon may hold one item, provided that the item is permitted by the selected format.

### Moves and Abilities
Pokémon may use moves and Abilities available to them through legitimate gameplay, subject to the restrictions of the selected format. This can include Hidden Abilities and event-exclusive moves or Abilities.

Availability through gameplay does not automatically mean that a move or Ability is legal in every format.

## 5. Mega Evolution

- A compatible Mega Stone is required.
- Mega Evolution availability depends on the selected format.
- Mega Evolution can change a Pokémon's form, stats, typing or Ability.
- The number of permitted Mega Evolutions per battle is determined by the applicable rules.

The AI must distinguish between Pokémon that can Mega Evolve in the game and Pokémon whose Mega Evolution is permitted in the selected format.

## 6. Format-Specific Restrictions

A battle format or Regulation Set can introduce additional restrictions concerning:
- permitted Pokémon and forms;
- banned or restricted Pokémon;
- held items;
- moves and Abilities;
- available battle mechanics;
- team size;
- the number of Pokémon selected for battle.

These restrictions must be maintained separately from the general battle rules.

A Pokémon being available in the game does not necessarily mean it is legal in every competitive format.

## 7. Ranked Battles vs Official VGC

### Ranked Battles
- Played through the in-game competitive ladder.
- Can include Singles and Doubles.
- Follow the rules and restrictions of the currently active in-game format.
- Team size and selection rules depend on the selected mode.

### Official VGC
- Uses the official tournament rules published by Play! Pokémon.
- Uses the Doubles format.
- Normally follows the six-Pokémon registration and four-Pokémon selection structure.
- Includes additional team construction and tournament requirements.

Official tournament documents and organiser announcements take precedence for tournament-specific procedures.

## 8. Rules Validation for AI

Before analysing or generating a team, identify:

1. Battle format (Singles, Doubles or another format).
2. Competition type (Ranked, official VGC or custom).
3. Team size.
4. Number of Pokémon selected for battle.
5. Whether Species Clause and Item Clause apply.
6. Whether any format-specific restrictions apply.
7. Which battle mechanics are available.

Always calculate Pokémon stats using the Level 50 baseline.

If the format is unknown, do not assume that standard VGC rules apply.

## 9. Important Terminology

| Term | Meaning |
|---|---|
| Battle Team | Complete registered team |
| Team Preview | Stage for inspecting teams and selecting Pokémon |
| Selected Pokémon | Pokémon chosen to participate in battle |
| Active Pokémon | Pokémon currently on the battlefield |
| Reserve Pokémon | Selected Pokémon not currently active |
| Species Clause | Restriction on duplicate National Pokédex numbers |
| Item Clause | Restriction on duplicate held items |
| Regulation Set | Format-specific rules and legality restrictions |
| Mega Evolution | Temporary transformation using a compatible Mega Stone |
| Level 50 baseline | Standard level used for all Pokémon stat calculations in Champions |

## Sources
- [Serebii — Pokémon Champions](https://www.serebii.net/pokemonchampions/)
- [Victory Road — Pokémon Champions Regulations](https://victoryroad.pro/champions-regulations/)
- [Official Play! Pokémon Rules and Resources](https://www.pokemon.com/us/play-pokemon/about/tournaments-rules-and-resources/)

**Document scope:** General battle structure, Pokémon levels and stat baseline, and general team construction concepts. Current Regulation Sets, permitted Pokémon and items, and tournament procedures are maintained separately.

Last reviewed: 2026-11-18.