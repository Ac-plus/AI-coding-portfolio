from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
FRONTEND_PUBLIC_DIR = FRONTEND_DIR / "public"
FRONTEND_SRC_DIR = FRONTEND_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
SUBMISSIONS_DIR = DATA_DIR / "submissions"
TAGS_DIR = DATA_DIR / "tags"
TEMP_DIR = BACKEND_DIR / "temp"

HOST = "0.0.0.0"
PORT = 8000
DEFAULT_TIME_LIMIT_MS = 1000
DEFAULT_MEMORY_LIMIT_MB = 256
