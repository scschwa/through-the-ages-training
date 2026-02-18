"""
Through the Ages Coaching API
Run from the backend/ directory: uvicorn main:app --reload --port 8000
"""
from pathlib import Path
from typing import Optional, List

# Load .env before anything else
try:
    from dotenv import load_dotenv
    for parent in [Path(__file__).parent, Path(__file__).parent.parent]:
        if (parent / ".env").exists():
            load_dotenv(parent / ".env")
            break
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import json
import os
import anthropic

from coach import build_full_system_prompt, format_game_state, build_suggest_prompt, build_evaluate_prompt, call_claude

REPO_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"


# ── App Setup ──────────────────────────────────────────────────────────────────

app = FastAPI(title="Through the Ages Coaching API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load strategy + system prompt once at startup (not on every request)
_system_prompt: str = ""

@app.on_event("startup")
async def startup():
    global _system_prompt
    _system_prompt = build_full_system_prompt()


# ── Pydantic Models ────────────────────────────────────────────────────────────

class PlayerState(BaseModel):
    civil_actions: int
    military_actions: int
    food_production: int
    ore_production: int
    science_production: int
    culture_production: int
    military_strength: int
    culture_points: int
    leader: Optional[str] = None
    wonders_complete: List[str] = []
    wonders_in_progress: List[str] = []
    technologies: List[str] = []
    hand_cards: List[str] = []


class OpponentState(BaseModel):
    id: str = "opponent"
    military_strength: int
    culture_production_estimate: Optional[int] = None
    culture_points_estimate: Optional[int] = None


class CardRow(BaseModel):
    age_1_cards: List[str] = []
    age_2_cards: List[str] = []
    age_3_cards: List[str] = []


class Events(BaseModel):
    next_visible: Optional[str] = None


class Meta(BaseModel):
    age: int
    round: int
    player_count: int = 4


class GameState(BaseModel):
    meta: Meta
    player: PlayerState
    opponents: List[OpponentState] = []
    card_row: CardRow = CardRow()
    events: Events = Events()


class SuggestMovesRequest(BaseModel):
    game_state: GameState
    model: str = "claude-sonnet-4-6"


class EvaluateMoveRequest(BaseModel):
    game_state: GameState
    proposed_move: str
    model: str = "claude-sonnet-4-6"


class CoachResponse(BaseModel):
    advice: str
    model: str


class ParseScreenshotRequest(BaseModel):
    image_base64: str
    media_type: str = "image/png"


class ParseScreenshotResponse(BaseModel):
    game_state: dict
    notes: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "strategy_loaded": len(_system_prompt) > 500,
    }


@app.post("/api/suggest-moves", response_model=CoachResponse)
async def suggest_moves(req: SuggestMovesRequest):
    state_dict = req.game_state.model_dump()
    game_state_text = format_game_state(state_dict)
    user_message = build_suggest_prompt(game_state_text)
    try:
        advice = call_claude(_system_prompt, user_message, req.model)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")
    return CoachResponse(advice=advice, model=req.model)


@app.post("/api/evaluate-move", response_model=CoachResponse)
async def evaluate_move(req: EvaluateMoveRequest):
    state_dict = req.game_state.model_dump()
    game_state_text = format_game_state(state_dict)
    user_message = build_evaluate_prompt(game_state_text, req.proposed_move)
    try:
        advice = call_claude(_system_prompt, user_message, req.model)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")
    return CoachResponse(advice=advice, model=req.model)


@app.post("/api/parse-screenshot", response_model=ParseScreenshotResponse)
async def parse_screenshot(req: ParseScreenshotRequest):
    prompt_file = PROMPTS_DIR / "parse_screenshot.md"
    if not prompt_file.exists():
        raise HTTPException(status_code=500, detail="parse_screenshot.md prompt not found")
    vision_prompt = prompt_file.read_text(encoding="utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": req.media_type,
                            "data": req.image_base64,
                        },
                    },
                    {"type": "text", "text": vision_prompt},
                ],
            }],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")

    raw = message.content[0].text.strip()

    # Strip markdown fences if Claude wrapped the JSON anyway
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not parse Claude response as JSON: {str(e)}. Raw (first 300 chars): {raw[:300]}"
        )

    game_state = parsed.get("game_state", parsed)
    notes = parsed.get("notes", "Game state extracted from screenshot.")
    return ParseScreenshotResponse(game_state=game_state, notes=notes)
