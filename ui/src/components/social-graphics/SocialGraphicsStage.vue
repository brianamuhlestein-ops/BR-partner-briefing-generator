<script setup lang="ts">
import Konva from 'konva'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type {
  SocialGraphicsElement,
  SocialGraphicsImageElement,
  SocialGraphicsScene,
  SocialGraphicsTextElement,
} from '../../types'

const props = defineProps<{
  scene: SocialGraphicsScene
  selectedElementId: string | null
}>()

const emit = defineEmits<{
  'select-element': [elementId: string | null]
  'update-element': [elementId: string, patch: Partial<SocialGraphicsElement>]
}>()

const wrapperRef = ref<HTMLDivElement | null>(null)
const stageRef = ref()
const transformerRef = ref()
const stageWidth = ref(props.scene.width)
const imageCache = ref<Record<string, HTMLImageElement>>({})
const nodeRefs = new Map<string, Konva.Node>()
let resizeObserver: ResizeObserver | null = null

const MAX_DISPLAY_SCALE = 1

const displayScale = computed(() =>
  Math.min(MAX_DISPLAY_SCALE, stageWidth.value / props.scene.width),
)
const stageHeight = computed(() => props.scene.height * displayScale.value)

function isEditable(element: SocialGraphicsElement): boolean {
  return !element.locked
}

function setNodeRef(elementId: string) {
  return (instance: { getNode: () => Konva.Node } | null) => {
    if (!instance) {
      nodeRefs.delete(elementId)
      return
    }
    nodeRefs.set(elementId, instance.getNode())
  }
}

function getImageSource(element: SocialGraphicsImageElement) {
  return imageCache.value[element.id]
}

function buildImageConfig(element: SocialGraphicsImageElement) {
  const image = getImageSource(element)
  if (!image || element.fit === 'contain') {
    return {
      x: element.x,
      y: element.y,
      width: element.width,
      height: element.height,
      image,
      opacity: element.opacity,
      cornerRadius: element.cornerRadius,
      draggable: true,
    }
  }

  const sourceAspect = image.width / image.height
  const targetAspect = element.width / element.height

  let cropWidth = image.width
  let cropHeight = image.height
  let cropX = 0
  let cropY = 0

  if (sourceAspect > targetAspect) {
    cropWidth = image.height * targetAspect
    cropX = (image.width - cropWidth) / 2
  } else {
    cropHeight = image.width / targetAspect
    cropY = (image.height - cropHeight) / 2
  }

  return {
    x: element.x,
    y: element.y,
    width: element.width,
    height: element.height,
    image,
    cropX,
    cropY,
    cropWidth,
    cropHeight,
    opacity: element.opacity,
    cornerRadius: element.cornerRadius,
    draggable: true,
  }
}

function loadImages() {
  const nextImages: Record<string, HTMLImageElement> = {}
  props.scene.elements.forEach((element) => {
    if (element.kind !== 'image' || !element.src) {
      return
    }
    const image = new window.Image()
    image.src = element.src
    nextImages[element.id] = image
  })
  imageCache.value = nextImages
}

function syncTransformer() {
  nextTick(() => {
    const transformer = transformerRef.value?.getNode?.()
    if (!transformer) {
      return
    }

    const selectedNode = props.selectedElementId ? nodeRefs.get(props.selectedElementId) : null
    transformer.nodes(selectedNode ? [selectedNode] : [])
    transformer.getLayer()?.batchDraw()
  })
}

function handleResize() {
  if (!wrapperRef.value) {
    return
  }
  const bounds = wrapperRef.value.getBoundingClientRect()
  stageWidth.value = Math.max(320, bounds.width - 2)
}

function handleStagePointerDown(event: { target: Konva.Node }) {
  const target = event.target
  const stage = stageRef.value?.getNode?.()
  if (target === stage) {
    emit('select-element', null)
  }
}

function selectIfEditable(element: SocialGraphicsElement) {
  if (!isEditable(element)) {
    return
  }
  emit('select-element', element.id)
}

function handleDragEnd(elementId: string, event: { target: Konva.Node }) {
  emit('update-element', elementId, {
    x: Math.round(event.target.x()),
    y: Math.round(event.target.y()),
  })
}

function handleTransformEnd(element: SocialGraphicsElement, event: { target: Konva.Node }) {
  const node = event.target
  const scaleX = node.scaleX()
  const scaleY = node.scaleY()

  node.scaleX(1)
  node.scaleY(1)

  const patch: Partial<SocialGraphicsElement> = {
    x: Math.round(node.x()),
    y: Math.round(node.y()),
    width: Math.max(1, Math.round(node.width() * scaleX)),
    height: Math.max(1, Math.round(node.height() * scaleY)),
  }

  if (element.kind === 'text') {
    ;(patch as Partial<SocialGraphicsTextElement>).fontSize = Math.max(
      18,
      Math.round(element.fontSize * scaleY),
    )
  }

  emit('update-element', element.id, patch)
}

function linePoints(element: SocialGraphicsElement) {
  if (element.kind !== 'line') {
    return []
  }
  return [0, 0, element.width, element.height]
}

