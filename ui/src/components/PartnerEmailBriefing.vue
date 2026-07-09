<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { exportElementToPdf } from '../utils/exportPdf'

type RiskLevel = 'Little to None' | 'Minor' | 'Moderate' | 'Major' | 'Extreme'

const riskLevels: { label: RiskLevel; color: string; text: string }[] = [
  { label: 'Little to None', color: '#a8e6a1', text: '#102316' },
  { label: 'Minor', color: '#ffe564', text: '#111827' },
  { label: 'Moderate', color: '#ff9838', text: '#111827' },
  { label: 'Major', color: '#e84f4f', text: '#ffffff' },
  { label: 'Extreme', color: '#a027d7', text: '#ffffff' },
]

const sectors = [
  'Power Grid',
  'Aviation',
  'Satellite',
  'Communications & GNSS',
  'Human Spaceflight',
  'Emergency Management',
]
const days = ['Day 1\nApr 13 (Mon)', 'Day 2\nApr 14 (Tue)', 'Day 3\nApr 15 (Wed)']

type MediaItem = {
  id: number
  fileName: string
  dataUrl: string
  caption: string
}

function formatIssueTime(date: Date): string {
  const month = date.toLocaleString('en-US', { month: 'short', timeZone: 'UTC' })
  const day = date.toLocaleString('en-US', { day: '2-digit', timeZone: 'UTC' })
  const year = date.toLocaleString('en-US', { year: 'numeric', timeZone: 'UTC' })
  const hour = date.getUTCHours().toString().padStart(2, '0')
  const minute = date.getUTCMinutes().toString().padStart(2, '0')
  return `${month} ${day}, ${year} ${hour}${minute} UTC`
}

const briefing = reactive({
  dateTime: formatIssueTime(new Date()),
  headline: 'Elevated Geomagnetic Activity Possible Late Thursday into Friday',
  summary:
    'A high-speed solar wind stream from a coronal hole is expected to reach Earth late Thursday into Friday. This may lead to elevated geomagnetic activity, with G1-G2 (Minor to Moderate) storm levels possible, primarily on Friday. Conditions are expected to improve by Saturday. No significant solar flares are anticipated.',
  keyPoints:
    'A high-speed solar wind stream is expected to reach Earth late Thursday into Friday.\nG1-G2 (Minor to Moderate) geomagnetic storm levels are possible, mainly on Friday.\nConfidence is moderate in the timing; low to moderate in the magnitude.\nSectors of interest: power grid, aviation, satellite, communications and GNSS, human spaceflight, and emergency management partners.\nConditions are expected to calm by Saturday.',
  activeProducts:
    'Geomagnetic Storm Watch: 14 Apr 0000 UTC - 15 Apr 2359 UTC\nSpace Weather Summary: In Effect\nRadiation Storm Warning: None',
  impacts:
    'Periods of voltage control issues and false alarms on the power grid.\nDegraded HF radio communications at higher latitudes, especially on polar routes.\nIncreased range error in GNSS positioning at higher latitudes.\nIncreased drag on low Earth orbit satellites may require maneuvering.\nAurora may be visible at higher latitudes in the Northern Hemisphere on Friday night.',
  watchNext:
    'Monitor updates for changes to timing and geomagnetic storm levels.\nCheck for additional watches or warnings as conditions evolve.\nFollow SWPC social media and website for the latest information.',
  info:
    'For the latest forecasts, alerts, and space weather information, visit www.spaceweather.gov.\nQuestions or to report impacts, contact SWPC at swpc.customersupport@noaa.gov or (303) 497-0016.\nYou are receiving this email because you are a valued space weather partner.',
  media: [
    {
      id: 1,
      fileName: '',
      dataUrl: '',
      caption: '',
    },
  ] as MediaItem[],
  riskOutlook: Object.fromEntries(
    sectors.map((sector) => [
      sector,
      sector === 'Aviation' || sector === 'Human Spaceflight'
        ? ['Little to None', 'Little to None', 'Minor']
        : sector === 'Satellite'
          ? ['Little to None', 'Minor', 'Minor']
          : ['Little to None', 'Minor', 'Moderate'],
    ]),
  ) as Record<string, RiskLevel[]>,
})

let mediaId = 1
let issueClock: number | undefined
const pdfPreviewRef = ref<HTMLElement | null>(null)

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

