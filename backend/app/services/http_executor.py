import time
from typing import Any

import httpx

from app.models import AuthType, HttpMethod
from app.schemas.execute import ExecuteRequest, ExecuteResponse


def _stringify_params(params: dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in params.items()}


def _apply_auth_headers(
    headers: dict[str, str], auth_type: AuthType, auth_config: dict
) -> dict[str, str]:
    result = dict(headers)
    if auth_type == AuthType.BEARER:
        token = auth_config.get("token", "")
        if token:
            result["Authorization"] = f"Bearer {token}"
    elif auth_type == AuthType.API_KEY:
        key_name = auth_config.get("key_name", "X-API-Key")
        key_value = auth_config.get("key_value", "")
        if key_value:
            result[key_name] = key_value
    return result


def _resolve_basic_auth(
    auth_type: AuthType, auth_config: dict
) -> tuple[str, str] | None:
    if auth_type != AuthType.BASIC:
        return None
    username = auth_config.get("username", "")
    password = auth_config.get("password", "")
    if not username:
        return None
    return username, password


def _friendly_request_error(exc: httpx.RequestError) -> str:
    message = str(exc)
    if "Name or service not known" in message or "getaddrinfo failed" in message:
        host = getattr(exc.request, "url", None)
        host_str = str(host.host) if host else "the hostname in your URL"
        return (
            f"DNS lookup failed for {host_str}. "
            "Check the URL spelling, include https://, and use a real hostname. "
            "If calling a service on your PC, use host.docker.internal instead of localhost "
            "(the API runs inside Docker)."
        )
    if "Connection refused" in message:
        return (
            f"Connection refused — nothing is listening at that address. {message}"
        )
    return message


def _response_headers(response: httpx.Response) -> dict[str, str]:
    return {key: value for key, value in response.headers.items()}


async def execute_http_request(request: ExecuteRequest) -> ExecuteResponse:
    headers = _apply_auth_headers(request.headers, request.auth_type, request.auth_config)
    params = _stringify_params(request.query_params)
    basic_auth = _resolve_basic_auth(request.auth_type, request.auth_config)

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.request(
                method=request.method.value,
                url=request.url,
                headers=headers,
                params=params,
                content=request.body.encode() if request.body else None,
                auth=basic_auth,
                timeout=request.timeout_seconds,
            )
        latency_ms = (time.perf_counter() - start) * 1000
        return ExecuteResponse(
            status_code=response.status_code,
            headers=_response_headers(response),
            body=response.text,
            latency_ms=round(latency_ms, 2),
            success=response.is_success,
        )
    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - start) * 1000
        return ExecuteResponse(
            latency_ms=round(latency_ms, 2),
            success=False,
            error=f"Request timed out after {request.timeout_seconds}s",
        )
    except httpx.RequestError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return ExecuteResponse(
            latency_ms=round(latency_ms, 2),
            success=False,
            error=_friendly_request_error(exc),
        )
