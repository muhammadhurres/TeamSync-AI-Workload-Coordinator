"""
User account storage and persistent dashboard isolation for TeamSync AI.
Safely manages credentials, role-based profiles (Team Lead vs Candidate),
and separate dashboard state per user.
"""

import hashlib
import hmac
import json
import os
import tempfile
from typing import Dict, Any, Optional

DATA_DIR = (
    os.path.join(tempfile.gettempdir(), "teamsync-data")
    if os.getenv("VERCEL")
    else os.path.join(os.path.dirname(__file__), "data")
)
STORAGE_FILE = os.path.join(DATA_DIR, "user_store.json")
SALT = "teamsync_security_salt_2026"


def hash_password(password: str) -> str:
    """Hash password securely using SHA-256 and salt."""
    return hashlib.sha256((password + SALT).encode("utf-8")).hexdigest()


DEFAULT_USERS = {
    "lead": {
        "username": "lead",
        "password_hash": hash_password("lead123"),
        "display_name": "Elena (Team Lead)",
        "role": "lead",
        "skills": "Project Management, System Design, Hackathon Strategy",
        "hours": 20.0,
        "dashboard_data": {
            "members": [
                {"name": "Alex Chen", "skills": "Frontend, React, UI/UX, CSS", "hours": 12.0},
                {"name": "Samira Patel", "skills": "Backend, Python, FastAPI, API", "hours": 10.0},
                {"name": "Ali", "skills": "Python, Backend, Architecture", "hours": 8.0},
                {"name": "Taylor Reed", "skills": "Data Science, PyTorch, Pitch Deck", "hours": 8.0}
            ],
            "tasks": [
                {"title": "Design responsive dashboard layout", "required_skill": "UI/UX", "hours": 3.0},
                {"title": "Implement kinetic CSS animations and cards", "required_skill": "Frontend", "hours": 4.0},
                {"title": "Build FastAPI coordination endpoint", "required_skill": "Backend", "hours": 4.0},
                {"title": "Develop automated coordinator tests", "required_skill": "Python", "hours": 3.0},
                {"title": "Prepare demo pitch presentation", "required_skill": "Pitch Deck", "hours": 2.0}
            ],
            "latest_schedule": None
        }
    },
    "ali": {
        "username": "ali",
        "password_hash": hash_password("team123"),
        "display_name": "Ali",
        "role": "candidate",
        "skills": "Python, Backend, Architecture, Security",
        "hours": 8.0,
        "dashboard_data": {
            "bio": "Full-stack Python developer specializing in secure API backends and automation.",
            "status": "Available for Hackathon Sprints",
            "personal_notes": "Focused on backend optimization and security architecture."
        }
    },
    "alex": {
        "username": "alex",
        "password_hash": hash_password("team123"),
        "display_name": "Alex Chen",
        "role": "candidate",
        "skills": "Frontend, React, UI/UX, CSS Animations",
        "hours": 12.0,
        "dashboard_data": {
            "bio": "Passionate UI/UX engineer building kinetic interfaces and high-contrast designs.",
            "status": "Ready for UI tasks",
            "personal_notes": "Delivering responsive cards and smooth transitions."
        }
    }
}


def load_store() -> Dict[str, Any]:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STORAGE_FILE):
        save_store(DEFAULT_USERS)
        return DEFAULT_USERS.copy()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_USERS.copy()


def save_store(data: Dict[str, Any]) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def authenticate_user(username: str, password: str, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
    store = load_store()
    u = username.strip().lower().replace(" ", "_")
    if u not in store:
        return None
    
    user = store[u]
    if not hmac.compare_digest(user["password_hash"], hash_password(password)):
        return None

    if role and user["role"] != role.lower():
        # Role mismatch
        return None

    # Return clean user copy without password_hash
    clean_user = user.copy()
    clean_user.pop("password_hash", None)
    return clean_user


def register_user(username: str, password: str, display_name: str, role: str, skills: str = "", hours: float = 8.0) -> Optional[Dict[str, Any]]:
    store = load_store()
    u = username.strip().lower()
    if u in store:
        return None  # Username already taken

    clean_role = "lead" if role.lower() == "lead" else "candidate"
    
    initial_dashboard = {}
    if clean_role == "lead":
        initial_dashboard = {
            "members": [
                {"name": "Team Member 1", "skills": "Frontend, UI", "hours": 10.0},
                {"name": "Team Member 2", "skills": "Backend, API", "hours": 10.0}
            ],
            "tasks": [
                {"title": "Initial Setup Deliverable", "required_skill": "Frontend", "hours": 4.0}
            ],
            "latest_schedule": None
        }
    else:
        initial_dashboard = {
            "bio": f"Registered candidate specializing in {skills or 'General Software Engineering'}.",
            "status": "Ready for Project Tasks",
            "personal_notes": "Awaiting coordinator task allocation."
        }

    new_user = {
        "username": u,
        "password_hash": hash_password(password),
        "display_name": display_name.strip() or u.capitalize(),
        "role": clean_role,
        "skills": skills.strip() or ("Project Coordination" if clean_role == "lead" else "General Development"),
        "hours": float(hours),
        "dashboard_data": initial_dashboard
    }

    store[u] = new_user
    save_store(store)

    clean_user = new_user.copy()
    clean_user.pop("password_hash", None)
    return clean_user


def get_user_data(username: str) -> Optional[Dict[str, Any]]:
    store = load_store()
    u = username.strip().lower()
    if u in store:
        user = store[u].copy()
        user.pop("password_hash", None)
        return user
    return None


def update_user_dashboard(username: str, dashboard_data: Dict[str, Any]) -> bool:
    store = load_store()
    u = username.strip().lower()
    if u in store:
        store[u]["dashboard_data"] = dashboard_data
        save_store(store)
        return True
    return False


def get_shared_team_schedule() -> Optional[Dict[str, Any]]:
    """Returns the latest schedule generated by the team lead for team-wide candidate visibility."""
    store = load_store()
    lead_user = store.get("lead")
    if lead_user and "dashboard_data" in lead_user:
        return lead_user["dashboard_data"].get("latest_schedule")
    return None


def save_shared_team_schedule(schedule: Dict[str, Any]) -> None:
    store = load_store()
    if "lead" in store:
        if "dashboard_data" not in store["lead"]:
            store["lead"]["dashboard_data"] = {}
        store["lead"]["dashboard_data"]["latest_schedule"] = schedule
        save_store(store)
