<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  recommendedAssetsForContext,
  socialGraphicsAssetApplyTargetLabels,
  socialGraphicsAssetCatalog,
  socialGraphicsAssetCategoryOptions,
  socialGraphicsAssetTypeOptions,
} from '../../assetFinder/catalog'
import type {
  GraphicsWorkspaceMode,
  OpsToCommsRecommendation,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
  SocialGraphicsAssetCategory,
  SocialGraphicsAssetType,
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

const searchTerm = ref('')
const activeType = ref<SocialGraphicsAssetType | 'all'>('all')
const activeCategory = ref<SocialGraphicsAssetCategory | 'all'>('all')
const selectedAssetId = ref<string | null>(null)
const applyTarget = ref<SocialGraphicsAssetApplyTarget>('background')

const recommendedAssets = computed(() =>
  recommendedAssetsForContext(props.recommendation, props.mode),
)

const recommendedAssetIds = computed(() => new Set(recommendedAssets.value.map((asset) => asset.id)))

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
  const term = searchTerm.value.trim().toLowerCase()

  return socialGraphicsAssetCatalog.filter((asset) => {
    if (activeType.value !== 'all' && asset.assetType !== activeType.value) {
      return false
    }
    if (activeCategory.value !== 'all' && asset.category !== activeCategory.value) {
      return false
    }
    if (!term) {
      return true
    }

    return (
      asset.title.toLowerCase().includes(term) ||
      asset.description.toLowerCase().includes(term) ||
      asset.tags.some((tag) => tag.toLowerCase().includes(term))
    )
  })
})

const selectedAsset = computed(() => {
  return (
    socialGraphicsAssetCatalog.find((asset) => asset.id === selectedAssetId.value) ??
    recommendedAssets.value[0] ??
    filteredAssets.value[0] ??
    null
  )
})

const previewAssetList = computed(() => {
  const seen = new Set<string>()
  const merged = [...recommendedAssets.value, ...filteredAssets.value]
  return merged.filter((asset) => {
    if (seen.has(asset.id)) {
      return false
    }
    seen.add(asset.id)
    return true
  })
})

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
  recommendedAssets,
  (assets) => {
    const firstAsset = assets[0]
    if (!selectedAssetId.value && firstAsset) {
      selectedAssetId.value = firstAsset.id
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

function assetAudienceLabel(asset: SocialGraphicsAsset): string {
  if (asset.audience.includes('public') && asset.audience.includes('partners')) {
    return 'Public + partner ready'
  }
  if (asset.audience.includes('mixed')) {
    return 'Mixed audience'
  }
  if (asset.audience.includes('public')) {
    return 'Public leaning'
  }
  if (asset.audience.includes('partners') || asset.audience.includes('internal')) {
    return 'Partner leaning'
  }
  return 'General use'
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
        Surface message-first visual options that support the current Ops to Comms recommendation.
      </p>
    </div>

    <div v-if="recommendation" class="asset-finder__guidance">
      <span class="asset-finder__guidance-chip">Suggested visual: {{ recommendation.recommendedVisualType }}</span>
      <span
        v-for="category in recommendation.recommendedAssetCategories"
        :key="category"
        class="asset-finder__guidance-chip asset-finder__guidance-chip--muted"
      >
        {{ category }}
      </span>
      <p class="asset-finder__guidance-copy">
        {{ recommendation.recommendedMessageEmphasis }}
      </p>
    </div>

    <div class="asset-finder__controls">
      <label class="asset-finder__field">
        Search
        <input v-model="searchTerm" type="search" placeholder="Search approved visuals" />
      </label>

      <div class="asset-finder__control-grid">
        <label class="asset-finder__field">
          Asset Type
          <select v-model="activeType">
            <option v-for="option in socialGraphicsAssetTypeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="asset-finder__field">
          Category
          <select v-model="activeCategory">
            <option
              v-for="option in socialGraphicsAssetCategoryOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </label>
      </div>
    </div>

    <div class="asset-finder__recommended">
      <div class="asset-finder__section-label">Recommended for this case</div>
      <div class="asset-finder__card-row">
        <button
          v-for="asset in recommendedAssets.slice(0, 3)"
          :key="asset.id"
          type="button"
          class="asset-card asset-card--compact"
          :class="{ 'asset-card--active': asset.id === selectedAsset?.id }"
          @click="selectAsset(asset.id)"
        >
          <img class="asset-card__thumb" :src="asset.thumbnailPath ?? asset.localPath ?? asset.url" :alt="asset.title" />
          <span class="asset-card__title">{{ asset.title }}</span>
          <span class="asset-card__meta">{{ assetAudienceLabel(asset) }}</span>
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
          <span v-if="recommendedAssetIds.has(selectedAsset.id)" class="asset-finder__recommended-badge">
            Recommended
          </span>
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

    <div class="asset-finder__catalog">
      <div class="asset-finder__section-label">Approved catalog</div>
      <div class="asset-finder__catalog-grid">
        <button
          v-for="asset in previewAssetList"
          :key="asset.id"
          type="button"
          class="asset-card"
          :class="{ 'asset-card--active': asset.id === selectedAsset?.id }"
          @click="selectAsset(asset.id)"
        >
          <img class="asset-card__thumb" :src="asset.thumbnailPath ?? asset.localPath ?? asset.url" :alt="asset.title" />
          <span class="asset-card__title-row">
            <span class="asset-card__title">{{ asset.title }}</span>
            <span v-if="recommendedAssetIds.has(asset.id)" class="asset-card__pill">Recommended</span>
          </span>
          <span class="asset-card__meta">{{ asset.category }} | {{ asset.assetType }}</span>
          <span class="asset-card__tags">{{ asset.tags.slice(0, 3).join(' • ') }}</span>
        </button>
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
.asset-finder__guidance-copy,
.asset-finder__use,
.asset-finder__empty-note {
  margin: 0;
  color: rgba(220, 230, 244, 0.75);
  font-size: 0.84rem;
  line-height: 1.45;
}

.asset-finder__guidance {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(118, 175, 255, 0.2);
  background: rgba(85, 138, 224, 0.08);
}

.asset-finder__guidance-chip {
  display: inline-flex;
  width: fit-content;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(113, 187, 255, 0.18);
  color: #e4f0ff;
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: capitalize;
}

.asset-finder__guidance-chip--muted {
  background: rgba(255, 255, 255, 0.05);
}

.asset-finder__controls,
.asset-finder__preview {
  display: grid;
  gap: 12px;
}

.asset-finder__control-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
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

.asset-finder__card-row,
.asset-finder__catalog-grid {
  display: grid;
  gap: 10px;
}

.asset-finder__card-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.asset-finder__preview {
  grid-template-columns: 220px minmax(0, 1fr);
  align-items: start;
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

.asset-finder__recommended-badge,
.asset-card__pill {
  display: inline-flex;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(103, 191, 255, 0.16);
  color: #dff1ff;
  font-size: 0.72rem;
  font-weight: 700;
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

.asset-card--compact {
  padding: 8px;
}

.asset-card--active {
  border-color: rgba(141, 206, 255, 0.55);
  box-shadow: 0 12px 24px rgba(21, 58, 116, 0.28);
}

.asset-card__thumb {
  aspect-ratio: 16 / 9;
}

.asset-card__title-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
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

  .asset-finder__card-row {
    grid-template-columns: 1fr;
  }
}
</style>
