from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import debug as debug_crud
from app.crud import run as run_crud
from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.debug import (
    DebugAnalyzeRequest,
    DebugSessionResponse,
    FailureContext,
    MultiAgentDebugResponse,
    SingleDebugResponse,
)
from app.services.failure_context import analyze_single, format_failure_context
from app.services.multi_agent_debugger import run_multi_agent_debug
from app.services.rag import format_rag_context, index_debug_session, retrieve_similar

router = APIRouter(prefix="/debug", tags=["debug"])


def _resolve_context(
    db: Session, data: DebugAnalyzeRequest
) -> tuple[FailureContext, UUID | None]:
    if data.run_id:
        run = run_crud.get_run(db, data.run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        if run.success and not data.force:
            raise HTTPException(
                status_code=400,
                detail="Run succeeded — only failed runs can be debugged (use force=true to override)",
            )
        return debug_crud.context_from_run(run), run.id

    if data.context:
        if data.context.success and not data.force:
            raise HTTPException(
                status_code=400,
                detail="Context indicates success — provide a failed request",
            )
        return data.context, None

    raise HTTPException(status_code=400, detail="Provide run_id or context")


async def _get_rag_context(db: Session, ctx: FailureContext) -> str:
    try:
        hits = await retrieve_similar(db, format_failure_context(ctx))
        return format_rag_context(hits)
    except Exception:
        return ""


@router.post("/analyze", response_model=SingleDebugResponse)
async def debug_analyze(data: DebugAnalyzeRequest, db: Session = Depends(get_db)):
    ctx, run_id = _resolve_context(db, data)
    rag_context = await _get_rag_context(db, ctx)
    result, llm_used = await analyze_single(ctx, rag_context=rag_context)
    session = debug_crud.create_single_session(
        db, run_id=run_id, result=result, llm_used=llm_used
    )
    try:
        await index_debug_session(db, session)
    except Exception:
        pass
    return SingleDebugResponse(session_id=session.id, llm_used=llm_used, result=result)


@router.post("/multi-agent", response_model=MultiAgentDebugResponse)
async def debug_multi_agent(data: DebugAnalyzeRequest, db: Session = Depends(get_db)):
    ctx, run_id = _resolve_context(db, data)
    rag_context = await _get_rag_context(db, ctx)
    result, llm_used = await run_multi_agent_debug(ctx, rag_context=rag_context)
    session = debug_crud.create_multi_agent_session(
        db, run_id=run_id, result=result, llm_used=llm_used
    )
    try:
        await index_debug_session(db, session)
    except Exception:
        pass
    return MultiAgentDebugResponse(session_id=session.id, llm_used=llm_used, result=result)


@router.post("/runs/{run_id}/analyze", response_model=SingleDebugResponse)
async def debug_run_single(
    run_id: UUID,
    force: bool = False,
    db: Session = Depends(get_db),
):
    return await debug_analyze(
        DebugAnalyzeRequest(run_id=run_id, force=force), db
    )


@router.post("/runs/{run_id}/multi-agent", response_model=MultiAgentDebugResponse)
async def debug_run_multi(
    run_id: UUID,
    force: bool = False,
    db: Session = Depends(get_db),
):
    return await debug_multi_agent(
        DebugAnalyzeRequest(run_id=run_id, force=force), db
    )


@router.get("/sessions", response_model=PaginatedResponse[DebugSessionResponse])
def list_debug_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    run_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    items = debug_crud.list_sessions(db, skip=skip, limit=limit, run_id=run_id)
    total = debug_crud.count_sessions(db, run_id=run_id)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/sessions/{session_id}", response_model=DebugSessionResponse)
def get_debug_session(session_id: UUID, db: Session = Depends(get_db)):
    session = debug_crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    return session
