# Pokémon Champions — Field Effects

## 1. Scope

This document describes battle effects that are not ordinary weather or terrain. These effects can apply to:

- one side of the battlefield;
- the opposing side;
- the entire battlefield;
- a specific active position;
- a Pokémon entering battle;
- a Pokémon or position after a delayed effect resolves.

They are separate from weather, terrain, individual status conditions and stat stages.

The AI must not represent all of them as one generic field modifier. Each effect needs its own scope, duration, activation conditions, resolution rules and removal conditions.

### 1.1 Evidence and availability labels

Use the following labels when interpreting this document:

- **Champions-listed:** The effect appears in a Pokémon Champions battle-effects or move database.
- **Champions-reported:** A Champions-specific source describes the effect, but its exact implementation needs further confirmation.
- **Reference-only:** The mechanic is known from another Pokémon game, but Champions availability or behaviour has not been established.
- **Unavailable:** The relevant move or mechanic is currently listed as unavailable in Champions.
- **Needs verification:** The effect is listed, but one or more implementation details have not been independently confirmed.

Do not automatically enable a Reference-only or Needs verification mechanic in the battle simulator.

---

## 2. Classification of field effects

| Category | Examples | Scope |
|---|---|---|
| Defensive screens | Reflect, Light Screen, Aurora Veil | One side |
| Status protection | Safeguard | One side |
| Speed control | Tailwind, Trick Room | One side or whole field, depending on effect |
| Entry hazards | Stealth Rock, Spikes, Toxic Spikes, Sticky Web | One side |
| Room effects | Magic Room, Wonder Room | Whole field |
| Gravity | Gravity | Whole field |
| Switching restrictions | Fairy Lock | Whole field |
| Delayed recovery | Wish | Specific position |
| Delayed attack | Future Attack | Specific position |
| Move restriction | Sealing Off | Opposing Pokémon |
| Pledge combinations | Sea of Fire, Rainbow, Swamp | One side |

Weather and terrain are documented separately in `weather_and_terrain.md`.

---

# PART I — SIDE CONDITIONS

## 3. Reflect

**Scope:** User's side of the battlefield.

**Effect:** Reduces incoming physical damage.

| Battle format | Damage received |
|---|---:|
| Singles | ×0.5 |
| Doubles | ×2/3 |

Reflect protects Pokémon on the side that created it, not just the Pokémon that used the move.

### 3.1 Duration

The standard Champions description gives Reflect a duration of 5 turns.

The turn counter should be stored on the protected side, not on the Pokémon that created the effect.

### 3.2 Damage calculation

Reflect applies to physical damage.

It does not reduce:
- special damage;
- fixed damage that does not use the ordinary physical damage calculation;
- damage that explicitly ignores screen effects.

The AI must identify the move's damage category before applying Reflect.

### 3.3 Interactions

- Light Screen can be active at the same time.
- Aurora Veil can be active as a separate effect.
- Infiltrator can bypass Reflect when the Pokémon uses an affected move.
- Screen Cleaner removes Reflect, Light Screen and Aurora Veil when its user enters battle.
- Psychic Fangs, Brick Break and Raging Bull can remove screens.
- Defog is listed as removing Reflect and other side conditions.

### 3.4 Strategic implications

Reflect is useful against physical attackers and physical spread damage.

The AI should evaluate:
- the opposing team's physical damage output;
- the expected number of turns Reflect will remain active;
- whether the opponent has a screen-removal move;
- whether the team benefits more from Reflect or another support action.

**Availability:** Champions-listed.

---

## 4. Light Screen

**Scope:** User's side of the battlefield.

**Effect:** Reduces incoming special damage.

| Battle format | Damage received |
|---|---:|
| Singles | ×0.5 |
| Doubles | ×2/3 |

### 4.1 Duration

The standard Champions description gives Light Screen a duration of 5 turns.

The duration belongs to the protected side.

### 4.2 Damage calculation

Light Screen applies to special damage.

It does not reduce:
- physical damage;
- unrelated residual damage;
- fixed damage that does not use the ordinary special damage calculation;
- damage that explicitly ignores screen effects.

### 4.3 Interactions

