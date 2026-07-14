<script setup lang="ts">
import { reactive, ref } from 'vue'
import { exportElementToPdf } from '../utils/exportPdf'

type TimingRow = {
  window: string
  forecast: string
  meaning: string
}

type MediaItem = {
  id: number
  fileName: string
  dataUrl: string
  caption: string
}

const sectorOptions = [
  'Power Grid',
  'Aviation & Radiation',
  'Satellite',
  'Communications & GNSS',
  'Human Spaceflight',
  'Emergency Management',
]

const briefing = reactive({
  issued: 'Fri May 10, 2024 | 1230 UTC',
  productTitle: 'Grid Operations Briefing',
  headline: 'Geomagnetic Disturbance Expected Today into Saturday',
  audience:
    'This briefing is tailored for reliability coordinators, balancing authorities, transmission operators, ISOs/RTOs, and operational coordination groups.',
  overview:
    'A train of CMEs is expected to reach Earth today into Saturday. Significant geomagnetic activity is expected, and warning-level conditions may persist through the weekend. Current analysis continues to show an 80-90% chance that two or more CMEs will impact Earth. G3 to G4 geomagnetic conditions are expected, with a 50-60% chance of G5 conditions.',
  probabilities: [
    {
      level: 'Probability of G3',
      subtitle: 'Strong geomagnetic storming',
      probability: '80-90%',
      tone: 'moderate',
      bullets:
        'G3 conditions are expected during the event window.\nHeightened monitoring is warranted for susceptible systems.\nRegional response may vary with local ground conductivity and system posture.',
    },
    {
      level: 'Probability of G4',
      subtitle: 'Severe geomagnetic storming',
      probability: '50-60%',
      tone: 'high',
      bullets:
        'Severe intervals are possible if CME coupling is favorable.\nVoltage alarms, voltage control issues, or GIC response may become more likely.\nSustained storming would increase operational concern.',
    },
    {
      level: 'Probability of G5',
      subtitle: 'Extreme geomagnetic storming',
      probability: '20-30%',
      tone: 'extreme',
      bullets:
        'Extreme conditions remain possible but less likely.\nConcern increases if multiple CME structures arrive close together.\nUse observed SWPC alerts and local indicators to reassess readiness.',
    },
  ],
  durationConcern:
    'With multiple CMEs expected to arrive, elevated geomagnetic activity could persist for 24 to 48 hours. There is a 70-80% chance of disturbed conditions lasting 24 hours or longer, and a 50-60% chance of disturbed conditions lasting 48 hours or longer.',
  confidence:
    "Confidence is medium to high that significant geomagnetic activity will occur. Confidence is lower in exact peak intensity and duration. The most important uncertainty is how strongly Earth's magnetic environment responds after CME arrival and whether additional CME structures prolong the event.",
  nextUpdate:
    'SWPC will continue issuing Warning Updates at least every 12 hours while the Warning remains in effect, or sooner if observations, impacts, or forecast guidance change.',
  footer: 'For additional information, monitor spaceweather.gov and SWPC decision-support guidance.',
  timingRows: [
    {
      window: 'Fri afternoon-Fri evening UTC',
      forecast: '60-70% chance of initial CME arrival',
      meaning: 'Begin heightened monitoring if not already active',
    },
    {
      window: 'Fri night-early Sat UTC',
      forecast: '20-30% chance of later arrival',
      meaning: 'Maintain readiness through the overnight period',
    },
    {
      window: 'Sat into Sun',
      forecast: 'Additional CME influences likely',
      meaning: 'Prepare for prolonged or repeated disturbance periods',
    },
    {
      window: 'After peak conditions',
      forecast: 'Possible de-escalation to Advisory',
      meaning: 'Continue monitoring until conditions clearly decrease',
    },
  ] as TimingRow[],
  impacts:
    'Voltage alarms or voltage control issues.\nIncreased geomagnetically induced current potential.\nWeak to moderate power system fluctuations.\nGreater concern if severe storming is sustained over multiple hours.\nPossible repeated periods of enhanced geomagnetic activity as additional CME structures arrive.',
  watchItems:
    'SWPC Warning Updates.\nObserved Space Weather Alerts, especially G4 or G5 conditions.\nSolar wind conditions after CME arrival.\nRegional geoelectric field guidance, if available.\nInternal GIC monitors, transformer response, voltage alarms, and local system indicators.\nAny reports from neighboring systems or reliability coordination channels.',
  activeProducts:
    'Space Weather Warning: In effect.\nObserved Space Weather Alerts: Expected if thresholds are reached.\nPartner briefings and Warning Updates: Continuing through the event.',
  media: [
    {
      id: 1,
      fileName: '',
      dataUrl: '',
      caption: '',
    },
  ] as MediaItem[],
})

