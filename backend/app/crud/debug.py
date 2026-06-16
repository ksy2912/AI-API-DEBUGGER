import json
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DebugMode, DebugSession, RequestRun
from app.schemas.debug import FailureContext, MultiAgentDebugResult, SingleDebugResult


def context_from_run(run: RequestRun) -> FailureContext:
    return FailureContext(
        method=run.method,
        url=run.url,
        request_headers=run.request_headers or {},
        request_body=run.request_body,
        status_code=run.status_code,
        response_headers=run.response_headers or {},
        response_body=run.response_body,
        latency_ms=run.latency_ms,
        success=run.success,
        error=run.error,
    )


def create_single_session(
    db: Session,
    *,
    run_id: UUID | None,
    result: SingleDebugResult,
    llm_used: bool,
) -> DebugSession:
    session = DebugSession(
        run_id=run_id,
        mode=DebugMode.SINGLE,
        cause=result.cause,
        fix=result.fix,
        optimized_request={},
        agent_trace=[],
        llm_used=llm_used,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def create_multi_agent_session(
    db: Session,
    *,
    run_id: UUID | None,
    result: MultiAgentDebugResult,
    llm_used: bool,
) -> DebugSession:
    session = DebugSession(
        run_id=run_id,
        mode=DebugMode.MULTI_AGENT,
        diagnosis=result.diagnosis,
        root_cause=result.root_cause,
        suggested_fix=result.suggested_fix,
        validated_fix=result.validated_fix,
        optimized_request=result.optimized_request.model_dump(),
        agent_trace=[step.model_dump() for step in result.agent_trace],
        llm_used=llm_used,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: UUID) -> DebugSession | None:
    return db.get(DebugSession, session_id)


def list_sessions(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    run_id: UUID | None = None,
) -> list[DebugSession]:
    stmt = select(DebugSession)
    if run_id is not None:
        stmt = stmt.where(DebugSession.run_id == run_id)
    stmt = stmt.offset(skip).limit(limit).order_by(DebugSession.created_at.desc())
    return list(db.scalars(stmt).all())


def count_sessions(db: Session, run_id: UUID | None = None) -> int:
    stmt = select(func.count()).select_from(DebugSession)
    if run_id is not None:
        stmt = stmt.where(DebugSession.run_id == run_id)
    return db.scalar(stmt) or 0
