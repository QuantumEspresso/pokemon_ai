# Pokémon Champions — Stat Stages

## 1. What stat stages are

Stat stages are temporary in-battle modifiers applied to a Pokémon's combat stats. They are distinct from permanent build customisation through Stat Points and Stat Alignment.

The familiar stage range is **−6 to +6**. Stages can be changed by moves, Abilities and other battle effects. Switching normally resets a Pokémon's own stages; field effects and side conditions are separate.

Combat stats affected include Attack, Defense, Special Attack, Special Defense and Speed. Accuracy and evasion also use stages, but they are separate hidden battle values and should not be treated as one of the six displayed stats.

## 2. Standard stat-stage multipliers

For Attack, Defense, Special Attack, Special Defense and Speed, the standard multiplier is:

- If stage >= 0: `(2 + stage) / 2`
- If stage < 0: `2 / (2 - stage)`

| Stage | Multiplier |
|---:|---:|
| −6 | 0.25× |
| −5 | 2/7× |
| −4 | 1/3× |
| −3 | 0.4× |
| −2 | 0.5× |
| −1 | 2/3× |
| 0 | 1× |
| +1 | 1.5× |
| +2 | 2× |
| +3 | 2.5× |
| +4 | 3× |
| +5 | 3.5× |
| +6 | 4× |

This table is documented by VGC.tools and matches the conventional Pokémon stage system. Keep Champions-specific Ability and move interactions separate.

## 3. Common examples

- Swords Dance: raises Attack by two stages.
- Nasty Plot: raises Special Attack by two stages.
- Agility: raises Speed by two stages.
- Intimidate: lowers opposing Attack, subject to immunity or prevention effects.

These are examples of familiar move/Ability behaviour; check Champions move and Ability records for exact availability and any game-specific changes.

## 4. Accuracy and evasion

Accuracy and evasion are not ordinary damage stats. A common stage model combines the user's accuracy stage and the target's evasion stage, clamps the difference to the stage range, and applies the accuracy/evasion multiplier. Use the Champions-aware engine for exact hit chance and exceptions.

Do not multiply a move's listed accuracy by an arbitrary stat-stage multiplier without accounting for both sides' stages and move-specific effects.

## 5. Critical hits and stages

Critical hits can interact with positive defensive stages and negative offensive stages differently from an ordinary hit. Do not implement critical-hit stage bypass rules from memory; use the Champions-aware damage engine and test the interaction.

## 6. AI requirements

The team analyzer should track current battle stages independently for every active Pokémon:
- Attack;
- Defense;
- Special Attack;
- Special Defense;
- Speed;
- accuracy;
- evasion.

Stage changes should be clamped to the legal range. A stage reset, Haze-like effect, switching event or Ability may alter the state; implement those effects from the move/Ability data.

## Sources

- [VGC.tools — Stats guide](https://vgc.tools/guides/stats)
- [DexDB — Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- [DexDB — Pokémon battle glossary](https://dexdb.io/glossary/)

**Last researched:** 2026-11-18. The stage multiplier table is a general battle rule; move availability and edge-case interactions remain Champions-specific.
