<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import type { RuntimeContext } from '../../types'
import { fetchEmailBriefingDocument, saveEmailBriefingDocument } from '../../api'
import { exportElementToPng } from '../../utils/exportPng'
import { formatIssueTime } from '../../utils/briefingTime'
import may2024Catalog from '../../data/may-2024-social-products.json'

type SocialProductId =
  | 'swpc_brief'
  | 'outlook'
  | 'statement'
  | 'watch'
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

type ExerciseSocialProduct = {
  product_id: string
  sequence: number
  editorial_status: 'draft' | 'reviewed' | 'approved'
  official_product: { type: string; title: string; issue_time_utc: string }
  social: {
    effective_time_utc: string
    template_id: SocialProductId
    headline: string
    subheadline: string
    summary: string
    confidence_label: string
    confidence_value: string
    confidence_detail: string
    what_we_know: string[]
    impact_sectors: string[]
    footer_left: string
    footer_center: string
    footer_right: string
    media_number?: number
    visual_asset?: string
    visual_alt_text?: string
    visual_fit?: 'fit' | 'fill'
  }
}

const exerciseMediaAssets = import.meta.glob(
  '../../../../docs/exercise/gannon/social-media/media/*.{png,jpg,jpeg,webp}',
  { eager: true, query: '?url', import: 'default' },
) as Record<string, string>

function numberedMediaAsset(mediaNumber: number): string {
  const prefix = `${String(mediaNumber).padStart(2, '0')}-`
  return Object.entries(exerciseMediaAssets).find(([path]) => {
    const fileName = path.split('/').pop() ?? ''
    return fileName.startsWith(prefix)
  })?.[1] ?? ''
}

type SectorSymbol = {
  id: string
  label: string
  icon: string
  aliases: string[]
}

