# Pokémon Champions — Status Conditions

## 1. Status system overview

Pokémon Champions distinguishes between two broad categories of status conditions:

1. **Major status conditions** — persistent conditions such as Burn, Poison, Paralysis, Sleep and Freeze. They normally remain after switching.
2. **Other statuses (volatile conditions)** — temporary effects applied to an individual Pokémon. They normally disappear when that Pokémon leaves the battlefield.

There is also a third useful implementation category:

3. **Transient action effects** — short-lived effects that influence a particular action or turn, such as Flinching. These should not necessarily be stored as ordinary persistent statuses.

The AI must not store every condition in a single `status` field. Each condition needs its own duration, trigger, scope and removal rules.

---

## 2. Major status conditions

A Pokémon can normally have only one major status condition at a time.

The six major conditions recognised by the Champions battle-effects database are:

- Burn
- Poison
- Bad Poison
- Paralysis
- Sleep
- Freeze

Major status conditions normally remain when the Pokémon switches out and returns to battle.

Type immunities, Abilities, items and field effects can prevent or remove individual conditions.

### 2.1 Burn

**Effect:**
- Deals damage equal to 1/16 of maximum HP at the end of each turn.
- Halves damage dealt by the affected Pokémon's physical moves.

Fire-type Pokémon are immune to Burn.

The physical damage reduction is separate from the residual damage. The AI must apply both effects independently.

**Removal and prevention:**
- Switching does not remove Burn.
- Fire-type immunity prevents the condition.
- Certain Abilities and items can prevent or cure it.

### 2.2 Poison

**Effect:** Deals damage equal to 1/8 of maximum HP at the end of each turn.

Poison- and Steel-type Pokémon are immune.

Poison is not the same as Bad Poison. It uses a constant damage amount rather than an escalating counter.

**Removal and prevention:**
- Switching does not remove Poison.
- Poison- and Steel-type immunity prevents it.
- Certain Abilities and items can prevent or cure it.

### 2.3 Bad Poison

**Effect:** Deals increasing residual damage.

The damage starts at 1/16 of maximum HP and increases by another 1/16 at each subsequent residual-damage resolution.

| Damage stage | HP lost |
|---|---:|
| 1 | 1/16 |
| 2 | 2/16 |
| 3 | 3/16 |
| 4 | 4/16 |
| 5 | 5/16 |
| 6 | 6/16 |
| 7 | 7/16 |
| 8 | 8/16 |

Poison- and Steel-type Pokémon are immune.

**Switching interaction:**

When a badly poisoned Pokémon switches out and later returns, the escalating damage counter restarts at 1/16.

The major status itself remains. Only its damage progression is reset.

The AI must therefore store the Bad Poison counter separately from the major status identifier.

### 2.4 Paralysis

**Effects:**
- Speed is reduced to 1/2.
- There is a 1-in-8 (12.5%) chance that the Pokémon cannot execute its move.

Electric-type Pokémon are immune to Paralysis in Champions.

The AI must treat the Speed penalty and the action-prevention chance as separate effects.

Do not use the traditional 25% full-paralysis probability.

### 2.5 Sleep

**Effect:** A sleeping Pokémon cannot use normal moves.

Snore and Sleep Talk are exceptions.

**Champions-specific duration:**

- The Pokémon remains asleep during its first turn after becoming asleep.
- On its second turn, it has a 1-in-3 chance to wake up.
- It wakes up on its third turn if it has not already woken up.

Rest has a special interaction: a Pokémon that used Rest cannot wake up through the ordinary second-turn chance. It wakes on its third turn.

The AI must distinguish ordinary Sleep from Sleep caused by Rest.

Do not use a generic random 1–3-turn Sleep counter.

### 2.6 Freeze

**Effects:**
- The Pokémon cannot use almost all moves.
- It has a 25% chance to thaw when attempting to act.
- It is guaranteed to thaw on its third turn after becoming frozen.

Fire-type move damage and certain other moves can thaw the target.

Ice-type Pokémon are immune to Freeze in Champions.

The AI must check the move's explicit thawing behaviour rather than assuming that every Fire-type move has the same effect.

---

# PART II — VOLATILE STATUSES

## 3. General rules

Volatile statuses are temporary conditions attached to an individual Pokémon.

Unlike major status conditions, they normally disappear when the affected Pokémon leaves the battlefield.

This includes:
- voluntary switching;
- forced switching;
- other effects that actually remove the Pokémon from its active position.

A Pokémon that switches out and returns should not automatically regain its previous volatile statuses.

### 3.1 Important distinction: switching restrictions

Some volatile statuses prevent switching.

Examples:
- Bound;
- Ingrained;
- Can't Escape;
- Jaw Locked.

These conditions must be checked before allowing a switch.

