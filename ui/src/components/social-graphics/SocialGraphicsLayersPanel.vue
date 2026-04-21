<script setup lang="ts">
import type { SocialGraphicsScene } from '../../types'

defineProps<{
  scene: SocialGraphicsScene
  selectedElementId: string | null
}>()

const emit = defineEmits<{
  select: [elementId: string]
  toggle: [elementId: string]
  move: [elementId: string, direction: 'up' | 'down']
}>()
</script>

<template>
  <section class="social-side-card">
    <div class="social-side-card__header">
      <div>
        <div class="panel-kicker">Layers</div>
        <h2 class="social-side-card__title">Element Stack</h2>
      </div>
    </div>

    <div class="layer-list">
      <button
        v-for="(element, index) in [...scene.elements].reverse()"
        :key="element.id"
        type="button"
        class="layer-item"
        :class="{ 'layer-item--active': element.id === selectedElementId }"
        @click="emit('select', element.id)"
      >
        <span class="layer-item__name">{{ element.name }}</span>
        <span class="layer-item__meta">{{ element.kind }}</span>
        <span class="layer-item__actions">
          <span class="layer-item__action" @click.stop="emit('toggle', element.id)">
            {{ element.visible ? 'Hide' : 'Show' }}
          </span>
          <span
            v-if="scene.elements.length - 1 - index < scene.elements.length - 1"
            class="layer-item__action"
            @click.stop="emit('move', element.id, 'up')"
          >
            Up
          </span>
          <span
            v-if="scene.elements.length - 1 - index > 0"
            class="layer-item__action"
            @click.stop="emit('move', element.id, 'down')"
          >
            Down
          </span>
        </span>
      </button>
    </div>
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

.layer-list {
  display: grid;
  gap: 10px;
}

.layer-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 4px 8px;
  align-items: center;
  text-align: left;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
}

.layer-item--active {
  border-color: rgba(173, 210, 255, 0.5);
  box-shadow: 0 14px 28px rgba(24, 69, 140, 0.22);
}

.layer-item__name {
  color: #f2f7ff;
  font-weight: 700;
}

.layer-item__meta {
  color: rgba(220, 230, 244, 0.65);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.layer-item__actions {
  display: inline-flex;
  flex-wrap: wrap;
  justify-content: end;
  gap: 8px;
  grid-column: 2;
  grid-row: 1 / span 2;
}

.layer-item__action {
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #dce8f5;
  font-size: 0.74rem;
  font-weight: 700;
}
</style>
