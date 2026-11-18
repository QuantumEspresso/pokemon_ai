# Pokémon Champions — Type Matchups

## 1\. Purpose and scope

This document describes the standard Pokémon type effectiveness system used in Pokémon Champions.

It contains:

- the complete type matchup chart for all 18 Pokémon types;
- descriptions of effectiveness categories;
- rules for calculating effectiveness against dual-type Pokémon.

The type chart describes the base effectiveness multiplier of a move against a target's type or types.

## 2\. Type effectiveness categories

Pokémon Champions uses the following effectiveness categories:

| Effectiveness | Multiplier | Description |
| --- | ---: | --- |
| No effect | ×0 | The move has no effect on the target. |
| Mostly Ineffective | ×0.25 | The move is resisted by both types of a dual-type target. |
| Not Very Effective | ×0.5 | The move is resisted by the target's type. |
| Neutral | ×1 | The move deals normal type-based damage. |
| Super Effective | ×2 | The move is super effective against one defending type. |
| Extremely Effective | ×4 | The move is super effective against both types of a dual-type target. |

## 3\. Complete type matchup chart

Attacking types are listed in rows. Defending types are listed in columns.

| Attack ↓ / Defense → | Normal | Fire | Water | Electric | Grass | Ice | Fighting | Poison | Ground | Flying | Psychic | Bug | Rock | Ghost | Dragon | Dark | Steel | Fairy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Normal** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0.5 | 0 | 1 | 1 | 0.5 | 1 |
| **Fire** | 1 | 0.5 | 0.5 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 0.5 | 1 | 0.5 | 1 | 2 | 1 |
| **Water** | 1 | 2 | 0.5 | 1 | 0.5 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 0.5 | 1 | 1 | 1 |
| **Electric** | 1 | 1 | 2 | 0.5 | 0.5 | 1 | 1 | 1 | 0 | 2 | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 |
| **Grass** | 1 | 0.5 | 2 | 1 | 0.5 | 1 | 1 | 0.5 | 2 | 0.5 | 1 | 0.5 | 2 | 1 | 0.5 | 1 | 0.5 | 1 |
| **Ice** | 1 | 0.5 | 0.5 | 1 | 2 | 0.5 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 0.5 | 1 |
| **Fighting** | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 0.5 | 1 | 0.5 | 0.5 | 0.5 | 2 | 0 | 1 | 2 | 2 | 0.5 |
| **Poison** | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 0.5 | 0.5 | 1 | 1 | 1 | 0.5 | 0.5 | 1 | 1 | 0 | 2 |
| **Ground** | 1 | 2 | 1 | 2 | 0.5 | 1 | 1 | 2 | 1 | 0 | 1 | 0.5 | 2 | 1 | 1 | 1 | 2 | 1 |
| **Flying** | 1 | 1 | 1 | 0.5 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 0.5 | 1 | 1 | 1 | 0.5 | 1 |
| **Psychic** | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 | 0 | 0.5 | 1 |
| **Bug** | 1 | 0.5 | 1 | 1 | 2 | 1 | 0.5 | 0.5 | 1 | 0.5 | 2 | 1 | 1 | 0.5 | 1 | 2 | 0.5 | 0.5 |
| **Rock** | 1 | 2 | 1 | 1 | 1 | 2 | 0.5 | 1 | 0.5 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 0.5 | 1 |
| **Ghost** | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 0.5 | 1 | 1 |
| **Dragon** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 0.5 | 0 |
| **Dark** | 1 | 1 | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 0.5 | 1 | 0.5 |
| **Steel** | 1 | 0.5 | 0.5 | 0.5 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 0.5 | 2 |
| **Fairy** | 1 | 0.5 | 1 | 1 | 1 | 1 | 2 | 0.5 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 0.5 | 1 |

Values represent the effectiveness multiplier:

- `0` = No effect
- `0.5` = Not Very Effective
- `1` = Neutral
- `2` = Super Effective

Values of `0.25` and `4` occur when effectiveness against both defending types is combined.

## 4\. Dual-type Pokémon

When a Pokémon has two types, the effectiveness of an incoming move is calculated separately against each type. The two multipliers are then multiplied together.

| First type multiplier | Second type multiplier | Combined multiplier | Result |
| ---: | ---: | ---: | --- |
| ×2 | ×2 | ×4 | Extremely Effective |
| ×2 | ×1 | ×2 | Super Effective |
| ×2 | ×0.5 | ×1 | Neutral |
| ×0.5 | ×0.5 | ×0.25 | Mostly Ineffective |
| ×0.5 | ×1 | ×0.5 | Not Very Effective |
| ×0.5 | ×2 | ×1 | Neutral |
| ×1 | ×1 | ×1 | Neutral |
| ×0 | Any value | ×0 | No effect |

### Examples

**Example A — Extremely Effective**

Target: Garchomp (Dragon/Ground)

Attack: Ice

- Ice against Dragon: ×2
- Ice against Ground: ×2
- Combined effectiveness: ×4

Result: Extremely Effective.

**Example B — Mostly Ineffective**

Target: Water/Dragon

Attack: Fire

- Fire against Water: ×0.5
- Fire against Dragon: ×0.5
- Combined effectiveness: ×0.25

Result: Mostly Ineffective.

**Example C — Neutral**

Target: Grass/Water

Attack: Fire

- Fire against Grass: ×2
- Fire against Water: ×0.5
- Combined effectiveness: ×1

Result: Neutral.

**Example D — No effect**

Target: Ground/Flying

Attack: Electric

- Electric against Ground: ×0
- Electric against Flying: ×2
- Combined effectiveness: ×0

Result: No effect.