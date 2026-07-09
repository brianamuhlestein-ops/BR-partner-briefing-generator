<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import type { GraphicsWorkspaceMode, OpsToCommsRecommendation } from '../../types'

type SocialProductId =
  | 'outlook'
  | 'statement'
  | 'watch'
  | 'advisory'
  | 'warning'
  | 'observed_alert'
  | 'notice'
  | 'summary'

type SocialTemplate = {
  id: SocialProductId
  label: string
  badge: string
  color: string
  headline: string
  subheadline: string
  issueTime: string
  summary: string
  confidenceLabel: string
  confidenceValue: string
  confidenceDetail: string
  whatWeKnow: string
  impactIcons: string[]
  footerLeft: string
  footerCenter: string
  footerRight: string
  imagePlaceholder: string
}

defineProps<{
  mode: GraphicsWorkspaceMode
  presentation?: 'default' | 'social-tab'
  recommendation?: OpsToCommsRecommendation | null
}>()

const templates: SocialTemplate[] = [
  {
    id: 'outlook',
    label: 'Outlook',
    badge: 'SPACE WEATHER OUTLOOK',
    color: '#1E73BE',
    headline: 'Active Space Weather Conditions Expected This Week',
    subheadline: 'Planning outlook for May 6-12',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'Space weather activity may increase this week as solar activity and geomagnetic conditions remain under review.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium',
    confidenceDetail: 'Forecast confidence will be updated as new model guidance arrives.',
    whatWeKnow:
      'Active solar regions remain under monitoring.\nGeomagnetic activity may increase later in the outlook period.\nPartners should monitor SWPC updates for watches or warnings.\nForecast confidence may change with new observations.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aurora'],
    footerLeft: 'Outlooks are issued once weekly on Mondays.',
    footerCenter: 'Monitor SWPC products for changes.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'statement',
    label: 'Statement',
    badge: 'SPACE WEATHER STATEMENT',
    color: '#0065B3',
    headline: 'CME Under Analysis',
    subheadline: 'Forecast confidence may change',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'SWPC is analyzing solar activity and possible Earth-directed impacts. Additional products may be issued if confidence increases.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Low to Medium',
    confidenceDetail: 'Timing, strength, and duration remain uncertain.',
    whatWeKnow:
      'A solar event is under analysis.\nInitial model guidance is being reviewed.\nNo warning-level product is in effect unless separately issued.\nUpdates will follow as confidence changes.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites'],
    footerLeft: 'SWPC is analyzing the event and will issue updates as confidence changes.',
    footerCenter: 'No Watch or Warning in effect at this time.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'watch',
    label: 'Watch',
    badge: 'SPACE WEATHER WATCH',
    color: '#F4B000',
    headline: 'Significant Geomagnetic Activity Possible',
    subheadline: 'Friday into the weekend',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'A CME sequence may reach Earth and produce significant geomagnetic activity. Confidence and timing will be refined with new observations.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: 'Potential for G3 or greater conditions is credible.',
    whatWeKnow:
      '70-80% chance of initial arrival Friday afternoon into Friday night.\nMultiple CME influences may continue into the weekend.\nG3 to G4 conditions are possible.\nElevated activity could persist 24-48 hours.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aurora'],
    footerLeft: 'Watch will be updated at least every 12 hours.',
    footerCenter: 'Monitor SWPC updates as confidence changes.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'advisory',
    label: 'Advisory',
    badge: 'SPACE WEATHER ADVISORY',
    color: '#F28C28',
    headline: 'Lingering Geomagnetic Activity',
    subheadline: 'Elevated conditions continue',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'Elevated space weather conditions continue, but the primary warning-level concern has decreased.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: 'Conditions are expected to gradually decrease.',
    whatWeKnow:
      'Advisory-level conditions remain possible.\nResidual impacts may continue for susceptible systems.\nConditions are expected to decrease with time.\nPartners should continue routine monitoring.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aviation'],
    footerLeft: 'Advisory replaces the previous Warning.',
    footerCenter: 'Continue monitoring SWPC products as conditions decrease.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'warning',
    label: 'Warning',
    badge: 'SPACE WEATHER WARNING',
    color: '#D94A1E',
    headline: 'Significant Geomagnetic Activity Expected',
    subheadline: 'Friday into the weekend',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'Multiple CMEs are expected to reach Earth and cause significant geomagnetic activity. Severe intervals are possible if coupling is favorable.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: '80-90% chance that two or more CMEs will impact Earth.',
    whatWeKnow:
      '70-80% chance of initial arrival Friday afternoon into Friday night.\n20-30% chance of arrival as early as midday Friday.\nG3 to G4 conditions expected; G5 conditions possible.\nElevated geomagnetic activity could persist 36-48 hours.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aurora'],
    footerLeft: 'Warning will be updated at least every 12 hours while in effect.',
    footerCenter: 'Monitor SWPC updates and follow sector-specific procedures.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'observed_alert',
    label: 'Observed Alert',
    badge: 'OBSERVED SPACE WEATHER ALERT',
    color: '#B31B1B',
    headline: 'Strong Geomagnetic Conditions Reached',
    subheadline: 'Observed threshold reached',
    issueTime: 'Observed Jul 09, 2026 2036 UTC',
    summary: 'Observed geomagnetic conditions have reached an event-level alert threshold based on official monitoring.',
    confidenceLabel: 'Observed',
    confidenceValue: 'G3 at 2036 UTC',
    confidenceDetail: 'Based on official space weather observations.',
    whatWeKnow:
      'Observed threshold has been reached.\nWarning remains in effect if separately issued.\nConditions may fluctuate during the event.\nAdditional alerts may be issued if higher thresholds are reached.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aurora'],
    footerLeft: 'Event-level alert issued.',
    footerCenter: 'Warning remains in effect.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'notice',
    label: 'Notice',
    badge: 'SPACE WEATHER NOTICE',
    color: '#5C6B7A',
    headline: 'CME Analysis May Be Affected',
    subheadline: 'Coronagraph imagery degraded',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'A data availability issue may affect timeliness or confidence in solar event analysis. Official products remain valid unless updated.',
    confidenceLabel: 'Status',
    confidenceValue: 'Ongoing',
    confidenceDetail: 'Forecast updates continue while data availability is degraded.',
    whatWeKnow:
      'A forecast-support data source is degraded.\nCME analysis may be delayed or less certain.\nOfficial products remain in effect.\nMonitor SWPC products for changes.',
    impactIcons: ['Notice', 'Time', 'Status'],
    footerLeft: 'Forecast updates continue.',
    footerCenter: 'Monitor SWPC products for changes.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'summary',
    label: 'Summary',
    badge: 'SPACE WEATHER SUMMARY',
    color: '#0065B3',
    headline: 'Significant Space Weather Event Ongoing',
    subheadline: 'Mid-event recap',
    issueTime: 'Issued Jul 09, 2026 2036 UTC',
    summary: 'SWPC continues to monitor an ongoing space weather event. This graphic summarizes current status and observed conditions.',
    confidenceLabel: 'Status',
    confidenceValue: 'Warning in Effect',
    confidenceDetail: 'Current status is based on active SWPC products.',
    whatWeKnow:
      'Event remains ongoing.\nObserved conditions and forecast guidance continue to be reviewed.\nSome operational areas may remain affected.\nAdditional updates will follow as conditions change.',
    impactIcons: ['Power', 'HF Radio', 'GNSS', 'Satellites', 'Aurora'],
    footerLeft: 'SWPC will continue to monitor the Sun and near-Earth space environment.',
    footerCenter: 'Partners should monitor active products.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
]

