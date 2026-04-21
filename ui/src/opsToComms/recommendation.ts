import type {
  OpsToCommsAudience,
  OpsToCommsEventType,
  OpsToCommsInput,
  OpsToCommsLevel,
  OpsToCommsPathId,
  OpsToCommsRecommendation,
  OpsToCommsSector,
  OpsToCommsSeverity,
  OpsToCommsTimingStatus,
  SocialGraphicsAssetCategory,
  SocialGraphicsAssetType,
  SocialGraphicsTemplateId,
} from '../types'

export const opsToCommsEventOptions: { value: OpsToCommsEventType; label: string }[] = [
  { value: 'geomagnetic-storm', label: 'Geomagnetic storm' },
  { value: 'solar-radiation-storm', label: 'Solar radiation storm' },
  { value: 'radio-blackout', label: 'Radio blackout' },
  { value: 'flare', label: 'Flare' },
  { value: 'cme', label: 'CME' },
  { value: 'coronal-hole', label: 'Coronal hole' },
  { value: 'outlook-forecast', label: 'Outlook / forecast' },
  { value: 'other', label: 'Other' },
]

export const opsToCommsSeverityOptions: { value: OpsToCommsSeverity; label: string }[] = [
  { value: 'minor', label: 'Minor' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'strong', label: 'Strong' },
  { value: 'severe', label: 'Severe' },
  { value: 'extreme', label: 'Extreme' },
]

export const opsToCommsTimingOptions: { value: OpsToCommsTimingStatus; label: string }[] = [
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'imminent', label: 'Imminent' },
  { value: 'forecast', label: 'Forecast' },
  { value: 'past-summary', label: 'Past / summary' },
]

export const opsToCommsLevelOptions: { value: OpsToCommsLevel; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'high', label: 'High' },
  { value: 'very-high', label: 'Very High' },
]

export const opsToCommsAudienceOptions: { value: OpsToCommsAudience; label: string }[] = [
  { value: 'public', label: 'Public' },
  { value: 'partners', label: 'Partners' },
  { value: 'internal', label: 'Internal' },
  { value: 'mixed', label: 'Mixed' },
]

export const opsToCommsSectorOptions: { value: OpsToCommsSector; label: string }[] = [
  { value: 'aviation', label: 'Aviation' },
  { value: 'satellite', label: 'Satellite' },
  { value: 'power-grid', label: 'Power grid' },
  { value: 'communications', label: 'Communications' },
  { value: 'gnss-positioning', label: 'GNSS / positioning' },
  { value: 'human-spaceflight', label: 'Human spaceflight' },
  { value: 'public-aurora', label: 'Public / aurora' },
  { value: 'government-emergency-management', label: 'Government / emergency management' },
]

const scoreMap: Record<OpsToCommsLevel | OpsToCommsSeverity, number> = {
  low: 1,
  minor: 1,
  moderate: 2,
  high: 3,
  strong: 3,
  'very-high': 4,
  severe: 4,
  extreme: 5,
}

function levelScore(level: OpsToCommsLevel | OpsToCommsSeverity): number {
  return scoreMap[level]
}

export function createDefaultOpsToCommsInput(): OpsToCommsInput {
  return {
    eventType: 'geomagnetic-storm',
    severity: 'moderate',
    timingStatus: 'forecast',
    impactedSectors: ['aviation', 'communications'],
    riskLevel: 'moderate',
    impactProbability: 'moderate',
    confidence: 'moderate',
    audience: 'mixed',
  }
}

export function opsToCommsPathLabel(path: OpsToCommsPathId): string {
  return path === 'social-design-review'
    ? 'Social Media Design Review'
    : 'Partner Graphic Design Review'
}

function includesAnySector(input: OpsToCommsInput, sectors: OpsToCommsSector[]): boolean {
  return sectors.some((sector) => input.impactedSectors.includes(sector))
}

function determineTone(input: OpsToCommsInput): OpsToCommsRecommendation['recommendedHeadlineTone'] {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)

  if ((input.timingStatus === 'ongoing' || input.timingStatus === 'imminent') && severity >= 4 && risk >= 3) {
    return 'urgent'
  }

  if (input.timingStatus === 'forecast' && confidence <= 2) {
    return 'watchful'
  }

  if (input.timingStatus === 'past-summary') {
    return 'reassuring'
  }

  return confidence >= 3 ? 'informational' : 'watchful'
}