- Reflect can coexist with Light Screen.
- Aurora Veil is a separate screen effect.
- Infiltrator can bypass Light Screen.
- Screen Cleaner removes Light Screen, Reflect and Aurora Veil.
- Psychic Fangs, Brick Break and Raging Bull can remove screens.
- Defog is listed as a screen-removal effect.

### 4.4 Strategic implications

Light Screen is useful against special attackers, especially when the team needs additional time to set up or maintain a defensive position.

The AI should distinguish physical and special damage rather than applying Light Screen as a universal damage reduction.

**Availability:** Champions-listed.

---

## 5. Aurora Veil

**Scope:** User's side of the battlefield.

**Effect:** Reduces both physical and special incoming damage.

| Battle format | Damage received |
|---|---:|
| Singles | ×0.5 |
| Doubles | ×2/3 |

Aurora Veil combines the defensive purpose of Reflect and Light Screen into one effect.

### 5.1 Duration

The standard Champions description gives Aurora Veil a duration of 5 turns.

### 5.2 Weather requirement

In the traditional Pokémon implementation, Aurora Veil can only be established during hail or snow.

Do not assume this requirement is identical in Champions without checking the Champions move implementation. The Champions field-effect description confirms the defensive effect but does not, by itself, establish every activation restriction.

### 5.3 Interactions

- Screen Cleaner removes Aurora Veil.
- Infiltrator can bypass Aurora Veil.
- Psychic Fangs, Brick Break and Raging Bull can remove screens.
- Defog is listed as a removal effect.
- Reflect and Light Screen are separate effects and must not be silently overwritten by Aurora Veil.

### 5.4 Strategic implications

Aurora Veil is valuable because one action can improve both physical and special survivability.

The AI should compare the value of Aurora Veil with using Reflect and Light Screen separately.

**Availability:** Champions-listed. Activation requirements: Needs verification.

---

## 6. Safeguard

**Scope:** User's side of the battlefield.

**Effect:** Protects Pokémon on the side from status conditions and confusion.

The Champions description states that protected Pokémon are immune to status conditions and cannot become confused.

### 6.1 What it protects against

The AI should check Safeguard when an opponent attempts to inflict:

- burn;
- paralysis;
- poison;
- badly poisoned;
- sleep;
- freeze;
- confusion.

Do not treat Safeguard as a healing effect. It does not automatically remove a status condition that was already present when Safeguard became active.

### 6.2 Duration

The standard Champions description identifies Safeguard as a side condition. Its exact turn counter should be read from the Champions implementation or move data.

Do not hardcode a duration from another generation if the Champions source does not confirm it.

### 6.3 Interactions

The AI should distinguish Safeguard from Misty Terrain:

- Safeguard is attached to one side.
- Misty Terrain affects grounded Pokémon on the field.
- Safeguard does not require the protected Pokémon to be grounded.
- Misty Terrain also has a Dragon-type damage reduction effect.

### 6.4 Strategic implications

Safeguard is useful against teams relying on status disruption or confusion.

**Availability:** Champions-listed.

---

## 7. Tailwind

**Scope:** User's side of the battlefield.

**Effect:** Doubles the Speed stat of Pokémon on the side that established Tailwind.

### 7.1 Duration

Tailwind lasts 4 turns in Champions.

The duration belongs to the side, not to the Pokémon that used Tailwind.

Switching out the original setter does not make the effect a Pokémon-specific stat change.

### 7.2 Speed calculation

Tailwind doubles the effective Speed used for turn order.

It is not a permanent Speed-stage increase.

The AI should keep the Tailwind modifier separate from:
- base Speed;
- Stat Points;
- stat stages;
- paralysis;
- Choice Scarf or other item effects;
- Trick Room.

Tailwind does not change move priority.

### 7.3 Interactions

- Trick Room can reverse the Speed order while Tailwind is active.
- Tailwind does not cancel Trick Room.
- If both sides have Tailwind, both sides receive their respective Speed increase.
- A Pokémon switching into the side with active Tailwind benefits from the remaining duration.

### 7.4 Strategic implications

Tailwind is a team-wide speed-control tool.

The AI should evaluate:
- which Pokémon gain important Speed thresholds;
- whether Tailwind lets the team outspeed specific threats;
- whether the opponent can establish Trick Room;
- how many useful turns remain after Tailwind is activated.

