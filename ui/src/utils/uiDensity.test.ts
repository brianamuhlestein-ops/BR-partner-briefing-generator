import { describe, expect, it } from 'vitest'

import {
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
    expect(readUiDensity(storage())).toBe(DEFAULT_UI_DENSITY)
  })

  it('rejects an invalid stored preference', () => {
    expect(readUiDensity(storage('oversized'))).toBe('comfortable')
  })

  it('applies a valid saved preference before mount', () => {
    const root = densityRoot()
    expect(initializeUiDensity(storage('compact'), root)).toBe('compact')
    expect(root.dataset.uiDensity).toBe('compact')
  })

  it('applies and persists a density change', () => {
    const memory = storage()
    const root = densityRoot()
    setUiDensity('compact', memory, root)
    expect(root.dataset.uiDensity).toBe('compact')
    expect(memory.value()).toBe('compact')
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
    expect(root.dataset.uiDensity).toBe('compact')
  })

  it('uses the application-specific storage key', () => {
    expect(UI_DENSITY_STORAGE_KEY).toBe('swift-partner-briefing-ui-density')
  })
})
