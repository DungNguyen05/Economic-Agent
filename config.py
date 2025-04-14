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

# Base paths with explicit creation
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Ensure data directory is created with a more robust method
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))).resolve()

# Create necessary directories with logging
def create_directories():
    """Create all necessary directories with logging"""
    directories = [
        TEMPLATES_DIR,
        STATIC_DIR,
        DATA_DIR,
        DATA_DIR / "qdrant_storage",
        DATA_DIR / "transformers_cache",
        DATA_DIR / "torch_hub_cache"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        except Exception as e:
            logging.error(f"Error creating directory {directory}: {e}")

# Call directory creation immediately
create_directories()

# Document storage file
DOCUMENTS_FILE = DATA_DIR / "documents.json"


# Default to all-MiniLM-L6-v2 which is fast and good quality
# Alternative models to consider:
# - "multi-qa-mpnet-base-dot-v1" (better quality, more resource intensive)
# - "all-mpnet-base-v2" (best quality, more resource intensive)
# - "all-MiniLM-L6-v2" (fast, good quality, default)
# - "paraphrase-multilingual-mpnet-base-v2" (for multilingual support)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Advanced RAG configuration
# Text chunking settings
CHUNK_SIZE = _parse_int(os.getenv("CHUNK_SIZE"), 1000)
CHUNK_OVERLAP = _parse_int(os.getenv("CHUNK_OVERLAP"), 200)

# Query transformation settings
USE_QUERY_EXPANSION = _parse_bool(os.getenv("USE_QUERY_EXPANSION", "true"))

# Reranking settings
USE_RERANKING = _parse_bool(os.getenv("USE_RERANKING", "true"))

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


def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Ensure DEBUG level is set

setup_logging()