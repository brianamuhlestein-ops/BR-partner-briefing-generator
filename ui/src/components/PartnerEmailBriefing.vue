<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import type { RuntimeContext } from '../types'
import { fetchEmailBriefingDocument, saveEmailBriefingDocument } from '../api'
import coreBriefingCatalog from '../../../docs/exercise/gannon/core-briefings/may-2024-core-briefings.json'
import { exportElementToPdf } from '../utils/exportPdf'
import { forecastDayLabels, formatIssueTime, fromDatetimeLocal, toDatetimeLocal } from '../utils/briefingTime'

const props = defineProps<{ runtimeNow: RuntimeContext | null }>()

type RiskLevel = 'Little to None' | 'Minor' | 'Moderate' | 'High' | 'Extreme'

const riskLevels: { label: RiskLevel; color: string; text: string }[] = [
  { label: 'Little to None', color: '#a8e6a1', text: '#102316' },
  { label: 'Minor', color: '#ffe564', text: '#111827' },
  { label: 'Moderate', color: '#ff9838', text: '#111827' },
  { label: 'High', color: '#e84f4f', text: '#ffffff' },
  { label: 'Extreme', color: '#a027d7', text: '#ffffff' },
]

const sectors = [
  'Power Grid',
  'Aviation and Radiation',
  'Satellite Operations',
  'Communications and Navigation',
  'Human Spaceflight',
  'Emergency Management',
]

function emptyRiskOutlook(): Record<string, RiskLevel[]> {
  return Object.fromEntries(
    sectors.map((sector) => [sector, ['Little to None', 'Little to None', 'Little to None']]),
  ) as Record<string, RiskLevel[]>
}

type MediaItem = {
  id: number
  fileName: string
  dataUrl: string
  caption: string
}

type BriefingPreset = {
  id: string
  label: string
  issueTimeUtc: string
  headline: string
  summary: string
  statusBadge: string
  summaryCallout: string
  keyPoints: string
  activeProducts: string
  impacts: string
  impactsLabel: string
  actions: string
  watchNext: string
  watchLabel: string
  info: string
  riskNote: string
  hasRiskOutlook: boolean
  media: MediaItem[]
  riskOutlook: Record<string, RiskLevel[]>
}

type BriefingMediaRecord = {
  asset: string
  caption: string
}

type CoreBriefingRecord = {
  id: string
  label: string
  issue_time_utc: string
  headline: string
  summary: string
  status_badge?: string
  summary_callout?: string
  key_points: string[]
  active_products: string[]
  potential_impacts: string[]
  impacts_label?: string
  actions?: string[]
  watch_next: string[]
  watch_label?: string
  information: string[]
  media?: BriefingMediaRecord[]
  risk_note?: string
  risk_outlook?: Record<string, RiskLevel[]>
}

const briefingImageAssets = import.meta.glob(
  '../../../docs/exercise/gannon/email-briefing-graphics/*',
  { eager: true, query: '?url', import: 'default' },
) as Record<string, string>

function briefingImageUrl(asset: string) {
  return Object.entries(briefingImageAssets).find(([path]) => path.endsWith(`/${asset}`))?.[1] ?? ''
}

const briefingPresets: BriefingPreset[] = (coreBriefingCatalog.briefings as CoreBriefingRecord[]).map(
  (record) => ({
    id: record.id,
    label: record.label,
    issueTimeUtc: record.issue_time_utc,
    headline: record.headline,
    summary: record.summary,
    statusBadge: record.status_badge ?? '',
    summaryCallout: record.summary_callout ?? '',
    keyPoints: record.key_points.join('\n'),
    activeProducts: record.active_products.join('\n'),
    impacts: record.potential_impacts.join('\n'),
    impactsLabel: record.impacts_label ?? 'Potential Impacts',
    actions: (record.actions ?? []).join('\n'),
    watchNext: record.watch_next.join('\n'),
    watchLabel: record.watch_label ?? 'What To Watch Next',
    info: record.information.join('\n'),
    riskNote: record.risk_note ?? '',
    hasRiskOutlook: Boolean(record.risk_outlook),
    media: (record.media ?? []).map((item, index) => ({
      id: index + 1,
      fileName: item.asset,
      dataUrl: briefingImageUrl(item.asset),
      caption: item.caption,
    })),
    riskOutlook: record.risk_outlook ?? emptyRiskOutlook(),
  }),
)

