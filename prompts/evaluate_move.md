# Move Evaluation Prompt Template

This file documents the prompt template used by the CLI and backend for move evaluation.
The CLI builds these prompts programmatically using `coach_cli.py`.

---

## Evaluate a Specific Move

```
Here is the current game state:

{game_state}

PROPOSED MOVE: {proposed_move}

Please evaluate this move with:

1. A score from 1-10 (10 = perfectly optimal)
2. Your assessment: why is this move good or bad given this specific game state?
3. Specific reasoning referencing the actual numbers (military strength, civil actions,
   science production, culture production rate, etc.)
4. If the score is below 8: the top 2 alternative moves you would recommend instead
5. One specific action or situation to watch for next turn
```

---

## Request Top Move Suggestions (no specific move provided)

```
Here is the current game state:

{game_state}

Please analyze this game state and suggest the top 3 moves I should consider this turn,
ranked by strategic priority. For each move:

1. Name the action clearly
2. Explain why it is the right move given the current numbers
3. Note any trade-offs or conditions that could change the recommendation

Then provide one overall strategic insight about the current game state —
what is my biggest structural advantage or risk right now?
```

---

## Game State Format Reference

The `{game_state}` block is formatted by `coach_cli.py` from the JSON game state file.
It includes:

- Age, round, player count
- Your civilization: civil actions, military actions, food/ore/science/culture production,
  military strength, culture points, leader, wonders, technologies, hand cards
- Opponents: military strength estimates, culture production estimates, culture point estimates
- Card row: available cards by age
- Next visible event (if known)

---

## Example Evaluation Output

```
SCORE: 7/10

ASSESSMENT: Drafting Code of Laws is a solid move here — getting to 6 civil actions
is a meaningful upgrade — but the urgency is slightly lower than addressing your
military gap first.

REASONING: You have 5 civil actions and your opponents are at 12, 11, and 13 military
strength. You're at 10. The gap to Opponent 1 (13) is 3 — above the safe threshold
of 2. Before next round's military event fires, bringing that gap to 2 or less should
take priority. However, Code of Laws is worth 2 civil actions in one pick and will
pay dividends immediately. If the military event is more than 1 round away, taking
Code of Laws now and building a Knight next turn is the right sequencing.

ALTERNATIVES (if you want to address military gap first):
1. Draft Knights — Closes the military gap efficiently at current ore production level
2. Draft Tactics card — Multiplies your existing military without using ore; raises
   effective strength by ~40% immediately

NEXT TURN: If you take Code of Laws now, your turn 1 priority next round must be
closing the military gap to ≤2 vs Opponent 1 before the next event fires.
```
