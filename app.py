"""
TeamSync AI - FastAPI Application
Provides endpoints for health checking, task coordination, and serving the kinetic dashboard.
"""

import logging
import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from security import (
    CoordinationRequest,
    CoordinationResponse,
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthUserResponse,
)
from coordinator import coordinate_tasks, OPENROUTER_API_KEY, MOCK_MODE
from storage import (
    authenticate_user,
    register_user,
    get_user_data,
    update_user_dashboard,
    get_shared_team_schedule,
    save_shared_team_schedule,
)

load_dotenv()

logger = logging.getLogger("teamsync.app")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="TeamSync AI",
    description="AI-powered Team Task & Resource Coordinator with Role-based Dashboards",
    version="1.1.0",
)

basic_auth = HTTPBasic(auto_error=False)


def require_user(
    credentials: Optional[HTTPBasicCredentials] = Depends(basic_auth),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please sign in to access this account.",
            headers={"WWW-Authenticate": "Basic"},
        )

    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


# CORS: restrict to localhost / same origin for high security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", summary="Serve dashboard")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "TeamSync AI Backend Running."})


@app.get("/judge", summary="Serve Judge Scrollytelling Page")
def get_judge_page():
    judge_path = os.path.join(static_dir, "judge.html")
    if os.path.exists(judge_path):
        return FileResponse(judge_path)
    return FileResponse("static/judge.html")


@app.get("/api/health", summary="Health check and status")
async def health_check():
    is_mock = MOCK_MODE or not bool(OPENROUTER_API_KEY)
    return {
        "status": "online",
        "mock_mode": is_mock,
        "engine": "Offline Mock Engine" if is_mock else "OpenRouter Live API",
    }


@app.post("/api/auth/login", response_model=AuthUserResponse, summary="Role-based Login")
async def api_login(credentials: AuthLoginRequest):
    user = authenticate_user(credentials.username, credentials.password, credentials.role)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid username or password for role '{credentials.role}'. Check your credentials or sign up.",
        )

    # Attach shared team schedule if candidate
    if user["role"] == "candidate":
        shared_sched = get_shared_team_schedule()
        if shared_sched and "latest_schedule" not in user["dashboard_data"]:
            user["dashboard_data"]["shared_schedule"] = shared_sched

    return AuthUserResponse(
        success=True,
        username=user["username"],
        display_name=user["display_name"],
        role=user["role"],
        skills=user.get("skills", ""),
        hours=user.get("hours", 8.0),
        dashboard_data=user.get("dashboard_data", {}),
        message=f"Welcome back, {user['display_name']}!",
    )


@app.post("/api/auth/register", response_model=AuthUserResponse, summary="Register new Team Lead or Candidate")
async def api_register(req: AuthRegisterRequest):
    if req.role.lower() == "lead":
        raise HTTPException(
            status_code=403,
            detail="Team Lead accounts cannot be created through public sign-up.",
        )

    user = register_user(
        username=req.username,
        password=req.password,
        display_name=req.display_name,
        role=req.role,
        skills=req.skills,
        hours=req.hours,
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{req.username}' is already registered. Please choose another username.",
        )

    return AuthUserResponse(
        success=True,
        username=user["username"],
        display_name=user["display_name"],
        role=user["role"],
        skills=user.get("skills", ""),
        hours=user.get("hours", 8.0),
        dashboard_data=user.get("dashboard_data", {}),
        message=f"Account created successfully for {user['display_name']} ({user['role'].capitalize()})!",
    )


@app.get("/api/user/{username}/dashboard", summary="Fetch isolated dashboard data")
async def get_dashboard(username: str, current_user: dict = Depends(require_user)):
    if username.strip().lower() != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only access your own dashboard.")

    user = get_user_data(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Enrich with shared team schedule if available
    shared_sched = get_shared_team_schedule()
    user["dashboard_data"]["shared_schedule"] = shared_sched
    return user


@app.post("/api/user/{username}/dashboard", summary="Persist user-specific dashboard state")
async def save_dashboard(
    username: str,
    data: dict,
    current_user: dict = Depends(require_user),
):
    if username.strip().lower() != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only update your own dashboard.")

    success = update_user_dashboard(username, data)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"success": True, "message": "Dashboard state saved."}


@app.post("/api/coordinate", response_model=CoordinationResponse, summary="Coordinate team tasks")
async def coordinate(
    request: CoordinationRequest,
    current_user: dict = Depends(require_user),
):
    if current_user["role"] != "lead":
        raise HTTPException(status_code=403, detail="Only team leads can generate a shared schedule.")

    try:
        if len(request.members) == 0 or len(request.tasks) == 0:
            raise HTTPException(status_code=400, detail="At least 1 team member and 1 task are required.")
        
        result = await coordinate_tasks(request)
        
        # Persist generated schedule to shared team store so candidates immediately see their assignments!
        save_shared_team_schedule(result.dict())
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during coordination: {e}", exc_info=True)
        # Security: Mask internal stack trace and return safe message
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the schedule. Please check your inputs or retry.",
        )


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"[*] TeamSync AI starting at http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=False)
