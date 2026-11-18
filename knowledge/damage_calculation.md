# Pokémon Champions — Damage Calculation

## 1. Scope and Reference Implementation

This document describes the damage calculation used by Pokémon Champions.

The reference implementation is the Pokémon Champions mechanics module in [`@smogon/calc`](https://github.com/smogon/damage-calc), specifically:

- `calc/src/mechanics/champions.ts`
- `calc/src/mechanics/util.ts`

The Champions calculator at [DexDB](https://dexdb.io/calc/) uses `@smogon/calc` with Champions-specific mechanics.

**Important:** Do not implement the Scarlet & Violet formula by simply copying its assumptions or data. Champions uses its own move data, Stat Points, abilities, items and mechanics. The calculation pipeline is based on Generation IX battle mechanics, with Champions-specific handling.

All Pokémon use the Level 50 stat baseline.

---

## 2. Overview: Exact Calculation Order

For a normal damaging move, the calculation follows this order:

1. Determine the move's actual type, category and base power.
2. Determine the effective Attack and Defense stats, including stat stages and relevant effects.
3. Calculate base damage.
4. Apply the Doubles spread modifier, if applicable.
5. Apply weather damage modification.
6. Apply the critical-hit modifier.
7. Apply one of the 16 random damage rolls.
8. Apply STAB.
9. Apply type effectiveness.
10. Apply the burn damage reduction, if applicable.
11. Apply special damage interactions such as damage through Protect, if applicable.
12. Apply the chained final modifiers from Abilities, items, screens and other effects.
13. Apply the final rounding and integer limits.

**The order must be preserved.** Moving a modifier to another stage can change the final damage by one or more HP.

---

## 3. Base Damage Formula

The standard base damage formula is:

```text
BaseDamage = floor(
    floor(
        floor((2 × Level / 5) + 2)
        × MovePower
        × Attack
        / Defense
    )
    / 50
    + 2
)
```

For Pokémon Champions, Level is always 50.

Therefore:

```text
floor((2 × 50 / 5) + 2) = 22
```

The formula can be simplified to:

```text
BaseDamage = floor(
    floor(22 × MovePower × Attack / Defense) / 50 + 2
)
```

### Variables

| Variable | Meaning |
|---|---|
| Level | 50 |
| MovePower | Effective move base power after move-specific changes |
| Attack | Effective offensive stat |
| Defense | Effective defensive stat |
| floor() | Round down to the nearest integer |

### Which stats are used?

| Move category | Offensive stat | Defensive stat |
|---|---|---|
| Physical | Attack | Defense |
| Special | Special Attack | Special Defense |

Some moves override this behaviour:
- **Body Press** uses the user's Defense as its offensive stat.
- **Foul Play** uses the target's Attack as the offensive stat.
- Some moves can dynamically choose their category or defensive stat.

The calculator must use the move's actual calculation rules, not only its displayed category.

### Example

Assume:

- Level: 50
- Move Power: 80
- Attack: 150
- Defense: 100

```text
BaseDamage = floor(
    floor(22 × 80 × 150 / 100) / 50 + 2
)

BaseDamage = floor(2640 / 50 + 2)

BaseDamage = floor(54.8)

BaseDamage = 54
```

The result before damage modifiers is **54**.

---

## 4. Move Base Power Modifiers

The move's listed base power is not always its effective base power.

Before calculating damage, apply any conditions that change the move's power.

Examples include:

| Condition | Effect |
|---|---|
| Facade while the user has a major status condition | Power ×2 |
| Venoshock against a poisoned target | Power ×2 |
| Lash Out after the user's stats have been lowered | Power ×2 |
| Acrobatics when the user has no held item | Power ×2 |
| Weather Ball during applicable weather | Power ×2 |
| Terrain Pulse when the user is grounded and terrain is active | Power ×2 |
| Rising Voltage against a grounded target in Electric Terrain | Power ×2 |
| Expanding Force under its applicable Psychic Terrain conditions | Move-specific power and targeting changes |
| Knock Off against a target holding a removable item | Move-specific power increase |
| Eruption / Water Spout | Power depends on the user's current HP |
| Flail / Reversal | Power depends on the user's current HP |
| Triple Axel | Power changes with each consecutive hit |

Abilities and held items can also modify move power.

Examples:
- Iron Fist boosts punching moves.
- Reckless boosts moves with recoil or crash damage.
- Type Gems boost the power of a matching-type move.
- Matching type-boosting items provide a smaller power increase.

The exact conditions and exceptions are move-specific. The AI must use the Champions move database and the reference mechanics implementation rather than applying a universal multiplier.

---

## 5. Attack and Defense Stat Modifiers

The Attack and Defense values in the base formula are not necessarily the Pokémon's unmodified stats.

They must account for:

### 5.1 Stat stages

Stat stages range from -6 to +6.

For modern Pokémon battle mechanics, the multipliers are:

| Stage | Multiplier |
|---:|---:|
| -6 | 2/8 |
| -5 | 2/7 |
| -4 | 2/6 |
| -3 | 2/5 |
| -2 | 2/4 |
| -1 | 2/3 |
| 0 | 2/2 |
| +1 | 3/2 |
| +2 | 4/2 |
| +3 | 5/2 |
| +4 | 6/2 |
| +5 | 7/2 |
| +6 | 8/2 |

The resulting stat is rounded down according to the engine's stat calculation.

### 5.2 Critical hits and stat stages

A critical hit changes how stat stages are handled:

- The attacker's negative offensive stat stages are ignored.
- The defender's positive defensive stat stages are ignored.
- The opposite stat stages are not automatically ignored.

Abilities such as Unaware can also change whether the opponent's stat stages are considered.

### 5.3 Ability and item modifiers

Abilities and items can modify the effective offensive or defensive stat before the base damage formula.

Examples:

| Effect | Modifier |
|---|---:|
| Huge Power / Pure Power | Physical Attack ×2 |
| Hustle | Physical Attack ×1.5 |
| Guts | Physical Attack ×1.5 while affected by a major status condition |
| Solar Power | Special Attack ×1.5 in Sun |
| Water Bubble | Water move's offensive damage calculation is boosted; Fire damage against the holder is reduced |
| Fur Coat | Physical Defense ×2 |
| Marvel Scale | Physical Defense ×1.5 while affected by a major status condition |
| Grass Pelt | Physical Defense ×1.5 in Grassy Terrain |

These are examples, not an exhaustive list. Some effects modify the stat itself, while others modify move power or final damage. Their calculation stage matters.

### 5.4 Weather-based defensive bonuses

Some weather effects modify defensive stats directly:

- Sandstorm: Rock-type Pokémon receive a ×1.5 Special Defense bonus.
- Snow: Ice-type Pokémon receive a ×1.5 Defense bonus.

These are defensive stat modifications, not general damage multipliers.

---

## 6. Spread Damage in Doubles

Moves that target multiple Pokémon can receive a spread damage modifier.

```text
Spread Modifier = 0.75
```

This means the move deals 75% of its normal damage to each affected target.

Example:

```text
Damage before spread modifier = 100

100 × 0.75 = 75
```

The modifier applies to qualifying spread moves in Doubles when they hit multiple targets.

If only one target can actually be hit, the move can deal full damage instead.

The calculator must distinguish between:
- a move that targets multiple Pokémon;
- a move that targets one Pokémon;
- a spread move that can only hit one available target.

Do not apply the spread modifier to every move simply because the battle is Doubles.

---

## 7. Weather Damage Modifiers

Weather modifies the base damage before the critical-hit and random-roll stages.

| Weather | Move type | Modifier |
|---|---|---:|
| Sun | Fire | ×1.5 |
| Sun | Water | ×0.5 |
| Rain | Water | ×1.5 |
| Rain | Fire | ×0.5 |
| Other weather | Other types | No general damage modifier |

These are damage modifiers, not move base power changes.

Weather can also affect Abilities, move power and defensive stats. Those effects must be calculated separately.

For example, Sandstorm's Special Defense bonus for Rock-type Pokémon is handled during defensive stat calculation, not as a damage modifier.

---

## 8. Critical Hits

A critical hit applies:

```text
Critical Modifier = 1.5
```

The modifier is applied to base damage after the spread and weather modifiers.

A critical hit also changes stat-stage handling:
- The attacker's negative Attack or Special Attack stages are ignored.
- The defender's positive Defense or Special Defense stages are ignored.

In the Champions reference mechanics, critical hits also bypass the damage reduction from Reflect, Light Screen and Aurora Veil.

Other Ability and item effects must be checked individually. A critical hit does not automatically ignore every defensive effect.

---

## 9. Random Damage Rolls

**Pokémon Champions uses 16 possible random damage rolls.**

The random multiplier is an integer percentage from 85% through 100%.

It is not a continuous random number between 0.9 and 1.1.

For each damage calculation, the engine evaluates:

```text
RandomMultiplier = (85 + i) / 100

where i = 0, 1, 2, ..., 15
```

The resulting damage is:

```text
RandomDamage = floor(BaseDamageAfterCritical × (85 + i) / 100)
```

### All 16 possible rolls

| Roll | Multiplier |
|---:|---:|
| 1 | 85% |
| 2 | 86% |
| 3 | 87% |
| 4 | 88% |
| 5 | 89% |
| 6 | 90% |
| 7 | 91% |
| 8 | 92% |
| 9 | 93% |
| 10 | 94% |
| 11 | 95% |
| 12 | 96% |
| 13 | 97% |
| 14 | 98% |
| 15 | 99% |
| 16 | 100% |

Each roll has an equal probability of:

```text
1 / 16 = 6.25%
```

The random roll is applied **after the critical-hit modifier and before STAB**.

### Example

If damage before the random roll is 100:

```text
Minimum = floor(100 × 0.85) = 85
Maximum = floor(100 × 1.00) = 100
```

The possible results are 85, 86, 87, ..., 100.

The calculator must evaluate all 16 values independently. It must not calculate only an average or use a single random floating-point value.

---

## 10. STAB — Same-Type Attack Bonus

STAB is applied when the move's type matches one of the user's types.

### Standard STAB

```text
STAB = ×1.5
```

Example:

```text
Damage before STAB = 100

100 × 1.5 = 150
```

### Adaptability

Adaptability increases the STAB modifier:

```text
STAB with Adaptability = ×2.0
```

Example:

```text
Damage before STAB = 100

100 × 2.0 = 200
```

The calculator must determine STAB from the user's actual type at the time of the move.

Abilities that change a move's type, such as Aerilate, Pixilate, Refrigerate or Dragonize, can change whether STAB applies.

**Champions implementation note:** Do not implement Terastallization or Stellar STAB as active Champions mechanics unless the game rules and reference implementation explicitly add them. They belong to other game formats.

---

## 11. Type Effectiveness

Type effectiveness is applied after STAB.

The effectiveness of a move is determined by its type against the target's defensive type combination.

### Standard effectiveness values

| Result | Multiplier |
|---|---:|
| Immune | ×0 |
| Double resisted | ×0.25 |
| Resisted | ×0.5 |
| Neutral | ×1 |
| Super effective | ×2 |
| Double super effective | ×4 |

For a Pokémon with two types, multiply the effectiveness against both types.

Example:

```text
Move effectiveness against first type = ×2
Move effectiveness against second type = ×0.5

Total effectiveness = 2 × 0.5 = 1
```

The move deals neutral damage overall.

The type chart must be stored as structured data and loaded from the Champions-compatible type database.

Abilities, items, move-specific exceptions and changes to a Pokémon's type can alter the result.

An immunity results in zero damage unless a specific mechanic overrides that immunity.

---

## 12. Burn Damage Reduction

Burn reduces damage from Physical moves:

```text
Burn Modifier = ×0.5
```

This reduction applies after type effectiveness.

Exceptions include:
- Guts: the usual burn damage reduction does not apply.
- Facade: the usual burn damage reduction does not apply.

Burn does not halve Special move damage.

---

## 13. Final Damage Modifiers

After the previous stages, the game applies other applicable damage modifiers.

These include effects from:
- Reflect;
- Light Screen;
- Aurora Veil;
- Helping Hand;
- Friend Guard;
- offensive Abilities;
- defensive Abilities;
- held items;
- type-resist berries;
- move-specific effects;
- Protect interactions;
- other field and battle effects.

### Important modifier examples

| Effect | Modifier |
|---|---:|
| Reflect in Singles | ×0.5 |
| Light Screen in Singles | ×0.5 |
| Reflect in Doubles | approximately ×0.667 |
| Light Screen in Doubles | approximately ×0.667 |
| Aurora Veil in Singles | ×0.5 |
| Aurora Veil in Doubles | approximately ×0.667 |
| Helping Hand | ×1.5 |
| Friend Guard | ×0.75 |
| Tinted Lens against a resisted target | ×2 |
| Solid Rock / Filter / Prism Armor against super-effective damage | ×0.75 |
| Expert Belt against a super-effective target | ×1.2 |
| Life Orb | ×1.3 |
| Matching type-resist berry | ×0.5 |

The table gives common values. It is not a replacement for the complete Ability, item and field-effect implementation.

### Screens

- Reflect reduces Physical damage.
- Light Screen reduces Special damage.
- Aurora Veil reduces both.
- In Doubles, the reduction is approximately 1/3 rather than 1/2.
- Critical hits bypass the screen reduction in the Champions reference implementation.
- Infiltrator can bypass screens.

Reflect, Light Screen and Aurora Veil do not stack with each other as separate reductions.

### Protect

Protect normally prevents a move from dealing damage.

Some Abilities and move interactions can bypass Protect. The calculator must check whether the move actually penetrates the protection.

The Champions reference implementation also has a special ×0.25 damage interaction for applicable moves that hit through Protect. This is not a general modifier for ordinary attacks.

---

## 14. Modifier Arithmetic and Rounding

Rounding is essential for exact calculations.

The reference implementation uses fixed-point arithmetic for chained modifiers rather than multiplying all floating-point values together.

### 14.1 Fixed-point scale

The modifier scale is:

```text
4096 = 1.0
```

Examples:

| Multiplier | Fixed-point value |
|---:|---:|
| ×0.25 | 1024 |
| ×0.5 | 2048 |
| ×0.667 approximately | 2732 |
| ×0.75 | 3072 |
| ×1.0 | 4096 |
| ×1.2 | 4915 |
| ×1.3 | 5325 |
| ×1.5 | 6144 |
| ×2.0 | 8192 |

### 14.2 Chaining modifiers

Modifiers in the same modifier group are chained one at a time.

The reference calculation is equivalent to:

```text
M = 4096

for modifier in modifiers:
    M = (M × modifier + 2048) >> 12
```

The result is clamped to the limits used by the reference implementation.

Do not simply multiply all modifiers as floating-point numbers and round once at the end.

### 14.3 Pokémon rounding

The reference implementation uses a special rounding rule called `pokeRound`:

```text
If fractional part > 0.5:
    round up
Otherwise:
    round down
```

Therefore:

```text
1.4 -> 1
1.5 -> 1
1.6 -> 2
```

A value ending in exactly `.5` is rounded down.

Other calculation stages explicitly use `floor()`. Do not replace every rounding operation with `pokeRound()`.

### 14.4 Integer overflow

The reference implementation also models 16-bit and 32-bit overflow in relevant arithmetic operations.

For exact compatibility, use the same integer handling as `@smogon/calc`. Ordinary floating-point calculations may produce different results in edge cases.

---

## 15. Complete Final Damage Pseudocode

The following pseudocode describes the main damage pipeline for a normal damaging move.

It intentionally leaves move-specific power, stat and final modifier calculation as separate functions because those functions depend on the actual move, Pokémon, Ability, item and field state.

```python
def calculate_damage_rolls(
    level,
    move_power,
    attack,
    defense,
    spread_modifier,
    weather_modifier,
    critical,
    stab_modifier,
    type_effectiveness,
    burned,
    final_modifier
):
    level_factor = floor((2 * level) / 5) + 2

    base = floor(
        floor(level_factor * move_power * attack / defense) / 50 + 2
    )

    if spread_modifier != 1:
        base = poke_round(base * spread_modifier)

    if weather_modifier != 1:
        base = poke_round(base * weather_modifier)

    if critical:
        base = floor(base * 1.5)

    results = []

    for roll in range(85, 101):
        damage = floor(base * roll / 100)

        if stab_modifier != 1:
            damage = poke_round(damage * stab_modifier)

        damage = floor(damage * type_effectiveness)

        if burned:
            damage = floor(damage / 2)

        damage = poke_round(max(1, damage) * final_modifier)

        results.append(damage)

    return results
```

**Implementation warning:** This is a readable representation of the calculation order, not a drop-in replacement for the reference engine. An exact implementation must also reproduce:
- fixed-point modifier chaining;
- exact intermediate rounding;
- Champions-specific move power and stat calculations;
- the actual final modifier chain;
- immunity and Protect handling;
- special moves and fixed-damage effects;
- integer overflow behaviour.

---

## 16. Worked Example: Full Calculation

Assume the following conditions:

- Level: 50
- Move Power: 80
- Attack: 150
- Defense: 100
- The move matches the user's type.
- The target has neutral type effectiveness.
- No weather, burn, critical hit, spread modifier or other effects.

### Step 1 — Base damage

```text
BaseDamage = floor(
    floor(22 × 80 × 150 / 100) / 50 + 2
)

BaseDamage = 54
```

### Step 2 — Random roll

Minimum roll:

```text
floor(54 × 0.85) = 45
```

Maximum roll:

```text
floor(54 × 1.00) = 54
```

### Step 3 — STAB

The move receives ×1.5 STAB.

Minimum:

```text
pokeRound(45 × 1.5) = 67
```

Maximum:

```text
pokeRound(54 × 1.5) = 81
```

### Step 4 — Type effectiveness

The target is neutral to the move:

```text
×1.0
```

No damage change.

### Final result

```text
Damage range = 67–81 HP
```

There are 16 possible damage rolls. The calculator should retain the full distribution rather than only the minimum and maximum.

---

## 17. Special Damage Cases

Not every damaging move uses the ordinary damage pipeline.

The calculator must handle these separately:

### Fixed damage
Some moves deal a fixed amount of damage or a fixed amount based on the user's level.

Examples include:
- Seismic Toss;
- Night Shade;
- Dragon Rage;
- Sonic Boom.

### HP-based damage
Some moves deal damage based on the target's current HP or another HP-related condition.

Examples include:
- Super Fang and similar moves;
- moves whose power depends on the user's current HP, such as Eruption and Water Spout.

### Multi-hit moves
Each hit must be calculated according to the move's rules.

The total damage is not always equal to a single-hit result multiplied by the number of hits. Some moves change power between hits, and certain Abilities or effects can change stats or conditions during the sequence.

### Recoil, drain and secondary effects
Recoil and HP recovery are not part of the direct damage formula. They must be calculated after the move's damage is determined.

---

## 18. Damage Ranges and KO Probability

The calculator should store all 16 possible damage results.

For a single-hit move, if the target has `CurrentHP`, the KO probability is:

```text
KO probability =
    number of rolls where damage >= CurrentHP
    / 16
```

For example, if 12 of the 16 rolls deal enough damage to knock out the target:

```text
KO probability = 12 / 16 = 75%
```

For multi-hit moves, calculate the possible total damage combinations according to the number of hits and the move's individual hit rules.

Do not estimate KO probability using average damage.

Useful outputs include:
- minimum damage;
- maximum damage;
- damage as a percentage of target HP;
- guaranteed KO;
- guaranteed survival;
- probability of a one-hit KO;
- probability of a two-hit KO;
- probability of a KO after a specified number of hits.

---

## 19. Implementation Requirements for This Project

The damage calculator should follow these rules:

1. Always use the Pokémon Champions Level 50 stat baseline.
2. Calculate Champions stats from Stat Points and Stat Alignment, not traditional EV spreads.
3. Use the actual Champions move power, category, type and move-specific effects.
4. Apply stat stages before calculating base damage.
5. Apply spread, weather and critical modifiers in the correct order.
6. Evaluate all 16 random rolls from 85% to 100%.
7. Apply STAB before type effectiveness.
8. Apply burn after type effectiveness.
9. Apply final modifiers using fixed-point arithmetic and the correct rounding.
10. Handle immunities, fixed-damage moves, multi-hit moves and special move effects separately.
11. Keep all Ability, item, weather, terrain and screen interactions data-driven where possible.
12. Validate results against a pinned version of `@smogon/calc` and known in-game calculations.

### Reference engine

Use the Champions-specific implementation in:

- [`champions.ts`](https://github.com/smogon/damage-calc/blob/master/calc/src/mechanics/champions.ts)
- [`util.ts`](https://github.com/smogon/damage-calc/blob/master/calc/src/mechanics/util.ts)

Record the exact engine version or commit used by the project. If the reference implementation changes, rerun the test suite.

---

## Sources

- [Smogon — Pokémon Damage Calculator repository](https://github.com/smogon/damage-calc)
- [Smogon — Champions mechanics implementation](https://github.com/smogon/damage-calc/blob/master/calc/src/mechanics/champions.ts)
- [Smogon — Damage calculation utilities](https://github.com/smogon/damage-calc/blob/master/calc/src/mechanics/util.ts)
- [DexDB — Pokémon Champions Damage Calculator](https://dexdb.io/calc/)
- [DexDB — Pokémon Champions mechanics](https://dexdb.io/champions/mechanics/)

**Document scope:** Detailed damage calculation mechanics. Current Regulation Set restrictions and the current legal Pokémon or item pool are maintained separately.

Last researched: 2026-11-18.