#!/usr/bin/env python3
"""
Through the Ages Coaching CLI

Analyzes your current game state and provides strategic coaching advice
powered by the Claude AI with embedded tournament-level strategy knowledge.

Usage:
  # Get top 3 move suggestions for your current state:
  python coach_cli.py --state ../data/example_game_states/age2_normal.json

  # Evaluate a specific move you are considering:
  python coach_cli.py --state ../data/example_game_states/age2_normal.json --move "Draft Code of Laws"

  # Use a different Claude model:
  python coach_cli.py --state ../data/example_game_states/age2_normal.json --model claude-opus-4-6

Setup:
  pip install -r requirements.txt
  cp ../.env.example ../.env
  # Edit .env and add your ANTHROPIC_API_KEY
"""

import json
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows (handles em-dashes, arrows, etc. in Claude responses)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load .env file if present (look up the directory tree)
try:
    from dotenv import load_dotenv
    # Search up to 3 levels up for a .env file
    for parent in [Path(__file__).parent, Path(__file__).parent.parent]:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break
except ImportError:
    pass  # dotenv optional; user can set env var directly

try:
    import anthropic
except ImportError:
    print("ERROR: 'anthropic' package not installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: 'pyyaml' package not installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent
STRATEGY_DIR = REPO_ROOT / "strategy"
PROMPTS_DIR = REPO_ROOT / "prompts"


# ── Data Loading ───────────────────────────────────────────────────────────────

def load_strategy_context() -> str:
    """Load all strategy YAML files into a single formatted context block."""
    if not STRATEGY_DIR.exists():
        return ""

    parts = []
    # Consistent ordering: military first (most relevant), then age guide, then others
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

    # Pick up any additional YAML files not in the ordered list
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
    # Minimal fallback if file is missing
    return (
        "You are an expert Through the Ages coach specializing in tournament-level "
        "adaptive play for 4-player games with military escalation dynamics."
    )


# ── Game State Formatting ──────────────────────────────────────────────────────

def format_game_state(state: dict) -> str:
    """Convert game state dict to a readable text block for the prompt."""
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

        # Compute military gaps for context
        player_mil = player.get("military_strength", 0)
        for i, opp in enumerate(opponents, 1):
            opp_mil = opp.get("military_strength", "?")
            gap_str = ""
            if isinstance(opp_mil, (int, float)) and isinstance(player_mil, (int, float)):
                gap = opp_mil - player_mil
                if gap > 0:
                    gap_str = f"  [GAP: +{gap} vs you]"
                elif gap < 0:
                    gap_str = f"  [GAP: {gap} vs you]"
                else:
                    gap_str = "  [TIED]"

            opp_line = (
                f"  Opponent {i}: "
                f"Military {opp_mil}{gap_str}  |  "
                f"~{opp.get('culture_production_estimate', '?')} culture/turn  |  "
                f"~{opp.get('culture_points_estimate', '?')} pts"
            )
            note = opp.get("_note") or opp.get("notes")
            if note:
                opp_line += f"  [{note}]"
            lines.append(opp_line)

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


def compute_military_summary(state: dict) -> Optional[str]:
    """Generate a quick military situation summary for context."""
    player = state.get("player", {})
    opponents = state.get("opponents", [])
    player_mil = player.get("military_strength")

    if not isinstance(player_mil, (int, float)) or not opponents:
        return None

    opp_strengths = [
        o.get("military_strength")
        for o in opponents
        if isinstance(o.get("military_strength"), (int, float))
    ]
    if not opp_strengths:
        return None

    max_opp = max(opp_strengths)
    gap = max_opp - player_mil

    if gap > 2:
        return f"!! MILITARY WARNING: Gap of {gap} vs strongest opponent (threshold is 2)"
    elif gap > 0:
        return f"Military gap: {gap} vs strongest opponent (within safe threshold)"
    else:
        return f"Military: you are leading or tied with all opponents"


# ── Prompt Building ────────────────────────────────────────────────────────────

def build_suggest_prompt(game_state_text: str) -> str:
    return f"""Here is the current game state:

{game_state_text}

Please analyze this game state and suggest the top 3 moves I should consider this turn,
ranked by strategic priority.

For each move:
1. Name the action clearly
2. Explain why it is the right move given the current numbers
3. Note any trade-offs or conditions that could change the recommendation

Then provide one overall strategic insight about my current game state —
what is my biggest structural advantage or risk right now?"""


def build_evaluate_prompt(game_state_text: str, proposed_move: str) -> str:
    return f"""Here is the current game state:

{game_state_text}

PROPOSED MOVE: {proposed_move}

Please evaluate this move with:
1. A score from 1-10 (10 = perfectly optimal given the situation)
2. Your assessment: why is this move good or bad given this specific game state?
3. Specific reasoning referencing actual numbers (military gaps, civil actions,
   science production, culture rate, etc.)
4. If the score is below 8: the top 2 alternative moves you would recommend instead
5. One specific action or situation to watch for next turn"""


# ── API Call ───────────────────────────────────────────────────────────────────

def call_claude(system_prompt: str, user_message: str, model: str) -> str:
    """Call the Claude API and return the text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nERROR: ANTHROPIC_API_KEY is not set.")
        print("Options:")
        print("  1. Create a .env file in the repo root with: ANTHROPIC_API_KEY=your_key")
        print("  2. Or export it: export ANTHROPIC_API_KEY=your_key")
        print("\nGet an API key at: https://console.anthropic.com")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


# ── Display ────────────────────────────────────────────────────────────────────

WIDTH = 60

def divider(char: str = "-") -> str:
    return char * WIDTH

def header(title: str) -> str:
    pad = (WIDTH - len(title) - 2) // 2
    return f"\n{'=' * WIDTH}\n{' ' * pad} {title}\n{'=' * WIDTH}"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Through the Ages AI Coaching CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Get move suggestions:
    python coach_cli.py --state ../data/example_game_states/age2_normal.json

  Evaluate a specific move:
    python coach_cli.py --state ../data/example_game_states/age2_normal.json \\
        --move "Draft Code of Laws from the card row"

  Use Opus for deeper analysis:
    python coach_cli.py --state ../data/example_game_states/age2_military_crisis.json \\
        --model claude-opus-4-6
        """,
    )
    parser.add_argument(
        "--state",
        required=True,
        help="Path to game state JSON file",
    )
    parser.add_argument(
        "--move",
        default=None,
        help="Proposed move to evaluate (free text). Omit to get top 3 suggestions.",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--no-strategy",
        action="store_true",
        help="Skip injecting strategy YAML into the prompt (faster, uses less tokens)",
    )

    args = parser.parse_args()

    # ── Load game state ──────────────────────────────────────────────────────
    state_path = Path(args.state)
    if not state_path.exists():
        # Try resolving relative to script directory
        state_path = SCRIPTS_DIR / args.state
    if not state_path.exists():
        print(f"ERROR: Game state file not found: {args.state}")
        sys.exit(1)

    with open(state_path, encoding="utf-8") as f:
        game_state = json.load(f)

    # ── Build system prompt ──────────────────────────────────────────────────
    base_system = load_system_prompt()

    if not args.no_strategy:
        strategy_context = load_strategy_context()
        if strategy_context:
            full_system = (
                f"{base_system}\n\n"
                f"---\n\n"
                f"## Strategy Knowledge Base\n\n"
                f"Use the following strategy knowledge when evaluating moves. "
                f"All principles in here represent tournament-level best practices.\n\n"
                f"{strategy_context}"
            )
        else:
            full_system = base_system
    else:
        full_system = base_system

    # ── Format game state ────────────────────────────────────────────────────
    game_state_text = format_game_state(game_state)
    mil_summary = compute_military_summary(game_state)

    # ── Print game state summary ─────────────────────────────────────────────
    print(header("Through the Ages - Coaching System"))
    print(f"\n{divider()}")
    print("CURRENT GAME STATE")
    print(divider())
    print(game_state_text)

    if mil_summary:
        print(f"\n{mil_summary}")

    print(f"\n{divider()}")

    # ── Determine mode and build user prompt ─────────────────────────────────
    if args.move:
        mode_label = "MOVE EVALUATION"
        user_message = build_evaluate_prompt(game_state_text, args.move)
        print(f"Evaluating move: {args.move}")
    else:
        mode_label = "COACHING ADVICE"
        user_message = build_suggest_prompt(game_state_text)
        print("Mode: suggest top 3 moves")

    print(f"Model: {args.model}")
    print(f"\nCalling Claude API...\n")

    # ── Call Claude ──────────────────────────────────────────────────────────
    try:
        response = call_claude(full_system, user_message, args.model)
    except anthropic.APIStatusError as e:
        print(f"ERROR: Claude API returned status {e.status_code}: {e.message}")
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("ERROR: Could not connect to Claude API. Check your internet connection.")
        sys.exit(1)

    # ── Print response ───────────────────────────────────────────────────────
    print(header(mode_label))
    print()
    print(response)
    print(f"\n{'=' * WIDTH}\n")


if __name__ == "__main__":
    main()
