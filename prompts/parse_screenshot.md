You are analyzing a screenshot from the board game **Through the Ages: A New Story of Civilization** (Steam or Board Game Arena version).

Your job is to extract the current game state for the **active player** — the player whose board is primarily shown or whose turn it is.

Return a single JSON object with **exactly** this structure and no other text:

```json
{
  "game_state": {
    "meta": {
      "age": 2,
      "round": 3,
      "player_count": 4
    },
    "player": {
      "civil_actions": 5,
      "military_actions": 3,
      "food_production": 8,
      "ore_production": 6,
      "science_production": 4,
      "culture_production": 7,
      "military_strength": 12,
      "culture_points": 34,
      "leader": "Caesar",
      "wonders_complete": ["Pyramids"],
      "wonders_in_progress": [],
      "technologies": ["Chivalry", "Printing Press"],
      "hand_cards": ["Drama", "Knights"]
    },
    "opponents": [
      {"id": "opp1", "military_strength": 14, "culture_production_estimate": 5, "culture_points_estimate": 28},
      {"id": "opp2", "military_strength": 11, "culture_production_estimate": 7, "culture_points_estimate": 32},
      {"id": "opp3", "military_strength": 13, "culture_production_estimate": 4, "culture_points_estimate": 20}
    ],
    "card_row": {
      "age_1_cards": [],
      "age_2_cards": ["Tactics", "Code of Laws", "Aqueduct"],
      "age_3_cards": []
    },
    "events": {
      "next_visible": "Military Dominance"
    }
  },
  "notes": "What you found and any values you were uncertain about or estimated."
}
```

## Extraction Rules

**meta:**
- `age`: Determine from which cards are in play (Bronze/Iron/Steel Age = 1, Chivalry/Printing Press = 2, etc.)
- `round`: Read from the round counter if visible; estimate if not
- `player_count`: Count the number of player boards/tabs visible

**player production values** — these are *per-turn* rates, not totals:
- `food_production`: Count farm/irrigation tokens on the production track
- `ore_production`: Count mine tokens on the production track
- `science_production`: Count library/lab tokens
- `culture_production`: Count theater/arena tokens

**player other:**
- `military_strength`: The total military power shown (sum of all unit tokens + tactics bonus)
- `culture_points`: The running *score total*, not production rate (shown in the score track)
- `civil_actions`: Remaining action tokens (yellow/white tokens available this turn)
- `military_actions`: Remaining military action tokens
- `leader`: Name of the current leader card, or null
- `wonders_complete`: Names of fully built wonders
- `wonders_in_progress`: Wonders currently under construction
- `technologies`: Names of technology cards that have been built (on the player board)
- `hand_cards`: Cards visible in the player's hand (may be empty if face-down)

**opponents:**
- Extract military strength from their boards if visible
- Estimate culture production from visible production track if shown
- Estimate culture points from the score track if visible
- Include only opponents you can actually see data for

**card_row:**
- List cards visible in the card row, sorted by age tier

**For values not visible:** use `null` for strings, `0` for numbers.

**notes:** Briefly describe what was clearly visible vs. what was estimated or not found.

Return ONLY the JSON — no markdown fences, no explanation, no other text.
