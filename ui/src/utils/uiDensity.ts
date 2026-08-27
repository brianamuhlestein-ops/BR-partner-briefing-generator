export type UiDensity = 'comfortable' | 'compact'

export const UI_DENSITY_STORAGE_KEY = 'swift-partner-briefing-ui-density'
export const DEFAULT_UI_DENSITY: UiDensity = 'comfortable'
export const COMPACT_UI_ENABLED = false

type DensityStorage = Pick<Storage, 'getItem' | 'setItem'>
type DensityRoot = { dataset: { uiDensity?: string } }

export function isUiDensity(value: unknown): value is UiDensity {
  return value === 'comfortable' || value === 'compact'
}

function browserStorage(): DensityStorage | null {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

function documentRoot(): DensityRoot | null {
  return typeof document === 'undefined' ? null : document.documentElement
}

export function readUiDensity(storage: DensityStorage | null = browserStorage()): UiDensity {
  if (!COMPACT_UI_ENABLED) return DEFAULT_UI_DENSITY
  if (!storage) return DEFAULT_UI_DENSITY
  try {
    const stored = storage.getItem(UI_DENSITY_STORAGE_KEY)
    return isUiDensity(stored) ? stored : DEFAULT_UI_DENSITY
  } catch {
    return DEFAULT_UI_DENSITY
  }
}

export function applyUiDensity(
  density: UiDensity,
  root: DensityRoot | null = documentRoot(),
): UiDensity {
  const resolved = COMPACT_UI_ENABLED ? density : DEFAULT_UI_DENSITY
  if (root) root.dataset.uiDensity = resolved
  return resolved
}

export function persistUiDensity(
  density: UiDensity,
  storage: DensityStorage | null = browserStorage(),
): void {
  if (!storage) return
  try {
    storage.setItem(UI_DENSITY_STORAGE_KEY, COMPACT_UI_ENABLED ? density : DEFAULT_UI_DENSITY)
  } catch {
    // The current session still receives the selected density when storage is unavailable.
  }
}

export function initializeUiDensity(
  storage: DensityStorage | null = browserStorage(),
  root: DensityRoot | null = documentRoot(),
): UiDensity {
  return applyUiDensity(readUiDensity(storage), root)
}

export function setUiDensity(
  density: UiDensity,
  storage: DensityStorage | null = browserStorage(),
  root: DensityRoot | null = documentRoot(),
): UiDensity {
  const resolved = applyUiDensity(density, root)
  persistUiDensity(resolved, storage)
  return resolved
}
