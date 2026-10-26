---
doc: spec
status: approved
---

# TeamSync AI — Technical Specification

## How This Works, In Plain Language
TeamSync AI is a lightweight Python web application that solves team task coordination.
1. The user opens the dashboard in their browser. They can click "⚡ Load Sample Hackathon Data" to instantly fill realistic team members and tasks, or type their own rows.
2. When the user clicks "Generate Balanced Schedule", the frontend sends the validated team and task data to a Python FastAPI backend endpoint (`/api/coordinate`).
3. The backend checks for an OpenRouter API key. If present and `MOCK_MODE=False`, it sends a strictly structured prompt to OpenRouter (`qwen/qwen-2.5-coder-32b-instruct:free` with fallback to `meta-llama/llama-3.3-70b-instruct:free`). If offline, or if the API key is absent, or if `MOCK_MODE=True`, an intelligent mock coordination engine generates the realistic schedule instantly.
4. The backend validates and parses the response into a structured JSON schema containing the **Workload Fairness Score (0–100%)**, a 2-sentence executive summary, and individual task assignments with 1-sentence explanations.
5. The frontend receives the JSON, triggers a smooth scroll to the results view, animates the fairness score badge from 0% to the target percentage, and renders the task cards with staggered kinetic fade-in transitions.

This architecture was chosen over bulky full-stack setups or rigid UI wrappers because FastAPI + Vanilla HTML/CSS/JS provides maximum animation freedom, zero build tools, rock-solid security, and starts with a single command: `python app.py`.

## The Core Journey Through the System
Implements [prd.md > The Core Journey](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L14-L24):
1. **User lands on `http://127.0.0.1:8000`**: FastAPI serves `static/index.html` with bundled `static/style.css` and `static/app.js`.
2. **User clicks "⚡ Load Sample Hackathon Data"**: `app.js` updates DOM input rows with 3 members and 5 tasks.
3. **User clicks "Generate Balanced Schedule"**: 
   - `app.js` runs client-side validation (ensures at least 1 member and 1 task). If empty, triggers an inline toast.
   - If valid, activates button loading spinner and sends a `POST` request to `/api/coordinate`.
4. **Backend Processing (`app.py` & `coordinator.py`)**:
   - Pydantic models validate and sanitize inputs (strips control characters, enforces field length bounds).
   - If `MOCK_MODE=True` or API key is not configured, returns deterministic, realistic hackathon assignments.
   - Otherwise, invokes OpenRouter API with `response_format: {"type": "json_object"}`. If JSON parsing fails, regex extractor recovers the payload; if the primary model errors, switches to fallback model.
5. **Results Rendering**:
   - `app.js` receives verified JSON response.
   - Smoothly scrolls to `#results-section`.
   - Triggers count-up keyframe animation for the Workload Fairness Score badge.
   - Injects sanitized task cards using safe DOM methods (`textContent` / escaped templates).
6. **Error / Retry**: If the server returns a 500 or network drops, `app.js` displays an inline alert banner with a "Retry Generation" button, preserving existing input values.

