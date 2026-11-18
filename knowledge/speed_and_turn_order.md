# Pokémon Champions — Speed and Turn Order

## 1. Scope

This document describes how Pokémon Champions determines the order of actions during a battle.

Turn order is controlled by several separate systems:

1. Turn phases — switching, Mega Evolution, moves and end-of-turn processing.
2. Move priority — the priority bracket assigned to a move.
3. Priority modifiers — Abilities and conditional effects that change a move's priority.
4. Speed order — effective Speed within the same priority bracket.
5. Special ordering effects — Quick Claw, Quick Draw, Stall, After You and Quash.

These systems must not be treated as interchangeable.

A switch is not a move with priority +6. Mega Evolution is not a move with priority +5. Both are separate actions resolved in dedicated phases.

---

## 2. Overall Turn Resolution

A normal turn follows these main phases:

| Phase | Action | Description |
|---:|---|---|
| 1 | Voluntary switching | Pokémon selected to switch out are replaced before Mega Evolution and moves |
| 2 | Mega Evolution | Selected Pokémon Mega Evolve before any move is executed |
| 3 | Move execution | All selected moves are resolved by priority and then Speed |
| 4 | Forced switching and pivoting | Pokémon are replaced when an executed move or automatic effect causes a switch |
| 5 | End-of-turn processing | Residual damage, healing, Ability effects, status counters and field-effect durations are processed |

The exact internal processing of some simultaneous events is more complicated than this overview. Sections below describe the relevant details.

### Important consequences

- A voluntary switch happens before Mega Evolution.
- Mega Evolution happens before all moves, including Fake Out and Protect.
- A Pokémon cannot be stopped from Mega Evolving by being flinched by Fake Out later in the turn.
- Moves that force a Pokémon to switch out resolve at their own move priority. They do not receive the priority of a voluntary switch.
- Pivot moves resolve as moves first, then switch their user out.

---

## 3. Switching

### 3.1 Voluntary switching

A player-selected switch is resolved during the switching phase, before Mega Evolution and all moves.

Examples:
- Switching a Pokémon for a reserve Pokémon.
- Switching to reset stat stages.
- Switching to activate Regenerator.
- Switching to change the active Pokémon before an opponent's attack.

A voluntary switch does not have a numerical move-priority value.

**Example:**

- Player A selects a switch.
- Player B selects Mega Evolution.
- Player A's switch is resolved first.
- Player B's Pokémon Mega Evolves afterward.
- The remaining moves are executed afterward.

Do not treat switching as priority +6 or any other move-priority bracket.

### 3.2 Simultaneous switches

When both players select switches, both switching actions belong to the switching phase.

Do not automatically assume that the left player, faster Pokémon or a particular player side always switches first. The exact order of simultaneous switch processing and the resulting entry effects should be handled by the battle engine.

Entry Abilities can have their own Speed-based activation order. This is not the same as the order in which the switch commands were selected.

### 3.3 Entry effects

When a Pokémon enters battle, several effects may occur:

- Entry hazards, such as Stealth Rock, Spikes, Toxic Spikes and Sticky Web.
- Entry Abilities, such as Intimidate, Drizzle, Drought, Snow Warning, Sand Stream, Grassy Surge and Psychic Surge.
- Other effects that activate when a Pokémon enters battle.

The order of entry Ability activations can depend on Speed.

Pokémon Champions fixed an issue in Version 1.0.3 in which held-item Speed changes were not properly reflected in the order of Ability activations.

Research also found that entry hazards and entry Abilities are not necessarily processed as one combined event when multiple Pokémon enter after simultaneous knockouts.

**Implementation rule:** Model entry hazards and entry Abilities as separate event types. Use the Champions engine for their exact ordering.

---

## 4. Mega Evolution

Mega Evolution is a separate turn phase.

### 4.1 When Mega Evolution happens

Mega Evolution is resolved:

1. After voluntary switches.
2. Before all selected moves.
3. Before priority moves such as Fake Out, Helping Hand and Protect.

