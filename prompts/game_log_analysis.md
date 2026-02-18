# Game Log Analysis Prompt Template

This file documents the prompt template used for post-game analysis of Yucata.de game logs.
This feature is part of Phase 4 implementation.

---

## Full Game Log Analysis

```
I am going to share a Through the Ages game log with you. This log captures the full
sequence of moves made by all players across all ages.

Please analyze this game with a focus on:

1. GAME SUMMARY (2-3 sentences): Who won, what was the decisive factor, and when was
   the game effectively decided?

2. TURNING POINTS: Identify 3-5 specific turns where a player's decision significantly
   changed the game trajectory (for better or worse).

3. THE PLAYER'S KEY DECISIONS: For the player named {player_name}, identify:
   - Their best decision of the game and why
   - Their most costly mistake and what they should have done instead
   - A moment where adaptive play would have helped them (e.g., military escalation
     response, CA timing, wonder sequencing)

4. MILITARY DYNAMICS: How did the military situation evolve? Was there an escalation
   pattern? Who benefited from it and who was drained by it?

5. ACTIONABLE COACHING POINTS: 3 specific things {player_name} should do differently
   in their next game based on this analysis.

Game log follows:

{game_log_json}
```

---

## Turn-by-Turn Analysis (for a specific range of turns)

```
Here is a sequence of turns from a Through the Ages game. Please evaluate each of
{player_name}'s moves in this sequence:

For each move, provide:
- A brief assessment (1-2 sentences)
- A score 1-10
- The best alternative if the score is below 7

Focus especially on:
- Civil action efficiency (was every CA well spent?)
- Military threshold maintenance
- Science and culture production growth rate
- Wonder timing

Turn sequence:

{turn_sequence}
```

---

## Yucata Log Format Notes

When Phase 4 is implemented, the `yucata_parser.py` script will:
1. Load `yucataplays.json` from Yucata.de
2. Extract per-turn game state reconstructions
3. Format them into the template above
4. Send to Claude for analysis
5. Return a structured report

The Yucata format includes full move sequences, player choices, and card draws for
all players. It does NOT include hidden information (cards in hand that were not played).

---

## Screenshot Analysis Fallback (Steam Games)

For Steam games where no log is available, use the in-game progression graphs:

```
This is a screenshot of the end-of-game progression graphs from Through the Ages.
The graphs show all players' progression over time for: food production, ore production,
military strength, science production, and culture production.

Please analyze:
1. At what point did the winner's trajectory diverge from the others?
2. Which resource(s) did the winner dominate that others neglected?
3. Was there a military escalation event visible in the military strength graph?
   If so, which players were drained by it and which benefited?
4. What should the player who came in {player_position} have done differently
   based on their production curves?

Use this analysis to give 3 specific coaching points for the next game.
```
