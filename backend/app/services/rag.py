from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DebugSession, LogEmbedding, RequestRun
from app.services.embeddings import embed_text


def _truncate(s: str | None, limit: int = 500) -> str:
    if not s:
        return ""
    return s if len(s) <= limit else s[:limit] + "..."


def build_run_document(run: RequestRun) -> str:
    return (
        f"API run {run.method.value} {run.url}\n"
        f"Status: {run.status_code}, Success: {run.success}, Latency: {run.latency_ms}ms\n"
        f"Error: {run.error or 'none'}\n"
        f"Response: {_truncate(run.response_body, 400)}"
    )


def build_debug_document(session: DebugSession) -> str:
    parts = [f"Debug session mode={session.mode.value}"]
    if session.cause:
        parts.append(f"Cause: {session.cause}")
    if session.fix:
        parts.append(f"Fix: {session.fix}")
    if session.root_cause:
        parts.append(f"Root cause: {session.root_cause}")
    if session.validated_fix:
        parts.append(f"Validated fix: {session.validated_fix}")
    return "\n".join(parts)


async def index_run(db: Session, run: RequestRun) -> None:
    if not settings.rag_enabled or not settings.openrouter_api_key:
        return
    content = build_run_document(run)
    embedding = await embed_text(content)
    record = LogEmbedding(
        source_type="request_run",
        source_id=run.id,
        content=content,
        embedding=embedding,
        meta={"url": run.url, "method": run.method.value, "success": run.success},
    )
    db.add(record)
    db.commit()


async def index_debug_session(db: Session, session: DebugSession) -> None:
    if not settings.rag_enabled or not settings.openrouter_api_key:
        return
    content = build_debug_document(session)
    embedding = await embed_text(content)
    record = LogEmbedding(
        source_type="debug_session",
        source_id=session.id,
        content=content,
        embedding=embedding,
        meta={"mode": session.mode.value, "run_id": str(session.run_id) if session.run_id else None},
    )
    db.add(record)
    db.commit()


async def retrieve_similar(db: Session, query: str, top_k: int | None = None) -> list[dict]:
    if not settings.rag_enabled or not settings.openrouter_api_key:
        return []

    k = top_k or settings.rag_top_k
    query_embedding = await embed_text(query)

    stmt = (
        select(LogEmbedding)
        .order_by(LogEmbedding.embedding.cosine_distance(query_embedding))
        .limit(k)
    )
    results = db.scalars(stmt).all()
    return [
        {
            "source_type": r.source_type,
            "source_id": str(r.source_id),
            "content": r.content,
            "metadata": r.meta,
        }
        for r in results
    ]


def format_rag_context(hits: list[dict]) -> str:
    if not hits:
        return ""
    lines = ["## Similar past incidents and logs (retrieved via pgvector RAG):"]
    for i, hit in enumerate(hits, 1):
        lines.append(f"\n### Match {i} ({hit['source_type']})")
        lines.append(hit["content"])
    return "\n".join(lines)