Mega Evolution cannot be prevented by a move that causes flinching during the move phase.

### 4.2 Two Pokémon Mega Evolving

If both players Mega Evolve during the same turn, their Mega Evolution actions are ordered by Speed before the transformation, according to the available Champions mechanics research.

The Mega Evolution phase is separate from the move-priority queue.

### 4.3 Mega Evolution and Speed

The Mega form's Speed is used for move ordering during that same turn.

Example:

- A Pokémon has 120 Speed before Mega Evolution.
- Its Mega form has 150 Speed.
- It Mega Evolves.
- The Mega form's 150 Speed is used when determining its move order later that turn.

The original Speed is relevant to the ordering of Mega Evolution actions; the Mega form's Speed is relevant to the subsequent move phase.

### 4.4 Mega Evolution and switching

A voluntary switch is resolved before the Mega Evolution phase.

The engine must therefore resolve the switch before processing the selected Mega Evolution actions.

Do not implement Mega Evolution as an ordinary move with a priority value.

---

## 5. Move Priority Brackets

Every move has a priority value.

A higher priority value executes before a lower priority value, regardless of the user's Speed.

For example:

- A +2 move executes before a +1 move.
- A +1 move executes before a normal 0-priority move.
- A 0-priority move executes before a -3 move.
- Trick Room has -7 priority and is normally executed after all other moves.

Within the same priority bracket, additional ordering rules apply.

### 5.1 Complete priority values used by Pokémon Champions

The following table lists the priority brackets present in the Champions move data.

| Priority | Number of moves | Examples |
|---:|---:|---|
| +5 | 1 | Helping Hand |
| +4 | 6 | Protect, Detect, Endure, King's Shield, Spiky Shield, Baneful Bunker |
| +3 | 4 | Fake Out, Quick Guard, Wide Guard, Upper Hand |
| +2 | 6 | Ally Switch, Extreme Speed, Feint, First Impression, Follow Me, Rage Powder |
| +1 | 12 | Accelerock, Aqua Jet, Baby-Doll Eyes, Bullet Punch, Ice Shard, Jet Punch, Mach Punch, Quick Attack, Shadow Sneak, Sucker Punch, Vacuum Wave, Water Shuriken |
| 0 | Most moves | Flamethrower, Earthquake, Tailwind, Protect-related support effects not listed above, etc. |
| -1 | 0 | No move in the current move data |
| -2 | 0 | No move in the current move data |
| -3 | 2 | Beak Blast, Focus Punch |
| -4 | 1 | Avalanche |
| -5 | 2 | Counter, Mirror Coat |
| -6 | 4 | Circle Throw, Dragon Tail, Roar, Whirlwind |
| -7 | 1 | Trick Room |

The move database must remain the source of truth for individual moves.

The counts above describe the priority values in the researched Champions move data. They are not a promise that future game updates cannot add or change moves.

### 5.2 Priority +5

**Helping Hand**

- Acts before all other moves.
- Boosts the power of an ally's move.
- It does not deal damage itself.

### 5.3 Priority +4

Defensive moves:

- Protect
- Detect
- Endure
- King's Shield
- Spiky Shield
- Baneful Bunker

These moves normally execute before +3, +2, +1 and 0 priority moves.

### 5.4 Priority +3

- Fake Out
- Quick Guard
- Wide Guard
- Upper Hand

Important:
- Fake Out only works when it is the first move its user uses after entering battle.
- Upper Hand only works if the target is about to use a priority move.
- Quick Guard protects the user's side against opposing priority moves.
- Wide Guard protects the user's side against qualifying spread moves.

### 5.5 Priority +2

- Ally Switch
- Extreme Speed
- Feint
- First Impression
- Follow Me
- Rage Powder

Important:
- Ally Switch changes the positions of the user's active Pokémon in Doubles. It does not switch a Pokémon with a reserve Pokémon.
- Feint can break through Protect and similar protection effects.
- First Impression only works as the first move after the user enters battle.
- Follow Me and Rage Powder redirect eligible opposing moves.

### 5.6 Priority +1

