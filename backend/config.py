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
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    
    # Cloud Inference (Groq Free Tier Models)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    ACTIVE_PROVIDER: str = os.getenv("FAIDA_PROVIDER", "groq")  # 'groq' (default) or 'ollama'
    
    # Extended Macro & Broker APIs (Optional)
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    BROKER_API_KEY: str = os.getenv("BROKER_API_KEY", "")
    BROKER_NAME: str = os.getenv("BROKER_NAME", "upstox")

    # Database
    DB_PATH: str = str(DATA_DIR / "faida_journal.duckdb")
    FEATURE_STORE_PATH: str = str(DATA_DIR / "faida_features.duckdb")
    CACHE_EXPIRY_MINUTES: int = 15
    FUNDAMENTALS_CACHE_HOURS: int = 24

settings = Settings()

