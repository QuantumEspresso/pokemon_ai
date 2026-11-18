# Pokémon Champions — Weather and Terrain

## 1. Scope and terminology

Weather and terrain are global battle conditions. They modify damage, defensive stats, status interactions, recovery, move behaviour and certain Abilities.

Pokémon Champions has four standard weather conditions:

- Harsh Sunlight
- Rain
- Sandstorm
- Snow

It also has four standard terrains:

- Electric Terrain
- Grassy Terrain
- Misty Terrain
- Psychic Terrain

Weather and terrain occupy separate field slots. One weather condition and one terrain condition can be active simultaneously.

**Important distinction:**

- Weather generally affects the entire battlefield. Individual effects may apply only to particular types or moves.
- Terrain affects grounded Pokémon. A Pokémon that is not grounded does not receive the terrain's ordinary benefits or restrictions.
- Weather and terrain do not directly change a Pokémon's permanent stats or stat stages. Their effects are applied separately during battle calculations.

This document describes the general Champions rules. Regulation-specific Pokémon availability and the current roster of setters must be read from the relevant datasets.

---

## 2. Weather duration and general rules

### 2.1 Duration

Weather set by a move or an Ability normally lasts **5 turns**.

The corresponding weather-extending items increase this to **8 turns**:

| Weather | Extending item |
|---|---|
| Harsh Sunlight | Heat Rock |
| Rain | Damp Rock |
| Sandstorm | Smooth Rock |
| Snow | Icy Rock |

The extension applies when the Pokémon setting the weather holds the matching item. The rule applies to weather set by moves and Abilities.

The game text and Champions mechanics ledger support these durations. The simulator implements the turn counts, although published independent in-game turn counts for the extender items are limited.

### 2.2 Weather replacement

Only one weather condition can be active at a time.

Setting a different weather replaces the previous one. For example:

1. Drought activates and creates Harsh Sunlight.
2. An opposing Pokémon uses Rain Dance.
3. Rain replaces Harsh Sunlight.

The AI must not treat different weather conditions as simultaneously active.

### 2.3 Weather persists after its setter leaves

The Champions simulator models weather as continuing for its remaining duration even after the Pokémon that created it switches out.

This behaviour is simulator-supported, but the mechanics ledger does not classify it as independently confirmed by an in-game test. Mark it as a simulator-derived rule rather than an independently verified game rule.

### 2.4 Weather suppression

Cloud Nine suppresses the effects of weather.

Important distinction:

- Suppressing weather does not mean removing the weather condition.
- The weather's duration continues to count down while its effects are suppressed.
- When the suppression ends, the remaining weather can become effective again.

The AI must distinguish between:
- no weather active;
- weather active and effective;
- weather active but suppressed.

Do not represent all three states as `weather = null`.

---

## 3. Harsh Sunlight

### 3.1 Standard effects

Harsh Sunlight changes the damage dealt by two move types:

| Effect | Modifier |
|---|---:|
| Fire-type move damage | ×1.5 |
| Water-type move damage | ×0.5 |

These are damage modifiers, not changes to the move's listed base power.

Example:

A 100-power Fire-type move receives the weather damage modifier and is treated as having an effective weather-adjusted power of 150 before the remaining damage calculation modifiers.

A 100-power Water-type move receives the opposite modifier and is treated as having an effective weather-adjusted power of 50.

The actual damage still depends on the complete damage formula, including STAB, defensive stats, type effectiveness, random damage rolls and other modifiers.

### 3.2 Move interactions

Weather can also change the behaviour of individual moves.

The AI should account for the following standard interactions when the move is present in the Champions move database:

| Move | Interaction with Harsh Sunlight |
|---|---|
| Solar Beam | Does not require its normal charging turn |
| Solar Blade | Does not require its normal charging turn |
| Growth | Receives its weather-specific stat-boost effect |
| Synthesis | Restores more HP |
| Morning Sun | Restores more HP |
| Moonlight | Restores more HP |
| Weather Ball | Becomes a Fire-type move and receives the weather-dependent power increase |

For the recovery moves, the standard weather-dependent healing values are:

| Weather state | HP restored |
|---|---:|
| No weather or ordinary weather | 1/2 max HP |
| Harsh Sunlight | 2/3 max HP |
| Rain, Sandstorm or Snow | 1/4 max HP |

