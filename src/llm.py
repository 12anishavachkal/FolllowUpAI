"""Builds the Gemini model from settings in .env, so no key or model name is hard-coded."""

import os

from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

load_dotenv()  # reads the local .env file (never committed)

DEFAULT_MODEL = "gemini-3.8-flash"


class LLMConfigError(Exception):
    """Raised when the model or API key is not configured."""


def get_model() -> GoogleModel:
    """Return a Gemini model configured from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise LLMConfigError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    model_name = os.getenv("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return GoogleModel(model_name, provider=GoogleProvider(api_key=api_key))