# Pokémon Champions — Stat Points

## 1. Stat Points, not classic EVs

Pokémon Champions uses **Stat Points** to customise stats. They serve a role similar to EV investment in main-series games, but they are not the same system and must not be stored or calculated as EVs.

Current VGC.tools and Champions calculator references report:
- **66 total Stat Points** per Pokémon;
- **0–32 Stat Points** in any one stat;
- points are allocated across HP, Attack, Defense, Special Attack, Special Defense and Speed;
- each Stat Point adds directly into the stat formula's pre-level term;
- the standard competitive battle level is 50.

The 66-point total is a Champions rule, not the classic 510 EV budget. The classic 252-per-stat EV cap does not apply.

## 2. IVs

Current Champions references state that player-assigned IVs are not part of the normal build system and model all Pokémon as having **31 IVs in every stat** (perfect IVs).

For the AI:
- do not ask the user to allocate IVs for a normal Champions build;
- do not infer a hidden IV spread;
- use 31 as the stat-formula IV constant where the calculator requires it;
- keep IV fields separate from Stat Points in any imported main-series data.

## 3. Stat Alignment

Victory Road's tournament team-list terminology is **Stat Alignment**. It provides the familiar nature-like adjustment to non-HP stats: one stat is increased by 10% and another is decreased by 10%; neutral alignments do not modify stats.

Some third-party tools call this a nature. In Champions-facing output, prefer `Stat Alignment`, and map legacy nature names only as a compatibility alias.

HP is not increased or decreased by Stat Alignment.

## 4. Stat formula

VGC.tools publishes the following non-HP stat formula, using perfect IVs:

`floor((floor((2 × BaseStat + 31 + StatPoints) × Level / 100) + 5) × AlignmentModifier)`

Where:
- `BaseStat` is the species/form base stat;
- `31` is the fixed perfect-IV value;
- `StatPoints` is the investment in that stat (0–32);
- `Level` is the battle level (normally 50);
- `AlignmentModifier` is 1.1, 0.9 or 1.0.

For HP, use the HP-specific formula in the trusted calculator rather than applying the non-HP alignment multiplier. The HP formula follows the standard HP stat structure with the Champions Stat Point input; verify exact integer handling against the calculator before implementing it.

## 5. Building a spread

A valid spread must satisfy:

`sum(HP, Atk, Def, SpA, SpD, Spe) <= 66`

and each individual stat must satisfy:

`0 <= StatPoints[stat] <= 32`

A spread does not have to use all 66 points unless the chosen build benefits from doing so.

## 6. Stat Points versus EVs — compatibility

| Concept | Main-series EV system | Pokémon Champions |
|---|---|---|
| Training value | EVs | Stat Points |
| Total budget | 510 EVs | 66 Stat Points |
| Per-stat cap | 252 EVs | 32 Stat Points |
| IV assignment | Usually configurable | Treated as perfect (31) in current references |
| Stat nature terminology | Nature | Stat Alignment (nature-like) |

Do not convert 252 EVs to 32 Stat Points by simply copying the number. If importing an old team, translate the intended final stat goals using a Champions calculator.

## 7. AI validation

Reject or flag:
- any stat with more than 32 points;
- a total above 66;
- negative Stat Points;
- user-provided IVs that conflict with the standard Champions model;
- a Stat Alignment applied to HP.

## Sources

- [VGC.tools — Stats guide](https://vgc.tools/guides/stats)
- [Victory Road — Pokémon Champions Regulations](https://victoryroad.pro/champions-regulations/)
- [DexDB — Pokémon Champions Damage Calculator](https://dexdb.io/calc/)

**Last researched:** 2026-11-18. Confirm formula details against the current calculator after game updates.
