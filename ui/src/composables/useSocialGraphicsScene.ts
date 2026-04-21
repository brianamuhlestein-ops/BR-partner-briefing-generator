import { computed, ref } from 'vue'

import {
  createSocialGraphicsDraft,
  exportSocialGraphic,
  fetchSocialGraphicsDraft,
  updateSocialGraphicsDraft,
} from '../api'
import {
  createSceneFromTemplate,
  getDefaultTemplateId,
  getGraphicsTemplateOptions,
  templateBelongsToMode,
} from '../socialGraphics/templates'
import type {
  GraphicsWorkspaceMode,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
  SocialGraphicsDraft,
  SocialGraphicsElement,
  SocialGraphicsExportResult,
  SocialGraphicsImageElement,
  SocialGraphicsScene,
  SocialGraphicsTemplateId,
} from '../types'

function cloneScene(scene: SocialGraphicsScene): SocialGraphicsScene {
  return JSON.parse(JSON.stringify(scene)) as SocialGraphicsScene
}

function clampDimension(value: number): number {
  return Number.isFinite(value) ? Math.max(1, Math.round(value)) : 1
}

function lastDraftKey(mode: GraphicsWorkspaceMode): string {
  return `partnerbrief-${mode}-graphics-last-draft`
}

function imageElementByRole(
  scene: SocialGraphicsScene,
  role: SocialGraphicsImageElement['assetRole'],
): SocialGraphicsImageElement | null {
  return (
    scene.elements.find(
      (element): element is SocialGraphicsImageElement =>
        element.kind === 'image' && element.assetRole === role,
    ) ?? null
  )
}

