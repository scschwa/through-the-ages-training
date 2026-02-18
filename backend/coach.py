"""
Core coaching logic — shared between the CLI tool and the web backend.
"""
import os
from pathlib import Path
from typing import Optional

import anthropic
import yaml

REPO_ROOT = Path(__file__).parent.parent
STRATEGY_DIR = REPO_ROOT / "strategy"
PROMPTS_DIR = REPO_ROOT / "prompts"


def load_strategy_context() -> str:
    """Load all strategy YAML files into a single formatted context block."""
    if not STRATEGY_DIR.exists():
        return ""

    parts = []
    ordered_files = [
        "military.yaml",
        "age_guide.yaml",
        "card_priority.yaml",
        "leaders.yaml",
        "wonders.yaml",
    ]

    for filename in ordered_files:
        yaml_file = STRATEGY_DIR / filename
        if yaml_file.exists():
            with open(yaml_file, encoding="utf-8") as f:
                content = f.read()
            title = filename.replace(".yaml", "").replace("_", " ").title()
            parts.append(f"### {title}\n\n```yaml\n{content}\n```")

    for yaml_file in sorted(STRATEGY_DIR.glob("*.yaml")):
        if yaml_file.name not in ordered_files:
            with open(yaml_file, encoding="utf-8") as f:
                content = f.read()
            title = yaml_file.stem.replace("_", " ").title()
            parts.append(f"### {title}\n\n```yaml\n{content}\n```")

    return "\n\n---\n\n".join(parts)


def load_system_prompt() -> str:
    """Load the main coaching system prompt."""
    system_file = PROMPTS_DIR / "coach_system.md"
    if system_file.exists():
        return system_file.read_text(encoding="utf-8")
    return (
        "You are an expert Through the Ages coach specializing in tournament-level "
        "adaptive play for 4-player games with military escalation dynamics."
    )


def build_full_system_prompt() -> str:
    """Build the complete system prompt with embedded strategy knowledge."""
    base = load_system_prompt()
    strategy = load_strategy_context()
    if strategy:
        return (
            f"{base}\n\n---\n\n"
            f"## Strategy Knowledge Base\n\n"
            f"Use the following strategy knowledge when evaluating moves. "
            f"All principles here represent tournament-level best practices.\n\n"
            f"{strategy}"
        )
    return base


def format_game_state(state: dict) -> str:
    """Convert a game state dict to a readable text block for the prompt."""
    lines = []

    meta = state.get("meta", {})
    lines.append(
        f"AGE: {meta.get('age', '?')}  |  "
        f"ROUND: {meta.get('round', '?')}  |  "
        f"PLAYERS: {meta.get('player_count', '?')}"
    )

    player = state.get("player", {})
    lines.append("\nYOUR CIVILIZATION:")
    lines.append(
        f"  Civil Actions: {player.get('civil_actions', '?')}  |  "
        f"Military Actions: {player.get('military_actions', '?')}"
    )
    lines.append(
        f"  Food Production: {player.get('food_production', '?')}/turn  |  "
        f"Ore Production: {player.get('ore_production', '?')}/turn"
    )
    lines.append(
        f"  Science: {player.get('science_production', '?')}/turn  |  "
        f"Culture Production: {player.get('culture_production', '?')}/turn"
    )
    lines.append(
        f"  Military Strength: {player.get('military_strength', '?')}  |  "
        f"Culture Points: {player.get('culture_points', '?')}"
    )

    leader = player.get("leader")
    if leader:
        lines.append(f"  Leader: {leader}")

    wonders_complete = player.get("wonders_complete", [])
    if wonders_complete:
        lines.append(f"  Wonders Complete: {', '.join(wonders_complete)}")

    wonders_in_progress = player.get("wonders_in_progress", [])
    if wonders_in_progress:
        lines.append(f"  Wonders In Progress: {', '.join(wonders_in_progress)}")

    technologies = player.get("technologies", [])
    if technologies:
        lines.append(f"  Technologies: {', '.join(technologies)}")

    hand_cards = player.get("hand_cards", [])
    if hand_cards:
        lines.append(f"  Cards in Hand: {', '.join(hand_cards)}")

    opponents = state.get("opponents", [])
    if opponents:
        lines.append("\nOPPONENTS:")
        player_mil = player.get("military_strength", 0)
        for i, opp in enumerate(opponents, 1):
            opp_mil = opp.get("military_strength", "?")
            gap_str = ""
            if isinstance(opp_mil, (int, float)) and isinstance(player_mil, (int, float)):
                gap = opp_mil - player_mil
                gap_str = f"  [GAP: +{gap}]" if gap > 0 else (f"  [GAP: {gap}]" if gap < 0 else "  [TIED]")
            lines.append(
                f"  Opponent {i}: Military {opp_mil}{gap_str}  |  "
                f"~{opp.get('culture_production_estimate', '?')} culture/turn  |  "
                f"~{opp.get('culture_points_estimate', '?')} pts"
            )

    card_row = state.get("card_row", {})
    available_cards = []
    for age_key in ["age_1_cards", "age_2_cards", "age_3_cards"]:
        available_cards.extend(card_row.get(age_key, []))
    if available_cards:
        lines.append(f"\nCARD ROW: {', '.join(available_cards)}")

    events = state.get("events", {})
    next_event = events.get("next_visible")
    if next_event:
        lines.append(f"\nNEXT EVENT: {next_event}")

    return "\n".join(lines)


def build_suggest_prompt(game_state_text: str) -> str:
    return f"""Here is the current game state:

{game_state_text}

Please analyze this game state and suggest the top 3 moves I should consider this turn,
ranked by strategic priority.

For each move:
1. Name the action clearly
2. Explain why it is the right move given the current numbers
3. Note any trade-offs or conditions that could change the recommendation

Then provide one overall strategic insight about my current game state."""


def build_evaluate_prompt(game_state_text: str, proposed_move: str) -> str:
    return f"""Here is the current game state:

{game_state_text}

PROPOSED MOVE: {proposed_move}

Please evaluate this move with:
1. A score from 1-10 (10 = perfectly optimal)
2. Your assessment: why is this move good or bad given this specific game state?
3. Specific reasoning referencing actual numbers (military gaps, civil actions, science, culture rate)
4. If the score is below 8: the top 2 alternative moves you would recommend instead
5. One specific action or situation to watch for next turn"""


def call_claude(system_prompt: str, user_message: str, model: str = "claude-sonnet-4-6") -> str:
    """Call the Claude API and return the text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text
