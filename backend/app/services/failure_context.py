from app.models import AuthType, HttpMethod
from app.schemas.debug import FailureContext, OptimizedRequest, SingleDebugResult


def _truncate(text: str | None, limit: int = 1500) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n... [truncated]"


def format_failure_context(ctx: FailureContext) -> str:
    return f"""HTTP Method: {ctx.method.value}
URL: {ctx.url}
Request Headers: {ctx.request_headers}
Request Body: {_truncate(ctx.request_body)}
Status Code: {ctx.status_code}
Response Headers: {ctx.response_headers}
Response Body: {_truncate(ctx.response_body)}
Latency (ms): {ctx.latency_ms}
Connection Error: {ctx.error or "none"}
Success: {ctx.success}
"""


def _heuristic_single(ctx: FailureContext) -> SingleDebugResult:
    error = (ctx.error or "").lower()
    status = ctx.status_code
    body = (ctx.response_body or "").lower()

    if "name or service not known" in error or "dns" in error:
        return SingleDebugResult(
            cause="DNS resolution failed — the hostname in the URL cannot be resolved.",
            fix="Verify the URL hostname, include https://, and use host.docker.internal instead of localhost when calling services on your machine from Docker.",
            confidence="high",
        )
    if "timed out" in error or "timeout" in error:
        return SingleDebugResult(
            cause="The request exceeded the configured timeout before receiving a response.",
            fix="Increase timeout_seconds, check if the target service is running, and verify network connectivity.",
            confidence="high",
        )
    if "connection refused" in error:
        return SingleDebugResult(
            cause="Nothing is listening on the target host and port.",
            fix="Start the target service, confirm the port is correct, and use host.docker.internal for local services.",
            confidence="high",
        )
    if status == 401 or "unauthorized" in body:
        return SingleDebugResult(
            cause="Authentication failed — missing or invalid credentials.",
            fix="Set auth_type to bearer/basic/api_key and provide valid credentials in auth_config, or link an auth profile.",
            confidence="high",
        )
    if status == 403:
        return SingleDebugResult(
            cause="The server rejected the request due to insufficient permissions.",
            fix="Check API scopes, tokens, and ensure the authenticated user has access to this resource.",
            confidence="medium",
        )
    if status == 404:
        return SingleDebugResult(
            cause="The endpoint path was not found on the server.",
            fix="Verify the URL path, API version prefix, and trailing slashes. Check environment variable substitution for {{base_url}}.",
            confidence="high",
        )
    if status == 422 or "validation" in body:
        return SingleDebugResult(
            cause="Request payload or parameters failed server-side validation.",
            fix="Review required fields in the request body, Content-Type header, and query parameter types.",
            confidence="medium",
        )
    if status and status >= 500:
        return SingleDebugResult(
            cause=f"Server error (HTTP {status}) — the API encountered an internal failure.",
            fix="Retry with backoff, check server logs, and confirm the request body matches the API contract.",
            confidence="medium",
        )
    return SingleDebugResult(
        cause="The request did not succeed but no specific pattern was detected.",
        fix="Inspect response body and headers, compare against API documentation, and test with a minimal request.",
        confidence="low",
    )


async def analyze_single(
    ctx: FailureContext, rag_context: str = ""
) -> tuple[SingleDebugResult, bool]:
    from app.services.llm import invoke_llm, llm_available, parse_json_response

    if not llm_available():
        return _heuristic_single(ctx), False

    system = """You are an expert API debugger. Analyze failed HTTP requests and respond ONLY with JSON:
{"cause": "likely root symptom", "fix": "actionable fix steps", "confidence": "low|medium|high"}"""
    user = format_failure_context(ctx)
    if rag_context:
        user = f"{rag_context}\n\n## Current failure:\n{user}"

    try:
        raw = await invoke_llm(system, user)
        data = parse_json_response(raw)
        return SingleDebugResult(
            cause=data.get("cause", "Unknown cause"),
            fix=data.get("fix", "Review the request manually"),
            confidence=data.get("confidence", "medium"),
        ), True
    except Exception:
        return _heuristic_single(ctx), False


def build_optimized_from_context(ctx: FailureContext, fix: str) -> OptimizedRequest:
    url = ctx.url
    headers = dict(ctx.request_headers)
    auth_type = AuthType.NONE
    auth_config: dict = {}

    error = (ctx.error or "").lower()
    if "localhost" in url:
        url = url.replace("localhost", "host.docker.internal")
    if ctx.status_code == 401:
        auth_type = AuthType.BEARER
        auth_config = {"token": "{{api_token}}"}
        headers.setdefault("Authorization", "Bearer {{api_token}}")

    return OptimizedRequest(
        method=ctx.method,
        url=url,
        headers=headers,
        body=ctx.request_body,
        auth_type=auth_type,
        auth_config=auth_config,
        notes=fix,
    )
