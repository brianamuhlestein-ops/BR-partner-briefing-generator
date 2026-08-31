import type { RuntimeContext } from './types'

const API_BASE = '/api/v1/partner-briefing'

export type EmailBriefingKind = 'core' | 'tailored' | 'social'

export type EmailBriefingDocument<T extends object> = {
  briefing_kind: EmailBriefingKind
  document: T
  updated_at: string
  record_version: number
}

type ApiItem<T> = {
  status: 'ok'
  item: T
}

type ApiErrorPayload = {
  error?: { message?: string }
  description?: string
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function responseError(response: Response): Promise<ApiError> {
  let payload: ApiErrorPayload | null = null
  try {
    payload = await response.json() as ApiErrorPayload
  } catch {
    // The status text remains the fallback for non-JSON proxy errors.
  }
  const message = payload?.error?.message
    || payload?.description
    || `Request failed: ${response.status}`
  return new ApiError(response.status, message)
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw await responseError(response)
  }
  return response.json() as Promise<T>
}

export async function fetchRuntimeNow(): Promise<RuntimeContext> {
  return request<RuntimeContext>('/now', { cache: 'no-store' })
}

export async function fetchEmailBriefingDocument<T extends object>(
  briefingKind: EmailBriefingKind,
): Promise<EmailBriefingDocument<T> | null> {
  const response = await fetch(`${API_BASE}/email-briefings/${briefingKind}`, { cache: 'no-store' })
  if (response.status === 404) return null
  if (!response.ok) throw await responseError(response)
  const payload = await response.json() as ApiItem<EmailBriefingDocument<T>>
  return payload.item
}

export async function saveEmailBriefingDocument<T extends object>(
  briefingKind: EmailBriefingKind,
  document: T,
  expectedVersion: number,
): Promise<EmailBriefingDocument<T>> {
  const response = await request<ApiItem<EmailBriefingDocument<T>>>(
    `/email-briefings/${briefingKind}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'If-Match': `"${expectedVersion}"`,
      },
      body: JSON.stringify({ document }),
    },
  )
  return response.item
}
