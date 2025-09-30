const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ThreadUserIds {
  thread_id: string;
  user_id: string;
}

export interface CreateETLRequest {
  user_prompt: string;
  ids: ThreadUserIds;
}

export interface ETLResponse {
  ids: ThreadUserIds;
  processing_done: boolean;
  processing_percentage_done: number;
  processing_message: string;
  success: boolean;
  error_message?: string;
  extract_config?: Record<string, unknown>;
  transform_config?: Record<string, unknown>;
  load_config?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
}

export interface CreateETLResponse extends ETLResponse {}

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
  extract_config?: Record<string, unknown>;
  transform_config?: Record<string, unknown>;
  load_config?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
}

export interface UpdateETLResponse extends ETLResponse {}

export interface PublishETLRequest {
  ids: ThreadUserIds;
}

export interface PublishETLResponse extends ETLResponse {}

export async function* createETL(request: CreateETLRequest): AsyncGenerator<CreateETLResponse> {
  const response = await fetch(`${API_BASE_URL}/create_etl`, {
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

export async function* publishETL(request: PublishETLRequest): AsyncGenerator<PublishETLResponse> {
  const response = await fetch(`${API_BASE_URL}/publish_etl`, {
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