These move-specific interactions should be verified against the Champions move implementation before being treated as authoritative. The game's weather description itself only guarantees the Fire- and Water-type damage changes.

### 3.3 Strategic implications

Harsh Sunlight is useful for:

- increasing Fire-type offensive pressure;
- weakening opposing Water-type attacks;
- supporting Fire-type sweepers;
- reducing the opportunity cost of Solar Beam and Solar Blade;
- improving the recovery of Pokémon using weather-dependent healing moves.

It can also hurt a team that relies heavily on Water-type attacks.

When evaluating a Sun team, the AI should calculate both the offensive benefit and the defensive cost of activating sunlight.

---

## 4. Rain

### 4.1 Standard effects

Rain changes the damage dealt by Water- and Fire-type moves:

| Effect | Modifier |
|---|---:|
| Water-type move damage | ×1.5 |
| Fire-type move damage | ×0.5 |

As with sunlight, these are damage modifiers and must be incorporated into the damage calculation rather than permanently changing move base power.

### 4.2 Move interactions

Rain can affect the accuracy or behaviour of certain moves.

| Move | Interaction with Rain |
|---|---|
| Thunder | Normally bypasses its usual accuracy check in Rain |
| Hurricane | Normally bypasses its usual accuracy check in Rain |
| Weather Ball | Becomes a Water-type move and receives the weather-dependent power increase |
| Solar Beam | Its normal charging/attack behaviour is affected by weather |
| Solar Blade | Its normal charging/attack behaviour is affected by weather |
| Synthesis | Restores less HP |
| Morning Sun | Restores less HP |
| Moonlight | Restores less HP |

The standard accuracy interaction for Thunder and Hurricane is 100% accuracy in Rain. Their accuracy is reduced outside Rain according to their normal move data.

Do not assume every move with a weather-related description behaves identically. For example, Electro Shot has its own charging behaviour and should be modelled from its Champions-specific move implementation.

### 4.3 Strategic implications

Rain is useful for:

- strengthening Water-type attacks;
- reducing incoming Fire-type damage;
- supporting Water-type attackers;
- enabling reliable Thunder and Hurricane use;
- disrupting opposing Sun teams.

Rain can weaken a team's own Fire-type attacks. The AI should account for this when selecting coverage moves and evaluating matchups.

---

## 5. Sandstorm

### 5.1 Standard effects

Sandstorm has two main effects.

**Residual damage**

At the end of each turn, Pokémon that are not Rock-, Ground- or Steel-type take damage equal to:

`1/16` of their maximum HP.

Rock-, Ground- and Steel-type Pokémon are immune to this Sandstorm damage.

**Special Defense increase**

Rock-type Pokémon receive a 50% increase to their Special Defense stat while Sandstorm is active.

| Pokémon type | Sandstorm damage immunity | Special Defense boost |
|---|---|---|
| Rock | Yes | ×1.5 |
| Ground | Yes | No |
| Steel | Yes | No |
| Other types | No | No |

A dual-type Pokémon is immune to Sandstorm damage if at least one of its types is Rock, Ground or Steel.

The Special Defense bonus is specifically for Rock-type Pokémon, not all three immune types.

### 5.2 Damage and defensive calculations

The Sandstorm Special Defense increase must be applied when calculating incoming special damage against a Rock-type Pokémon.

It does not increase:

- Defense;
- Attack;
- Special Attack;
- Speed;
- the Special Defense of Ground- or Steel-type Pokémon.

The residual damage is a separate end-of-turn effect. It should not be added to the normal attack damage formula.

### 5.3 Strategic implications

Sandstorm can be useful for:

- gradually wearing down opponents;
- improving the special bulk of Rock-type Pokémon;
- supporting teams that can ignore or mitigate residual damage;
- punishing teams that rely on repeated switching or prolonged positioning.

A Sandstorm team should be evaluated for how many of its Pokémon take residual damage. A team does not automatically benefit from Sandstorm just because it contains a Rock-type attacker.

---

## 6. Snow

### 6.1 Standard effects

Snow increases the Defense stat of Ice-type Pokémon by 50%.

| Pokémon type | Defense boost |
|---|---|
| Ice | ×1.5 |
| Other types | No boost |

A dual-type Pokémon receives the boost if one of its types is Ice.

Snow does **not** deal residual damage at the end of each turn.

