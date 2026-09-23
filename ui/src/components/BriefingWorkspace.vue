<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchRuntimeNow } from '../api'
import type { RuntimeContext, WorkspaceTypeId } from '../types'
import { readUiDensity, setUiDensity, type UiDensity } from '../utils/uiDensity'
import SynopsisWorkspace from './SynopsisWorkspace.vue'
import PartnerEmailBriefing from './PartnerEmailBriefing.vue'
import PartnerTailoredBrief from './PartnerTailoredBrief.vue'
import SocialGraphicsWorkspace from './social-graphics/SocialGraphicsWorkspace.vue'

const titleActions = [
  { label: 'Science Layer', icon: 'mdi-atom' },
  { label: 'User Guide', icon: 'mdi-book-open-page-variant-outline' },
  { label: 'Export Application JSON', icon: 'mdi-database-export-outline' },
]

const workspaceBriefingTypes = [
  { id: 'synopsis', label: 'Synopsis' },
  { id: 'partner', label: 'Core Distribution Brief' },
  { id: 'partner-tailored', label: 'Partner Tailored Brief' },
  { id: 'social-graphic', label: 'Media Generator' },
] as const

const activeWorkspaceStorageKey = 'partnerbrief-hub.active-workspace'

const selectedType = ref<WorkspaceTypeId>('synopsis')
const runtimeNow = ref<RuntimeContext | null>(null)
const runtimeError = ref('')
const uiDensity = ref<UiDensity>(readUiDensity())

const runtimeBadgeText = computed(() => {
  if (!runtimeNow.value) return 'CLOCK UNAVAILABLE'
  if (runtimeNow.value.data_source === 'replay') {
    return `${runtimeNow.value.data_kind === 'synthetic' ? 'EXERCISE' : 'REPLAY'} ${runtimeNow.value.now_utc?.replace('T', ' ').replace(':00Z', 'Z') ?? 'CLOCK?'}`
  }
  return 'OPERATIONAL UTC'
})

const isSynopsisMode = computed(() => selectedType.value === 'synopsis')
const isPartnerMode = computed(() => selectedType.value === 'partner')
const isPartnerTailoredMode = computed(() => selectedType.value === 'partner-tailored')
const isPartnerBriefMode = computed(() => isPartnerMode.value || isPartnerTailoredMode.value)
const isSocialGraphicsMode = computed(() => selectedType.value === 'social-graphic')

function briefingTypeIcon(briefingTypeId: WorkspaceTypeId) {
  const icons: Record<WorkspaceTypeId, string> = {
    synopsis: 'mdi-text-box-outline',
    partner: 'mdi-email-outline',
    'partner-tailored': 'mdi-account-details-outline',
    'social-graphic': 'mdi-share-variant-outline',
  }
  return icons[briefingTypeId]
}

function selectWorkspace(briefingType: WorkspaceTypeId) {
  selectedType.value = briefingType
}

function toggleCompactDensity() {
  uiDensity.value = setUiDensity(uiDensity.value === 'compact' ? 'comfortable' : 'compact')
}

watch(selectedType, (briefingType) => {
  try {
    window.localStorage.setItem(activeWorkspaceStorageKey, briefingType)
  } catch {
    // Workspace switching remains available when browser storage is unavailable.
  }
})

onMounted(async () => {
  try {
    const storedWorkspace = window.localStorage.getItem(activeWorkspaceStorageKey) as WorkspaceTypeId | null
    if (storedWorkspace && workspaceBriefingTypes.some((item) => item.id === storedWorkspace)) {
      selectedType.value = storedWorkspace
    }
  } catch {
    // The first workspace remains selected when browser storage is unavailable.
  }

  try {
    runtimeNow.value = await fetchRuntimeNow()
  } catch (error) {
    runtimeError.value = error instanceof Error ? error.message : 'Runtime clock is unavailable.'
  }
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
          <h1>Briefing &amp; Synopsis</h1>
          <p class="mission-line">Brief: Shared situational assessment, partner communications, and media products.</p>
        </div>
      </div>

      <div class="title-tools" aria-label="Application tools">
        <v-btn
          class="ui-density-btn"
          :class="{ selected: uiDensity === 'compact' }"
          variant="tonal"
          density="compact"
          prepend-icon="mdi-laptop"
          :aria-pressed="uiDensity === 'compact'"
          :aria-label="uiDensity === 'compact' ? 'Disable Compact interface density' : 'Enable Compact interface density'"
          @click="toggleCompactDensity"
        >
          <span class="ui-density-label">Compact</span>
        </v-btn>
        <span
          class="runtime-mode-badge"
          :class="{ 'runtime-mode-badge--replay': runtimeNow?.data_source === 'replay' }"
          :title="runtimeError || runtimeNow?.clock_source"
        >{{ runtimeBadgeText }}</span>
        <span data-swift-hazard-anchor></span>
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
      <v-card class="ma-tabs-card swift-primary-tabs" elevation="0">
        <v-tabs v-model="selectedType" color="primary" density="comfortable" grow show-arrows>
          <v-tab
            v-for="item in workspaceBriefingTypes"
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
            'workspace-grid--partner': isSynopsisMode,
            'workspace-grid--graphics': isSocialGraphicsMode,
          }"
        >
          <section class="panel panel--primary" :class="{ 'panel--full-width': isSynopsisMode || isPartnerBriefMode }">
            <!-- All workspaces remain mounted so switching tabs cannot discard in-progress edits. -->
            <SynopsisWorkspace v-show="isSynopsisMode" />
            <PartnerEmailBriefing v-show="isPartnerMode" :runtime-now="runtimeNow" />
            <PartnerTailoredBrief v-show="isPartnerTailoredMode" :runtime-now="runtimeNow" />
            <div v-show="isSocialGraphicsMode" class="social-media-stack">
              <SocialGraphicsWorkspace :runtime-now="runtimeNow" />
            </div>
          </section>
        </div>
      </div>
    </section>
  </main>
</template>
