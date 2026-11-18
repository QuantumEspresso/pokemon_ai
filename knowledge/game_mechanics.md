# Pokémon Champions — Game Mechanics

> **Scope:** General battle-system reference for Pokémon Champions. This document describes mechanics that are broadly stable; format-specific legality belongs in `battle_rules.md`, and regulation-specific Pokémon/move/item legality belongs in separate regulation data.
>
> **Evidence policy:** `Confirmed` means supported by official rules, in-game text, or corroborated current game data. `Reported` means community research or a simulator implementation supports it but direct game verification is incomplete. `Unknown` means do not assume the main-series rule applies.

## 1. Battle model

Pokémon Champions is a turn-based Pokémon battle game with both Singles and Doubles modes. In Doubles, two Pokémon per side are active simultaneously. Ranked rules and official VGC tournament rules are related but not identical; see `battle_rules.md`.

Battles use level 50 stats for competitive formats covered by current rules. Teams are built from up to six Pokémon, with a smaller number selected for the actual match.

## 2. Pokémon configuration

A competitive Pokémon configuration includes:
- species and form;
- Ability;
- four selected moves (subject to game availability and move legality);
- held item;
- Stat Alignment;
- Stat Point allocation;
- Mega Stone and Mega Evolution eligibility, where applicable.

Champions uses **Stat Points**, not the classic EV training system. Champions also does not expose player-assigned IVs in the same way as main-series games; current competitive references model every stat as having a perfect IV value of 31. See `stat_points.md`.

The in-game terminology used by Victory Road is **Stat Alignment**. Some community tools call this a nature because the familiar +10% / -10% stat adjustment pattern is similar. Do not confuse the terminology with EVs or IVs.

## 3. Mega Evolution

Current Champions regulations can allow Mega Evolution. The current mechanics reference reports:
- each side can Mega Evolve once per battle;
- the Pokémon must hold its own compatible Mega Stone.

Mega eligibility is regulation-specific. A Pokémon being present in the game does not automatically mean its Mega form is legal in a particular regulation.

Do not assume other battle gimmicks from Scarlet/Violet or earlier games (Terastallization, Dynamax, Z-Moves) are available in Champions unless a current source explicitly confirms them.

## 4. Moves, Abilities, items and battle effects

Move power, accuracy, PP, effects and learnsets can differ from the main-series games and can change through patches. Use the Champions-specific move database and the current game data rather than copying Scarlet/Violet values.

Abilities and held items can modify:
- damage dealt or received;
- Speed and turn order;
- weather and terrain;
- status conditions;
- targeting, redirection and protection;
- switching and end-of-turn effects.

A simulator's implementation is useful evidence, but it is not automatically proof that every obscure interaction has been verified in the live game.

## 5. Evidence labels for the AI

Every nontrivial mechanic should carry one of these labels in internal reasoning or structured data:

| Label | Meaning | AI behaviour |
|---|---|---|
| `confirmed` | Official rule, current in-game text, or direct reproducible verification | May use as a rule |
| `reported` | Community testing or a maintained simulator implementation | May use with a confidence note |
| `unknown` | No reliable Champions-specific confirmation | Do not assert; request testing or use a clearly labelled provisional assumption |
| `format_specific` | True only for a named format or regulation | Check the requested format first |

## 6. Do not import rules blindly

The main-series games are a useful starting point, not an authoritative Champions specification. In particular, verify before assuming:
- exact damage rounding and modifier order;
- status durations and probabilities;
- weather and terrain durations;
- move priority and turn-order edge cases;
- spread-move damage and protection interactions;
- the exact rules for official events versus in-game Ranked Battles.

## Sources

- [Victory Road — Pokémon Champions Regulations](https://victoryroad.pro/champions-regulations/)
- [Serebii — Pokémon Champions](https://www.serebii.net/pokemonchampions/)
- [DexDB — Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- [DexDB — Pokémon Champions glossary](https://dexdb.io/glossary/)
- [VGC.tools — Stats guide](https://vgc.tools/guides/stats)

**Last researched:** 2026-11-18. Re-check patch-sensitive details before using this document as an executable rules engine.