const selectedProductId = ref<SocialProductId>('warning')
const uploadedImage = ref('')
const uploadedImageName = ref('')

const selectedTemplate = computed(() => {
  return templates.find((template) => template.id === selectedProductId.value) ?? templates[0]!
})

const draft = reactive({ ...selectedTemplate.value })

const whatWeKnowLines = computed(() => lines(draft.whatWeKnow).slice(0, 5))
const impactLabels = computed(() => draft.impactIcons.slice(0, 6))
const impactIconsText = computed({
  get: () => draft.impactIcons.join(', '),
  set: (value: string) => {
    draft.impactIcons = value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
  },
})

watch(selectedTemplate, (template) => {
  Object.assign(draft, template)
  uploadedImage.value = ''
  uploadedImageName.value = ''
})

function lines(value: string) {
  return value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0]
  uploadedImageName.value = file?.name ?? ''
  uploadedImage.value = ''

  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.addEventListener('load', () => {
    uploadedImage.value = typeof reader.result === 'string' ? reader.result : ''
  })
  reader.readAsDataURL(file)
}
</script>

<template>
  <section class="swift-social-workspace">
    <header class="swift-social-product-row">
      <div class="swift-social-product-buttons" aria-label="Social media product type">
        <button
          v-for="template in templates"
          :key="template.id"
          type="button"
          class="swift-social-product-button"
          :class="{ 'swift-social-product-button--active': selectedProductId === template.id }"
          :style="selectedProductId === template.id ? { borderColor: template.color } : undefined"
          @click="selectedProductId = template.id"
        >
          {{ template.label }}
        </button>
      </div>

      <span class="swift-social-product-source">SWIFT WWA JSON driven</span>
    </header>

    <div class="swift-social-grid">
      <aside class="swift-social-panel swift-social-json-panel">
        <div class="swift-social-heading">
          <h2>Product JSON</h2>
          <span>WWA rendering.social_media</span>
        </div>

        <label>
          Product Badge
          <input v-model="draft.badge" type="text" />
        </label>
        <label>
          Headline
          <textarea v-model="draft.headline" class="swift-social-short-textarea" />
        </label>
        <label>
          Subheadline
          <input v-model="draft.subheadline" type="text" />
        </label>
        <label>
          Issue Time
          <input v-model="draft.issueTime" type="text" />
        </label>
        <label>
          What We Know
          <textarea v-model="draft.whatWeKnow" />
        </label>
      </aside>

      <aside class="swift-social-panel swift-social-review-panel">
        <div class="swift-social-heading">
          <h2>Review</h2>
          <span>Forecaster copy check</span>
        </div>

        <label>
          Summary
          <textarea v-model="draft.summary" />
        </label>
        <label>
          Confidence / Status Label
          <input v-model="draft.confidenceLabel" type="text" />
        </label>
        <label>
          Confidence / Status Value
          <input v-model="draft.confidenceValue" type="text" />
        </label>
        <label>
          Confidence / Status Detail
          <textarea v-model="draft.confidenceDetail" class="swift-social-short-textarea" />
        </label>
        <label>
          Impact Icons
          <input v-model="impactIconsText" type="text" />
        </label>
        <label>
          Footer Left
          <input v-model="draft.footerLeft" type="text" />
        </label>
        <label>
          Footer Center
          <input v-model="draft.footerCenter" type="text" />
        </label>
      </aside>

      <section class="swift-social-preview-panel" aria-label="Social media graphic preview">
        <article class="swift-social-card" :style="{ '--product-color': draft.color }">
          <header class="swift-social-card-header">
            <div class="swift-social-brand">
              <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
              <img src="/assets/visual-finder/logos/NWSlogo.png" alt="National Weather Service" />
              <div>
                <strong>Space Weather Prediction Center</strong>
                <span>National Weather Service</span>
              </div>
            </div>
            <div class="swift-social-badge">{{ draft.badge }}</div>
          </header>

          <main class="swift-social-card-body">
            <section class="swift-social-message">
              <h1>{{ draft.headline }}</h1>
              <p class="swift-social-subhead">{{ draft.subheadline }}</p>
              <p class="swift-social-time">{{ draft.issueTime }}</p>
              <p class="swift-social-summary">{{ draft.summary }}</p>

              <div class="swift-social-confidence">
                <span>{{ draft.confidenceLabel }}</span>
                <strong>{{ draft.confidenceValue }}</strong>
                <p>{{ draft.confidenceDetail }}</p>
              </div>
            </section>

            <section class="swift-social-image-frame">
              <img v-if="uploadedImage" :src="uploadedImage" :alt="uploadedImageName || 'Uploaded social media image'" />
              <div v-else>
                <span>{{ draft.imagePlaceholder }}</span>
              </div>
              <label class="swift-social-image-upload">
                Upload Image
                <input type="file" accept="image/*" @change="handleImageUpload" />
              </label>
            </section>
          </main>

          <section class="swift-social-know-row">
            <div class="swift-social-know">
              <h2>What We Know</h2>
              <ul>
                <li v-for="item in whatWeKnowLines" :key="item">{{ item }}</li>
              </ul>
            </div>

            <div class="swift-social-impact-strip">
              <div v-for="impact in impactLabels" :key="impact" class="swift-social-impact">
                <span>{{ impact.charAt(0) }}</span>
                <strong>{{ impact }}</strong>
              </div>
            </div>
          </section>

          <footer class="swift-social-card-footer">
            <span>{{ draft.footerLeft }}</span>
            <span>{{ draft.footerCenter }}</span>
            <strong>{{ draft.footerRight }}</strong>
          </footer>
        </article>
      </section>
    </div>
  </section>
