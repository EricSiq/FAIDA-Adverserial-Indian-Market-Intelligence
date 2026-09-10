import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseModel):
    # App Settings
    APP_NAME: str = "FAIDA"
    APP_TITLE: str = "FAIDA - Financial Adversarial Indian Data Agents"
    HOST: str = "127.0.0.1"
    PORT: int = int(os.getenv("FAIDA_PORT", "8765"))
    DEBUG: bool = os.getenv("FAIDA_DEBUG", "false").lower() == "true"
    
    # LLM Settings
    # Primary local model is gemma4:e4b in Ollama
    DEFAULT_LOCAL_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Cloud Fallback (Groq API or Gemini)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    ACTIVE_PROVIDER: str = os.getenv("FAIDA_PROVIDER", "ollama")  # 'ollama' or 'groq'
    
    # Database
    DB_PATH: str = str(DATA_DIR / "faida_journal.duckdb")
    CACHE_EXPIRY_MINUTES: int = 15
    FUNDAMENTALS_CACHE_HOURS: int = 24

settings = Settings()
