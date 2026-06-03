import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

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
  OpsToCommsRecommendation,
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

const retiredSeedAssetIds = new Set([
  'aurora-ribbon-visual',
  'hazard-explainer-icon',
  'ops-grid-background',
])

const retiredSeedAssetSrcs = new Set([
  '/assets/visual-finder/aurora-ribbon-visual.svg',
  '/assets/visual-finder/hazard-explainer-icon.svg',
  '/assets/visual-finder/ops-grid-background.svg',
  '/NOAA_logo.png',
])

function clampDimension(value: number): number {
  return Number.isFinite(value) ? Math.max(1, Math.round(value)) : 1
}

const templateLayoutPinnedElementIds = new Set([
  'feature-block',
  'feature-rule-left',
  'feature-rule-right',
  'feature-label',
  'education-graphic',
  'main-image-placeholder',
  'education-title',
  'right-panel',
  'topic-kicker',
  'topic-title',
  'topic-subtitle',
  'content-divider',
  'meaning-title',
  'meaning-copy',
  'why-title',
  'why-copy',
  'sectors-divider',
  'sectors-title',
  'sector-icon-1',
  'sector-icon-2',
  'sector-icon-3',
  'sector-icon-4',
  'sector-row-1',
  'sector-row-2',
  'sector-row-3',
  'sector-row-4',
  'footer-rule',
  'resource-line-1',
  'resource-line-2',
  'resource-line-3',
  'noaa-brand-lockup',
  'nws-brand-lockup',
])

const templateManagedTextElementIds = new Set([
  'resource-line-1',
  'resource-line-2',
  'resource-line-3',
])

function shouldPreserveTemplateLayout(element: SocialGraphicsElement): boolean {
  return Boolean(element.locked) || templateLayoutPinnedElementIds.has(element.id)
}

function rebaseSceneOntoCurrentTemplate(sourceScene: SocialGraphicsScene): SocialGraphicsScene {
  const rebasedScene = createSceneFromTemplate(sourceScene.templateId)
  const sourceElements = new Map(sourceScene.elements.map((element) => [element.id, element]))

  rebasedScene.elements = rebasedScene.elements.map((templateElement) => {
    const sourceElement = sourceElements.get(templateElement.id)
    if (!sourceElement || sourceElement.kind !== templateElement.kind) {
      return templateElement
    }

    const preserveTemplateLayout = shouldPreserveTemplateLayout(templateElement)

    if (preserveTemplateLayout) {
      if (templateElement.kind === 'text' && sourceElement.kind === 'text') {
        return {
          ...templateElement,
          text: templateManagedTextElementIds.has(templateElement.id)
            ? templateElement.text
            : sourceElement.text,
          visible: sourceElement.visible,
          opacity: sourceElement.opacity,
        }
      }

      if (templateElement.kind === 'image' && sourceElement.kind === 'image') {
        return {
          ...templateElement,
          src: sourceElement.src,
          fit: sourceElement.fit,
          cornerRadius: sourceElement.cornerRadius,
          linkedAssetId: sourceElement.linkedAssetId,
          visible: sourceElement.visible,
          opacity: sourceElement.opacity,
        }
      }

      if (templateElement.kind === 'rect' && sourceElement.kind === 'rect') {
        return {
          ...templateElement,
          visible: sourceElement.visible,
          opacity: sourceElement.opacity,
        }
      }

      if (templateElement.kind === 'line' && sourceElement.kind === 'line') {
        return {
          ...templateElement,
          visible: sourceElement.visible,
          opacity: sourceElement.opacity,
        }
      }
    }

    const merged: SocialGraphicsElement = {
      ...templateElement,
      x: preserveTemplateLayout ? templateElement.x : sourceElement.x,
      y: preserveTemplateLayout ? templateElement.y : sourceElement.y,
      width: preserveTemplateLayout ? templateElement.width : sourceElement.width,
      height: preserveTemplateLayout ? templateElement.height : sourceElement.height,
      visible: sourceElement.visible,
      opacity: sourceElement.opacity,
    }

    if (templateElement.kind === 'text' && sourceElement.kind === 'text') {
      return {
        ...merged,
        text: sourceElement.text,
        fill: sourceElement.fill,
        fontFamily: sourceElement.fontFamily,
        fontSize: sourceElement.fontSize,
        fontWeight: sourceElement.fontWeight,
        align: sourceElement.align,
        lineHeight: sourceElement.lineHeight,
      }
    }

    if (templateElement.kind === 'image' && sourceElement.kind === 'image') {
      return {
        ...merged,
        src: sourceElement.src,
        fit: sourceElement.fit,
        cornerRadius: sourceElement.cornerRadius,
        linkedAssetId: sourceElement.linkedAssetId,
      }
    }

    if (templateElement.kind === 'rect' && sourceElement.kind === 'rect') {
      return {
        ...merged,
        fill: sourceElement.fill,
        cornerRadius: sourceElement.cornerRadius,
      }
    }

    if (templateElement.kind === 'line' && sourceElement.kind === 'line') {
      return {
        ...merged,
        stroke: sourceElement.stroke,
        strokeWidth: sourceElement.strokeWidth,
      }
    }

    return templateElement
  })

  return rebasedScene
}

