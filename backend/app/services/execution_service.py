import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import auth_profile as auth_profile_crud
from app.crud import environment as environment_crud
from app.crud import run as run_crud
from urllib.parse import urlparse

from app.models import ApiRequest, AuthProfile, Environment
from app.schemas.execute import ExecuteRequest, ExecuteResponse
from app.services.http_executor import execute_http_request
from app.services.variable_substitution import (
    has_unresolved_placeholders,
    substitute_dict,
    substitute_variables,
)


def _resolve_auth(
    auth_type, auth_config: dict, auth_profile: AuthProfile | None
):
    if auth_profile:
        return auth_profile.auth_type, dict(auth_profile.auth_config)
    return auth_type, dict(auth_config)


def _validate_resolved_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")
    if not parsed.netloc:
        raise ValueError("URL is missing a hostname after variable substitution")


def apply_environment(
    request: ExecuteRequest,
    environment: Environment | None,
    auth_profile: AuthProfile | None = None,
) -> ExecuteRequest:
    variables = dict(environment.variables) if environment else {}
    auth_type, auth_config = _resolve_auth(
        request.auth_type, request.auth_config, auth_profile
    )

    url = substitute_variables(request.url, variables) or request.url
    body = substitute_variables(request.body, variables)
    headers = substitute_dict(request.headers, variables)
    query_params = substitute_dict(request.query_params, variables)
    auth_config = substitute_dict(auth_config, variables)

    if has_unresolved_placeholders(url):
        raise ValueError(
            "URL still contains unresolved {{variables}} after substitution. "
            "Check your environment variables."
        )
    _validate_resolved_url(url)

    return ExecuteRequest(
        method=request.method,
        url=url,
        headers=headers,
        query_params=query_params,
        body=body,
        auth_type=auth_type,
        auth_config=auth_config,
        timeout_seconds=request.timeout_seconds,
        environment_id=request.environment_id,
        api_request_id=request.api_request_id,
    )


def build_execute_request_from_saved(
    saved: ApiRequest,
    environment_override_id: UUID | None = None,
) -> ExecuteRequest:
    environment_id = environment_override_id or saved.environment_id
    return ExecuteRequest(
        method=saved.method,
        url=saved.url,
        headers={str(k): str(v) for k, v in saved.headers.items()},
        query_params={str(k): str(v) for k, v in saved.query_params.items()},
        body=saved.body,
        auth_type=saved.auth_type,
        auth_config=dict(saved.auth_config),
        environment_id=environment_id,
        api_request_id=saved.id,
    )


async def execute_and_persist(
    db: Session,
    request: ExecuteRequest,
    *,
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
) -> ExecuteResponse:
    environment = None
    if request.environment_id:
        environment = environment_crud.get_environment(db, request.environment_id)
        if not environment:
            raise ValueError(f"Environment not found: {request.environment_id}")

    auth_profile = None
    if api_request_id:
        saved = db.get(ApiRequest, api_request_id)
        if saved and saved.auth_profile_id:
            auth_profile = auth_profile_crud.get_auth_profile(db, saved.auth_profile_id)

    resolved = apply_environment(request, environment, auth_profile)
    result = await execute_http_request(resolved)

    run = run_crud.create_run(
        db,
        api_request_id=api_request_id or request.api_request_id,
        monitor_id=monitor_id,
        environment_id=request.environment_id,
        method=resolved.method,
        url=resolved.url,
        request_headers=resolved.headers,
        request_body=resolved.body,
        status_code=result.status_code,
        response_headers=result.headers,
        response_body=result.body,
        latency_ms=result.latency_ms,
        success=result.success,
        error=result.error,
    )

    result.run_id = run.id

    try:
        from app.services.rag import index_run
        await index_run(db, run)
    except Exception:
        pass

    return result


def execute_and_persist_sync(
    db: Session,
    request: ExecuteRequest,
    *,
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
) -> ExecuteResponse:
    return asyncio.run(
        execute_and_persist(
            db,
            request,
            api_request_id=api_request_id,
            monitor_id=monitor_id,
        )
    )
