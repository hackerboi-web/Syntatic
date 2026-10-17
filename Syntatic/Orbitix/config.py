import os
from pathlib import Path

APP_NAME = "Orbitix"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "XXXXX")
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
