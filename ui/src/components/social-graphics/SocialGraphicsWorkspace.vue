<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { useSocialGraphicsScene } from '../../composables/useSocialGraphicsScene'
import type {
  GraphicsWorkspaceMode,
  OpsToCommsPathId,
  OpsToCommsRecommendation,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
  SocialGraphicsTemplateId,
} from '../../types'
import AssetFinderPanel from './AssetFinderPanel.vue'
import SocialGraphicsExportPanel from './SocialGraphicsExportPanel.vue'
import SocialGraphicsInspector from './SocialGraphicsInspector.vue'
import SocialGraphicsLayersPanel from './SocialGraphicsLayersPanel.vue'
import SocialGraphicsStage from './SocialGraphicsStage.vue'

const props = defineProps<{
  mode: GraphicsWorkspaceMode
  recommendation?: OpsToCommsRecommendation | null
}>()

const emit = defineEmits<{
  'recommendation-applied': []
}>()

const stageComponent = ref<InstanceType<typeof SocialGraphicsStage> | null>(null)
const hasAppliedRecommendation = ref(false)

const {
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
} = useSocialGraphicsScene(props.mode)

function pathForMode(mode: GraphicsWorkspaceMode): OpsToCommsPathId {
  return mode === 'social' ? 'social-design-review' : 'partner-design-review'
}

function recommendedTemplateForMode(
  recommendation: OpsToCommsRecommendation | null | undefined,
): SocialGraphicsTemplateId | null {
  if (!recommendation) {
    return null
  }

  return recommendation.recommendedPathTemplates[pathForMode(props.mode)] ?? null
}

function handleTemplateChange(event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) {
    return
  }
  applyTemplate(target.value as SocialGraphicsTemplateId)
}

async function handleSaveDraft() {
  await saveDraft()
}

async function handleExport() {
  const png = stageComponent.value?.toDataURL()
  if (!png) {
    return
  }

  if (!draftId.value) {
    await saveDraft()
  }
  await exportScene(png)
}

function handleApplyAsset(asset: SocialGraphicsAsset, target: SocialGraphicsAssetApplyTarget) {
  applyAssetToScene(asset, target)
}

watch(
  () => props.recommendation,
  (value) => {
    const nextTemplate = recommendedTemplateForMode(value)
    if (!nextTemplate) {
      return
    }
    hasAppliedRecommendation.value = true
    startFreshFromTemplate(nextTemplate)
    emit('recommendation-applied')
  },
  { immediate: true },
)

onMounted(async () => {
  if (!hasAppliedRecommendation.value) {
    await loadDraft()
  }
})
</script>

<template>
  <section class="social-graphics-workspace">
    <div class="toolbar social-graphics-toolbar">
      <label>
        Starter Template
        <select :value="templateId" @change="handleTemplateChange">
          <option v-for="option in templateOptions" :key="option.id" :value="option.id">
            {{ option.label }}
          </option>
        </select>
      </label>

      <div class="toolbar-actions">
        <button type="button" :disabled="busy" @click="resetTemplate">Reset Template</button>
        <button type="button" :disabled="busy" @click="handleSaveDraft">Save Draft</button>
        <button type="button" :disabled="busy" @click="handleExport">Export Graphic</button>
      </div>
    </div>

    <p v-if="errorMessage" class="message workspace-alert error">{{ errorMessage }}</p>

    <div class="social-graphics-body">
      <div class="social-graphics-canvas-panel">
        <SocialGraphicsStage
          ref="stageComponent"
          :scene="scene"
          :selected-element-id="selectedElementId"
          @select-element="selectElement"
          @update-element="updateElement"
        />
      </div>

      <aside class="social-graphics-sidebar">
        <div class="social-graphics-sidebar-grid">
          <SocialGraphicsLayersPanel
            :scene="scene"
            :selected-element-id="selectedElementId"
            @select="selectElement"
            @toggle="toggleVisibility"
            @move="moveElement"
          />

          <SocialGraphicsInspector
            :element="selectedElement"
            @update="updateElement"
            @replace-image="replaceImageSource"
          />
        </div>

        <AssetFinderPanel
          :mode="mode"
          :recommendation="recommendation"
          :scene="scene"
          :selected-element-id="selectedElementId"
          @apply-asset="handleApplyAsset"
        />

        <SocialGraphicsExportPanel
          :draft-id="draftId"
          :save-status="saveStatus"
          :export-result="exportResult"
        />
      </aside>
    </div>
  </section>
</template>

<style scoped>
.social-graphics-workspace {
  display: grid;
  gap: 12px;
}

.social-graphics-toolbar {
  margin-bottom: 0;
  justify-content: flex-start;
}

.social-graphics-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 680px;
  gap: 16px;
  align-items: start;
}

.social-graphics-canvas-panel {
  min-width: 0;
}

.social-graphics-sidebar {
  display: grid;
  gap: 16px;
}

.social-graphics-sidebar-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

@media (max-width: 1600px) {
  .social-graphics-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .social-graphics-sidebar-grid {
    grid-template-columns: 1fr;
  }
}
</style>