If an effect prevents switching, the AI must not clear that effect simply because a switch was requested.

A successful switch normally clears the departing Pokémon's volatile statuses, but side conditions and global field effects remain separate.

### 3.2 Volatile status categories

For implementation, divide volatile statuses into these groups:

| Category | Examples |
|---|---|
| Action restrictions | Taunted, Encore, Move Disabled, Unable to Repeat |
| Action disruption | Confused, Infatuated, Flinching, Drowsy |
| Residual damage | Bound, Cursed, Leech Seeded, Salt Cured |
| Switching restrictions | Bound, Ingrained, Can't Escape, Jaw Locked |
| Move restrictions | Throat Chopped, Taunted, Encore, Move Disabled |
| Delayed effects | Perishing, Drowsy, Locked On |
| Position and grounding | Sky-High, Submerged, Underground, Concealed, Magnet Rise, Landed |
| Temporary stat and damage modifiers | Wide Open, Octolocked, Critical-Hit Ratio Boost, Atk/Def Swapped |
| Temporary recovery and power effects | Aqua Ring, Micle Berry, Electric Boost, Flash Fire Boost |
| Multi-turn move states | Charging, Uproar, Rampaging, Recharging |

---

## 4. Confused

**Effect:** The affected Pokémon has a 1-in-3 chance of hurting itself instead of successfully executing its selected move.

**Duration:** 1–4 turns.

Confusion is independent of major status conditions. A Pokémon can be confused while also burned, poisoned, paralysed, asleep or frozen.

### 4.1 Behaviour

At the appropriate point in action resolution, the game checks whether confusion prevents the Pokémon from executing its selected move.

The AI must not treat Confusion as:
- a reduction in Accuracy;
- a change in move priority;
- a stat-stage reduction;
- an ordinary major status condition.

### 4.2 Interactions

- Own Tempo prevents Confusion.
- Tangled Feet increases evasiveness while the Pokémon is confused.
- Lum Berry cures Confusion.
- Persim Berry cures Confusion.
- Switching clears Confusion.

### 4.3 Move sources

Champions-listed sources include:
- Confuse Ray;
- Dynamic Punch;
- Swagger;
- Flatter;
- Sweet Kiss;
- Teeter Dance;
- Hurricane;
- Water Pulse;
- Alluring Voice;
- Axe Kick.

The exact probability of applying Confusion depends on the move.

---

## 5. Infatuated (Attraction)

**Effect:** The Pokémon has a 50% chance of being unable to use its move while the Pokémon that caused Infatuation remains on the field.

This is the Champions status corresponding to the traditional Attraction/Infatuation mechanic.

### 5.1 Behaviour

The status is linked to the source Pokémon.

It is not a generic 50% action-prevention effect that lasts independently of the source.

The AI should store the source Pokémon's battle identity and check whether that Pokémon remains on the field.

### 5.2 Interactions

- Oblivious prevents Infatuation.
- Aroma Veil protects the Pokémon and its allies from Infatuation.
- Mental Herb cures Infatuation.
- Switching clears Infatuation.

Attract fails against a target of the same gender as the user or a target whose gender is unknown.

### 5.3 Strategic implications

Infatuation is an action-disruption condition. Its value depends on the target's ability to remain in battle and the source Pokémon's ability to stay active.

---

## 6. Taunted

**Effect:** The affected Pokémon can use only attacking moves.

Status moves are prohibited while Taunt is active.

### 6.1 Behaviour

The AI should filter the affected Pokémon's legal move choices.

For example:
- an attacking move remains selectable;
- Protect is unavailable;
- a stat-boosting move is unavailable;
- a recovery move is unavailable.

Do not treat Taunt as a reduction in move priority or as a forced attack.

### 6.2 Interactions

- Oblivious prevents Taunt.
- Aroma Veil protects the Pokémon and its allies from Taunt.
- Mental Herb cures Taunt.
- Switching clears Taunt.

### 6.3 Duration

The exact Champions duration should be taken from the current move/effect implementation. Do not hardcode a duration from another Pokémon game without confirmation.

---

## 7. Encore

**Effect:** The affected Pokémon can use only the move it used immediately before gaining Encore.

### 7.1 Behaviour

The AI must remember the target's last successfully selected/executed move according to the battle engine's definition.

Encore restricts the move choice. It does not:
- change the move's base power;
- change its type;
- change its priority;
- automatically force the move to succeed.

If the recorded move becomes unavailable or cannot legally be used, the engine's failure rules must be applied.

### 7.2 Interactions

- Aroma Veil protects the Pokémon and its allies from Encore.
- Mental Herb cures Encore.
- Switching clears Encore.

### 7.3 Strategic implications

Encore can punish:
- Protect;
- setup moves;
- recovery moves;
- predictable support actions.

