---
doc: prd
status: approved
---

# TeamSync AI — Product Requirements Document

An AI-driven coordination dashboard for hackathon captains and student group leads to distribute project tasks fairly, visualize workload balance, and understand assignment rationales.

**Source Reference**: [scope.md > The Unique Kernel](file:///c:/Users/7420/Desktop/October26,%202026/devpost/scope.md#L10-L12), [scope.md > The Core Loop](file:///c:/Users/7420/Desktop/October26,%202026/devpost/scope.md#L18-L23), [scope.md > The POC Boundary](file:///c:/Users/7420/Desktop/October26,%202026/devpost/scope.md#L45-L51).

## The Core Journey
1. **Arrival**: The team lead opens the TeamSync AI dashboard. They see an inviting single-page interface with a prominent top action bar and clean input tables for team members and tasks.
2. **Input / Pre-fill**:
   - The user can click **"⚡ Load Sample Hackathon Data"** to instantly pre-fill 3 team members (with varied skills and availability) and 5 distinct tasks.
   - Alternatively, the user can manually add, edit, or remove rows in the Team Members table (Name, Skills, Available Hours) and Tasks table (Task Title, Required Skill, Estimated Hours).
3. **Generation**: The user clicks the primary action button **"Generate Balanced Schedule"**.
   - If inputs are incomplete, an inline warning toast appears: *"Please add at least 1 team member and 1 task before generating."*
   - During generation, the button shows an active loading indicator while preserving all inputs.
4. **Inspection & Results**:
   - The page smoothly scrolls down to the Results section with staggered kinetic animations.
   - The **Summary Banner** displays a prominent **Workload Fairness Score badge** (animating with a count-up effect from 0% to the computed score, e.g. 92%) and a 2-sentence executive overview of workload distribution and bottlenecks.
   - **Task Cards** fade in with distinct color-coded member avatars, required skill tags, estimated hours, and a clear 1-sentence assignment explanation.
5. **Iteration / Retry**: The user can modify inputs at the top and re-generate anytime. If an API call fails or times out, an inline alert banner displays a friendly error and a **"Retry Generation"** button without clearing user inputs.

## Screens and Layout
A **single unified scrollable dashboard** divided into three clean, reactive sections:

1. **Header & Quick Actions**:
   - Title: **TeamSync AI** with subtitle: *"AI-Powered Team Task & Resource Coordinator"*.
   - Prominent Quick Action Button: `[⚡ Load Sample Hackathon Data]`.
2. **Input Configuration Section (Side-by-side or stacked responsive cards)**:
   - **Team Members Panel**: Row-based table/cards containing inputs for `Name`, `Skills` (comma-separated or tags), and `Available Hours`, with an `[+ Add Member]` button and delete icon per row.
   - **Tasks Panel**: Row-based table/cards containing inputs for `Task Title`, `Required Skill`, and `Estimated Hours`, with an `[+ Add Task]` button and delete icon per row.
   - **Generate Bar**: High-contrast primary action button `[Generate Balanced Schedule]`.
3. **Results & Insights Section (Rendered below on generation)**:
   - **Executive Summary Banner**:
     - Large animated **Workload Fairness Score Badge** (0–100%).
     - 2-sentence balance and bottleneck explanation.
   - **Assignment Grid**: Responsive grid of individual task cards showing task title, assigned person, skill match tag, effort, and AI rationale.

## Look and Feel
- **Visual Direction**: Organic-industrial high-contrast palette with kinetic typography and smooth scroll transitions.
- **Color Palette**:
  - **Primary Base**: *Raw Ochre / Terracotta* (`#C86D51` / `#B85D3B`) — used for structural elements, headers, and primary card accents.
  - **Grounding Neutral**: *Weathered Slate / Charcoal* (`#1E232A` / `#2B323B`) — used for dark container backgrounds, card borders, and structural backing.
  - **Synthetic Pop Accent**: *Industrial Cyan / Acid Lime* (`#00F0FF` / `#A3E635`) — reserved for key action buttons, hover states, the animated Workload Fairness Score badge, and critical highlights.
- **Motion & Micro-interactions**:
  - Kinetic scroll reveal when navigating between input and results.
  - Animated count-up effect on the Fairness Score percentage badge upon load.
  - Staggered CSS fade-in and subtle lift on task assignment cards.

## Features and Behavior

### 1. Sample Data Pre-fill
- As a hackathon lead preparing a 60-second video demo, I want to load realistic sample data with one click so that I don't have to type data manually on camera.
  - [ ] Clicking "⚡ Load Sample Hackathon Data" fills 3 team members:
    - *Alex* (Frontend, React, UI/UX — 12 hrs)
    - *Sam* (Backend, Python, API — 10 hrs)
    - *Taylor* (Data Science, ML, Pitch — 8 hrs)
  - [ ] Fills 5 project tasks:
    - *Build Landing Page* (Frontend, 4 hrs)
    - *Design Interactive UI Mockup* (UI/UX, 3 hrs)
    - *Build REST API Endpoints* (Backend, 5 hrs)
    - *Integrate AI Model API* (Python, 4 hrs)
    - *Prepare Pitch Slide Deck & Demo* (Pitch, 3 hrs)
  - [ ] Preserves row controls so loaded sample items can be edited or deleted.

### 2. Custom Input Management
- As a team lead with a custom team, I want to add or remove members and tasks easily so that the plan reflects my actual team.
  - [ ] Each member row has editable fields: Name, Skills, Hours.
  - [ ] Each task row has editable fields: Task Title, Required Skill, Estimated Hours.
  - [ ] Clicking "[+ Add Member]" or "[+ Add Task]" appends a new blank row.
  - [ ] Clicking the trash/delete icon removes that specific row.

### 3. AI-Driven Schedule & Fairness Generation
- As a team lead, I want an AI engine to analyze skill overlap, availability, and task effort so that tasks are distributed without overloading anyone.
  - [ ] Form submission packages members and tasks into structured payload.
  - [ ] Calls OpenRouter API (`qwen/qwen-2.5-coder-32b-instruct:free`).
  - [ ] Returns valid structured data containing:
    - `fairness_score`: Integer (0–100).
    - `executive_summary`: 2 sentences summarizing workload balance and trade-offs.
    - `assignments`: List of objects, each with `task_title`, `assigned_to`, `required_skill`, `estimated_hours`, and `reasoning`.

### 4. Interactive Results & Rationale Display
- As a team lead, I want to see why each assignment was made and how fair the workload is so I can explain the decisions to my teammates.
  - [ ] Displays the Workload Fairness Score prominently in a glowing accent badge with an animated count-up.
  - [ ] Displays the 2-sentence summary.
  - [ ] Renders each task card with member avatar, title, skill, hours, and 1-sentence assignment rationale.

### 5. Security and Data Protection
- As a security-conscious developer and user, I want the application to handle credentials and user data securely from day one so that secrets are never leaked and inputs are safe.
  - [ ] **Credential Isolation**: OpenRouter API keys are strictly read from local environment variables / `.env` files; never hardcoded, logged, or exposed to the client.
  - [ ] **Input Sanitization**: User inputs (names, skills, tasks) are stripped of control characters and validated against length bounds before being injected into the AI prompt template to mitigate prompt injection.
  - [ ] **XSS Prevention in UI**: All dynamic strings rendered in custom HTML/CSS cards are properly escaped so arbitrary HTML/scripts cannot be injected via task titles or member names.
  - [ ] **Safe Error Masking**: Client-facing error toasts and alert banners display human-friendly explanations without leaking backend stack traces, system paths, or raw API tokens.
  - [ ] **Git Protection**: `.gitignore` strictly protects `.env`, `.env.*` and personal learning context files from ever entering git commits.

## States and Boundaries
- **First Use (Empty State)**: Input tables show 1 empty row each or helpful placeholder hints with the "⚡ Load Sample Hackathon Data" button prominently featured.
- **Validation State (Incomplete Inputs)**: If user clicks "Generate" with fewer than 1 member or 1 task, an inline warning toast appears; no API call is made.
- **Loading State**: Button displays a spinner with text *"Analyzing skills and balancing workloads..."*; input fields remain locked or disabled during generation to prevent double submissions.
- **Success State**: Smooth transition to the results section, animated count-up of fairness score badge, and staggered fade-in of assignment cards.
- **Error State (API Timeout / Failure)**: An inline banner appears with a clear error explanation and a **"Retry Generation"** button; existing input values are strictly preserved.
- **Persistence Boundary**: In-memory session state only. Refreshing resets to default empty state (or sample data can be re-loaded instantly).

## Product Decisions
- **Single Page over Multi-step Wizard**: Kept on a single scrollable page so the entire workflow is viewable and operable within a 60-second video demo.
- **Pre-fill Button Placement**: Placed at the top level to guarantee effortless one-click presentation for hackathon evaluators.
- **Raw Ochre / Charcoal / Industrial Cyan Palette**: Selected by user for a distinctive high-contrast aesthetic that avoids generic AI template styling.
- **In-Memory Session vs. Database**: Omitted database storage to keep build time strictly within 2–4 hours while maximizing frontend kinetic polish.

## What We're Building (POC Boundary)
1. Single-page responsive web dashboard in Python/Gradio with custom CSS for Raw Ochre/Charcoal/Industrial Cyan styling and kinetic animations.
2. "⚡ Load Sample Hackathon Data" instant pre-fill button.
3. Dynamic row-based team and task input tables with add/delete capability.
4. OpenRouter API integration returning structured JSON (fairness score, executive summary, assignments, reasoning).
5. Animated Workload Fairness Score badge (0–100% count-up) and 2-sentence summary.
6. Task cards displaying assigned teammate, skill match, hours, and 1-sentence reasoning.
7. Inline validation toast and API error alert with retry button.
8. Comprehensive security hardening: environment-isolated API secrets, input sanitization against prompt injection, HTML escaping against XSS, and error stack masking.

## Deferred From the POC
- **User Accounts & Login**: Unnecessary for a 60-second PoC demo.
- **Multi-project History Storage**: Local session is sufficient for the hackathon.
- **Drag-and-Drop Task Re-assignment**: High implementation cost; deferred to v2.
- **Calendar & Slack Webhooks**: Deferred to post-hackathon extensions.

## Non-Goals
- Real-time multi-user collaborative editing.
- Automatic time-tracking or Gantt chart day-by-day scheduling.
- Direct integration with third-party project management APIs (Jira, Trello, Asana).

## Open Questions
- None blocking `4-spec`: All functional requirements, layout, behaviors, and visual palette have been resolved.