const selectedSector = ref(sectorOptions[0]!)
const pdfPreviewRef = ref<HTMLElement | null>(null)
let mediaId = 1

function lines(value: string) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function addTimingRow() {
  briefing.timingRows.push({
    window: '',
    forecast: '',
    meaning: '',
  })
}

function removeTimingRow(index: number) {
  briefing.timingRows.splice(index, 1)
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
  exportElementToPdf(pdfPreviewRef.value, 'Partner Tailored Brief')
}

function isTailoredSectorLocked(sector: string) {
  return sector !== 'Power Grid'
}
</script>

<template>
  <section class="tailored-brief">
    <div class="tailored-workspace">
      <nav class="tailored-sector-selector" aria-label="Partner tailored sectors">
        <button
          v-for="sector in sectorOptions"
          :key="sector"
          type="button"
          class="tailored-sector-button"
          :class="{
            'tailored-sector-button--active': selectedSector === sector,
            'tailored-sector-button--locked': isTailoredSectorLocked(sector),
          }"
          :disabled="isTailoredSectorLocked(sector)"
          @click="selectedSector = sector"
        >
          {{ sector }}
        </button>
      </nav>

      <aside class="tailored-editor tailored-editor--forecast" aria-label="Forecast inputs">
        <div class="tailored-column-heading">
          <h2>Forecast</h2>
          <span>{{ selectedSector }}</span>
        </div>

        <section class="tailored-editor-section">
          <h3>Product Setup</h3>
          <label>
            Issue Time
            <input v-model="briefing.issued" type="text" />
          </label>
          <label>
            Product Title
            <input v-model="briefing.productTitle" type="text" />
          </label>
        </section>

        <details class="tailored-editor-section">
          <summary>G-Scale Probabilities</summary>
          <div class="tailored-probability-editor">
            <div
              v-for="card in briefing.probabilities"
              :key="card.level"
              class="tailored-probability-editor-card"
            >
              <label>
                Label
                <input v-model="card.level" type="text" />
              </label>
              <label>
                Subtitle
                <input v-model="card.subtitle" type="text" />
              </label>
              <label>
                Probability
                <input v-model="card.probability" type="text" />
              </label>
              <label>
                Forecast Notes
                <textarea v-model="card.bullets" />
              </label>
            </div>
          </div>
        </details>

        <details class="tailored-editor-section">
          <summary>Timing</summary>
          <div class="tailored-timing-editor">
            <div v-for="(row, index) in briefing.timingRows" :key="index" class="tailored-timing-row">
              <label>
                Timing Window
                <input v-model="row.window" type="text" />
              </label>
              <label>
                Forecast Message
                <input v-model="row.forecast" type="text" />
              </label>
              <label>
                Operational Meaning
                <input v-model="row.meaning" type="text" />
              </label>
              <button
                v-if="briefing.timingRows.length > 1"
                class="tailored-remove-button"
                type="button"
                @click="removeTimingRow(index)"
              >
                Remove
              </button>
            </div>
          </div>
          <button class="tailored-add-button" type="button" @click="addTimingRow">Add Timing Row</button>
        </details>

        <section class="tailored-editor-section">
          <h3>Products / Updates</h3>
          <label>
            Active Products
            <textarea v-model="briefing.activeProducts" />
          </label>
          <label>
            Next Update
            <textarea v-model="briefing.nextUpdate" class="tailored-short-textarea" />
          </label>
        </section>
      </aside>

      <aside class="tailored-editor tailored-editor--narrative" aria-label="Narrative inputs">
        <div class="tailored-column-heading">
          <h2>Narrative</h2>
          <span>Forecaster review</span>
        </div>

        <section class="tailored-editor-section">
          <h3>Header Copy</h3>
          <label>
            Headline
            <textarea v-model="briefing.headline" class="tailored-short-textarea" />
          </label>
          <label>
            Partner Disclaimer
            <textarea v-model="briefing.audience" class="tailored-short-textarea" />
          </label>
        </section>

        <section class="tailored-editor-section tailored-review-section">
          <h3>Synopsis</h3>
          <label>
            Forecaster-reviewed synopsis
            <textarea v-model="briefing.overview" />
          </label>
        </section>

        <section class="tailored-editor-section tailored-review-section">
          <h3>Confidence and Uncertainty</h3>
          <label>
            Forecaster-reviewed confidence language
            <textarea v-model="briefing.confidence" />
          </label>
        </section>

        <section class="tailored-editor-section tailored-review-section">
          <h3>Duration Concern</h3>
          <label>
            Forecaster-reviewed duration language
            <textarea v-model="briefing.durationConcern" />
          </label>
        </section>

        <details class="tailored-editor-section">
          <summary>Operational Narrative</summary>
          <label>
            Potential Grid-Relevant Impacts
            <textarea v-model="briefing.impacts" />
          </label>
          <label>
            What Operators Should Watch
            <textarea v-model="briefing.watchItems" />
          </label>
          <label>
            Footer
            <textarea v-model="briefing.footer" class="tailored-short-textarea" />
          </label>
        </details>

        <details class="tailored-editor-section tailored-media-editor" open>
          <summary>Media</summary>
          <div class="tailored-media-list">
            <div v-for="item in briefing.media" :key="item.id" class="tailored-media-row">
              <label class="tailored-media-upload-button">
                Upload Image
                <input type="file" accept="image/*" @change="handleMediaUpload(item, $event)" />
              </label>
              <span class="tailored-media-file-name">{{ item.fileName || 'No image selected' }}</span>
              <label>
                Image Caption
                <textarea v-model="item.caption" class="tailored-media-caption" />
              </label>
            </div>
          </div>
          <button class="tailored-add-button" type="button" @click="addMediaItem">
            Add More Media
          </button>
        </details>
      </aside>

      <div class="tailored-preview-column">
        <div class="tailored-column-heading tailored-column-heading--preview">
          <div>
            <h2>Preview</h2>
            <span>Generated product</span>
          </div>
          <button class="tailored-export-button" type="button" @click="exportBriefingPdf">
            Export PDF
          </button>
        </div>

      <article ref="pdfPreviewRef" class="tailored-brief-page" aria-label="Grid operations tailored briefing">
      <header class="tailored-masthead">
        <div class="tailored-brand">
          <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
          <img src="/assets/visual-finder/logos/NWSlogo.png" alt="National Weather Service" />
          <div>
            <div>National Weather Service</div>
            <strong>Space Weather Prediction Center</strong>
            <span>National Oceanic and Atmospheric Administration</span>
          </div>
        </div>
        <div class="tailored-meta">
          <strong>{{ briefing.productTitle }}</strong>
          <span>{{ briefing.issued }}</span>
        </div>
      </header>

      <section class="tailored-hero">
        <h1>{{ briefing.headline }}</h1>
        <p>{{ briefing.audience }}</p>
      </section>

      <section class="tailored-section">
        <p>{{ briefing.overview }}</p>
      </section>

      <section class="tailored-section">
        <h3>Storm-Level Probability</h3>
        <div class="tailored-probability-grid">
          <article
            v-for="card in briefing.probabilities"
            :key="card.level"
            class="tailored-probability-card"
            :class="`tailored-probability-card--${card.tone}`"
          >
            <h4>{{ card.level }}</h4>
            <strong>{{ card.subtitle }}</strong>
            <ul>
              <li v-for="item in lines(card.bullets)" :key="item">{{ item }}</li>
            </ul>
            <div class="tailored-probability-value">{{ card.probability }}</div>
          </article>
        </div>
      </section>

      <section class="tailored-section">
        <h3>Key Timing</h3>
        <table class="tailored-table">
          <thead>
            <tr>
              <th>Timing Window</th>
              <th>Forecast Message</th>
              <th>Operational Meaning</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in briefing.timingRows" :key="`${row.window}-${row.forecast}`">
              <td>{{ row.window }}</td>
              <td>{{ row.forecast }}</td>
              <td>{{ row.meaning }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="tailored-section">
        <h3>Duration Concern</h3>
        <p>{{ briefing.durationConcern }}</p>
      </section>

      <section class="tailored-section">
        <h3>Confidence and Uncertainty</h3>
        <p>{{ briefing.confidence }}</p>
      </section>

      <section class="tailored-section tailored-grid">
        <div>
          <h3>Potential Grid-Relevant Impacts</h3>
          <ul>
            <li v-for="item in lines(briefing.impacts)" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div>
          <h3>What Operators Should Watch</h3>
          <ul>
            <li v-for="item in lines(briefing.watchItems)" :key="item">{{ item }}</li>
          </ul>
        </div>
      </section>

      <section class="tailored-section tailored-grid">
        <div>
          <h3>Active Products</h3>
          <ul>
            <li v-for="item in lines(briefing.activeProducts)" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div>
          <h3>Next Update</h3>
          <p>{{ briefing.nextUpdate }}</p>
        </div>
      </section>

      <section class="tailored-section" v-if="briefing.media.some((item) => item.dataUrl || item.fileName || item.caption)">
        <h3>Media</h3>
        <div v-for="item in briefing.media" :key="item.id" class="tailored-pdf-media-item">
          <img v-if="item.dataUrl" :src="item.dataUrl" :alt="item.caption || item.fileName || 'Uploaded media'" />
          <strong v-else-if="item.fileName">{{ item.fileName }}</strong>
          <p v-if="item.caption">{{ item.caption }}</p>
        </div>
      </section>

      <footer class="tailored-footer">
        {{ briefing.footer }}
      </footer>
      </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tailored-brief {
  display: grid;
  gap: 14px;
  align-items: start;
  min-width: 0;
}

.tailored-sector-selector {
  display: grid;
  gap: 8px;
  align-content: start;
  min-width: 0;
}

.tailored-sector-button {
  width: 100%;
  min-height: 32px;
  padding: 0 14px;
  border: 1px solid rgba(210, 218, 230, 0.18);
  border-radius: 6px;
  background: rgba(145, 153, 166, 0.24);
  color: rgba(231, 236, 244, 0.78);
  font-size: 0.84rem;
  font-weight: 400;
  letter-spacing: 0;
}

.tailored-sector-button--active {
  border-color: rgba(255, 229, 94, 0.38);
  background: #0b3f73;
  color: #ffe55e;
  box-shadow: inset 0 0 0 1px rgba(255, 229, 94, 0.38);
}

.tailored-sector-button:not(.tailored-sector-button--active):not(:disabled):hover {
  background: rgba(178, 187, 201, 0.32);
  color: rgba(255, 255, 255, 0.9);
}

.tailored-sector-button--locked,
.tailored-sector-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.tailored-workspace {
  display: grid;
  grid-template-columns: minmax(150px, 180px) repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
  min-width: 0;
}

.tailored-editor {
  display: grid;
  gap: 12px;
  min-width: 0;
  align-content: start;
}

.tailored-column-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
  padding: 0 2px;
}