const props = defineProps<{
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
    color: '#F28C28',
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
const selectedExerciseProductId = ref('')
const uploadedImage = ref('')
const uploadedImageName = ref('')
const imageFit = ref<'fit' | 'fill'>('fill')
const imageAspectRatio = ref(1)
const isUpdatedProduct = ref(false)
const socialPreviewRef = ref<HTMLElement | null>(null)
const isSaving = ref(false)
const saveStatus = ref('Not saved')
const persistedVersion = ref(0)
const hasRestoredSavedDocument = ref(false)

const selectedTemplate = computed(() => {
  return templates.find((template) => template.id === selectedProductId.value) ?? templates[0]!
})
const exerciseProducts = may2024Catalog.products as ExerciseSocialProduct[]
const isMay2024Replay = computed(() => {
  if (props.runtimeNow?.data_source !== 'replay') return false
  if (props.runtimeNow.scenario === may2024Catalog.scenario.id) return true
  const now = Date.parse(props.runtimeNow.now_utc ?? '')
  const first = Date.parse(exerciseProducts[0]?.social.effective_time_utc ?? '')
  const last = Date.parse(exerciseProducts[exerciseProducts.length - 1]?.social.effective_time_utc ?? '')
  return Number.isFinite(now) && now >= first && now <= last + 7 * 24 * 60 * 60 * 1000
})
const availableExerciseProducts = computed(() => {
  const now = Date.parse(props.runtimeNow?.now_utc ?? '')
  if (!isMay2024Replay.value || !Number.isFinite(now)) return []
  return exerciseProducts.filter((product) => Date.parse(product.social.effective_time_utc) <= now)
})

const draft = reactive({ ...selectedTemplate.value })

const whatWeKnowLines = computed(() => lines(draft.whatWeKnow).slice(0, 5))
const impactLabels = computed(() => draft.impactIcons.slice(0, 7))
const impactSymbols = computed(() => impactLabels.value.map((label) => sectorSymbolFor(label)))
const impactRowLabel = computed(() => selectedProductId.value === 'notice' ? 'Operational Impacts' : 'Potential Impacts')
const updatedProductLabel = computed(() => `Updated ${selectedTemplate.value.label}`)
const selectedSectorIds = computed(() => {
  return new Set(draft.impactIcons.map((label) => sectorSymbolFor(label).id))
})
const productBadgeIcons = computed(() => {
  if (selectedProductId.value === 'outlook') return ['mdi-calendar-month']
  if (selectedProductId.value === 'statement') return ['mdi-file-document-outline', 'mdi-information-outline']
  if (selectedProductId.value === 'watch') return ['mdi-bell-ring-outline']
  if (selectedProductId.value === 'notice') return ['mdi-satellite-uplink']
  if (selectedProductId.value === 'warning') return ['mdi-alert-outline']
  if (selectedProductId.value === 'observed_alert') return ['mdi-pulse']
  return []
})
const socialCardStyle = computed(() => ({
  '--product-color': draft.color,
  '--product-rgb': hexToRgbTriplet(draft.color),
}))

function runtimeIssueLabel() {
  return `Published ${formatIssueTime(props.runtimeNow?.now_utc).replace('Issue time unavailable', 'time unavailable')}`
}

watch(selectedTemplate, (template) => {
  Object.assign(draft, template)
  if (props.runtimeNow?.now_utc) draft.issueTime = runtimeIssueLabel()
  uploadedImage.value = ''
  uploadedImageName.value = ''
  imageFit.value = 'fill'
  isUpdatedProduct.value = false
}, { flush: 'sync' })

function applyExerciseProduct(product: ExerciseSocialProduct) {
  selectedExerciseProductId.value = product.product_id
  selectedProductId.value = product.social.template_id
  const baseTemplate = templates.find((template) => template.id === product.social.template_id) ?? templates[0]!
  Object.assign(draft, baseTemplate, {
    headline: product.social.headline,
    subheadline: product.social.subheadline,
    issueTime: `Published ${formatIssueTime(product.social.effective_time_utc)}`,
    summary: product.social.summary,
    confidenceLabel: product.social.confidence_label,
    confidenceValue: product.social.confidence_value,
    confidenceDetail: product.social.confidence_detail,
    whatWeKnow: product.social.what_we_know.join('\n'),
    impactIcons: [...product.social.impact_sectors],
    footerLeft: product.social.footer_left,
    footerCenter: product.social.footer_center,
    footerRight: product.social.footer_right,
  })
  uploadedImage.value = numberedMediaAsset(product.social.media_number ?? product.sequence)
    || product.social.visual_asset
    || ''
  uploadedImageName.value = product.social.visual_alt_text ?? ''
  imageFit.value = product.social.visual_fit ?? 'fill'
  isUpdatedProduct.value = product.official_product.type.includes('update')
}

function selectExerciseProduct(event: Event) {
  const productId = (event.target as HTMLSelectElement).value
  const product = availableExerciseProducts.value.find((item) => item.product_id === productId)
  if (product) applyExerciseProduct(product)
}

function selectBaseTemplate(templateId: SocialProductId) {
  selectedExerciseProductId.value = ''
  selectedProductId.value = templateId
}

watch(
  () => props.runtimeNow?.now_utc,
  (value) => {
    if (!value) return
    if (hasRestoredSavedDocument.value) return
    if (isMay2024Replay.value) {
      const available = availableExerciseProducts.value
      const current = available[available.length - 1]
      if (current) applyExerciseProduct(current)
      return
    }
    draft.issueTime = runtimeIssueLabel()
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

function captureImageAspectRatio(event: Event) {
  const image = event.target as HTMLImageElement | null
  if (!image?.naturalWidth || !image.naturalHeight) return
  imageAspectRatio.value = image.naturalWidth / image.naturalHeight
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
  const noticeSymbols: Record<string, string> = {
    'cme analysis': 'mdi-chart-timeline-variant',
    'forecast timing': 'mdi-clock-outline',
    'active watch': 'mdi-shield-check-outline',
  }
  return (
    sectorSymbols.find((symbol) => {
      return symbol.aliases.some((alias) => normalizeSectorLabel(alias) === normalized)
    }) ?? {
      id: normalized || 'custom',
      label,
      icon: noticeSymbols[normalized] ?? 'mdi-alert-circle-outline',
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

async function loadSavedSocialJson() {
  try {
    const saved = await fetchEmailBriefingDocument<{
      selectedProductId: SocialProductId
      selectedExerciseProductId: string
      draft: SocialTemplate
      uploadedImage: string
      uploadedImageName: string
      imageFit: 'fit' | 'fill'
      isUpdatedProduct: boolean
    }>('social')
    if (!saved) return
    hasRestoredSavedDocument.value = true
    selectedProductId.value = saved.document.selectedProductId
    selectedExerciseProductId.value = saved.document.selectedExerciseProductId
    Object.assign(draft, saved.document.draft)
    const selectedProduct = exerciseProducts.find(
      (product) => product.product_id === saved.document.selectedExerciseProductId,
    )
    uploadedImage.value = saved.document.uploadedImage.startsWith('data:')
      ? saved.document.uploadedImage
      : selectedProduct
        ? numberedMediaAsset(selectedProduct.social.media_number ?? selectedProduct.sequence)
          || saved.document.uploadedImage
        : saved.document.uploadedImage
    uploadedImageName.value = saved.document.uploadedImageName
    imageFit.value = saved.document.imageFit
    isUpdatedProduct.value = saved.document.isUpdatedProduct
    persistedVersion.value = saved.record_version
    saveStatus.value = `Loaded ${new Date(saved.updated_at).toLocaleString()}`
  } catch (error) {
    saveStatus.value = error instanceof Error ? error.message : 'Unable to load saved JSON'
  }
}

async function saveSocialJson() {
  isSaving.value = true
  saveStatus.value = 'Saving...'
  try {
    const saved = await saveEmailBriefingDocument('social', {
      selectedProductId: selectedProductId.value,
      selectedExerciseProductId: selectedExerciseProductId.value,
      draft: JSON.parse(JSON.stringify(draft)),
      uploadedImage: uploadedImage.value,
      uploadedImageName: uploadedImageName.value,
      imageFit: imageFit.value,
      isUpdatedProduct: isUpdatedProduct.value,
    }, persistedVersion.value)
    persistedVersion.value = saved.record_version
    hasRestoredSavedDocument.value = true
    saveStatus.value = `Saved ${new Date(saved.updated_at).toLocaleString()}`
  } catch (error) {
    saveStatus.value = error instanceof Error ? error.message : 'Unable to save JSON'
  } finally {
    isSaving.value = false
  }
}

onMounted(loadSavedSocialJson)
</script>

<template>
  <section class="swift-social-workspace">
    <header class="swift-social-product-row">
      <div v-if="isMay2024Replay" class="swift-social-exercise-picker">
        <label>
          Exercise Graphic
          <select :value="selectedExerciseProductId" @change="selectExerciseProduct">
            <option v-if="availableExerciseProducts.length === 0" value="">No social product effective yet</option>
            <option
              v-for="product in availableExerciseProducts"
              :key="product.product_id"
              :value="product.product_id"
            >
              {{ product.sequence }}. {{ product.official_product.title }} — {{ product.social.effective_time_utc.slice(5, 16).replace('T', ' ') }}Z
            </option>
          </select>
        </label>
        <span>{{ availableExerciseProducts.length }} of {{ exerciseProducts.length }} products available</span>
      </div>
      <div class="swift-social-product-buttons" aria-label="Social media product type">
        <button
          v-for="template in templates"
          :key="template.id"
          type="button"
          class="swift-social-product-button"
          :class="{ 'swift-social-product-button--active': selectedProductId === template.id }"
          :style="selectedProductId === template.id ? { borderColor: template.color } : undefined"
          @click="selectBaseTemplate(template.id)"
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
        <span class="swift-social-save-status" role="status">{{ saveStatus }}</span>
        <button
          type="button"
          class="swift-social-product-button swift-social-save-button"
          :disabled="isSaving"
          @click="saveSocialJson"
        >
          {{ isSaving ? 'Saving...' : 'Save JSON' }}
        </button>
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
          Confidence / Status Level / Observed Level
          <input v-model="draft.confidenceLabel" type="text" />
        </label>
        <label>
          Card Value
          <input v-model="draft.confidenceValue" type="text" />
        </label>
        <label>
          Card Detail
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
        <article
          ref="socialPreviewRef"
          class="swift-social-card"
          :style="socialCardStyle"
          data-export-width="1120"
          data-export-height="747"
        >
          <header class="swift-social-card-header">
            <div class="swift-social-brand">
              <span class="swift-social-noaa-frame">
                <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
              </span>
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
                <span
                  v-if="productBadgeIcons.length"
                  class="swift-social-badge-icon"
                  :class="{ 'swift-social-badge-icon--overlay': selectedProductId === 'statement' }"
                  aria-hidden="true"
                >
                  <i v-for="icon in productBadgeIcons" :key="icon" class="mdi" :class="icon"></i>
                </span>
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

            <section
              class="swift-social-image-frame"
              :class="[
                `swift-social-image-frame--${imageFit}`,
                { 'swift-social-image-frame--portrait': imageAspectRatio < 1 },
              ]"
              :style="{ '--image-aspect-ratio': imageAspectRatio }"
            >
              <img
                v-if="uploadedImage"
                :src="uploadedImage"
                :alt="uploadedImageName || 'Uploaded social media image'"
                :class="`swift-social-image--${imageFit}`"
                @load="captureImageAspectRatio"
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
              <div class="swift-social-impact-label">{{ impactRowLabel }}</div>
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

<style scoped src="./SocialGraphicsWorkspace.css"></style>
