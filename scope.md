---
doc: scope
status: approved
---

# TeamSync AI (Team Task & Resource Coordinator)

An AI-driven coordination tool that takes team members and tasks, balances workloads, and generates a fair task assignment schedule with transparent reasoning.

## The Unique Kernel
The **"Fairness Score & Assignment Reasoning"** engine. Rather than outputting an opaque to-do list, TeamSync evaluates workload distribution across members, computes a prominent **Workload Fairness Score (0–100%)**, and provides explicit 1-sentence rationales explaining why each assignment was made based on skills, hours, and deadlines.

## Who It's For
A **hackathon team captain or student group lead** managing 3–6 teammates under tight deadlines. 
- **Today's pain**: Using chaotic WhatsApp chats or ad-hoc Google Sheets where tasks are assigned arbitrarily, causing unequal workloads, resentment, missed deadlines, and misaligned skill assignments.
- **With TeamSync**: They input their team's skills and availability once, hit a button, and get a balanced, justifiable action plan in seconds.

## The Core Loop
1. **Input / Pre-fill**: The user adds team members (name, skills, available hours) and tasks (title, required skill, effort/deadline), or clicks "Load Sample Hackathon Data".
2. **Analyze & Optimize**: The user clicks "Generate Balanced Schedule", sending the structured data to an AI model via OpenRouter API.
3. **Review & Justify**: The user inspects the color-coded task assignments, checks the Workload Fairness Score, and reviews the bottleneck/trade-off summary to share with their team.

## Inspiration & Identity
- **Vibe**: Creative, strategic, responsive, and intelligent.
- **Aesthetic**: Polished modern interface featuring constant typography, kinetic motion, sleek CSS card transitions, smooth scroll animations, and micro-interactions.
- **Visual Polish (Crucial for Demo)**:
  - Smooth scroll transitions between dashboard sections.
  - Staggered fade-in animations for task assignment cards.
  - Dynamic count-up animation for the Workload Fairness Score percentage badge.
- **Tone**: Objective, constructive project coach.

## Why This Matters to the Learner
To practice a disciplined plan-first methodology that keeps an AI agent project strictly scoped to a 2–4 hour build, delivering an end-to-end working proof of concept with Python and Gradio.

## What "Working" Looks Like
A crisp 60-second screen recording demo:
1. User opens the web app and clicks **"Load Sample Hackathon Data"** (auto-populating 3 teammates with distinct skills and 5 project tasks).
2. User clicks **"Generate Balanced Schedule"**.
3. Within 5–8 seconds, an animated results view displays:
   - A color-coded table/card layout showing which team member owns which task.
   - A highlighted **Workload Fairness Score (e.g. 92%)** badge.
   - Clear 1-sentence reasoning per task and a short bottleneck summary note.

## The POC Boundary (Now)
- **Inputs**: Simple form/table inputs for team members (name, skills, hours) and tasks (name, skill tag, estimated effort).
- **One-Click Demo Button**: "Load Sample Hackathon Data" for instant testing without manual typing.
- **AI Backend**: Python pipeline using OpenRouter API (`qwen/qwen-2.5-coder-32b-instruct:free` or fallback) with strict structured JSON output parsing.
- **Scoring & Reasoning**: AI-evaluated fairness score (0–100%) and per-task justification.
- **Frontend**: Responsive Gradio web UI with styled cards, status badges, and smooth state updates.

## Later
- Drag-and-drop manual re-assignment with live AI fairness recalculation.
- Calendar integration (Google Calendar / iCal export).
- Multi-project persistent history with cloud database.
- Direct Slack / Discord webhook notifications.

## Explicitly Cut
- **User accounts & authentication**: Unnecessary friction for a 2–4 hour PoC; local in-memory session is sufficient.
- **Persistent database setup**: Replaced by in-memory state and sample presets to keep the architecture lightweight and reliable.
- **Real-time multi-user sockets**: Adds significant complexity with no extra value for the single-coordinator demo flow.
