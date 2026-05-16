import { API_BASE_URL } from './config'

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface SuccessEnvelope<T> {
  success: boolean
  message: string
  data: T
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    cache: 'no-store',
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = await res.json()
      detail = err.detail ?? err.message ?? detail
    } catch {
      /* ignore */
    }
    throw new ApiError(String(detail), res.status)
  }

  const json = (await res.json()) as SuccessEnvelope<T>
  if (!json.success) {
    throw new ApiError(json.message || 'Error en la API')
  }

  return json.data
}