</template>

<style scoped>
.swift-social-workspace {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.swift-social-product-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  min-width: 0;
}

.swift-social-product-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  min-width: 0;
}

.swift-social-product-button,
.swift-social-upload-button {
  border: 1px solid rgba(95, 199, 255, 0.24);
  background: rgba(95, 199, 255, 0.09);
  color: rgba(232, 239, 248, 0.86);
  cursor: pointer;
  font-weight: 400;
}

.swift-social-product-button--active {
  background: rgba(95, 199, 255, 0.22);
  color: #ffffff;
}

.swift-social-upload-button {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  white-space: nowrap;
}

.swift-social-product-source {
  color: rgba(232, 239, 248, 0.58);
  font-size: 0.78rem;
  white-space: nowrap;
}

.swift-social-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.82fr) minmax(260px, 0.82fr) minmax(580px, 1.36fr);
  gap: 14px;
  align-items: start;
  min-width: 0;
}

.swift-social-panel {
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 12px;
  border: 1px solid rgba(95, 199, 255, 0.22);
  border-radius: var(--app-radius);
  background:
    linear-gradient(180deg, rgba(95, 199, 255, 0.06), rgba(95, 199, 255, 0.025)),
    rgba(4, 10, 18, 0.28);
}

.swift-social-heading {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: baseline;
}

