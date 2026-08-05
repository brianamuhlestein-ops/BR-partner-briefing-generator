import type { RuntimeContext } from './types'

const API_BASE = '/api/v1/partner-briefing'

export type EmailBriefingKind = 'core' | 'tailored' | 'social'

export type EmailBriefingDocument<T extends object> = {
  briefing_kind: EmailBriefingKind
  document: T
  updated_at: string
}

type ApiItem<T> = {
  status: 'ok'
  item: T
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
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
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  const payload = await response.json() as ApiItem<EmailBriefingDocument<T>>
  return payload.item
}

export async function saveEmailBriefingDocument<T extends object>(
  briefingKind: EmailBriefingKind,
  document: T,
): Promise<EmailBriefingDocument<T>> {
  const response = await request<ApiItem<EmailBriefingDocument<T>>>(
    `/email-briefings/${briefingKind}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document }),
    },
  )
  return response.item
}