The AI should evaluate the target's last move before using Encore.

---

## 8. Move Disabled

**Effect:** The affected Pokémon cannot use the move it last used before receiving Move Disabled.

### 8.1 Behaviour

Unlike Encore, Disable removes one specific move from the available move choices.

The AI must store:
- the disabled move identifier;
- the remaining duration;
- the source of the effect, if required by the engine.

The move cannot be selected while the condition is active.

### 8.2 Duration

Disable applies the Move Disabled status for 4 turns in Champions.

### 8.3 Interactions

- Cursed Body can apply Move Disabled when the Pokémon with the Ability takes damage from a move. The reported chance is 30%.
- Aroma Veil protects the Pokémon and its allies from Move Disabled.
- Mental Herb cures Move Disabled.
- Switching clears Move Disabled.

---

## 9. Unable to Repeat

**Effect:** The affected Pokémon cannot use the same move twice in a row.

This is the Champions status associated with Torment.

### 9.1 Behaviour

The AI should compare the next selected move with the move used on the preceding turn.

If it is the same move, the move is prohibited while Unable to Repeat remains active.

This is not the same as:
- Encore, which forces one move;
- Disable, which prohibits one specific move.

### 9.2 Interactions

- Aroma Veil protects the Pokémon and its allies from Unable to Repeat.
- Mental Herb cures the status.
- Switching clears the status.

---

## 10. Drowsy

**Effect:** The affected Pokémon falls asleep at the end of the next turn after receiving Drowsy.

Drowsy is a delayed status application, not Sleep itself.

### 10.1 Behaviour

The AI should track:
- whether the Pokémon is Drowsy;
- the turn when the status was applied;
- whether the scheduled Sleep application has already resolved.

When the scheduled resolution point arrives, the Pokémon receives Sleep if the effect has not been removed or prevented.

### 10.2 Interactions

The status can be prevented or removed by relevant Abilities and effects.

The current Champions data lists:
- Yawn as a move that applies Drowsy;
- Sweet Veil and Insomnia as relevant Ability interactions;
- Electric Terrain and other sleep-prevention effects as relevant field interactions.

The AI must distinguish Drowsy from Sleep when checking whether a Pokémon can act.

Switching clears Drowsy.

---

## 11. Healing Prevented

**Effect:** The affected Pokémon cannot restore HP through moves, Abilities or held items.

This is a recovery restriction, not a damage-over-time condition.

### 11.1 Behaviour

While Healing Prevented is active, the AI must block applicable recovery sources.

Examples:
- Recover;
- Roost;
- healing Abilities;
- passive recovery items.

The AI should not confuse this status with:
- Heal Block in another game's implementation;
- anti-healing effects that apply only to one specific move;
- reduced healing from weather.

### 11.2 Interactions

- Aroma Veil protects the Pokémon and its allies from Healing Prevented.
- Mental Herb cures the condition.
- Switching clears the condition.

---

## 12. No Ability

**Effect:** The affected Pokémon's Ability loses its effect.

This is an Ability suppression status.

### 12.1 Behaviour

While active, the Pokémon's Ability does not provide its normal effect.

The AI must distinguish this from:
- replacing an Ability;
- copying an Ability;
- permanently changing an Ability;
- an Ability that is simply inactive because its activation condition is not met.

### 12.2 Interactions

The exact removal and duration rules should be taken from the Champions implementation of the move that applies No Ability.

Switching clears the volatile status.

---

## 13. Bound

**Effect:**
- Deals damage equal to 1/8 of maximum HP at the end of each turn.
- Prevents the affected Pokémon from switching out.

### 13.1 Duration

Champions lists a duration of 4–5 turns.

The AI must track the duration and not assume that every application lasts the same number of turns.

### 13.2 Behaviour

Bound is both:
- a residual-damage effect;
- a switching restriction.

The AI must check it before allowing a voluntary switch.

### 13.3 Interactions

- Certain moves and effects can remove or bypass trapping.
- Shed Shell is listed as an item interaction.
- Switching restrictions must be resolved according to the actual Champions rules.

Switching out successfully clears Bound.

---

## 14. Cursed

**Effect:** The affected Pokémon loses 1/4 of its maximum HP at the end of every turn.

Cursed is a residual-damage condition.

It is separate from Burn, Poison and Bad Poison.

### 14.1 Behaviour

The AI must process the damage as an end-of-turn effect.

Do not apply it immediately when the status is received.

### 14.2 Removal

Switching clears Cursed.

The exact interaction with the source Pokémon and the move that applies the condition should be handled through move-specific data.

---

## 15. Leech Seeded

**Effect:**
- The affected Pokémon loses 1/8 of its maximum HP at the end of each turn.
- The Pokémon occupying the source Pokémon's position restores HP equal to the amount drained.

