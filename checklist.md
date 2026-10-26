---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [x] **1. Project scaffold, security layer, and interactive dashboard with sample loader**
  Becomes usable: A running FastAPI web application serving the single-page dashboard in the Raw Ochre / Weathered Slate / Industrial Cyan theme. The user can add/remove team members and tasks, or click "⚡ Load Sample Hackathon Data" to instantly populate the inputs.
  Why now: Bootstraps the project, sets up dependencies and security bounds, and establishes the complete UI surface so the AI coordination engine has real, structured inputs to work with.
  PRD ref: `prd.md > Screens and Layout`, `prd.md > 1. Sample Data Pre-fill`, `prd.md > 2. Custom Input Management`, `prd.md > 5. Security and Data Protection`
  Spec ref: `spec.md > Components > 1. Web Server & Static Router`, `spec.md > Components > 3. Security Hardening Layer`, `spec.md > File Structure`, `spec.md > Look and Feel`
  Build: Create `requirements.txt`, `.env.example`, `security.py`, `app.py`, `static/index.html`, `static/style.css`, and `static/app.js` with table input controls and sample hackathon pre-fill data.
  Verify (mechanical): Run Python syntax checks on `app.py` and `security.py`; start the server briefly to verify `GET /` and `GET /api/health` return 200 OK.
  Learner check: Open `http://127.0.0.1:8000`, click "⚡ Load Sample Hackathon Data", and verify 3 teammates and 5 tasks populate with row add/remove controls.
  Commit: `Scaffold dashboard, security bounds, and sample data loader`

- [x] **2. Coordination engine with OpenRouter API integration and offline Mock Mode**
  Becomes usable: Clicking "Generate Balanced Schedule" sends data to `/api/coordinate`, which analyzes skill sets and workloads using OpenRouter (`qwen/qwen-2.5-coder-32b-instruct:free` with `llama-3.3-70b` fallback) or high-fidelity offline mock mode, returning structured task assignments with reasoning and fairness score.
  Why now: Delivers the unique kernel—the core reasoning and fairness evaluation engine—so that the application produces intelligent coordination plans.
  PRD ref: `prd.md > 3. AI-Driven Schedule & Fairness Generation`, `prd.md > The Unique Kernel`
  Spec ref: `spec.md > Components > 2. Task Coordinator Engine`, `spec.md > Data Model`, `spec.md > External Services and Dependencies`
  Build: Implement `coordinator.py` with structured prompt engineering, JSON regex extraction fallback, OpenRouter HTTP client, and realistic offline mock generator; wire to `POST /api/coordinate` in `app.py`.
  Verify (mechanical): Execute automated test query against `/api/coordinate` and confirm returned JSON strictly matches `CoordinationResponse` schema with fairness score and per-task rationales.
  Learner check: Click "Generate Balanced Schedule" and verify the backend logs successful coordination and returns JSON assignments.
  Commit: `Implement coordination engine with OpenRouter API and mock fallback`

- [x] **3. Kinetic UI polish, animated fairness count-up badge, and error retry flows**
  Becomes usable: The full end-to-end user journey with animations: smooth scroll to the results view, count-up animation for the Workload Fairness Score badge, staggered fade-in task cards with teammate color badges and 1-sentence reasoning, plus inline validation toasts and API error retry banners.
  Why now: Brings the complete visual and kinetic vision to life, ensuring the 60-second video demo is striking and resilient against empty inputs or API timeouts.
  PRD ref: `prd.md > Look and Feel`, `prd.md > 4. Interactive Results & Rationale Display`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Look and Feel`, `spec.md > Important Failure Modes`
  Build: Update `static/style.css` and `static/app.js` with CSS keyframe transitions, count-up badge script, staggered card animations, inline validation toast, and error banner with retry.
  Verify (mechanical): Verify CSS keyframes, trigger validation with empty inputs to test toast, and run a mock coordination to confirm result cards render with valid DOM elements and count-up animation.
  Learner check: Load sample data, click "Generate Balanced Schedule", observe the smooth scroll, watch the score count up, and inspect the staggered task cards.
  Commit: `Add kinetic score animation, card transitions, and error retry UI`

## Hands-on Checkpoints

- [x] Early usable behavior explored — Slice 1 dashboard with sample loader and row controls
- [x] Final kick-the-tires exploration and feedback completed

## Final Review

- [x] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [x] Learning activity complete — focused recap connecting plan-first scoping to the verified working outcome
- [x] Optional edit and transfer reflection addressed — zero-risk mock engine pattern identified
- [x] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: Focused alternative connecting user's goal (strict plan-first scoping within 2-4 hours) to implementation and verification in `app.py`, `coordinator.py`, and `static/app.js`.
Route and stops: `static/app.js:handleCoordinate` -> `app.py:coordinate` -> `coordinator.py:coordinate_tasks` -> `static/app.js:renderAssignments`.
Edit outcome: Verified live in browser at `http://127.0.0.1:8000`.
Reflection: Addressed through the dual-mode resilience pattern (OpenRouter API with offline mock fallback).
Activity mode: Live app verified in browser and static SVG app-map generated.

## Revisions