## Stack
- **Language**: Python 3.12+ ([Python Docs](https://docs.python.org/3/))
- **Backend Web Server**: FastAPI ([FastAPI Docs](https://fastapi.tiangolo.com/)) with Uvicorn ([Uvicorn Docs](https://www.uvicorn.org/))
  - *Rationale*: High performance, built-in Pydantic data validation, serves static assets effortlessly, zero configuration.
- **HTTP Client**: `httpx` ([HTTPX Docs](https://www.python-httpx.org/))
  - *Rationale*: Modern, synchronous/asynchronous HTTP client for clean OpenRouter API interaction.
- **Environment Management**: `python-dotenv` ([python-dotenv Docs](https://saurabh-kumar.com/python-dotenv/))
  - *Rationale*: Securely loads API credentials from `.env` without exposing them to source control.
- **Frontend**: Vanilla HTML5, Modern CSS3, and ES6 JavaScript (No npm/Node build step required)
  - *Rationale*: Total creative control over kinetic typography, CSS keyframe animations, smooth scrolling, and custom theme tokens.
- **AI Service**: OpenRouter API ([OpenRouter Docs](https://openrouter.ai/docs))
  - Primary Model: `qwen/qwen-2.5-coder-32b-instruct:free`
  - Fallback Model: `meta-llama/llama-3.3-70b-instruct:free`

## Where It Runs and How Someone Tries It
- **Runtime Environment**: Local machine running Python 3.10+ and any modern web browser (Chrome, Edge, Firefox, Safari).
- **Vercel Preview**: `vercel.json` routes requests to the FastAPI function and includes the `static/` assets in its bundle. The JSON file store uses Vercel's temporary directory so auth and dashboard actions can run in a preview; data is not durable across function cold starts or deployments. Use a hosted database before relying on persistent accounts or schedules.
- **Environment Variables**:
  - `OPENROUTER_API_KEY`: OpenRouter API Key (optional if using `MOCK_MODE=True`).
  - `MOCK_MODE`: `True` or `False` (defaults to `True` if no API key is detected, guaranteeing seamless demo recording).
- **Start Command**:
  ```bash
  python app.py
  ```
- **What to Open**: Navigate browser to `http://127.0.0.1:8000`.
- **Demo Recording Guide**:
  1. Open `http://127.0.0.1:8000`.
  2. Click **"⚡ Load Sample Hackathon Data"** (shows instant auto-fill).
  3. Click **"Generate Balanced Schedule"** (shows kinetic loading state).
  4. Showcase the animated **Workload Fairness Score (e.g. 92%)**, the executive summary, and the individual task cards with 1-sentence assignment rationales.

## Look and Feel
Implements [prd.md > Look and Feel](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L35-L48):
- **Design System Tokens (`static/style.css`)**:
  - `--color-base-ochre`: `#C86D51` (Raw Ochre / Terracotta)
  - `--color-base-ochre-dark`: `#8C4129`
  - `--color-neutral-slate`: `#181C22` (Weathered Slate Background)
  - `--color-neutral-card`: `#222831` (Charcoal Container Surface)
  - `--color-neutral-border`: `#343D4B` (Subtle Card Border)
  - `--color-accent-cyan`: `#00F0FF` (Industrial Cyan Pop Accent)
  - `--color-accent-lime`: `#A3E635` (Acid Lime Secondary Highlight)
  - `--color-text-main`: `#F3F4F6` (High-contrast primary typography)
  - `--color-text-muted`: `#9CA3AF` (Muted secondary typography)
- **Typography**: Clean, geometric sans-serif (`Inter` / system stack) with kinetic letter-spacing and weighted uppercase badges.
- **Kinetic Motion & Micro-interactions**:
  - `@keyframes countUp`: CSS/JS numerical transition for the fairness score badge.
  - `@keyframes cardFadeIn`: Staggered CSS animation (`animation-delay: calc(var(--index) * 80ms)`).
  - Smooth native scroll (`scroll-behavior: smooth`) when transitioning to results.
  - Button hover glow and subtle card lift on hover (`transform: translateY(-2px)`).

## Components

### 1. Web Server & Static Router (`app.py`)
Implements [prd.md > Screens and Layout](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L26-L34):
- Initializes FastAPI app and mounts `static/` directory.
- Exposes `GET /` returning `static/index.html`.
- Exposes `POST /api/coordinate` receiving validated payloads and returning task coordination results.
- Exposes `GET /api/health` returning system status and whether Mock Mode or Live API is active.

### 2. Task Coordinator Engine (`coordinator.py`)
Implements [prd.md > 3. AI-Driven Schedule & Fairness Generation](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L76-L84):
- Constructs prompt incorporating team members, skills, availability, and tasks.
- Calls OpenRouter API with timeout, retry, and model fallback logic.
- Sanitizes and parses LLM output into validated Pydantic schemas.
- Contains high-fidelity `mock_coordinate()` fallback function producing realistic fairness allocations when running offline.

### 3. Security Hardening Layer (`security.py`)
Implements [prd.md > 5. Security and Data Protection](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L91-L99):
- **API Access**: Protected dashboard requests re-check the user's username and password; users can only change their own dashboard, and only an existing team lead can generate a shared schedule. Credentials stay in browser memory and are not saved in local storage. Public sign-up creates candidate accounts only.
- **Input Sanitization**: Cleans strings against prompt injection attempts, strips non-printable control characters, and enforces strict length caps (e.g., max 60 chars per member name, max 120 chars per task title).
- **Bounds Checking**: Enforces max 10 team members and max 20 tasks per request to prevent Denial of Service and compute abuse.
- **Safe HTML Escaping**: Provides sanitization utilities ensuring no unescaped strings reach the DOM.
- **Error Shielding**: Catches internal exceptions, logs them safely on the backend, and returns generic user-friendly error codes to the client.

### 4. Interactive Frontend Dashboard (`static/index.html`, `static/style.css`, `static/app.js`)
Implements [prd.md > Screens and Layout](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L26-L34) and [prd.md > 4. Interactive Results & Rationale Display](file:///c:/Users/7420/Desktop/October26,%202026/devpost/prd.md#L85-L90):
- **Top Quick Bar**: "⚡ Load Sample Hackathon Data" button and Status Indicator (Live API / Mock Mode).
- **Dynamic Input Tables**: Add/delete row controls with clear placeholder guides.
- **Results View**: Animated Workload Fairness Score badge, 2-sentence executive summary, and staggered task cards with teammate avatars and rationales.
- **Notification Toast & Error Banner**: Inline messages for validation warnings and connection errors with retry actions.

## Data Model

### TeamMember Schema
```python
class TeamMember(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    skills: str = Field(..., min_length=1, max_length=150)
    hours: float = Field(..., ge=1.0, le=168.0)
```

### TaskItem Schema
```python
class TaskItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    required_skill: str = Field(..., min_length=1, max_length=80)
    estimated_hours: float = Field(..., ge=0.5, le=100.0)
```

### CoordinationRequest Schema
```python
class CoordinationRequest(BaseModel):
    members: list[TeamMember] = Field(..., min_items=1, max_items=10)
    tasks: list[TaskItem] = Field(..., min_items=1, max_items=20)
```

### AssignmentItem Schema
```python
class AssignmentItem(BaseModel):
    task_title: str
    assigned_to: str
    required_skill: str
    estimated_hours: float
    reasoning: str
```

### CoordinationResponse Schema
```python
class CoordinationResponse(BaseModel):
    fairness_score: int = Field(..., ge=0, le=100)
    executive_summary: str
    assignments: list[AssignmentItem]
    is_mock: bool = False
```

## File Structure
```
October26, 2026/
├── app.py                # FastAPI entry point, routes, server startup
├── coordinator.py        # OpenRouter API client, prompt logic, mock fallback
├── security.py           # Input sanitization, validation rules, XSS shielding
├── requirements.txt      # Python dependencies (fastapi, uvicorn, httpx, python-dotenv)
├── .env.example          # Sample environment template (OPENROUTER_API_KEY, MOCK_MODE)
├── .gitignore            # Git exclusion rules (protecting .env and learner profile)
├── static/
│   ├── index.html        # Single-page dashboard markup
│   ├── style.css         # Raw Ochre / Charcoal / Cyan palette & kinetic animations
│   └── app.js           # Client state, sample data loader, animations, API caller
└── devpost/              # Hackathon planning artifacts
    ├── learner-profile.md
    ├── scope.md
    ├── prd.md
    └── spec.md
```

## External Services and Dependencies
- **OpenRouter API**:
  - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
  - Auth Header: `Authorization: Bearer $OPENROUTER_API_KEY`
  - Payload: Standard Chat Completion payload with system instructions and JSON response format.
  - Documentation: [OpenRouter Documentation](https://openrouter.ai/docs)
  - Cost: Free tier (`:free` tagged models).

## Important Failure Modes
- **API Key Missing or Empty**: Automatically falls back to high-fidelity mock coordination engine with an informative UI badge; the demo never breaks.
- **OpenRouter Timeout / Rate Limit**: Retries once on secondary fallback model (`llama-3.3-70b-instruct:free`). If both fail, falls back gracefully to local coordinator with an inline notice.
- **Malformed LLM Output**: The regex JSON extractor retrieves the JSON dictionary even if the model prefixes/suffixes Markdown explanations.
- **Incomplete / Malformed Input**: Pydantic and frontend validation reject invalid inputs immediately with an inline toast without crashing the server.

## What Was Simplified and Why
- **FastAPI + Vanilla Frontend instead of React/Next.js**: Eliminates Node.js build pipelines, node_modules bloat, and deployment complexity, allowing the app to launch with a single `python app.py` command while delivering instant kinetic CSS animations.
- **In-Memory Session State instead of PostgreSQL/SQLite**: Coordination plans are ephemeral and shareable via screen demo; eliminating a database prevents schema migration risks and ensures the build is finished in 2–4 hours.
- **Deterministic Mock Mode instead of Hard API Failure**: Ensures that evaluating or recording the video demo never fails due to external API outages or rate limits.

## Decisions and Open Issues
- **Learner Decision**: Approved Option A (FastAPI + Vanilla HTML/CSS/JS) for complete aesthetic and kinetic motion freedom using Raw Ochre, Weathered Slate, and Industrial Cyan.
- **Learner Decision**: Added Mock Mode flag to guarantee zero-risk demo recording.
- **Learner Decision**: Security-first implementation with input sanitization, bounds checking, XSS escaping, and credential isolation.
- **Identified Uncertainty Clarified**: Addressed how free-tier LLMs sometimes wrap JSON in markdown by specifying a two-tier extraction pipeline (`response_format` + regex JSON boundary parser).
- **Open Issues**: None. All dependencies, schemas, and routes are fully mapped.