Grass-type Pokémon are immune.

### 15.1 Position tracking

The healing recipient is associated with the position of the Pokémon that applied Leech Seed.

The AI must track the source position rather than permanently attaching the healing to the original Pokémon.

If the source Pokémon switches, the Pokémon that replaces it in that position can receive the healing according to the Champions description.

### 15.2 Interactions

- Grass-type immunity prevents Leech Seed.
- Switching clears Leech Seeded.
- The residual damage and recovery must be resolved as separate effects.

---

## 16. Perishing

**Effect:** The affected Pokémon faints three turns after receiving Perishing.

### 16.1 Countdown

The AI must track the Perishing counter separately from ordinary residual damage.

It is a delayed knockout condition, not a conventional damage-over-time status.

### 16.2 Behaviour

When the countdown reaches its resolution point, the Pokémon faints unless the effect has been removed or prevented.

### 16.3 Interactions

- Switching clears Perishing.
- Protecting the Pokémon from ordinary damage does not automatically remove the countdown.
- The AI must not treat Perishing as a move that deals a fixed amount of damage.

---

## 17. Ingrained

**Effects:**
- Restores 1/16 of maximum HP at the end of every turn.
- Makes the Pokémon grounded.
- Prevents the Pokémon from switching out.

### 17.1 Behaviour

Ingrained combines three separate effects:
1. Passive recovery.
2. Grounding.
3. Switching restriction.

The AI must store these properties separately so that the recovery effect is not confused with terrain healing or Aqua Ring.

### 17.2 Interactions

- Grounding changes interactions with Ground-type attacks, terrain and entry hazards.
- Ingrained prevents ordinary switching.
- Shed Shell is listed as an item interaction.
- Switching successfully clears the volatile status.

---

## 18. Can't Escape

**Effect:** The affected Pokémon cannot switch out.

Ghost-type Pokémon are immune.

### 18.1 Behaviour

Can't Escape is a switching restriction.

The AI should not treat it as a damage effect or a move-selection restriction.

### 18.2 Interactions

- Ghost-type immunity prevents the condition.
- Certain moves and Abilities can apply it.
- Shed Shell is listed as an item interaction.
- Switching clears the condition if the Pokémon successfully leaves the field.

---

## 19. Jaw Locked

**Effect:** Neither the Pokémon that applied Jaw Locked nor the affected Pokémon can switch out.

This is a linked switching restriction.

### 19.1 Behaviour

The AI must store the identities of both Pokémon involved.

It must check both sides when evaluating switching options.

This is not equivalent to a simple target-only trapping effect.

### 19.2 Removal

Switching restrictions must be handled through the Champions move implementation.

Do not assume that the source can switch out while the target remains trapped.

---

## 20. Throat Chopped

**Effect:** The affected Pokémon cannot use sound-based moves for 2 turns.

### 20.1 Behaviour

The AI should filter the Pokémon's move choices based on the move's sound-based classification.

Do not infer sound-based status from a move's animation or description alone.

### 20.2 Interactions

- Switching clears Throat Chopped.
- The effect lasts 2 turns in Champions.

---

## 21. Charging

**Effect:** The Pokémon spends a turn charging before using its move on the following turn.

This is a multi-turn action state.

### 21.1 Behaviour

The AI must store:
- the move being charged;
- the turn on which charging started;
- whether the move is scheduled to execute;
- any weather or other effects that can remove the charging requirement.

### 21.2 Important exception

Electro Shot does not require its normal charging turn in Rain.

The AI must therefore evaluate move-specific weather interactions before assigning the Charging status.

### 21.3 Other interactions

Moves such as Solar Beam, Solar Blade and other two-turn attacks have their own charging rules. Do not assume all charging moves use identical exceptions.

---

## 22. Locked On

**Effect:** On the next turn after gaining Locked On, the Pokémon's move will not miss when targeting the Pokémon that was locked onto.

### 22.1 Behaviour

Locked On is target-specific.

The AI must store:
- the target's battle identity;
- the turn when Locked On was applied;
- the turn on which the accuracy guarantee expires.

The accuracy guarantee does not mean the move automatically hits every Pokémon.

### 22.2 Interactions

- Switching clears the status.
- The guaranteed accuracy applies to the specified target.
- Other accuracy and move-resolution rules must still be evaluated according to the engine.

---

## 23. Magnet Rise

**Effect:** The Pokémon floats above the ground.

It becomes immune to:
- Ground-type moves;
- Spikes;
- Toxic Spikes;
- Sticky Web.

### 23.1 Grounding

Magnet Rise changes the Pokémon's grounding state.

The AI must use the resulting grounding state for terrain and hazard calculations.

### 23.2 Interactions

- Gravity can change grounding.
- Effects that explicitly ground the Pokémon can change the result.
- Switching clears Magnet Rise.

