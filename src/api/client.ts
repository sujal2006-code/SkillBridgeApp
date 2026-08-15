/// <reference types="vite/client" />

/**
 * SkillBridge Backend API Client
 * Configurable via VITE_API_URL environment variable with fallback to http://127.0.0.1:8000
 */

const getBaseUrl = () => {
  const envUrl = ((import.meta as any).env?.VITE_API_URL as string | undefined)?.trim();
  const isProd = (import.meta as any).env?.PROD;

  if (isProd) {
    // In production, only use VITE_API_URL if it is an explicit public remote URL (not localhost)
    if (envUrl && !envUrl.includes('127.0.0.1') && !envUrl.includes('localhost')) {
      return envUrl.replace(/\/+$/, '');
    }
    // Default to same-origin relative path for Vercel unified deployment
    return '';
  }

  // In local development, connect to local FastAPI server
  return (envUrl || 'http://127.0.0.1:8000').replace(/\/+$/, '');
};

const API_BASE_URL = getBaseUrl();

export class ApiError extends Error {
  public status: number;
  public data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 15000, headers = {}, ...customConfig } = options;

  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const config: RequestInit = {
    ...customConfig,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...headers,
    },
    signal: controller.signal,
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);

    // Handle 204 No Content
    if (response.status === 204) {
      return null as T;
    }

    const isJson = response.headers.get('content-type')?.includes('application/json');
    const responseData = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMessage =
        (typeof responseData === 'object' && responseData !== null && (responseData.detail || responseData.message)) ||
        response.statusText ||
        `HTTP Error ${response.status}`;

      throw new ApiError(response.status, typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage), responseData);
    }

    return responseData as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    if (error.name === 'AbortError') {
      throw new ApiError(408, 'Request timeout: Backend server did not respond in time.');
    }
    throw new ApiError(0, error.message || 'Network connection error. Is the FastAPI backend running?');
  }
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) => request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: any, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: any, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: any, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string, options?: RequestOptions) => request<T>(path, { ...options, method: 'DELETE' }),
  getBaseUrl: () => API_BASE_URL,
};