watch(
  () => props.scene.elements,
  () => {
    loadImages()
    syncTransformer()
  },
  { deep: true, immediate: true },
)

watch(
  () => props.selectedElementId,
  () => {
    syncTransformer()
  },
)

onMounted(() => {
  handleResize()
  resizeObserver = new ResizeObserver(handleResize)
  if (wrapperRef.value) {
    resizeObserver.observe(wrapperRef.value)
  }
  syncTransformer()
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})

defineExpose({
  toDataURL() {
    const stage = stageRef.value?.getNode?.()
    if (!stage) {
      return ''
    }
    return stage.toDataURL({
      mimeType: 'image/png',
      pixelRatio: props.scene.width / stage.width(),
    })
  },
})
</script>

<template>
  <div class="graphics-stage-shell">
    <div class="graphics-stage-meta">
      <span class="graphics-stage-chip">Canonical Canvas {{ scene.width }} x {{ scene.height }}</span>
    </div>

    <div ref="wrapperRef" class="graphics-stage-wrap">
      <v-stage
        ref="stageRef"
        :config="{
          width: scene.width * displayScale,
          height: stageHeight,
          scaleX: displayScale,
          scaleY: displayScale,
        }"
        @mousedown="handleStagePointerDown"
        @touchstart="handleStagePointerDown"
      >
        <v-layer>
          <template v-for="element in scene.elements" :key="element.id">
            <v-rect
              v-if="element.kind === 'rect' && element.visible"
              :ref="setNodeRef(element.id)"
              :config="{
                x: element.x,
                y: element.y,
                width: element.width,
                height: element.height,
                fill: element.fill,
                cornerRadius: element.cornerRadius,
                opacity: element.opacity,
                draggable: isEditable(element),
                listening: isEditable(element),
              }"
              @click="selectIfEditable(element)"
              @tap="selectIfEditable(element)"
              @dragend="handleDragEnd(element.id, $event)"
              @transformend="handleTransformEnd(element, $event)"
            />

            <v-text
              v-else-if="element.kind === 'text' && element.visible"
              :ref="setNodeRef(element.id)"
              :config="{
                x: element.x,
                y: element.y,
                width: element.width,
                height: element.height,
                text: element.text,
                fill: element.fill,
                fontFamily: element.fontFamily,
                fontSize: element.fontSize,
                fontStyle: element.fontWeight >= 700 ? 'bold' : 'normal',
                align: element.align,
                lineHeight: element.lineHeight,
                opacity: element.opacity,
                draggable: isEditable(element),
                listening: isEditable(element),
              }"
              @click="selectIfEditable(element)"
              @tap="selectIfEditable(element)"
              @dragend="handleDragEnd(element.id, $event)"
              @transformend="handleTransformEnd(element, $event)"
            />

            <v-image
              v-else-if="element.kind === 'image' && element.visible"
              :ref="setNodeRef(element.id)"
              :config="{ ...buildImageConfig(element), draggable: isEditable(element), listening: isEditable(element) }"
              @click="selectIfEditable(element)"
              @tap="selectIfEditable(element)"
              @dragend="handleDragEnd(element.id, $event)"
              @transformend="handleTransformEnd(element, $event)"
            />

            <v-line
              v-else-if="element.kind === 'line' && element.visible"
              :ref="setNodeRef(element.id)"
              :config="{
                x: element.x,
                y: element.y,
                points: linePoints(element),
                stroke: element.stroke,
                strokeWidth: element.strokeWidth,
                opacity: element.opacity,
                draggable: isEditable(element),
                listening: isEditable(element),
              }"
              @click="selectIfEditable(element)"
              @tap="selectIfEditable(element)"
              @dragend="handleDragEnd(element.id, $event)"
              @transformend="handleTransformEnd(element, $event)"
            />
          </template>

          <v-transformer
            ref="transformerRef"
            :config="{
              rotateEnabled: false,
              enabledAnchors: [
                'top-left',
                'top-right',
                'bottom-left',
                'bottom-right',
                'middle-left',
                'middle-right',
              ],
              borderStroke: '#78b4ff',
              anchorFill: '#102643',
              anchorStroke: '#dfeeff',
              anchorSize: 12,
            }"
          />
        </v-layer>
      </v-stage>
    </div>
  </div>
</template>

<style scoped>
.graphics-stage-shell {
  display: grid;
  gap: 14px;
}

.graphics-stage-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.graphics-stage-chip {
  border: 1px solid rgba(171, 199, 235, 0.16);
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(225, 235, 245, 0.82);
  font-size: 0.78rem;
  font-weight: 700;
}

.graphics-stage-wrap {
  overflow: auto;
  border-radius: 18px;
  border: 1px solid rgba(171, 199, 235, 0.16);
  background:
    linear-gradient(180deg, rgba(9, 16, 27, 0.96), rgba(6, 11, 18, 0.98)),
    rgba(4, 10, 18, 0.92);
  padding: 18px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  width: fit-content;
  max-width: 100%;
}
</style>