---

## 24. Landed

**Effect:** The Pokémon becomes grounded.

This status is relevant to:
- Ground-type attacks;
- terrain effects;
- Spikes;
- Toxic Spikes;
- Sticky Web.

### 24.1 Behaviour

Landed must override the Pokémon's normal airborne state while active, according to the Champions grounding rules.

The AI should not assume that a Flying-type Pokémon is always immune to Ground-type attacks if Landed is active.

### 24.2 Interactions

- Gravity and other grounding effects can affect the final grounding state.
- Switching clears Landed.

---

## 25. Aqua Ring

**Effect:** Restores 1/16 of maximum HP at the end of every turn.

Aqua Ring is a self-recovery effect.

### 25.1 Behaviour

It does not:
- remove major status conditions;
- increase Defense;
- heal the whole team;
- create a side condition.

### 25.2 Interactions

Aqua Ring is a separate recovery source from:
- Grassy Terrain;
- Ingrain;
- Leftovers;
- Leech Seed recovery.

The AI should account for multiple simultaneous recovery sources and use the Champions residual-effect order.

Switching clears Aqua Ring.

---

## 26. Uproar

**Effect:**
- The Pokémon continues its attack for 3 turns.
- It cannot take other actions during this period.
- No Pokémon on the battlefield can fall asleep while Uproar is active.

### 26.1 Behaviour

Uproar is a multi-turn attack state.

The AI must track the number of remaining Uproar turns and prevent ordinary move selection while the attack continues.

### 26.2 Sleep interaction

Uproar prevents Sleep from being applied to Pokémon on the field.

This is a global interaction, even though Uproar is attached to one Pokémon.

### 26.3 Switching

Switching clears the volatile status if switching is permitted by the engine.

---

## 27. Rampaging

**Effect:**
- The Pokémon continues attacking for 2–3 turns.
- It cannot take other actions while rampaging.
- When the rampage ends, the Pokémon becomes confused.

### 27.1 Behaviour

The AI must track:
- the move being repeated;
- the number of remaining turns;
- the eventual Confusion application.

### 27.2 Important distinction

Rampaging and Confused are separate statuses.

Confusion is applied after the rampage finishes. The AI must not apply the Confusion chance during every rampaging turn.

Switching clears the Rampaging state.

---

## 28. Octolocked

**Effect:** At the end of every turn, the affected Pokémon's Defense and Special Defense each decrease by one stage.

### 28.1 Behaviour

Octolocked causes progressive defensive stat-stage reductions.

The AI must track the current Defense and Special Defense stages and apply the normal stage limits.

### 28.2 Removal

Switching clears Octolocked.

The stat-stage changes should be handled according to the Champions stat-stage reset rules when the Pokémon leaves battle.

---

## 29. Wide Open

**Effect:**
- Opponents' moves cannot miss the affected Pokémon.
- Opponents' moves deal double damage to the affected Pokémon.

### 29.1 Behaviour

Wide Open is a defensive vulnerability effect.

The AI must apply it to attacks targeting the affected Pokémon.

It is not:
- an Accuracy reduction on the affected Pokémon's own moves;
- a general damage increase for the entire opposing side;
- a type effectiveness modifier.

### 29.2 Interactions

The effect should be applied in the appropriate accuracy and damage stages.

Switching clears Wide Open.

---

## 30. Salt Cured

**Effect:** Deals residual damage at the end of each turn.

| Target type | Damage |
|---|---:|
| Most types | 1/16 max HP |
| Steel | 1/8 max HP |
| Water | 1/8 max HP |

### 30.1 Behaviour

Salt Cured has increased damage against Water- and Steel-type Pokémon.

The AI must evaluate the target's current type when resolving the residual damage.

### 30.2 Removal

Switching clears Salt Cured.

---

## 31. Sky-High

**Effect:** The Pokémon rises high above the battlefield and becomes immune to most moves.

Exceptions include specific moves such as:
- Thunder;
- Hurricane;
- Smack Down.

The Pokémon is also unaffected by terrain.

### 31.1 Behaviour

Sky-High is a position and targeting state.

The AI must check whether a move can hit a Sky-High target before calculating damage.

Do not simply treat the Pokémon as Flying-type.

### 31.2 Interactions

The exact list of moves that can hit Sky-High targets must be sourced from Champions move data.

Switching clears the status.

---

## 32. Submerged

**Effect:** The Pokémon is underwater and cannot be hit by most moves.

Exceptions include:
- Surf;
- Whirlpool.

These moves deal double damage to Submerged targets.

The Pokémon is also unaffected by terrain.

### 32.1 Behaviour

Submerged is a targeting and damage-modification state.

