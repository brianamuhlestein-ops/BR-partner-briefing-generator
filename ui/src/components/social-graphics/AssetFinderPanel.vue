<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  catalogAssetsForLibrary,
  filterAssetsByLibraryCategory,
  socialGraphicsAssetApplyTargetLabels,
  socialGraphicsLibraryFilterOptions,
  type SocialGraphicsLibraryFilter,
} from '../../assetFinder/catalog'
import type {
  GraphicsWorkspaceMode,
  OpsToCommsRecommendation,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
  SocialGraphicsScene,
} from '../../types'

const props = defineProps<{
  mode: GraphicsWorkspaceMode
  recommendation?: OpsToCommsRecommendation | null
  scene: SocialGraphicsScene
  selectedElementId: string | null
}>()

const emit = defineEmits<{
  'apply-asset': [asset: SocialGraphicsAsset, target: SocialGraphicsAssetApplyTarget]
}>()

const activeCategory = ref<SocialGraphicsLibraryFilter>('all-images')
const selectedAssetId = ref<string | null>(null)
const applyTarget = ref<SocialGraphicsAssetApplyTarget>('background')

const libraryAssets = computed(() => catalogAssetsForLibrary(props.recommendation))

const availableTargets = computed<SocialGraphicsAssetApplyTarget[]>(() => {
  const targets = new Set<SocialGraphicsAssetApplyTarget>()

  for (const element of props.scene.elements) {
    if (element.kind !== 'image') {
      continue
    }
    if (element.assetRole === 'background') {
      targets.add('background')
    }
    if (element.assetRole === 'logo') {
      targets.add('logo')
    }
    if (element.assetRole === 'main-image') {
      targets.add('main-image')
    }
    if (element.assetRole === 'secondary-image') {
      targets.add('secondary-image')
    }
    if (element.assetRole === 'icon-slot') {
      targets.add('icon-slot')
    }
  }

  const selectedElement = props.scene.elements.find((element) => element.id === props.selectedElementId)
  if (selectedElement?.kind === 'image') {
    targets.add('selected-image')
  }

  return [...targets]
})

const filteredAssets = computed(() => {
  return filterAssetsByLibraryCategory(libraryAssets.value, activeCategory.value)
})

const selectedAsset = computed(() => {
  return (
    libraryAssets.value.find((asset) => asset.id === selectedAssetId.value) ??
    filteredAssets.value[0] ??
    null
  )
})

const previewAssetList = computed(() => filteredAssets.value)

function applyTargetForAsset(asset: SocialGraphicsAsset | null): SocialGraphicsAssetApplyTarget {
  if (!asset) {
    return availableTargets.value[0] ?? 'background'
  }

  if (availableTargets.value.includes(asset.defaultApplyTarget)) {
    return asset.defaultApplyTarget
  }

  return availableTargets.value[0] ?? asset.defaultApplyTarget
}

watch(
  [selectedAsset, availableTargets],
  ([asset]) => {
    applyTarget.value = applyTargetForAsset(asset)
  },
  { immediate: true },
)

watch(
  filteredAssets,
  (assets) => {
    const selectedStillVisible = assets.some((asset) => asset.id === selectedAssetId.value)
    if (!selectedStillVisible) {
      selectedAssetId.value = assets[0]?.id ?? null
    }
  },
  { immediate: true },
)

function selectAsset(assetId: string) {
  selectedAssetId.value = assetId
}

function handleApplyAsset() {
  if (!selectedAsset.value) {
    return
  }

  emit('apply-asset', selectedAsset.value, applyTarget.value)
}

function categoryLabel(filter: SocialGraphicsLibraryFilter): string {
  return socialGraphicsLibraryFilterOptions.find((option) => option.value === filter)?.label ?? 'All Images'
}
</script>