**Availability:** Champions-listed. Duration: Champions mechanics data.

---

## 8. Trick Room

**Scope:** Whole battlefield.

**Effect:** Reverses Speed order within the same move-priority bracket.

Slower Pokémon act before faster Pokémon when Trick Room is active.

### 8.1 Duration

Trick Room lasts 5 turns.

The activation turn counts toward its duration according to the battle engine's turn-resolution rules.

### 8.2 Priority interaction

Trick Room does not reverse move priority.

For example:
- a +1 priority move still acts before a 0 priority move;
- a 0 priority move still acts before a -1 priority move;
- Speed order is reversed only between actions within the same priority bracket.

The AI must calculate priority before applying the Trick Room Speed ordering.

### 8.3 Interaction with Tailwind

Tailwind and Trick Room can coexist.

The AI must not remove one effect when the other is activated.

It should calculate effective Speed with the active Speed modifiers and then apply the reversed Speed ordering for actions in the same priority bracket.

### 8.4 Strategic implications

Trick Room benefits Pokémon with low effective Speed and can disrupt teams built around conventional Speed control.

The AI should evaluate:
- the team's Speed distribution;
- the opponent's Speed distribution;
- the remaining Trick Room duration;
- priority moves that bypass the usual Speed comparison;
- whether the team can protect its Trick Room setter.

**Availability:** Champions-listed.

---

# PART II — ENTRY HAZARDS

## 9. General entry-hazard model

Entry hazards are side conditions that affect Pokémon when they enter the battlefield.

They are not ordinary end-of-turn effects.

The AI must evaluate hazards whenever a Pokémon enters an affected side, including:
- voluntary switches;
- forced switches;
- replacement after a Pokémon is knocked out;
- other entry events supported by the battle engine.

Hazards are attached to a side, not to an individual Pokémon.

The four principal entry hazards are:

1. Stealth Rock
2. Spikes
3. Toxic Spikes
4. Sticky Web

Each side can have its own hazard state.

---

## 10. Stealth Rock

**Scope:** Opposing side.

**Effect:** Damages Pokémon when they enter battle.

The damage depends on the incoming Pokémon's type effectiveness against Rock.

### 10.1 Damage calculation

The standard calculation is:

`1/8 max HP × Rock-type effectiveness`

| Rock effectiveness against target | Entry damage |
|---|---:|
| 4× | 1/2 max HP |
| 2× | 1/4 max HP |
| 1× | 1/8 max HP |
| 1/2× | 1/16 max HP |
| 1/4× | 1/32 max HP |
| 0× | No damage |

Stealth Rock is not a layered hazard. Setting it again does not increase its damage.

### 10.2 Grounding

Stealth Rock is not restricted to grounded Pokémon in the same way as Spikes.

Flying-type Pokémon and Pokémon with Levitate can still be affected by Stealth Rock.

Do not use the Spikes grounding immunity for Stealth Rock.

### 10.3 Strategic implications

Stealth Rock is particularly effective against Pokémon weak to Rock.

The AI should calculate the exact entry damage for each possible switch-in and account for the cumulative cost of repeated switching.

**Availability:** Champions-listed.

---

## 11. Spikes

**Scope:** Opposing side.

**Effect:** Damages grounded Pokémon when they enter battle.

Spikes can be stacked up to three layers.

### 11.1 Layer system

The standard Spikes damage values are:

| Layers | Entry damage |
|---|---:|
| 1 | 1/8 max HP |
| 2 | 1/6 max HP |
| 3 | 1/4 max HP |

The Champions field-effect description confirms that damage increases with additional layers. The exact fractions should be validated against the current Champions implementation before being treated as final calculator constants.

### 11.2 Grounding and immunity

Spikes do not affect Pokémon that are not grounded.

Examples of Pokémon normally unaffected include:
- Flying types;
- Pokémon with Levitate;
- Pokémon floating due to an applicable effect.

Grounding effects such as Gravity can change whether a Pokémon is affected.

### 11.3 Strategic implications

Spikes punish repeated switching and can create cumulative damage thresholds.

The AI should evaluate:
- the number of layers;
- the opponent's grounded Pokémon;
- how often the opponent is likely to switch;
- whether the opponent has a reliable hazard-removal move.