The AI must check:
1. Whether the selected move can hit Submerged targets.
2. Whether the move receives the ×2 damage modifier.
3. Whether the target is still Submerged when the attack resolves.

### 32.2 Interactions

- Switching clears Submerged.
- Surf and Whirlpool have explicit interactions.
- Do not assume all Water-type attacks can hit the target.

---

## 33. Underground

**Effect:** The Pokémon is underground and cannot be hit by most moves.

Earthquake can hit the Pokémon and deals double damage.

The Pokémon is also unaffected by terrain.

### 33.1 Behaviour

The AI must check move-specific interactions before resolving an attack against an Underground target.

Earthquake's damage increase is specific to the Underground status.

It is separate from its Grassy Terrain damage reduction.

### 33.2 Interactions

- Switching clears Underground.
- Earthquake can hit and deals double damage.
- Other moves require explicit support in Champions move data.

---

## 34. Concealed

**Effect:** The Pokémon cannot be hit by moves and is unaffected by terrain.

This is a stronger protection state than ordinary evasion.

The AI must not model it as a simple Accuracy modifier.

### 34.1 Behaviour

While Concealed is active, ordinary moves cannot hit the Pokémon.

The AI should not attempt an ordinary damage calculation against a protected target.

Any exception must be explicitly defined by Champions move data.

Switching clears Concealed.

---

## 35. Minimized

**Effect:** Certain moves cannot miss the affected Pokémon and deal double damage.

The Champions description lists examples including:
- Supercell Slam;
- Body Slam;
- Dragon Rush;
- Flying Press;
- Heat Crash;
- Heavy Slam.

### 35.1 Behaviour

Minimized is not a universal damage vulnerability.

Only moves with the appropriate interaction receive the accuracy and damage effects.

The AI should store a separate move-to-status interaction table.

Switching clears Minimized.

---

## 36. Critical-Hit Ratio Boost

**Effect:** The affected Pokémon's attacks are more likely to score critical hits.

This is a temporary critical-hit modifier.

### 36.1 Behaviour

The AI must apply the modifier to attacks made by the affected Pokémon.

It is not a guaranteed critical hit.

The exact critical-hit stage and probability should be read from the Champions critical-hit calculation.

### 36.2 Interactions

The status can be created by moves, Abilities and items.

Switching clears the temporary status.

---

## 37. Atk/Def Swapped

**Effect:** The affected Pokémon's Attack and Defense stats are swapped.

This changes the stats used by the damage calculation.

### 37.1 Behaviour

The AI must retain the original stats and apply the swap as a temporary calculation modifier.

Do not permanently overwrite the Pokémon's base Attack and Defense values.

### 37.2 Interactions

The exact scope of the swap should be taken from the Champions move implementation.

Switching clears the volatile status.

---

## 38. Recharging

**Effect:** The Pokémon cannot take any actions for 1 turn.

This is the state associated with moves that require a recharge turn.

### 38.1 Behaviour

The AI must mark the Pokémon as unable to select or execute an ordinary move during the recharge turn.

Recharging is different from:
- Sleep;
- Flinching;
- Paralysis;
- Charging.

The AI should track it as a one-turn action restriction.

Switching clears the volatile status.

---

## 39. Flash Fire Boost

**Effect:** Increases the power of the affected Pokémon's Fire-type moves by 50%.

This is a temporary offensive boost associated with Flash Fire.

The AI must apply the modifier to the relevant Fire-type damage calculation.

Do not confuse the boost with Harsh Sunlight. They are separate modifiers.

Switching clears the temporary boost status.

---

## 40. Destiny Bound

**Effect:** If the affected Pokémon is knocked out by an opponent, that opponent is also knocked out.

### 40.1 Behaviour

Destiny Bound is a conditional knockout effect.

The AI must check:
- whether the affected Pokémon has Destiny Bound;
- whether the knockout was caused by an opponent;
- which opponent caused the knockout.

Do not treat it as residual damage or as an unconditional immediate knockout.

Switching clears Destiny Bound.

---

## 41. Electric Boost

**Effect:** The next Electric-type move used by the affected Pokémon has double power.

### 41.1 Behaviour

This is a one-use offensive modifier.

The AI must:
1. Check whether the next move is Electric-type.
2. Apply the ×2 power modifier.
3. Consume the boost when the qualifying move resolves according to the Champions implementation.

Do not apply it to every Electric-type move for the entire battle.

Switching clears the temporary status.

---

## 42. Stockpiling

**Effect:** Defense and Special Defense are increased by one stage for each Stockpile level.

The status tracks how many times Stockpile has been used.

### 42.1 Behaviour

The AI must store the Stockpile level.

The stat-stage increase is tied to that level.

Moves such as Swallow and Spit Up have specific interactions with Stockpiling.

### 42.2 Interactions

