"""Vercel entry point for the FastAPI application."""

import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parent.parent)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app import app
