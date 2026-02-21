function normalizeApiBaseUrl(rawBaseUrl: string) {
  const trimmed = rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl;
  if (trimmed.endsWith('/v1')) return trimmed;
  return `${trimmed}/v1`;
}

const API_BASE_URL = normalizeApiBaseUrl(
  import.meta.env.VITE_API_URL ?? 'http://localhost:3000',
);
export const AUTH_TOKEN_KEY = 'bom-jesus-auth-token';
export const REFRESH_TOKEN_KEY = 'bom-jesus-refresh-token';

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const request = async (token?: string) =>
    fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers ?? {}),
      },
      ...options,
    });

  const token = localStorage.getItem(AUTH_TOKEN_KEY) ?? undefined;
  let response = await request(token);

  if (response.status === 401) {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      const refreshed = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken }),
      });

      if (refreshed.ok) {
        const tokens = (await refreshed.json()) as {
          accessToken: string;
          refreshToken: string;
        };
        localStorage.setItem(AUTH_TOKEN_KEY, tokens.accessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
        response = await request(tokens.accessToken);
      } else {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
      }
    }
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Erro na API (${response.status})`);
  }

  return (await response.json()) as T;
}

export async function apiTextRequest(
  path: string,
  options: RequestInit = {},
): Promise<string> {
  const request = async (token?: string) =>
    fetch(`${API_BASE_URL}${path}`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers ?? {}),
      },
      ...options,
    });

  const token = localStorage.getItem(AUTH_TOKEN_KEY) ?? undefined;
  let response = await request(token);
  if (response.status === 401) {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      const refreshed = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken }),
      });
      if (refreshed.ok) {
        const tokens = (await refreshed.json()) as {
          accessToken: string;
          refreshToken: string;
        };
        localStorage.setItem(AUTH_TOKEN_KEY, tokens.accessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
        response = await request(tokens.accessToken);
      }
    }
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Erro na API (${response.status})`);
  }

  return response.text();
}

export { API_BASE_URL };