- Swallow restores HP according to the Stockpile level.
- Spit Up uses the Stockpile level to determine its power.
- Switching clears the volatile Stockpiling state and associated temporary stat stages.

---

## 43. Trick-or-Treating

**Effect:** The affected Pokémon gains the Ghost type.

### 43.1 Behaviour

The AI must update the Pokémon's effective type for the duration of the status.

This affects:
- type effectiveness;
- STAB;
- defensive immunities;
- move interactions that depend on the target's type.

Do not permanently overwrite the Pokémon's original typing.

Switching clears the temporary type change.

---

## 44. Forest Cursed

**Effect:** The affected Pokémon gains the Grass type.

This is a temporary type modification.

### 44.1 Behaviour

The AI must update the effective type for:
- damage calculations;
- STAB;
- defensive type matchups;
- type-based status immunities;
- terrain interactions.

The original type must remain stored separately.

Switching clears the temporary type change.

---

## 45. Syrupy

**Effect:** The affected Pokémon's Speed decreases by one stage at the end of every turn.

### 45.1 Behaviour

Syrupy applies repeated Speed-stage reductions.

The AI must:
- apply the reduction at the end-of-turn resolution point;
- respect the normal minimum stat-stage limit;
- track the current Speed stage;
- remove the volatile status when the Pokémon switches out.

Do not model Syrupy as a flat Speed multiplier.

---

# PART III — TRANSIENT ACTION EFFECTS

## 46. Flinching

Flinching is an action-prevention effect rather than a persistent major status.

**Effect:** The affected Pokémon cannot execute its move if it flinches before acting.

### 46.1 Behaviour

Flinching is relevant only to the current turn's action resolution.

If the Pokémon has already acted, a later flinch does not retroactively cancel that action.

### 46.2 Move interactions

Champions-listed moves can inflict flinching through:
- direct flinch effects;
- chance-based secondary effects;
- Ability and item interactions.

The AI must evaluate the move's flinch chance and the action order.

### 46.3 Difference from other statuses

Flinching should not be stored as a multi-turn volatile condition.

Use a transient action flag such as:

```json
{
  "flinched_this_turn": true
}
```

Reset it at the appropriate turn boundary.

---

## 47. Other temporary action restrictions

Some effects are represented as volatile statuses in the battle database, while others are better understood as action-resolution states.

The AI should keep these distinctions:

| Effect | Meaning |
|---|---|
| Flinching | Prevents an action in the current turn if applied before the Pokémon acts |
| Recharging | Prevents action for a designated turn |
| Charging | Requires a charging turn before the move executes |
| Rampaging | Forces repeated attacks for a limited number of turns |
| Uproar | Forces repeated attacks and prevents Sleep on the field |
| Confused | Gives a chance of self-injury instead of acting |
| Infatuated | Gives a chance of being unable to act |
| Paralysis | Gives a chance of being unable to act and reduces Speed |

These effects must not be merged into one generic `cannot_move` status.

---

# PART IV — INTERACTIONS AND IMMUNITIES

## 48. Aroma Veil

Aroma Veil protects the Pokémon with the Ability and its allies from several mental and move-restriction statuses.

Champions data lists protection against:

- Infatuated;
- Taunted;
- Unable to Repeat;
- Move Disabled;
- Healing Prevented;
- Encore.

The AI must evaluate Aroma Veil before applying these conditions.

Do not assume it protects against every volatile status.

## 49. Mental Herb

Mental Herb cures the holder of:

- Infatuated;
- Taunted;
- Unable to Repeat;
- Move Disabled;
- Healing Prevented;
- Encore.

The item is consumed after use.

The AI must check the exact status interaction before consuming the item.

## 50. Lum Berry and Persim Berry

**Lum Berry:** Cures any major status condition or Confusion.

**Persim Berry:** Cures Confusion.

These items must be handled separately from Mental Herb.

## 51. Switching and status clearing

The AI must distinguish the following:

| Condition | Cleared by switching? |
|---|---|
| Burn | No |
| Poison | No |
| Bad Poison | No, but its damage counter resets |
| Paralysis | No |
| Sleep | No |
| Freeze | No |
| Confused | Yes |
| Infatuated | Yes |
| Bound | Yes, if the Pokémon successfully leaves |
| Cursed | Yes |
| Taunted | Yes |
| Unable to Repeat | Yes |
| Move Disabled | Yes |
| Drowsy | Yes |
| Healing Prevented | Yes |
| No Ability | Yes |
| Leech Seeded | Yes |
| Perishing | Yes |
| Ingrained | Yes, if the Pokémon successfully leaves |
| Can't Escape | Yes, if the Pokémon successfully leaves |
| Encore | Yes |
| Throat Chopped | Yes |
| Charging | Yes |
| Locked On | Yes |
| Magnet Rise | Yes |
| Landed | Yes |
| Aqua Ring | Yes |
| Uproar | Yes |
| Rampaging | Yes |
| Octolocked | Yes |
| Jaw Locked | Yes, if the Pokémon successfully leaves |
| Wide Open | Yes |
| Salt Cured | Yes |
| Sky-High | Yes |
| Submerged | Yes |
| Underground | Yes |
| Concealed | Yes |
| Minimized | Yes |
| Critical-Hit Ratio Boost | Yes |
| Atk/Def Swapped | Yes |
| Recharging | Yes |
| Flash Fire Boost | Yes |
| Destiny Bound | Yes |
| Electric Boost | Yes |
| Stockpiling | Yes |
| Trick-or-Treating | Yes |
| Forest Cursed | Yes |
| Syrupy | Yes |

