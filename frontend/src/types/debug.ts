export interface RequestRun {
  id: string;
  method: string;
  url: string;
  status_code: number | null;
  success: boolean;
  error: string | null;
  latency_ms: number;
  created_at: string;
}

export interface SingleDebugResult {
  cause: string;
  fix: string;
  confidence: string;
}

export interface AgentTraceStep {
  agent: string;
  output: string;
}

export interface OptimizedRequest {
  method: string;
  url: string;
  headers: Record<string, string>;
  query_params: Record<string, string>;
  body: string | null;
  auth_type: string;
  auth_config: Record<string, string>;
  notes: string | null;
}

export interface MultiAgentDebugResult {
  diagnosis: string;
  root_cause: string;
  suggested_fix: string;
  validated_fix: string;
  validation_passed: boolean;
  optimized_request: OptimizedRequest;
  agent_trace: AgentTraceStep[];
}

export interface SingleDebugResponse {
  session_id: string;
  llm_used: boolean;
  result: SingleDebugResult;
}

export interface MultiAgentDebugResponse {
  session_id: string;
  llm_used: boolean;
  result: MultiAgentDebugResult;
}

export interface DebugSession {
  id: string;
  run_id: string | null;
  mode: "single" | "multi_agent";
  cause: string | null;
  fix: string | null;
  diagnosis: string | null;
  root_cause: string | null;
  created_at: string;
  llm_used: boolean;
}
