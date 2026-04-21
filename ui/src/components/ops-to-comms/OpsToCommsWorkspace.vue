<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import { graphicsTemplateLabel } from '../../socialGraphics/templates'
import {
  buildOpsToCommsRecommendation,
  createDefaultOpsToCommsInput,
  opsToCommsAudienceOptions,
  opsToCommsEventOptions,
  opsToCommsLevelOptions,
  opsToCommsPathLabel,
  opsToCommsSectorOptions,
  opsToCommsSeverityOptions,
  opsToCommsTimingOptions,
} from '../../opsToComms/recommendation'
import type {
  OpsToCommsPathId,
  OpsToCommsRecommendation,
  OpsToCommsSector,
} from '../../types'

const emit = defineEmits<{
  'update:recommendation': [recommendation: OpsToCommsRecommendation]
  'open-path': [path: OpsToCommsPathId, recommendation: OpsToCommsRecommendation]
}>()

const form = reactive(createDefaultOpsToCommsInput())

const recommendation = computed(() => {
  return buildOpsToCommsRecommendation({
    eventType: form.eventType,
    severity: form.severity,
    timingStatus: form.timingStatus,
    impactedSectors: [...form.impactedSectors],
    riskLevel: form.riskLevel,
    impactProbability: form.impactProbability,
    confidence: form.confidence,
    audience: form.audience,
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

function openWorkspace(path: OpsToCommsPathId) {
  emit('open-path', path, recommendation.value)
}

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
      <section class="ops-card">
        <div class="panel-kicker">1. Event Characterization</div>
        <div class="ops-card__fields ops-card__fields--two">
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

      <section class="ops-card">
        <div class="panel-kicker">2. Risk / Confidence / Timing</div>
        <div class="ops-card__fields ops-card__fields--three">
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

      <section class="ops-card">
        <div class="panel-kicker">3. Impacted Sectors and Audience</div>
        <div class="ops-card__fields">
          <label>
            Intended Audience
            <select v-model="form.audience">
              <option v-for="option in opsToCommsAudienceOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <div class="ops-sector-group">
            <div class="ops-sector-group__label">Impacted Sectors</div>
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

      <section class="ops-card ops-card--recommendation">
        <div class="panel-kicker">4. Communication Recommendation</div>

        <div class="ops-recommendation-grid">
          <div class="ops-recommendation-item">
            <div class="ops-recommendation-item__label">Primary Path</div>
            <div class="ops-recommendation-item__value">
              {{ opsToCommsPathLabel(recommendation.recommendedPrimaryPath) }}
            </div>
          </div>

          <div class="ops-recommendation-item">
            <div class="ops-recommendation-item__label">Secondary Path</div>
            <div class="ops-recommendation-item__value">
              {{
                recommendation.recommendedSecondaryPath
                  ? opsToCommsPathLabel(recommendation.recommendedSecondaryPath)
                  : 'None'
              }}
            </div>
          </div>

          <div class="ops-recommendation-item">
            <div class="ops-recommendation-item__label">Recommended Template</div>
            <div class="ops-recommendation-item__value">
              {{ graphicsTemplateLabel(recommendation.recommendedTemplate) }}
            </div>
          </div>

          <div class="ops-recommendation-item">
            <div class="ops-recommendation-item__label">Headline Tone</div>
            <div class="ops-recommendation-item__value ops-recommendation-item__value--caps">
              {{ recommendation.recommendedHeadlineTone }}
            </div>
          </div>
        </div>

        <div class="ops-message-card">
          <div class="ops-message-card__label">Message Emphasis</div>
          <p class="message ops-message-card__text">
            {{ recommendation.recommendedMessageEmphasis }}
          </p>
        </div>

        <div class="ops-summary-card">
          <div class="ops-summary-card__title">Narrative Summary</div>
          <p class="message ops-summary-card__text">
            {{ recommendation.summary }}
          </p>
        </div>

        <div class="toolbar-actions ops-actions">
          <button
            type="button"
            :class="{ 'ops-actions__button--secondary': recommendation.recommendedPrimaryPath !== 'social-design-review' }"
            @click="openWorkspace('social-design-review')"
          >
            Open Social Media Design Review
          </button>

          <button
            type="button"
            :class="{ 'ops-actions__button--secondary': recommendation.recommendedPrimaryPath !== 'partner-design-review' }"
            @click="openWorkspace('partner-design-review')"
          >
            Open Partner Graphic Design Review
          </button>
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
  gap: 16px;
}

.ops-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.ops-card__fields {
  display: grid;
  gap: 14px;
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

.ops-card--recommendation {
  gap: 16px;
}

.ops-recommendation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.ops-recommendation-item,
.ops-message-card,
.ops-summary-card {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(171, 199, 235, 0.14);
  background: rgba(255, 255, 255, 0.04);
}

.ops-recommendation-item__label,
.ops-message-card__label {
  color: rgba(158, 197, 247, 0.8);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.ops-recommendation-item__value {
  color: #f2f7ff;
  font-size: 1rem;
  font-weight: 700;
}

.ops-recommendation-item__value--caps {
  text-transform: capitalize;
}

.ops-message-card__text,
.ops-summary-card__text {
  margin-bottom: 0;
}

.ops-summary-card__title {
  color: #f2f7ff;
  font-size: 0.98rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.ops-actions {
  margin-top: 2px;
}

.ops-actions__button--secondary {
  background: linear-gradient(180deg, rgba(26, 45, 73, 0.96), rgba(16, 31, 52, 0.98));
}

@media (max-width: 1100px) {
  .ops-card__fields--two,
  .ops-card__fields--three,
  .ops-recommendation-grid {
    grid-template-columns: 1fr;
  }
}
</style>
