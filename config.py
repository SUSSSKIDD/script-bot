import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
FAISS_DIR = DATA_DIR / "faiss"
USERS_FILE = DATA_DIR / "users.json"
HISTORY_DIR = DATA_DIR / "history"

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GENERATION_MODEL = "gemini-3-flash-preview"
EMBEDDING_MODEL = "gemini-embedding-001"

# FAISS
TOP_K_RESULTS = 5

# App
APP_TITLE = "Reels Script Generator"
SCRIPT_SECTIONS = ["Hook", "Introduction", "Problem", "Solution", "CTA"]
