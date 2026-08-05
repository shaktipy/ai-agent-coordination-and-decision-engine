"""
agents/utils/llm_factory.py — LLM Factory
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def build_llm(
    provider: str = "groq",
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.0,
):
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            groq_api_key=GROQ_API_KEY,
            temperature=temperature,
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: 'groq', 'gemini'."
        )
