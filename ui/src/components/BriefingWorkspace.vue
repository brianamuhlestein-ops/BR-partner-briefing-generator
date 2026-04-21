<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import {
  createDraft,
  fetchActiveAlerts,
  fetchActiveIcaoAdvisories,
  fetchBriefingTypes,
  updateDraft,
} from '../api'
import type {
  BriefingDraft,
  BriefingTemplate,
  BriefingType,
  ContextItem,
  DerivedOutputStatus,
  DownstreamOutputId,
  OpsToCommsPathId,
  OpsToCommsRecommendation,
  SectionValue,
  TemplateSection,
  WorkspaceTypeId,
} from '../types'
import ContextPanel from './ContextPanel.vue'
import OpsToCommsWorkspace from './ops-to-comms/OpsToCommsWorkspace.vue'
import PartnerBriefing from './PartnerBriefing.vue'
import PreviewPanel from './PreviewPanel.vue'
import SchemaForm from './SchemaForm.vue'
import SocialGraphicsWorkspace from './social-graphics/SocialGraphicsWorkspace.vue'

const legacySchemas: Record<string, string[]> = {
  master: [
    'Solar Activity - 24 hr Summary Discussion',
    'Solar Activity - Probability Table',
    'Solar Activity - Forecast Rationale',
    'Energetic Particles - 24 hr Summary Discussion',
    'Energetic Particles - Probability Table',
    'Energetic Particles - Forecast Rationale',
    'Solar Wind - 24 hr Summary Discussion',
    'Solar Wind - Forecast Rationale',
    'Ionosphere - 24 hr Summary Discussion',
    'Geospace - 24 hr Summary Discussion',
    'Geospace - Probability Table',
    'Geospace - Forecast Rationale',
    'Operational Notes',
  ],
  discussion: [
    'Solar Activity - 24 hr Summary Discussion',
    'Solar Activity - Probability Table',
    'Solar Activity - Forecast Rationale',
    'Energetic Particles - 24 hr Summary Discussion',
    'Energetic Particles - Probability Table',
    'Energetic Particles - Forecast Rationale',
    'Solar Wind - 24 hr Summary Discussion',
    'Solar Wind - Forecast Rationale',
    'Geospace - 24 hr Summary Discussion',
    'Geospace - Probability Table',
    'Geospace - Forecast Rationale',
  ],
  icao: [
    'Solar Activity - 24 hr Summary Discussion',
    'Solar Activity - Probability Table',
    'Solar Activity - Forecast Rationale',
    'Energetic Particles - 24 hr Summary Discussion',
    'Energetic Particles - Probability Table',
    'Energetic Particles - Forecast Rationale',
    'Solar Wind - 24 hr Summary Discussion',
    'Solar Wind - Forecast Rationale',
    'Ionosphere - 24 hr Summary Discussion',
    'Geospace - 24 hr Summary Discussion',
    'Geospace - Probability Table',
    'Geospace - Forecast Rationale',
  ],
  staff: [
    'Solar Activity - Probability Table',
    'Solar Activity - Forecast Rationale',
    'Energetic Particles - Probability Table',
    'Energetic Particles - Forecast Rationale',
    'Solar Wind - Forecast Rationale',
    'Geospace - Probability Table',
    'Geospace - Forecast Rationale',
    'Operational Notes',
  ],
}

const workspaceBriefingTypes: BriefingType[] = [
  { id: 'master', label: 'Master' },
  { id: 'partner', label: 'I&R Awareness' },
  { id: 'ops-to-comms', label: 'Ops to Comms' },
  { id: 'social-graphic', label: 'Social Media Design Review' },
  { id: 'single-briefing-graphic', label: 'Partner Graphic Design Review' },
]

const downstreamProducts: { id: DownstreamOutputId; label: string }[] = [
  { id: 'discussion', label: 'Discussion' },
  { id: 'icao', label: 'ICAO' },
  { id: 'staff', label: 'Staff' },
]

