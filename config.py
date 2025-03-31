# config.py - Configuration settings with environment variable support
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Helper functions for parsing environment variables
def _parse_bool(value: Optional[str]) -> bool:
    """Parse string to boolean."""
    if value is None:
        return False
    return value.lower() in ("yes", "true", "t", "1")

def _parse_int(value: Optional[str], default: int) -> int:
    """Parse string to integer with default."""
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _parse_float(value: Optional[str], default: float) -> float:
    """Parse string to float with default."""
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

# Base paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

# Create necessary directories
Path(TEMPLATES_DIR).mkdir(exist_ok=True)
Path(STATIC_DIR).mkdir(exist_ok=True)
Path(DATA_DIR).mkdir(exist_ok=True)

# Document storage file
DOCUMENTS_FILE = Path(DATA_DIR) / "documents.json"

# Embedding model configuration
# Use local sentence-transformers for embeddings (to save tokens)
USE_LOCAL_EMBEDDINGS = _parse_bool(os.getenv("USE_LOCAL_EMBEDDINGS", "true"))
# Default to all-MiniLM-L6-v2 which is fast and good quality
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LLM configuration
# Use OpenAI for chat completions (for best quality responses)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")

# Application settings
MAX_SEARCH_RESULTS = _parse_int(os.getenv("MAX_SEARCH_RESULTS"), 5)
MAX_TOKENS_RESPONSE = _parse_int(os.getenv("MAX_TOKENS_RESPONSE"), 500)
TEMPERATURE = _parse_float(os.getenv("TEMPERATURE"), 0.3)
MAX_CONTEXT_LENGTH = _parse_int(os.getenv("MAX_CONTEXT_LENGTH"), 4000)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = _parse_int(os.getenv("PORT"), 8000)
RELOAD = _parse_bool(os.getenv("RELOAD"))
DEBUG = _parse_bool(os.getenv("DEBUG"))

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)