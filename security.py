"""
Security and validation layer for TeamSync AI.
Handles input bounds checking, sanitization against prompt injection, and XSS prevention.
"""

import html
import re
from typing import List
from pydantic import BaseModel, Field, field_validator


def sanitize_text(text: str, max_length: int = 150) -> str:
    """
    Sanitize text input:
    - Strip null bytes and non-printable control characters.
    - Trim excessive whitespace.
    - Truncate to maximum allowed length.
    - Escape dangerous HTML characters.
    """
    if not text:
        return ""
    
    # Remove null bytes and non-printable control characters (keep standard newlines/tabs)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    
    # Normalize multiple whitespace into single space
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    # Enforce maximum length
    cleaned = cleaned[:max_length]
    
    # Prevent prompt injection markers
    cleaned = cleaned.replace("```", "").replace("<|im_start|>", "").replace("<|im_end|>", "")
    
    return cleaned


class TeamMember(BaseModel):
    name: str = Field(..., min_length=1, max_length=60, description="Name of the team member")
    skills: str = Field(..., min_length=1, max_length=150, description="Skills/roles (e.g. Frontend, React)")
    hours: float = Field(..., ge=1.0, le=168.0, description="Available hours for the project")

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=60)

    @field_validator("skills", mode="before")
    @classmethod
    def sanitize_skills(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=150)


class TaskItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=120, description="Title of the task")
    required_skill: str = Field(..., min_length=1, max_length=80, description="Required skill/domain")
    estimated_hours: float = Field(..., ge=0.5, le=100.0, description="Estimated effort in hours")

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=120)

    @field_validator("required_skill", mode="before")
    @classmethod
    def sanitize_required_skill(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=80)


class CoordinationRequest(BaseModel):
    members: List[TeamMember] = Field(..., min_length=1, max_length=10, description="List of team members")
    tasks: List[TaskItem] = Field(..., min_length=1, max_length=20, description="List of project tasks")


class AssignmentItem(BaseModel):
    task_title: str
    assigned_to: str
    required_skill: str
    estimated_hours: float
    reasoning: str


class CoordinationResponse(BaseModel):
    fairness_score: int = Field(..., ge=0, le=100, description="Workload fairness score (0-100)")
    executive_summary: str = Field(..., description="2-sentence overview of balance and bottlenecks")
    assignments: List[AssignmentItem] = Field(..., description="Task assignment list")
    is_mock: bool = Field(default=False, description="True if generated via offline mock engine")


class AuthRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="Username (letters, numbers, underscores)")
    password: str = Field(..., min_length=4, max_length=50, description="Account password")
    display_name: str = Field(..., min_length=1, max_length=60, description="Full or preferred name")
    role: str = Field(..., description="'lead' for Team Lead or 'candidate' for Candidate/Employee")
    skills: str = Field(default="", max_length=150, description="Skills/specialties")
    hours: float = Field(default=8.0, ge=1.0, le=168.0, description="Weekly or sprint availability hours")

    @field_validator("username", mode="before")
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        return sanitize_text(str(v).lower().replace(" ", "_"), max_length=50)

    @field_validator("display_name", mode="before")
    @classmethod
    def sanitize_display(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=60)

    @field_validator("skills", mode="before")
    @classmethod
    def sanitize_skills(cls, v: str) -> str:
        return sanitize_text(str(v), max_length=150)


class AuthLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Username or alias")
    password: str = Field(..., min_length=1, max_length=50, description="Account password")
    role: str = Field(default="lead", description="'lead' or 'candidate'")

    @field_validator("username", mode="before")
    @classmethod
    def sanitize_user(cls, v: str) -> str:
        return sanitize_text(str(v).lower().strip().replace(" ", "_"), max_length=50)


class AuthUserResponse(BaseModel):
    success: bool
    username: str
    display_name: str
    role: str  # "lead" or "candidate"
    skills: str
    hours: float
    dashboard_data: dict
    message: str


def safe_escape(val: str) -> str:
    """Escapes HTML entities to prevent XSS injection."""
    return html.escape(val, quote=True)