**Availability:** Champions-listed.

---

## 12. Toxic Spikes

**Scope:** Opposing side.

**Effect:** Poisons grounded Pokémon when they enter battle.

Toxic Spikes can have one or two layers.

### 12.1 Layer system

| Layers | Effect |
|---|---|
| 1 | Normal poison |
| 2 | Bad poison |

The effect is applied when an eligible Pokémon enters battle.

### 12.2 Immunities

Toxic Spikes do not affect Pokémon that are not grounded.

Poison-type and Steel-type Pokémon are immune to poisoning.

A Poison-type Pokémon entering battle removes Toxic Spikes from its own side of the field.

This removal behaviour is particularly important for defensive team building.

### 12.3 Existing status conditions

A Pokémon that already has a status condition should not be treated as a fresh valid poisoning target.

The AI should check the target's current status before applying the hazard.

### 12.4 Strategic implications

Toxic Spikes can punish defensive teams and repeated switching.

Their value depends on:
- the number of grounded opposing Pokémon;
- the opponent's Poison- and Steel-type Pokémon;
- whether the opponent has a Poison-type Pokémon that can clear them;
- whether the opponent can remove hazards through moves.

**Availability:** Champions-listed.

---

## 13. Sticky Web

**Scope:** Opposing side.

**Effect:** Lowers the Speed of grounded Pokémon by one stage when they enter battle.

### 13.1 Application

Sticky Web activates on entry.

The Speed reduction is a stat-stage change, not a permanent change to base Speed.

The AI should apply the normal stat-stage rules and respect the minimum stage limit.

### 13.2 Immunities

Sticky Web does not affect Pokémon that are not grounded.

Examples include:
- Flying types;
- Pokémon with Levitate;
- Pokémon made airborne by an applicable effect.

Grounding effects can make a Pokémon susceptible to Sticky Web.

### 13.3 Strategic implications

Sticky Web is useful for controlling the opponent's Speed thresholds.

The AI should evaluate:
- which opposing Pokémon are grounded;
- whether lowering their Speed changes move order;
- whether the opponent can remove the hazard;
- whether the opposing team benefits from Trick Room.

**Availability:** Champions-listed.

---

## 14. Entry-hazard removal

Hazard removal must be represented separately from hazard application.

Champions data lists several moves that can remove hazards.

| Move | Relevant removal behaviour |
|---|---|
| Rapid Spin | Removes hazards from the user's side; also raises the user's Speed |
| Mortal Spin | Removes hazards from the user's side; also has a poisoning effect |
| Defog | Removes listed field effects, including hazards and screens |
| Tidy Up | Removes listed hazards and certain other effects from the field |

The AI must check the exact Champions move description for the removal scope.

Do not assume that every move removes both sides' hazards.

### 14.1 Removal timing

Hazard removal is part of the move's resolution.

The AI should not remove hazards before checking whether the move successfully resolves.

### 14.2 Hazard state representation

Suggested structure:

```json
{
  "side_conditions": {
    "player": {
      "stealth_rock": false,
      "spikes_layers": 0,
      "toxic_spikes_layers": 0,
      "sticky_web": false
    },
    "opponent": {
      "stealth_rock": true,
      "spikes_layers": 2,
      "toxic_spikes_layers": 1,
      "sticky_web": false
    }
  }
}
```

This is an illustrative state, not a live battle state.

---

# PART III — GLOBAL FIELD EFFECTS

## 15. Magic Room

**Scope:** Whole battlefield.

**Effect:** Suppresses the effects of most held items.

### 15.1 Behaviour

While Magic Room is active, most held-item effects do not function.

The AI must distinguish between:
- an item being held;
- the item being active;
- the item being consumed or removed.

Magic Room does not mean that every Pokémon loses its held item. It suppresses item effects for the duration of the field condition.

### 15.2 Implementation requirements

The item system should evaluate Magic Room before applying held-item modifiers.

Examples of item effects that may be suppressed include:
- damage modifiers;
- stat modifiers;
- Speed modifiers;
- recovery effects;
- automatic defensive effects.

Do not automatically suppress effects that are not ordinary held-item effects without checking their implementation.

### 15.3 Duration

The exact Champions duration should be read from the current move and battle-effect data. Do not assume a duration from another generation.

