<script setup lang="ts">
import type { ContextItem } from '../types'

defineProps<{
  alerts: ContextItem[]
  advisories: ContextItem[]
}>()
</script>

<template>
  <aside class="panel panel--side">
    <div class="panel-header">
      <div>
        <div class="panel-kicker">Context</div>
        <h2 class="panel-title">Operational Context</h2>
      </div>
    </div>

    <section class="context-section">
      <h3>Active Alerts</h3>
      <ul class="context-list">
        <li v-for="item in alerts" :key="item.id">
          {{ item.summary }}
        </li>
      </ul>
    </section>

    <section v-if="advisories.length" class="context-section">
      <h3>ICAO Advisories</h3>
      <ul class="context-list">
        <li v-for="item in advisories" :key="item.id">
          {{ item.summary }}
        </li>
      </ul>
    </section>
  </aside>
</template>