function slugifySectionId(label: string): string {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}

function probabilityCategories(label: string): string[] {
  const normalized = label.toLowerCase()
  if (normalized.includes('solar activity')) {
    return ['R1-R2', 'R3+']
  }
  if (normalized.includes('energetic')) {
    return ['S1-S2', 'S3+']
  }
  if (normalized.includes('solar wind') || normalized.includes('geospace')) {
    return ['G1-G2', 'G3+']
  }
  return ['R1-R2', 'R3+']
}

function buildLegacyTemplate(briefingType: string): BriefingTemplate {
  const sectionLabels = legacySchemas[briefingType] ?? []
  const sections: TemplateSection[] = sectionLabels.map((label) => {
    if (label.toLowerCase().includes('probability table')) {
      return {
        id: slugifySectionId(label),
        label,
        kind: 'probability_table',
        categories: probabilityCategories(label),
        days: ['Day 1', 'Day 2', 'Day 3'],
      }
    }

    return {
      id: slugifySectionId(label),
      label,
      kind: 'text',
    }
  })

  return {
    briefing_type: briefingType,
    title: `${briefingType.charAt(0).toUpperCase()}${briefingType.slice(1)} Briefing`,
    sections,
  }
}

function createLocalDraft(briefingType: string): BriefingDraft {
  return {
    draft_id: `local-${briefingType}`,
    briefing_type: briefingType,
    template_version: 'legacy-ui',
    sections: {},
    status: 'draft',
  }
}

function isLocalDraft(draftId: string): boolean {
  return draftId.startsWith('local-')
}