const selectedPresetId = ref(briefingPresets[0]!.id)
const isMay2024Replay = computed(() => {
  if (props.runtimeNow?.data_source !== 'replay') return false
  if (props.runtimeNow.scenario === 'may_2024_geomagnetic_storm') return true
  const now = Date.parse(props.runtimeNow.now_utc ?? '')
  return Number.isFinite(now)
    && now >= Date.parse('2024-05-06T15:00:00Z')
    && now <= Date.parse('2024-05-23T16:10:00Z')
})
const availableBriefingPresets = computed(() => {
  const now = Date.parse(props.runtimeNow?.now_utc ?? '')
  if (!isMay2024Replay.value) return briefingPresets
  if (!Number.isFinite(now)) return []
  return briefingPresets.filter((preset) => Date.parse(preset.issueTimeUtc) <= now)
})

const briefing = reactive({
  headline: briefingPresets[0]!.headline,
  summary:
    briefingPresets[0]!.summary,
  statusBadge: briefingPresets[0]!.statusBadge,
  summaryCallout: briefingPresets[0]!.summaryCallout,
  showSummaryCallout: false,
  keyPoints:
    briefingPresets[0]!.keyPoints,
  activeProducts:
    briefingPresets[0]!.activeProducts,
  impacts:
    briefingPresets[0]!.impacts,
  impactsLabel: briefingPresets[0]!.impactsLabel,
  actions:
    briefingPresets[0]!.actions,
  watchNext:
    briefingPresets[0]!.watchNext,
  watchLabel: briefingPresets[0]!.watchLabel,
  info:
    briefingPresets[0]!.info,
  riskNote: briefingPresets[0]!.riskNote,
  hasRiskOutlook: briefingPresets[0]!.hasRiskOutlook,
  media: structuredClone(briefingPresets[0]!.media),
  riskOutlook: structuredClone(briefingPresets[0]!.riskOutlook),
})

let mediaId = 1
const pdfPreviewRef = ref<HTMLElement | null>(null)
const issueTimeUtc = ref<string | null>(briefingPresets[0]!.issueTimeUtc)
const isSaving = ref(false)
const saveStatus = ref('Not saved')
const hasRestoredSavedDocument = ref(false)
const issueTimeDisplay = computed(() => formatIssueTime(issueTimeUtc.value))
const days = computed(() => forecastDayLabels(issueTimeUtc.value))
const issueTimeInput = computed({
  get: () => toDatetimeLocal(issueTimeUtc.value),
  set: (value: string) => {
    issueTimeUtc.value = fromDatetimeLocal(value)
  },
})

watch(
  () => props.runtimeNow?.now_utc,
  (value) => {
    if (!value) return
    if (hasRestoredSavedDocument.value) return
    if (isMay2024Replay.value) {
      const current = availableBriefingPresets.value[availableBriefingPresets.value.length - 1]
      if (current) applyPreset(current)
      return
    }
    if (!issueTimeUtc.value) issueTimeUtc.value = value
  },
  { immediate: true },
)

function lines(value: string): string[] {
  return value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function riskStyle(level: RiskLevel) {
  const risk = riskLevels.find((item) => item.label === level) ?? riskLevels[0]!
  return {
    backgroundColor: risk.color,
    color: risk.text,
  }
}

function riskLevelFor(sector: string, index: number): RiskLevel {
  return briefing.riskOutlook[sector]?.[index] ?? 'Little to None'
}

function handleRiskChange(sector: string, index: number, event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) {
    return
  }
  const value = target.value as RiskLevel
  const sectorRisk = briefing.riskOutlook[sector]
  if (!sectorRisk) {
    return
  }
  sectorRisk[index] = value
}

function resetIssueTime() {
  issueTimeUtc.value = props.runtimeNow?.now_utc ?? null
}