export function useSocialGraphicsScene(mode: GraphicsWorkspaceMode) {
  const defaultTemplateId = getDefaultTemplateId(mode)
  const templateId = ref<SocialGraphicsTemplateId>(defaultTemplateId)
  const scene = ref<SocialGraphicsScene>(createSceneFromTemplate(defaultTemplateId))
  const selectedElementId = ref<string | null>(null)
  const draftId = ref<string | null>(null)
  const saveStatus = ref('Working locally')
  const exportResult = ref<SocialGraphicsExportResult | null>(null)
  const busy = ref(false)
  const errorMessage = ref('')

  const templateOptions = getGraphicsTemplateOptions(mode)

  const selectedElement = computed(() => {
    return scene.value.elements.find((element) => element.id === selectedElementId.value) ?? null
  })

  function setScene(nextScene: SocialGraphicsScene) {
    scene.value = cloneScene(nextScene)
    templateId.value = nextScene.templateId
    selectedElementId.value = nextScene.elements.find((element) => element.visible)?.id ?? null
  }

  function applyTemplate(nextTemplateId: SocialGraphicsTemplateId) {
    exportResult.value = null
    saveStatus.value = 'Working locally'
    setScene(createSceneFromTemplate(nextTemplateId))
  }

  function startFreshFromTemplate(nextTemplateId: SocialGraphicsTemplateId) {
    draftId.value = null
    exportResult.value = null
    errorMessage.value = ''
    saveStatus.value = 'Prepared from Ops to Comms recommendation'
    setScene(createSceneFromTemplate(nextTemplateId))
  }

  function resetTemplate() {
    applyTemplate(templateId.value)
  }

  function selectElement(elementId: string | null) {
    selectedElementId.value = elementId
  }

  function updateElement(elementId: string, patch: Partial<SocialGraphicsElement>) {
    const element = scene.value.elements.find((entry) => entry.id === elementId)
    if (!element) {
      return
    }

    Object.assign(element, patch)

    if ('width' in patch && typeof patch.width === 'number') {
      element.width = clampDimension(patch.width)
    }
    if ('height' in patch && typeof patch.height === 'number') {
      element.height = clampDimension(patch.height)
    }
    if (element.kind === 'text' && 'fontSize' in patch && typeof patch.fontSize === 'number') {
      element.fontSize = clampDimension(patch.fontSize)
    }
    if (element.kind === 'line' && 'strokeWidth' in patch && typeof patch.strokeWidth === 'number') {
      element.strokeWidth = clampDimension(patch.strokeWidth)
    }
  }

  function replaceImageSource(elementId: string, src: string) {
    const element = scene.value.elements.find((entry) => entry.id === elementId)
    if (!element || element.kind !== 'image') {
      return
    }
    element.src = src
    element.linkedAssetId = null
  }

  function resolveAssetTarget(
    preferredTarget: SocialGraphicsAssetApplyTarget,
  ): SocialGraphicsImageElement | null {
    if (preferredTarget === 'selected-image') {
      const selected = scene.value.elements.find(
        (element): element is SocialGraphicsImageElement =>
          element.id === selectedElementId.value && element.kind === 'image',
      )
      return selected ?? null
    }

    const targetRoleMap: Record<
      Exclude<SocialGraphicsAssetApplyTarget, 'selected-image'>,
      SocialGraphicsImageElement['assetRole']
    > = {
      background: 'background',
      logo: 'logo',
      'main-image': 'main-image',
      'secondary-image': 'secondary-image',
      'icon-slot': 'icon-slot',
    }

    return imageElementByRole(scene.value, targetRoleMap[preferredTarget])
  }

  function applyAssetToScene(
    asset: SocialGraphicsAsset,
    preferredTarget: SocialGraphicsAssetApplyTarget = asset.defaultApplyTarget,
  ): boolean {
    const src = asset.localPath ?? asset.url
    if (!src) {
      errorMessage.value = 'This asset does not have a usable image source.'
      return false
    }

    const target =
      resolveAssetTarget(preferredTarget) ??
      resolveAssetTarget(asset.defaultApplyTarget) ??
      resolveAssetTarget('selected-image') ??
      imageElementByRole(scene.value, 'main-image') ??
      imageElementByRole(scene.value, 'secondary-image') ??
      imageElementByRole(scene.value, 'background') ??
      imageElementByRole(scene.value, 'logo')

    if (!target) {
      errorMessage.value = 'No compatible image slot is available in this template.'
      return false
    }

    target.src = src
    target.visible = true
    target.linkedAssetId = asset.id
    target.fit =
      target.assetRole === 'logo' || target.assetRole === 'icon-slot' || asset.assetType === 'icon' || asset.assetType === 'chart'
        ? 'contain'
        : asset.assetType === 'background'
          ? 'cover'
          : target.fit
    if (target.assetRole === 'background') {
      target.opacity = 0.94
      target.cornerRadius = 0
    }
    if (target.assetRole === 'logo') {
      target.cornerRadius = 0
    }

    selectedElementId.value = target.id
    exportResult.value = null
    errorMessage.value = ''
    saveStatus.value = `Applied asset ${asset.title}`
    return true
  }

  function toggleVisibility(elementId: string) {
    const element = scene.value.elements.find((entry) => entry.id === elementId)
    if (!element) {
      return
    }
    element.visible = !element.visible
  }

  function moveElement(elementId: string, direction: 'up' | 'down') {
    const index = scene.value.elements.findIndex((element) => element.id === elementId)
    if (index < 0) {
      return
    }

    const targetIndex = direction === 'up' ? index + 1 : index - 1
    if (targetIndex < 0 || targetIndex >= scene.value.elements.length) {
      return
    }

    const reordered = [...scene.value.elements]
    const [moved] = reordered.splice(index, 1)
    if (!moved) {
      return
    }
    reordered.splice(targetIndex, 0, moved)
    scene.value.elements = reordered
  }

  async function loadDraft() {
    const storedDraftId = window.localStorage.getItem(lastDraftKey(mode))
    if (!storedDraftId) {
      return
    }

    busy.value = true
    errorMessage.value = ''

    try {
      const draft = await fetchSocialGraphicsDraft(storedDraftId)
      if (!templateBelongsToMode(draft.template_id, mode)) {
        window.localStorage.removeItem(lastDraftKey(mode))
        return
      }

      draftId.value = draft.draft_id
      saveStatus.value = `Loaded draft ${draft.draft_id}`
      setScene(draft.scene)
    } catch {
      window.localStorage.removeItem(lastDraftKey(mode))
    } finally {
      busy.value = false
    }
  }

  async function saveDraft() {
    busy.value = true
    errorMessage.value = ''

    try {
      let draft: SocialGraphicsDraft
      if (draftId.value) {
        draft = await updateSocialGraphicsDraft(draftId.value, {
          template_id: templateId.value,
          scene: scene.value,
        })
      } else {
        draft = await createSocialGraphicsDraft({
          template_id: templateId.value,
          scene: scene.value,
        })
      }

      draftId.value = draft.draft_id
      templateId.value = draft.template_id
      scene.value = cloneScene(draft.scene)
      saveStatus.value = `Saved ${new Date(draft.updated_at).toLocaleString()}`
      window.localStorage.setItem(lastDraftKey(mode), draft.draft_id)
      return draft
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : 'Unable to save graphics draft.'
      throw error
    } finally {
      busy.value = false
    }
  }

  async function exportScene(basePng: string) {
    busy.value = true
    errorMessage.value = ''

    try {
      const result = await exportSocialGraphic({
        draft_id: draftId.value,
        template_id: templateId.value,
        scene: scene.value,
        base_png: basePng,
      })
      exportResult.value = result
      saveStatus.value = `Exported ${new Date(result.created_at).toLocaleString()}`
      return result
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : 'Unable to export graphic.'
      throw error
    } finally {
      busy.value = false
    }
  }

  return {
    templateId,
    templateOptions,
    scene,
    selectedElementId,
    selectedElement,
    draftId,
    saveStatus,
    exportResult,
    busy,
    errorMessage,
    applyTemplate,
    startFreshFromTemplate,
    resetTemplate,
    selectElement,
    updateElement,
    replaceImageSource,
    applyAssetToScene,
    toggleVisibility,
    moveElement,
    saveDraft,
    loadDraft,
    exportScene,
  }
}