### 15.4 Strategic implications

Magic Room can disrupt teams that rely on held items for damage, Speed or survivability.

The AI should identify which side loses more value from item suppression.

**Availability:** Champions-listed.

---

## 16. Wonder Room

**Scope:** Whole battlefield.

**Effect:** Swaps Defense and Special Defense for damage calculations.

### 16.1 Behaviour

While Wonder Room is active:

- Defense is used where Special Defense would normally be used;
- Special Defense is used where Defense would normally be used.

This changes which defensive stat is used against physical and special attacks.

It does not permanently rewrite the Pokémon's base stats.

### 16.2 Important distinction

Wonder Room is not the same as:
- changing a Pokémon's type;
- changing its stat stages;
- permanently increasing Defense or Special Defense.

The AI should preserve the original stat values and apply the swap only while the effect is active.

### 16.3 Strategic implications

Wonder Room can reverse the usual defensive matchup.

The AI should evaluate:
- which Pokémon have a large difference between Defense and Special Defense;
- whether the user's attacks become more effective;
- whether the opponent benefits more from the stat swap.

**Availability:** Champions-listed.

---

## 17. Gravity

**Scope:** Whole battlefield.

**Effect:** Increases move accuracy and grounds Pokémon that would normally be airborne.

### 17.1 Accuracy

The Champions field-effect description reports a 67% increase to move accuracy.

The standard mathematical interpretation is a multiplier of approximately `5/3` applied to accuracy.

The AI should use the Champions implementation's exact accuracy formula and rounding rather than simply adding 67 percentage points.

For example, a move with 60% base accuracy should not be treated as having 127% accuracy.

### 17.2 Grounding

Gravity causes Pokémon that would normally be airborne to become grounded.

This can change interactions with:
- Ground-type attacks;
- Electric Terrain;
- Grassy Terrain;
- Misty Terrain;
- Psychic Terrain;
- Spikes;
- Toxic Spikes;
- Sticky Web.

Grounding must be recalculated while Gravity is active.

### 17.3 Move restrictions

Moves involving flying or leaping cannot be used while Gravity is active.

The AI must check the move's Champions-specific restrictions rather than trying to infer them only from the move's type.

### 17.4 Strategic implications

Gravity can:
- improve the reliability of inaccurate attacks;
- make airborne Pokémon susceptible to Ground-type attacks;
- change which Pokémon are affected by terrain and entry hazards;
- restrict certain movement-based moves.

**Availability:** Champions-listed.

---

## 18. Fairy Lock

**Scope:** Whole battlefield.

**Effect:** Prevents Pokémon on the field from switching out.

### 18.1 Duration

The Champions description states that switching is prevented until the end of the next turn after Fairy Lock is activated.

This should be represented as a timed global restriction, not as a permanent status condition on the Pokémon that used the move.

### 18.2 Interaction with switching

The AI should evaluate Fairy Lock when checking:
- voluntary switching;
- pivot moves;
- forced switching effects;
- escape or switching abilities.

Do not assume that every forced-switch effect and every pivot move interacts identically. The exact Champions implementation must determine whether the action fails, the switch is prevented, or another effect occurs.

### 18.3 Strategic implications

Fairy Lock can trap the opposing team temporarily and create opportunities to:
- target a vulnerable Pokémon;
- prevent a defensive switch;
- secure a knockout;
- exploit a favourable matchup.

**Availability:** Champions-listed.

---

# PART IV — POSITION-BASED AND DELAYED EFFECTS

## 19. Wish

**Scope:** A specific battlefield position.

**Effect:** Restores HP to the Pokémon occupying the affected position after a delay.

### 19.1 Timing

The Champions description states that Wish resolves at the end of the next turn after the Wish status is activated.

It is not an immediate recovery move.

### 19.2 Healing amount

The restored HP is equal to half of the maximum HP of the Pokémon that created Wish.

This is important: the amount is based on the original user's maximum HP, not the maximum HP of the Pokémon receiving the healing.

### 19.3 Position-based behaviour

Wish is associated with a battlefield position.

The AI must track:
- which position received the Wish effect;
- which Pokémon created it;
- the creator's maximum HP;
- the turn on which it will resolve.

The Pokémon occupying the position when Wish resolves receives the recovery according to the Champions implementation.