function hasSectionContent(value: SectionValue | undefined): boolean {
  if (!value) {
    return false
  }

  if (typeof value === 'string') {
    return value.trim().length > 0
  }

  return Object.values(value).some((category) =>
    Object.values(category).some((cell) => cell.trim().length > 0),
  )
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderProbabilityTable(section: TemplateSection, value: SectionValue | undefined): string {
  const tableValue = typeof value === 'string' || !value ? {} : value
  const days = section.days ?? []
  const categories = section.categories ?? []
  const headerCells = days.map((day) => `<th>${escapeHtml(day)}</th>`).join('')
  const bodyRows = categories
    .map((category) => {
      const cells = days
        .map((day) => {
          const cellValue = tableValue[category]?.[day] ?? ''
          return `<td>${escapeHtml(cellValue)}</td>`
        })
        .join('')

      return `<tr><th>${escapeHtml(category)}</th>${cells}</tr>`
    })
    .join('')

  return `
    <section class="preview-section">
      <h2>${escapeHtml(section.label)}</h2>
      <table class="preview-table">
        <thead>
          <tr>
            <th></th>
            ${headerCells}
          </tr>
        </thead>
        <tbody>
          ${bodyRows}
        </tbody>
      </table>
    </section>
  `
}

function buildLocalPreviewHtml(
  template: BriefingTemplate,
  sections: Record<string, SectionValue>,
): string {
  const content = template.sections
    .map((section) => {
      const value = sections[section.id]
      if (section.kind === 'probability_table') {
        return renderProbabilityTable(section, value)
      }

      return `
        <section class="preview-section">
          <h2>${escapeHtml(section.label)}</h2>
          <p>${escapeHtml(typeof value === 'string' ? value : '')}</p>
        </section>
      `
    })
    .join('')

  return `
    <html>
      <head>
        <style>
          body {
            color: #0f172a;
            font-family: "DejaVu Sans", Arial, sans-serif;
            line-height: 1.5;
            margin: 0;
            padding: 24px;
          }
          h1 {
            border-bottom: 2px solid #cbd5e1;
            margin: 0 0 18px;
            padding-bottom: 12px;
          }
          h2 {
            color: #0b2a4a;
            font-size: 1.05rem;
            margin: 0 0 8px;
          }
          p {
            margin: 0;
            white-space: pre-wrap;
          }
          .preview-section + .preview-section {
            margin-top: 18px;
          }
          .preview-table {
            border-collapse: collapse;
            width: 100%;
          }
          .preview-table th,
          .preview-table td {
            border: 1px solid #cbd5e1;
            padding: 8px;
            text-align: center;
          }
          .preview-table th {
            background: #eff6ff;
          }
        </style>
      </head>
      <body>
        <h1>${escapeHtml(template.title)}</h1>
        ${content}
      </body>
    </html>
  `
}

const downstreamTemplates: Record<DownstreamOutputId, BriefingTemplate> = {
  discussion: buildLegacyTemplate('discussion'),
  icao: buildLegacyTemplate('icao'),
  staff: buildLegacyTemplate('staff'),
}

const briefingTypes = ref<BriefingType[]>([])
const selectedType = ref<WorkspaceTypeId>('master')
const selectedOutput = ref<DownstreamOutputId>('discussion')
const template = ref<BriefingTemplate | null>(null)
const draft = ref<BriefingDraft | null>(null)
const alerts = ref<ContextItem[]>([])
const advisories = ref<ContextItem[]>([])
const opsRecommendation = ref<OpsToCommsRecommendation | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const pdfMessage = ref('')

const isPartnerMode = computed(() => selectedType.value === 'partner')
const isOpsToCommsMode = computed(() => selectedType.value === 'ops-to-comms')
const isSocialGraphicsMode = computed(() => selectedType.value === 'social-graphic')
const isSingleGraphicMode = computed(() => selectedType.value === 'single-briefing-graphic')
const isGraphicMode = computed(() => {
  return isSocialGraphicsMode.value || isSingleGraphicMode.value
})
const isMasterMode = computed(() => selectedType.value === 'master')

const currentBadge = computed(() => {
  if (selectedType.value === 'partner') {
    return 'IDSS'
  }
  if (selectedType.value === 'ops-to-comms') {
    return 'OTC'
  }
  if (selectedType.value === 'social-graphic') {
    return 'SMDR'
  }
  if (selectedType.value === 'single-briefing-graphic') {
    return 'PGDR'
  }
  return 'SWPC'
})

const currentTitle = computed(() => 'PartnerBrief Hub')
const currentSubtitle = computed(() => {
  return 'A unified impact-based decision support services briefing generator'
})

const workspaceIntro = computed(() => {
  if (selectedType.value === 'master') {
    return {
      kicker: 'Master Briefing',
      text: 'Build the source briefing content that feeds downstream discussion, ICAO, and staff outputs.',
    }
  }

  if (selectedType.value === 'partner') {
    return {
      kicker: 'I&R Awareness',
      text: 'Assess sector risk, consequence, and partner-facing impacts to support impact-based decision support services.',
    }
  }

  if (selectedType.value === 'ops-to-comms') {
    return {
      kicker: 'Ops to Comms',
      text: 'Characterize the event, assess operational significance, and get a recommended path into the right communication design review workspace.',
    }
  }

  if (selectedType.value === 'social-graphic') {
    return {
      kicker: 'Social Media Design Review',
      text: 'Shape public-facing graphics with the recommended template, visual direction, and approved asset guidance.',
    }
  }

  return {
    kicker: 'Partner Graphic Design Review',
    text: 'Build partner-focused slides with operational structure, approved visuals, and message-first design review.',
  }
})

const availableBriefingTypes = computed(() => {
  return workspaceBriefingTypes.map((workspaceType) => {
    return briefingTypes.value.find((item) => item.id === workspaceType.id) ?? workspaceType
  })
})

const visibleAdvisories = computed(() => {
  return isMasterMode.value && selectedOutput.value === 'icao' ? advisories.value : []
})

const downstreamOutputs = computed<DerivedOutputStatus[]>(() => {
  const masterSections = draft.value?.sections ?? {}

  return downstreamProducts.map((product) => {
    const downstreamTemplate = downstreamTemplates[product.id]
    const derivedSections = Object.fromEntries(
      downstreamTemplate.sections.map((section) => [section.id, masterSections[section.id] ?? '']),
    ) as Record<string, SectionValue>

    const missingSections = downstreamTemplate.sections
      .filter((section) => !hasSectionContent(derivedSections[section.id]))
      .map((section) => section.label)

    const readiness = missingSections.length === 0 ? 'ready' : 'missing_inputs'

    return {
      id: product.id,
      label: product.label,
      readiness,
      missingSections,
      html:
        readiness === 'ready'
          ? buildLocalPreviewHtml(downstreamTemplate, derivedSections)
          : null,
      pdfMessage:
        readiness === 'ready'
          ? `${product.label} PDF export is not implemented yet, but all required sections are populated.`
          : `${product.label} PDF cannot be generated yet. Missing sections: ${missingSections.join(', ')}`,
    }
  })
})

const activeOutput = computed(() => {
  return downstreamOutputs.value.find((output) => output.id === selectedOutput.value) ?? downstreamOutputs.value[0]
})

const currentPdfButtonLabel = computed(() => {
  return activeOutput.value ? `Generate ${activeOutput.value.label} PDF` : 'Generate PDF'
})

function workspaceTypeForPath(path: OpsToCommsPathId): WorkspaceTypeId {
  return path === 'social-design-review' ? 'social-graphic' : 'single-briefing-graphic'
}

async function loadWorkspace(briefingType: string) {
  loading.value = true
  errorMessage.value = ''
  pdfMessage.value = ''

  try {
    if (
      briefingType === 'partner' ||
      briefingType === 'ops-to-comms' ||
      briefingType === 'social-graphic' ||
      briefingType === 'single-briefing-graphic'
    ) {
      template.value = null
      draft.value = null
      return
    }

    template.value = buildLegacyTemplate('master')
    selectedOutput.value = 'discussion'

    try {
      draft.value = await createDraft({
        briefing_type: 'master',
        template_version: 'legacy-ui',
        sections: {},
      })
    } catch {
      draft.value = createLocalDraft('master')
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load workspace.'
    template.value = buildLegacyTemplate('master')
    draft.value = createLocalDraft('master')
  } finally {
    loading.value = false
  }
}

async function loadContext() {
  try {
    alerts.value = await fetchActiveAlerts()
    advisories.value = await fetchActiveIcaoAdvisories()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load context.'
  }
}

async function handleSectionsChange(sections: Record<string, SectionValue>) {
  if (!draft.value) {
    return
  }

  pdfMessage.value = ''
  draft.value = {
    ...draft.value,
    sections,
  }

  if (isLocalDraft(draft.value.draft_id)) {
    return
  }

  try {
    draft.value = await updateDraft(draft.value.draft_id, { sections })
  } catch {
    draft.value = {
      ...draft.value,
      draft_id: `local-${draft.value.briefing_type}`,
    }
  }
}

function handleGeneratePdf() {
  if (!activeOutput.value) {
    return
  }

  pdfMessage.value = activeOutput.value.pdfMessage
}

function handleOpsRecommendationUpdate(recommendation: OpsToCommsRecommendation) {
  opsRecommendation.value = recommendation
}

function handleOpenRecommendedPath(path: OpsToCommsPathId, recommendation: OpsToCommsRecommendation) {
  opsRecommendation.value = { ...recommendation }
  selectedType.value = workspaceTypeForPath(path)
}

function clearPendingGraphicsRecommendation() {
  opsRecommendation.value = null
}

watch(selectedType, async (briefingType) => {
  await loadWorkspace(briefingType)
})

watch(selectedOutput, () => {
  pdfMessage.value = ''
})

onMounted(async () => {
  try {
    briefingTypes.value = await fetchBriefingTypes()
  } catch {
    briefingTypes.value = []
  }

  if (
    availableBriefingTypes.value.length > 0 &&
    !availableBriefingTypes.value.some((item) => item.id === selectedType.value)
  ) {
    selectedType.value = (availableBriefingTypes.value[0]?.id as WorkspaceTypeId | undefined) ?? 'master'
  }

  await loadWorkspace(selectedType.value)
  await loadContext()
})
</script>

<template>
  <main class="workspace-shell">
    <header class="briefing-topbar">
      <div class="briefing-topbar-shell">
        <div class="briefing-topbar-badge">{{ currentBadge }}</div>
        <div class="briefing-topbar-inner">
          <div class="briefing-topbar-kicker">NOAA Space Weather Prediction Center</div>
          <div class="briefing-topbar-title-row">
            <div class="briefing-topbar-copy">
              <div class="briefing-topbar-title">{{ currentTitle }}</div>
              <div class="briefing-topbar-subtitle">{{ currentSubtitle }}</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div
      class="workspace-grid"
      :class="{
        'workspace-grid--partner': isPartnerMode,
        'workspace-grid--ops': isOpsToCommsMode,
        'workspace-grid--graphics': isGraphicMode,
      }"
    >
      <section class="panel panel--primary">
        <div class="workspace-controls-row">
          <div class="toolbar workspace-controls-toolbar">
            <label>
              Workspace Controls
              <select v-model="selectedType">
                <option v-for="item in availableBriefingTypes" :key="item.id" :value="item.id">
                  {{ item.label }}
                </option>
              </select>
            </label>

            <div v-if="isMasterMode" class="toolbar-actions">
              <button :disabled="!draft || loading" @click="handleGeneratePdf">
                {{ currentPdfButtonLabel }}
              </button>
            </div>
          </div>

          <div class="workspace-intro">
            <div class="workspace-intro__kicker">{{ workspaceIntro.kicker }}</div>
            <p class="workspace-intro__text">{{ workspaceIntro.text }}</p>
          </div>
        </div>

        <div v-if="isMasterMode" class="status-row">
          <span v-if="draft" class="status-chip">Draft ID: {{ draft.draft_id }}</span>
          <span v-if="draft" class="status-chip">Status: {{ draft.status }}</span>
          <span v-if="draft && isLocalDraft(draft.draft_id)" class="status-chip">Local schema mode</span>
        </div>

        <p v-if="errorMessage" class="message workspace-alert error">{{ errorMessage }}</p>
        <p v-else-if="isMasterMode && pdfMessage" class="message workspace-alert">{{ pdfMessage }}</p>
        <p v-if="loading" class="message workspace-alert">Loading workspace...</p>

        <PartnerBriefing v-if="isPartnerMode && !loading" />
        <OpsToCommsWorkspace
          v-else-if="isOpsToCommsMode && !loading"
          @update:recommendation="handleOpsRecommendationUpdate"
          @open-path="handleOpenRecommendedPath"
        />
        <SocialGraphicsWorkspace
          v-else-if="isSocialGraphicsMode && !loading"
          mode="social"
          :recommendation="opsRecommendation"
          @recommendation-applied="clearPendingGraphicsRecommendation"
        />
        <SocialGraphicsWorkspace
          v-else-if="isSingleGraphicMode && !loading"
          mode="briefing"
          :recommendation="opsRecommendation"
          @recommendation-applied="clearPendingGraphicsRecommendation"
        />
        <SchemaForm
          v-else-if="template && draft && !loading"
          :template="template"
          :model-value="draft.sections"
          @update:model-value="handleSectionsChange"
        />
      </section>

      <PreviewPanel
        v-if="isMasterMode"
        :outputs="downstreamOutputs"
        :selected-output="selectedOutput"
        :pdf-message="pdfMessage"
        @update:selected-output="selectedOutput = $event"
      />
      <ContextPanel v-if="!isGraphicMode" :alerts="alerts" :advisories="visibleAdvisories" />
    </div>
  </main>
</template>
