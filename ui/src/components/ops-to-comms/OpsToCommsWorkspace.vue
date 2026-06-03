<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import {
  buildOpsToCommsRecommendation,
  createDefaultOpsToCommsInput,
  educationTopicRequiresActions,
  opsToCommsActionsToTakeOptions,
  opsToCommsCommunicationModeOptions,
  opsToCommsEducationTemplateOptions,
  opsToCommsEventOptions,
  opsToCommsLevelOptions,
  opsToCommsSectorOptions,
  opsToCommsSeverityOptions,
  opsToCommsTimingOptions,
  opsToCommsWhatItIsOptionsForEvent,
  opsToCommsWhyItMattersOptionsForEvent,
} from '../../opsToComms/recommendation'
import type {
  OpsToCommsRecommendation,
  OpsToCommsSector,
} from '../../types'

const emit = defineEmits<{
  'update:recommendation': [recommendation: OpsToCommsRecommendation]
}>()

const cmeEducationSectors: OpsToCommsSector[] = [
  'gnss-positioning',
  'satellite',
  'power-grid',
  'communications',
]

const form = reactive(createDefaultOpsToCommsInput())
const isEducationMode = computed(() => form.communicationMode === 'education-outreach')
const selectedCommunicationMode = computed(() => {
  return opsToCommsCommunicationModeOptions.find((option) => option.value === form.communicationMode) ?? null
})
const requiresActionsStatement = computed(() => educationTopicRequiresActions(form.eventType))
const whatItIsOptions = computed(() => opsToCommsWhatItIsOptionsForEvent(form.eventType))
const whyItMattersOptions = computed(() => opsToCommsWhyItMattersOptionsForEvent(form.eventType))

const recommendation = computed(() => {
  return buildOpsToCommsRecommendation({
    communicationMode: form.communicationMode,
    educationTemplateFamily: form.educationTemplateFamily,
    eventType: form.eventType,
    whatItIsOptionId: form.whatItIsOptionId,
    whyItMattersOptionId: form.whyItMattersOptionId,
    actionsToTakeOptionId: form.actionsToTakeOptionId,
    severity: form.severity,
    timingStatus: form.timingStatus,
    impactedSectors: [...form.impactedSectors],
    riskLevel: form.riskLevel,
    impactProbability: form.impactProbability,
    confidence: form.confidence,
  })
})

function toggleSector(sector: OpsToCommsSector) {
  const index = form.impactedSectors.indexOf(sector)
  if (index >= 0) {
    form.impactedSectors.splice(index, 1)
    return
  }
  form.impactedSectors.push(sector)
}

watch(
  () => form.eventType,
  (eventType) => {
    const nextWhatItIs = opsToCommsWhatItIsOptionsForEvent(eventType)
    const nextWhyItMatters = opsToCommsWhyItMattersOptionsForEvent(eventType)

    if (!nextWhatItIs.some((option) => option.id === form.whatItIsOptionId)) {
      form.whatItIsOptionId = nextWhatItIs[0]?.id ?? ''
    }
    if (!nextWhyItMatters.some((option) => option.id === form.whyItMattersOptionId)) {
      form.whyItMattersOptionId = nextWhyItMatters[0]?.id ?? ''
    }
    if (isEducationMode.value && eventType === 'cme') {
      form.impactedSectors.splice(0, form.impactedSectors.length, ...cmeEducationSectors)
    }
  },
  { immediate: true },
)

watch(
  () => form.communicationMode,
  (mode) => {
    if (mode === 'education-outreach' && form.eventType === 'cme') {
      form.impactedSectors.splice(0, form.impactedSectors.length, ...cmeEducationSectors)
    }
  },
)

watch(
  recommendation,
  (value) => {
    emit('update:recommendation', value)
  },
  { immediate: true },
)
</script>