function determineMessageEmphasis(input: OpsToCommsInput): string {
  const hasPartnerSector = includesAnySector(input, [
    'aviation',
    'satellite',
    'power-grid',
    'communications',
    'gnss-positioning',
    'human-spaceflight',
    'government-emergency-management',
  ])
  const hasPublicSector = includesAnySector(input, ['public-aurora'])

  if (input.audience === 'partners' || input.audience === 'internal') {
    return 'Sector impacts, operational timing, and confidence framing'
  }

  if (input.audience === 'public' && input.timingStatus !== 'past-summary') {
    return 'Public awareness, plain-language impacts, and action-oriented messaging'
  }

  if (hasPartnerSector && hasPublicSector) {
    return 'Dual-track messaging with public awareness supported by sector impact context'
  }

  return 'Operational context, likely impacts, and recommended communication posture'
}

function uniqueValues<T>(values: T[]): T[] {
  return [...new Set(values)]
}

function determineVisualGuidance(input: OpsToCommsInput): {
  recommendedVisualType: SocialGraphicsAssetType
  recommendedVisualKeywords: string[]
  recommendedAssetTags: string[]
  recommendedAssetCategories: SocialGraphicsAssetCategory[]
} {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)
  const publicFacing = input.audience === 'public' || input.audience === 'mixed'
  const partnerFacing = input.audience === 'partners' || input.audience === 'internal' || input.audience === 'mixed'
  const urgent = input.timingStatus === 'ongoing' || input.timingStatus === 'imminent'
  const forecastLike = input.timingStatus === 'forecast' || input.eventType === 'outlook-forecast'
  const auroraRelevant = includesAnySector(input, ['public-aurora'])
  const sectorFocused = includesAnySector(input, [
    'aviation',
    'satellite',
    'power-grid',
    'communications',
    'gnss-positioning',
    'human-spaceflight',
    'government-emergency-management',
  ])

  let recommendedVisualType: SocialGraphicsAssetType = forecastLike ? 'chart' : 'abstract'
  const recommendedVisualKeywords = ['space weather', 'SWPC', input.eventType.replace(/-/g, ' ')]
  const recommendedAssetTags = ['approved', input.audience, input.timingStatus]
  const recommendedAssetCategories: SocialGraphicsAssetCategory[] = ['backgrounds']

  if (forecastLike) {
    recommendedVisualType = partnerFacing && !publicFacing ? 'chart' : 'background'
    recommendedAssetCategories.push('maps-charts')
    recommendedAssetTags.push('forecast', 'planning', 'confidence')
    recommendedVisualKeywords.push('outlook', 'forecast', 'planning')
  }

  if (input.eventType === 'geomagnetic-storm' || input.eventType === 'coronal-hole') {
    if (publicFacing || auroraRelevant) {
      recommendedVisualType = urgent && severity >= 3 ? 'photo' : 'background'
      recommendedAssetCategories.push('aurora-geomagnetic')
      recommendedAssetTags.push('geomagnetic', 'aurora', 'contrast')
      recommendedVisualKeywords.push('geomagnetic', 'aurora', 'northern lights')
    } else {
      recommendedVisualType = 'map'
      recommendedAssetCategories.push('maps-charts', 'sector-operations')
      recommendedAssetTags.push('geomagnetic', 'operations', 'sector-risk')
      recommendedVisualKeywords.push('geomagnetic impacts', 'sector risk', 'operations')
    }
  }

  if (input.eventType === 'radio-blackout') {
    recommendedVisualType = publicFacing && urgent ? 'icon' : 'map'
    recommendedAssetCategories.push('radio-communications')
    recommendedAssetTags.push('communications', 'HF', 'radio blackout')
    recommendedVisualKeywords.push('communications', 'HF degradation', 'radio blackout')
  }

  if (input.eventType === 'solar-radiation-storm' || input.eventType === 'flare' || input.eventType === 'cme') {
    recommendedVisualType = publicFacing && !sectorFocused ? 'satellite' : 'chart'
    recommendedAssetCategories.push('solar-satellite')
    recommendedAssetTags.push('solar', 'satellite', 'space environment')
    recommendedVisualKeywords.push('solar imagery', 'satellite view', 'space weather source region')
  }

  if (sectorFocused) {
    recommendedAssetCategories.push('sector-operations', 'maps-charts')
    recommendedAssetTags.push('impact-focused', 'operations', 'decision support')
    recommendedVisualKeywords.push('impacts', 'operations', 'decision support')
  }

  if (includesAnySector(input, ['aviation'])) {
    recommendedAssetTags.push('aviation')
    recommendedVisualKeywords.push('aviation routing')
  }
  if (includesAnySector(input, ['communications'])) {
    recommendedAssetTags.push('communications')
    recommendedVisualKeywords.push('communications network')
  }
  if (includesAnySector(input, ['gnss-positioning'])) {
    recommendedAssetTags.push('GNSS')
    recommendedVisualKeywords.push('GNSS positioning')
  }
  if (includesAnySector(input, ['power-grid'])) {
    recommendedAssetTags.push('power grid')
    recommendedVisualKeywords.push('power grid operations')
  }
  if (includesAnySector(input, ['satellite', 'human-spaceflight'])) {
    recommendedAssetTags.push('satellite')
    recommendedVisualKeywords.push('satellite operations')
  }

  if (publicFacing && urgent && risk >= 3) {
    recommendedAssetTags.push('high-contrast', 'public-awareness')
    recommendedVisualKeywords.push('clear public message', 'high contrast')
  }

  if (partnerFacing && confidence >= 3) {
    recommendedAssetTags.push('confidence framing', 'partner-ready')
    recommendedVisualKeywords.push('confidence framing', 'operational timing')
  }

  if (input.audience === 'internal') {
    recommendedAssetTags.push('technical', 'internal')
    recommendedVisualKeywords.push('technical context', 'internal decision support')
  }

  if (publicFacing && urgent) {
    recommendedAssetTags.push('informed-design', 'actions', 'severity scale')
    recommendedAssetCategories.push('event-icons')
    recommendedVisualKeywords.push('impact graphic', 'actions to take', 'severity scale')
  }

  if ((input.timingStatus === 'forecast' || input.timingStatus === 'past-summary') && confidence >= 2) {
    recommendedAssetTags.push('educational', 'explainer')
    recommendedAssetCategories.push('event-icons')
    recommendedVisualKeywords.push('what this means', 'explainer graphic', 'education')
  }

  return {
    recommendedVisualType,
    recommendedVisualKeywords: uniqueValues(recommendedVisualKeywords),
    recommendedAssetTags: uniqueValues(recommendedAssetTags),
    recommendedAssetCategories: uniqueValues(recommendedAssetCategories),
  }
}

