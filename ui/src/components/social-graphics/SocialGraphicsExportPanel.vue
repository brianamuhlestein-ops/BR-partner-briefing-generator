<script setup lang="ts">
import type { SocialGraphicsExportResult } from '../../types'

defineProps<{
  draftId: string | null
  saveStatus: string
  exportResult: SocialGraphicsExportResult | null
}>()
</script>

<template>
  <section class="social-side-card">
    <div class="social-side-card__header">
      <div>
        <div class="panel-kicker">Export</div>
        <h2 class="social-side-card__title">Output Variants</h2>
      </div>
    </div>

    <div class="export-status">
      <div v-if="draftId" class="status-chip">Draft {{ draftId }}</div>
      <p class="message export-status__message">{{ saveStatus }}</p>
    </div>

    <div v-if="exportResult" class="export-variants">
      <a
        v-for="variant in exportResult.variants"
        :key="variant.variant_id"
        class="export-variant"
        :href="variant.url"
        target="_blank"
        rel="noreferrer"
      >
        <div class="export-variant__label">{{ variant.label }}</div>
        <div class="export-variant__meta">{{ variant.width }} x {{ variant.height }}</div>
      </a>
    </div>

    <p v-else class="message export-empty">
      Export results will appear here after the base PNG is sent to the backend.
    </p>
  </section>
</template>

<style scoped>
.social-side-card {
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-radius: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.social-side-card__header {
  margin-bottom: 12px;
}

.social-side-card__title {
  margin: 0;
  color: #f2f7ff;
  font-size: 1.1rem;
}

.export-status__message {
  margin-bottom: 0;
}

.export-variants {
  display: grid;
  gap: 10px;
}

.export-variant {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(171, 199, 235, 0.16);
  background: rgba(255, 255, 255, 0.04);
  color: #f2f7ff;
  text-decoration: none;
}

.export-variant__label {
  font-weight: 700;
}

.export-variant__meta {
  color: rgba(220, 230, 244, 0.72);
  font-size: 0.82rem;
}

.export-empty {
  margin-bottom: 0;
}
</style>
