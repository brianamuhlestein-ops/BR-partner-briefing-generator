import type {
  GraphicsWorkspaceMode,
  OpsToCommsRecommendation,
  SocialGraphicsAsset,
  SocialGraphicsAssetApplyTarget,
  SocialGraphicsAssetCategory,
  SocialGraphicsAssetType,
} from '../types'

export const socialGraphicsAssetTypeOptions: {
  value: SocialGraphicsAssetType | 'all'
  label: string
}[] = [
  { value: 'all', label: 'All asset types' },
  { value: 'background', label: 'Backgrounds' },
  { value: 'photo', label: 'Photos' },
  { value: 'icon', label: 'Icons' },
  { value: 'logo', label: 'Logos' },
  { value: 'map', label: 'Maps' },
  { value: 'chart', label: 'Charts' },
  { value: 'satellite', label: 'Satellite' },
  { value: 'abstract', label: 'Abstract' },
  { value: 'texture', label: 'Textures' },
]

export const socialGraphicsAssetCategoryOptions: {
  value: SocialGraphicsAssetCategory | 'all'
  label: string
}[] = [
  { value: 'all', label: 'All categories' },
  { value: 'branding', label: 'Branding' },
  { value: 'event-icons', label: 'Event Icons' },
  { value: 'aurora-geomagnetic', label: 'Aurora / Geomagnetic' },
  { value: 'solar-satellite', label: 'Solar / Satellite' },
  { value: 'radio-communications', label: 'Radio / Communications' },
  { value: 'sector-operations', label: 'Sector Operations' },
  { value: 'backgrounds', label: 'Backgrounds' },
  { value: 'maps-charts', label: 'Maps / Charts' },
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
    id: 'noaa-brand-mark',
    title: 'NOAA Brand Mark',
    description: 'Primary NOAA logo for SWPC-branded products and review slides.',
    assetType: 'logo',
    category: 'branding',
    tags: ['NOAA', 'branding', 'official', 'logo'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: [
      'geomagnetic-storm',
      'solar-radiation-storm',
      'radio-blackout',
      'flare',
      'cme',
      'coronal-hole',
      'outlook-forecast',
      'other',
    ],
    recommendedUse: 'Use in the logo slot for branded social and partner products.',
    sourceType: 'local',
    localPath: '/NOAA_logo.png',
    thumbnailPath: '/NOAA_logo.png',
    attribution: 'NOAA',
    approvedForUse: true,
    priority: 10,
    defaultApplyTarget: 'logo',
  },
  {
    id: 'ops-grid-background',
    title: 'Operational Grid Background',
    description: 'Restrained SWPC-style grid background for briefing and planning products.',
    assetType: 'background',
    category: 'backgrounds',
    tags: ['background', 'restrained', 'operations', 'forecast', 'confidence', 'educational'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'radio-blackout', 'outlook-forecast', 'other'],
    recommendedUse: 'Best for partner-oriented graphics where the message should stay dominant.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/ops-grid-background.svg',
    thumbnailPath: '/assets/visual-finder/ops-grid-background.svg',
    approvedForUse: true,
    priority: 9,
    defaultApplyTarget: 'background',
  },
  {
    id: 'alert-chevron-background',
    title: 'Alert Signal Background',
    description: 'Higher-contrast alert background for urgent public-facing cards.',
    assetType: 'background',
    category: 'backgrounds',
    tags: ['urgent', 'high-contrast', 'public-awareness', 'alert', 'informed-design'],
    audience: ['public', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'radio-blackout', 'solar-radiation-storm', 'flare'],
    recommendedUse: 'Use for urgent, simple public alert products with minimal copy.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/alert-chevron-background.svg',
    thumbnailPath: '/assets/visual-finder/alert-chevron-background.svg',
    approvedForUse: true,
    priority: 9,
    defaultApplyTarget: 'background',
  },
  {
    id: 'aurora-ribbon-visual',
    title: 'Aurora Ribbon Visual',
    description: 'Public-friendly geomagnetic visual with a restrained aurora treatment.',
    assetType: 'photo',
    category: 'aurora-geomagnetic',
    tags: ['geomagnetic', 'aurora', 'public-awareness', 'contrast'],
    audience: ['public', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'coronal-hole'],
    recommendedUse: 'Use when geomagnetic messaging has clear public or aurora relevance.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/aurora-ribbon-visual.svg',
    thumbnailPath: '/assets/visual-finder/aurora-ribbon-visual.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'solar-disk-panel',
    title: 'Solar Disk Panel',
    description: 'Solar imagery-style panel for flare, CME, and solar radiation messaging.',
    assetType: 'satellite',
    category: 'solar-satellite',
    tags: ['solar', 'satellite', 'flare', 'CME', 'space environment'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: ['solar-radiation-storm', 'flare', 'cme'],
    recommendedUse: 'Use as the primary visual for source-region or storm-driver messaging.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/solar-disk-panel.svg',
    thumbnailPath: '/assets/visual-finder/solar-disk-panel.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'radio-blackout-signal',
    title: 'Radio Blackout Signal Icon',
    description: 'Clean signal-loss graphic for radio blackout and communications degradation messaging.',
    assetType: 'icon',
    category: 'radio-communications',
    tags: ['communications', 'HF', 'radio blackout', 'high-contrast'],
    audience: ['public', 'partners', 'mixed'],
    eventTypes: ['radio-blackout', 'solar-radiation-storm'],
    recommendedUse: 'Works well when the communication needs to stay simple and direct.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/radio-blackout-signal.svg',
    thumbnailPath: '/assets/visual-finder/radio-blackout-signal.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'hazard-explainer-icon',
    title: 'Hazard Explainer Icon',
    description: 'Large-format explainer icon for educational hazard cards and action slides.',
    assetType: 'icon',
    category: 'event-icons',
    tags: ['educational', 'explainer', 'informed-design', 'actions', 'severity scale'],
    audience: ['public', 'partners', 'mixed'],
    eventTypes: [
      'geomagnetic-storm',
      'solar-radiation-storm',
      'radio-blackout',
      'flare',
      'cme',
      'coronal-hole',
      'outlook-forecast',
      'other',
    ],
    recommendedUse: 'Best for explainer slides that need a strong icon-first focal point.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/hazard-explainer-icon.svg',
    thumbnailPath: '/assets/visual-finder/hazard-explainer-icon.svg',
    approvedForUse: true,
    priority: 9,
    defaultApplyTarget: 'icon-slot',
  },
  {
    id: 'severity-scale-guide',
    title: 'Severity Scale Guide',
    description: 'Color-blocked scale panel for educational and informed-design graphics.',
    assetType: 'chart',
    category: 'event-icons',
    tags: ['educational', 'informed-design', 'severity scale', 'explainer', 'actions'],
    audience: ['public', 'partners', 'internal', 'mixed'],
    eventTypes: [
      'geomagnetic-storm',
      'solar-radiation-storm',
      'radio-blackout',
      'flare',
      'cme',
      'coronal-hole',
      'outlook-forecast',
      'other',
    ],
    recommendedUse: 'Use when the message needs explicit level framing and a simple scale reference.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/severity-scale-guide.svg',
    thumbnailPath: '/assets/visual-finder/severity-scale-guide.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'aviation-route-map',
    title: 'Aviation Route Map',
    description: 'Operational route-map style graphic for aviation-affected messaging.',
    assetType: 'map',
    category: 'sector-operations',
    tags: ['aviation', 'operations', 'sector-risk', 'decision support'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'radio-blackout', 'solar-radiation-storm', 'outlook-forecast'],
    recommendedUse: 'Best for partner products that need to emphasize operational routing impacts.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/aviation-route-map.svg',
    thumbnailPath: '/assets/visual-finder/aviation-route-map.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'gnss-network-chart',
    title: 'GNSS Network Chart',
    description: 'Technical GNSS-style visual for positioning and signal integrity messaging.',
    assetType: 'chart',
    category: 'maps-charts',
    tags: ['GNSS', 'technical', 'confidence framing', 'operations'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'outlook-forecast', 'other'],
    recommendedUse: 'Useful when internal or partner graphics need a more technical visual language.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/gnss-network-chart.svg',
    thumbnailPath: '/assets/visual-finder/gnss-network-chart.svg',
    approvedForUse: true,
    priority: 7,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'power-grid-network',
    title: 'Power Grid Network',
    description: 'Infrastructure-oriented visual for sector-specific electric grid messaging.',
    assetType: 'photo',
    category: 'sector-operations',
    tags: ['power grid', 'infrastructure', 'impact-focused', 'operations'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['geomagnetic-storm', 'outlook-forecast', 'other'],
    recommendedUse: 'Use when the message emphasizes grid operations or infrastructure readiness.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/power-grid-network.svg',
    thumbnailPath: '/assets/visual-finder/power-grid-network.svg',
    approvedForUse: true,
    priority: 7,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'satellite-orbit-graphic',
    title: 'Satellite Orbit Graphic',
    description: 'Clean orbital visual for satellite operations and space environment messaging.',
    assetType: 'satellite',
    category: 'solar-satellite',
    tags: ['satellite', 'operations', 'technical', 'space environment'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['solar-radiation-storm', 'cme', 'geomagnetic-storm', 'other'],
    recommendedUse: 'Use when the audience needs a more technical, orbit-aware visual.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/satellite-orbit-graphic.svg',
    thumbnailPath: '/assets/visual-finder/satellite-orbit-graphic.svg',
    approvedForUse: true,
    priority: 7,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'communications-uplink',
    title: 'Communications Uplink',
    description: 'Uplink-style visual for communications and coordination messaging.',
    assetType: 'photo',
    category: 'radio-communications',
    tags: ['communications', 'network', 'partner-ready', 'impact-focused'],
    audience: ['partners', 'mixed'],
    eventTypes: ['radio-blackout', 'geomagnetic-storm', 'other'],
    recommendedUse: 'Use when the message is partner-facing and communications impacts matter more than aurora appeal.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/communications-uplink.svg',
    thumbnailPath: '/assets/visual-finder/communications-uplink.svg',
    approvedForUse: true,
    priority: 7,
    defaultApplyTarget: 'main-image',
  },
  {
    id: 'operational-chart-board',
    title: 'Operational Chart Board',
    description: 'Map-and-chart panel for forecast, outlook, and readiness messaging.',
    assetType: 'chart',
    category: 'maps-charts',
    tags: ['forecast', 'planning', 'confidence framing', 'decision support'],
    audience: ['partners', 'internal', 'mixed'],
    eventTypes: ['outlook-forecast', 'geomagnetic-storm', 'solar-radiation-storm', 'other'],
    recommendedUse: 'Works well when the communication should feel measured, operational, and planning-oriented.',
    sourceType: 'local',
    localPath: '/assets/visual-finder/operational-chart-board.svg',
    thumbnailPath: '/assets/visual-finder/operational-chart-board.svg',
    approvedForUse: true,
    priority: 8,
    defaultApplyTarget: 'main-image',
  },
]

function matchScore(
  asset: SocialGraphicsAsset,
  recommendation: OpsToCommsRecommendation | null | undefined,
  mode: GraphicsWorkspaceMode,
): number {
  let score = asset.priority * 10

  if (!asset.approvedForUse) {
    score -= 1000
  }

  if (!recommendation) {
    return score
  }

  if (asset.audience.includes(recommendation.audience)) {
    score += 30
  }

  if (asset.eventTypes.includes(recommendation.eventType)) {
    score += 35
  }

  if (asset.assetType === recommendation.recommendedVisualType) {
    score += 28
  }

  if (recommendation.recommendedAssetCategories.includes(asset.category)) {
    score += 24
  }

  const tagMatches = asset.tags.filter((tag) =>
    recommendation.recommendedAssetTags.some((recommendedTag) =>
      recommendedTag.toLowerCase() === tag.toLowerCase(),
    ),
  )
  score += tagMatches.length * 12

  const keywordMatches = recommendation.recommendedVisualKeywords.filter((keyword) => {
    const loweredKeyword = keyword.toLowerCase()
    return (
      asset.title.toLowerCase().includes(loweredKeyword) ||
      asset.description.toLowerCase().includes(loweredKeyword) ||
      asset.tags.some((tag) => tag.toLowerCase().includes(loweredKeyword))
    )
  })
  score += keywordMatches.length * 8

  if (mode === 'social' && (asset.audience.includes('public') || asset.audience.includes('mixed'))) {
    score += 10
  }

  if (
    mode === 'briefing' &&
    (asset.audience.includes('partners') || asset.audience.includes('internal') || asset.audience.includes('mixed'))
  ) {
    score += 10
  }

  return score
}

export function recommendedAssetsForContext(
  recommendation: OpsToCommsRecommendation | null | undefined,
  mode: GraphicsWorkspaceMode,
): SocialGraphicsAsset[] {
  return [...socialGraphicsAssetCatalog]
    .sort((left, right) => matchScore(right, recommendation, mode) - matchScore(left, recommendation, mode))
    .slice(0, 6)
}