function applyPreset(preset: BriefingPreset) {
  selectedPresetId.value = preset.id
  issueTimeUtc.value = preset.issueTimeUtc
  briefing.headline = preset.headline
  briefing.summary = preset.summary
  briefing.statusBadge = preset.statusBadge
  briefing.summaryCallout = preset.summaryCallout
  briefing.showSummaryCallout = false
  briefing.keyPoints = preset.keyPoints
  briefing.activeProducts = preset.activeProducts
  briefing.impacts = preset.impacts
  briefing.impactsLabel = preset.impactsLabel
  briefing.actions = preset.actions
  briefing.watchNext = preset.watchNext
  briefing.watchLabel = preset.watchLabel
  briefing.info = preset.info
  briefing.riskNote = preset.riskNote
  briefing.hasRiskOutlook = preset.hasRiskOutlook
  briefing.media = structuredClone(preset.media)
  mediaId = Math.max(0, ...briefing.media.map((item) => item.id))
  briefing.riskOutlook = structuredClone(preset.riskOutlook)
}

function selectExerciseBriefing(event: Event) {
  const presetId = (event.target as HTMLSelectElement).value
  const preset = availableBriefingPresets.value.find((item) => item.id === presetId)
  if (preset) applyPreset(preset)
}

function addMediaItem() {
  mediaId += 1
  briefing.media.push({
    id: mediaId,
    fileName: '',
    dataUrl: '',
    caption: '',
  })
}

function handleMediaUpload(item: MediaItem, event: Event) {
  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0]
  item.fileName = file?.name ?? ''
  item.dataUrl = ''

  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.addEventListener('load', () => {
    item.dataUrl = typeof reader.result === 'string' ? reader.result : ''
  })
  reader.readAsDataURL(file)
}

function exportBriefingPdf() {
  exportElementToPdf(pdfPreviewRef.value, 'Core Distribution Brief')
}

async function loadSavedBriefingJson() {
  try {
    const saved = await fetchEmailBriefingDocument<{
      selectedPresetId: string
      issueTimeUtc: string | null
      briefing: typeof briefing
    }>('core')
    if (!saved) return
    hasRestoredSavedDocument.value = true
    selectedPresetId.value = saved.document.selectedPresetId
    issueTimeUtc.value = saved.document.issueTimeUtc
    Object.assign(briefing, saved.document.briefing)
    briefing.media = briefing.media.map((item) => ({
      ...item,
      dataUrl: item.dataUrl.startsWith('data:')
        ? item.dataUrl
        : briefingImageUrl(item.fileName) || item.dataUrl,
    }))
    mediaId = Math.max(0, ...briefing.media.map((item) => item.id))
    saveStatus.value = `Loaded ${new Date(saved.updated_at).toLocaleString()}`
  } catch (error) {
    saveStatus.value = error instanceof Error ? error.message : 'Unable to load saved JSON'
  }
}

async function saveBriefingJson() {
  isSaving.value = true
  saveStatus.value = 'Saving...'
  try {
    const saved = await saveEmailBriefingDocument('core', {
      selectedPresetId: selectedPresetId.value,
      issueTimeUtc: issueTimeUtc.value,
      briefing: JSON.parse(JSON.stringify(briefing)),
    })
    hasRestoredSavedDocument.value = true
    saveStatus.value = `Saved ${new Date(saved.updated_at).toLocaleString()}`
  } catch (error) {
    saveStatus.value = error instanceof Error ? error.message : 'Unable to save JSON'
  } finally {
    isSaving.value = false
  }
}

onMounted(loadSavedBriefingJson)

</script>

