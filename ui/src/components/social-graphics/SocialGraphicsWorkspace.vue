<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import type { GraphicsWorkspaceMode, OpsToCommsRecommendation, RuntimeContext } from '../../types'
import { exportElementToPng } from '../../utils/exportPng'
import { formatIssueTime } from '../../utils/briefingTime'

type SocialProductId =
  | 'swpc_brief'
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

type SectorSymbol = {
  id: string
  label: string
  icon: string
  aliases: string[]
}

const props = defineProps<{
  mode: GraphicsWorkspaceMode
  presentation?: 'default' | 'social-tab'
  recommendation?: OpsToCommsRecommendation | null
  runtimeNow?: RuntimeContext | null
}>()

const sectorSymbols: SectorSymbol[] = [
  {
    id: 'power-grid',
    label: 'Power Grid',
    icon: 'mdi-transmission-tower',
    aliases: ['power', 'power grid', 'electric power', 'electric power grid', 'grid'],
  },
  {
    id: 'aviation',
    label: 'Aviation & Radiation',
    icon: 'mdi-airplane',
    aliases: ['aviation', 'aviation & radiation', 'aviation radiation', 'aviation operations', 'aircraft'],
  },
  {
    id: 'satellite',
    label: 'Satellite',
    icon: 'mdi-satellite-variant',
    aliases: ['satellite', 'satellites', 'satellite operations', 'spacecraft'],
  },
  {
    id: 'communications-gnss',
    label: 'Comms / GNSS',
    icon: 'mdi-radio-tower',
    aliases: ['communications & gnss', 'communications', 'communication/gnss', 'communication', 'hf radio', 'hf communications', 'gnss', 'navigation'],
  },
  {
    id: 'human-spaceflight',
    label: 'Human Spaceflight',
    icon: 'mdi-rocket-launch',
    aliases: ['human spaceflight', 'spaceflight', 'crew', 'astronaut'],
  },
  {
    id: 'emergency-management',
    label: 'Emergency Mgmt',
    icon: 'mdi-shield-alert-outline',
    aliases: ['emergency management', 'critical comms', 'emergency management / critical comms', 'emergency'],
  },
  {
    id: 'aurora',
    label: 'Aurora',
    icon: 'mdi-weather-night',
    aliases: ['aurora', 'public / aurora', 'public', 'aurora observers'],
  },
]