Do not automatically attach Wish to the original user as a personal status effect.

### 19.4 Strategic implications

Wish can support switching and defensive positioning.

The AI should consider whether a Pokémon can switch into the affected position before Wish resolves.

**Availability:** Champions-listed.

---

## 20. Future Attack

**Scope:** A specific targeted position.

**Effect:** Deals delayed damage to the Pokémon occupying the targeted position.

### 20.1 Timing

The Champions description states that the targeted position takes damage two turns after the effect is activated.

It is not resolved as ordinary damage immediately when the move is used.

### 20.2 Position tracking

The AI should track:
- the targeted position;
- the source of the delayed attack;
- the turn when it resolves;
- the damage calculation data required by the Champions implementation.

Do not assume that the original target remains the eventual recipient.

The position-based description means switching and replacement events must be handled carefully.

### 20.3 Damage calculation

The delayed attack must use its own Champions move data and damage rules.

Do not calculate it as a generic fixed-damage effect.

The implementation should determine:
- whether the move's original offensive stat is used;
- which defensive stat is used;
- whether STAB applies;
- whether type effectiveness applies;
- which field modifiers are evaluated at activation and which at resolution.

These details should be verified against the Champions implementation rather than imported automatically from another generation.

### 20.4 Strategic implications

Future Attack can create delayed pressure and punish predictable positioning.

The AI should consider whether the opponent can switch, protect the affected position or otherwise alter the eventual target.

**Availability:** Champions-listed.

---

# PART V — MOVE RESTRICTION EFFECTS

## 21. Sealing Off

**Scope:** Opposing Pokémon.

**Effect:** Prevents opponents from using moves known by the Pokémon that caused the effect.

### 21.1 Behaviour

The Champions description states that moves known by the source Pokémon cannot be used by its opponents.

This is not the same as disabling one specific move on one target.

The AI should identify:
- the Pokémon that created the effect;
- the moves known by that Pokémon;
- which opposing Pokémon are affected;
- whether the effect is still active.

### 21.2 Move selection

When selecting a move, the AI should remove prohibited moves from the legal move set.

It must not simply reduce the move's priority or power.

### 21.3 Duration and scope

The exact duration and target-selection behaviour must be read from the Champions implementation.

Do not assume the effect applies to every move known by the opponent, or that it disables moves globally without considering the source Pokémon.

### 21.4 Strategic implications

Sealing Off can restrict the opponent's available actions.

The AI should evaluate whether the source Pokémon knows moves that are especially important to the opposing team.

**Availability:** Champions-listed. Detailed restrictions: Needs verification.

---

# PART VI — PLEDGE COMBINATIONS

## 22. General Pledge mechanics

The traditional Pledge system allows two Pokémon to combine compatible moves.

The combinations create a special side condition.

These are not ordinary weather or terrain conditions.

The standard combinations are:

| First move | Second move | Combined effect |
|---|---|---|
| Fire Pledge | Grass Pledge | Sea of Fire |
| Fire Pledge | Water Pledge | Rainbow |
| Water Pledge | Grass Pledge | Swamp |

The traditional combined attack has 150 base power.

The combined move is resolved through a special two-Pokémon interaction rather than two independent ordinary attacks.

### 22.1 Champions availability

The Pledge effects are included here as reference mechanics, not as active Champions rules.

The current Champions move-availability references consulted for this document do not establish these combinations as available. ViZukan also labels Pledge side conditions as unverified for Champions.

Therefore:

- do not add Pledge moves to the active legal move pool based on this section;
- do not enable Pledge combinations in the battle simulator;
- retain the mechanics as reference data only;
- recheck availability if the Champions move roster changes.

**Availability:** Reference-only / not verified as available in Champions.

---

## 23. Sea of Fire

**Created by:** Fire Pledge + Grass Pledge.

**Scope:** Opposing side.

**Traditional effect:** Damages Pokémon on the affected side at the end of each turn, except Fire-type Pokémon.

The standard reference damage is `1/8` of maximum HP per turn.

### AI requirements

If the combination becomes available in Champions, the AI must:
- track the affected side;
- track the remaining duration;
- check each affected Pokémon's type;
- apply residual damage at the correct end-of-turn stage;
- avoid applying damage to Fire-type Pokémon.

