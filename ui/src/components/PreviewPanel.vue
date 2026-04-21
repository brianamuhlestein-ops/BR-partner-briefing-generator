<script setup lang="ts">
import { computed } from 'vue'

import type { DerivedOutputStatus, DownstreamOutputId } from '../types'

const props = defineProps<{
  outputs: DerivedOutputStatus[]
  selectedOutput: DownstreamOutputId
  pdfMessage: string
}>()

const emit = defineEmits<{
  'update:selectedOutput': [value: DownstreamOutputId]
}>()

const activeOutput = computed(() => {
  return props.outputs.find((output) => output.id === props.selectedOutput) ?? props.outputs[0]
})

function selectOutput(outputId: DownstreamOutputId) {
  emit('update:selectedOutput', outputId)
}
</script>

<template>
  <section class="panel panel--side">
    <div class="panel-header">
      <div>
        <div class="panel-kicker">Outputs</div>
        <h2 class="panel-title">Downstream Products</h2>
      </div>
    </div>

    <div class="output-tab-row">
      <button
        v-for="output in outputs"
        :key="output.id"
        type="button"
        class="output-tab"
        :class="{ 'output-tab--active': output.id === selectedOutput }"
        @click="selectOutput(output.id)"
      >
        <span>{{ output.label }}</span>
        <span
          class="output-tab__status"
          :class="{
            'output-tab__status--ready': output.readiness === 'ready',
            'output-tab__status--missing': output.readiness === 'missing_inputs',
          }"
        >
          {{ output.readiness === 'ready' ? 'Ready' : `Missing ${output.missingSections.length}` }}
        </span>
      </button>
    </div>

    <template v-if="activeOutput">
      <div class="output-summary">
        <div class="output-summary__label">{{ activeOutput.label }} Preview</div>
        <div
          class="output-summary__chip"
          :class="{
            'output-summary__chip--ready': activeOutput.readiness === 'ready',
            'output-summary__chip--missing': activeOutput.readiness === 'missing_inputs',
          }"
        >
          {{ activeOutput.readiness === 'ready' ? 'Ready to Review' : 'Not Enough Information' }}
        </div>
      </div>

      <iframe
        v-if="activeOutput.html"
        class="preview-frame"
        :srcdoc="activeOutput.html"
        :title="`${activeOutput.label} Preview`"
      />

      <div v-else class="preview-empty-state">
        <p class="message preview-empty-state__message">
          Not enough information for {{ activeOutput.label }}.
        </p>
        <p class="message">Complete the following master sections to populate this downstream briefing:</p>
        <ul class="output-missing-list">
          <li v-for="section in activeOutput.missingSections" :key="section">
            {{ section }}
          </li>
        </ul>
      </div>

      <div class="pdf-status-card">
        <div class="pdf-status-card__title">PDF Status</div>
        <p class="message">{{ pdfMessage || activeOutput.pdfMessage }}</p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.output-tab-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.output-tab {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
  min-width: 0;
}

.output-tab--active {
  border-color: rgba(173, 210, 255, 0.5);
  box-shadow: 0 14px 28px rgba(24, 69, 140, 0.28);
}

.output-tab__status {
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  white-space: nowrap;
}

.output-tab__status--ready {
  background: rgba(91, 214, 141, 0.16);
  color: #d9ffe8;
}

.output-tab__status--missing {
  background: rgba(255, 188, 92, 0.18);
  color: #ffe4b5;
}

.output-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.output-summary__label {
  color: #f2f7ff;
  font-size: 1rem;
  font-weight: 700;
}

.output-summary__chip {
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 6px 10px;
}

.output-summary__chip--ready {
  background: rgba(91, 214, 141, 0.16);
  color: #d9ffe8;
}

.output-summary__chip--missing {
  background: rgba(255, 188, 92, 0.18);
  color: #ffe4b5;
}

.preview-empty-state {
  border: 1px dashed rgba(171, 199, 235, 0.2);
  border-radius: 14px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.preview-empty-state__message {
  color: #f2f7ff;
  font-weight: 700;
}

.output-missing-list {
  color: rgba(220, 230, 244, 0.8);
  margin: 0;
  padding-left: 20px;
}

.output-missing-list li + li {
  margin-top: 8px;
}

.pdf-status-card {
  margin-top: 14px;
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-radius: 14px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
}

.pdf-status-card__title {
  color: #f2f7ff;
  font-size: 0.92rem;
  font-weight: 700;
  margin-bottom: 8px;
}
</style>