const templates: SocialTemplate[] = [
  {
    id: 'swpc_brief',
    label: 'SWPC Brief',
    badge: 'SWPC BRIEF',
    color: '#0065B3',
    headline: 'Space Weather Briefing',
    subheadline: 'Executive update',
    issueTime: 'Issue time pending',
    summary: 'SWPC is monitoring space weather conditions and will continue to provide updates as forecast confidence or observed conditions change.',
    confidenceLabel: 'Status',
    confidenceValue: 'Monitoring',
    confidenceDetail: 'Current guidance is based on active SWPC analysis and partner decision-support information.',
    whatWeKnow:
      'SWPC forecast and observational data remain under review.\nActive products and updates will be reflected as conditions evolve.\nPartners should use official SWPC products for operational decisions.\nAdditional briefings may be issued as needed.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aviation & Radiation'],
    footerLeft: 'SWPC will continue to monitor the Sun and near-Earth space environment.',
    footerCenter: 'Use official SWPC products for current watches, warnings, and alerts.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
  {
    id: 'outlook',
    label: 'Outlook',
    badge: 'SPACE WEATHER OUTLOOK',
    color: '#1E73BE',
    headline: 'Active Space Weather Conditions Expected This Week',
    subheadline: 'Planning outlook for May 6-12',
    issueTime: 'Issue time pending',
    summary: 'Space weather activity may increase this week as solar activity and geomagnetic conditions remain under review.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium',
    confidenceDetail: 'Forecast confidence will be updated as new model guidance arrives.',
    whatWeKnow:
      'Active solar regions remain under monitoring.\nGeomagnetic activity may increase later in the outlook period.\nPartners should monitor SWPC updates for watches or warnings.\nForecast confidence may change with new observations.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aurora'],
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
    issueTime: 'Issue time pending',
    summary: 'SWPC is analyzing solar activity and possible Earth-directed impacts. Additional products may be issued if confidence increases.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Low to Medium',
    confidenceDetail: 'Timing, strength, and duration remain uncertain.',
    whatWeKnow:
      'A solar event is under analysis.\nInitial model guidance is being reviewed.\nNo warning-level product is in effect unless separately issued.\nUpdates will follow as confidence changes.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite'],
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
    issueTime: 'Issue time pending',
    summary: 'A CME sequence may reach Earth and produce significant geomagnetic activity. Confidence and timing will be refined with new observations.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: 'Potential for G3 or greater conditions is credible.',
    whatWeKnow:
      '70-80% chance of initial arrival Friday afternoon into Friday night.\nMultiple CME influences may continue into the weekend.\nG3 to G4 conditions are possible.\nElevated activity could persist 24-48 hours.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aurora'],
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
    issueTime: 'Issue time pending',
    summary: 'Elevated space weather conditions continue, but the primary warning-level concern has decreased.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: 'Conditions are expected to gradually decrease.',
    whatWeKnow:
      'Advisory-level conditions remain possible.\nResidual impacts may continue for susceptible systems.\nConditions are expected to decrease with time.\nPartners should continue routine monitoring.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aviation & Radiation'],
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
    issueTime: 'Issue time pending',
    summary: 'Multiple CMEs are expected to reach Earth and cause significant geomagnetic activity. Severe intervals are possible if coupling is favorable.',
    confidenceLabel: 'Confidence',
    confidenceValue: 'Medium to High',
    confidenceDetail: '80-90% chance that two or more CMEs will impact Earth.',
    whatWeKnow:
      '70-80% chance of initial arrival Friday afternoon into Friday night.\n20-30% chance of arrival as early as midday Friday.\nG3 to G4 conditions expected; G5 conditions possible.\nElevated geomagnetic activity could persist 36-48 hours.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aurora'],
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
    issueTime: 'Observation time pending',
    summary: 'Observed geomagnetic conditions have reached an event-level alert threshold based on official monitoring.',
    confidenceLabel: 'Observed',
    confidenceValue: 'G3 at 2036 UTC',
    confidenceDetail: 'Based on official space weather observations.',
    whatWeKnow:
      'Observed threshold has been reached.\nWarning remains in effect if separately issued.\nConditions may fluctuate during the event.\nAdditional alerts may be issued if higher thresholds are reached.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aurora'],
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
    issueTime: 'Issue time pending',
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
    issueTime: 'Issue time pending',
    summary: 'SWPC continues to monitor an ongoing space weather event. This graphic summarizes current status and observed conditions.',
    confidenceLabel: 'Status',
    confidenceValue: 'Warning in Effect',
    confidenceDetail: 'Current status is based on active SWPC products.',
    whatWeKnow:
      'Event remains ongoing.\nObserved conditions and forecast guidance continue to be reviewed.\nSome operational areas may remain affected.\nAdditional updates will follow as conditions change.',
    impactIcons: ['Power Grid', 'Communications & GNSS', 'Satellite', 'Aurora'],
    footerLeft: 'SWPC will continue to monitor the Sun and near-Earth space environment.',
    footerCenter: 'Partners should monitor active products.',
    footerRight: 'spaceweather.gov',
    imagePlaceholder: 'INSERT APPROPRIATE IMAGE HERE',
  },
]

const selectedProductId = ref<SocialProductId>('swpc_brief')
const uploadedImage = ref('')
const uploadedImageName = ref('')
const imageFit = ref<'fit' | 'fill'>('fit')
const isUpdatedProduct = ref(false)
const socialPreviewRef = ref<HTMLElement | null>(null)

const selectedTemplate = computed(() => {
  return templates.find((template) => template.id === selectedProductId.value) ?? templates[0]!
})

const draft = reactive({ ...selectedTemplate.value })

const whatWeKnowLines = computed(() => lines(draft.whatWeKnow).slice(0, 5))
const impactLabels = computed(() => draft.impactIcons.slice(0, 7))
const impactSymbols = computed(() => impactLabels.value.map((label) => sectorSymbolFor(label)))
const updatedProductLabel = computed(() => `Updated ${selectedTemplate.value.label}`)
const selectedSectorIds = computed(() => {
  return new Set(draft.impactIcons.map((label) => sectorSymbolFor(label).id))
})
const productBadgeIcon = computed(() => (selectedProductId.value === 'outlook' ? 'mdi-calendar-month' : ''))
const socialCardStyle = computed(() => ({
  '--product-color': draft.color,
  '--product-rgb': hexToRgbTriplet(draft.color),
}))

