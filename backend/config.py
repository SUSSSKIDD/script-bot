import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# MongoDB
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASS = os.getenv("MONGO_PASS", "")
MONGO_HOST = os.getenv("MONGO_HOST", "")
MONGO_APP = os.getenv("MONGO_APP", "")
MONGO_DB_NAME = "script_bot"

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GENERATION_MODEL = "models/gemini-2.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"

# Search
TOP_K_RESULTS = 8

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
