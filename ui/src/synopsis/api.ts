import type { ApiCollection, ApiItem, Bundle, BundleSummary, Draft, DraftSummary, Health } from "./types";

const ROOT = "/api/v1/space-weather-summary";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload?.error?.message || payload?.title || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return payload as T;
}

export function getHealth(): Promise<Health> {
  return request<Health>(`${ROOT}/health`);
}

export function listBundles(): Promise<ApiCollection<BundleSummary>> {
  return request<ApiCollection<BundleSummary>>(`${ROOT}/source-bundles?limit=50`);
}

export function getBundle(bundleId: string): Promise<ApiItem<Bundle>> {
  return request<ApiItem<Bundle>>(`${ROOT}/source-bundles/${encodeURIComponent(bundleId)}`);
}

export function createBundle(cutoffAtUtc: string | null): Promise<ApiItem<Bundle>> {
  return request<ApiItem<Bundle>>(`${ROOT}/source-bundles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...(cutoffAtUtc ? { cutoff_at_utc: cutoffAtUtc } : {}),
      actor_id: "summary-builder-ui",
      actor_type: "forecaster",
    }),
  });
}

export function listDrafts(): Promise<ApiCollection<DraftSummary>> {
  return request<ApiCollection<DraftSummary>>(`${ROOT}/drafts?limit=50`);
}

export function getDraft(draftId: string): Promise<ApiItem<Draft>> {
  return request<ApiItem<Draft>>(`${ROOT}/drafts/${encodeURIComponent(draftId)}`);
}

export function createDraft(bundleId: string): Promise<ApiItem<Draft>> {
  return request<ApiItem<Draft>>(`${ROOT}/drafts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bundle_id: bundleId,
      actor_id: "summary-builder-ui",
      actor_type: "forecaster",
    }),
  });
}