function runtimeIssueLabel() {
  const prefix = selectedProductId.value === 'observed_alert' ? 'Observed' : 'Issued'
  return `${prefix} ${formatIssueTime(props.runtimeNow?.now_utc).replace('Issue time unavailable', 'time unavailable')}`
}

watch(selectedTemplate, (template) => {
  Object.assign(draft, template)
  if (props.runtimeNow?.now_utc) draft.issueTime = runtimeIssueLabel()
  uploadedImage.value = ''
  uploadedImageName.value = ''
  imageFit.value = 'fit'
  isUpdatedProduct.value = false
})

watch(
  () => props.runtimeNow?.now_utc,
  (value) => {
    if (value) draft.issueTime = runtimeIssueLabel()
  },
  { immediate: true },
)

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
  imageFit.value = 'fit'

  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.addEventListener('load', () => {
    uploadedImage.value = typeof reader.result === 'string' ? reader.result : ''
  })
  reader.readAsDataURL(file)
}

function normalizeSectorLabel(value: string) {
  return value.trim().toLowerCase().replace(/\s+/g, ' ')
}

function hexToRgbTriplet(value: string) {
  const normalized = value.replace('#', '').trim()
  const fullHex =
    normalized.length === 3
      ? normalized
          .split('')
          .map((character) => `${character}${character}`)
          .join('')
      : normalized

  const number = Number.parseInt(fullHex, 16)
  if (Number.isNaN(number)) {
    return '217, 74, 30'
  }

  return `${(number >> 16) & 255}, ${(number >> 8) & 255}, ${number & 255}`
}

function sectorSymbolFor(label: string) {
  const normalized = normalizeSectorLabel(label)
  return (
    sectorSymbols.find((symbol) => {
      return symbol.aliases.some((alias) => normalizeSectorLabel(alias) === normalized)
    }) ?? {
      id: normalized || 'custom',
      label,
      icon: 'mdi-alert-circle-outline',
      aliases: [label],
    }
  )
}

function isSectorSelected(symbol: SectorSymbol) {
  return selectedSectorIds.value.has(symbol.id)
}

function toggleSector(symbol: SectorSymbol, event: Event) {
  const checked = (event.target as HTMLInputElement | null)?.checked ?? false
  const selected = draft.impactIcons
    .map((label) => sectorSymbolFor(label))
    .filter((item, index, items) => items.findIndex((candidate) => candidate.id === item.id) === index)

  if (checked && !selected.some((item) => item.id === symbol.id)) {
    selected.push(symbol)
  }

  draft.impactIcons = selected
    .filter((item) => checked || item.id !== symbol.id)
    .map((item) => item.label)
}

