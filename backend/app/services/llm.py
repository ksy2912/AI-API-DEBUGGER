import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings


def llm_available() -> bool:
    return bool(settings.llm_enabled and settings.openrouter_api_key)


def get_chat_model() -> ChatOpenAI:
    if not llm_available():
        raise RuntimeError("OpenRouter API key not configured (set OPENROUTER_API_KEY)")
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.2,
        default_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.app_name,
        },
    )


async def invoke_llm(system: str, user: str) -> str:
    model = get_chat_model()
    response = await model.ainvoke(
        [SystemMessage(content=system), HumanMessage(content=user)]
    )
    return str(response.content)


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)