<template>
  <section class="partner-email-briefing">
    <div class="partner-exercise-picker">
      <label>
        Exercise Core Brief
        <select :value="selectedPresetId" @change="selectExerciseBriefing">
          <option v-if="availableBriefingPresets.length === 0" value="">No core briefing effective yet</option>
          <option
            v-for="preset in availableBriefingPresets"
            :key="preset.id"
            :value="preset.id"
          >
            {{ preset.label }} - {{ preset.issueTimeUtc.slice(5, 16).replace('T', ' ') }}Z
          </option>
        </select>
      </label>
      <span>{{ availableBriefingPresets.length }} of {{ briefingPresets.length }} briefings available</span>
    </div>
    <div class="partner-email-workspace">
      <aside class="partner-email-editor partner-email-editor--forecast" aria-label="Core distribution forecast inputs">
        <div class="partner-email-column-heading">
          <h2>Forecast</h2>
          <span>SWIFT suite JSON</span>
        </div>

        <section class="partner-email-input-section">
          <div class="partner-email-editor-heading">Active Products</div>
          <label>
            <span class="partner-email-field-note">Future feed: auto-populated from SWIFT Suite product JSON APIs.</span>
            <textarea v-model="briefing.activeProducts" />
          </label>
        </section>

        <details v-if="briefing.hasRiskOutlook" class="partner-email-input-section partner-email-risk-editor" open>
          <summary class="partner-email-editor-heading">Risk Outlook</summary>
          <div class="partner-email-risk-grid">
            <div class="partner-email-risk-head">Sector</div>
            <div v-for="day in days" :key="day" class="partner-email-risk-head">
              {{ day.split('\n')[0] }}
            </div>
            <template v-for="sector in sectors" :key="sector">
              <div class="partner-email-risk-sector">{{ sector }}</div>
              <select
                v-for="(_, index) in days"
                :key="`${sector}-editor-${index}`"
                :value="riskLevelFor(sector, index)"
                :style="riskStyle(riskLevelFor(sector, index))"
                class="partner-email-risk-select"
                @change="handleRiskChange(sector, index, $event)"
              >
                <option v-for="risk in riskLevels" :key="risk.label" :value="risk.label">
                  {{ risk.label }}
                </option>
              </select>
            </template>
          </div>
        </details>
      </aside>

      <aside class="partner-email-editor partner-email-editor--narrative" aria-label="Core distribution narrative inputs">
        <div class="partner-email-column-heading">
          <h2>Narrative</h2>
          <span>Forecaster review</span>
        </div>

        <section class="partner-email-input-section">
          <div class="partner-email-editor-heading">Briefing Header</div>
          <label>
            Forecast Issue Time (UTC)
            <input v-model="issueTimeInput" type="datetime-local" />
          </label>
          <button class="partner-add-media-button" type="button" @click="resetIssueTime">
            Set to {{ runtimeNow?.data_source === 'replay' ? 'Replay' : 'Operational' }} Time
          </button>

          <label>
            Headline
            <input v-model="briefing.headline" type="text" />
          </label>
        </section>

        <section class="partner-email-input-section partner-email-review-section">
          <div class="partner-email-editor-heading">Summary</div>
          <label>
            Forecaster-reviewed summary
            <textarea v-model="briefing.summary" />
          </label>
          <button
            v-if="briefing.summaryCallout"
            type="button"
            class="partner-last-brief-button"
            :class="{ 'partner-last-brief-button--active': briefing.showSummaryCallout }"
            :aria-pressed="briefing.showSummaryCallout"
            @click="briefing.showSummaryCallout = !briefing.showSummaryCallout"
          >
            {{ briefing.statusBadge || 'Last Brief' }}
          </button>
        </section>

        <section class="partner-email-input-section partner-email-review-section">
          <div class="partner-email-editor-heading">Key Points</div>
          <label>
            Forecaster-reviewed key points
            <textarea v-model="briefing.keyPoints" />
          </label>
        </section>

        <details class="partner-email-input-section">
          <summary class="partner-email-editor-heading">Operational Narrative</summary>
          <label>
            {{ briefing.impactsLabel }}
            <textarea v-model="briefing.impacts" />
          </label>

          <label>
            What To Do Now
            <textarea v-model="briefing.actions" />
          </label>

          <label v-if="lines(briefing.watchNext).length">
            {{ briefing.watchLabel }}
            <textarea v-model="briefing.watchNext" />
          </label>

          <label>
            More Information
            <textarea v-model="briefing.info" />
          </label>
        </details>

        <details class="partner-email-input-section partner-email-media-editor" open>
          <summary class="partner-email-editor-heading">Media</summary>
          <div class="partner-email-media-list">
            <div v-for="item in briefing.media" :key="item.id" class="partner-email-media-row">
              <label class="partner-media-upload-button">
                Upload Image
                <input type="file" accept="image/*" @change="handleMediaUpload(item, $event)" />
              </label>
              <span class="partner-media-file-name">{{ item.fileName || 'No image selected' }}</span>
              <label>
                Image Caption
                <textarea v-model="item.caption" class="partner-media-caption" />
              </label>
            </div>
          </div>
          <button class="partner-add-media-button" type="button" @click="addMediaItem">
            Add More Media
          </button>
        </details>
      </aside>

      <div class="partner-preview-column">
        <div class="partner-email-column-heading partner-email-column-heading--preview">
          <div>
            <h2>Preview</h2>
            <span>Generated product</span>
          </div>
          <div class="partner-preview-actions">
            <span class="partner-save-status" role="status">{{ saveStatus }}</span>
            <button
              class="partner-save-button"
              type="button"
              :disabled="isSaving"
              @click="saveBriefingJson"
            >
              {{ isSaving ? 'Saving...' : 'Save JSON' }}
            </button>
            <button class="partner-export-button" type="button" @click="exportBriefingPdf">
              Export PDF
            </button>
          </div>
        </div>

        <article ref="pdfPreviewRef" class="partner-pdf-preview" aria-label="Partner briefing PDF preview">
        <header class="partner-pdf-masthead">
          <div class="partner-pdf-brand">
            <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
            <img src="/assets/visual-finder/logos/NWSlogo.png" alt="National Weather Service" />
            <div>
              <div>National Weather Service</div>
              <strong>Space Weather Prediction Center</strong>
              <span>National Oceanic and Atmospheric Administration</span>
            </div>
          </div>
          <div class="partner-pdf-meta">
            <strong>Partner Briefing</strong>
            <span>{{ issueTimeDisplay }}</span>
          </div>
        </header>

        <section class="partner-pdf-title">
          <h3>{{ briefing.headline }}</h3>
          <p>{{ briefing.summary }}</p>
        </section>

        <div v-if="briefing.showSummaryCallout && briefing.summaryCallout" class="partner-pdf-final-callout">
          <strong>{{ briefing.summaryCallout }}</strong>
        </div>

        <section class="partner-pdf-section">
          <h4>Key Points</h4>
          <ul>
            <li v-for="item in lines(briefing.keyPoints)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section v-if="briefing.hasRiskOutlook" class="partner-pdf-section">
          <h4>Space Weather Risk Outlook</h4>
          <table class="partner-pdf-risk-table">
            <thead>
              <tr>
                <th>Sector</th>
                <th v-for="day in days" :key="day">
                  <span v-for="line in day.split('\n')" :key="line">{{ line }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sector in sectors" :key="sector">
                <th>{{ sector }}</th>
                <td
                  v-for="(_, index) in days"
                  :key="`${sector}-${index}`"
                  :style="riskStyle(riskLevelFor(sector, index))"
                >
                  {{ riskLevelFor(sector, index) }}
                </td>
              </tr>
            </tbody>
          </table>

          <p v-if="briefing.riskNote" class="partner-pdf-risk-note">
            {{ briefing.riskNote }}
          </p>

          <div class="partner-pdf-legend">
            <strong>Risk Levels:</strong>
            <span v-for="risk in riskLevels" :key="risk.label" :style="{ backgroundColor: risk.color, color: risk.text }">
              {{ risk.label }}
            </span>
          </div>
        </section>

        <section class="partner-pdf-section">
          <h4>Active Products</h4>
          <ul>
            <li v-for="item in lines(briefing.activeProducts)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
          <h4>{{ briefing.impactsLabel }}</h4>
          <ul>
            <li v-for="item in lines(briefing.impacts)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section v-if="lines(briefing.actions).length" class="partner-pdf-section">
          <h4>What To Do Now</h4>
          <ul>
            <li v-for="item in lines(briefing.actions)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section v-if="lines(briefing.watchNext).length" class="partner-pdf-section">
          <h4>{{ briefing.watchLabel }}</h4>
          <ul>
            <li v-for="item in lines(briefing.watchNext)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section partner-pdf-info">
          <h4>For More Information</h4>
          <p v-for="item in lines(briefing.info)" :key="item">{{ item }}</p>
        </section>

        <section class="partner-pdf-section" v-if="briefing.media.some((item) => item.dataUrl || item.fileName || item.caption)">
          <h4>Media</h4>
          <div v-for="item in briefing.media" :key="item.id" class="partner-pdf-media-item">
            <img v-if="item.dataUrl" :src="item.dataUrl" :alt="item.caption || item.fileName || 'Uploaded media'" />
            <strong v-else-if="item.fileName">{{ item.fileName }}</strong>
            <p v-if="item.caption">{{ item.caption }}</p>
          </div>
        </section>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.partner-email-briefing {
  display: grid;
  gap: 14px;
}

.partner-exercise-picker {
  display: flex;
  width: 100%;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 183, 77, 0.38);
  border-radius: 8px;
  background: rgba(177, 94, 13, 0.12);
}