function isEditableElement(element: SocialGraphicsElement): boolean {
  return !element.locked
}

function lastDraftKey(mode: GraphicsWorkspaceMode): string {
  return `partnerbrief-${mode}-graphics-last-draft`
}

function localSceneKey(mode: GraphicsWorkspaceMode): string {
  return `partnerbrief-${mode}-graphics-scene`
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

function formatEventLabel(value: OpsToCommsRecommendation['eventType']): string {
  if (value === 'cme') {
    return 'Coronal Mass Ejection'
  }
  return value
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function formatSectorLabel(value: OpsToCommsRecommendation['impactedSectors'][number]): string {
  switch (value) {
    case 'gnss-positioning':
      return 'GNSS / positioning'
    case 'power-grid':
      return 'Power grid'
    case 'human-spaceflight':
      return 'Human spaceflight'
    case 'public-aurora':
      return 'Public / aurora'
    case 'government-emergency-management':
      return 'Government / emergency management'
    default:
      return value
        .split('-')
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ')
  }
}

function formatUpdatedTimestamp(date: Date): string {
  const month = date.toLocaleString('en-US', { month: 'short' })
  const day = date.toLocaleString('en-US', { day: 'numeric' })
  const year = date.toLocaleString('en-US', { year: 'numeric' })
  const time = date.toLocaleString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZoneName: 'short',
  })
  return `${month} ${day}, ${year} ${time}`
}

function textElementById(scene: SocialGraphicsScene, id: string) {
  return scene.elements.find(
    (element): element is Extract<SocialGraphicsElement, { kind: 'text' }> =>
      element.id === id && element.kind === 'text',
  ) ?? null
}

function elementById(scene: SocialGraphicsScene, id: string) {
  return scene.elements.find((element) => element.id === id) ?? null
}

function placeholderIdForImageRole(
  role: SocialGraphicsImageElement['assetRole'] | undefined,
): string | null {
  switch (role) {
    case 'main-image':
    case 'secondary-image':
      return 'main-image-placeholder'
    case 'icon-slot':
      return 'icon-slot-placeholder'
    default:
      return null
  }
}

function syncImagePlaceholderVisibility(
  targetScene: SocialGraphicsScene,
  imageElement: SocialGraphicsImageElement,
) {
  const placeholderId = placeholderIdForImageRole(imageElement.assetRole)
  if (!placeholderId) {
    return
  }

  const placeholder = textElementById(targetScene, placeholderId)
  if (!placeholder) {
    return
  }

  placeholder.visible = !Boolean(imageElement.src)
}

