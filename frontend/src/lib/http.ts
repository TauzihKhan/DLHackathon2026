const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_TIMEOUT_MS = 10000;

export class HttpError extends Error {
  status: number;
  responseBody: string;

  constructor(status: number, responseBody: string) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
    this.status = status;
    this.responseBody = responseBody;
  }
}

type RequestOptions = {
  baseUrl?: string;
  timeoutMs?: number;
};

function _readViteBaseUrl(): string | undefined {
  try {
    const env = (import.meta as unknown as { env?: Record<string, string | undefined> }).env;
    return env?.VITE_API_BASE_URL;
  } catch {
    return undefined;
  }
}

export function resolveApiBaseUrl(explicitBaseUrl?: string): string {
  const fromWindow =
    typeof window !== "undefined"
      ? ((window as unknown as { __API_BASE_URL__?: string }).__API_BASE_URL__ ?? undefined)
      : undefined;

  const baseUrl = explicitBaseUrl ?? _readViteBaseUrl() ?? fromWindow ?? DEFAULT_API_BASE_URL;
  return baseUrl.replace(/\/+$/, "");
}

export async function httpGetJson<T>(
  path: string,
  options?: RequestOptions,
): Promise<T> {
  const baseUrl = resolveApiBaseUrl(options?.baseUrl);
  const timeoutMs = options?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method: "GET",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
      },
    });

    const text = await response.text();
    if (!response.ok) {
      throw new HttpError(response.status, text);
    }

    return (text ? JSON.parse(text) : {}) as T;
  } finally {
    clearTimeout(timeout);
  }
}