.swift-social-heading h2 {
  margin: 0;
  color: var(--app-primary);
  font-size: 0.86rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.swift-social-heading span {
  color: rgba(232, 239, 248, 0.58);
  font-size: 0.74rem;
}

.swift-social-panel label {
  display: grid;
  gap: 5px;
  min-width: 0;
  color: rgba(232, 239, 248, 0.78);
  font-weight: 400;
}

.swift-social-panel input,
.swift-social-panel textarea {
  display: block;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  background: rgba(2, 8, 15, 0.96);
  color: #e8eff8;
  font-weight: 400;
}

.swift-social-panel textarea {
  min-height: 82px;
  resize: vertical;
}

.swift-social-short-textarea {
  min-height: 54px !important;
}

.swift-social-preview-panel {
  min-width: 0;
}

.swift-social-card {
  --product-color: #d94a1e;
  width: min(100%, 760px);
  aspect-ratio: 3 / 2;
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  overflow: hidden;
  border: 1px solid rgba(171, 199, 235, 0.18);
  border-radius: 6px;
  background: #ffffff;
  color: #1e1e1e;
  font-family: Arial, Helvetica, sans-serif;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}

.swift-social-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 14px 18px;
  background: linear-gradient(90deg, #001b3f, #003e7e);
  color: #ffffff;
}

.swift-social-brand {
  display: flex;
  gap: 8px;
  align-items: center;
  text-transform: uppercase;
}

.swift-social-brand img {
  width: 42px;
  height: 42px;
  object-fit: contain;
  border-radius: 50%;
  background: #ffffff;
}

.swift-social-brand div {
  display: grid;
  line-height: 1;
}

.swift-social-brand strong {
  font-size: 0.95rem;
}

.swift-social-brand span {
  font-size: 0.62rem;
}

.swift-social-badge {
  max-width: 190px;
  padding: 7px 10px;
  border-radius: 4px;
  background: var(--product-color);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
}

.swift-social-card-body {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(220px, 0.92fr);
  gap: 18px;
  padding: 18px 20px 12px;
  min-height: 0;
}

.swift-social-message {
  display: grid;
  gap: 7px;
  align-content: start;
  min-width: 0;
}

.swift-social-message h1 {
  margin: 0;
  color: #002b5c;
  font-size: 1.45rem;
  line-height: 1.05;
}

.swift-social-subhead,
.swift-social-time,
.swift-social-summary,
.swift-social-confidence p {
  margin: 0;
}

.swift-social-subhead {
  color: var(--product-color);
  font-size: 1rem;
  font-weight: 700;
}

.swift-social-time {
  color: #5c6b7a;
  font-size: 0.74rem;
}

.swift-social-summary {
  font-size: 0.86rem;
  line-height: 1.25;
}

.swift-social-confidence {
  display: grid;
  gap: 2px;
  margin-top: 4px;
  padding: 10px;
  border-left: 5px solid var(--product-color);
  background: #eaf3fb;
}

.swift-social-confidence span {
  color: #5c6b7a;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.swift-social-confidence strong {
  color: #002b5c;
  font-size: 1.05rem;
}

.swift-social-confidence p {
  font-size: 0.78rem;
}

.swift-social-image-frame {
  position: relative;
  display: grid;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border: 2px dashed #b8c7d8;
  background: #eaf3fb;
}

.swift-social-image-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.swift-social-image-frame div {
  display: grid;
  place-items: center;
  padding: 18px;
  color: #5c6b7a;
  font-size: 0.86rem;
  font-weight: 700;
  text-align: center;
}

.swift-social-image-upload {
  position: absolute;
  right: 10px;
  bottom: 10px;
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 10px;
  border: 1px solid rgba(0, 43, 92, 0.28);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.92);
  color: #002b5c;
  cursor: pointer;
  font-size: 0.74rem;
  font-weight: 700;
}