- Accelerock
- Aqua Jet
- Baby-Doll Eyes
- Bullet Punch
- Ice Shard
- Jet Punch
- Mach Punch
- Quick Attack
- Shadow Sneak
- Sucker Punch
- Vacuum Wave
- Water Shuriken

These moves act before normal-priority moves, but can still be outsped by moves with +2 or higher priority.

### 5.7 Priority 0

Most moves use priority 0.

This includes many moves that do not deal direct damage:
- Tailwind
- Trick
- Encore
- Taunt
- Thunder Wave
- Will-O-Wisp
- Protect is an exception and has +4.
- Follow Me is an exception and has +2.
- Helping Hand is an exception and has +5.

A move being a Status move does not automatically give it positive priority.

### 5.8 Negative priority

Negative-priority moves are intentionally delayed.

| Priority | Move | Purpose |
|---:|---|---|
| -3 | Beak Blast | Prepares before attacking; can burn contact attackers before it executes |
| -3 | Focus Punch | Fails if the user has already taken damage from a move during the turn |
| -4 | Avalanche | Gains increased power if the target has already damaged the user |
| -5 | Counter | Returns damage from a physical attack |
| -5 | Mirror Coat | Returns damage from a special attack |
| -6 | Circle Throw | Forces the target to switch out after a successful hit |
| -6 | Dragon Tail | Forces the target to switch out after a successful hit |
| -6 | Roar | Forces the target to switch out |
| -6 | Whirlwind | Forces the target to switch out |
| -7 | Trick Room | Reverses Speed order for five turns |

Negative priority does not mean a move is automatically unsuccessful. It means the move is placed later in the move queue.

---

## 6. Conditional Priority Changes

Some moves can receive a different priority value depending on the user's Ability or the battlefield.

### 6.1 Prankster

Prankster increases the priority of the user's Status moves by +1.

Examples:
- Tailwind: 0 → +1.
- Thunder Wave: 0 → +1.
- Encore: 0 → +1.
- Taunt: 0 → +1.
- Trick Room: -7 → -6.

Prankster does not increase the priority of damaging moves.

**Dark-type interaction:** Opposing Dark-type Pokémon are immune to Status moves that receive increased priority from Prankster.

### 6.2 Gale Wings

Gale Wings increases the priority of Flying-type moves by +1 when the user is at full HP.

Example:

```text
Brave Bird: 0 → +1
```

If the user is not at full HP, Gale Wings does not provide the priority increase.

### 6.3 Grassy Glide

Grassy Glide receives +1 priority when:
- Grassy Terrain is active;
- the user is grounded.

Otherwise, it has its normal priority of 0.

### 6.4 Other Abilities

Do not assume every Ability from the main series exists in Pokémon Champions.

For example, Triage is not currently part of the Champions Ability pool, so its usual +3 healing priority must not be added to the Champions implementation.

The move priority system should only apply Ability modifiers that are present in the Champions Ability database.

---

## 7. Speed Order Within a Priority Bracket

After priority has been determined, Speed decides the order of moves within the same bracket.

Normally:

```text
Higher effective Speed = acts first
Lower effective Speed = acts later
```

Under Trick Room:

```text
Lower effective Speed = acts first
Higher effective Speed = acts later
```

Trick Room does not change move priority.

Example:

| Pokémon | Move priority | Speed |
|---|---:|---:|
| Pokémon A | +1 | 100 |
| Pokémon B | 0 | 200 |
| Pokémon C | +1 | 80 |

Normal order:

1. Pokémon A (+1, Speed 100)
2. Pokémon C (+1, Speed 80)
3. Pokémon B (0, Speed 200)

Pokémon B is faster than both other Pokémon, but its lower move priority means it acts later.

Under Trick Room:

1. Pokémon C (+1, Speed 80)
2. Pokémon A (+1, Speed 100)
3. Pokémon B (0, Speed 200)

Priority still takes precedence over Speed.

### 7.1 Effective Speed

