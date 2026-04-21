<script setup lang="ts">
import type {
  SocialGraphicsElement,
  SocialGraphicsImageElement,
  SocialGraphicsLineElement,
  SocialGraphicsRectElement,
  SocialGraphicsTextElement,
} from '../../types'

const props = defineProps<{
  element: SocialGraphicsElement | null
}>()

const emit = defineEmits<{
  update: [elementId: string, patch: Partial<SocialGraphicsElement>]
  'replace-image': [elementId: string, src: string]
}>()

function updateField(field: string, value: string | number | boolean) {
  if (!props.element) {
    return
  }

  emit('update', props.element.id, { [field]: value } as Partial<SocialGraphicsElement>)
}

function readTargetValue(event: Event): string {
  const target = event.target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null
  return target?.value ?? ''
}

function handleBooleanField(field: string, event: Event) {
  updateField(field, readTargetValue(event) === 'true')
}

function handleStringField(field: string, event: Event) {
  updateField(field, readTargetValue(event))
}

function handleNumberField(field: string, event: Event) {
  updateField(field, Number(readTargetValue(event)))
}

function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0]
  const elementId = props.element?.kind === 'image' ? props.element.id : null
  if (!file || !elementId) {
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    if (typeof reader.result === 'string') {
      emit('replace-image', elementId, reader.result)
    }
  }
  reader.readAsDataURL(file)

  if (input) {
    input.value = ''
  }
}

function handleImageSourceInput(event: Event) {
  if (!props.element) {
    return
  }
  emit('replace-image', props.element.id, readTargetValue(event))
}

function asTextElement(element: SocialGraphicsElement | null): SocialGraphicsTextElement | null {
  return element?.kind === 'text' ? element : null
}

function asRectElement(element: SocialGraphicsElement | null): SocialGraphicsRectElement | null {
  return element?.kind === 'rect' ? element : null
}

function asImageElement(element: SocialGraphicsElement | null): SocialGraphicsImageElement | null {
  return element?.kind === 'image' ? element : null
}

function asLineElement(element: SocialGraphicsElement | null): SocialGraphicsLineElement | null {
  return element?.kind === 'line' ? element : null
}
</script>

<template>
  <section class="social-side-card">
    <div class="social-side-card__header">
      <div>
        <div class="panel-kicker">Inspector</div>
        <h2 class="social-side-card__title">Selected Element</h2>
      </div>
    </div>

    <div v-if="element" class="inspector-fields">
      <div class="inspector-chip">{{ element.name }}</div>

      <label class="inspector-field">
        Visible
        <select :value="String(element.visible)" @change="handleBooleanField('visible', $event)">
          <option value="true">Visible</option>
          <option value="false">Hidden</option>
        </select>
      </label>

      <div class="inspector-grid">
        <label class="inspector-field">
          X
          <input type="number" :value="element.x" @input="handleNumberField('x', $event)" />
        </label>

        <label class="inspector-field">
          Y
          <input type="number" :value="element.y" @input="handleNumberField('y', $event)" />
        </label>

        <label class="inspector-field">
          Width
          <input type="number" :value="element.width" @input="handleNumberField('width', $event)" />
        </label>

        <label class="inspector-field">
          Height
          <input type="number" :value="element.height" @input="handleNumberField('height', $event)" />
        </label>
      </div>

      <label class="inspector-field">
        Opacity
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          :value="element.opacity"
          @input="handleNumberField('opacity', $event)"
        />
      </label>

      <template v-if="asTextElement(element)">
        <label class="inspector-field">
          Text
          <textarea :value="asTextElement(element)?.text" @input="handleStringField('text', $event)" />
        </label>

        <div class="inspector-grid">
          <label class="inspector-field">
            Font Size
            <input
              type="number"
              :value="asTextElement(element)?.fontSize"
              @input="handleNumberField('fontSize', $event)"
            />
          </label>

          <label class="inspector-field">
            Weight
            <input
              type="number"
              step="100"
              min="300"
              max="900"
              :value="asTextElement(element)?.fontWeight"
              @input="handleNumberField('fontWeight', $event)"
            />
          </label>
        </div>

        <label class="inspector-field inspector-field--color">
          Fill
          <input type="color" :value="asTextElement(element)?.fill" @input="handleStringField('fill', $event)" />
        </label>

        <label class="inspector-field">
          Alignment
          <select :value="asTextElement(element)?.align" @change="handleStringField('align', $event)">
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
          </select>
        </label>
      </template>

      <template v-if="asRectElement(element)">
        <label class="inspector-field inspector-field--color">
          Fill
          <input type="color" :value="asRectElement(element)?.fill" @input="handleStringField('fill', $event)" />
        </label>

        <label class="inspector-field">
          Corner Radius
          <input
            type="number"
            :value="asRectElement(element)?.cornerRadius"
            @input="handleNumberField('cornerRadius', $event)"
          />
        </label>
      </template>

      <template v-if="asImageElement(element)">
        <label class="inspector-field">
          Image Source
          <input type="text" :value="asImageElement(element)?.src" @input="handleImageSourceInput($event)" />
        </label>

        <label class="inspector-field">
          Upload Image
          <input type="file" accept="image/png,image/jpeg,image/webp" @change="handleImageUpload" />
        </label>

        <label class="inspector-field">
          Fit
          <select :value="asImageElement(element)?.fit" @change="handleStringField('fit', $event)">
            <option value="contain">Contain</option>
            <option value="cover">Cover</option>
          </select>
        </label>

        <label class="inspector-field">
          Corner Radius
          <input
            type="number"
            :value="asImageElement(element)?.cornerRadius"
            @input="handleNumberField('cornerRadius', $event)"
          />
        </label>

        <p class="inspector-note">
          Uploaded files are safest for export. Remote images can fail if the source blocks canvas access.
        </p>
      </template>

      <template v-if="asLineElement(element)">
        <label class="inspector-field inspector-field--color">
          Stroke
          <input type="color" :value="asLineElement(element)?.stroke" @input="handleStringField('stroke', $event)" />
        </label>

        <label class="inspector-field">
          Stroke Width
          <input
            type="number"
            :value="asLineElement(element)?.strokeWidth"
            @input="handleNumberField('strokeWidth', $event)"
          />
        </label>
      </template>
    </div>

    <div v-else class="inspector-empty">
      Select a layer to edit position, text, colors, and image properties.
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

.inspector-fields {
  display: grid;
  gap: 12px;
}

.inspector-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.inspector-field {
  display: grid;
  gap: 6px;
  color: rgba(220, 230, 244, 0.82);
  font-size: 0.88rem;
  font-weight: 600;
}

.inspector-field input,
.inspector-field select,
.inspector-field textarea {
  width: 100%;
}

.inspector-field--color input[type='color'] {
  min-height: 42px;
  padding: 4px;
}

.inspector-chip {
  display: inline-flex;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(105, 168, 255, 0.14);
  border: 1px solid rgba(105, 168, 255, 0.2);
  color: #dbe9fb;
  font-size: 0.78rem;
  font-weight: 700;
}

.inspector-note,
.inspector-empty {
  margin: 0;
  color: rgba(220, 230, 244, 0.72);
  font-size: 0.84rem;
}
</style>
