import type {
  BriefingDraft,
  BriefingTemplateResponse,
  BriefingType,
  ContextItem,
  PdfResponse,
  PreviewResponse,
  SectionValue,
  SocialGraphicsDraft,
  SocialGraphicsExportResult,
  SocialGraphicsScene,
  SocialGraphicsTemplateId,
} from './types'

const API_BASE = '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchBriefingTypes(): Promise<BriefingType[]> {
  const response = await request<{ items: BriefingType[] }>('/briefing-types')
  return response.items
}

export function fetchTemplate(briefingType: string): Promise<BriefingTemplateResponse> {
  return request(`/templates/${briefingType}`)
}

export function createDraft(payload: {
  briefing_type: string
  template_version: string
  sections?: Record<string, SectionValue>
}): Promise<BriefingDraft> {
  return request('/drafts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function updateDraft(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<BriefingDraft> {
  return request(`/drafts/${draftId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function generatePreview(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<PreviewResponse> {
  return request(`/drafts/${draftId}/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function generatePdf(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<PdfResponse> {
  return request(`/drafts/${draftId}/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function deriveDraft(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<object> {
  return request(`/drafts/${draftId}/derive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function fetchActiveAlerts(): Promise<ContextItem[]> {
  const response = await request<{ items: ContextItem[] }>('/context/alerts/active')
  return response.items
}

export async function fetchActiveIcaoAdvisories(): Promise<ContextItem[]> {
  const response = await request<{ items: ContextItem[] }>('/context/advisories/icao/active')
  return response.items
}

export function createSocialGraphicsDraft(payload: {
  template_id: SocialGraphicsTemplateId
  scene: SocialGraphicsScene
}): Promise<SocialGraphicsDraft> {
  return request('/social-graphics/drafts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function fetchSocialGraphicsDraft(draftId: string): Promise<SocialGraphicsDraft> {
  return request(`/social-graphics/drafts/${draftId}`)
}

export function updateSocialGraphicsDraft(
  draftId: string,
  payload: { template_id: SocialGraphicsTemplateId; scene: SocialGraphicsScene },
): Promise<SocialGraphicsDraft> {
  return request(`/social-graphics/drafts/${draftId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function exportSocialGraphic(payload: {
  draft_id: string | null
  template_id: SocialGraphicsTemplateId
  scene: SocialGraphicsScene
  base_png: string
}): Promise<SocialGraphicsExportResult> {
  return request('/social-graphics/exports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
