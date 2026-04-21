<script setup lang="ts">
defineProps<{
  title: string
  description: string
  canvasLabel: string
}>()
</script>

<template>
  <section class="graphic-placeholder">
    <header class="graphic-placeholder__header">
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </header>

    <div class="graphic-placeholder__canvas">
      <div class="graphic-placeholder__badge">Future Workflow</div>
      <div class="graphic-placeholder__label">{{ canvasLabel }}</div>
      <p>
        This mode is reserved for a future slide or graphic composition workflow. For the demo,
        this placeholder marks where the graphic workspace will live.
      </p>
    </div>
  </section>
</template>