function applyRecommendationContent(
  targetScene: SocialGraphicsScene,
  recommendation: OpsToCommsRecommendation | null | undefined,
) {
  if (!recommendation) {
    return
  }

  const eventLabel = formatEventLabel(recommendation.eventType)

  if (targetScene.templateId === 'educational-slide') {
    const title = textElementById(targetScene, 'education-title')
    const topicTitle = textElementById(targetScene, 'topic-title')
    const topicSubtitle = textElementById(targetScene, 'topic-subtitle')
    const meaningTitle = textElementById(targetScene, 'meaning-title')
    const meaningCopy = textElementById(targetScene, 'meaning-copy')
    const whyTitle = textElementById(targetScene, 'why-title')
    const whyCopy = textElementById(targetScene, 'why-copy')
    const sectorsTitle = textElementById(targetScene, 'sectors-title')
    const resourceLine1 = textElementById(targetScene, 'resource-line-1')
    const resourceLine2 = textElementById(targetScene, 'resource-line-2')
    const resourceLine3 = textElementById(targetScene, 'resource-line-3')

    if (title) {
      title.text = recommendation.eventType === 'cme' ? 'What is a Coronal Mass Ejection?' : `What is ${eventLabel}?`
    }
    if (topicTitle) {
      topicTitle.text = recommendation.eventType === 'cme' ? 'Coronal Mass Ejection (CME)' : eventLabel
    }
    if (topicSubtitle) {
      topicSubtitle.text =
        recommendation.selectedActionsToTakeText
          ? `Use the top-right space for the topic framing while the right columns explain what it is, why it matters, and what action is useful now.`
          : 'Use the top-right space for the topic framing while the right columns explain what it is and why it matters.'
    }
    if (meaningTitle) {
      meaningTitle.text = 'What it is:'
    }
    if (meaningCopy) {
      meaningCopy.text = recommendation.selectedWhatItIsText
    }
    if (whyTitle) {
      whyTitle.text = 'Why it matters:'
    }
    if (whyCopy) {
      whyCopy.text = recommendation.selectedWhyItMattersText
    }
    if (sectorsTitle) {
      sectorsTitle.text = 'Sectors at Risk:'
    }
    const sectorLabels = recommendation.impactedSectors.map(formatSectorLabel)
    for (let index = 0; index < 4; index += 1) {
      const row = textElementById(targetScene, `sector-row-${index + 1}`)
      const icon = elementById(targetScene, `sector-icon-${index + 1}`)
      const label = sectorLabels[index]
      if (row) {
        row.text = label ?? ''
        row.visible = Boolean(label)
      }
      if (icon) {
        icon.visible = Boolean(label)
      }
    }
    if (resourceLine1) {
      resourceLine1.text = 'swpc.noaa.gov'
    }
    if (resourceLine2) {
      resourceLine2.text = 'Space Weather Prediction Center • Boulder, CO'
    }
    if (resourceLine3) {
      resourceLine3.text = `Updated: ${formatUpdatedTimestamp(new Date())}`
    }
  }

  if (targetScene.templateId === 'informed-design-event') {
    const title = textElementById(targetScene, 'title')
    const impactCopy = textElementById(targetScene, 'impact-copy')
    const actionsCopy = textElementById(targetScene, 'actions-copy')

    if (title) {
      title.text = `${eventLabel} Communication Graphic`
    }
    if (impactCopy) {
      impactCopy.text = recommendation.selectedWhatItIsText
    }
    if (recommendation.selectedActionsToTakeText) {
      if (actionsCopy) {
        actionsCopy.text = recommendation.selectedActionsToTakeText
      }
    } else if (actionsCopy) {
      actionsCopy.text = recommendation.selectedWhyItMattersText
    }
  }
}

