import httpx

from app.config import settings


async def embed_text(text: str) -> list[float]:
    if not settings.openrouter_api_key:
        raise RuntimeError("OpenRouter API key required for embeddings")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.openrouter_base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": settings.openrouter_site_url,
                "X-Title": settings.app_name,
            },
            json={
                "model": settings.embedding_model,
                "input": text[:8000],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
