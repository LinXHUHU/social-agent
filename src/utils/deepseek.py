"""DeepSeek-V3 API wrapper. Uses OpenAI-compatible endpoint."""
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-your-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)
    return _client


def chat(
    system: str,
    user: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """Send a chat completion and return the response text."""
    response = get_client().chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content