.partner-exercise-picker label {
  display: grid;
  flex: 1;
  gap: 5px;
  color: #ffd9a0;
  font-size: 0.78rem;
  font-weight: 700;
}

.partner-exercise-picker select {
  min-height: 38px;
  padding: 0 10px;
  border: 1px solid rgba(255, 183, 77, 0.45);
  border-radius: 6px;
  background: #101a27;
  color: #f5f8fc;
}

.partner-exercise-picker > span {
  padding-bottom: 9px;
  color: rgba(255, 226, 184, 0.72);
  font-size: 0.76rem;
  white-space: nowrap;
}

.partner-email-workspace {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
  min-width: 0;
}

.partner-email-editor {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.partner-email-column-heading {
  display: flex;
  min-height: 26px;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  color: rgba(232, 239, 248, 0.72);
  text-transform: uppercase;
}

.partner-email-column-heading h2 {
  margin: 0;
  color: #eef7ff;
  font-size: 0.92rem;
  font-weight: 500;
  letter-spacing: 0.04em;
}

.partner-email-column-heading span {
  color: rgba(232, 239, 248, 0.46);
  font-size: 0.68rem;
  font-weight: 400;
  letter-spacing: 0.04em;
}

.partner-email-column-heading--preview {
  width: 100%;
  align-items: center;
}

.partner-preview-column {
  display: grid;
  gap: 8px;
  min-width: 0;
  justify-items: center;
}

.partner-preview-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 7px;
}

