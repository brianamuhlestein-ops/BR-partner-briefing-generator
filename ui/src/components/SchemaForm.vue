<script setup lang="ts">
import { reactive, watch } from 'vue'

import type { BriefingTemplate, ProbabilityTableValue, SectionValue } from '../types'

const props = defineProps<{
  template: BriefingTemplate
  modelValue: Record<string, SectionValue>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, SectionValue>]
}>()

const localSections = reactive<Record<string, SectionValue>>({ ...props.modelValue })

watch(
  () => props.modelValue,
  (value) => {
    Object.keys(localSections).forEach((key) => {
      delete localSections[key]
    })
    Object.assign(localSections, value)
  },
  { deep: true },
)

function getTextValue(sectionId: string): string {
  const currentValue = localSections[sectionId]
  return typeof currentValue === 'string' ? currentValue : ''
}

function updateText(sectionId: string, value: string) {
  localSections[sectionId] = value
  emit('update:modelValue', { ...localSections })
}

function updateTableCell(sectionId: string, category: string, day: string, value: string) {
  const currentTable = (localSections[sectionId] as ProbabilityTableValue | undefined) ?? {}
  const nextTable: ProbabilityTableValue = {
    ...currentTable,
    [category]: {
      ...(currentTable[category] ?? {}),
      [day]: value,
    },
  }
  localSections[sectionId] = nextTable
  emit('update:modelValue', { ...localSections })
}

function getTableValue(sectionId: string, category: string, day: string): string {
  const currentTable = localSections[sectionId]
  if (!currentTable || typeof currentTable === 'string') {
    return ''
  }
  return currentTable[category]?.[day] ?? ''
}
</script>

<template>
  <div>
    <div v-for="section in template.sections" :key="section.id" class="field field-card">
      <div class="field-header">
        <label :for="section.id" class="field-label">{{ section.label }}</label>
        <span class="field-kind">
          {{ section.kind === 'probability_table' ? 'Probability Grid' : 'Narrative Block' }}
        </span>
      </div>

      <textarea
        v-if="section.kind === 'text'"
        :id="section.id"
        :value="getTextValue(section.id)"
        @input="updateText(section.id, ($event.target as HTMLTextAreaElement).value)"
      />

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th></th>
              <th v-for="day in section.days ?? []" :key="day">{{ day }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in section.categories ?? []" :key="category">
              <th>{{ category }}</th>
              <td v-for="day in section.days ?? []" :key="`${section.id}-${category}-${day}`">
                <input
                  type="text"
                  class="probability-input"
                  :value="getTableValue(section.id, category, day)"
                  @input="updateTableCell(section.id, category, day, ($event.target as HTMLInputElement).value)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
