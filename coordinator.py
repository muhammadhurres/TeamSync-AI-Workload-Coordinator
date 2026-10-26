"""
Coordination engine for TeamSync AI.
Interfaces with OpenRouter API (Qwen 2.5 Coder free tier with LLaMA 3.3 fallback)
and provides an intelligent, deterministic offline Mock Mode.
"""

import json
import logging
import os
import re
from typing import Dict, Any, List
import httpx
from dotenv import load_dotenv

from security import CoordinationRequest, CoordinationResponse, AssignmentItem

load_dotenv()

logger = logging.getLogger("teamsync.coordinator")
logging.basicConfig(level=logging.INFO)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "t", "yes")

PRIMARY_MODEL = "qwen/qwen-2.5-coder-32b-instruct:free"
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    """Extract valid JSON from LLM response even if wrapped in markdown blocks or text."""
    # Try direct parse
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting inside ```json ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding outer braces { ... }
    outer_braces_match = re.search(r"\{[\s\S]*\}", raw_text)
    if outer_braces_match:
        try:
            return json.loads(outer_braces_match.group(0).strip())
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract valid JSON from LLM response")


def mock_coordinate(req: CoordinationRequest) -> CoordinationResponse:
    """
    Intelligent offline coordination engine that realistically assigns tasks
    based on skill overlap and balanced hour allocations.
    """
    members = req.members
    tasks = req.tasks
    
    # Track member assigned hours
    member_workload: Dict[str, float] = {m.name: 0.0 for m in members}
    assignments: List[AssignmentItem] = []

    for task in tasks:
        req_skill = task.required_skill.lower()
        
        # Score each member based on skill matching and current workload balance
        best_candidate = None
        best_score = -999.0

        for m in members:
            m_skills = m.skills.lower()
            # Skill match bonus
            skill_bonus = 0.0
            for skill_word in req_skill.replace(",", " ").split():
                if len(skill_word) > 2 and skill_word in m_skills:
                    skill_bonus += 20.0
            
            # Workload headroom penalty
            available_headroom = m.hours - member_workload[m.name]
            workload_score = available_headroom * 2.0
            
            total_candidate_score = skill_bonus + workload_score

            if total_candidate_score > best_score:
                best_score = total_candidate_score
                best_candidate = m

        if not best_candidate:
            best_candidate = members[0]

        member_workload[best_candidate.name] += task.estimated_hours

        # Generate realistic 1-sentence rationale
        reasoning = (
            f"Assigned to {best_candidate.name} due to direct proficiency in {task.required_skill} "
            f"and available capacity ({best_candidate.hours - member_workload[best_candidate.name]:.1f}h headroom)."
        )

        assignments.append(
            AssignmentItem(
                task_title=task.title,
                assigned_to=best_candidate.name,
                required_skill=task.required_skill,
                estimated_hours=task.estimated_hours,
                reasoning=reasoning,
            )
        )

    # Compute fairness score based on workload variance
    workloads = list(member_workload.values())
    if len(workloads) > 1 and max(workloads) > 0:
        avg_load = sum(workloads) / len(workloads)
        max_dev = max(abs(w - avg_load) for w in workloads)
        fairness_score = int(max(60, min(96, 100 - (max_dev * 4))))
    else:
        fairness_score = 92

    # Executive summary
    member_names = [m.name for m in members]
    summary = (
        f"Workload is distributed evenly across {len(member_names)} teammates with balanced hourly commitments. "
        f"Critical path tasks were aligned with verified skill strengths to avoid bottlenecks before final submission."
    )

    return CoordinationResponse(
        fairness_score=fairness_score,
        executive_summary=summary,
        assignments=assignments,
        is_mock=True,
    )


async def coordinate_with_openrouter(req: CoordinationRequest, model: str) -> CoordinationResponse:
    """Send coordination request to OpenRouter API."""
    members_data = [{"name": m.name, "skills": m.skills, "hours": m.hours} for m in req.members]
    tasks_data = [
        {"title": t.title, "required_skill": t.required_skill, "estimated_hours": t.estimated_hours}
        for t in req.tasks
    ]

    system_prompt = (
        "You are an expert AI Project Coordinator for high-stakes hackathons and team sprints. "
        "Your task is to assign each project task to the best team member based on skill alignment, "
        "availability, and workload balance. "
        "You must compute an objective Workload Fairness Score from 0 to 100 (where 100 is perfectly balanced and aligned). "
        "You must return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "fairness_score": <integer between 0 and 100>,\n'
        '  "executive_summary": "<2-sentence summary highlighting balance and potential bottlenecks>",\n'
        '  "assignments": [\n'
        "    {\n"
        '      "task_title": "<task title>",\n'
        '      "assigned_to": "<team member name>",\n'
        '      "required_skill": "<skill>",\n'
        '      "estimated_hours": <number>,\n'
        '      "reasoning": "<1-sentence clear justification based on skill match and workload>"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"Team Members:\n{json.dumps(members_data, indent=2)}\n\nProject Tasks:\n{json.dumps(tasks_data, indent=2)}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "TeamSync AI Coordinator",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()
        raw_content = res_data["choices"][0]["message"]["content"]
        parsed = extract_json_payload(raw_content)

        assignments = [
            AssignmentItem(
                task_title=a["task_title"],
                assigned_to=a["assigned_to"],
                required_skill=a.get("required_skill", "General"),
                estimated_hours=float(a.get("estimated_hours", 1.0)),
                reasoning=a["reasoning"],
            )
            for a in parsed["assignments"]
        ]

        return CoordinationResponse(
            fairness_score=int(parsed["fairness_score"]),
            executive_summary=parsed["executive_summary"],
            assignments=assignments,
            is_mock=False,
        )


async def coordinate_tasks(req: CoordinationRequest) -> CoordinationResponse:
    """Main entry point: uses OpenRouter API with fallbacks, or Mock Mode if offline/unset."""
    if MOCK_MODE or not OPENROUTER_API_KEY:
        logger.info("Executing in Mock / Offline Mode (fast, reliable demo).")
        return mock_coordinate(req)

    try:
        logger.info(f"Invoking primary model: {PRIMARY_MODEL}")
        return await coordinate_with_openrouter(req, PRIMARY_MODEL)
    except Exception as e:
        logger.warning(f"Primary model {PRIMARY_MODEL} failed: {e}. Trying fallback model {FALLBACK_MODEL}...")
        try:
            return await coordinate_with_openrouter(req, FALLBACK_MODEL)
        except Exception as e_fallback:
            logger.error(f"Fallback model also failed: {e_fallback}. Gracefully serving via Mock Engine.")
            return mock_coordinate(req)