Do not implement this as Sandstorm or ordinary burn damage.

**Champions availability:** Not verified.

---

## 24. Rainbow

**Created by:** Fire Pledge + Water Pledge.

**Scope:** User's side.

**Traditional effect:** Doubles the chance of secondary effects from moves used by the protected side.

This affects chance-based additional effects, not the move's base damage.

Examples of secondary effects include:
- stat reductions;
- status conditions;
- flinching;
- other effects explicitly defined as secondary effects.

The AI must distinguish a secondary effect from:
- a guaranteed effect;
- a move's primary effect;
- an effect that occurs independently of the move's secondary-effect chance.

The exact interaction with Serene Grace and other probability modifiers must be implemented according to the actual engine rules.

**Champions availability:** Not verified.

---

## 25. Swamp

**Created by:** Water Pledge + Grass Pledge.

**Scope:** Opposing side.

**Traditional effect:** Reduces the Speed of Pokémon on the affected side to one-quarter of their normal Speed for the duration.

This is a field condition, not a permanent reduction to base Speed.

The AI should:
- store Swamp separately from Tailwind;
- calculate its Speed modifier at the correct stage;
- account for Trick Room;
- restore ordinary Speed calculation when the effect ends.

Do not model Swamp as a simple -2 Speed stage unless the Champions engine explicitly implements it that way.

**Champions availability:** Not verified.

---

# PART VII — FIELD EFFECT INTERACTIONS

## 26. Multiple effects at once

Different field effects can coexist when their scopes and rules permit it.

Examples:

- Reflect + Light Screen;
- Reflect + Tailwind;
- Stealth Rock + Spikes;
- Stealth Rock + Toxic Spikes;
- Tailwind + Trick Room;
- Gravity + terrain;
- Wish + Future Attack.

The AI must not use one generic `field_effect` variable.

Each effect should have its own state and scope.

### 26.1 Side-specific state

Suggested structure:

```json
{
  "side_conditions": {
    "player": {
      "reflect": {
        "active": true,
        "remaining_turns": 3
      },
      "light_screen": {
        "active": false,
        "remaining_turns": 0
      },
      "aurora_veil": {
        "active": false,
        "remaining_turns": 0
      },
      "safeguard": {
        "active": false,
        "remaining_turns": 0
      },
      "tailwind": {
        "active": true,
        "remaining_turns": 2
      },
      "stealth_rock": false,
      "spikes_layers": 0,
      "toxic_spikes_layers": 0,
      "sticky_web": false
    },
    "opponent": {
      "reflect": {
        "active": false,
        "remaining_turns": 0
      },
      "light_screen": {
        "active": false,
        "remaining_turns": 0
      },
      "aurora_veil": {
        "active": false,
        "remaining_turns": 0
      },
      "safeguard": {
        "active": false,
        "remaining_turns": 0
      },
      "tailwind": {
        "active": false,
        "remaining_turns": 0
      },
      "stealth_rock": true,
      "spikes_layers": 2,
      "toxic_spikes_layers": 1,
      "sticky_web": false
    }
  }
}
```

### 26.2 Global state

```json
{
  "global_field_effects": {
    "trick_room": {
      "active": false,
      "remaining_turns": 0
    },
    "magic_room": {
      "active": false,
      "remaining_turns": 0
    },
    "wonder_room": {
      "active": false,
      "remaining_turns": 0
    },
    "gravity": {
      "active": false,
      "remaining_turns": 0
    },
    "fairy_lock": {
      "active": false,
      "remaining_turns": 0
    }
  }
}
```

### 26.3 Position-based state

```json
{
  "position_effects": {
    "player_left": {
      "wish": null,
      "future_attack": null
    },
    "player_right": {
      "wish": null,
      "future_attack": null
    },
    "opponent_left": {
      "wish": null,
      "future_attack": null
    },
    "opponent_right": {
      "wish": null,
      "future_attack": null
    }
  }
}
```

These are illustrative structures. Actual position identifiers should match the battle simulator's active-slot model.

---

## 27. Turn-resolution requirements

Field effects must be processed at the correct point in the battle engine.

Recommended conceptual sequence:

