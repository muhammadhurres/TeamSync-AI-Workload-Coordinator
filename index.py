import sys
import os
# Root directory ko path mein add karein taake app.py import ho sake
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app