function sanitizeSeededImages(targetScene: SocialGraphicsScene) {
  for (const element of targetScene.elements) {
    if (element.kind !== 'image') {
      continue
    }

    const isRetiredSeedImage =
      (element.linkedAssetId !== undefined && retiredSeedAssetIds.has(element.linkedAssetId ?? '')) ||
      retiredSeedAssetSrcs.has(element.src)

    if (!isRetiredSeedImage) {
      syncImagePlaceholderVisibility(targetScene, element)
      continue
    }

    if (element.assetRole === 'logo' && element.linkedAssetId === 'noaa-brand-mark') {
      continue
    }

    element.src = ''
    element.linkedAssetId = null
    syncImagePlaceholderVisibility(targetScene, element)
  }
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

  watch(
    scene,
    () => {
      persistLocalScene()
    },
    { deep: true },
  )

  function persistLocalScene() {
    if (typeof window === 'undefined') {
      return
    }

    window.localStorage.setItem(localSceneKey(mode), JSON.stringify(scene.value))
  }

  function setScene(nextScene: SocialGraphicsScene) {
    scene.value = cloneScene(nextScene)
    templateId.value = nextScene.templateId
    selectedElementId.value =
      nextScene.elements.find((element) => element.visible && isEditableElement(element))?.id ?? null
    persistLocalScene()
  }

  function applyTemplate(nextTemplateId: SocialGraphicsTemplateId) {
    exportResult.value = null
    saveStatus.value = 'Working locally'
    setScene(createSceneFromTemplate(nextTemplateId))
  }

  function startFreshFromTemplate(
    nextTemplateId: SocialGraphicsTemplateId,
    recommendation?: OpsToCommsRecommendation | null,
  ) {
    draftId.value = null
    exportResult.value = null
    errorMessage.value = ''
    saveStatus.value = 'Prepared from Ops to Comms recommendation'
    const nextScene = createSceneFromTemplate(nextTemplateId)
    applyRecommendationContent(nextScene, recommendation)
    setScene(nextScene)
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

    persistLocalScene()
  }

  function replaceImageSource(elementId: string, src: string) {
    const element = scene.value.elements.find((entry) => entry.id === elementId)
    if (!element || element.kind !== 'image') {
      return
    }
    element.src = src
    element.linkedAssetId = null
    syncImagePlaceholderVisibility(scene.value, element)
    persistLocalScene()
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

    syncImagePlaceholderVisibility(scene.value, target)

    selectedElementId.value = target.id
    exportResult.value = null
    errorMessage.value = ''
    saveStatus.value = `Applied asset ${asset.title}`
    persistLocalScene()
    return true
  }

  function toggleVisibility(elementId: string) {
    const element = scene.value.elements.find((entry) => entry.id === elementId)
    if (!element) {
      return
    }
    element.visible = !element.visible
    persistLocalScene()
  }

  function moveElement(elementId: string, direction: 'up' | 'down') {
    const index = scene.value.elements.findIndex((element) => element.id === elementId)
    if (index < 0) {
      return
    }

    const step = direction === 'up' ? 1 : -1
    let targetIndex = index + step

    while (targetIndex >= 0 && targetIndex < scene.value.elements.length) {
      const candidate = scene.value.elements[targetIndex]
      if (candidate && isEditableElement(candidate)) {
        break
      }
      targetIndex += step
    }

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
    persistLocalScene()
  }

  function persistOnUnload() {
    persistLocalScene()
  }

  onMounted(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('pagehide', persistOnUnload)
      window.addEventListener('beforeunload', persistOnUnload)
    }
  })

  onBeforeUnmount(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('pagehide', persistOnUnload)
      window.removeEventListener('beforeunload', persistOnUnload)
    }
  })

  async function loadDraft() {
    if (typeof window !== 'undefined') {
      const storedScene = window.localStorage.getItem(localSceneKey(mode))
      if (storedScene) {
        try {
          const parsed = JSON.parse(storedScene) as SocialGraphicsScene
          if (templateBelongsToMode(parsed.templateId, mode)) {
            const rebasedScene = rebaseSceneOntoCurrentTemplate(parsed)
            sanitizeSeededImages(rebasedScene)
            saveStatus.value = 'Restored local workspace'
            setScene(rebasedScene)
            return
          }
        } catch {
          window.localStorage.removeItem(localSceneKey(mode))
        }
      }
    }

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

      const rebasedScene = rebaseSceneOntoCurrentTemplate(draft.scene)
      sanitizeSeededImages(rebasedScene)

      draftId.value = draft.draft_id
      saveStatus.value = `Loaded draft ${draft.draft_id}`
      setScene(rebasedScene)
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