function exportSocialPng() {
  exportElementToPng(socialPreviewRef.value, `${draft.label}-${draft.headline}`)
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
        <button
          type="button"
          class="swift-social-product-button swift-social-update-button"
          :class="{ 'swift-social-product-button--active': isUpdatedProduct }"
          :style="isUpdatedProduct ? { borderColor: draft.color } : undefined"
          @click="isUpdatedProduct = !isUpdatedProduct"
        >
          {{ isUpdatedProduct ? updatedProductLabel : 'Updated' }}
        </button>
      </div>

      <div class="swift-social-product-actions">
        <span class="swift-social-product-source">SWIFT WWA JSON driven</span>
        <button
          type="button"
          class="swift-social-product-button swift-social-export-button"
          @click="exportSocialPng"
        >
          Export PNG
        </button>
      </div>
    </header>

    <div class="swift-social-grid">
      <aside class="swift-social-panel swift-social-sector-panel">
        <div class="swift-social-heading">
          <h2>Impacted Sectors</h2>
          <span>JSON sectors</span>
        </div>

        <div class="swift-social-sector-list">
          <label v-for="symbol in sectorSymbols" :key="symbol.id" class="swift-social-sector-option">
            <input
              type="checkbox"
              :checked="isSectorSelected(symbol)"
              @change="toggleSector(symbol, $event)"
            />
            <span class="swift-social-sector-icon">
              <i class="mdi" :class="symbol.icon" aria-hidden="true"></i>
            </span>
            <span>{{ symbol.label }}</span>
          </label>
        </div>
      </aside>

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
      </aside>

      <aside class="swift-social-panel swift-social-footer-panel">
        <div class="swift-social-heading">
          <h2>Footer</h2>
          <span>Persistent template copy</span>
        </div>

        <label>
          Footer Left
          <input v-model="draft.footerLeft" type="text" />
        </label>
        <label>
          Footer Center
          <input v-model="draft.footerCenter" type="text" />
        </label>
        <label>
          Footer Right
          <input v-model="draft.footerRight" type="text" />
        </label>
      </aside>

      <section class="swift-social-preview-panel" aria-label="Social media graphic preview">
        <article ref="socialPreviewRef" class="swift-social-card" :style="socialCardStyle">
          <header class="swift-social-card-header">
            <div class="swift-social-brand">
              <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
              <img src="/assets/visual-finder/logos/NWSlogo.png" alt="National Weather Service" />
              <div>
                <span>National Weather Service</span>
                <strong>Space Weather Prediction Center</strong>
                <span>National Oceanic and Atmospheric Administration</span>
              </div>
            </div>
            <div class="swift-social-badge-stack">
              <div class="swift-social-badge">
                <span>{{ draft.badge }}</span>
                <i v-if="productBadgeIcon" class="mdi" :class="productBadgeIcon" aria-hidden="true"></i>
              </div>
              <div v-if="isUpdatedProduct" class="swift-social-update-label">
                {{ updatedProductLabel }}
              </div>
            </div>
          </header>

          <main class="swift-social-card-body">
            <section class="swift-social-message">
              <h1>{{ draft.headline }}</h1>
              <p class="swift-social-subhead">{{ draft.subheadline }}</p>
              <p class="swift-social-time">{{ draft.issueTime }}</p>
              <div class="swift-social-message-divider" aria-hidden="true"></div>
              <p class="swift-social-summary">{{ draft.summary }}</p>

              <div class="swift-social-message-support">
                <div class="swift-social-confidence">
                  <span>{{ draft.confidenceLabel }}</span>
                  <strong>{{ draft.confidenceValue }}</strong>
                  <p>{{ draft.confidenceDetail }}</p>
                </div>

                <div class="swift-social-know">
                  <h2>What We Know</h2>
                  <ul>
                    <li v-for="item in whatWeKnowLines" :key="item">{{ item }}</li>
                  </ul>
                </div>
              </div>
            </section>

            <section class="swift-social-image-frame">
              <img
                v-if="uploadedImage"
                :src="uploadedImage"
                :alt="uploadedImageName || 'Uploaded social media image'"
                :class="`swift-social-image--${imageFit}`"
              />
              <div v-else>
                <span>{{ draft.imagePlaceholder }}</span>
              </div>
              <div v-if="uploadedImage" class="swift-social-image-fit-toggle" aria-label="Image fit mode">
                <button
                  type="button"
                  :class="{ 'swift-social-image-fit-toggle--active': imageFit === 'fit' }"
                  @click="imageFit = 'fit'"
                >
                  Fit
                </button>
                <button
                  type="button"
                  :class="{ 'swift-social-image-fit-toggle--active': imageFit === 'fill' }"
                  @click="imageFit = 'fill'"
                >
                  Fill
                </button>
              </div>
              <label class="swift-social-image-upload">
                Upload Image
                <input type="file" accept="image/*" @change="handleImageUpload" />
              </label>
            </section>
          </main>

          <section class="swift-social-impact-row">
            <div class="swift-social-impact-strip">
              <div class="swift-social-impact-label">Potential Impacts</div>
              <div v-for="symbol in impactSymbols" :key="`${symbol.id}-${symbol.label}`" class="swift-social-impact">
                <span>
                  <i class="mdi" :class="symbol.icon" aria-hidden="true"></i>
                </span>
                <strong>{{ symbol.label }}</strong>
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

.swift-social-product-actions {
  display: flex;
  gap: 14px;
  align-items: center;
  justify-content: flex-end;
  margin-left: auto;
  min-width: max-content;
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

.swift-social-update-button {
  min-width: 96px;
}

.swift-social-export-button {
  border-color: rgba(255, 229, 100, 0.38);
  background: rgba(255, 229, 100, 0.12);
  color: #fff0a8;
  min-height: 40px;
  padding: 0 16px;
  white-space: nowrap;
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
  grid-template-columns: minmax(220px, 250px) minmax(300px, 1fr) minmax(340px, 1.12fr) minmax(920px, 1120px);
  gap: 18px;
  align-items: start;
  min-width: 0;
}

.swift-social-panel {
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 16px;
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
  gap: 7px;
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
  border-color: rgba(171, 199, 235, 0.58);
  background: #ffffff;
  color: #111827;
  font-weight: 400;
}

.swift-social-panel textarea {
  min-height: 98px;
  resize: vertical;
}

.swift-social-sector-panel {
  align-content: start;
}

.swift-social-footer-panel {
  grid-column: 1 / 4;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-items: end;
}

.swift-social-footer-panel .swift-social-heading {
  grid-column: 1 / -1;
}

.swift-social-sector-list {
  display: grid;
  gap: 8px;
}

.swift-social-sector-option {
  display: grid !important;
  grid-template-columns: 18px 28px minmax(0, 1fr);
  gap: 8px !important;
  align-items: center;
  min-height: 36px;
  padding: 6px 7px;
  border: 1px solid rgba(171, 199, 235, 0.18);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(232, 239, 248, 0.84) !important;
  cursor: pointer;
}

.swift-social-sector-option input {
  width: 15px;
  height: 15px;
  accent-color: var(--app-primary);
}

.swift-social-sector-icon {
  display: grid;
  width: 26px;
  height: 26px;
  place-items: center;
  color: #e7a01b;
  font-size: 1.24rem;
  line-height: 1;
}

.swift-social-sector-icon .mdi::before {
  display: block;
  line-height: 1;
}

.swift-social-short-textarea {
  min-height: 68px !important;
}

.swift-social-preview-panel {
  grid-column: 4;
  grid-row: 1 / span 2;
  display: grid;
  width: 100%;
  min-width: 0;
  justify-items: end;
}

.swift-social-card {
  --product-color: #d94a1e;
  --product-rgb: 217, 74, 30;
  width: min(100%, 1120px);
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
  gap: 14px;
  align-items: center;
  padding: 8px 14px;
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
  width: 78px;
  height: 78px;
  object-fit: contain;
  border-radius: 50%;
  background: #ffffff;
}

.swift-social-brand img:first-child {
  object-fit: cover;
  padding: 0;
}

.swift-social-brand div {
  display: grid;
  line-height: 0.96;
}

.swift-social-brand strong {
  font-size: 1.62rem;
  font-weight: 500;
}

.swift-social-brand span {
  font-size: 0.88rem;
  font-weight: 500;
}

.swift-social-badge-stack {
  display: grid;
  justify-items: end;
  gap: 5px;
}

.swift-social-badge {
  display: flex;
  min-width: 330px;
  min-height: 62px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 10px 20px 10px 32px;
  border-radius: 6px 0 0 6px;
  background: var(--product-color);
  color: #ffffff;
  clip-path: polygon(8% 0, 100% 0, 100% 100%, 0 100%);
  font-size: 1.28rem;
  font-weight: 500;
  line-height: 1.05;
  text-align: center;
  text-transform: uppercase;
}

.swift-social-badge .mdi {
  font-size: 1.9rem;
  line-height: 1;
}

.swift-social-badge .mdi::before {
  display: block;
  line-height: 1;
}

.swift-social-update-label {
  width: fit-content;
  max-width: 170px;
  padding: 4px 9px;
  border: 1px solid rgba(0, 43, 92, 0.18);
  border-radius: 4px;
  background: #f6d889;
  color: #002b5c;
  font-size: 0.68rem;
  font-weight: 800;
  text-align: center;
  text-transform: uppercase;
}

.swift-social-card-body {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(220px, 0.92fr);
  gap: 18px;
  align-items: stretch;
  padding: 18px 20px 12px;
  min-height: 0;
}

.swift-social-message {
  display: grid;
  grid-template-rows: auto auto auto auto auto minmax(0, 1fr);
  gap: 8px;
  align-content: stretch;
  min-width: 0;
  min-height: 0;
}

.swift-social-message h1 {
  margin: 0;
  color: #002b5c;
  font-size: 2.12rem;
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
  font-size: 1.42rem;
  font-weight: 700;
}

.swift-social-time {
  color: #5c6b7a;
  font-size: 0.82rem;
}

.swift-social-message-divider {
  width: 44%;
  height: 3px;
  margin: 2px 0 1px;
  background: var(--product-color);
}

.swift-social-summary {
  font-size: 1.28rem;
  line-height: 1.18;
}

.swift-social-confidence {
  display: grid;
  align-content: start;
  gap: 5px;
  min-height: 128px;
  height: 100%;
  padding: 14px;
  border-left: 6px solid var(--product-color);
  background: #eaf3fb;
  box-sizing: border-box;
}

.swift-social-confidence span {
  color: #5c6b7a;
  font-size: 0.86rem;
  font-weight: 700;
  text-transform: uppercase;
}

.swift-social-confidence strong {
  color: #002b5c;
  font-size: 1.36rem;
}

.swift-social-confidence p {
  font-size: 1rem;
  line-height: 1.18;
}

.swift-social-message-support {
  display: grid;
  grid-template-columns: minmax(170px, 0.52fr) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
  align-self: stretch;
  margin-top: 12px;
  min-height: 0;
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
}

.swift-social-image--fit {
  object-fit: contain;
}

.swift-social-image--fill {
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

.swift-social-image-fit-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  display: inline-flex !important;
  overflow: hidden;
  padding: 0;
  border: 1px solid rgba(0, 43, 92, 0.22);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 18px rgba(0, 43, 92, 0.12);
}

.swift-social-image-fit-toggle button {
  min-height: 30px;
  padding: 0 10px;
  border: 0;
  border-right: 1px solid rgba(0, 43, 92, 0.14);
  background: transparent;
  color: #002b5c;
  cursor: pointer;
  font-size: 0.72rem;
  font-weight: 700;
}

.swift-social-image-fit-toggle button:last-child {
  border-right: 0;
}

.swift-social-image-fit-toggle--active {
  background: #002b5c !important;
  color: #ffffff !important;
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

.swift-social-impact-row {
  display: grid;
  grid-template-columns: 1fr;
  padding: 0 20px 14px;
}

.swift-social-know {
  display: grid;
  align-content: start;
  min-height: 128px;
  height: 100%;
  padding: 14px;
  border-left: 1px solid rgba(var(--product-rgb), 0.22);
  background: #f8fbff;
  box-sizing: border-box;
}

.swift-social-know h2 {
  margin: 0 0 7px;
  color: #002b5c;
  font-size: 1.08rem;
  text-transform: uppercase;
}

.swift-social-know ul {
  margin: 0;
  padding-left: 20px;
  font-size: 0.96rem;
  line-height: 1.32;
}

.swift-social-know li + li {
  margin-top: 7px;
}

.swift-social-impact-strip {
  display: grid;
  grid-template-columns: minmax(124px, 0.58fr) repeat(auto-fit, minmax(78px, 1fr));
  gap: 0;
  overflow: hidden;
  border: 1px solid rgba(var(--product-rgb), 0.55);
  border-radius: 5px;
  background: #f8fbff;
}

.swift-social-impact-label {
  display: grid;
  place-items: center;
  padding: 11px 8px;
  border-right: 1px solid rgba(var(--product-rgb), 0.38);
  background: rgba(var(--product-rgb), 0.12);
  color: #002b5c;
  font-size: 0.94rem;
  font-weight: 700;
  line-height: 1.05;
  text-align: center;
  text-transform: uppercase;
}

.swift-social-impact {
  display: grid;
  place-items: center;
  gap: 3px;
  min-width: 0;
  padding: 11px 4px 8px;
  border-right: 1px solid rgba(var(--product-rgb), 0.26);
  background: #ffffff;
}

.swift-social-impact:last-child {
  border-right: 0;
}

.swift-social-impact span {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--product-color);
  font-size: 1.84rem;
  line-height: 1;
}

.swift-social-impact .mdi::before {
  display: block;
  line-height: 1;
}

.swift-social-impact strong {
  color: #002b5c;
  font-size: 0.75rem;
  line-height: 1.05;
  text-align: center;
}

.swift-social-card-footer {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  min-height: 58px;
  gap: 0;
  align-items: center;
  padding: 8px 18px;
  background: #002b5c;
  color: #ffffff;
  font-size: 0.82rem;
  line-height: 1.16;
}

.swift-social-card-footer span,
.swift-social-card-footer strong {
  display: grid;
  min-height: 34px;
  align-items: center;
  justify-items: center;
  min-width: 0;
  padding: 0 18px;
  text-align: center;
}

.swift-social-card-footer span:nth-child(n + 2),
.swift-social-card-footer strong {
  border-left: 1px solid rgba(255, 255, 255, 0.36);
}

.swift-social-card-footer strong {
  font-size: 1.05rem;
  font-weight: 600;
  white-space: nowrap;
}

@media (max-width: 1300px) {
  .swift-social-grid {
    grid-template-columns: 1fr;
  }

  .swift-social-footer-panel,
  .swift-social-preview-panel {
    grid-column: auto;
    grid-row: auto;
  }

  .swift-social-card {
    justify-self: center;
  }
}
</style>