function updateIssueTime() {
  briefing.dateTime = formatIssueTime(new Date())
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

onMounted(() => {
  updateIssueTime()
  issueClock = window.setInterval(updateIssueTime, 30_000)
})

onBeforeUnmount(() => {
  if (issueClock !== undefined) {
    window.clearInterval(issueClock)
  }
})
</script>

<template>
  <section class="partner-email-briefing">
    <div class="partner-email-layout">
      <aside class="partner-email-editor" aria-label="Forecaster briefing inputs">
        <details class="partner-email-input-section" open>
          <summary class="partner-email-editor-heading">Briefing Header</summary>
          <label>
            Issue Time
            <input :value="briefing.dateTime" type="text" readonly />
          </label>

          <label>
            Headline
            <input v-model="briefing.headline" type="text" />
          </label>

          <label>
            Summary
            <textarea v-model="briefing.summary" />
          </label>
        </details>

        <details class="partner-email-input-section" open>
          <summary class="partner-email-editor-heading">Briefing Body</summary>
          <label>
            Key Points
            <textarea v-model="briefing.keyPoints" />
          </label>

          <label>
            Active Products
            <span class="partner-email-field-note">Future feed: auto-populated from SWIFT Suite product JSON APIs.</span>
            <textarea v-model="briefing.activeProducts" />
          </label>

          <label>
            Potential Impacts
            <textarea v-model="briefing.impacts" />
          </label>

          <label>
            What To Watch Next
            <textarea v-model="briefing.watchNext" />
          </label>
        </details>

        <details class="partner-email-input-section partner-email-risk-editor" open>
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
                @change="handleRiskChange(sector, index, $event)"
              >
                <option v-for="risk in riskLevels" :key="risk.label" :value="risk.label">
                  {{ risk.label }}
                </option>
              </select>
            </template>
          </div>
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
        <div class="partner-preview-actions">
          <button class="partner-export-button" type="button" @click="exportBriefingPdf">
            Export PDF
          </button>
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
            <span>{{ briefing.dateTime }}</span>
          </div>
        </header>

        <section class="partner-pdf-title">
          <h3>{{ briefing.headline }}</h3>
          <p>{{ briefing.summary }}</p>
        </section>

        <section class="partner-pdf-section">
          <h4>Key Points</h4>
          <ul>
            <li v-for="item in lines(briefing.keyPoints)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
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
          <h4>Potential Impacts</h4>
          <ul>
            <li v-for="item in lines(briefing.impacts)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
          <h4>What To Watch Next</h4>
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

.partner-email-layout {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(420px, 2fr);
  gap: 16px;
  align-items: start;
  min-width: 0;
}

.partner-email-editor {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.partner-preview-column {
  display: grid;
  gap: 10px;
  min-width: 0;
  justify-items: center;
}

.partner-preview-actions {
  width: min(100%, 860px);
  display: flex;
  justify-content: flex-end;
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
  background: rgba(2, 8, 15, 0.96);
  color: #e8eff8;
  font-weight: 400;
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
  grid-template-columns: minmax(120px, 1fr) repeat(3, minmax(0, 0.75fr));
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

.partner-email-media-editor {
  display: grid;
}

.partner-email-media-list {
  display: grid;
  gap: 12px;
}

.partner-email-media-row {
  display: grid;
  grid-template-columns: minmax(120px, auto) minmax(0, 0.4fr) minmax(0, 1fr);
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
  width: min(100%, 860px);
  min-width: 0;
  justify-self: center;
  padding: 18px 42px 28px;
  background: #ffffff;
  color: #111827;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 14px;
  line-height: 1.28;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}

.partner-pdf-masthead {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin: 0 -18px 18px;
  padding: 16px 18px;
  background: linear-gradient(90deg, #003f86, #002d62);
  color: #ffffff;
}

.partner-pdf-brand {
  display: flex;
  gap: 10px;
  align-items: center;
  text-transform: uppercase;
}

.partner-pdf-brand img {
  width: 52px;
  height: 52px;
  object-fit: contain;
  background: #ffffff;
  border-radius: 999px;
}

.partner-pdf-brand div {
  display: grid;
  line-height: 1.05;
}

.partner-pdf-brand strong {
  font-size: 18px;
}

.partner-pdf-brand span,
.partner-pdf-brand div > div {
  font-size: 11px;
}

.partner-pdf-meta {
  display: grid;
  gap: 4px;
  text-align: right;
  white-space: nowrap;
}

.partner-pdf-meta strong {
  font-size: 18px;
  font-weight: 500;
}

.partner-pdf-title {
  display: grid;
  gap: 8px;
  text-align: center;
}

.partner-pdf-title h3 {
  margin: 0;
  color: #0052b5;
  font-size: 22px;
  line-height: 1.18;
}

.partner-pdf-title p {
  margin: 8px auto 0;
  max-width: 720px;
  text-align: left;
}

.partner-pdf-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #cfd8e3;
}

.partner-pdf-section h4 {
  margin: 0 0 6px;
  color: #0052b5;
  font-size: 17px;
  text-transform: uppercase;
}

.partner-pdf-section ul {
  margin: 0;
  padding-left: 24px;
}

.partner-pdf-risk-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.partner-pdf-risk-table th,
.partner-pdf-risk-table td {
  border: 3px solid #ffffff;
  padding: 8px;
}

.partner-pdf-risk-table thead th,
.partner-pdf-risk-table tbody th {
  background: #e5e7eb;
  color: #111827;
  font-weight: 700;
}

.partner-pdf-risk-table thead span {
  display: block;
}

.partner-pdf-risk-table td {
  font-weight: 700;
}

.partner-pdf-legend {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
  font-size: 12px;
  font-weight: 700;
}

.partner-pdf-legend span {
  min-width: 112px;
  padding: 7px 10px;
  text-align: center;
}

.partner-pdf-info p {
  margin: 2px 0;
}

.partner-pdf-media-item + .partner-pdf-media-item {
  margin-top: 8px;
}

.partner-pdf-media-item img {
  display: block;
  max-width: 100%;
  max-height: 260px;
  object-fit: contain;
  margin: 0 auto 6px;
  border: 1px solid #cfd8e3;
}

.partner-pdf-media-item p {
  margin: 4px 0 0;
}

@media (max-width: 1300px) {
  .partner-email-layout {
    grid-template-columns: 1fr;
  }

  .partner-preview-column,
  .partner-pdf-preview {
    justify-self: stretch;
  }

  .partner-preview-actions {
    width: 100%;
  }
}

@media (max-width: 820px) {
  .partner-email-media-row {
    grid-template-columns: 1fr;
  }
}
</style>
