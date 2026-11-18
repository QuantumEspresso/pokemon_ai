# Pokémon Champions — Doubles Mechanics

## 1. Doubles field

In Doubles, each side can have two active Pokémon at the same time. Each player selects four Pokémon from the registered team for the match; two start on the field and the other two are reserves.

A move may target:
- the user;
- the user's ally;
- one opposing Pokémon;
- both opponents / all adjacent Pokémon;
- the field or a side of the field.

Use the move's actual target field from the Champions move database. Do not infer targeting solely from its name.

## 2. Spread moves

A spread move can affect multiple Pokémon at once. DexDB's Champions damage calculator documents a **0.75× damage modifier** when a spread move hits multiple targets.

Special targeting cases exist. If only one target can be hit, a spread move may deal full damage to that target. Some moves have bespoke multi-target behaviour; Dragon Darts, for example, distributes its hits according to its specific targeting rules.

The damage engine must know how many valid targets were actually hit, not merely that the move is classified as a spread move.

## 3. Protect and guard moves

Protect blocks most moves aimed at the user for the turn. Champions mechanics references state that consecutive uses of Protect and its family reduce the next success chance to **one third**.

Protect is not absolute against every move or effect. Check move flags and exceptions in the engine. Protect-like moves have priority; current Champions move data lists Protect/Detect/Endure at +4 and Fake Out/guard moves at +3.

## 4. Fake Out

Fake Out is a high-priority move used to deny an opponent's action by flinching it, subject to its move-specific use restrictions. Current Champions references list it at +3 priority. The exact first-turn/reuse behaviour has been discussed in community testing; use the current move engine rather than assuming every historical detail.

## 5. Helping Hand

Helping Hand targets an ally and boosts that ally's attack for the turn. Current Champions move data lists it at **+5 priority**. The exact damage modifier should be read from the Champions damage engine; do not hardcode a generic multiplier if a specific implementation is available.

## 6. Redirection

Redirection moves and Abilities can change which Pokémon an opposing single-target move hits. Examples from the broader Pokémon ruleset include Follow Me, Rage Powder and Lightning Rod-like effects, but the AI must first verify that the effect and Pokémon are available in Champions.

The target-selection stage must occur before damage calculation. A move's intended target may not be its final target after redirection, immunity or other targeting effects.

## 7. Ally positioning and switching

Switching, pivot moves, Ally Switch and effects that alter targeting can change the board state. Do not treat the two active slots as interchangeable without accounting for slot-specific targeting and move effects. Confirm Ally Switch availability and behaviour in the Champions move database before relying on it.

## 8. Partner effects

Doubles calculations can depend on the partner:
- Helping Hand;
- Friend Guard and similar damage modifiers;
- Intimidate or other field-entry Abilities;
- redirection;
- partner-targeted healing or boosts;
- spread damage affecting both foes;
- side conditions such as screens and Tailwind.

DexDB's 2v2 calculator explicitly models partner effects such as Helping Hand, Friend Guard and a second Intimidate. Use a 2v2 calculation for realistic damage estimates; isolated 1v1 calculations can be misleading.

## 9. Team-building implications

A Doubles team should be evaluated in pairs and four-Pokémon selections, not only as six independent Pokémon. Consider:
- lead pair synergy;
- speed control;
- defensive switching and positioning;
- protection and safe setup turns;
- redirection and partner support;
- spread-move pressure;
- coverage against common opposing pairs;
- whether the selected four can still function if the preferred lead is unavailable.

## Sources

- [Victory Road — Pokémon Champions Regulations](https://victoryroad.pro/champions-regulations/)
- [DexDB — Pokémon Champions Damage Calculator](https://dexdb.io/calc/)
- [DexDB — Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- [DexDB — Pokémon battle glossary](https://dexdb.io/glossary/)
- [Serebii — Pokémon Champions moves](https://www.serebii.net/pokemonchampions/moves.shtml)

**Last researched:** 2026-11-18. Verify the availability and exact behaviour of individual Doubles moves/Abilities against current Champions data.