This is an important distinction from the older Hail weather mechanic in some Pokémon games. Do not implement Hail's residual damage in Pokémon Champions.

### 6.2 Defensive calculations

The Snow bonus applies to the Defense stat, so it improves the physical bulk of Ice-type Pokémon.

It does not increase:

- Special Defense;
- Attack;
- Special Attack;
- Speed.

The bonus must be incorporated into the defensive calculation before calculating incoming physical damage.

### 6.3 Move interactions

Snow can also interact with individual moves.

The AI should check Champions move data for weather-dependent behaviour, including:

- Weather Ball changing its type and power;
- moves whose accuracy or damage depends on Snow;
- recovery moves whose healing changes with weather.

Do not automatically import every Hail-related interaction from the main series. Only apply an interaction when the move's Champions data or a verified Champions mechanics source supports it.

### 6.4 Strategic implications

Snow is primarily a defensive weather condition.

It can be useful for:

- increasing the physical durability of Ice-type Pokémon;
- supporting Ice-type defensive cores;
- weakening opposing weather conditions through replacement;
- creating opportunities for Ice-type attackers to survive physical attacks they would otherwise not withstand.

Do not treat Snow as an offensive damage boost for Ice-type attacks. Its documented base effect is a Defense increase.

---

## 7. Terrain — general rules

### 7.1 Duration

All four standard terrains last **5 turns**.

Terrain Extender increases the duration to **8 turns**.

| Terrain | Extending item |
|---|---|
| Electric Terrain | Terrain Extender |
| Grassy Terrain | Terrain Extender |
| Misty Terrain | Terrain Extender |
| Psychic Terrain | Terrain Extender |

As with weather, the duration is supported by Champions game text and the mechanics ledger. The simulator implements the turn count.

### 7.2 Grounded Pokémon

Terrain affects grounded Pokémon only.

The AI must determine whether each Pokémon is grounded at the moment an effect is evaluated.

A Pokémon may be ungrounded because of:

- Flying typing;
- Levitate;
- a move or volatile effect that makes it airborne;
- another Champions-specific effect that changes its grounding state.

A Pokémon may become grounded through effects such as Gravity or a specific move or status effect.

Do not use type alone as the complete grounding test.

For example:
- A Flying-type Pokémon is normally not grounded.
- A Pokémon with Levitate is normally not grounded.
- A Pokémon affected by Gravity becomes grounded.
- A Pokémon with a specific grounded status may be affected by terrain even if it would normally be airborne.

Some position states explicitly make a Pokémon unaffected by terrain. Sky-High, Underground, Submerged and Concealed are examples of such states in the Champions battle-condition data.

### 7.3 Terrain replacement

Only one terrain can be active at a time.

Setting a different terrain replaces the previous terrain.

Weather and terrain are separate conditions, so setting terrain does not remove weather, and setting weather does not remove terrain.

The AI should track both independently.

---

## 8. Electric Terrain

### 8.1 Standard effects

Electric Terrain has two documented effects on grounded Pokémon:

| Effect | Result |
|---|---|
| Electric-type move power | ×1.3 |
| Sleep | Grounded Pokémon cannot fall asleep |

The power increase applies to Electric-type moves used by grounded Pokémon.

The sleep protection applies to grounded Pokémon. It does not protect an ungrounded Pokémon merely because Electric Terrain is active.

### 8.2 Move interactions

Electric Terrain interacts with certain moves.

**Rising Voltage**

Rising Voltage receives a terrain-dependent power increase when its target is grounded and Electric Terrain is active.

The standard interaction doubles its power against a grounded target.

This is a separate move-specific effect. Do not confuse it with the general ×1.3 Electric-type terrain modifier.

**Other Electric-type moves**

Electric-type moves used by grounded Pokémon receive the standard ×1.3 terrain boost.

The AI must check the move's type and the user's grounded state.

### 8.3 Ability interactions

Electric Terrain can activate or support Abilities whose descriptions explicitly reference Electric Terrain.

Examples include:

- Quark Drive;
- Hadron Engine.

The AI must read the actual Ability data rather than assuming that every Electric-type Pokémon benefits from the terrain.

### 8.4 Strategic implications

Electric Terrain is useful for:

- strengthening grounded Electric-type attackers;
- preventing sleep on grounded teammates;
- supporting terrain-dependent Abilities;
- enabling stronger Rising Voltage attacks.