<template>
  <section class="social-side-card asset-finder">
    <div class="social-side-card__header">
      <div>
        <div class="panel-kicker">Asset Finder</div>
        <h2 class="social-side-card__title">Visual Finder</h2>
      </div>
      <p class="asset-finder__intro">
        Review approved local graphics and insert them into the current slide.
      </p>
    </div>

    <div class="asset-finder__controls">
      <label class="asset-finder__field">
        Category
        <select v-model="activeCategory">
          <option v-for="option in socialGraphicsLibraryFilterOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
    </div>

    <div class="asset-finder__catalog">
      <div class="asset-finder__section-label">Approved catalog</div>
      <div class="asset-finder__catalog-grid">
        <button
          v-for="asset in previewAssetList"
          :key="asset.id"
          type="button"
          class="asset-card asset-card--catalog"
          :class="{ 'asset-card--active': asset.id === selectedAsset?.id }"
          @click="selectAsset(asset.id)"
        >
          <img class="asset-card__thumb" :src="asset.thumbnailPath ?? asset.localPath ?? asset.url" :alt="asset.title" />
          <span class="asset-card__title">{{ asset.title }}</span>
          <span class="asset-card__meta">{{ categoryLabel(asset.tags.includes('cme-library') ? 'cme' : 'all-images') }}</span>
          <span class="asset-card__tags">{{ asset.tags.slice(0, 3).join(' • ') }}</span>
        </button>
      </div>
    </div>

    <div class="asset-finder__preview" v-if="selectedAsset">
      <img
        class="asset-finder__preview-image"
        :src="selectedAsset.localPath ?? selectedAsset.url"
        :alt="selectedAsset.title"
      />
      <div class="asset-finder__preview-copy">
        <div class="asset-finder__preview-title-row">
          <h3>{{ selectedAsset.title }}</h3>
        </div>
        <p>{{ selectedAsset.description }}</p>
        <p class="asset-finder__use">{{ selectedAsset.recommendedUse }}</p>

        <div class="asset-finder__tags">
          <span v-for="tag in selectedAsset.tags" :key="tag" class="asset-finder__tag">{{ tag }}</span>
        </div>

        <label class="asset-finder__field">
          Apply To
          <select v-model="applyTarget">
            <option
              v-for="target in availableTargets"
              :key="target"
              :value="target"
            >
              {{ socialGraphicsAssetApplyTargetLabels[target] }}
            </option>
          </select>
        </label>

        <button
          type="button"
          :disabled="availableTargets.length === 0"
          @click="handleApplyAsset"
        >
          Insert Asset
        </button>

        <p v-if="availableTargets.length === 0" class="asset-finder__empty-note">
          This template does not currently expose an image slot for insertion.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.asset-finder {
  display: grid;
  gap: 16px;
}

.asset-finder__intro,
.asset-finder__use,
.asset-finder__empty-note {
  margin: 0;
  color: rgba(220, 230, 244, 0.75);
  font-size: 0.84rem;
  line-height: 1.45;
}

.asset-finder__controls,
.asset-finder__preview {
  display: grid;
  gap: 12px;
}

.asset-finder__field {
  display: grid;
  gap: 6px;
  color: rgba(220, 230, 244, 0.82);
  font-size: 0.86rem;
  font-weight: 600;
}

.asset-finder__section-label {
  color: rgba(220, 230, 244, 0.78);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.asset-finder__catalog-grid {
  display: grid;
  gap: 10px;
}

.asset-finder__preview {
  grid-template-columns: 220px minmax(0, 1fr);
  align-items: start;
}

.asset-finder__catalog-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.asset-finder__preview-image,
.asset-card__thumb {
  width: 100%;
  border-radius: 14px;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.04);
}

.asset-finder__preview-image {
  min-height: 146px;
  border: 1px solid rgba(171, 199, 235, 0.14);
}

.asset-finder__preview-copy {
  display: grid;
  gap: 10px;
}

.asset-finder__preview-title-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.asset-finder__preview-title-row h3 {
  margin: 0;
  color: #f3f8ff;
  font-size: 1rem;
}

.asset-finder__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.asset-finder__tag {
  display: inline-flex;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #d7e7f8;
  font-size: 0.72rem;
}

.asset-card {
  display: grid;
  gap: 8px;
  padding: 10px;
  text-align: left;
  background: rgba(255, 255, 255, 0.03);
}

.asset-card--catalog {
  padding: 8px;
  gap: 6px;
}

.asset-card--catalog .asset-card__thumb {
  aspect-ratio: 1 / 1;
}

.asset-card--catalog .asset-card__title {
  font-size: 0.78rem;
}

.asset-card--catalog .asset-card__meta,
.asset-card--catalog .asset-card__tags {
  font-size: 0.68rem;
}

.asset-card--active {
  border-color: rgba(141, 206, 255, 0.55);
  box-shadow: 0 12px 24px rgba(21, 58, 116, 0.28);
}

.asset-card__thumb {
  aspect-ratio: 16 / 9;
}

.asset-card__title {
  color: #f2f7ff;
  font-size: 0.88rem;
  font-weight: 700;
}

.asset-card__meta,
.asset-card__tags {
  color: rgba(220, 230, 244, 0.68);
  font-size: 0.74rem;
}

@media (max-width: 1320px) {
  .asset-finder__preview {
    grid-template-columns: 1fr;
  }

  .asset-finder__catalog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
