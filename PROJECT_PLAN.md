# Through the Ages: Training System

> A personal coaching and analysis system for competitive multiplayer play, tailored for the 4-player arms-race meta.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem: Military Escalation in 4-Player Games](#2-the-problem-military-escalation-in-4-player-games)
3. [Strategy Knowledge Base](#3-strategy-knowledge-base)
   - 3.1 The Adaptive Framework
   - 3.2 Military Escalation Management
   - 3.3 Age-by-Age Priority Guide
   - 3.4 Card Draft Priority Hierarchy
   - 3.5 Leader & Wonder Tier Notes
   - 3.6 Event Deck Awareness
4. [Steam Game History: What's Possible](#4-steam-game-history-whats-possible)
5. [Interactive Coaching App Architecture](#5-interactive-coaching-app-architecture)
   - 5.1 Vision
   - 5.2 Tech Stack
   - 5.3 Core Components
   - 5.4 Data Model
   - 5.5 API Design
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Repository File Structure](#7-repository-file-structure)
8. [Quick Start Guide](#8-quick-start-guide)
9. [Resources & References](#9-resources--references)

---

## 1. Executive Summary

This repository contains the plan and eventual codebase for a **Through the Ages coaching system** — a combination of strategy reference material and an interactive web application that analyzes game states and provides coaching feedback in real time.

The system is designed around one specific challenge: playing 4-player Through the Ages against friends who engage in coordinated military escalation, making both pure builder and pure militarist strategies unreliable. The answer, validated by tournament-level analysis, is **adaptive play** — a flexible approach that permanently evades the arms-race trap.

**Three deliverables:**

| Deliverable | Status | Description |
|---|---|---|
| Strategy Knowledge Base | In this document | Competitive strategy reference for tournament-level adaptive play |
| Interactive Coaching App | To be built | Web app: input game state → get coaching feedback via Claude AI |
| Steam Game Analysis | Research spike needed | Post-game analysis of past games; partially blocked by missing data format |

---

## 2. The Problem: Military Escalation in 4-Player Games

The situation is common in group play: the moment one player builds military, everyone else builds a little more. The moment you ignore military entirely, everyone builds just enough to outpace you. This creates a **group equilibrium trap** where:

- Building military → opponents escalate harder, outpacing you
- Ignoring military → opponents sit just above you and extract value via aggression

This is not a flaw in the game — it's a real strategic tension that tournament players have studied extensively. The solution is not to win the arms race or opt out of it. The solution is to **weaponize the arms race against the others**.

### The Key Insight

In a 4-player game, three players collectively building military hurts each of them individually. Every civil action spent on military is a civil action not spent on economy, science, or culture. If you are the player who understands the *minimum viable military threshold*, you can:

1. Hold that threshold cheaply
2. Let the other three overbuild relative to each other
3. Win on culture points while they waste actions in an escalation loop

This is described in detail in Section 3.

---

## 3. Strategy Knowledge Base

### 3.1 The Adaptive Framework

The single biggest mistake in Through the Ages is committing to a strategic identity too early — "I am going to be the military player" or "I am going to be the culture engine." Tournament-level play is defined by **reactive adaptation**: every decision is made in response to the current game state, not a pre-game plan.

**Mental model**: At the start of each age, ask four questions:

1. **Am I within military range?** (Can I afford one strong attack, or absorb one?)
2. **Is my science keeping pace?** (Will I be able to upgrade in the next age?)
3. **Are my civil actions maxed for this age?** (Am I leaving cards undrawn?)
4. **What is my culture production rate vs. the table?** (Am I winning the long game?)

If all four answers are yes, you are in a strong position regardless of your current military ranking. If any is no, that gap is your priority.

**The adaptive cycle:**

```
Each Round:
  Assess military gap vs. each opponent
  ├── Gap > 2: Address immediately (warfare card or military unit)
  ├── Gap 0–2: Monitor, do not react
  └── You lead: Invest elsewhere; never escalate voluntarily

  Assess science production
  ├── < 3 per turn by Age I end: Science is your bottleneck
  └── ≥ 3: Proceed to next Age upgrades normally

  Assess civil actions
  ├── < 5 by mid-Age I: CA acquisition is top priority
  └── ≥ 5: Proceed normally; consider 6th CA in Age II

  Take the highest-value available action given the above
```

### 3.2 Military Escalation Management

#### The "Hair's Breadth" Rule

You do not need to lead in military. You do not even need to be second. What you need is to be **close enough that attacking you costs the attacker more than the attack is worth**.

In practice, this means:

- **Target differential**: Stay within ~2 military strength of the weakest-looking aggressor
- **Posture, not power**: A Swordsmen + Tactics card is often sufficient to deter a raid even without leading strength
- **Threat math**: An opponent considering aggression against you must ask: "Is the reward worth the lost civil action and the card I burn on war?" Make the answer no.

#### The Escalation Trap (Your Friends' Mistake)

When three players simultaneously escalate military against each other, they fall into what competitive players call the **escalation drain**:

- Each military action is a civil action not spent on food → fewer workers → less production
- Fewer workers means slower wonders, fewer blue cards built, slower science upgrades
- By Age III, escalating players often find themselves with strong militaries and weak culture production — and culture wins the game

Your goal: be the one player at the table who did *not* drain their economy into the escalation loop. Let your friends police each other.

#### The Counter-Escalation Move

If you find yourself being targeted because you look "safe" (low military, high culture):

1. **Buy one military card immediately** — not to win the arms race, but to raise the cost of attacking you
2. **Draft the best available Tactics card** — Tactics multiply the strength of existing units; this is often better than adding raw units
3. **Announce intent (if playing with friends who discuss)**: "If anyone hits me I'm going to spend the next three turns doing nothing but military" — deterrence via credible threat

#### Age III Inflection Point

By late Age II / early Age III, military dynamics shift:

- Air Force replaces earlier units as the dominant force multiplier
- Whoever has the most accumulated science will upgrade to modern military fastest
- The player with the best economy (most food/resources) can build military *and* build wonders simultaneously

This is why science and economy are the true foundations of military power — not early unit purchases.

### 3.3 Age-by-Age Priority Guide

#### Age I: Foundation

| Priority | Action | Why |
|---|---|---|
| 1 | Get 5th Civil Action | Highest ROI move in the game. Every future action is worth more. |
| 2 | Establish 3+ science/turn | Science enables all future upgrades. Cannot be overproduced. |
| 3 | Grab 1–2 military units | Swordsmen or Knights. Cheap, strong, enables Tactics. |
| 4 | Bronze Age infrastructure | Get food and resource production online. |
| 5 | Draft Warfare if missing 3rd MA | A 3rd Military Action enables better card cycling. |

**Age I danger signals:**
- Ending Age I with only 4 civil actions → you are behind, catch up immediately in Age II
- No science building → you will miss Age II upgrades
- Military strength more than 3 below any opponent → become a raid target

#### Age II: Acceleration

| Priority | Action | Why |
|---|---|---|
| 1 | Add 1–2 more Civil Actions (if not at 6) | More CAs = more cards per round = better drafting options |
| 2 | Upgrade military to Knights/Chivalry | Most cost-efficient military in Age II |
| 3 | Build 1–2 Age II wonders | Points + special abilities |
| 4 | Establish strong culture production | Culture snowballs; start now |
| 5 | Maintain military within "hair's breadth" | Never lose sight of the military gap |

**Key Age II cards to prioritize (if available):**
- Code of Laws (2 CAs)
- Drama / Renaissance (culture engines)
- Any strong Tactics card
- Printing Press / Library (science)

#### Age III: Endgame

| Priority | Action | Why |
|---|---|---|
| 1 | Upgrade to Age III military (Air Force) if you plan to fight | Air Force is decisive |
| 2 | Complete an Age III wonder | End-game point injection; 1 per game unless exceptional economy |
| 3 | Maximize culture production | All culture cards, events, and bonus points culminate here |
| 4 | Political leverage | Use military threat credibly to extract event bonuses |

**Age III trap**: Do not start an Age III wonder you cannot finish. An incomplete wonder costs you the production and gives nothing back.

### 3.4 Card Draft Priority Hierarchy

When multiple cards are available and you can only take one:

```
Tier 1 — Always Consider First
  ├── Civil Action card (if below 6 CAs)
  ├── Military Action card (if below 3 MAs and no Warfare)
  └── Science building (if below 3/turn)

Tier 2 — Strong Pickups
  ├── Knights / Swordsmen (Age I–II military)
  ├── Tactics cards (multiply existing units)
  ├── Culture engines (Drama, Shakespeare's plays)
  └── Wonder enablers (if you have a specific wonder in play)

Tier 3 — Situational
  ├── Economic upgrades (farms, mines) — good early, diminishing returns
  ├── Colony cards — strong if you have Military Actions to spare
  └── Leader upgrades — depends heavily on your current leader

Tier 4 — Deny Opponent
  ├── Take a card an opponent needs even if it's suboptimal for you
  └── Especially: deny powerful military cards when you are in a strong position
```

**Draft order awareness**: In 4-player games, the player who goes last in draft often has fewer good options but can better react to what was taken. Adapt your priorities based on your draft position.

### 3.5 Leader & Wonder Tier Notes (New Leaders & Wonders Expansion)

#### Leaders to Watch

| Leader | Strength | Best Pairing |
|---|---|---|
| Napoleon | Late-game military dominance | Age III military push |
| Genghis Khan | Early-mid aggressive raiding | Tactics + Knights |
| Caesar | Military + production efficiency | Mixed game |
| Shakespeare | Exceptional culture rate | Requires military deterrence |
| Columbus | Colonial expansion engine | Extra Military Actions |
| Newton | Science acceleration | Science → tech rush |

**Note on Shakespeare**: Extremely powerful in culture, but makes you a target. Only viable if you establish military credibility first or your opponents are busy fighting each other.

#### Wonder Considerations

- **Age III wonders**: One per game unless you have an exceptional production engine. Plan which one by mid-Age II.
- **New expansion wonders**: The Silk Road and Red Cross wonders add economic and military recovery dimensions — worth understanding before they come up in your game.
- **Wonder timing**: Never start a wonder in the last 2–3 turns of an Age if you won't complete it before the Age ends — you'll lose the investment.

### 3.6 Event Deck Awareness

Events are often overlooked by casual players but are critical at competitive levels:

- **Events benefit strong civilizations disproportionately**. Being in the lead on culture, science, or military when key events fire amplifies your lead significantly.
- **Military events** (raids, wars) can completely reverse a game position. Tracking when age-end military events are likely is essential.
- **Know the event deck composition** for each age — the general distribution of military vs. culture vs. science events shapes your risk profile.

---

## 4. Steam Game History: What's Possible

### Current State of Access

| Platform | Data Access | Notes |
|---|---|---|
| Steam (CGE) | ❌ No export | Binary save files, no documented format |
| Board Game Arena | ❌ No API | ToS prohibits scraping; no official export |
| CGE Online (czechgames.com) | ❌ No public API | Official asynchronous play; no documented API |
| **Yucata.de** | ✅ Full JSON export | Documented `yucataplays.json` format with full replay |

### Steam Save File Investigation (Research Spike)

The Steam version stores saves at:
```
C:\Program Files (x86)\Steam\userdata\<YOUR_STEAM_ID>\758370\remote\SAVES\
```
(Replace `758370` with Through the Ages' Steam App ID.)

To investigate the format:
1. Navigate to the save directory
2. Copy a save file and open with a hex editor (HxD is free on Windows)
3. Look for: JSON patterns, repeated structures, known strings (card names, resource labels)
4. If JSON/text: parse directly; if binary: use a format reverse-engineering approach (comparing multiple saves to identify variable sections)

**Estimated effort**: 2–4 hours for initial reconnaissance; 1–2 days to build a working parser if format is tractable.

**Likely outcome**: The format is either CGE's proprietary binary format (hard to parse without documentation) or an obfuscated JSON/protobuf (potentially parseable). Community research suggests no one has published a working parser.

### Recommended Path: Yucata.de Parallel Play

The pragmatic solution for game analysis now:

1. **Play games on Yucata.de** alongside your Steam games — it's free and supports asynchronous 4-player
2. After each game, export the `yucataplays.json` log
3. Feed the log into the coaching app's analyzer (Phase 4 of implementation)
4. Get turn-by-turn analysis: "On turn 14, taking the Warfare card instead of the second farm would have been +7 points EV by end of game"

### Screenshot Analysis Fallback

The Steam version displays in-game progression graphs for all players (food, resources, military, science, culture over time). These can be analyzed via screenshot + Claude Vision API:

1. Screenshot the end-of-game graphs
2. Send to Claude Vision with prompt: "Analyze this Through the Ages progression chart. Identify the turning points where the winner diverged from other players."

This won't give move-by-move analysis but does provide post-game insight into *when* games were won or lost.

---

## 5. Interactive Coaching App Architecture

### 5.1 Vision

A web application where you can:

1. **Track your current game state** as you play on Steam (input your board state each turn)
2. **Before making a move**, input your proposed action and receive coaching feedback
3. **After a game**, load a Yucata JSON log and receive turn-by-turn analysis
4. **Study strategy** via an interactive reference guide built into the app

The coaching engine uses the Claude API (claude-sonnet-4-6) with a deeply embedded strategy knowledge base, calibrated specifically for the 4-player arms-race meta described in this document.

### 5.2 Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React (Vite) + Tailwind CSS | Fast iteration, great component ecosystem, good for forms and dashboards |
| Backend | Python FastAPI | Lightweight API server; excellent Python AI/ML ecosystem |
| AI Layer | Anthropic Claude API (claude-sonnet-4-6) | Best-in-class natural language coaching; strong rule comprehension |
| Heuristics | Python (custom evaluator) | Rule-based move scoring before LLM evaluation |
| State Storage | JSON files (local) or SQLite | No database overhead needed initially |
| Hosting | Local (`localhost`) or Vercel/Railway | Run it on your machine; optionally host for remote access |
| Packaging | Optional Electron wrapper | Desktop app distribution if preferred |

### 5.3 Core Components

#### Component 1: Game State Tracker

A form-based UI for entering your current board state. Fields:

- **General**: Current age, round number, turn within round
- **Your civilization**: Civil actions, military actions, food/ore production, science production, culture production, current military strength, current culture points
- **Your hand**: Cards currently held (free-text or dropdown)
- **Card row**: Cards currently visible in the card row (free-text)
- **Opponents**: For each opponent — estimated military strength, estimated culture production, approximate culture points
- **Wonders**: Which wonders are in progress, which are complete
- **Events**: Next event card visible (if known)

The tracker persists state between turns so you only need to input *changes* each round.

#### Component 2: Move Evaluator

Core coaching flow:

```
User inputs: proposed move + current game state
        ↓
Heuristic pre-filter: score move against rule-based criteria
        ↓
Claude prompt: game state + proposed move + strategy knowledge + "evaluate this move"
        ↓
Output:
  - Move quality score (1–10)
  - Reasoning ("You're sacrificing a CA for 1 military unit when you're already within range")
  - Top 2 alternative moves with brief rationale
  - One specific pattern to watch for next turn
```

#### Component 3: Coaching Engine (Claude Prompt Architecture)

The system prompt embeds:
- Full adaptive strategy framework (Section 3 of this document)
- Military escalation heuristics specific to 4-player games
- Age-by-age priority tables
- Card draft hierarchy
- The specific situation context: "This player's friends tend to military-escalate; the goal is adaptive positioning, not arms-race participation"

The user-turn prompt provides:
- Current game state (serialized JSON → readable text)
- The specific move under consideration
- Any clarifying context

Output format is structured: score, reasoning, alternatives, next-turn tip.

#### Component 4: Game Log Analyzer

For Yucata.de JSON logs:

1. Parse `yucataplays.json` into turn sequence
2. For each turn, reconstruct game state
3. Evaluate each player's move against the coaching engine
4. Generate a full-game report: "The game was decided on Turn 19 when Player A took the War card against Player C, exposing Player B as the cultural winner."

#### Component 5: Strategy Dashboard

An interactive reference built into the app:
- Searchable strategy guide (the content of Section 3)
- Quick-reference card priority table
- Military threshold calculator: given opponent strengths, what's the minimum military you need?
- Wonder timing planner: given current production, when will you complete a wonder?

### 5.4 Data Model

**Game State Object (JSON)**

```json
{
  "meta": {
    "age": 2,
    "round": 4,
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
    "wonders_complete": ["Pyramids"],
    "wonders_in_progress": [],
    "leader": "Shakespeare",
    "hand_cards": ["Knights", "Drama"],
    "technologies": ["Chivalry", "Printing Press"]
  },
  "opponents": [
    {
      "id": "opponent_1",
      "military_strength": 14,
      "culture_production_estimate": 5,
      "culture_points_estimate": 28
    }
  ],
  "card_row": {
    "age_1_cards": [],
    "age_2_cards": ["Code of Laws", "Tactics", "Aqueduct"],
    "age_3_cards": []
  },
  "events": {
    "next_visible": "Military Dominance"
  }
}
```

**Move Object (JSON)**

```json
{
  "action_type": "draft_card",
  "card_name": "Code of Laws",
  "cost_civil_actions": 1,
  "rationale": "Need another civil action to keep pace with card draw"
}
```

### 5.5 API Design

```
POST /api/evaluate-move
  Body: { game_state: GameState, proposed_move: Move }
  Response: { score: int, reasoning: string, alternatives: Move[], next_turn_tip: string }

POST /api/suggest-moves
  Body: { game_state: GameState }
  Response: { top_moves: [{ move: Move, score: int, rationale: string }] }

POST /api/analyze-game-log
  Body: { yucata_log: object }
  Response: { turn_analysis: TurnAnalysis[], game_summary: string, key_decisions: Decision[] }

GET /api/strategy/{topic}
  Params: topic = "military" | "age_i" | "age_ii" | "age_iii" | "card_draft" | "leaders"
  Response: { content: string, quick_reference: object }

GET /api/military-threshold
  Params: opponent_strengths[]
  Response: { minimum_strength: int, reasoning: string }
```

---

## 6. Implementation Roadmap

### Phase 1 — Strategy Foundation (Weeks 1–2)

**Goal**: Validate the coaching engine before building UI.

- [x] Convert strategy knowledge base (Section 3) into structured YAML files (`strategy/military.yaml`, `strategy/age_guide.yaml`, etc.)
- [x] Write the Claude system prompt (`prompts/coach_system.md`) embedding all strategy
- [x] Build CLI tool (`scripts/coach_cli.py`): accepts game state JSON → prints coaching advice
- [ ] Test the CLI with 5–10 real game scenarios (3 example states included; add your own)
- [ ] Refine prompt based on output quality

**Success criteria**: CLI tool gives advice that matches what an experienced player would say for 80%+ of test scenarios.

### Phase 2 — Web App MVP (Weeks 3–5)

**Goal**: Working end-to-end web application.

- [ ] Initialize FastAPI backend (`backend/`)
- [ ] Initialize React frontend with Vite (`frontend/`)
- [ ] Implement `POST /api/evaluate-move` endpoint
- [ ] Build game state input form (basic HTML form, not polished)
- [ ] Wire form → API → display coaching response
- [ ] Local dev setup: `npm run dev` (frontend) + `uvicorn` (backend)

**Success criteria**: You can input a game state and get coaching feedback in the browser.

### Phase 3 — Enhanced Coaching (Weeks 6–8)

**Goal**: App becomes genuinely useful during play.

- [ ] Add persistent game session (state carries forward turn to turn)
- [ ] Implement `POST /api/suggest-moves` (proactive suggestions, not just evaluation)
- [ ] Add heuristic pre-evaluator in Python (rule-based scoring before Claude call)
- [ ] Build Strategy Dashboard (searchable reference guide in the app)
- [ ] Add military threshold calculator
- [ ] Polish UI (Tailwind CSS, readable layout)
- [ ] Add session history (log of moves + coaching across a game)

**Success criteria**: You can track an entire game session and review coaching advice across all turns.

### Phase 4 — Data Integration (Weeks 9–10)

**Goal**: Post-game analysis from real game data.

- [ ] Build Yucata JSON log parser (`backend/parsers/yucata_parser.py`)
- [ ] Implement `POST /api/analyze-game-log` endpoint
- [ ] Build game log analysis UI (upload log → view per-turn report)
- [ ] Steam save file research spike:
  - Locate save files, inspect with hex editor
  - Attempt to identify format (JSON, protobuf, proprietary binary)
  - If parseable: build Steam log parser; if not: document and defer
- [ ] Screenshot analysis feature: upload Steam graph screenshot → Claude Vision summary

**Success criteria**: You can upload a Yucata game log and get a post-game analysis report.

---

## 7. Repository File Structure

```
through-the-ages-training/
│
├── PROJECT_PLAN.md              ← This document
│
├── strategy/                    ← Strategy knowledge base (structured data)
│   ├── military.yaml
│   ├── age_guide.yaml
│   ├── card_priority.yaml
│   ├── leaders.yaml
│   └── wonders.yaml
│
├── prompts/                     ← Claude prompt templates
│   ├── coach_system.md          ← Main coaching system prompt
│   ├── evaluate_move.md         ← Move evaluation prompt template
│   └── game_log_analysis.md     ← Post-game analysis prompt
│
├── scripts/                     ← CLI tools and utilities
│   ├── coach_cli.py             ← Command-line coaching tool
│   └── steam_save_inspector.py  ← Steam save file reverse engineering
│
├── backend/                     ← Python FastAPI server
│   ├── main.py
│   ├── routers/
│   │   ├── evaluate.py
│   │   ├── strategy.py
│   │   └── game_log.py
│   ├── models/
│   │   ├── game_state.py
│   │   └── move.py
│   ├── parsers/
│   │   └── yucata_parser.py
│   ├── evaluators/
│   │   └── heuristic_evaluator.py
│   └── requirements.txt
│
├── frontend/                    ← React (Vite) application
│   ├── src/
│   │   ├── components/
│   │   │   ├── GameStateForm.jsx
│   │   │   ├── MoveEvaluator.jsx
│   │   │   ├── CoachingPanel.jsx
│   │   │   ├── StrategyDashboard.jsx
│   │   │   └── GameLogAnalyzer.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── data/
    └── example_game_states/     ← Sample JSON states for testing
```

---

## 8. Quick Start Guide

### Prerequisites

- Python 3.12 — installed at `C:\Users\svenftw\AppData\Local\Programs\Python\Python312\`
- Node.js 20+ — needed for Phase 2+ web app (not yet required)
- An Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

> **Note**: Python was installed via `winget`. To use `python` without the full path,
> add `C:\Users\svenftw\AppData\Local\Programs\Python\Python312\` to your system PATH,
> or open a new terminal after installation (winget updates PATH on install but the
> current session needs to be refreshed).

### Run the CLI Coach (Phase 1) — Ready Now

**Step 1: Set up your API key**
```
# Create a .env file in the repo root:
copy .env.example .env
# Then edit .env and paste your ANTHROPIC_API_KEY
```

**Step 2: Run**
```
# From the repo root (using full Python path, or just 'python' in a new terminal):
C:\Users\svenftw\AppData\Local\Programs\Python\Python312\python.exe scripts\coach_cli.py ^
    --state data\example_game_states\age2_normal.json

# Evaluate a specific move:
python scripts\coach_cli.py ^
    --state data\example_game_states\age2_military_crisis.json ^
    --move "Draft Knights from the card row"

# Try the Age I scenario:
python scripts\coach_cli.py --state data\example_game_states\age1_mid.json
```

**Dependencies already installed**: `anthropic`, `pyyaml`, `python-dotenv`

### Run the Web App (Phase 2+)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Run with Docker Compose (future)

```yaml
# docker-compose.yml (to be created in Phase 3)
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
```

---

## 9. Resources & References

### Community Strategy Resources

| Resource | URL | Value |
|---|---|---|
| BGG Strategy Guide with Expansion | boardgamegeek.com/thread/2801950 | Core competitive guide, 3-4 player focus |
| BGG Civil Card Analysis (all cards rated) | boardgamegeek.com/thread/2294034 | 1–10 rating for every civil card |
| BGG Advanced Gameplay Reviews | boardgamegeek.com/thread/2509142 | Analysis from 2000+ online games |
| BGG Military for Dummies | boardgamegeek.com/thread/1605310 | Military system deep dive |
| Steam Strategy Guide (Blue/Veliq) | steamcommunity.com/sharedfiles/filedetails/?id=1367549747 | Accessible intro to tournament thinking |
| TtA Hyper Cheat Sheet | silverhammermba.github.io/throughtheages/ | Quick reference for all cards and values |
| Stately Play Strategy 101 | statelyplay.com/2017/09/25/strategy-101-through-the-ages-resource-edition/ | Resource-focused strategic primer |

### Official Platforms

| Platform | URL | Notes |
|---|---|---|
| CGE Official Site | throughtheages.com | Game rules, news |
| CGE Online Play | account.czechgames.com | Official async play |
| Board Game Arena | boardgamearena.com (search TtA) | Popular online platform; no API |
| Yucata.de | yucata.de | Best for game log export (JSON) |
| BGG Game Page | boardgamegeek.com/boardgame/182028 | Reviews, forums, expansions |
| BGG Expansion Page | boardgamegeek.com/boardgame/280833 | New Leaders & Wonders info |

### Technical References

| Reference | URL | Notes |
|---|---|---|
| Anthropic Claude API | docs.anthropic.com | API docs for coaching engine |
| FastAPI | fastapi.tiangolo.com | Backend framework docs |
| React + Vite | vitejs.dev | Frontend setup |
| Open-source TtA (JS) | github.com/jwlodek/Through-The-Ages | Reference implementation to study |
| Open-source TtA (alt) | github.com/KazeEmanuar/Through-The-Ages | Alternative implementation |
| Yucata Log Format | yucata.de (in-game export) | Documented JSON replay format |
| PCGamingWiki TtA Page | pcgamingwiki.com/wiki/Through_the_Ages | Save file locations, PC specifics |

### Competitive Play

| Resource | URL | Notes |
|---|---|---|
| BGA Tournaments | boardgamearena.com/tournament | Active tournament listings |
| Meeple League TtA Tournament | meepleleague.com/through-the-ages-online-tournament/ | Community tournament org |
| World Championship 2021 | boardgamegeek.com/thread/2751895 | 2-player championship discussions |

---

*Last updated: February 2026*
*Status: Phase 1 — Complete ✓ | Phase 2 — Not yet started*
