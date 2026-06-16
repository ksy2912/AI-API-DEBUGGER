export interface GeneratedTestCase {
  name: string;
  test_type: string;
  description: string;
  method: string;
  url: string;
  headers: Record<string, string>;
  body: string | null;
  expected_status: number | null;
}

export interface GenerateTestsRequest {
  spec?: string;
  method?: string;
  url?: string;
  headers?: Record<string, string>;
  body?: string | null;
  count?: number;
}

export interface GeneratedTestResponse {
  api_request_id: string | null;
  llm_used: boolean;
  tests: GeneratedTestCase[];
}