The Speed value used for move ordering must account for:
- the Pokémon's Level 50 Speed stat;
- Stat Points and Stat Alignment;
- Speed stages;
- paralysis;
- Tailwind;
- weather-dependent Abilities;
- held items;
- other Speed-modifying Abilities and effects;
- Mega Evolution, if applicable.

Use the separate Speed calculation rules for the exact stat calculation.

### 7.2 Speed ties

If two Pokémon have exactly the same effective Speed in the same priority bracket, their order is random.

Do not assume the left-side Pokémon, first player or a fixed team position wins a Speed tie.

For probability calculations, a two-Pokémon Speed tie should be represented as a 50/50 ordering.

---

## 8. Trick Room

Trick Room reverses the Speed order within each priority bracket.

- Duration: 5 turns.
- Move priority: -7.
- Slower Pokémon act before faster Pokémon.
- Priority brackets are not reversed.
- Speed ties remain random.
- Using Trick Room while it is already active ends its effect.

Example:

```text
Pokémon A: 180 Speed, priority 0
Pokémon B: 60 Speed, priority 0
```

Without Trick Room:

```text
A → B
```

With Trick Room:

```text
B → A
```

But if Pokémon A uses a +1 move and Pokémon B uses a 0 move, Pokémon A still acts first even under Trick Room.

### Trick Room and Speed overflow

The Champions mechanics ledger reports that Trick Room does not suffer from the high-Speed overflow behaviour found in some older main-series mechanics.

Do not introduce an arbitrary Speed cap or overflow rule without evidence from the Champions implementation.

---

## 9. Tailwind

Tailwind doubles the effective Speed of the affected side.

```text
Speed with Tailwind = Speed × 2
```

- Duration: 4 turns.
- Applies to the entire side.
- Persists when Pokémon switch.
- Does not change move priority.
- Can be active at the same time as Trick Room.

When Trick Room is active, Tailwind still doubles Speed, but the resulting Speed order is reversed.

---

## 10. Priority-Order Modifiers Within the Same Bracket

Some effects can change which Pokémon moves first or last without changing the move's numeric priority.

### 10.1 Quick Claw

- 20% chance to move first among moves of the same priority.
- Does not change the move's priority value.
- Does not allow a normal-priority move to jump ahead of a higher-priority move.

Example:

```text
Pokémon A: Flamethrower, priority 0, Quick Claw activates
Pokémon B: Quick Attack, priority +1

Pokémon B still acts first.
```

Quick Claw only changes the order within the same priority bracket.

### 10.2 Quick Draw

- 30% chance to move first within the same priority bracket.
- Applies to attacking moves.
- Does not change the move's numeric priority.

### 10.3 Stall

Stall causes the Pokémon to move last among Pokémon using the same or greater priority moves, according to its Champions Ability description.

It does not change the numerical priority of the selected move.

### 10.4 Items and Abilities not present in Champions

Do not add the following mechanics merely because they exist in other Pokémon games:

- Lagging Tail;
- Full Incense;
- Custap Berry;
- Triage.

They must only be implemented if they become available in Pokémon Champions.

---

## 11. Effects That Change the Move Queue

Some moves do not have a special numeric priority, but they can directly alter the order of actions.

### 11.1 After You

After You makes the target use its selected move immediately after the user.

- The move itself has normal priority.
- It does not simply give the target +1 priority.
- It changes the target's position in the current turn's move sequence.
- It fails if the target has already acted.

### 11.2 Quash

Quash makes the target move last in the current turn.

- The move itself has normal priority.
- It does not give the target a permanent -1 priority.
- It changes the target's position in the current turn's move sequence.

### 11.3 Encore

Encore forces the target to repeat its last successfully used move.

If Encore is applied before the target acts, the target can use the priority value of the move it is forced to repeat.

The interaction between Encore and Ability-based priority modifiers has conflicting reports. The AI should not assume a universal rule for every combination without validating it against the Champions engine.

---

## 12. Priority Blocking

Priority moves can be blocked by certain Abilities and field effects.

### 12.1 Armor Tail, Queenly Majesty and Dazzling