1. Resolve move selection and priority.
2. Resolve the move that creates or removes a field effect.
3. Apply immediate effects, such as stat changes or screen creation.
4. Resolve switching and entry hazards when a Pokémon enters.
5. Resolve damage and secondary effects from moves.
6. Resolve delayed effects when their scheduled turn arrives.
7. Resolve end-of-turn residual damage and recovery.
8. Decrease relevant duration counters according to the Champions turn-resolution rules.
9. Remove expired effects.

This is a conceptual implementation sequence, not a claim that every Champions effect is processed in exactly this order. The engine's actual ordering must be used for interactions where timing matters.

### 27.1 Important timing distinctions

- Entry hazards resolve when a Pokémon enters.
- Reflect and Light Screen apply to damage calculations while active.
- Tailwind and Trick Room affect turn order.
- Wish resolves at a scheduled end-of-turn point.
- Future Attack resolves after its delay.
- Sea of Fire, if supported, would cause residual damage.
- Magic Room and Wonder Room affect calculations while active.
- Gravity changes grounding and move restrictions while active.

Do not process all effects as end-of-turn damage.

---

## 28. Recommended data model

Each effect should have a structured definition.

Suggested schema:

```json
{
  "id": "reflect",
  "name": "Reflect",
  "category": "side_condition",
  "scope": "side",
  "availability": "champions_listed",
  "duration": {
    "base_turns": 5,
    "extension_item": null
  },
  "activation": {
    "type": "move"
  },
  "effect": {
    "physical_damage_multiplier": {
      "singles": 0.5,
      "doubles": 0.6666667
    }
  },
  "removal": [
    "screen_cleaner",
    "psychic_fangs",
    "brick_break",
    "raging_bull",
    "defog"
  ],
  "evidence": {
    "status": "champions_listed",
    "notes": "Damage reduction and removal interactions are listed in Champions battle-effect data."
  }
}
```

For effects that have multiple layers, delayed resolution or target positions, add the appropriate fields rather than forcing them into the same schema.

Recommended categories:

- `side_condition`
- `global_field_effect`
- `entry_hazard`
- `position_effect`
- `delayed_effect`
- `move_restriction`
- `reference_only`

Recommended availability values:

- `champions_listed`
- `champions_confirmed`
- `champions_reported`
- `needs_verification`
- `reference_only`
- `unavailable`

---

## 29. AI validation checklist

Before using a field effect in a team evaluation or battle simulation, verify:

1. Is the effect available in Pokémon Champions?
2. What is its scope?
3. Which side or position does it affect?
4. Does it have a duration?
5. When does its duration decrease?
6. Does it affect all Pokémon or only certain types or grounded Pokémon?
7. Does it change damage, stats, move legality, switching or turn order?
8. Can it coexist with other effects?
9. Which moves, Abilities or items remove or suppress it?
10. Does it have special Doubles behaviour?
11. Is the exact interaction confirmed in Champions or imported from another game?

If any important detail is unverified, the AI should report the uncertainty instead of inventing a rule.

---

## Sources

- Pokémon Zone — [Pokémon Champions Field Effects](https://www.pokemon-zone.com/champions/field-effects/)
- Pokémon Zone — [Pokémon Champions Battle Effects](https://www.pokemon-zone.com/champions/battle-effects/)
- Pokémon Zone — [Reflect](https://www.pokemon-zone.com/champions/field-effects/reflect/)
- Pokémon Zone — [Light Screen](https://www.pokemon-zone.com/champions/field-effects/light-screen/)
- Pokémon Zone — [Spikes](https://www.pokemon-zone.com/champions/field-effects/spikes/)
- Pokémon Zone — [Stealth Rock](https://www.pokemon-zone.com/champions/field-effects/stealth-rock/)
- Pokémon Zone — [Sticky Web](https://www.pokemon-zone.com/champions/field-effects/sticky-web/)
- Pokémon Zone — [Toxic Spikes](https://www.pokemon-zone.com/champions/field-effects/toxic-spikes/)
- ViZukan — [Battlefield Effects](https://www.vizukan.app/en/field-effects)

**Last researched:** 2026-11-18.

**Important:** This document separates Champions-listed mechanics from reference mechanics. Pledge combinations and other unverified effects must not be enabled in the active Champions simulator until their availability and exact behaviour are confirmed.