.partner-save-status {
  max-width: 220px;
  color: rgba(232, 239, 248, 0.58) !important;
  font-size: 0.66rem !important;
  text-align: right;
  white-space: normal;
}

.partner-save-button {
  border: 1px solid rgba(255, 229, 100, 0.48);
  background: rgba(255, 229, 100, 0.13);
  color: #fff0a8;
  font-weight: 500;
}

.partner-save-button:disabled {
  opacity: 0.58;
}

.partner-export-button {
  border: 1px solid rgba(95, 199, 255, 0.32);
  background: rgba(95, 199, 255, 0.12);
  color: #d9efff;
  font-weight: 400;
}

.partner-email-input-section {
  display: grid;
  gap: 12px;
  min-width: 0;
  max-width: 100%;
  overflow: visible;
  padding: 14px;
  border: 1px solid rgba(95, 199, 255, 0.22);
  border-radius: var(--app-radius);
  background:
    linear-gradient(180deg, rgba(95, 199, 255, 0.06), rgba(95, 199, 255, 0.025)),
    rgba(4, 10, 18, 0.28);
}

.partner-email-review-section {
  border-color: rgba(255, 229, 94, 0.5);
  background:
    linear-gradient(180deg, rgba(255, 229, 94, 0.11), rgba(255, 229, 94, 0.045)),
    rgba(4, 10, 18, 0.26);
}

.partner-email-review-section .partner-email-editor-heading {
  color: #ffe55e;
}

.partner-email-input-section[open] {
  gap: 12px;
}