.swift-social-image-upload input {
  display: none;
}

.swift-social-know-row {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: 14px;
  padding: 0 20px 14px;
}

.swift-social-know {
  padding: 10px 12px;
  border-top: 4px solid var(--product-color);
  background: #f5f8fb;
}

.swift-social-know h2 {
  margin: 0 0 5px;
  color: #002b5c;
  font-size: 0.82rem;
  text-transform: uppercase;
}

.swift-social-know ul {
  margin: 0;
  padding-left: 18px;
  font-size: 0.76rem;
  line-height: 1.22;
}

.swift-social-impact-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 7px;
}

.swift-social-impact {
  display: grid;
  place-items: center;
  gap: 2px;
  min-width: 0;
  padding: 7px 4px;
  border: 1px solid #d6dee8;
  border-radius: 4px;
  background: #ffffff;
}

.swift-social-impact span {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--product-color);
  color: #ffffff;
  font-weight: 700;
}

.swift-social-impact strong {
  color: #002b5c;
  font-size: 0.64rem;
  text-align: center;
}

.swift-social-card-footer {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 9px 16px;
  background: #002b5c;
  color: #ffffff;
  font-size: 0.68rem;
}

.swift-social-card-footer strong {
  white-space: nowrap;
}

@media (max-width: 1300px) {
  .swift-social-grid {
    grid-template-columns: 1fr;
  }

  .swift-social-card {
    justify-self: center;
  }
}
</style>
