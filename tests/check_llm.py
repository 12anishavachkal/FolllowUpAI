"""Checks the Gemini connection. Run with: python -m tests.check_llm"""

from pydantic_ai import Agent

from src.llm import LLMConfigError, get_model

try:
    agent = Agent(get_model())
    result = agent.run_sync("Reply with exactly one word: OK")
    print("Gemini replied:", result.output)
except LLMConfigError as exc:
    print("Configuration problem:", exc)
except Exception as exc:  # shows the real cause: bad key, wrong model name, quota, network
    print("Call failed:", type(exc).__name__, "-", exc)