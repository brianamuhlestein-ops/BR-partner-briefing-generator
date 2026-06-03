<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

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

const educationOnlySocialTemplate: SocialGraphicsTemplateId = 'educational-slide'

const props = defineProps<{
  mode: GraphicsWorkspaceMode
  presentation?: 'default' | 'social-tab'
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

const availableTemplateOptions = computed(() => {
  if (props.mode === 'social' && props.recommendation?.communicationMode === 'education-outreach') {
    return templateOptions.filter((option) => option.id === educationOnlySocialTemplate)
  }

  return templateOptions
})

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
    startFreshFromTemplate(nextTemplate, value)
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
  <section class="social-graphics-workspace" :class="{ 'social-graphics-workspace--social-tab': presentation === 'social-tab' }">
    <div class="toolbar social-graphics-toolbar">
      <label>
        Starter Template
        <select :value="templateId" @change="handleTemplateChange">
          <option v-for="option in availableTemplateOptions" :key="option.id" :value="option.id">
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

    <div class="social-graphics-body" :class="{ 'social-graphics-body--social-tab': presentation === 'social-tab' }">
      <div class="social-graphics-main">
        <div class="social-graphics-canvas-panel">
          <SocialGraphicsStage
            ref="stageComponent"
            :scene="scene"
            :selected-element-id="selectedElementId"
            @select-element="selectElement"
            @update-element="updateElement"
          />
        </div>
      </div>

      <aside class="social-graphics-sidebar social-graphics-sidebar--controls">
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

        <SocialGraphicsExportPanel
          :draft-id="draftId"
          :save-status="saveStatus"
          :export-result="exportResult"
        />
      </aside>

      <aside class="social-graphics-sidebar social-graphics-sidebar--finder">
        <AssetFinderPanel
          :mode="mode"
          :recommendation="recommendation"
          :scene="scene"
          :selected-element-id="selectedElementId"
          @apply-asset="handleApplyAsset"
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

.social-graphics-workspace--social-tab {
  display: contents;
}

.social-graphics-toolbar {
  margin-bottom: 0;
  justify-content: flex-start;
}

.social-graphics-body {
  display: grid;
  grid-template-columns: minmax(0, 1240px) 320px minmax(420px, 1fr);
  gap: 16px;
  align-items: start;
  width: 100%;
}

.social-graphics-body--social-tab {
  display: contents;
}

.social-graphics-workspace--social-tab .social-graphics-main {
  grid-column: 2;
  grid-row: 1 / span 2;
  padding-top: 62px;
}

.social-graphics-workspace--social-tab .social-graphics-sidebar--finder {
  grid-column: 1;
  grid-row: 2;
}

.social-graphics-workspace--social-tab .social-graphics-sidebar--controls {
  grid-column: 2;
  grid-row: 3;
  width: 100%;
}

.social-graphics-workspace--social-tab .social-graphics-toolbar {
  grid-column: 2;
  grid-row: 1;
}

.social-graphics-workspace--social-tab .social-graphics-canvas-panel {
  max-width: 100%;
}

.social-graphics-main {
  min-width: 0;
}

.social-graphics-canvas-panel {
  min-width: 0;
  max-width: 1240px;
}

.social-graphics-sidebar {
  display: grid;
  gap: 16px;
  align-content: start;
}

.social-graphics-sidebar-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  align-items: start;
}

.social-graphics-sidebar--controls {
  width: 320px;
}

.social-graphics-sidebar--finder {
  width: 100%;
  min-width: 0;
}

@media (max-width: 1600px) {
  .social-graphics-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1300px) {
  .social-graphics-workspace--social-tab .social-graphics-toolbar,
  .social-graphics-workspace--social-tab .social-graphics-main,
  .social-graphics-workspace--social-tab .social-graphics-sidebar--finder,
  .social-graphics-workspace--social-tab .social-graphics-sidebar--controls {
    grid-column: 1;
    grid-row: auto;
  }

  .social-graphics-workspace--social-tab .social-graphics-main {
    padding-top: 0;
  }
}

@media (max-width: 960px) {
  .social-graphics-canvas-panel {
    max-width: 100%;
  }
}
</style>
