export interface ReviewedSynopsis {
  review_id: string
  version: number
  text: string
  product_text: string
  reporting_start_utc: string
  reporting_end_utc: string
  reviewed_at_utc: string
  sha256: string
  runtime: { data_source: string; scenario: string | null }
}

export async function synopsisRequest(path: string, method = 'GET', body?: unknown, version?: number) {
  const response = await fetch(`/api/v1/space-weather-summary/${path}`, {
    method, headers: { 'Content-Type': 'application/json', ...(version !== undefined ? { 'If-Match': String(version) } : {}) },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  })
  const result = await response.json()
  if (!response.ok) throw new Error(result.description || result.error?.message || result.title || 'Synopsis request failed.')
  return result
}
