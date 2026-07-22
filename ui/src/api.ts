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
  RuntimeContext,
} from './types'

const API_BASE = '/api/v1/partner-briefing'

type ApiCollection<T> = {
  status: 'ok'
  items: T[]
  total: number
}

type ApiItem<T> = {
  status: 'ok'
  item: T
}

type ApiResult<T> = {
  status: 'ok'
  result: T
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchBriefingTypes(): Promise<BriefingType[]> {
  const response = await request<ApiCollection<BriefingType>>('/briefing-types')
  return response.items
}

export async function fetchRuntimeNow(): Promise<RuntimeContext> {
  return request<RuntimeContext>('/now', { cache: 'no-store' })
}

export async function fetchTemplate(briefingType: string): Promise<BriefingTemplateResponse> {
  const response = await request<ApiItem<BriefingTemplateResponse>>(`/templates/${briefingType}`)
  return response.item
}

export async function createDraft(payload: {
  briefing_type: string
  template_version: string
  sections?: Record<string, SectionValue>
  issue_time_utc?: string
}): Promise<BriefingDraft> {
  const response = await request<ApiItem<BriefingDraft>>('/drafts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.item
}

export async function updateDraft(
  draftId: string,
  payload: { sections: Record<string, SectionValue>; issue_time_utc?: string },
): Promise<BriefingDraft> {
  const response = await request<ApiItem<BriefingDraft>>(`/drafts/${draftId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.item
}

export async function generatePreview(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<PreviewResponse> {
  const response = await request<ApiResult<PreviewResponse>>(`/drafts/${draftId}/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.result
}

export async function generatePdf(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<PdfResponse> {
  const response = await request<ApiResult<PdfResponse>>(`/drafts/${draftId}/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.result
}

export async function deriveDraft(
  draftId: string,
  payload: { sections: Record<string, SectionValue> },
): Promise<object> {
  const response = await request<ApiResult<object>>(`/drafts/${draftId}/derive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.result
}

export async function fetchActiveAlerts(): Promise<ContextItem[]> {
  const response = await request<ApiCollection<ContextItem>>('/context/alerts/active')
  return response.items
}

export async function fetchActiveIcaoAdvisories(): Promise<ContextItem[]> {
  const response = await request<ApiCollection<ContextItem>>('/context/advisories/icao/active')
  return response.items
}

export async function createSocialGraphicsDraft(payload: {
  template_id: SocialGraphicsTemplateId
  scene: SocialGraphicsScene
}): Promise<SocialGraphicsDraft> {
  const response = await request<ApiItem<SocialGraphicsDraft>>('/social-graphics/drafts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.item
}

export async function fetchSocialGraphicsDraft(draftId: string): Promise<SocialGraphicsDraft> {
  const response = await request<ApiItem<SocialGraphicsDraft>>(`/social-graphics/drafts/${draftId}`)
  return response.item
}

export async function updateSocialGraphicsDraft(
  draftId: string,
  payload: { template_id: SocialGraphicsTemplateId; scene: SocialGraphicsScene },
): Promise<SocialGraphicsDraft> {
  const response = await request<ApiItem<SocialGraphicsDraft>>(`/social-graphics/drafts/${draftId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.item
}

export async function exportSocialGraphic(payload: {
  draft_id: string | null
  template_id: SocialGraphicsTemplateId
  scene: SocialGraphicsScene
  base_png: string
}): Promise<SocialGraphicsExportResult> {
  const response = await request<ApiResult<SocialGraphicsExportResult>>('/social-graphics/exports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return response.result
}
