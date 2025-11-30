"""Configuration management for the Email Assistant."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Email Configuration
    EMAIL_ID = os.getenv("EMAIL_ID", "")
    APP_PASSWORD = os.getenv("APP_PASSWORD", "")

    # Date Range for Email Fetching
    START_DATE = os.getenv("START_DATE", "2025-11-28")
    END_DATE = os.getenv("END_DATE", "2025-11-30")

    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "llama3.1:8b")

    # Vector Store Configuration
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_store")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "emails")

    # LLM Configuration
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    # Query Configuration
    DEFAULT_RETRIEVAL_COUNT = int(os.getenv("DEFAULT_RETRIEVAL_COUNT", "50"))

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []

        if not cls.EMAIL_ID:
            errors.append("EMAIL_ID is required")
        if not cls.APP_PASSWORD:
            errors.append("APP_PASSWORD is required")
        if not cls.OLLAMA_BASE_URL:
            errors.append("OLLAMA_BASE_URL is required")
        if not cls.OLLAMA_LLM_MODEL:
            errors.append("OLLAMA_LLM_MODEL is required")

        if errors:
            raise ValueError(
                f"Configuration validation failed:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        return True


# Create a singleton config instance
config = Config()