These Abilities prevent opposing priority moves from affecting the Pokémon and its allies, as applicable to the Ability.

They do not change the priority value of the move.

### 12.2 Psychic Terrain

Psychic Terrain prevents opposing priority moves from hitting grounded Pokémon.

The move can still be selected and executed, but its effect against a protected grounded target is blocked.

### 12.3 Quick Guard

Quick Guard protects the user's side against opposing priority moves for the turn.

It does not change the order of the moves themselves.

---

## 13. Pivot Moves and Switching During the Move Phase

Some moves attack or apply an effect and then switch the user out.

These are not voluntary switch actions. They are moves with their own priority values.

Examples:
- U-turn
- Volt Switch
- Flip Turn
- Parting Shot
- Baton Pass
- Chilly Reception

Most of these moves have priority 0.

Their sequence is:

1. The move reaches its position in the move queue.
2. The move is executed.
3. Its damage or other effect is resolved.
4. The user switches out if the move's conditions are satisfied.
5. The replacement Pokémon enters.
6. Entry effects are processed.
7. The remaining move queue continues.

### Eject Button

Eject Button is an automatic held-item effect, not a player-selected switch action.

When its conditions are met, it can cause the holder to switch out after taking a hit.

Champions-specific behaviour also allows U-turn and Volt Switch to switch their user out even when the opponent's Eject Button activates.

Do not model Eject Button as a priority bracket.

### Red Card

Red Card is another automatic held-item effect that can force the attacker to switch out after hitting its holder.

It is resolved as an effect of the move and item interaction, not as a separate move with a priority value.

---

## 14. Forced Switching Moves

These moves force the target to leave the battlefield:

- Circle Throw: -6
- Dragon Tail: -6
- Roar: -6
- Whirlwind: -6

They are ordinary move actions with negative priority.

Their sequence is:

1. The move reaches its position in the move queue.
2. The move is executed.
3. Its accuracy, protection and other conditions are checked.
4. If successful, the target is forced to switch out.
5. A replacement Pokémon enters.
6. Entry effects are processed.
7. The remaining move queue continues.

The forced switch does not happen during the initial voluntary switching phase.

### Pursuit

Pursuit is not available in Pokémon Champions.

It is marked as unusable in the Champions move availability list.

Therefore:
- Do not implement Pursuit's switch-interception mechanic.
- Do not give switching Pokémon a special interaction with Pursuit.
- Do not import the Pursuit exception from older Pokémon generations.

---

## 15. End-of-Turn Effects

End-of-turn effects are not move-priority actions.

They are processed after the move phase has finished.

Examples include:
- weather damage;
- burn and poison damage;
- Leech Seed;
- Curse;
- binding effects;
- Salt Cure;
- Leftovers healing;
- Aqua Ring;
- Ingrain;
- Speed Boost;
- status counter updates;
- Perish Song countdown;
- weather, terrain, screen, Tailwind and Trick Room duration updates.

These effects can cause Pokémon to faint, heal or change stats.

The exact order of residual effects must follow the Champions battle engine. Do not treat all residual effects as one simultaneous event or sort them using the ordinary move-priority table.

When one effect causes a Pokémon to faint, later effects may no longer apply to that Pokémon.

---

## 16. Special Status and Action Restrictions

Some conditions prevent a Pokémon from executing its selected move.

These are not priority modifiers.

Examples:
- Flinching prevents the Pokémon from acting if it has not yet moved.
- Full paralysis can prevent the move from executing.
- Sleep can prevent the Pokémon from acting.
- Freeze can prevent the Pokémon from acting.
- Taunt can prevent the selection or use of Status moves.
- Disable can prevent the use of a specific move.
- Encore can force the use of a previously selected move.
- Recharge effects can prevent a Pokémon from executing a move on the following turn.

The move's position in the queue is still determined by its priority and Speed, but the move may fail or the Pokémon may be unable to act when its turn arrives.

---

## 17. Recommended Turn-Order Algorithm

The AI should use separate event queues rather than sorting every possible action as if it were an ordinary move.