The table describes ordinary switching behaviour. Switching restrictions must be checked first. A Pokémon cannot clear a status by switching if that status prevents it from switching.

---

# PART V — AI IMPLEMENTATION


## 52. Required status metadata

Each status definition should contain:

| Field | Purpose |
|---|---|
| `id` | Stable internal identifier |
| `category` | Major, volatile or transient |
| `description` | Human-readable explanation |
| `duration_type` | Fixed, random, conditional, one-use or indefinite |
| `duration` | Number of turns, if applicable |
| `activation_timing` | When the effect is checked |
| `resolution_timing` | When damage, healing or other effects occur |
| `switch_behavior` | Whether switching clears the condition |
| `switch_restriction` | Whether the condition prevents switching |
| `immunities` | Types, Abilities and other immunity sources |
| `removal_sources` | Moves, Abilities and items that cure it |
| `move_restrictions` | Which actions become unavailable |
| `stat_modifiers` | Any temporary stat effects |
| `damage_modifiers` | Any damage effects |
| `evidence_status` | Confidence and source classification |

## 53. Recommended status-resolution sequence

For each Pokémon action:

1. Check whether the Pokémon is legally allowed to switch or act.
2. Check move restrictions such as Taunt, Encore, Disable and Unable to Repeat.
3. Check major status restrictions such as Sleep, Freeze and Paralysis.
4. Check volatile action-disruption conditions such as Confusion and Infatuation.
5. Check transient effects such as Flinching.
6. Resolve the selected move.
7. Apply new status conditions and their immediate effects.
8. At the end of the turn, resolve residual damage, recovery, delayed effects and status counters in the Champions engine's order.

This is a conceptual processing model. The exact order of individual checks must follow the Champions battle engine.

## 54. Important implementation rules

- Do not assume all volatile statuses have a numeric turn counter.
- Do not assume every volatile status can coexist with every other status.
- Do not assume all statuses are removed by the same moves or items.
- Do not treat Flinching as a multi-turn status.
- Do not treat Drowsy as Sleep.
- Do not treat Rampaging as Confusion until the rampage ends.
- Do not treat Bound, Ingrained and Can't Escape as ordinary damage conditions.
- Do not treat Magnet Rise, Landed, Sky-High, Submerged and Underground as ordinary stat changes.
- Do not permanently overwrite base stats or original typing when applying temporary modifiers.
- Do not clear a switching-restriction status before determining whether the switch succeeds.
- Do not import durations or probabilities from other Pokémon games without Champions-specific evidence.

---

## Sources

- Pokémon Zone — [Status Conditions in Pokémon Champions](https://www.pokemon-zone.com/champions/status/)
- Pokémon Zone — [Confused](https://www.pokemon-zone.com/champions/status/confused/)
- Pokémon Zone — [Infatuated](https://www.pokemon-zone.com/champions/status/infatuated/)
- Pokémon Zone — [Taunted](https://www.pokemon-zone.com/champions/status/taunted/)
- Pokémon Zone — [Encore](https://www.pokemon-zone.com/champions/status/encore/)
- Pokémon Zone — [Move Disabled](https://www.pokemon-zone.com/champions/status/move-disabled/)
- Pokémon Zone — [Drowsy](https://www.pokemon-zone.com/champions/status/drowsy/)
- Pokémon Zone — [Healing Prevented](https://www.pokemon-zone.com/champions/status/healing-prevented/)
- Serebii — [Pokémon Champions Available Moves](https://www.serebii.net/pokemonchampions/moves.shtml)
- DexDB — [Pokémon Champions Mechanics Ledger](https://dexdb.io/champions/mechanics/)
- DexDB — [Pokémon Battle Glossary](https://dexdb.io/glossary/)

**Last researched:** 2026-11-18.

**Implementation note:** Champions recognises a large number of temporary battle statuses beyond the six major conditions. This document includes the full set listed by the current battle-effects reference. Exact duration, removal and interaction rules should be validated against Champions move, Ability and item data before being hardcoded.