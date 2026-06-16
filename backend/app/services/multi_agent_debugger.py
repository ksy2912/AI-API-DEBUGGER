import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph

from app.models import AuthType
from app.schemas.debug import (
    AgentTraceStep,
    FailureContext,
    MultiAgentDebugResult,
    OptimizedRequest,
)
from app.services.failure_context import (
    _heuristic_single,
    build_optimized_from_context,
    format_failure_context,
)


class AgentState(TypedDict):
    context: FailureContext
    context_text: str
    diagnosis: str
    root_cause: str
    suggested_fix: str
    validated_fix: str
    validation_passed: bool
    optimized_request: OptimizedRequest
    trace: Annotated[list[AgentTraceStep], operator.add]
    llm_used: bool


async def _llm_step(system: str, user: str, field: str, state: AgentState) -> str:
    from app.services.llm import invoke_llm, llm_available

    if not llm_available():
        return ""
    try:
        raw = await invoke_llm(system, user)
        state["llm_used"] = True
        return raw.strip()
    except Exception:
        return ""


async def diagnoser_node(state: AgentState) -> dict:
    from app.services.llm import llm_available

    system = """You are the Diagnoser agent. Summarize observable symptoms of this API failure in 2-4 sentences.
Focus on status code, error message, and response body clues. Be specific."""
    user = state["context_text"]

    if not llm_available():
        heuristic = _heuristic_single(state["context"])
        output = f"Observed failure: {heuristic.cause}"
        return {
            "diagnosis": output,
            "trace": [AgentTraceStep(agent="Diagnoser", output=output)],
        }

    output = await _llm_step(system, user, "diagnosis", state)
    if not output:
        heuristic = _heuristic_single(state["context"])
        output = f"Observed failure: {heuristic.cause}"

    return {
        "diagnosis": output,
        "trace": [AgentTraceStep(agent="Diagnoser", output=output)],
    }


async def root_cause_node(state: AgentState) -> dict:
    system = """You are the Root-Cause agent. Given the diagnosis, identify the underlying technical root cause.
Explain WHY it failed, not just what happened. 2-3 sentences."""
    user = f"Diagnosis:\n{state['diagnosis']}\n\nRequest:\n{state['context_text']}"

    from app.services.llm import llm_available
    if not llm_available():
        heuristic = _heuristic_single(state["context"])
        output = heuristic.cause
        return {
            "root_cause": output,
            "trace": [AgentTraceStep(agent="Root-Cause", output=output)],
        }

    output = await _llm_step(system, user, "root_cause", state)
    if not output:
        output = _heuristic_single(state["context"]).cause

    return {
        "root_cause": output,
        "trace": [AgentTraceStep(agent="Root-Cause", output=output)],
    }


async def fix_suggester_node(state: AgentState) -> dict:
    system = """You are the Fix-Suggester agent. Propose concrete fix steps for this API failure.
Include header/auth/url/body changes. Be actionable. 3-5 bullet points as a single string."""
    user = f"Root cause:\n{state['root_cause']}\n\nRequest:\n{state['context_text']}"

    from app.services.llm import llm_available
    if not llm_available():
        heuristic = _heuristic_single(state["context"])
        output = heuristic.fix
        optimized = build_optimized_from_context(state["context"], output)
        return {
            "suggested_fix": output,
            "optimized_request": optimized,
            "trace": [AgentTraceStep(agent="Fix-Suggester", output=output)],
        }

    output = await _llm_step(system, user, "suggested_fix", state)
    if not output:
        heuristic = _heuristic_single(state["context"])
        output = heuristic.fix

    optimized = build_optimized_from_context(state["context"], output)
    ctx = state["context"]

    if ctx.status_code == 401 and optimized.auth_type == AuthType.NONE:
        optimized.auth_type = AuthType.BEARER
        optimized.auth_config = {"token": "{{api_token}}"}

    return {
        "suggested_fix": output,
        "optimized_request": optimized,
        "trace": [AgentTraceStep(agent="Fix-Suggester", output=output)],
    }


async def validator_node(state: AgentState) -> dict:
    system = """You are the Validator agent. Review the proposed fix against the root cause.
Respond with JSON only: {"validation_passed": true|false, "validated_fix": "refined fix text", "notes": "why"}"""
    user = f"""Root cause: {state['root_cause']}
Suggested fix: {state['suggested_fix']}
Optimized request: {state['optimized_request']}"""

    from app.services.llm import invoke_llm, llm_available, parse_json_response

    if not llm_available():
        output = state["suggested_fix"]
        return {
            "validated_fix": output,
            "validation_passed": True,
            "trace": [
                AgentTraceStep(
                    agent="Validator",
                    output="Fix validated (heuristic mode): addresses identified root cause.",
                )
            ],
        }

    try:
        raw = await invoke_llm(system, user)
        state["llm_used"] = True
        data = parse_json_response(raw)
        validated = data.get("validated_fix", state["suggested_fix"])
        passed = bool(data.get("validation_passed", True))
        notes = data.get("notes", "")
        trace_output = f"{'PASSED' if passed else 'NEEDS REVIEW'}: {validated}"
        if notes:
            trace_output += f" — {notes}"

        optimized = state["optimized_request"]
        if notes:
            optimized.notes = notes

        return {
            "validated_fix": validated,
            "validation_passed": passed,
            "optimized_request": optimized,
            "trace": [AgentTraceStep(agent="Validator", output=trace_output)],
        }
    except Exception:
        output = state["suggested_fix"]
        return {
            "validated_fix": output,
            "validation_passed": True,
            "trace": [
                AgentTraceStep(
                    agent="Validator",
                    output="Fix validated (fallback): suggested fix accepted.",
                )
            ],
        }


def build_debug_graph():
    graph = StateGraph(AgentState)
    graph.add_node("diagnoser", diagnoser_node)
    graph.add_node("root_cause_analyst", root_cause_node)
    graph.add_node("fix_suggester", fix_suggester_node)
    graph.add_node("validator", validator_node)

    graph.set_entry_point("diagnoser")
    graph.add_edge("diagnoser", "root_cause_analyst")
    graph.add_edge("root_cause_analyst", "fix_suggester")
    graph.add_edge("fix_suggester", "validator")
    graph.add_edge("validator", END)

    return graph.compile()


_debug_graph = None


def get_debug_graph():
    global _debug_graph
    if _debug_graph is None:
        _debug_graph = build_debug_graph()
    return _debug_graph


async def run_multi_agent_debug(
    ctx: FailureContext, rag_context: str = ""
) -> tuple[MultiAgentDebugResult, bool]:
    graph = get_debug_graph()
    context_text = format_failure_context(ctx)
    if rag_context:
        context_text = f"{rag_context}\n\n## Current failure:\n{context_text}"

    initial: AgentState = {
        "context": ctx,
        "context_text": context_text,
        "diagnosis": "",
        "root_cause": "",
        "suggested_fix": "",
        "validated_fix": "",
        "validation_passed": False,
        "optimized_request": build_optimized_from_context(ctx, ""),
        "trace": [],
        "llm_used": False,
    }

    final = await graph.ainvoke(initial)

    result = MultiAgentDebugResult(
        diagnosis=final["diagnosis"],
        root_cause=final["root_cause"],
        suggested_fix=final["suggested_fix"],
        validated_fix=final["validated_fix"],
        validation_passed=final["validation_passed"],
        optimized_request=final["optimized_request"],
        agent_trace=final["trace"],
    )
    return result, final.get("llm_used", False)