function recommendPathTemplates(
  input: OpsToCommsInput,
  primaryPath: OpsToCommsPathId,
  secondaryPath: OpsToCommsPathId | null,
): Partial<Record<OpsToCommsPathId, SocialGraphicsTemplateId>> {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)
  const publicFacing = input.audience === 'public' || input.audience === 'mixed'
  const urgent = input.timingStatus === 'ongoing' || input.timingStatus === 'imminent'
  const educationLean =
    (input.timingStatus === 'forecast' || input.timingStatus === 'past-summary' || input.audience === 'mixed') &&
    confidence >= 2 &&
    input.audience !== 'internal'

  const socialTemplate: SocialGraphicsTemplateId =
    educationLean && publicFacing
      ? 'educational-slide'
      : publicFacing &&
          urgent &&
          (severity >= 3 || risk >= 3)
      ? 'informed-design-event'
      : (input.timingStatus === 'ongoing' || input.timingStatus === 'imminent') &&
          severity >= 3
        ? 'event-alert-card'
      : input.audience === 'public' || includesAnySector(input, ['public-aurora'])
        ? 'briefing-summary'
        : 'partner-spotlight'

  const partnerTemplate: SocialGraphicsTemplateId =
    input.timingStatus === 'forecast' || input.eventType === 'outlook-forecast'
      ? 'operational-snapshot'
      : input.audience === 'internal'
        ? 'decision-support-focus'
        : 'partner-impact-brief'

  const templates: Partial<Record<OpsToCommsPathId, SocialGraphicsTemplateId>> = {
    'social-design-review': socialTemplate,
    'partner-design-review': partnerTemplate,
  }

  return {
    [primaryPath]: templates[primaryPath],
    ...(secondaryPath ? { [secondaryPath]: templates[secondaryPath] } : {}),
  }
}

