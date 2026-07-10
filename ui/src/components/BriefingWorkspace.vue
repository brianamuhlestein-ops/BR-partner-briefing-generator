<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import {
  createDraft,
  fetchBriefingTypes,
  updateDraft,
} from '../api'
import type {
  BriefingDraft,
  BriefingTemplate,
  BriefingType,
  DerivedOutputStatus,
  DownstreamOutputId,
  SectionValue,
  TemplateSection,
  WorkspaceTypeId,
} from '../types'
import PartnerBriefing from './PartnerBriefing.vue'
import PartnerEmailBriefing from './PartnerEmailBriefing.vue'
import PartnerTailoredBrief from './PartnerTailoredBrief.vue'
import PreviewPanel from './PreviewPanel.vue'
import SchemaForm from './SchemaForm.vue'
import SocialGraphicsWorkspace from './social-graphics/SocialGraphicsWorkspace.vue'

const titleActions = [
  { label: 'Science Layer', icon: 'mdi-atom' },
  { label: 'User Guide', icon: 'mdi-book-open-page-variant-outline' },
  { label: 'Export Application JSON', icon: 'mdi-database-export-outline' },
]

const defaultSchemas: Record<string, string[]> = {
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
  { id: 'impact-risk', label: 'Impact & Risk Matrix' },
  { id: 'partner', label: 'Core Distribution Brief' },
  { id: 'partner-tailored', label: 'Partner Tailored Brief' },
  { id: 'social-graphic', label: 'Media Generator' },
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

function buildDefaultTemplate(briefingType: string): BriefingTemplate {
  const sectionLabels = defaultSchemas[briefingType] ?? []
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
    template_version: 'local-ui',
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
  discussion: buildDefaultTemplate('discussion'),
  icao: buildDefaultTemplate('icao'),
  staff: buildDefaultTemplate('staff'),
}

const activeWorkspaceStorageKey = 'partnerbrief-hub.active-workspace'

const briefingTypes = ref<BriefingType[]>([])
const selectedType = ref<WorkspaceTypeId>('impact-risk')
const selectedOutput = ref<DownstreamOutputId>('discussion')
const template = ref<BriefingTemplate | null>(null)
const draft = ref<BriefingDraft | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const pdfMessage = ref('')

const isImpactRiskMode = computed(() => selectedType.value === 'impact-risk')
const isPartnerMode = computed(() => selectedType.value === 'partner')
const isPartnerTailoredMode = computed(() => selectedType.value === 'partner-tailored')
const isPartnerBriefMode = computed(() => isPartnerMode.value || isPartnerTailoredMode.value)
const isOpsToCommsMode = computed(() => selectedType.value === 'ops-to-comms')
const isSocialGraphicsMode = computed(() => selectedType.value === 'social-graphic')
const isMasterMode = computed(() => false)
const isBlankSlateMode = computed(() => isOpsToCommsMode.value)
const isBriefingSchemaMode = computed(() => false)

const currentTitle = computed(() => 'Partner Briefing Generator')
const currentSubtitle = computed(() => {
  return 'Brief: A unified impact-based decision support services briefing generator'
})

const workspaceIntro = computed(() => {
  if (selectedType.value === 'impact-risk') {
    return {
      kicker: '',
      text: '',
    }
  }

  if (selectedType.value === 'partner' || selectedType.value === 'partner-tailored') {
    return {
      kicker: '',
      text: '',
    }
  }

  if (selectedType.value === 'ops-to-comms') {
    return {
      kicker: 'Significant Activity Response',
      text: 'Blank slate for significant activity response content.',
    }
  }

  if (selectedType.value === 'social-graphic') {
    return {
      kicker: '',
      text: '',
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

const briefingTypeIcon = (briefingTypeId: string) => {
  const icons: Record<string, string> = {
    'impact-risk': 'mdi-view-grid-outline',
    partner: 'mdi-email-outline',
    'partner-tailored': 'mdi-account-details-outline',
    'ops-to-comms': 'mdi-alert-outline',
    'social-graphic': 'mdi-share-variant-outline',
  }

  return icons[briefingTypeId] ?? 'mdi-file-document-outline'
}

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

async function loadWorkspace(briefingType: string) {
  loading.value = true
  errorMessage.value = ''
  pdfMessage.value = ''

  try {
    if (
      briefingType === 'ops-to-comms' ||
      briefingType === 'social-graphic' ||
      briefingType === 'single-briefing-graphic' ||
      briefingType === 'impact-risk' ||
      briefingType === 'partner' ||
      briefingType === 'partner-tailored'
    ) {
      template.value = null
      draft.value = null
      return
    }

    const schemaType = briefingType === 'icao' ? 'icao' : 'master'
    template.value = buildDefaultTemplate(schemaType)
    selectedOutput.value = schemaType === 'icao' ? 'icao' : 'discussion'

    try {
      draft.value = await createDraft({
        briefing_type: schemaType,
        template_version: 'local-ui',
        sections: {},
      })
    } catch {
      draft.value = createLocalDraft(schemaType)
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load workspace.'
    const fallbackType = briefingType === 'icao' ? 'icao' : 'master'
    template.value = buildDefaultTemplate(fallbackType)
    draft.value = createLocalDraft(fallbackType)
  } finally {
    loading.value = false
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

function selectWorkspace(briefingType: string) {
  selectedType.value = briefingType as WorkspaceTypeId
}

watch(selectedType, async (briefingType) => {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(activeWorkspaceStorageKey, briefingType)
  }
  await loadWorkspace(briefingType)
})

watch(selectedOutput, () => {
  pdfMessage.value = ''
})

onMounted(async () => {
  if (typeof window !== 'undefined') {
    const storedWorkspace = window.localStorage.getItem(activeWorkspaceStorageKey) as WorkspaceTypeId | null
    if (storedWorkspace && workspaceBriefingTypes.some((item) => item.id === storedWorkspace)) {
      selectedType.value = storedWorkspace
    }
  }

  try {
    briefingTypes.value = await fetchBriefingTypes()
  } catch {
    briefingTypes.value = []
  }

  if (
    availableBriefingTypes.value.length > 0 &&
    !availableBriefingTypes.value.some((item) => item.id === selectedType.value)
  ) {
    selectedType.value = (availableBriefingTypes.value[0]?.id as WorkspaceTypeId | undefined) ?? 'impact-risk'
  }

  await loadWorkspace(selectedType.value)
})
</script>

<template>
  <main class="app-shell ma-root">
    <header class="suite-bar">
      <div class="brand-lockup">
        <div class="swift-mark" aria-hidden="true">
          <span>SWIFT</span>
        </div>
        <div class="title-copy">
          <p class="eyebrow">NOAA Space Weather Prediction Center</p>
          <h1>{{ currentTitle }}</h1>
          <p class="mission-line">{{ currentSubtitle }}</p>
        </div>
      </div>

      <div class="title-tools" aria-label="Application tools">
        <button
          v-for="action in titleActions"
          :key="action.label"
          class="icon-button"
          type="button"
          :title="action.label"
          :aria-label="action.label"
        >
          <v-icon :icon="action.icon" size="21" />
        </button>
      </div>
    </header>

    <div class="ma-nav-shell">
      <v-card class="ma-tabs-card" elevation="0">
        <v-tabs v-model="selectedType" color="primary" density="comfortable" grow :show-arrows="false">
          <v-tab
            v-for="item in availableBriefingTypes"
            :key="item.id"
            :value="item.id"
            @click="selectWorkspace(item.id)"
          >
            <v-icon start>{{ briefingTypeIcon(item.id) }}</v-icon>
            {{ item.label }}
          </v-tab>
        </v-tabs>
      </v-card>
    </div>

    <section class="application-workspace" aria-label="Application content">
      <div class="workflow-workspace" aria-label="Selected workflow">
        <div
          class="workspace-grid workflow-view"
          :class="{
            'workspace-grid--partner': isImpactRiskMode,
            'workspace-grid--graphics': isSocialGraphicsMode,
          }"
        >
          <section class="panel panel--primary" :class="{ 'panel--full-width': isImpactRiskMode || isPartnerBriefMode }">
            <div class="workspace-controls-row">
              <div v-if="!isImpactRiskMode && !isPartnerBriefMode && !isSocialGraphicsMode" class="workspace-intro">
                <div class="workspace-intro__kicker">{{ workspaceIntro.kicker }}</div>
                <p class="workspace-intro__text">{{ workspaceIntro.text }}</p>
              </div>

              <div v-if="isBriefingSchemaMode" class="toolbar-actions workspace-action-row">
                <button :disabled="!draft || loading" @click="handleGeneratePdf">
                  {{ currentPdfButtonLabel }}
                </button>
              </div>
            </div>

            <div v-if="isBriefingSchemaMode" class="status-row">
              <span v-if="draft" class="status-chip">Draft ID: {{ draft.draft_id }}</span>
              <span v-if="draft" class="status-chip">Status: {{ draft.status }}</span>
              <span v-if="draft && isLocalDraft(draft.draft_id)" class="status-chip">Local schema mode</span>
            </div>

            <p v-if="errorMessage" class="message workspace-alert error">{{ errorMessage }}</p>
            <p v-else-if="isBriefingSchemaMode && pdfMessage" class="message workspace-alert">{{ pdfMessage }}</p>
            <p v-if="loading" class="message workspace-alert">Loading workspace...</p>

            <PartnerBriefing v-if="isImpactRiskMode && !loading" />
            <PartnerEmailBriefing v-else-if="isPartnerMode && !loading" />
            <PartnerTailoredBrief v-else-if="isPartnerTailoredMode && !loading" />
            <div v-else-if="isBlankSlateMode && !loading" class="blank-slate-panel">
              <span>{{ workspaceIntro.kicker }} workspace pending layout.</span>
            </div>
            <div v-else-if="isSocialGraphicsMode && !loading" class="social-media-stack">
              <SocialGraphicsWorkspace
                mode="social"
                presentation="social-tab"
              />
            </div>
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
        </div>
      </div>
    </section>
  </main>
</template>
