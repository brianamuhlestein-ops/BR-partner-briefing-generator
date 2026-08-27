import { describe, expect, it } from 'vitest'

import {
  COMPACT_UI_ENABLED,
  DEFAULT_UI_DENSITY,
  UI_DENSITY_STORAGE_KEY,
  initializeUiDensity,
  readUiDensity,
  setUiDensity,
} from './uiDensity'

function storage(initialValue: string | null = null) {
  let value = initialValue
  return {
    getItem: () => value,
    setItem: (_key: string, nextValue: string) => {
      value = nextValue
    },
    value: () => value,
  }
}

function densityRoot() {
  return { dataset: {} as { uiDensity?: string } }
}

describe('UI density preference', () => {
  it('defaults to comfortable when no preference is stored', () => {
    expect(COMPACT_UI_ENABLED).toBe(false)
    expect(readUiDensity(storage())).toBe(DEFAULT_UI_DENSITY)
  })

  it('rejects an invalid stored preference', () => {
    expect(readUiDensity(storage('oversized'))).toBe('comfortable')
  })

  it('ignores a saved compact preference while Compact is disabled', () => {
    const root = densityRoot()
    expect(initializeUiDensity(storage('compact'), root)).toBe('comfortable')
    expect(root.dataset.uiDensity).toBe('comfortable')
  })

  it('keeps Standard geometry when Compact is requested', () => {
    const memory = storage()
    const root = densityRoot()
    setUiDensity('compact', memory, root)
    expect(root.dataset.uiDensity).toBe('comfortable')
    expect(memory.value()).toBe('comfortable')
  })

  it('continues when storage access fails', () => {
    const failingStorage = {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('blocked')
      },
    }
    const root = densityRoot()

    expect(initializeUiDensity(failingStorage, root)).toBe('comfortable')
    expect(() => setUiDensity('compact', failingStorage, root)).not.toThrow()
    expect(root.dataset.uiDensity).toBe('comfortable')
  })

  it('uses the application-specific storage key', () => {
    expect(UI_DENSITY_STORAGE_KEY).toBe('swift-partner-briefing-ui-density')
  })
})