export function buildOpsToCommsRecommendation(input: OpsToCommsInput): OpsToCommsRecommendation {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const probability = levelScore(input.impactProbability)
  const confidence = levelScore(input.confidence)

  const publicWeight =
    (input.audience === 'public' ? 3 : 0) +
    (input.audience === 'mixed' ? 2 : 0) +
    (includesAnySector(input, ['public-aurora']) ? 2 : 0) +
    ((input.timingStatus === 'ongoing' || input.timingStatus === 'imminent') ? 2 : 0) +
    (severity >= 4 ? 2 : 0) +
    (risk >= 3 ? 1 : 0)

  const partnerWeight =
    (input.audience === 'partners' ? 3 : 0) +
    (input.audience === 'mixed' ? 2 : 0) +
    (input.audience === 'internal' ? 2 : 0) +
    (includesAnySector(input, [
      'aviation',
      'satellite',
      'power-grid',
      'communications',
      'gnss-positioning',
      'human-spaceflight',
      'government-emergency-management',
    ])
      ? 2
      : 0) +
    (input.eventType === 'outlook-forecast' || input.timingStatus === 'forecast' ? 2 : 0) +
    (confidence >= 3 ? 1 : 0)

  let recommendedPrimaryPath: OpsToCommsPathId =
    publicWeight >= partnerWeight ? 'social-design-review' : 'partner-design-review'
  let recommendedSecondaryPath: OpsToCommsPathId | null = null

  const shouldRecommendBoth =
    input.audience === 'mixed' ||
    (publicWeight >= 5 && partnerWeight >= 5) ||
    (severity >= 4 && probability >= 3 && confidence >= 3)

  if (shouldRecommendBoth) {
    recommendedSecondaryPath =
      recommendedPrimaryPath === 'social-design-review'
        ? 'partner-design-review'
        : 'social-design-review'
  }

  if (input.eventType === 'outlook-forecast' && input.audience !== 'public') {
    recommendedPrimaryPath = 'partner-design-review'
    recommendedSecondaryPath = input.audience === 'mixed' ? 'social-design-review' : null
  }

  if (input.audience === 'public' && input.timingStatus !== 'past-summary' && severity >= 3) {
    recommendedPrimaryPath = 'social-design-review'
    recommendedSecondaryPath = shouldRecommendBoth ? 'partner-design-review' : recommendedSecondaryPath
  }

  const recommendedPathTemplates = recommendPathTemplates(
    input,
    recommendedPrimaryPath,
    recommendedSecondaryPath,
  )

  const recommendedTemplate =
    recommendedPathTemplates[recommendedPrimaryPath] ?? 'briefing-summary'

  const tone = determineTone(input)
  const emphasis = determineMessageEmphasis(input)
  const visualGuidance = determineVisualGuidance(input)

  const primaryLabel = opsToCommsPathLabel(recommendedPrimaryPath)
  const sectorContext =
    input.impactedSectors.length > 0
      ? `with emphasis on ${input.impactedSectors.length > 1 ? 'cross-sector impacts' : 'sector risk'}`
      : 'with emphasis on operational context'
  const urgencyContext =
    input.timingStatus === 'ongoing' || input.timingStatus === 'imminent'
      ? 'elevated urgency'
      : input.timingStatus === 'forecast'
        ? 'forward-looking planning'
        : 'post-event summary'

  const summary = `Based on the selected event context, this case is best suited for ${primaryLabel.toLowerCase()} ${sectorContext}, ${urgencyContext}, and ${emphasis.toLowerCase()}.`

  return {
    ...input,
    recommendedPrimaryPath,
    recommendedSecondaryPath,
    recommendedTemplate,
    recommendedPathTemplates,
    ...visualGuidance,
    recommendedHeadlineTone: tone,
    recommendedMessageEmphasis: emphasis,
    summary,
    generatedAt: new Date().toISOString(),
  }
}