<template>
  <section class="ops-to-comms">
    <div class="ops-to-comms__grid">
      <section class="ops-card ops-card--full">
        <div class="panel-kicker">1. Communication Track</div>
        <div class="ops-card__fields ops-card__fields--single">
          <label>
            Communication Track
            <select v-model="form.communicationMode">
              <option
                v-for="option in opsToCommsCommunicationModeOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>
          <p v-if="selectedCommunicationMode" class="ops-field-note">
            {{ selectedCommunicationMode.description }}
          </p>
        </div>
      </section>

      <section class="ops-card ops-card--half">
        <div class="panel-kicker">{{ isEducationMode ? '2. Topic' : '2. Event Characterization' }}</div>
        <div v-if="isEducationMode" class="ops-card__fields">
          <label>
            Education Slide Family
            <select v-model="form.educationTemplateFamily">
              <option
                v-for="option in opsToCommsEducationTemplateOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            Topic
            <select v-model="form.eventType">
              <option v-for="option in opsToCommsEventOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
        <div v-else class="ops-card__fields ops-card__fields--two">
          <label>
            Event Type
            <select v-model="form.eventType">
              <option v-for="option in opsToCommsEventOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            Magnitude / Severity
            <select v-model="form.severity">
              <option v-for="option in opsToCommsSeverityOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="ops-card ops-card--half">
        <div class="panel-kicker">{{ isEducationMode ? '3. Canned Statements' : '3. Risk / Confidence / Timing' }}</div>
        <div v-if="isEducationMode" class="ops-card__fields">
          <label>
            What it is
            <select v-model="form.whatItIsOptionId">
              <option v-for="option in whatItIsOptions" :key="option.id" :value="option.id">
                {{ option.text }}
              </option>
            </select>
          </label>

          <label>
            Why it matters
            <select v-model="form.whyItMattersOptionId">
              <option v-for="option in whyItMattersOptions" :key="option.id" :value="option.id">
                {{ option.text }}
              </option>
            </select>
          </label>

          <label v-if="requiresActionsStatement">
            Actions to take
            <select v-model="form.actionsToTakeOptionId">
              <option v-for="option in opsToCommsActionsToTakeOptions" :key="option.id" :value="option.id">
                {{ option.text }}
              </option>
            </select>
          </label>
        </div>
        <div v-else class="ops-card__fields ops-card__fields--three">
          <label>
            Timing Status
            <select v-model="form.timingStatus">
              <option v-for="option in opsToCommsTimingOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            Risk Level
            <select v-model="form.riskLevel">
              <option v-for="option in opsToCommsLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            Impact Probability
            <select v-model="form.impactProbability">
              <option v-for="option in opsToCommsLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            Confidence
            <select v-model="form.confidence">
              <option v-for="option in opsToCommsLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="ops-card ops-card--full">
        <div class="panel-kicker">{{ isEducationMode ? '4. Sectors to Highlight' : '4. Impacted Sectors' }}</div>
        <div class="ops-card__fields">
          <div class="ops-sector-group">
            <div class="ops-sector-group__label">
              {{ isEducationMode ? 'Sectors to Highlight' : 'Impacted Sectors' }}
            </div>
            <div class="ops-sector-group__buttons">
              <button
                v-for="option in opsToCommsSectorOptions"
                :key="option.value"
                type="button"
                class="ops-sector-button"
                :class="{ 'ops-sector-button--active': form.impactedSectors.includes(option.value) }"
                @click="toggleSector(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.ops-to-comms {
  display: grid;
  gap: 16px;
}

.ops-to-comms__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.ops-card {
  display: grid;
  gap: 14px;
  padding: 0 0 14px;
  border: 0;
  border-bottom: 1px solid rgba(255, 232, 100, 0.22);
  border-radius: 0;
  background: transparent;
}

.ops-card--full {
  grid-column: 1 / -1;
}

.ops-mode-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.ops-mode-card {
  display: grid;
  gap: 8px;
  padding: 16px;
  text-align: left;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(171, 199, 235, 0.16);
  box-shadow: none;
}

.ops-mode-card--active {
  background: linear-gradient(180deg, rgba(57, 126, 220, 0.95), rgba(30, 84, 165, 0.96));
  border-color: rgba(173, 210, 255, 0.5);
  box-shadow: 0 14px 28px rgba(24, 69, 140, 0.22);
}

.ops-mode-card__title {
  color: #f3f8ff;
  font-size: 1rem;
  font-weight: 700;
}

.ops-mode-card__description {
  color: rgba(220, 230, 244, 0.82);
  font-size: 0.84rem;
  line-height: 1.4;
}

.ops-card__fields {
  display: grid;
  gap: 14px;
}

.ops-card__fields--single {
  grid-template-columns: minmax(220px, 0.45fr) minmax(0, 1fr);
  align-items: end;
}

.ops-card__fields--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ops-card__fields--three {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.ops-card__fields label,
.ops-sector-group__label {
  display: grid;
  gap: 7px;
  color: rgba(220, 230, 244, 0.82);
  font-weight: 600;
}

.ops-field-note {
  margin: 0;
  color: rgba(220, 230, 244, 0.74);
  font-size: 0.84rem;
  line-height: 1.45;
}

.ops-field-note--accent {
  color: rgba(158, 197, 247, 0.9);
}

.ops-sector-group {
  display: grid;
  gap: 10px;
}

.ops-sector-group__buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ops-sector-button {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(171, 199, 235, 0.16);
  box-shadow: none;
}

.ops-sector-button--active {
  background: linear-gradient(180deg, rgba(57, 126, 220, 0.95), rgba(30, 84, 165, 0.96));
  border-color: rgba(173, 210, 255, 0.5);
  box-shadow: 0 14px 28px rgba(24, 69, 140, 0.22);
}

@media (max-width: 1100px) {
  .ops-to-comms__grid,
  .ops-card__fields--single,
  .ops-mode-grid,
  .ops-card__fields--two,
  .ops-card__fields--three {
    grid-template-columns: 1fr;
  }
}
</style>
