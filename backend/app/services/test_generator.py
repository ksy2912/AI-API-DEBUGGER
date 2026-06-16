import json

from app.models import HttpMethod
from app.schemas.tests import GenerateTestsRequest, GeneratedTestCase
from app.services.llm import invoke_llm, llm_available, parse_json_response


def _heuristic_tests(req: GenerateTestsRequest) -> list[GeneratedTestCase]:
    method = req.method or HttpMethod.GET
    url = req.url or "https://api.example.com/resource"
    base_path = url.rstrip("/")

    return [
        GeneratedTestCase(
            name="Happy path",
            test_type="positive",
            description="Valid request should return 2xx",
            method=method,
            url=url,
            headers=req.headers,
            body=req.body,
            expected_status=200,
        ),
        GeneratedTestCase(
            name="Missing auth",
            test_type="auth",
            description="Request without credentials should return 401",
            method=method,
            url=url,
            headers={},
            body=req.body,
            expected_status=401,
        ),
        GeneratedTestCase(
            name="Invalid payload",
            test_type="negative",
            description="Malformed JSON body should return 400/422",
            method=HttpMethod.POST if method == HttpMethod.GET else method,
            url=url,
            headers={"Content-Type": "application/json"},
            body='{"invalid": true',
            expected_status=400,
        ),
        GeneratedTestCase(
            name="Not found path",
            test_type="edge_case",
            description="Non-existent resource path should return 404",
            method=method,
            url=f"{base_path}/nonexistent-id-99999",
            headers=req.headers,
            expected_status=404,
        ),
        GeneratedTestCase(
            name="Empty required field",
            test_type="negative",
            description="Empty required fields should fail validation",
            method=HttpMethod.POST,
            url=url,
            headers={"Content-Type": "application/json"},
            body="{}",
            expected_status=422,
        ),
    ][: req.count]


async def generate_tests(req: GenerateTestsRequest) -> tuple[list[GeneratedTestCase], bool]:
    if not llm_available():
        return _heuristic_tests(req), False

    spec = req.spec or f"{req.method or 'GET'} {req.url or '/api/resource'}"
    system = """You are an API test engineer. Generate API test cases as JSON array:
[{"name":"...", "test_type":"positive|negative|edge_case|auth", "description":"...",
  "method":"GET|POST|PUT|DELETE", "url":"...", "headers":{}, "body":null, "expected_status":400}]
Return ONLY valid JSON array."""
    user = f"""Generate {req.count} test cases for this API:
Spec: {spec}
Method: {req.method}
URL: {req.url}
Headers: {json.dumps(req.headers)}
Body: {req.body}

Include edge cases, invalid input tests, and authentication tests."""

    try:
        raw = await invoke_llm(system, user)
        data = parse_json_response(raw)
        items = data if isinstance(data, list) else data.get("tests", [])
        tests = []
        for item in items[: req.count]:
            tests.append(
                GeneratedTestCase(
                    name=item.get("name", "Test"),
                    test_type=item.get("test_type", "edge_case"),
                    description=item.get("description", ""),
                    method=HttpMethod(item.get("method", "GET")),
                    url=item.get("url", req.url or "/"),
                    headers=item.get("headers", {}),
                    body=item.get("body"),
                    expected_status=item.get("expected_status"),
                )
            )
        return tests, True
    except Exception:
        return _heuristic_tests(req), False