It is less useful when the team's primary Electric-type attackers are ungrounded, or when the opponent does not rely on sleep.

---

## 9. Grassy Terrain

### 9.1 Standard effects

Grassy Terrain has two documented effects on grounded Pokémon:

| Effect | Result |
|---|---|
| Grass-type move power | ×1.3 |
| End-of-turn recovery | 1/16 max HP |

The recovery occurs at the end of each turn while the terrain is active.

Only grounded Pokémon receive this terrain recovery.

### 9.2 Move interactions

Grassy Terrain has a special interaction with certain moves.

**Earthquake**

In the standard terrain interaction, Earthquake deals reduced damage while Grassy Terrain is active.

Do not apply this reduction to every Ground-type move. It is a move-specific interaction and must be checked by move identity.

**Grassy Glide**

Grassy Glide receives increased priority when used under Grassy Terrain, subject to its Champions move data and applicable conditions.

This is a priority interaction, not a damage multiplier.

**Other Grass-type moves**

Grass-type moves used by grounded Pokémon receive the standard ×1.3 terrain boost.

### 9.3 Ability interactions

Grassy Terrain can activate or support Abilities that explicitly reference it.

For example, Grassy Surge creates Grassy Terrain when the Pokémon with that Ability enters battle.

The AI should identify both the terrain setter and any teammates whose Abilities or moves benefit from the terrain.

### 9.4 Strategic implications

Grassy Terrain is useful for:

- increasing the damage of grounded Grass-type attackers;
- providing passive recovery;
- improving the team's ability to survive longer battles;
- enabling terrain-dependent moves and Abilities.

However, it can also weaken the team's own Earthquake damage. This is important when evaluating teams that use Ground-type spread attacks.

---

## 10. Misty Terrain

### 10.1 Standard effects

Misty Terrain has three documented effects on grounded Pokémon:

1. Grounded Pokémon are immune to status conditions.
2. Grounded Pokémon cannot become confused.
3. Dragon-type moves used against grounded Pokémon deal half damage.

| Effect | Result |
|---|---|
| Status conditions | Prevented on grounded Pokémon |
| Confusion | Prevented on grounded Pokémon |
| Incoming Dragon-type move damage | ×0.5 against grounded targets |

The Dragon damage reduction is defensive: it depends on the target being grounded.

Do not require the attacking Pokémon to be grounded.

### 10.2 Status protection

The status protection applies to grounded targets.

The AI should check this protection when evaluating attempts to inflict status conditions, including:

- burn;
- paralysis;
- poison;
- badly poisoned;
- sleep;
- freeze;
- confusion.

Confusion is listed separately in the terrain description and should not be omitted from the implementation.

The protection does not mean that an already existing status condition is automatically removed when Misty Terrain appears. Treat terrain protection and status removal as separate mechanics.

### 10.3 Ability and item interactions

Misty Terrain can interact with terrain-related held items and other effects.

The AI must check the relevant Champions item and Ability records rather than assuming that every terrain-related effect is identical across all four terrains.

### 10.4 Strategic implications

Misty Terrain is primarily defensive.

It is useful for:

- protecting grounded teammates from status conditions;
- reducing incoming Dragon-type damage;
- preventing confusion;
- supporting setup strategies that would otherwise be disrupted by status.

It is less effective when the team's important Pokémon are ungrounded or when the opponent relies mainly on direct damage rather than status.

---

## 11. Psychic Terrain

### 11.1 Standard effects

Psychic Terrain has two documented effects on grounded Pokémon:

| Effect | Result |
|---|---|
| Psychic-type move power | ×1.3 |
| Priority moves | Grounded Pokémon are immune to priority moves |

The Psychic-type power increase applies to Psychic-type moves used by grounded Pokémon.

The priority protection is defensive and applies to grounded targets.

### 11.2 Priority move protection

Psychic Terrain prevents priority moves from affecting grounded Pokémon.

This is not the same as lowering the priority of the opponent's move.

The move retains its normal priority value. The terrain instead prevents the move from affecting a protected grounded target.

The AI must therefore evaluate:

1. The move's effective priority.
2. Whether the intended target is grounded.
3. Whether the move is directed at that target or affects the field.
4. Whether the move has a special exception in the Champions implementation.