.partner-email-input-section:not([open]) {
  gap: 0;
}

.partner-email-input-section summary {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  list-style: none;
}

.partner-email-input-section summary::-webkit-details-marker {
  display: none;
}

.partner-email-input-section summary::after {
  content: ">";
  flex: 0 0 auto;
  color: var(--app-primary);
  font-size: 0.82rem;
  transform: rotate(90deg);
  transition: transform 120ms ease;
}

.partner-email-input-section:not([open]) summary::after {
  transform: rotate(0deg);
}

.partner-email-editor label {
  display: grid;
  gap: 6px;
  min-width: 0;
  color: rgba(232, 239, 248, 0.78);
  font-weight: 400;
}

.partner-email-field-note {
  color: rgba(232, 239, 248, 0.58);
  font-size: 0.76rem;
  font-weight: 400;
  line-height: 1.3;
}

.partner-email-editor input,
.partner-email-editor textarea,
.partner-email-editor select {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  display: block;
  border-color: rgba(171, 199, 235, 0.58);
  background: #ffffff;
  color: #111827;
  font-weight: 400;
}

.partner-email-editor input:read-only {
  background: #eef3f8;
  color: #344256;
}

.partner-email-editor textarea {
  min-height: 96px;
  resize: vertical;
}

.partner-email-editor-heading {
  color: var(--app-primary);
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.partner-email-risk-editor {
  display: grid;
  gap: 8px;
}

.partner-email-risk-grid {
  display: grid;
  grid-template-columns: minmax(112px, 1fr) repeat(3, minmax(0, 0.72fr));
  gap: 6px;
  align-items: center;
  min-width: 0;
}

.partner-email-risk-head,
.partner-email-risk-sector {
  color: rgba(232, 239, 248, 0.78);
  font-size: 0.78rem;
  font-weight: 700;
}

.partner-email-risk-select {
  border-color: rgba(255, 255, 255, 0.7) !important;
  font-weight: 700 !important;
  text-align: center;
}

.partner-email-media-editor {
  display: grid;
}

.partner-email-media-list {
  display: grid;
  gap: 12px;
}

.partner-email-media-row {
  display: grid;
  grid-template-columns: minmax(118px, auto) minmax(0, 1fr);
  gap: 12px;
  min-width: 0;
  align-items: start;
  padding: 10px;
  border: 1px solid rgba(171, 199, 235, 0.12);
  border-radius: var(--app-radius);
  background: rgba(255, 255, 255, 0.025);
}

.partner-email-media-row > * {
  min-width: 0;
}

.partner-email-media-row label:last-child {
  grid-column: 1 / -1;
}

.partner-media-upload-button {
  display: inline-flex !important;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: 1px solid rgba(95, 199, 255, 0.36);
  border-radius: var(--app-radius);
  background: rgba(95, 199, 255, 0.12);
  color: #d9efff !important;
  cursor: pointer;
  font-weight: 600 !important;
  white-space: nowrap;
}

.partner-media-upload-button input {
  display: none;
}

.partner-media-file-name {
  min-height: 40px;
  display: flex;
  align-items: center;
  min-width: 0;
  overflow: hidden;
  color: rgba(232, 239, 248, 0.7);
  font-size: 0.85rem;
  overflow-wrap: anywhere;
}

.partner-media-caption {
  min-height: 72px !important;
}

.partner-add-media-button {
  justify-self: start;
  padding: 9px 12px;
  border-color: rgba(95, 199, 255, 0.32);
  background: rgba(95, 199, 255, 0.1);
  color: #d9efff;
}

.partner-pdf-preview {
  width: min(100%, 760px);
  min-width: 0;
  justify-self: center;
  padding: 10px 24px 22px;
  border: 1px solid rgba(171, 199, 235, 0.18);
  border-radius: var(--app-radius);
  background: #ffffff;
  color: #172033;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 0.78rem;
  line-height: 1.28;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}

.partner-pdf-masthead {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin: 0 -8px 14px;
  padding: 14px 16px;
  background: linear-gradient(90deg, #001b3f, #003e7e);
  color: #ffffff;
}

.partner-pdf-brand {
  display: flex;
  gap: 7px;
  align-items: center;
  text-transform: uppercase;
}

.partner-pdf-brand img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  background: #ffffff;
  border-radius: 50%;
}

.partner-pdf-brand div {
  display: grid;
  line-height: 1.05;
}

.partner-pdf-brand strong {
  font-size: 0.76rem;
  font-weight: 600;
}

.partner-pdf-brand span,
.partner-pdf-brand div > div {
  font-size: 0.48rem;
}

.partner-pdf-meta {
  display: grid;
  gap: 4px;
  text-align: right;
  white-space: nowrap;
}

.partner-pdf-meta strong {
  font-size: 0.78rem;
  font-weight: 500;
}

.partner-pdf-meta span {
  font-size: 0.58rem;
}

.partner-pdf-title {
  display: grid;
  gap: 7px;
  padding-bottom: 11px;
  border-bottom: 2px solid #0b4f8a;
  text-align: center;
}

.partner-pdf-title h3 {
  margin: 0;
  color: #0b4f8a;
  font-size: 1.05rem;
  line-height: 1.18;
}

.partner-pdf-title p {
  margin: 0 auto;
  max-width: 720px;
  color: #3d4b5f;
  text-align: left;
}

.partner-pdf-final-callout {
  display: grid;
  justify-items: center;
  margin-top: 10px;
  text-align: center;
}

.partner-last-brief-button {
  justify-self: center;
  min-height: 32px;
  padding: 5px 14px;
  border: 1px solid #238636;
  border-radius: 999px;
  background: rgba(45, 164, 78, 0.16);
  color: #78dc91;
  font-size: 0.76rem;
  font-weight: 700;
}

.partner-last-brief-button--active {
  background: #2da44e;
  color: #ffffff;
}

.partner-pdf-final-callout strong {
  color: #1a7f37;
  font-size: 0.78rem;
}

.partner-pdf-section {
  margin-top: 11px;
  padding-top: 8px;
  border-top: 1px solid #cfd8e3;
}

.partner-pdf-section h4 {
  margin: 0 0 5px;
  color: #0b4f8a;
  font-size: 0.72rem;
  text-transform: uppercase;
}

.partner-pdf-section ul {
  margin: 0;
  padding-left: 16px;
}

.partner-pdf-risk-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.partner-pdf-risk-table th,
.partner-pdf-risk-table td {
  border: 1px solid #aebdca;
  padding: 4px 5px;
}

.partner-pdf-risk-table thead th,
.partner-pdf-risk-table tbody th {
  background: #dceaf7;
  color: #172033;
  font-weight: 700;
}

.partner-pdf-risk-table thead span {
  display: block;
}

.partner-pdf-risk-table td {
  font-weight: 700;
}

.partner-pdf-risk-note {
  margin: 7px 0 0;
  color: #4b5b70;
  font-size: 0.68rem;
}

.partner-pdf-legend {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  margin-top: 8px;
  font-size: 0.58rem;
  font-weight: 700;
}

.partner-pdf-legend span {
  min-width: 86px;
  padding: 5px 8px;
  text-align: center;
}

.partner-pdf-info p {
  margin: 2px 0;
}

.partner-pdf-media-item + .partner-pdf-media-item {
  margin-top: 8px;
}

.partner-pdf-media-item {
  display: grid;
  justify-items: center;
}

.partner-pdf-media-item img {
  display: block;
  width: min(100%, 660px);
  height: auto;
  max-height: 460px;
  object-fit: contain;
  margin: 0 auto 6px;
  border: 1px solid #cfd8e3;
}

.partner-pdf-media-item p {
  width: min(100%, 660px);
  margin: 4px 0 0;
}

@media (max-width: 1300px) {
  .partner-email-workspace {
    grid-template-columns: 1fr;
  }

  .partner-preview-column,
  .partner-pdf-preview {
    justify-self: stretch;
  }

  .partner-email-column-heading--preview {
    width: 100%;
  }
}

@media (max-width: 820px) {
  .partner-email-media-row {
    grid-template-columns: 1fr;
  }
}
</style>