### Phase A — Voluntary switches

1. Identify all player-selected switches.
2. Resolve the switch phase.
3. Process entry hazards.
4. Process entry Abilities and other entry effects in the engine-defined order.

### Phase B — Mega Evolution

1. Identify Pokémon selected to Mega Evolve.
2. Order Mega Evolution actions according to the applicable pre-Mega Speed rule.
3. Apply Mega forms, stats, typing and Abilities.
4. Process Mega Evolution effects.
5. Use the resulting stats for the subsequent move phase.

### Phase C — Move queue

For each selected move:

1. Read its base priority from the move database.
2. Apply conditional priority modifiers, such as Prankster and Gale Wings.
3. Apply move-specific conditional priority, such as Grassy Glide.
4. Apply effects that modify ordering within a priority bracket, such as Quick Claw, Quick Draw and Stall.
5. Order moves by priority.
6. Within the same priority bracket, apply the correct Speed ordering.
7. Reverse Speed ordering under Trick Room.
8. Resolve Speed ties randomly.
9. Apply queue-changing effects such as After You and Quash.
10. Execute the next valid action.

After each move:
- resolve its damage or effect;
- resolve fainting;
- resolve automatic held-item effects;
- resolve pivoting or forced switching;
- process the relevant entry effects;
- continue with the remaining move queue.

The exact handling of queue updates after mid-turn Speed changes must follow the Champions battle engine. Do not assume every Speed change automatically re-sorts all remaining actions.

### Phase D — End of turn

1. Resolve residual damage and healing.
2. Resolve end-of-turn Abilities.
3. Update status counters.
4. Update field-effect durations.
5. Resolve fainting and battle-ending conditions.

---

## 18. Implementation Requirements

For the Pokémon Champions AI:

1. Keep voluntary switching separate from move priority.
2. Keep Mega Evolution separate from move priority.
3. Resolve voluntary switches before Mega Evolution.
4. Resolve Mega Evolution before every move, including priority moves.
5. Use the Mega form's Speed for the move phase in the same turn.
6. Store the actual numeric priority for every move in `moves_database.json`.
7. Apply conditional priority modifiers from the Champions Ability database.
8. Apply conditional move priority, such as Grassy Glide under Grassy Terrain.
9. Use priority first and Speed second.
10. Reverse only Speed order under Trick Room, never priority brackets.
11. Model Quick Claw and Quick Draw as same-bracket ordering effects, not priority modifiers.
12. Model Stall as a same-bracket ordering effect.
13. Model After You and Quash as queue-modifying moves.
14. Model pivot moves as move actions followed by switching.
15. Model forced switching moves at their actual negative priority.
16. Do not implement Pursuit.
17. Resolve entry hazards and entry Abilities as separate events.
18. Keep end-of-turn effects separate from the move queue.
19. Use the Champions battle engine as the reference for ambiguous or unverified ordering interactions.

---

## Sources

- [DexDB — Pokémon Champions mechanics ledger](https://dexdb.io/champions/mechanics/)
- [DexDB — Mega Evolution timing](https://dexdb.io/champions/mechanics/mega-timing/)
- [DexDB — Priority move data and mechanics](https://dexdb.io/moves/)
- [PokéBase — Pokémon Champions move priority data](https://pokebase.app/pokemon-champions/moves?filter=traits%3D%5B%22priority%22%5D)
- [Serebii — Pokémon Champions available moves](https://www.serebii.net/pokemonchampions/moves.shtml)
- [Serebii — Pokémon Champions AttackDex](https://www.serebii.net/attackdex-champions/)
- [INF VGC — Mega Evolution timing and turn order](https://infovgc.com/blog/megaevolucion-reg-m-c)
- [Smogon — Pokémon Champions battle mechanics research](https://www.smogon.com/forums/threads/champions-battle-mechanics-research.3780372/)

**Document scope:** General turn order, move priority, switching, Mega Evolution and action sequencing. Current Regulation Set restrictions and the current legal Pokémon or item pool are maintained separately.

Last researched: 2026-11-18.