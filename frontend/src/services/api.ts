const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ThreadUserIds {
  thread_id: string;
  user_id: string;
}

export interface GenerateETLRequest {
  data_uri: string;
  ids: ThreadUserIds;
}

export interface GenerateETLResponse {
  ids: ThreadUserIds;
  message: string;
  done: boolean;
  extract_config?: Record<string, unknown>;
  transform_config?: Record<string, unknown>;
  load_config?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
}

export interface FeedbackItem {
  area: string;
  message: string;
  suggestion?: string;
}

export interface Feedback {
  items: FeedbackItem[];
  overall?: string;
}

export interface UpdateETLRequest {
  feedback: Feedback;
  ids: ThreadUserIds;
}

export interface UpdateETLResponse {
  ids: ThreadUserIds;
  message: string;
  done: boolean;
  extract_config?: Record<string, unknown>;
  transform_config?: Record<string, unknown>;
  load_config?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
}

export interface ExecuteETLRequest {
  ids: ThreadUserIds;
}

export interface ExecuteETLResponse {
  ids: ThreadUserIds;
  message: string;
  done: boolean;
  success: boolean;
}

export async function* generateETL(request: GenerateETLRequest): AsyncGenerator<GenerateETLResponse> {
  const response = await fetch(`${API_BASE_URL}/generate_etl`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('No response body');
  }

  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        yield JSON.parse(line);
      }
    }
  }
}

export async function* updateETL(request: UpdateETLRequest): AsyncGenerator<UpdateETLResponse> {
  const response = await fetch(`${API_BASE_URL}/update_etl`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('No response body');
  }

  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        yield JSON.parse(line);
      }
    }
  }
}

export async function* executeETL(request: ExecuteETLRequest): AsyncGenerator<ExecuteETLResponse> {
  const response = await fetch(`${API_BASE_URL}/execute_etl`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('No response body');
  }

  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        yield JSON.parse(line);
      }
    }
  }
}