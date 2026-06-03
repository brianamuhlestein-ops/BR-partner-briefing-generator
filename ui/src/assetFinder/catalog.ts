import type {
  OpsToCommsRecommendation,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
} from '../types'

export type SocialGraphicsLibraryFilter = 'all-images' | 'cme'

export const socialGraphicsLibraryFilterOptions: {
  value: SocialGraphicsLibraryFilter
  label: string
}[] = [
  { value: 'all-images', label: 'All Images' },
  { value: 'cme', label: 'CME' },
]

export const socialGraphicsAssetApplyTargetLabels: Record<SocialGraphicsAssetApplyTarget, string> = {
  background: 'Background',
  logo: 'Logo slot',
  'main-image': 'Main image block',
  'secondary-image': 'Secondary image block',
  'icon-slot': 'Icon slot',
  'selected-image': 'Selected image layer',
}

export const socialGraphicsAssetCatalog: SocialGraphicsAsset[] = [
  {
    id: 'cme-enlil-depiction',
    title: 'CME ENLIL Depiction',
    description: 'ENLIL-style CME propagation visual for explaining modeled travel and downstream geomagnetic relevance.',
    assetType: 'chart',
    category: 'maps-charts',
    library: 'education-outreach',
    tags: ['cme-library', 'cme', 'ENLIL', 'model', 'timeline'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: ['cme'],
    recommendedUse: 'Use when explaining how a CME moves outward through space and why arrival timing matters.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/cme/enlil-depiction.png',
    thumbnailPath: '/assets/visual-finder/cme/enlil-depiction.png',
    approvedForUse: true,
    priority: 10,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'cme-impacted-sectors',
    title: 'CME Impacted Sectors',
    description: 'Sector-focused CME impact graphic highlighting communications, satellite, GNSS, and power grid relevance.',
    assetType: 'chart',
    category: 'sector-operations',
    library: 'education-outreach',
    tags: ['cme-library', 'cme', 'impacted sectors', 'GNSS', 'satellite', 'power grid', 'communications'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: ['cme'],
    recommendedUse: 'Use when the slide should emphasize who may be affected and why CME awareness matters operationally.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/cme/impacted-sectors.png',
    thumbnailPath: '/assets/visual-finder/cme/impacted-sectors.png',
    approvedForUse: true,
    priority: 10,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'cme-source-of-cme',
    title: 'CME Source Region',
    description: 'Sun-source graphic for explaining where a CME begins and how it is launched from the solar surface.',
    assetType: 'satellite',
    category: 'solar-satellite',
    library: 'education-outreach',
    tags: ['cme-library', 'cme', 'source region', 'sun', 'solar eruption'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: ['cme'],
    recommendedUse: 'Use when the message starts with what a CME is and where it comes from.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/cme/source-of-cme.png',
    thumbnailPath: '/assets/visual-finder/cme/source-of-cme.png',
    approvedForUse: true,
    priority: 10,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'cme-timeline-viewer',
    title: 'CME Timeline Viewer',
    description: 'Timeline-oriented CME graphic for showing progression, arrival context, and pacing of impacts.',
    assetType: 'chart',
    category: 'maps-charts',
    library: 'education-outreach',
    tags: ['cme-library', 'cme', 'timeline', 'arrival', 'forecast'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: ['cme'],
    recommendedUse: 'Use when the slide needs a sequence view of launch, travel, and potential Earth impact timing.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/cme/timeline-viewer.png',
    thumbnailPath: '/assets/visual-finder/cme/timeline-viewer.png',
    approvedForUse: true,
    priority: 10,
    defaultApplyTarget: 'main-image',
  },
]

function isCmeLibraryAsset(asset: SocialGraphicsAsset): boolean {
  return asset.tags.includes('cme-library')
}

export function filterAssetsByLibraryCategory(
  assets: SocialGraphicsAsset[],
  filter: SocialGraphicsLibraryFilter,
): SocialGraphicsAsset[] {
  if (filter === 'cme') {
    return assets.filter((asset) => isCmeLibraryAsset(asset))
  }

  return assets
}

export function catalogAssetsForLibrary(
  recommendation: OpsToCommsRecommendation | null | undefined,
): SocialGraphicsAsset[] {
  if (recommendation?.eventType === 'cme') {
    return socialGraphicsAssetCatalog.filter((asset) => isCmeLibraryAsset(asset))
  }

  return socialGraphicsAssetCatalog
}
