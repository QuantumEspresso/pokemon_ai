# Pokémon Champions — Team-Building Guide

## 1. Choose the format first

Before building, define:
- Ranked Singles or Ranked Doubles;
- official VGC Doubles or a custom tournament;
- the applicable regulation and date;
- the registered team size and number selected for battle.

Do not use VGC assumptions for every in-game format. See `battle_rules.md`.

## 2. Build around a plan, not six isolated sets

A team should have a coherent win condition. Examples of broad archetypes include:
- balance: flexible offence and defence with safe switching;
- bulky offence: durable Pokémon that maintain pressure;
- hyper offence: fast pressure and setup;
- speed control: Tailwind, Trick Room, paralysis or priority;
- weather or terrain: a field setter plus beneficiaries;
- setup: create a safe turn for a Pokémon to boost;
- disruption: deny actions, alter targeting or weaken opposing attackers.

These are strategic categories, not a claim that every named archetype is equally viable in the current Champions metagame.

## 3. Core team roles

Evaluate whether the team has access to the following functions. A Pokémon can fill more than one role.

| Role | Purpose |
|---|---|
| Physical attacker | Applies damage using Attack |
| Special attacker | Applies damage using Special Attack |
| Physical wall | Takes physical attacks |
| Special wall | Takes special attacks |
| Speed control | Changes action order |
| Support | Enables allies with boosts, healing, screens or disruption |
| Pivot | Switches while maintaining momentum |
| Setup sweeper | Uses stat boosts to become a win condition |
| Priority user | Acts early within the turn's priority system |
| Field setter | Establishes weather or terrain |

Do not require exactly one Pokémon per role. Assess the functions covered by the full team.

## 4. Type and defensive coverage

Analyse both offensive coverage and defensive exposure:
- Can the team threaten common opposing types?
- Which types hit multiple team members super effectively?
- Does the team have immunities or resistances to important attacks?
- Can it switch safely when a key Pokémon is threatened?
- Does one defensive weakness become exploitable after the first knockout?

Type coverage alone is insufficient. Abilities, move coverage, speed, damage thresholds and regulation legality also matter.

## 5. Stat Point optimisation

Use Champions Stat Points:
- 66 total;
- maximum 32 in one stat;
- perfect IV assumption (31 in every stat);
- Stat Alignment instead of classic EV/nature assumptions.

Allocate points to meet explicit benchmarks:
- survive a known attack;
- secure a damage threshold or knockout;
- outspeed a target under the expected field conditions;
- survive residual damage or common spread attacks.

Do not copy a Scarlet/Violet EV spread directly. Recalculate it for Champions.

## 6. Doubles-specific evaluation

For Doubles, evaluate:
- lead pairs and backup pairs;
- how the team handles opposing speed control;
- Protect availability and safe positioning;
- partner support and redirection;
- spread-move damage;
- whether both active Pokémon can contribute in the same turn;
- the four-Pokémon selection from the six-member team.

A six-Pokémon roster can be balanced overall but still have poor four-Pokémon selections into a particular opponent.

## 7. Matchup analysis

For each likely opponent or archetype, record:
- preferred opposing leads;
- threats that outspeed or KO key members;
- defensive answers and their limitations;
- required team selection;
- a default opening plan;
- fallback plan if the lead matchup is unfavourable;
- win condition and resource to preserve.

A matchup score should be supported by damage calculations and realistic turn sequences, not type-chart coverage alone.

## 8. Data-driven improvement

Keep separate datasets for:
- in-game Ranked ladder usage;
- Pokémon Showdown usage;
- official tournament teams and results;
- community sample teams.

These populations are not interchangeable. Record source, date range, regulation, format, rank/event level and sample size. Never merge them into a single usage statistic without explicit weighting and provenance.

## 9. Suggested AI team-analysis output

For every proposed team, report:
1. format and regulation assumptions;
2. legality checks;
3. role coverage;
4. offensive type/move coverage;
5. defensive weaknesses and resistances;
6. Speed tiers and speed-control plan;
7. Stat Point spread rationale;
8. item and Species Clause checks;
9. lead pairs and four-Pokémon selection plans (Doubles);
10. major matchup risks;
11. confidence level and missing data.

## 10. Source and uncertainty discipline

Use:
- Victory Road for the general official VGC tournament framework;
- Serebii for game data and Ranked regulation pages;
- Champions-aware calculators/engines for damage and battle interactions;
- dated ladder/tournament sources for metagame evidence.

Mark unverified interactions. Never present an old regulation's legality list or usage statistics as current.

## Sources

- [Victory Road — Pokémon Champions Regulations](https://victoryroad.pro/champions-regulations/)
- [Serebii — Pokémon Champions](https://www.serebii.net/pokemonchampions/)
- [DexDB — Pokémon Champions Damage Calculator](https://dexdb.io/calc/)
- [DexDB — Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- [VGC.tools — Stats guide](https://vgc.tools/guides/stats)

**Last researched:** 2026-11-18.