.tailored-column-heading > div {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.tailored-column-heading h2 {
  margin: 0;
  color: #e8eff8;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.tailored-column-heading span {
  min-width: 0;
  color: rgba(232, 239, 248, 0.58);
  font-size: 0.78rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tailored-preview-column {
  display: grid;
  gap: 8px;
  min-width: 0;
  justify-items: center;
}

.tailored-column-heading--preview {
  width: 100%;
  align-items: center;
}

.tailored-export-button {
  border: 1px solid rgba(95, 199, 255, 0.32);
  background: rgba(95, 199, 255, 0.12);
  color: #d9efff;
  font-weight: 400;
}

.tailored-editor-section {
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

.tailored-editor-section[open] {
  gap: 12px;
}

.tailored-editor-section:not([open]) {
  gap: 0;
}

.tailored-editor-section h3 {
  margin: 0;
  color: var(--app-primary);
  font-size: 0.86rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.tailored-editor-section summary {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--app-primary);
  cursor: pointer;
  font-size: 0.86rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  list-style: none;
  text-transform: uppercase;
}

.tailored-editor-section summary::-webkit-details-marker {
  display: none;
}

.tailored-editor-section summary::after {
  content: ">";
  flex: 0 0 auto;
  color: var(--app-primary);
  font-size: 0.82rem;
  transform: rotate(90deg);
  transition: transform 120ms ease;
}

.tailored-editor-section:not([open]) summary::after {
  transform: rotate(0deg);
}

.tailored-review-section {
  border-color: rgba(255, 229, 100, 0.54);
  background:
    linear-gradient(180deg, rgba(255, 229, 100, 0.12), rgba(255, 229, 100, 0.04)),
    rgba(4, 10, 18, 0.32);
}

.tailored-review-section h3 {
  color: #ffe564;
}

.tailored-editor label {
  display: grid;
  gap: 6px;
  min-width: 0;
  color: rgba(232, 239, 248, 0.78);
  font-weight: 400;
}

.tailored-editor input,
.tailored-editor textarea {
  display: block;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  border-color: rgba(171, 199, 235, 0.58);
  background: #ffffff;
  color: #111827;
  font-weight: 400;
}

.tailored-editor textarea {
  min-height: 106px;
  resize: vertical;
}

.tailored-short-textarea {
  min-height: 70px !important;
}

.tailored-timing-editor {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.tailored-probability-editor {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.tailored-probability-editor-card {
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(95, 199, 255, 0.16);
  border-radius: calc(var(--app-radius) - 2px);
  background: rgba(2, 8, 15, 0.22);
}

.tailored-timing-row {
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(95, 199, 255, 0.16);
  border-radius: calc(var(--app-radius) - 2px);
  background: rgba(2, 8, 15, 0.22);
}

.tailored-media-editor {
  align-content: start;
}

.tailored-media-list {
  display: grid;
  gap: 12px;
}

.tailored-media-row {
  display: grid;
  grid-template-columns: minmax(118px, auto) minmax(0, 1fr);
  gap: 12px;
  min-width: 0;
  align-items: start;
  padding: 10px;
  border: 1px solid rgba(95, 199, 255, 0.16);
  border-radius: calc(var(--app-radius) - 2px);
  background: rgba(2, 8, 15, 0.22);
}

.tailored-media-row > * {
  min-width: 0;
}

.tailored-media-row label:last-child {
  grid-column: 1 / -1;
}

.tailored-media-upload-button {
  display: inline-flex !important;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  border: 1px solid rgba(255, 229, 100, 0.42);
  border-radius: 6px;
  background: rgba(255, 229, 100, 0.12);
  color: #fff0a8 !important;
  cursor: pointer;
  font-weight: 600 !important;
}

.tailored-media-upload-button input {
  display: none;
}

.tailored-media-file-name {
  align-self: center;
  overflow: hidden;
  color: rgba(232, 239, 248, 0.72);
  font-size: 0.82rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tailored-media-caption {
  min-height: 76px !important;
}

.tailored-add-button,
.tailored-remove-button {
  justify-self: start;
  border: 1px solid rgba(95, 199, 255, 0.24);
  background: rgba(95, 199, 255, 0.13);
  color: #d7ecff;
  font-weight: 400;
}

.tailored-remove-button {
  background: rgba(255, 111, 111, 0.12);
  color: #ffd7d7;
}

.tailored-brief-page {
  width: min(100%, 760px);
  min-width: 0;
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

.tailored-masthead {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin: 0 -8px 14px;
  padding: 14px 16px;
  background: linear-gradient(90deg, #001b3f, #003e7e);
  color: #ffffff;
}

.tailored-brand {
  display: flex;
  gap: 7px;
  align-items: center;
  text-transform: uppercase;
}

.tailored-brand img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  background: #ffffff;
  border-radius: 50%;
}

.tailored-brand div {
  display: grid;
  line-height: 1.05;
}

.tailored-brand strong {
  font-size: 0.76rem;
  font-weight: 600;
}

.tailored-brand span,
.tailored-brand div > div {
  font-size: 0.48rem;
}

.tailored-meta {
  display: grid;
  gap: 4px;
  text-align: right;
  white-space: nowrap;
}

.tailored-meta strong {
  font-size: 0.78rem;
  font-weight: 500;
  text-transform: uppercase;
}

.tailored-meta span {
  font-size: 0.58rem;
}

.tailored-hero {
  display: grid;
  gap: 7px;
  padding-bottom: 11px;
  border-bottom: 2px solid #0b4f8a;
  text-align: center;
}

.tailored-hero h1 {
  margin: 0;
  color: #0b4f8a;
  font-size: 1.05rem;
  line-height: 1.18;
}

.tailored-hero p {
  max-width: 860px;
  margin: 0 auto;
  color: #3d4b5f;
  text-align: left;
}

.tailored-section {
  margin-top: 11px;
  padding-top: 8px;
  border-top: 1px solid #cfd8e3;
}

.tailored-section h3 {
  margin: 0 0 5px;
  color: #0b4f8a;
  font-size: 0.72rem;
  text-transform: uppercase;
}

.tailored-section p,
.tailored-section ul {
  margin: 0;
}

.tailored-section ul {
  padding-left: 16px;
}

.tailored-table {
  width: 100%;
  border-collapse: collapse;
}

.tailored-probability-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 7px;
}

.tailored-probability-card {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 8px;
  border: 1px solid #d0dce8;
  border-radius: 8px;
  background: #f7fbff;
  color: #172033;
}

.tailored-probability-card h4,
.tailored-probability-card strong,
.tailored-probability-card ul {
  margin: 0;
}

.tailored-probability-card h4 {
  color: #0b4f8a;
  font-size: 0.58rem;
  text-transform: uppercase;
}

.tailored-probability-card strong {
  font-size: 0.66rem;
}

.tailored-probability-card ul {
  padding-left: 13px;
  font-size: 0.58rem;
}

.tailored-probability-value {
  align-self: end;
  margin-top: 4px;
  color: #0b4f8a;
  font-size: 0.9rem;
  font-weight: 700;
  text-align: center;
}

.tailored-probability-card--moderate {
  border-color: #f3b64e;
  background: #fff7e6;
}

.tailored-probability-card--moderate .tailored-probability-value {
  color: #b56a00;
}

.tailored-probability-card--high {
  border-color: #f07070;
  background: #fff0f0;
}

.tailored-probability-card--high .tailored-probability-value {
  color: #c42d2d;
}

.tailored-probability-card--extreme {
  border-color: #bf70f0;
  background: #f8f0ff;
}

.tailored-probability-card--extreme .tailored-probability-value {
  color: #8f2dcc;
}

.tailored-table th,
.tailored-table td {
  border: 1px solid #aebdca;
  padding: 4px 5px;
  color: #172033 !important;
  text-align: left;
}

.tailored-table th {
  background: #dceaf7;
  font-weight: 700;
}

.tailored-table td {
  background: #ffffff;
}

.tailored-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.tailored-pdf-media-item + .tailored-pdf-media-item {
  margin-top: 10px;
}

.tailored-pdf-media-item img {
  display: block;
  width: 100%;
  max-height: 280px;
  object-fit: contain;
  border: 1px solid #d8e0ea;
  background: #f7fbff;
}

.tailored-pdf-media-item strong {
  color: #172033;
}

.tailored-pdf-media-item p {
  margin-top: 5px;
  color: #3d4b5f;
  font-size: 0.72rem;
}

.tailored-footer {
  margin-top: 11px;
  padding-top: 8px;
  border-top: 2px solid #0b4f8a;
  color: #3d4b5f;
  font-weight: 700;
}

@media (max-width: 1280px) {
  .tailored-workspace {
    grid-template-columns: 1fr;
  }

  .tailored-sector-selector {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .tailored-preview-column,
  .tailored-brief-page {
    justify-self: center;
  }

}

@media (max-width: 800px) {
  .tailored-grid,
  .tailored-probability-grid {
    grid-template-columns: 1fr;
  }

  .tailored-media-row {
    grid-template-columns: 1fr;
  }

  .tailored-masthead {
    display: grid;
  }

  .tailored-meta {
    text-align: left;
    white-space: normal;
  }
}
</style>