Do not implement Psychic Terrain as a universal cancellation of all moves with positive priority. It is a protection applied to grounded targets, and self-targeting or field-affecting moves must be handled according to their actual targeting behaviour.

### 11.3 Move interactions

**Expanding Force**

Expanding Force has a special interaction with Psychic Terrain in the standard move mechanics.

The AI should check the Champions move implementation for its terrain-dependent power and targeting behaviour. Do not assume the standard main-series spread behaviour without confirming that the Champions implementation supports it.

**Other Psychic-type moves**

Psychic-type moves used by grounded Pokémon receive the standard ×1.3 terrain boost.

### 11.4 Ability interactions

Psychic Terrain can be set by Psychic Surge.

The AI should read the Ability database to determine which Pokémon can set it in the currently relevant roster.

### 11.5 Strategic implications

Psychic Terrain is useful for:

- strengthening grounded Psychic-type attackers;
- protecting grounded teammates from opposing priority attacks;
- supporting offensive strategies that rely on moving before the opponent;
- reducing the opponent's ability to finish weakened Pokémon with priority moves.

It is less useful when the team's primary attackers are ungrounded or when the opponent relies on ordinary Speed-based attacks rather than priority.

---

## 12. Special weather interactions

Some Champions-specific mechanics do not fit neatly into the four standard weather descriptions.

These must be modelled as separate Ability or effect rules rather than changing the definition of the weather itself.

### 12.1 Mega Sol

The Champions mechanics ledger documents special weather-related behaviour for Mega Sol.

Reported interactions include:

- Water-type moves used by a Pokémon with Mega Sol deal reduced damage as if Harsh Sunlight were active.
- Fire-type moves used by a Pokémon with Mega Sol receive the sunlight damage increase even when ordinary weather is not Harsh Sunlight.
- Weather Ball becomes Fire-type with 100 base power for a Pokémon with Mega Sol.
- Thunder and Hurricane have special accuracy behaviour associated with this Ability.
- The Ability has additional interactions with Sandstorm and Snow defensive bonuses.

These are Ability-specific exceptions. Do not implement them by globally changing the active weather state.

The mechanics ledger marks several of these details as reported or disputed, so they should be represented as separately sourced rules with confidence metadata.

### 12.2 Cloud Nine

Cloud Nine suppresses ordinary weather effects while it is active.

The weather itself remains active and continues counting down.

The AI must not confuse weather suppression with weather replacement or removal.

---

## 13. Weather and terrain interactions

Weather and terrain can be active simultaneously.

For example:

- Rain + Electric Terrain;
- Harsh Sunlight + Grassy Terrain;
- Sandstorm + Psychic Terrain;
- Snow + Misty Terrain.

The AI must apply both sets of rules when relevant.

Example:

A grounded Electric-type Pokémon using an Electric-type move in Electric Terrain while Rain is active can benefit from the Electric Terrain power increase. Rain does not independently increase Electric-type move damage.

Example:

A grounded Grass-type Pokémon in Grassy Terrain can receive the terrain's passive recovery at the end of the turn while Sandstorm is also active. Whether it takes Sandstorm damage depends on its type combination.

### 13.1 Modifier stacking

Do not combine weather and terrain effects by replacing one with the other.

Each modifier must be applied at the appropriate stage of the damage calculation.

The damage calculator must also preserve the Champions-specific order of operations and rounding rules documented in `damage_calculation.md`.

### 13.2 Grounding must be evaluated per Pokémon

The same terrain can affect one Pokémon but not another.

For example, under Electric Terrain:

- a grounded Electric-type Pokémon receives the Electric move power increase;
- a grounded non-Electric Pokémon receives sleep protection but no Electric move power increase;
- an ungrounded Electric-type Pokémon does not receive the terrain's ordinary benefits.

This distinction is essential for accurate damage and matchup analysis.

---

## 14. AI implementation requirements

The AI should represent weather and terrain as separate structured field states.

Suggested structure:

```json
{
  "field": {
    "weather": {
      "type": "rain",
      "remaining_turns": 3,
      "source": "drizzle",
      "suppressed": false
    },
    "terrain": {
      "type": "electric",
      "remaining_turns": 4,
      "source": "electric_terrain",
      "extender_used": false
    }
  }
}
```

The values above are illustrative, not a live battle state.

### 14.1 Required weather logic

The AI must be able to:

- distinguish all four weather conditions;
- apply Fire- and Water-type damage modifiers;
- apply Sandstorm residual damage;
- apply Rock-type Special Defense during Sandstorm;
- apply Ice-type Defense during Snow;
- account for weather duration;
- account for weather-extending items;
- replace one weather condition with another;
- distinguish suppressed weather from absent weather;
- apply move-specific weather interactions;
- apply Ability-specific weather exceptions.

### 14.2 Required terrain logic

The AI must be able to:

- distinguish all four terrains;
- determine whether each Pokémon is grounded;
- apply the appropriate type-specific move power increase;
- apply Electric Terrain's sleep protection;
- apply Grassy Terrain's end-of-turn healing;
- apply Misty Terrain's status and confusion protection;
- apply Misty Terrain's Dragon damage reduction;
- apply Psychic Terrain's priority protection;
- apply move-specific terrain interactions;
- account for terrain duration and Terrain Extender;
- replace one terrain with another.

### 14.3 Recommended calculation sequence

For each move:

1. Determine the current weather and terrain.
2. Determine whether the user and target are grounded.
3. Check whether weather effects are suppressed.
4. Check whether the move has a weather-specific interaction.
5. Check whether the move has a terrain-specific interaction.
6. Apply relevant Ability and item effects.
7. Calculate damage using the Champions damage formula.
8. Apply any relevant defensive terrain or weather effects to the correct Pokémon.
9. Resolve the move and its secondary effects.
10. At the end of the turn, process residual damage, healing and remaining field durations according to the Champions engine's resolution order.

Do not apply end-of-turn effects as part of the direct damage formula.

### 14.4 Data model recommendations

Keep the following information separate:

- base weather effects;
- base terrain effects;
- move-specific weather interactions;
- move-specific terrain interactions;
- Ability-specific weather interactions;
- Ability-specific terrain interactions;
- item-based duration modifiers;
- grounding rules;
- field-condition duration and replacement rules.

This avoids hardcoding all weather and terrain behaviour into a single damage formula.

---

## 15. Evidence and confidence

Use the following evidence levels when implementing the rules:

- **Confirmed by game text:** the game explicitly describes the effect.
- **Settled in the mechanics ledger:** the ledger considers the rule settled based on game text, reports or engine evidence.
- **Simulator-supported:** the Champions simulator implements the behaviour, but independent in-game confirmation is limited.
- **Reported or disputed:** player tests exist, but the result or interpretation is not fully settled.
- **Unverified:** do not use as a definitive rule.

Examples:

| Rule | Evidence status |
|---|---|
| Sun boosts Fire damage and halves Water damage | Confirmed by game text |
| Rain boosts Water damage and halves Fire damage | Confirmed by game text |
| Sandstorm damages non-Rock/Ground/Steel Pokémon and boosts Rock Sp. Def | Confirmed by game text |
| Snow boosts Ice-type Defense | Confirmed by game text |
| Electric, Grassy, Misty and Psychic Terrain effects | Confirmed by game text |
| Weather duration: 5 turns | Settled in mechanics ledger |
| Weather Rock duration: 8 turns | Settled in mechanics ledger |
| Terrain duration: 5 turns | Settled in mechanics ledger |
| Terrain Extender duration: 8 turns | Settled in mechanics ledger |
| Weather persists after setter leaves | Simulator-supported; not independently confirmed |
| Cloud Nine suppresses weather without stopping countdown | Simulator-supported |
| Mega Sol special weather interactions | Reported; individual details have different confidence levels |

---

## Sources

- DexDB — [Weather and terrain in Pokémon Champions](https://dexdb.io/champions/mechanics/weather-terrain/)
- DexDB — [Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- DexDB — [Pokémon Champions Damage Calculator](https://dexdb.io/calc/)
- Pokémon Zone — [Weather in Pokémon Champions](https://www.pokemon-zone.com/champions/weather/)
- Pokémon Zone — [Terrains in Pokémon Champions](https://www.pokemon-zone.com/champions/terrain/)
- Championspedia — [Pokémon Champions battle conditions](https://thechampionspedia.com/battle-conditions)

**Last researched:** 2026-11-18.

**Implementation note:** The documented base weather and terrain effects should be treated as the authoritative starting point. Move-specific, Ability-specific and simulator-derived interactions must remain separate rules with their own evidence and confidence levels. Do not silently import mechanics from another Pokémon game.